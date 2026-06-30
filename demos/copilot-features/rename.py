#!/usr/bin/env python3
from __future__ import annotations

import argparse
import logging
import os
from dataclasses import dataclass, field
from pathlib import Path

OLD_PREFIX = "globex_"
NEW_PREFIX = "chroma_"
EXCLUDED_DIRS = {".git", "node_modules"}

logger = logging.getLogger(__name__)


@dataclass
class Summary:
    scanned_files: int = 0
    changed_files: int = 0
    renamed_files: int = 0
    replacements: int = 0
    skipped_binary_files: int = 0
    skipped_dirs: int = 0
    errors: list[str] = field(default_factory=list)


def iter_files(root: Path, summary: Summary):
    for current_root, dirnames, filenames in os.walk(root, topdown=True):
        before = len(dirnames)
        dirnames[:] = [name for name in dirnames if name not in EXCLUDED_DIRS]
        summary.skipped_dirs += before - len(dirnames)

        for filename in filenames:
            yield Path(current_root) / filename


def rewrite_file(path: Path, dry_run: bool, summary: Summary) -> bool:
    summary.scanned_files += 1

    try:
        raw = path.read_bytes()
    except OSError as exc:
        summary.errors.append(f"read failed: {path} ({exc})")
        return False

    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        summary.skipped_binary_files += 1
        return False

    count = text.count(OLD_PREFIX)
    if count == 0:
        return False

    updated = text.replace(OLD_PREFIX, NEW_PREFIX)

    if not dry_run:
        try:
            path.write_bytes(updated.encode("utf-8"))
        except OSError as exc:
            summary.errors.append(f"write failed: {path} ({exc})")
            return False

    summary.changed_files += 1
    summary.replacements += count
    logger.info(
        "%s  %s  (%s replacements)",
        "WOULD UPDATE" if dry_run else "UPDATED",
        path,
        count,
    )
    return True


def rename_file(path: Path, dry_run: bool, summary: Summary) -> Path:
    if not path.name.startswith(OLD_PREFIX):
        return path

    new_name = NEW_PREFIX + path.name[len(OLD_PREFIX):]
    new_path = path.with_name(new_name)

    if new_path.exists():
        summary.errors.append(f"rename target exists: {path} -> {new_path}")
        return path

    if not dry_run:
        try:
            path.rename(new_path)
        except OSError as exc:
            summary.errors.append(f"rename failed: {path} -> {new_path} ({exc})")
            return path

    summary.renamed_files += 1
    logger.info(
        "%s  %s -> %s",
        "WOULD RENAME" if dry_run else "RENAMED",
        path,
        new_path,
    )
    return new_path


def run(root: Path, dry_run: bool) -> int:
    summary = Summary()

    for path in iter_files(root, summary):
        rewrite_file(path, dry_run, summary)
        rename_file(path, dry_run, summary)

    logger.info("")
    logger.info("Summary")
    logger.info("  Root:                 %s", root)
    logger.info("  Mode:                 %s", "dry-run" if dry_run else "apply")
    logger.info("  Files scanned:        %s", summary.scanned_files)
    logger.info("  Files updated:        %s", summary.changed_files)
    logger.info("  Files renamed:        %s", summary.renamed_files)
    logger.info("  Total replacements:   %s", summary.replacements)
    logger.info("  Binary files skipped: %s", summary.skipped_binary_files)
    logger.info("  Excluded dirs skipped:%s", summary.skipped_dirs)
    logger.info("  Errors:               %s", len(summary.errors))

    if summary.errors:
        logger.info("")
        logger.info("Errors")
        for error in summary.errors:
            logger.error("  - %s", error)
        return 1

    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Rename globex_ symbols and files to chroma_."
    )
    parser.add_argument(
        "root",
        nargs="?",
        default=".",
        help="Root directory to process. Defaults to current directory.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Dry run only. Print what would change without writing files.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    raise SystemExit(run(Path(args.root).resolve(), dry_run=args.check))
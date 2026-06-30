from pathlib import Path

from rename import Summary, rewrite_file, run


def test_run_renames_file_and_contents(tmp_path, caplog):
    source = tmp_path / "globex_example.py"
    source.write_text("def globex_value():\n    return 'globex_item'\n", encoding="utf-8")

    with caplog.at_level("INFO"):
        exit_code = run(tmp_path, dry_run=False)

    renamed = tmp_path / "chroma_example.py"
    assert exit_code == 0
    assert not source.exists()
    assert renamed.exists()
    assert "chroma_value" in renamed.read_text(encoding="utf-8")
    assert "globex_" not in renamed.read_text(encoding="utf-8")

    output = caplog.text
    assert "UPDATED" in output
    assert "RENAMED" in output
    assert "Files updated:        1" in output
    assert "Files renamed:        1" in output
    assert "Total replacements:   2" in output


def test_rewrite_file_skips_binary_content(tmp_path):
    binary_file = tmp_path / "globex_blob.bin"
    binary_file.write_bytes(b"\xff\xfe\x00globex_\x00")
    summary = Summary()

    changed = rewrite_file(binary_file, dry_run=False, summary=summary)

    assert changed is False
    assert summary.scanned_files == 1
    assert summary.skipped_binary_files == 1
    assert summary.changed_files == 0
    assert binary_file.read_bytes() == b"\xff\xfe\x00globex_\x00"


def test_run_check_mode_reports_without_modifying_files(tmp_path, caplog):
    source = tmp_path / "globex_example.py"
    original_text = "def globex_value():\n    return 'globex_item'\n"
    source.write_text(original_text, encoding="utf-8")

    with caplog.at_level("INFO"):
        exit_code = run(tmp_path, dry_run=True)

    assert exit_code == 0
    assert source.exists()
    assert source.read_text(encoding="utf-8") == original_text
    assert not (tmp_path / "chroma_example.py").exists()

    output = caplog.text
    assert "WOULD UPDATE" in output
    assert "WOULD RENAME" in output
    assert "Mode:                 dry-run" in output
    assert "Files updated:        1" in output
    assert "Files renamed:        1" in output
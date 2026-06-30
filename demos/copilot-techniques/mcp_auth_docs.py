#!/usr/bin/env python3
"""MyCorp-Auth MCP Server.

A minimal Model Context Protocol (MCP) server that exposes the local
``mycorp-auth-docs/`` Markdown knowledge base to an MCP client such as
GitHub Copilot Chat.

It speaks JSON-RPC 2.0 over stdin/stdout (the MCP "stdio" transport) and
requires no third-party dependencies, so it runs on a stock Python 3.11+.

Run modes:
    python3 mcp_auth_docs.py          # start the MCP stdio server
    python3 mcp_auth_docs.py test     # quick self-test against the docs
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any, Iterator

# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #

SERVER_NAME = "authDocs"
SERVER_VERSION = "1.0.0"
PROTOCOL_VERSION = "2024-11-05"

# Resolve the docs folder relative to this file so the server works no matter
# what the current working directory happens to be.
DOCS_DIR = Path(__file__).resolve().parent / "mycorp-auth-docs"

# How much surrounding text to include for each match.
SNIPPET_CHARS = 240


# --------------------------------------------------------------------------- #
# Document search
# --------------------------------------------------------------------------- #


def _iter_markdown_files() -> Iterator[Path]:
    """Yield every Markdown file in the docs folder (recursively)."""
    if not DOCS_DIR.is_dir():
        return
    yield from sorted(DOCS_DIR.rglob("*.md"))


def find_auth_docs(query: str) -> list[dict[str, Any]]:
    """Search the Markdown knowledge base for ``query``.

    Returns a list of matches, one per document that mentions the query,
    each with the relative file path, a count of occurrences and a short
    text snippet centered on the first match.
    """
    results: list[dict[str, Any]] = []
    if not query or not query.strip():
        return results

    pattern = re.compile(re.escape(query.strip()), re.IGNORECASE)

    for path in _iter_markdown_files():
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue

        matches = list(pattern.finditer(text))
        if not matches:
            continue

        first = matches[0]
        start = max(0, first.start() - SNIPPET_CHARS // 2)
        end = min(len(text), first.end() + SNIPPET_CHARS // 2)
        snippet = text[start:end].strip().replace("\n", " ")
        snippet = re.sub(r"\s+", " ", snippet)
        if start > 0:
            snippet = "…" + snippet
        if end < len(text):
            snippet = snippet + "…"

        results.append(
            {
                "path": str(path.relative_to(DOCS_DIR.parent)),
                "title": path.stem.replace("_", " ").title(),
                "matches": len(matches),
                "snippet": snippet,
            }
        )

    return results


def format_search_results(query: str, results: list[dict[str, Any]]) -> str:
    """Render search results as human-readable Markdown for the MCP client."""
    if not results:
        return f"No documents found mentioning '{query}'."

    lines = [f"Found {len(results)} document(s) mentioning '{query}':\n"]
    for item in results:
        lines.append(f"## {item['title']}  ({item['path']})")
        lines.append(f"_{item['matches']} match(es)_")
        lines.append("")
        lines.append(f"> {item['snippet']}")
        lines.append("")
    return "\n".join(lines).strip()


# --------------------------------------------------------------------------- #
# Tool registration
# --------------------------------------------------------------------------- #

TOOLS: list[dict[str, Any]] = [
    {
        "name": "search_auth_docs",
        "description": (
            "Search the MyCorp-Auth private Markdown documentation for a "
            "keyword or phrase (e.g. 'token flow', 'refresh', 'login'). "
            "Returns matching documents with excerpts."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The keyword or phrase to search for.",
                }
            },
            "required": ["query"],
        },
    },
    {
        "name": "list_auth_docs",
        "description": "List all available MyCorp-Auth documentation files.",
        "inputSchema": {"type": "object", "properties": {}},
    },
]


def call_tool(name: str, arguments: dict[str, Any]) -> str:
    """Dispatch a tool call and return its textual result."""
    if name == "search_auth_docs":
        query = str(arguments.get("query", "")).strip()
        if not query:
            return "Error: 'query' argument is required."
        return format_search_results(query, find_auth_docs(query))

    if name == "list_auth_docs":
        files = [str(p.relative_to(DOCS_DIR.parent)) for p in _iter_markdown_files()]
        if not files:
            return f"No documentation found in {DOCS_DIR}."
        return "Available documents:\n" + "\n".join(f"- {f}" for f in files)

    raise ValueError(f"Unknown tool: {name}")


# --------------------------------------------------------------------------- #
# JSON-RPC / MCP protocol handlers
# --------------------------------------------------------------------------- #


def _result(request_id: Any, result: Any) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": request_id, "result": result}


def _error(request_id: Any, code: int, message: str) -> dict[str, Any]:
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "error": {"code": code, "message": message},
    }


def handle_request(request: dict[str, Any]) -> dict[str, Any] | None:
    """Handle a single JSON-RPC request and return a response (or None).

    Notifications (requests without an ``id``) return ``None`` because the
    MCP spec forbids replying to them.
    """
    method = request.get("method")
    request_id = request.get("id")
    params = request.get("params") or {}
    is_notification = "id" not in request

    if method == "initialize":
        return _result(
            request_id,
            {
                "protocolVersion": PROTOCOL_VERSION,
                "capabilities": {"tools": {}},
                "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION},
            },
        )

    if method in ("notifications/initialized", "initialized"):
        return None

    if method == "tools/list":
        return _result(request_id, {"tools": TOOLS})

    if method == "tools/call":
        tool_name = params.get("name", "")
        arguments = params.get("arguments") or {}
        try:
            text = call_tool(tool_name, arguments)
            return _result(
                request_id,
                {"content": [{"type": "text", "text": text}], "isError": False},
            )
        except Exception as exc:  # noqa: BLE001 - report any tool failure to client
            return _result(
                request_id,
                {
                    "content": [{"type": "text", "text": f"Error: {exc}"}],
                    "isError": True,
                },
            )

    if method == "ping":
        return _result(request_id, {})

    if is_notification:
        return None

    return _error(request_id, -32601, f"Method not found: {method}")


# --------------------------------------------------------------------------- #
# stdio server loop
# --------------------------------------------------------------------------- #


def serve() -> None:
    """Read JSON-RPC messages from stdin and write responses to stdout."""
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        try:
            request = json.loads(line)
        except json.JSONDecodeError:
            error = _error(None, -32700, "Parse error")
            sys.stdout.write(json.dumps(error) + "\n")
            sys.stdout.flush()
            continue

        response = handle_request(request)
        if response is not None:
            sys.stdout.write(json.dumps(response) + "\n")
            sys.stdout.flush()


# --------------------------------------------------------------------------- #
# Self-test
# --------------------------------------------------------------------------- #


def run_test() -> None:
    """Quick smoke test that does not require an MCP client."""
    query = "token"
    results = find_auth_docs(query)
    print(f"Docs folder: {DOCS_DIR}")
    print(f"Found {len(results)} documents mentioning '{query}'")
    for item in results:
        print(f"  - {item['path']} ({item['matches']} match(es))")


def main() -> None:
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        run_test()
    else:
        serve()


if __name__ == "__main__":
    main()

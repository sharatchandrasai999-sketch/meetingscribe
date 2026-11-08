"""Command-line interface for meetingscribe.

Usage:
    meetingscribe <transcript.txt> [--format text|json]

Reads a plain-text transcript file (no audio) and prints a short
extractive summary plus the action items found in it. Exit code 0 on
success, 2 if the input file cannot be read.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .extract import parse_transcript


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="meetingscribe",
        description="Turn a meeting transcript (.txt) into action items.",
    )
    parser.add_argument("transcript", help="path to the .txt transcript file")
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="output format (default: text)",
    )
    return parser


def format_text(result: dict) -> str:
    lines = ["Summary", "-------", result["summary"] or "(no summary found)", ""]
    lines += ["Action Items", "------------"]
    if not result["action_items"]:
        lines.append("None found.")
    for i, item in enumerate(result["action_items"], start=1):
        due = f" [Due: {item['due']}]" if item["due"] else ""
        lines.append(f"{i}. [Owner: {item['owner']}] {item['task']}{due}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    path = Path(args.transcript)
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"error: cannot read {args.transcript}: {exc.strerror}", file=sys.stderr)
        return 2
    result = parse_transcript(text)
    if args.format == "json":
        print(json.dumps(result, indent=2))
    else:
        print(format_text(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

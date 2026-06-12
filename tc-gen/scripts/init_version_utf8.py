# -*- coding: utf-8 -*-
"""Initialize tc-gen version directories with UTF-8-safe input.

Usage:
  python ".cursor/skills/tc-gen/scripts/init_version_utf8.py" "<project_root>" "<version>"
  python ".cursor/skills/tc-gen/scripts/init_version_utf8.py" "<project_root>" --version-file "<utf8_file>"

When the version name contains Chinese characters, prefer --version-file so the
shell does not need to carry non-ASCII arguments.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path


UTF8 = "utf-8"


def configure_stdio() -> None:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding=UTF8, errors="replace")
    if sys.platform == "win32":
        os.system("chcp 65001 >nul 2>&1")


def read_version(args: argparse.Namespace) -> str:
    if args.version_file:
        text = Path(args.version_file).read_text(encoding="utf-8-sig")
        version = text.splitlines()[0].strip() if text.splitlines() else ""
    else:
        version = (args.version or "").strip()

    if not version:
        raise ValueError("version is required")
    return version


def init_version(project_root: Path, version: str) -> Path:
    if not project_root.exists() or not project_root.is_dir():
        raise ValueError(f"project root does not exist: {project_root}")

    version_root = project_root / ".test-standards" / version
    required_dirs = [
        version_root / "input" / "prodword" / "prodword_pic",
        version_root / "input" / "reference",
        version_root / "output",
    ]

    for directory in required_dirs:
        directory.mkdir(parents=True, exist_ok=True)

    return version_root


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Initialize tc-gen version directories safely.")
    parser.add_argument("project_root", help="Project root directory")
    parser.add_argument("version", nargs="?", help="Version name")
    parser.add_argument(
        "--version-file",
        help="UTF-8 text file whose first line is the version name",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    configure_stdio()
    try:
        args = parse_args(argv or sys.argv[1:])
        version = read_version(args)
        version_root = init_version(Path(args.project_root).resolve(), version)
    except Exception as exc:
        print(f"ERR {exc}")
        return 1

    print(f"OK version directory initialized: {version_root}")
    print("OK subdirectories: input/prodword/prodword_pic, input/reference, output")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

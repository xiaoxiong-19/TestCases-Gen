# -*- coding: utf-8 -*-
"""List tc-gen version input files with UTF-8-safe path handling.

Usage:
  python ".cursor/skills/tc-gen/scripts/list_version_inputs_utf8.py" "<project_root>" "<version>"
  python ".cursor/skills/tc-gen/scripts/list_version_inputs_utf8.py" "<project_root>" --version-file "<utf8_file>"
  python ".cursor/skills/tc-gen/scripts/list_version_inputs_utf8.py" "<project_root>" --version-prefix "V1.0.0"

The script prints JSON with ASCII escapes by default so Windows terminals with
GBK/CP936 output still produce unambiguous filenames for the agent.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any


UTF8 = "utf-8"


def configure_stdio() -> None:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding=UTF8, errors="replace")
    if sys.platform == "win32":
        os.system("chcp 65001 >nul 2>&1")


def read_first_line(path: str) -> str:
    text = Path(path).read_text(encoding="utf-8-sig")
    return text.splitlines()[0].strip() if text.splitlines() else ""


def resolve_version_dir(project_root: Path, args: argparse.Namespace) -> Path:
    standards_root = project_root / ".test-standards"
    if not standards_root.exists() or not standards_root.is_dir():
        raise ValueError(f".test-standards does not exist: {standards_root}")

    version = ""
    if args.version_file:
        version = read_first_line(args.version_file)
    elif args.version:
        version = args.version.strip()

    if version:
        exact = standards_root / version
        if exact.exists() and exact.is_dir():
            return exact

        matches = [p for p in standards_root.iterdir() if p.is_dir() and p.name.startswith(version)]
        if len(matches) == 1:
            return matches[0]
        if len(matches) > 1:
            names = ", ".join(p.name for p in matches)
            raise ValueError(f"multiple versions match {version!r}: {names}")
        raise ValueError(f"version directory not found: {version}")

    if args.version_prefix:
        matches = [p for p in standards_root.iterdir() if p.is_dir() and p.name.startswith(args.version_prefix)]
        if len(matches) == 1:
            return matches[0]
        if not matches:
            raise ValueError(f"no version matches prefix: {args.version_prefix}")
        names = ", ".join(p.name for p in matches)
        raise ValueError(f"multiple versions match prefix {args.version_prefix!r}: {names}")

    raise ValueError("version, --version-file, or --version-prefix is required")


def file_info(path: Path, base: Path) -> dict[str, Any]:
    return {
        "name": path.name,
        "relativePath": path.relative_to(base).as_posix(),
        "absolutePath": str(path),
        "size": path.stat().st_size,
        "suffix": path.suffix.lower(),
    }


def list_files(directory: Path, base: Path) -> list[dict[str, Any]]:
    if not directory.exists():
        return []
    return [file_info(p, base) for p in sorted(directory.iterdir(), key=lambda item: item.name.lower()) if p.is_file()]


def build_report(project_root: Path, version_root: Path) -> dict[str, Any]:
    prodword = version_root / "input" / "prodword"
    pics = prodword / "prodword_pic"
    reference = version_root / "input" / "reference"
    output = version_root / "output"

    prodword_files = [info for info in list_files(prodword, version_root) if info["name"] != "prodword_pic"]
    pic_files = list_files(pics, version_root)
    reference_files = list_files(reference, version_root)

    return {
        "projectRoot": str(project_root),
        "version": version_root.name,
        "versionRoot": str(version_root),
        "directories": {
            "prodword": {"path": str(prodword), "exists": prodword.exists()},
            "prodwordPic": {"path": str(pics), "exists": pics.exists()},
            "reference": {"path": str(reference), "exists": reference.exists()},
            "output": {"path": str(output), "exists": output.exists()},
        },
        "files": {
            "prodword": prodword_files,
            "prodwordPic": pic_files,
            "reference": reference_files,
            "output": list_files(output, version_root),
        },
        "summary": {
            "prodwordCount": len(prodword_files),
            "prodwordPicCount": len(pic_files),
            "referenceCount": len(reference_files),
            "docFiles": [f for f in prodword_files if f["suffix"] in {".doc", ".docx"}],
            "markdownFiles": [f for f in prodword_files if f["suffix"] == ".md"],
            "referenceExcelFiles": [f for f in reference_files if f["suffix"] in {".xls", ".xlsx"}],
            "imageFiles": [f for f in pic_files if f["suffix"] in {".png", ".jpg", ".jpeg", ".gif", ".webp"}],
        },
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="List tc-gen version input files safely.")
    parser.add_argument("project_root", help="Project root directory")
    parser.add_argument("version", nargs="?", help="Version name")
    parser.add_argument("--version-file", help="UTF-8 text file whose first line is the version name")
    parser.add_argument("--version-prefix", help="ASCII-safe prefix used to find exactly one version directory")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    configure_stdio()
    try:
        args = parse_args(argv or sys.argv[1:])
        project_root = Path(args.project_root).resolve()
        version_root = resolve_version_dir(project_root, args)
        report = build_report(project_root, version_root)
    except Exception as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=True, indent=2))
        return 1

    print(json.dumps({"ok": True, **report}, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

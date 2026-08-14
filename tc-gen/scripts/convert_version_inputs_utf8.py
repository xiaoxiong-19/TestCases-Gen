# -*- coding: utf-8 -*-
"""Convert a tc-gen version's Word/Excel inputs to Markdown with UTF-8-safe paths.

Usage:
  python convert_version_inputs_utf8.py "<project_root>" "<version>"
  python convert_version_inputs_utf8.py "<project_root>" --version-file "<utf8_file>"
  python convert_version_inputs_utf8.py "<project_root>" --version-prefix "V1.6.1"

This script is the only Word/Excel conversion entry for tc-gen stage 0.
Agents must not write one-off conversion scripts or mammoth/pandoc one-liners.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

from list_version_inputs_utf8 import configure_stdio, list_files, resolve_version_dir


def find_convert_to_md() -> Path:
    path = Path(__file__).resolve().parent / "convert_to_md.py"
    if not path.is_file():
        raise FileNotFoundError("convert_to_md.py not found next to this script: {}".format(path))
    return path


def load_convert_module():
    path = find_convert_to_md()
    spec = importlib.util.spec_from_file_location("tc_convert_to_md", str(path))
    if spec is None or spec.loader is None:
        raise ImportError("cannot load convert_to_md.py from {}".format(path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module, path


def unsupported_docs(directory: Path) -> list[dict[str, Any]]:
    if not directory.exists():
        return []
    items = []
    for path in sorted(directory.iterdir(), key=lambda item: item.name.lower()):
        if path.is_file() and path.suffix.lower() == ".doc" and not path.name.startswith("~$"):
            items.append(
                {
                    "name": path.name,
                    "absolutePath": str(path),
                    "reason": ".doc is not converted automatically; save as .docx and re-run",
                }
            )
    return items


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Convert tc-gen version Word/Excel inputs to Markdown.")
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
        convert_module, convert_script = load_convert_module()
    except Exception as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=True, indent=2))
        return 1

    prodword = version_root / "input" / "prodword"
    pics = prodword / "prodword_pic"
    reference = version_root / "input" / "reference"
    pics.mkdir(parents=True, exist_ok=True)

    prodword_report = convert_module.convert_directory(prodword, pics, quiet=True)
    reference_report = convert_module.convert_directory(reference, pics, quiet=True)
    skipped = unsupported_docs(prodword) + unsupported_docs(reference)
    converted_count = len(prodword_report.get("converted", [])) + len(reference_report.get("converted", []))
    error_count = len(prodword_report.get("errors", [])) + len(reference_report.get("errors", []))

    report = {
        "ok": error_count == 0,
        "projectRoot": str(project_root),
        "version": version_root.name,
        "versionRoot": str(version_root),
        "convertScript": str(convert_script),
        "picDir": str(pics),
        "prodword": prodword_report,
        "reference": reference_report,
        "skippedUnsupported": skipped,
        "summary": {
            "convertedCount": converted_count,
            "errorCount": error_count,
            "skippedDocCount": len(skipped),
            "imageCount": prodword_report.get("imageCount", 0),
            "prodwordMarkdown": [info["name"] for info in list_files(prodword, version_root) if info["suffix"] == ".md"],
            "referenceMarkdown": [info["name"] for info in list_files(reference, version_root) if info["suffix"] == ".md"],
        },
    }
    print(json.dumps(report, ensure_ascii=True, indent=2))
    if skipped:
        return 0
    return 1 if error_count and not converted_count else 0


if __name__ == "__main__":
    raise SystemExit(main())

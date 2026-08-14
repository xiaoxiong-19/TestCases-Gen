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
import json
import sys
from pathlib import Path
from typing import Any

import convert_to_md
from utf8_paths import add_version_args, configure_stdio, list_files, resolve_version_dir


def unsupported_docs(directory: Path) -> list[dict[str, Any]]:
    if not directory.exists():
        return []
    items = []
    for path in sorted(directory.rglob("*"), key=lambda item: item.as_posix().lower()):
        if not path.is_file() or path.name.startswith("~$"):
            continue
        suffix = path.suffix.lower()
        if suffix == ".doc":
            reason = ".doc is not converted automatically; save as .docx and re-run"
        elif suffix == ".xls":
            reason = ".xls is not converted automatically; save as .xlsx and re-run"
        else:
            continue
        items.append({"name": path.name, "absolutePath": str(path), "reason": reason})
    return items


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Convert tc-gen version Word/Excel inputs to Markdown.")
    add_version_args(parser)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    configure_stdio()
    try:
        args = parse_args(argv or sys.argv[1:])
        project_root = Path(args.project_root).resolve()
        version_root = resolve_version_dir(project_root, args)
    except Exception as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=True, indent=2))
        return 1

    prodword = version_root / "input" / "prodword"
    pics = prodword / "prodword_pic"
    reference = version_root / "input" / "reference"
    pics.mkdir(parents=True, exist_ok=True)

    prodword_report = convert_to_md.convert_directory(prodword, pics, quiet=True)
    reference_report = convert_to_md.convert_directory(reference, pics, quiet=True)
    skipped = unsupported_docs(prodword) + unsupported_docs(reference)
    converted_count = len(prodword_report.get("converted", [])) + len(reference_report.get("converted", []))
    error_count = len(prodword_report.get("errors", [])) + len(reference_report.get("errors", []))
    new_images = list(prodword_report.get("newImages", [])) + list(reference_report.get("newImages", []))
    image_count = len([p for p in pics.iterdir() if p.is_file()]) if pics.exists() else 0

    report = {
        "ok": error_count == 0,
        "projectRoot": str(project_root),
        "version": version_root.name,
        "versionRoot": str(version_root),
        "convertScript": str(Path(convert_to_md.__file__).resolve()),
        "picDir": str(pics),
        "prodword": prodword_report,
        "reference": reference_report,
        "skippedUnsupported": skipped,
        "summary": {
            "convertedCount": converted_count,
            "errorCount": error_count,
            "skippedDocCount": len(skipped),
            "imageCount": image_count,
            "newImageCount": len(new_images),
            "newImages": new_images,
            "prodwordMarkdown": [info["name"] for info in list_files(prodword, version_root, skip_parts=("prodword_pic",)) if info["suffix"] == ".md"],
            "referenceMarkdown": [info["name"] for info in list_files(reference, version_root) if info["suffix"] == ".md"],
        },
    }
    print(json.dumps(report, ensure_ascii=True, indent=2))
    return 1 if error_count and not converted_count else 0


if __name__ == "__main__":
    raise SystemExit(main())

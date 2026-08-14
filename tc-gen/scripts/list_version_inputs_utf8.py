# -*- coding: utf-8 -*-
"""List tc-gen version input files with UTF-8-safe path handling.

Usage:
  python list_version_inputs_utf8.py "<project_root>" "<version>"
  python list_version_inputs_utf8.py "<project_root>" --version-file "<utf8_file>"
  python list_version_inputs_utf8.py "<project_root>" --version-prefix "V1.0.0"

The script prints JSON with ASCII escapes by default so Windows terminals with
GBK/CP936 output still produce unambiguous filenames for the agent.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from utf8_paths import add_version_args, configure_stdio, list_files, resolve_version_dir


DOC_SUFFIXES = {".doc", ".docx"}
EXCEL_SUFFIXES = {".xls", ".xlsx"}
CONVERTIBLE_SUFFIXES = {".docx", ".xlsx"}
UNSUPPORTED_OFFICE_SUFFIXES = {".doc", ".xls"}
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".gif", ".webp"}


def build_report(project_root: Path, version_root: Path) -> dict[str, Any]:
    prodword = version_root / "input" / "prodword"
    pics = prodword / "prodword_pic"
    reference = version_root / "input" / "reference"
    output = version_root / "output"

    prodword_files = list_files(prodword, version_root, skip_parts=("prodword_pic",))
    pic_files = list_files(pics, version_root)
    reference_files = list_files(reference, version_root)
    office_files = prodword_files + reference_files

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
            "docFiles": [f for f in office_files if f["suffix"] in DOC_SUFFIXES],
            "excelFiles": [f for f in office_files if f["suffix"] in EXCEL_SUFFIXES],
            "convertibleOfficeFiles": [f for f in office_files if f["suffix"] in CONVERTIBLE_SUFFIXES],
            "unsupportedOfficeFiles": [f for f in office_files if f["suffix"] in UNSUPPORTED_OFFICE_SUFFIXES],
            "markdownFiles": [f for f in prodword_files if f["suffix"] == ".md"],
            "referenceMarkdownFiles": [f for f in reference_files if f["suffix"] == ".md"],
            "referenceExcelFiles": [f for f in reference_files if f["suffix"] in EXCEL_SUFFIXES],
            "imageFiles": [f for f in pic_files if f["suffix"] in IMAGE_SUFFIXES],
        },
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="List tc-gen version input files safely.")
    add_version_args(parser)
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

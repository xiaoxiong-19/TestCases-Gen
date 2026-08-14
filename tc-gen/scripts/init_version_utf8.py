# -*- coding: utf-8 -*-
"""Initialize tc-gen version directories with UTF-8-safe input.

Usage:
  python init_version_utf8.py "<project_root>" "<version>"
  python init_version_utf8.py "<project_root>" --version-file "<utf8_file>"
  python init_version_utf8.py "<project_root>" --version-prefix "V1.6.1"

When creating a new version whose name contains Chinese characters, prefer
--version-file so the shell does not need to carry non-ASCII arguments.
When the version directory already exists, --version-prefix is enough.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from utf8_paths import (
    add_version_args,
    configure_stdio,
    resolve_version_name_for_init,
)


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
    add_version_args(parser)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    configure_stdio()
    try:
        args = parse_args(argv or sys.argv[1:])
        project_root = Path(args.project_root).resolve()
        version = resolve_version_name_for_init(project_root, args)
        version_root = init_version(project_root, version)
    except Exception as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=True, indent=2))
        return 1

    print(
        json.dumps(
            {
                "ok": True,
                "projectRoot": str(project_root),
                "version": version,
                "versionRoot": str(version_root),
                "subdirectories": [
                    "input/prodword/prodword_pic",
                    "input/reference",
                    "output",
                ],
            },
            ensure_ascii=True,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

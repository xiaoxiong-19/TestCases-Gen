# -*- coding: utf-8 -*-
"""Convert a tc-gen version's 04-测试用例.md to XMind with UTF-8-safe paths.

Usage:
  python convert_cases_to_xmind_utf8.py "<project_root>" "<version>"
  python convert_cases_to_xmind_utf8.py "<project_root>" --version-file "<utf8_file>"
  python convert_cases_to_xmind_utf8.py "<project_root>" --version-prefix "V1.6.1"

Call this only after stage 4 has written 04-测试用例.md AND the user has agreed
to convert to XMind. Do not auto-run at the end of stage 4.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import cases_to_xmind
from utf8_paths import add_version_args, configure_stdio, resolve_version_dir


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Convert tc-gen test cases markdown to XMind.")
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

    md_path = version_root / "output" / "04-测试用例.md"
    output_path = version_root / "output" / "{}.xmind".format(version_root.name)
    if not md_path.is_file():
        print(
            json.dumps(
                {
                    "ok": False,
                    "error": "stage4 markdown not found: {}".format(md_path),
                    "hint": "Generate 04-测试用例.md in stage 4 before converting to XMind.",
                },
                ensure_ascii=True,
                indent=2,
            )
        )
        return 1

    try:
        markdown = md_path.read_text(encoding="utf-8-sig")
        cases = cases_to_xmind.parse_cases(markdown)
        if not cases:
            raise ValueError("no cases parsed; check table headers")
        content = cases_to_xmind.build_xmind(version_root.name, cases)
        cases_to_xmind.write_xmind(content, output_path)
    except Exception as exc:
        print(json.dumps({"ok": False, "error": str(exc), "markdown": str(md_path)}, ensure_ascii=True, indent=2))
        return 1

    print(
        json.dumps(
            {
                "ok": True,
                "projectRoot": str(project_root),
                "version": version_root.name,
                "versionRoot": str(version_root),
                "convertScript": str(Path(cases_to_xmind.__file__).resolve()),
                "markdown": str(md_path),
                "xmind": str(output_path),
                "caseCount": len(cases),
            },
            ensure_ascii=True,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

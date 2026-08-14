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
import importlib.util
import json
import sys
from pathlib import Path

from list_version_inputs_utf8 import configure_stdio, resolve_version_dir


def load_cases_to_xmind():
    path = Path(__file__).resolve().parent / "cases_to_xmind.py"
    if not path.is_file():
        raise FileNotFoundError("cases_to_xmind.py not found next to this script: {}".format(path))
    spec = importlib.util.spec_from_file_location("tc_gen_cases_to_xmind", str(path))
    if spec is None or spec.loader is None:
        raise ImportError("cannot load cases_to_xmind.py from {}".format(path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module, path


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Convert tc-gen test cases markdown to XMind.")
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
        xmind_module, script_path = load_cases_to_xmind()
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
        markdown = md_path.read_text(encoding="utf-8")
        cases = xmind_module.parse_cases(markdown)
        if not cases:
            raise ValueError("no cases parsed; check table headers")
        content = xmind_module.build_xmind(version_root.name, cases)
        xmind_module.write_xmind(content, output_path)
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
                "convertScript": str(script_path),
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

# -*- coding: utf-8 -*-
"""Shared UTF-8-safe path helpers for tc-gen scripts."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import Any, Iterable


UTF8 = "utf-8"
ILLEGAL_VERSION_CHARS = set('\\/:*?"<>|\n\r\t')


def configure_stdio() -> None:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding=UTF8, errors="replace")
    if sys.platform == "win32":
        try:
            os.system("chcp 65001 >nul 2>&1")
        except Exception:
            pass


def read_first_line(path: str) -> str:
    text = Path(path).read_text(encoding="utf-8-sig")
    return text.splitlines()[0].strip() if text.splitlines() else ""


def validate_version_name(name: str, label: str = "version") -> str:
    name = (name or "").strip()
    if not name:
        raise ValueError(f"{label} is required")
    if name in {".", ".."} or name.startswith(".."):
        raise ValueError(f"invalid {label}: {name}")
    if any(ch in ILLEGAL_VERSION_CHARS for ch in name):
        raise ValueError(f"{label} contains illegal characters: {name}")
    return name


def add_version_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("project_root", help="Project root directory")
    parser.add_argument("version", nargs="?", help="Version name")
    parser.add_argument("--version-file", help="UTF-8 text file whose first line is the version name")
    parser.add_argument("--version-prefix", help="ASCII-safe prefix used to find exactly one version directory")


def _match_version_dirs(standards_root: Path, prefix: str) -> list[Path]:
    return [p for p in standards_root.iterdir() if p.is_dir() and p.name.startswith(prefix)]


def resolve_version_dir(project_root: Path, args: argparse.Namespace) -> Path:
    standards_root = project_root / ".test-standards"
    if not standards_root.exists() or not standards_root.is_dir():
        raise ValueError(f".test-standards does not exist: {standards_root}")

    version = ""
    if args.version_file:
        version = validate_version_name(read_first_line(args.version_file))
    elif args.version:
        version = validate_version_name(args.version)

    if version:
        exact = standards_root / version
        if exact.exists() and exact.is_dir():
            return exact

        matches = _match_version_dirs(standards_root, version)
        if len(matches) == 1:
            return matches[0]
        if len(matches) > 1:
            names = ", ".join(p.name for p in matches)
            raise ValueError(f"multiple versions match {version!r}: {names}")
        raise ValueError(f"version directory not found: {version}")

    if args.version_prefix:
        prefix = validate_version_name(args.version_prefix, "version prefix")
        matches = _match_version_dirs(standards_root, prefix)
        if len(matches) == 1:
            return matches[0]
        if not matches:
            raise ValueError(f"no version matches prefix: {prefix}")
        names = ", ".join(p.name for p in matches)
        raise ValueError(f"multiple versions match prefix {prefix!r}: {names}")

    raise ValueError("version, --version-file, or --version-prefix is required")


def resolve_version_name_for_init(project_root: Path, args: argparse.Namespace) -> str:
    """Return a version directory name for init.

    Existing dirs may be selected by --version-prefix. New Chinese names must
    come from a positional argument or --version-file.
    """
    if args.version_file:
        return validate_version_name(read_first_line(args.version_file))
    if args.version:
        return validate_version_name(args.version)
    if args.version_prefix:
        return resolve_version_dir(project_root, args).name
    raise ValueError("version, --version-file, or --version-prefix is required")


def file_info(path: Path, base: Path) -> dict[str, Any]:
    return {
        "name": path.name,
        "relativePath": path.relative_to(base).as_posix(),
        "absolutePath": str(path),
        "size": path.stat().st_size,
        "suffix": path.suffix.lower(),
    }


def list_files(
    directory: Path,
    base: Path,
    skip_parts: Iterable[str] = (),
) -> list[dict[str, Any]]:
    """List files under directory recursively. Skip lock files and named path parts."""
    if not directory.exists():
        return []
    skip = set(skip_parts)
    result: list[dict[str, Any]] = []
    for path in sorted(directory.rglob("*"), key=lambda item: item.as_posix().lower()):
        if not path.is_file():
            continue
        if path.name.startswith("~$"):
            continue
        try:
            rel_parts = path.relative_to(directory).parts
        except ValueError:
            continue
        if skip and any(part in skip for part in rel_parts[:-1]):
            continue
        result.append(file_info(path, base))
    return result

"""Convert tc-gen markdown test cases to XMind.

Usage:
  python cases_to_xmind.py .test-standards/V1.12.0-xxx
  python cases_to_xmind.py .test-standards/V1.12.0-xxx/output/04-测试用例.md
  python cases_to_xmind.py <version_dir_or_case_md> <output.xmind>

Input markdown must contain table columns:
  用例等级 | 所属模块 | 用例标题 | 前置条件 | 用例步骤 | 预期结果

Only 前置条件 is optional. It is written as a note on the last case-title topic.
"""

from __future__ import annotations

import json
import re
import sys
import uuid
import zipfile
from pathlib import Path
from typing import Dict, Iterable, List, Optional


REQUIRED_COLUMNS = ["用例等级", "所属模块", "用例标题", "用例步骤", "预期结果"]
OPTIONAL_COLUMNS = ["前置条件"]

# 根节点结构：逻辑图向右
ROOT_STRUCTURE_CLASS = "org.xmind.ui.logic.right"

# 任务进度：用例名称起始父节点固定使用「任务完成」
TASK_DONE_MARKER = "task-done"

# 任务优先级：用例等级 -> XMind priority marker
PRIORITY_MARKERS = {
    "1": "priority-1",
    "2": "priority-2",
    "3": "priority-3",
    "4": "priority-4",
}


def new_id() -> str:
    return uuid.uuid4().hex


def is_separator_row(cells: List[str]) -> bool:
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", c.strip()) for c in cells)


def split_md_row(line: str) -> List[str]:
    line = line.strip()
    if not line.startswith("|") or "|" not in line[1:]:
        return []
    if line.endswith("|"):
        line = line[:-1]
    if line.startswith("|"):
        line = line[1:]
    return [cell.strip() for cell in line.split("|")]


def normalize_text(value: str) -> str:
    value = value.replace("<br/>", "<br>").replace("<br />", "<br>")
    value = re.sub(r"<br\s*>", "\n", value, flags=re.IGNORECASE)
    value = re.sub(r"\r\n?", "\n", value)
    return value.strip()


def split_lines(value: str) -> List[str]:
    value = normalize_text(value)
    if not value:
        return []
    lines = [line.strip() for line in value.split("\n")]
    return [line for line in lines if line]


def strip_expected_prefix(text: str) -> str:
    return re.sub(r"^\d+[、.]\s*", "", text.strip())


def split_expected(value: str) -> List[str]:
    """Split expected results by Chinese semicolon and number as 1、xxx, 2、yyy."""
    value = normalize_text(value)
    if not value:
        return []
    parts = [strip_expected_prefix(part) for part in value.split("；")]
    parts = [part for part in parts if part]
    return [f"{idx}、{part}" for idx, part in enumerate(parts, start=1)]


def parse_cases(markdown: str) -> List[Dict[str, str]]:
    cases: List[Dict[str, str]] = []
    active_header: Optional[List[str]] = None
    active_indexes: Dict[str, int] = {}
    expecting_separator = False

    for raw_line in markdown.splitlines():
        cells = split_md_row(raw_line)
        if not cells:
            active_header = None
            active_indexes = {}
            expecting_separator = False
            continue

        if active_header is None:
            header = [cell.strip() for cell in cells]
            if all(col in header for col in REQUIRED_COLUMNS):
                active_header = header
                active_indexes = {col: header.index(col) for col in REQUIRED_COLUMNS + OPTIONAL_COLUMNS if col in header}
                expecting_separator = True
            continue

        if expecting_separator:
            expecting_separator = False
            if is_separator_row(cells):
                continue

        if len(cells) < len(active_header):
            cells = cells + [""] * (len(active_header) - len(cells))

        item = {col: normalize_text(cells[idx]) for col, idx in active_indexes.items() if idx < len(cells)}
        if not any(item.get(col) for col in REQUIRED_COLUMNS):
            continue
        missing = [col for col in REQUIRED_COLUMNS if not item.get(col)]
        if missing:
            raise ValueError(f"用例表存在必填字段为空: {', '.join(missing)}; 行内容={cells}")
        if item["用例等级"] not in PRIORITY_MARKERS:
            raise ValueError(f"用例等级只允许 1/2/3/4: {item['用例等级']} ({item['用例标题']})")
        cases.append(item)

    return cases


def topic(
    title: str,
    children: Optional[List[dict]] = None,
    note: str = "",
    markers: Optional[List[str]] = None,
    structure_class: str = "",
) -> dict:
    data = {
        "id": new_id(),
        "class": "topic",
        "title": title,
    }
    if children:
        data["children"] = {"attached": children}
    if note:
        data["notes"] = {"plain": {"content": note}}
    if markers:
        data["markers"] = [{"markerId": marker_id} for marker_id in markers]
    if structure_class:
        data["structureClass"] = structure_class
    return data


def build_step_expected_children(steps: List[str], expected: List[str]) -> List[dict]:
    """Attach one steps node; numbered expected nodes hang under it in order."""
    expected_topics = [topic(line) for line in expected]
    if steps:
        return [topic("\n".join(steps), expected_topics or None)]
    return expected_topics


def build_case_title_tree(
    title_parts: List[str],
    level: str,
    steps: List[str],
    expected: List[str],
    note: str,
) -> dict:
    """Build case title hierarchy with icons, then attach steps and expected results.

    Structure:
      起始父节点 (task-done)
        └── ... 中间父节点 ...
              └── 末级用例名 (priority-N)
                    └── 全部步骤（一个子节点，多行）
                          ├── 1、预期一
                          └── 2、预期二
    """
    parts = title_parts if title_parts else ["未命名用例"]
    priority_marker = PRIORITY_MARKERS[level]

    leaf_children = build_step_expected_children(steps, expected)

    if len(parts) == 1:
        markers = [TASK_DONE_MARKER, priority_marker]
        return topic(parts[0], leaf_children or None, note=note, markers=markers)

    current = topic(parts[-1], leaf_children or None, note=note, markers=[priority_marker])
    for part in reversed(parts[1:-1]):
        current = topic(part, [current])
    return topic(parts[0], [current], markers=[TASK_DONE_MARKER])


def add_case(module_nodes: Dict[str, dict], root_children: List[dict], case: Dict[str, str]) -> None:
    module_path = [part.strip() for part in case["所属模块"].split("/") if part.strip()]
    if not module_path:
        module_path = ["未归类"]

    parent_children = root_children
    key_parts: List[str] = []
    for part in module_path:
        key_parts.append(part)
        key = "/".join(key_parts)
        node = module_nodes.get(key)
        if node is None:
            node = topic(part, [])
            module_nodes[key] = node
            parent_children.append(node)
        parent_children = node.setdefault("children", {}).setdefault("attached", [])

    title_parts = [part.strip() for part in case["用例标题"].split("/") if part.strip()]
    steps = split_lines(case["用例步骤"])
    expected = split_expected(case["预期结果"])
    precondition = case.get("前置条件", "").strip()
    note = f"前置条件：{precondition}" if precondition else ""

    case_node = build_case_title_tree(title_parts, case["用例等级"], steps, expected, note)
    parent_children.append(case_node)


def build_xmind(version_name: str, cases: Iterable[Dict[str, str]]) -> List[dict]:
    root_children: List[dict] = []
    module_nodes: Dict[str, dict] = {}
    for case in cases:
        add_case(module_nodes, root_children, case)

    root_topic = topic(version_name, root_children, structure_class=ROOT_STRUCTURE_CLASS)
    return [
        {
            "id": new_id(),
            "class": "sheet",
            "title": version_name,
            "rootTopic": root_topic,
        }
    ]


def resolve_paths(arg: str, output_arg: Optional[str]) -> tuple[Path, Path, str]:
    source = Path(arg).resolve()
    if source.is_dir():
        version_dir = source
        md_path = version_dir / "output" / "04-测试用例.md"
        version_name = version_dir.name
        output_path = Path(output_arg).resolve() if output_arg else version_dir / "output" / f"{version_name}.xmind"
    else:
        md_path = source
        version_dir = md_path.parent.parent if md_path.parent.name == "output" else md_path.parent
        version_name = version_dir.name
        output_path = Path(output_arg).resolve() if output_arg else md_path.with_suffix(".xmind")
    return md_path, output_path, version_name


def write_xmind(content: List[dict], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    active_sheet_id = content[0]["id"]
    metadata = {
        "creator": {"name": "tc-convert", "version": "2.4.1"},
        "activeSheetId": active_sheet_id,
    }
    manifest = {
        "file-entries": {
            "content.json": {},
            "metadata.json": {},
            "manifest.json": {},
        }
    }
    with zipfile.ZipFile(output_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("content.json", json.dumps(content, ensure_ascii=False, indent=2))
        zf.writestr("metadata.json", json.dumps(metadata, ensure_ascii=False, indent=2))
        zf.writestr("manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2))


def main() -> int:
    if len(sys.argv) not in (2, 3):
        print(__doc__.strip())
        return 2

    md_path, output_path, version_name = resolve_paths(sys.argv[1], sys.argv[2] if len(sys.argv) == 3 else None)
    if not md_path.exists():
        print(f"ERR 找不到用例文件: {md_path}")
        return 1

    markdown = md_path.read_text(encoding="utf-8")
    cases = parse_cases(markdown)
    if not cases:
        print(f"ERR 未解析到用例。请确认表头包含: {' | '.join(REQUIRED_COLUMNS)}")
        return 1

    content = build_xmind(version_name, cases)
    write_xmind(content, output_path)
    print(f"OK  已生成 XMind: {output_path}  用例数: {len(cases)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

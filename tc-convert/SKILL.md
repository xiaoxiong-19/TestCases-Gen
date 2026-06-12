---
name: tc-convert
description: 转换测试设计相关文档产物。用于用户说 tc-convert、转换 Word/Excel 为 Markdown、抽取 docx 图片、把测试用例 Markdown 转 XMind、docx to md、md to xmind 时。支持 .test-standards/<版本>/input/prodword 下需求文档转 md 并抽图到 prodword_pic，以及 .test-standards/<版本>/output/04-测试用例.md 转 .xmind。
---

# tc-convert：测试文档产物转换

`tc-convert` 是通用转换 skill，专门处理文档格式转换，不负责业务分析和测试设计。

## 能力范围

- Word/Excel 转 Markdown：`.docx` / `.xlsx` → `.md`。
- Word 图片抽取：把 `.docx` 内图片保存到同目录的 `prodword_pic/`。
- 测试用例转 XMind：把 `04-测试用例.md` 转成 `.xmind`。

## 目录约定

推荐配合 `tc-gen` 使用：

```text
.test-standards/<版本>/
├── input/
│   ├── prodword/
│   │   └── prodword_pic/
│   └── reference/
└── output/
    ├── 04-测试用例.md
    └── <版本>.xmind
```

## Word/Excel 转 Markdown

当用户要求转换需求文档，或 `tc-gen` 阶段0需要转换 `prodword` 时，运行：

```bash
python ".cursor/skills/tc-convert/scripts/convert_to_md.py" ".test-standards/<版本>/input/prodword"
```

也可以转换任意目录：

```bash
python ".cursor/skills/tc-convert/scripts/convert_to_md.py" "<目录路径>"
```

转换规则：

- `.docx` 转成同名 `.md`，原文件保留。
- `.xlsx` 每个 sheet 转成 Markdown 表格，原文件保留。
- `.docx` 内图片抽取到被转换目录下的 `prodword_pic/`。
- Markdown 中尽量在图片所在段落附近插入 `![图片](prodword_pic/xxx.png)`。
- 如果无法精确定位图片位置，脚本至少抽取图片，阶段0应读取 `prodword_pic/` 图片清单再人工/AI核对。

## 测试用例 Markdown 转 XMind

当用户要求转 XMind，或 `tc-gen` 阶段4完成后，运行：

```bash
python ".cursor/skills/tc-convert/scripts/cases_to_xmind.py" ".test-standards/<版本>"
```

默认读取：

```text
.test-standards/<版本>/output/04-测试用例.md
```

默认生成：

```text
.test-standards/<版本>/output/<版本>.xmind
```

也可以显式指定输入和输出：

```bash
python ".cursor/skills/tc-convert/scripts/cases_to_xmind.py" ".test-standards/<版本>/output/04-测试用例.md" ".test-standards/<版本>/output/<版本>.xmind"
```

## 用例表头要求

`cases_to_xmind.py` 只识别下列表头：

```markdown
| 用例等级 | 所属模块 | 用例标题 | 前置条件 | 用例步骤 | 预期结果 |
|---|---|---|---|---|---|
```

字段规则：

- `用例等级`：必填，只允许 `1`、`2`、`3`、`4`。
- `所属模块`：必填，支持 `/` 分层级，例如 `建档/自主建档/线上授权书`。
- `用例标题`：必填，脚本会自动加等级前缀，如 `【等级1】xxx`。
- `用例步骤`：必填，支持 `<br>` 分隔多步。
- `预期结果`：必填，支持 `<br>` 分隔多条断言。
- `前置条件`：非必填；如果有，写入 XMind 用例标题节点备注。

## XMind 层级

- 根节点：版本目录名，例如 `V1.12.0-xxx`。
- 中间节点：`所属模块` 按 `/` 拆分。
- 用例节点：带等级前缀的 `用例标题`。
- 用例节点下：`用例步骤`、`预期结果`。
- 前置条件：写入用例节点备注。

## 注意事项

- 转换脚本只做格式转换，不修改业务语义。
- 如果 Markdown 表格表头不符合要求，先调整表头再转 XMind。
- 如果 PowerShell 直接写中文临时文件出现乱码，优先用 Python 或编辑器以 UTF-8 写入。

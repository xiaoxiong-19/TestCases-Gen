---
name: tc-convert
description: 把测试用例 Markdown 转成 XMind。用于用户说 tc-convert、把测试用例 Markdown 转 XMind、md to xmind 时。默认读取 .test-standards/<版本>/output/04-测试用例.md，生成 .test-standards/<版本>/output/<版本>.xmind。
---

# tc-convert：测试用例 Markdown 转 XMind

`tc-convert` 只做格式转换，把 `04-测试用例.md` 转成 `.xmind`，不负责业务分析和测试设计。

## 目录约定

推荐配合 `tc-gen` 使用：

```text
.test-standards/<版本>/
└── output/
    ├── 04-测试用例.md
    └── <版本>.xmind
```

## 运行方式

当用户要求转 XMind，或 `tc-gen` 阶段4完成后，运行：

```bash
python "D:/Applications/IDEA/SKILL/TestCases-Gen/tc-convert/scripts/cases_to_xmind.py" ".test-standards/<版本>"
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
python "D:/Applications/IDEA/SKILL/TestCases-Gen/tc-convert/scripts/cases_to_xmind.py" ".test-standards/<版本>/output/04-测试用例.md" ".test-standards/<版本>/output/<版本>.xmind"
```

## 用例表头要求

`cases_to_xmind.py` 只识别下列表头：

```markdown
| 用例等级 | 所属模块 | 用例标题 | 前置条件 | 用例步骤 | 预期结果 |
|---|---|---|---|---|---|
```

字段规则：

- `用例等级`：必填，只允许 `1`、`2`、`3`、`4`；映射为 XMind 任务优先级图标。
- `所属模块`：必填，支持 `/` 分层级，例如 `建档/自主建档/线上授权书`。
- `用例标题`：必填，支持 `/` 拆成父节点与子节点，例如 `授权流程/线上授权书提交`。
- `用例步骤`：必填，支持 `<br>` 分隔多步。
- `预期结果`：必填，支持 `<br>` 分隔多条断言。
- `前置条件`：非必填；如果有，写入用例标题最后一个子节点备注。

## XMind 层级

- 根节点：版本目录名，例如 `V1.12.0-xxx`。
- 中间节点：`所属模块` 按 `/` 拆分。
- 用例名称：`用例标题` 按 `/` 拆成父节点链；若只有一级，则该节点同时承担起始父节点与末级子节点职责。
- 用例名称末级子节点之后：直接挂步骤节点，不再创建 `用例步骤` 中间节点。
- 步骤节点之后：直接挂预期结果节点，不再创建 `预期结果` 中间节点。

示例（`用例标题=授权流程/线上授权书提交`）：

```text
授权流程                          ← 起始父节点，图标：任务完成 (task-done)
└── 线上授权书提交                ← 末级子节点，图标：任务优先级 (priority-N)
    ├── 1. 打开授权页面
    ├── 2. 填写并提交
    ├── 页面展示授权表单
    └── 提交成功并返回结果页
```

## 图标映射

### 任务进度（起始父节点）

用例名称的第一个父节点固定添加「任务完成」图标：

| XMind markerId | 含义 |
|---|---|
| `task-done` | 任务完成 |

### 任务优先级（末级子节点）

用例名称的最后一个子节点，按 `用例等级` 添加优先级图标：

| 用例等级 | XMind markerId |
|---|---|
| `1` | `priority-1` |
| `2` | `priority-2` |
| `3` | `priority-3` |
| `4` | `priority-4` |

当 `用例标题` 只有一级、没有 `/` 拆分时，起始父节点与末级子节点为同一节点，同时添加 `task-done` 与对应 `priority-N` 两个图标。

## 注意事项

- 转换脚本只做格式转换，不修改业务语义。
- 如果 Markdown 表格表头不符合要求，先调整表头再转 XMind。
- 如果 PowerShell 直接写中文临时文件出现乱码，优先用 Python 或编辑器以 UTF-8 写入。

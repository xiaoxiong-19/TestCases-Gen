# 测试提效 Skills 使用说明

本目录包含两个配套使用的 Cursor Skill：

- `tc-gen`：面向版本迭代的测试概要、测试用例、变更影响分析生成流程。
- `tc-convert`：通用转换工具，负责 Word/Excel 转 Markdown、抽取需求图片、测试用例 Markdown 转 XMind。

推荐使用方式：先用 `tc-gen` 初始化版本目录，再把需求文档放入版本目录，随后按阶段生成测试产物；需要格式转换时由 `tc-gen` 调用 `tc-convert`，也可以单独调用 `tc-convert`。

## 目录结构

初始化一个版本后，目录结构如下：

```text
.test-standards/<版本>/
├── input/
│   ├── prodword/
│   │   └── prodword_pic/
│   └── reference/
└── output/
    ├── 01-定位.md
    ├── 02-变更分析.md
    ├── 03-测试概要.md
    ├── 04-测试用例.md
    └── <版本>.xmind
```

目录说明：

- `input/prodword/`：放版本需求文档，支持 `.docx`、`.md` 等。
- `input/prodword/prodword_pic/`：放需求文档中的图片，尤其是流程图、泳道图、时序图。
- `input/reference/`：放三方接口文档、联动文档、补充说明等参考资料。
- `output/`：放 `tc-gen` 分阶段生成的测试产物。

## tc-gen

`tc-gen` 用于生成测试概要与测试用例。它会结合：

- 版本需求文档
- 三方接口/联动文档
- `shcj-common/.dev-standards` 业务知识库
- `user-dev-standards` MCP
- 业务文档、代码地图、流程定义
- 需求中的流程图/图片

### 初始化版本

在 Cursor 中输入类似：

```text
tc-gen 初始化版本 V1.12.0-xxx
```

执行后会创建：

```text
.test-standards/V1.12.0-xxx/input/prodword/
.test-standards/V1.12.0-xxx/input/prodword/prodword_pic/
.test-standards/V1.12.0-xxx/input/reference/
.test-standards/V1.12.0-xxx/output/
```

如果 `.test-standards` 已存在，不会重复初始化根目录；如果版本目录已存在，只补齐缺失子目录，不覆盖已有文件。

### 放入输入资料

把需求文档放到：

```text
.test-standards/<版本>/input/prodword/
```

把接口文档、三方文档、补充材料放到：

```text
.test-standards/<版本>/input/reference/
```

如果需求文档中有流程图，`tc-convert` 会尽量从 Word 中自动抽取到：

```text
.test-standards/<版本>/input/prodword/prodword_pic/
```

也可以手工把流程图原图补充到该目录。

### 分阶段生成

`tc-gen` 分 5 个阶段执行，每阶段完成后必须停下来等确认：

```text
阶段0 准备：Word 转 md + 图片抽取 + 读取输入 + MCP需求校验
阶段1 定位：MCP匹配业务规则 + 读取业务文档/codemap/procdefs
阶段2 变更分析：需求 vs 业务现状 vs MCP服务知识
阶段3 测试概要：按6维度生成测试点
阶段4 详细用例 + 回归清单
```

常见指令示例：

```text
tc-gen 对 V1.12.0-xxx 执行阶段0
tc-gen 继续 V1.12.0-xxx 阶段1
tc-gen 基于已确认的变更清单生成 V1.12.0-xxx 阶段3测试概要
tc-gen 为 V1.12.0-xxx 生成阶段4详细测试用例
```

### 阶段产物

`tc-gen` 会在版本 `output/` 下生成：

```text
01-定位.md
02-变更分析.md
03-测试概要.md
04-测试用例.md
```

其中 `04-测试用例.md` 使用固定表头：

```markdown
| 用例等级 | 所属模块 | 用例标题 | 前置条件 | 用例步骤 | 预期结果 |
|---|---|---|---|---|---|
```

字段说明：

- `用例等级`：必填，只允许 `1`、`2`、`3`、`4`。
- `所属模块`：必填，支持 `/` 分层级，例如 `建档/自主建档/线上授权书`。
- `用例标题`：必填，单条原子用例标题。
- `前置条件`：非必填，转 XMind 后会作为备注。
- `用例步骤`：必填，支持 `<br>` 分隔多步。
- `预期结果`：必填，必须唯一明确且可断言。

## tc-convert

`tc-convert` 是转换工具，可单独调用，也可由 `tc-gen` 调用。

### Word/Excel 转 Markdown

推荐命令：

```bash
python ".cursor/skills/tc-convert/scripts/convert_to_md.py" ".test-standards/<版本>/input/prodword"
```

功能：

- `.docx` 转成同名 `.md`
- `.xlsx` 转成 Markdown 表格
- 抽取 `.docx` 图片到 `prodword_pic/`
- 尽量在 Markdown 中插入图片引用

注意：

- 原始 `.docx` / `.xlsx` 不会被删除。
- 如果图片无法精确定位到正文位置，至少会被抽取到 `prodword_pic/`，后续阶段0需要重点查看。

### 测试用例 Markdown 转 XMind

推荐命令：

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

XMind 层级：

```text
根节点：<版本>
  所属模块第1层
    所属模块第2层
      【等级1】用例标题
        用例步骤
        预期结果
```

如果 `前置条件` 有内容，会写入用例标题节点备注。

## 推荐工作流

1. 初始化版本：

   ```text
   tc-gen 初始化版本 V1.12.0-xxx
   ```

2. 放入需求和参考资料：

   ```text
   input/prodword/
   input/reference/
   ```

3. 执行阶段0，转换文档并解析需求、图片、流程图：

   ```text
   tc-gen 对 V1.12.0-xxx 执行阶段0
   ```

4. 逐阶段确认并生成：

   ```text
   01-定位.md
   02-变更分析.md
   03-测试概要.md
   04-测试用例.md
   ```

5. 转 XMind：

   ```bash
   python ".cursor/skills/tc-convert/scripts/cases_to_xmind.py" ".test-standards/V1.12.0-xxx"
   ```

## 使用建议

- `tc-gen` 负责测试分析和用例设计，`tc-convert` 只负责格式转换。
- 需求流程图、泳道图、时序图对阶段3“逐步骤功能操作偏离矩阵”很重要，务必确认 `prodword_pic/` 图片已被读取。
- 阶段3前置门禁没满足时，不要直接生成测试概要。
- 阶段4生成用例时，保持一条用例只覆盖一个明确校验点，方便后续转 XMind 和评审。

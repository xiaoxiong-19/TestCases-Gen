# TestCases-Gen Skills 使用说明

本仓库包含一组可同步到 Cursor / Trae / Codex 的本地 Skills：

| Skill 目录 | 触发语 | 用途 |
|---|---|---|
| `tc-gen/` | `tc-gen` | 版本迭代：分阶段生成测试概要、测试用例、变更影响与回归清单 |
| `tc-convert/` | `tc-convert` | 格式转换：测试用例 Markdown → XMind；另含 Word/Excel → Markdown 脚本 |
| `pic-to-vue/` | `proto-to-vue` / `pic-to-vue` | 原型图 → 低代码 `lls-*` Vue 页面（一次写完、少样例对照） |

配套脚本：

- `update-local-skills.bat`：拉取本仓库最新代码后，自动扫描仓库内**所有含 `SKILL.md` 的子目录**，同步到 `%USERPROFILE%\.cursor\skills`、`.trae-cn\skills`、`.codex\skills`（存在则同步；也可传入自定义 skills 根目录）。

---

## 快速同步到本机

在仓库根目录双击或执行：

```bat
update-local-skills.bat
```

要求：

1. 本目录是 Git 仓库，且工作区干净（无未提交改动）。
2. 能访问 `origin`（默认 `https://github.com/xiaoxiong-19/TestCases-Gen.git`）。
3. 使用 `git pull --ff-only` 更新后，按子目录同步 skill。

新增 skill 目录（含 `SKILL.md`）后无需改 bat，会自动纳入同步。

---

## 测试提效：`tc-gen` + `tc-convert`

推荐链路：先用 `tc-gen` 初始化版本并分阶段产出，需要转脑图时用 `tc-convert`（也可单独调用）。

### 版本目录结构

```text
.test-standards/<版本>/
├── input/
│   ├── prodword/           # 需求文档（.docx / .md 等）
│   │   └── prodword_pic/   # 需求图（流程图、泳道图、UI 截图等）
│   └── reference/          # 三方接口 / 联动 / 补充资料
└── output/
    ├── 01-定位.md
    ├── 02-变更分析.md
    ├── 03-测试概要.md
    ├── 04-测试用例.md
    └── <版本>.xmind
```

说明：

- `.test-standards` 根目录只初始化一次，不要在根下直接放 `input/` / `output/`。
- 每个迭代一个版本目录，互不影响。
- 本地代码知识库默认读项目下 `.dev-standards/`（业务文档 / codemap / service / procdefs）；**不是**活源码。

### `tc-gen`

结合「增量需求」与「全量知识库」，分 **5 个阶段**生成有证据链的测试产物；**每阶段结束后必须停下来等人确认**，禁止一次跑完。

核心原则：

- 本地需求 + `.dev-standards` 为主；`user-dev-standards` MCP **可选**，调不通则 fail-open，禁止重试卡死。
- 严禁用活源码（`.java` / `.xml` 等）替代知识库静态文档。
- 找不到默认知识库时必须询问用户：是否另有路径，或仅基于需求/接口降级继续。

#### 初始化版本

```text
tc-gen 初始化版本 V1.12.0-xxx
```

Agent 会通过 skill 内置 UTF-8 脚本创建目录（含中文版本名时优先 `--version-file`），不要用 PowerShell/`mkdir` 硬建中文路径。

初始化后请放入：

```text
input/prodword/      ← 需求文档
input/reference/     ← 接口与联动资料
```

#### 分阶段执行

```text
阶段0 准备：Word 转 md + 读输入 + 缺口驱动读图（可选 MCP 需求校验）
阶段1 定位：解析知识库路径 + 读业务文档/codemap/procdefs（MCP 可选）
阶段2 变更分析：需求 vs 业务现状（服务知识/MCP 可选）
阶段3 测试概要：过前置门禁后按 6 维度列测试点
阶段4 详细用例 + 回归清单 + 合并说明 + 自检
```

示例指令：

```text
tc-gen 对 V1.12.0-xxx 执行阶段0
tc-gen 继续 V1.12.0-xxx 阶段1
tc-gen 基于已确认的变更清单生成 V1.12.0-xxx 阶段3测试概要
tc-gen 为 V1.12.0-xxx 生成阶段4详细测试用例
```

#### 阶段要点（摘要）

| 阶段 | 产物 | 要点 |
|---|---|---|
| 0 | 对话摘要（确认后进 1） | 先全文再建图片缺口；按 P0–P3 分级读图；每轮最多 1 张视觉读；默认上限约 8 张 |
| 1 | `01-定位.md` | 匹配业务流程与 Handler；无知识库则停问用户 |
| 2 | `02-变更分析.md` | 新增/修改/波及老分支/三方接口；冲突单独列疑点 |
| 3 | `03-测试概要.md` | 6 维度测试点 + 偏离矩阵 + 维度用例预算参考表；门禁未过禁止生成 |
| 4 | `04-测试用例.md` | 一条用例 = 单路径 + 单组数据 + 单一预期；须合并说明清单与自检 |

阶段3 的 6 个维度：

1. 新功能正向  
2. 配置组合（判定表）  
3. 状态迁移  
4. 逐步骤功能操作偏离（重点，输出步骤 × 偏离矩阵）  
5. 接口与数据边界  
6. 回归影响（无 codemap 时标注降级推断，不可省略）

#### 用例表头（固定）

```markdown
| 用例等级 | 所属模块 | 用例标题 | 前置条件 | 用例步骤 | 预期结果 |
|---|---|---|---|---|---|
```

- `用例等级`：仅 `1` / `2` / `3` / `4`（核心主链路 → 择机补测）。
- `所属模块`：可用 `/` 分层，便于转 XMind。
- `前置条件`：非必填；转 XMind 后写入备注。
- `用例步骤` / `预期结果`：多步优先用 `<br>`；预期必须可断言。

细节见 `tc-gen/reference.md`（Word 转换、状态迁移、接口补充清单、操作偏离提问、回归分析等）。

### `tc-convert`

只做格式转换，不做测试设计。Skill 主路径是 **Markdown → XMind**；仓库内仍保留 `scripts/convert_to_md.py`，供阶段0 / 手工把 Word、Excel 转成 Markdown。

#### 测试用例 Markdown → XMind

```bash
python "<当前软件skills目录>/tc-convert/scripts/cases_to_xmind.py" ".test-standards/<版本>"
```

默认：

- 读：`.test-standards/<版本>/output/04-测试用例.md`
- 写：`.test-standards/<版本>/output/<版本>.xmind`

也可显式指定输入输出路径。

XMind 层级要点：

- 根节点：版本名（逻辑图向右）。
- 中间层：`所属模块` 按 `/` 拆分。
- 用例标题可再按 `/` 拆父/子节点；等级映射为 `priority-1`～`priority-4`。
- 步骤合并为一个子节点；预期结果按中文分号 `；` 拆成编号子节点。

#### Word / Excel → Markdown（脚本）

```bash
python "<当前软件skills目录>/tc-convert/scripts/convert_to_md.py" ".test-standards/<版本>/input/prodword"
```

- `.docx` → 同名 `.md`，图片抽到 `prodword_pic/`
- `.xlsx` → Markdown 表格
- 保留原始文件不删除

阶段0也可按 `tc-gen/reference.md` § 一优先用 pandoc / mammoth 等工具。

### 推荐工作流（测试）

1. `tc-gen 初始化版本 V1.12.0-xxx`
2. 放入 `input/prodword/`、`input/reference/`
3. 逐阶段执行 0→4，每阶段确认后再继续
4. `tc-convert` 将 `04-测试用例.md` 转为 `<版本>.xmind`

使用建议：

- `tc-gen` 负责分析与设计，`tc-convert` 只负责转换。
- 流程图 / 泳道图 / 时序图对阶段3偏离矩阵很重要；阶段0要按缺口读图，不要无差别通读全部 UI 截图。
- 阶段3门禁未满足时不要直接生成概要。
- 阶段4保持原子用例，方便评审与转 XMind。

---

## 前端落地：`pic-to-vue`（触发语 `proto-to-vue`）

把原型图落到低代码业务 `.vue`（`link-ui-web` / `lls-*`）。目录名为 `pic-to-vue`，正文与触发语常用 **`proto-to-vue`**。

工作流：

```text
读原型 → 定页面类型 → 最多对照 1～2 个参考页 → 对齐同目录兄弟约定 → 一次写完 → 说明假设
```

页面类型三选一：列表 / 多步编辑表单 / 只读详情。

常见输入：

```text
<template或版本目录>/图片样式/*.png
<template或版本目录>/目标.vue          # 可为空，直接覆盖写入
```

可选说明：「样式参考 bccp-business-front」。同目录已有兄弟 `.vue` 时，**优先对齐兄弟**（`$api`、`eventTriggers`、`lls-*` 等）。

硬性退出条件（满足即可停，禁止为「再像一点」整页重写）：

1. 目标 `.vue` 已写入且非空  
2. 分区 / 步骤 / 表格列 / 主操作与原型一致（不必像素级）  
3. 组件库与请求约定与兄弟页一致  
4. `financeType` 等未明时：字段齐全 + 预留过滤钩子即可  

参考样例优先从 `bccp-business-front/src/` 按类型各取 1～2 个（列表、多步壳、导入弹窗等），细则见 `pic-to-vue/reference.md`。

Windows 列中文目录请用 Python，避免 PowerShell 乱码：

```bash
python -c "import os,json; print(json.dumps(os.listdir(r'<绝对目录>'), ensure_ascii=False))"
```

示例触发语：

```text
参考 template/图片样式，在 template/index_template_.vue 写页面，样式参考 bccp-business-front
根据 credit/V1.15.0/我的模板.png 写列表
proto-to-vue 实现某某页
```

---

## 仓库目录一览

```text
TestCases-Gen/
├── README.md
├── update-local-skills.bat   # 拉取并同步全部 skill
├── tc-gen/
│   ├── SKILL.md
│   ├── reference.md
│   └── scripts/
│       ├── init_version_utf8.py
│       └── list_version_inputs_utf8.py
├── tc-convert/
│   ├── SKILL.md
│   └── scripts/
│       ├── cases_to_xmind.py
│       └── convert_to_md.py
└── pic-to-vue/
    ├── SKILL.md              # 正文标题：proto-to-vue
    └── reference.md
```

脚本路径不要写死某一 IDE 私有目录；以**本 skill 安装目录**或**当前软件 skills 根目录**解析绝对路径后再执行。

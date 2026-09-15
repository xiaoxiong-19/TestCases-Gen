# TestCases-Gen Skills 使用说明

本仓库同步到 Cursor / Trae / Codex 的本地 Skills：

| Skill 目录 | 触发语 | 用途 |
|---|---|---|
| `tc-gen/` | `tc-gen`、初始化版本、生成测试概要/用例、转 XMind、md to xmind、变更影响分析、精准回归 | 版本迭代：分阶段生成有证据链的测试概要与测试用例；阶段4完成后询问，用户同意后再转 XMind |

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

## 测试提效：`tc-gen`

为项目新需求生成高质量测试概要与测试用例。**分 5 个阶段，每阶段产出后必须停下来等用户确认，禁止一次性走完。**

主依据是**本地需求文档 + 本地代码知识库（`.dev-standards`）**。`user-dev-standards` MCP 为可选增强，**不强制调用**。MCP 不可用、调不通、超时或无匹配时：记录一次原因后 fail-open 回退本地流程，禁止重试/等待/卡死。

细节以 `tc-gen/SKILL.md` 为准；转换、状态迁移、接口补充、偏离提问、回归分析、XMind 见 `tc-gen/reference.md`。

### 核心原则

- **需求文档只写增量，知识库写全量。** 有知识库时必须结合两者：既测新功能，又不漏被影响的老功能。
- **本地知识库优先，MCP 可选。** 最终以本地业务文档、代码地图、流程定义和接口文档全文为准。
- **接地气且可追溯。** 测试点必须有证据链（需求变更项、业务文档章节、状态机/配置/通知矩阵、接口字段、codemap Handler）。禁止编造泛泛用例。
- **人工卡点。** 每阶段结束输出「请确认是否继续」。
- **版本隔离。** 每个迭代独立放在 `.test-standards/<版本>/`；根目录只初始化一次，不在根下直接放 `input/` / `output/`。
- **严禁以活源码替代知识库。** `codemap` / 业务文档 / `procdefs` 都是 `.dev-standards` 下预先沉淀的静态文档，不是 `.java` / `.xml` / `.yml`。用例依据是「系统应该做什么」，不是「代码现在怎么写」。

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
    └── <版本>.xmind         # 阶段4后用户同意才生成
```

说明：

- 初始化只补齐缺失子目录，不删除、不覆盖已有输入或阶段产物。
- 用例格式用 skill 内置模板；执行 `tc-gen` 时不必再读 `.test-standards/templates/测试用例模板.md`。
- 本地代码知识库默认：`.dev-standards/knowledge/business/`、`codemap/`、`service/`、`procdefs/`（存在则读，不存在不强求齐全）。
- 找不到默认知识库时必须询问：是否另有路径，或仅基于需求/`input/reference/` 降级继续。用户未确认前不得读活源码冒充定位。

### 脚本路径与中文版本名

- 脚本一律相对 **本 skill 安装目录**（含 `SKILL.md` 的目录），不要写死 `.cursor/skills/...`。
- Word/Excel → md、用例 md → XMind 都在 `tc-gen/scripts/`，**已无独立 `tc-convert` skill**。
- 版本目录操作必须走 UTF-8 脚本，禁止 PowerShell/`mkdir`/`New-Item`/`python -c` 硬建中文路径。
- **目录尚不存在**且版本名含中文：版本名写到系统临时目录 UTF-8 文件首行，再用 `--version-file`。禁止把该文件写进项目或 `.test-standards/`。
- **目录已存在**（发现输入、转换、转 XMind、补目录）：含中文时优先 `--version-prefix`（ASCII 前缀能唯一匹配即可）。
- 纯 ASCII 版本名可直接传 `"<版本>"` 位置参数。

### 初始化版本

```text
tc-gen 初始化版本 V1.12.0-xxx
```

只建目录，不进入阶段0。Agent 调用：

```bash
python "<本skill目录>/scripts/init_version_utf8.py" "<项目根目录>" "<版本>"
```

初始化后请放入：

```text
input/prodword/      ← 需求文档
input/reference/     ← 接口与联动资料
```

`prodword_pic/` 由转换流程抽图，也可手工补流程图原图。

### 分阶段执行

```text
阶段0 准备：Word 转 md + 读输入 + 缺口驱动读图（可选 MCP 需求校验）
阶段1 定位：解析知识库路径 + 读业务文档/codemap/procdefs（MCP 可选）
阶段2 变更分析：需求 vs 业务现状（服务知识/MCP 可选）
阶段3 测试概要：过前置门禁后按 6 维度列测试点 + 预算参考表
阶段4 详细用例 + 回归清单 + 合并说明 + 自检；询问是否转 XMind
```

示例指令：

```text
tc-gen 对 V1.12.0-xxx 执行阶段0
tc-gen 继续 V1.12.0-xxx 阶段1
tc-gen 基于已确认的变更清单生成 V1.12.0-xxx 阶段3测试概要
tc-gen 为 V1.12.0-xxx 生成阶段4详细测试用例
```

#### 阶段要点

| 阶段 | 产物 | 要点 |
|---|---|---|
| 0 | 对话摘要（确认后进 1） | 先用 UTF-8 脚本列文件，禁止用 Glob 空结果当「没放文件」。docx/xlsx 必须走内置转换。先读全文建图片索引与缺口，再按 P0–P3 视觉读图 |
| 1 | `01-定位.md` | 匹配业务流程与 Handler；无知识库则停问用户，禁止拿活源码顶替 |
| 2 | `02-变更分析.md` | 新增 / 修改 / 波及老分支 / 三方接口；冲突单独列疑点 |
| 3 | `03-测试概要.md` | 6 维度测试点 + 偏离矩阵 + 维度用例预算参考表；门禁未过禁止生成。未调 MCP 不构成门禁失败 |
| 4 | `04-测试用例.md` | 一条用例 = 单路径 + 单组数据 + 单一预期；等级1为少量正向冒烟；须合并说明与自检；**先问再转 XMind** |

阶段3 的 6 个维度：

1. 新功能正向（阶段4里只有少数正向主流程标等级1，其余正向细节标 2）
2. 配置组合（判定表）
3. 状态迁移（正常 + 退回/拒绝）
4. 逐步骤功能操作偏离（重点，输出步骤 × 前 6 类偏离矩阵；单元格只写「场景 + 断言方向」）
5. 接口与数据边界
6. 回归影响（无 codemap 时标注降级推断，不可省略）

阶段0 读图硬闸（防止漏测也防止卡死）：

- P0：流程/状态/结构专图，或正文以该图为准 → 必须读
- P1：正文写不清的验收点（字段/按钮/分支/校验）→ 必须读
- P2：正文已写清、图仅示意 → 预算剩余才读
- P3：装饰/未引用/纯重复 → 不读
- 同一轮最多视觉读 **1** 张图；读完先写可见要点再读下一张
- 阶段0 默认上限 **8** 张（P0+P1 优先）；未读完的 P1 必须列出待补读及风险
- 禁止按 `image1…N` 无差别通读；禁止只读字假装图不存在

阶段0 开始前必须先跑：

```bash
python "<本skill目录>/scripts/list_version_inputs_utf8.py" "<项目根>" --version-prefix "V1.0.0-saas"
```

以脚本 JSON 中的绝对路径为准。Glob 找不到但脚本找得到时，以脚本为准。

#### 用例表头（固定）

```markdown
| 用例等级 | 所属模块 | 用例标题 | 前置条件 | 用例步骤 | 预期结果 |
|---|---|---|---|---|---|
```

- `用例等级`：阶段4默认只用 `1` / `2` / `3`（转换脚本仍识别 `4`，一般不用，低风险归入 3）。
  - `1` 冒烟：本期新增正向主流程，宜少（一般 1～3 条）
  - `2` 重要/关键规则（配置组合、错误码、关键通知等）
  - `3` 其余（边界、格式、操作偏离细节、次要异常）
- `所属模块`：可用 `/` 分层，便于转 XMind。
- `前置条件`：非必填；转 XMind 后写入备注。
- `用例步骤` 多步优先 `<br>`；`预期结果` 多条断言用中文分号 `；` 分隔。
- 标题里不要手写 `【等级N】`；不要把「示例：」样例行写入产物表。

阶段4 裂变要点：

- 正反例、等价类、边界值、枚举逐值、条件必填、接口单字段破坏，各成一条。
- 用例总数明显低于测试点数 × 2 时要自查是否未裂变；低风险同质可合并，但必须写入 **合并说明清单**（无合并也要写「本次无合并/裁剪项」）。
- 资金/错误码处理/强监管/终态等为高风险，不得合并。
- 维度5 有文档则展开：错误码逐值、Dubbo 传参规则、落库字段、通知要素；没有对应文档时预算填 0，不要编造。

### MCP（可选，调不通必须 fail-open）

不是流程前置条件。同一会话每个 MCP 工具最多尝试 **1** 次；失败立即回退本地文档。工具列表没有 `user-dev-standards` 或读不到 schema 时直接跳过。

可选工具：`get-business-rule`（阶段1）、`validate-requirement`（阶段0/2 前）、`get-service-knowledge`（阶段2/3）、`query-standard`（规范风险时）。`projectPath` 禁止写死盘符，从当前 workspace 根推断。

### 测试用例 Markdown → XMind（阶段4之后，须用户同意）

写出 `04-测试用例.md` 并完成自检后，Agent **先询问**是否转 XMind，禁止同一回合自动转。用户回复同意类话术（如「转 XMind」「同意」「转脑图」）后再执行；只说「继续」而未提转换时不要转。

```bash
python "<本skill目录>/scripts/convert_cases_to_xmind_utf8.py" "<项目根>" --version-prefix "V1.6.1"
```

默认：

- 读：`.test-standards/<版本>/output/04-测试用例.md`
- 写：`.test-standards/<版本>/output/<版本>.xmind`

阶段4尚未产出 md 时禁止转。后续单独说「把该版本转 XMind」且 md 已存在，视为同意，可直接调脚本。表头不符时先改 md 再转，禁止自写 XMind 转换器。

XMind 层级要点：

- 根节点：版本名；结构固定为逻辑图向右（`org.xmind.ui.logic.right`）。
- 中间层：`所属模块` 按 `/` 拆分。
- 用例标题可再按 `/` 拆父/子节点；起始父节点 `task-done`，末级按等级 `priority-1`～`priority-4`。
- 全部步骤合并为一个多行子节点；预期结果按中文分号 `；` 拆成 `1、xxx`、`2、yyy` 挂在步骤节点下。
- `前置条件` 写入末级用例节点备注。
- 只识别固定六列表头；脚本只做格式转换，不改业务语义。

### Word / Excel → Markdown（阶段0 内置脚本）

阶段0 发现 `.docx` / `.xlsx` 后必须走版本 wrapper（同时转 prodword 与 reference，图片统一进 `prodword_pic/`）：

```bash
python "<本skill目录>/scripts/convert_version_inputs_utf8.py" "<项目根>" --version-prefix "V1.6.1"
```

单目录手工转换：

```bash
python "<本skill目录>/scripts/convert_to_md.py" ".test-standards/<版本>/input/prodword"
```

- `.docx` → 同名 `.md`，图片抽到 `prodword_pic/`（含表格内图片）；表格必须仍是 Markdown 表
- `.xlsx` → Markdown 表格（单元格 `|` 会转义）
- `.doc` / `.xls` 不转，需另存为 `.docx` / `.xlsx` 后重跑
- 保留原始文件不删除
- 依赖：`pip install -r "<本skill目录>/scripts/requirements.txt"`
- **不要**用 pandoc / mammoth 或现场编写转换脚本（mammoth 会把 Word 表格展平）
- **禁止**在项目或 `.test-standards/` 下新建 `_convert_*.py`、`_version_name_utf8.txt`

### 推荐工作流

1. `tc-gen 初始化版本 V1.12.0-xxx`
2. 放入 `input/prodword/`、`input/reference/`
3. 逐阶段执行 0→4，每阶段确认后再继续
4. 阶段4结束后，若同意转脑图，再生成 `<版本>.xmind`

使用建议：

- 流程图 / 泳道图 / 时序图对阶段3偏离矩阵很重要；阶段0按缺口读图，不要无差别通读全部 UI 截图。
- 阶段3门禁未满足时不要直接生成概要；MCP 失败不是门禁失败。
- 阶段4保持原子用例，方便评审与转 XMind；有合并必须写合并说明。
- 不要在用户未同意时自动转 XMind。

---

## 仓库目录一览

```text
TestCases-Gen/
├── README.md
├── update-local-skills.bat   # 拉取并同步全部 skill
└── tc-gen/
    ├── SKILL.md
    ├── reference.md
    └── scripts/
        ├── init_version_utf8.py
        ├── list_version_inputs_utf8.py
        ├── convert_version_inputs_utf8.py  # 阶段0：docx/xlsx → md
        ├── convert_to_md.py
        ├── convert_cases_to_xmind_utf8.py  # 阶段4后用户同意：md → xmind
        ├── cases_to_xmind.py
        ├── utf8_paths.py                   # 版本路径/UTF-8 公共逻辑
        └── requirements.txt                # python-docx、openpyxl
```

脚本路径不要写死某一 IDE 私有目录；以**本 skill 安装目录**解析绝对路径后再执行。

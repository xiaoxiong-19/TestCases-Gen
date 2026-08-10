---
name: pic-to-vue
description: >-
---

# proto-to-vue：原型图 → Vue

按「读原型 → 定类型 → 少样例对照 → 一次写完」落地页面。**禁止**为「再确认一下」全库扫 `bccp-business-front` 或整页反复重写。

## 触发与输入

用户通常给出：

```text
template/图片样式/*.png          # 或 <业务目录>/<版本>/某某.png
template/index_template_.vue     # 或同目录目标 .vue（可能为空）
```

可选说明：「样式参考 bccp-business-front」。同目录已有兄弟 `.vue` 时，**优先对齐兄弟文件约定**。

## 硬性退出条件（防死循环）

完成以下即可结束：

1. 目标 `.vue` 已写入且非空
2. 分区 / 步骤 / 表格列 / 主操作与原型一致（不必像素级）
3. 组件库、请求方式、事件约定与同目录兄弟页一致
4. `financeType` 等规则未定时：字段齐全 + 预留过滤钩子即可，不空转

识图冲突、规则未明、参考页找不到 **都不阻塞**：拍板写完，结束时一两句话说明假设。

## 工作流

```text
- [ ] 1. 定位输入输出文件
- [ ] 2. 读原型，抽出结构清单 + 判定类型
- [ ] 3. 只选 1～2 个参考页
- [ ] 4. 对齐同目录兄弟页约定
- [ ] 5. 一次写出完整 .vue
- [ ] 6. 语法抽查 + 说明假设
```

### 1. 定位文件（Windows 中文名）

PowerShell 列中文会乱码。用：

```bash
python -c "import os,json; print(json.dumps(os.listdir(r'<绝对目录>'), ensure_ascii=False))"
```

目标 vue 可为空，直接覆盖写入。多张原型图时**按文件名步骤顺序**读完再编码，不要边读边半写。

### 2. 读原型 → 结构清单 → 定类型

| 区域 | 记录什么 |
|------|----------|
| 标题 | 页头文案、是否返回 |
| 步骤 | 有无 `lls-steps`；几步；每步标题 |
| 分区 | 折叠灰头：申请人 / 信用证 / 贸易 / 交单 / 费用 / 其他… |
| 字段 | 每格：label、必填、控件类型（input/select/textarea）、后缀（% / 元）、禁用态 |
| 布局列数 | 多为 **顶标签三列栅格**；长文本是否整行 |
| 底栏 | 取消 / 暂存 / 上一步 / 下一步 / 提交 |
| 详情 vs 编辑 | 详情：无步骤条、只读、空值 `--` |

**三选一页面类型：**

| 类型 | 特征 | 写什么 |
|------|------|--------|
| 列表 | 搜索 + 表 + 分页 | 见下文「列表页要点」 |
| 多步编辑表单（向导） | 顶部 steps + 分步分区 + 底栏 | 见「多步表单要点」 |
| 只读详情 | 无 steps、分区全在一页、不可编辑 | 见「详情页要点」 |

识图矛盾时：同业务语义优先（开证/信用证），搜索字段与表格列互证，拍板后不再二次全图 OCR。

### 3. 定类型 → 少样例对照

`bccp-business-front` 是**组件库**，不是业务站。最多打开 **1～2** 个：

| 页面类型 | 优先参考（均在 `bccp-business-front/src/`） | 学什么 |
|----------|---------------------------------------------|--------|
| 列表 | `components/contractTemplate/components/ContractList.vue` | 搜索、表、分页 |
| 简单 CRUD 列表 | `components/emailManage/index.vue` | page-header + 表 |
| 多步壳子 | `components/caServiceFeePayment/index.vue` | `lls-steps` + 分步 + 底栏 |
| 分区灰头 + 返回 | `components/contractTemplate/components/AddTemplate.vue` | `lls-page-header`、`lls-collapse` |
| 表单项后缀/%/tooltip | `components/capitalPartnerRuleDynamicForm/components/RuleDynamicField.vue` | `slot="append"`、`lls-tooltip` |
| 导入三步弹窗 | `components/apaasInvoice/.../uploadImportDialog.vue` | alert + upload + 结果页（导入场景） |
| 只读详情 | **同目录编辑页字段复用**；无兄弟则新建详情文件 | 三列只读、折叠分区 |

更细映射见 [reference.md](reference.md)。

### 4. 对齐兄弟页约定

| 信号 | 约定 |
|------|------|
| `$api.post(...)` | 用低代码全局 `$api`，勿 axios 直连 |
| `eventTriggers` / `events` | 保留给设计器 |
| `designMode` / `parent` | 按兄弟页抄 |
| 仅用 `lls-*` | 禁止擅自换成 `el-*` |
| 无深层 import | 全局组件；子组件可同文件内联 |

`financeType` 未定时：保留 `props.financeType` / `setFinanceType`、字段上可选 `financeTypes: []`，`filterFields` 先全量展示。

### 5. 一次写出完整 Vue

#### 多步表单要点（本会话主路径）

1. 页头返回 + 标题；`lls-steps`；`activeStep` 切换内容
2. 分区：灰头 + 右侧箭头，可折叠（自绘 `section` 即可，不必硬上 collapse）
3. 普通字段：**顶标签 + CSS Grid 三列**（见 reference 栅格写法）
4. **长文本（受益人应提交单据 / 其他条款）禁止仍放在三列 grid 里随格排版** → 单独 `presentation-summary` / `detail-stack` 整行，否则会「跑到右边」
5. `lls-input` 多行 **原生 placeholder 多行不可靠**：空值时用浮层文案动态展示提示；**不要**把提示写进 `form` 当默认值
6. 后缀用 `slot="append"`（`%` / `元`）；问号旁注用 `lls-tooltip` + `lls-icon-question2`
7. 底栏：取消 / 暂存 / 上一步 / 下一步（末步可提交）；可 fixed
8. 校验：用兄弟页同环境的 `vue-template-compiler` 编译 template + `new Function` 过 script

用户说「增加高度」只动 `min-height` / `rows`，**不要**趁机改 `width` / `grid-column`。

#### 详情页要点

1. 与编辑页字段同源，**去掉步骤条**，所有分区一页纵向排列
2. 只读：label 上、值下；空值固定 `--`；选项字段字典转中文
3. 长文本只读：保留换行 `white-space: pre-wrap`；**不要**做成大边框容器（用户会当成弹框）
4. **样式类名必须带页面前缀**（如 `lc-detail-*`）。禁止 `detail-value` / `detail-item` / `detail-grid` 等通用名——会被 link-ui / 低代码全局 CSS 覆盖，表现为「改了不生效 / 空值居中」
5. 用 `scoped` 或根节点强限定（`.lc-template-detail .lc-detail-value`）；不要幻想用通用类 + `!important` 打赢全局样式

#### 列表页要点

- `lls-page-header`；查询 `primary plain` / 重置 `info plain`
- 行操作 `lls-button type="text" size="small"`
- 分页始终渲染（含「共 0 条」）；空单元格 `--`

**写完即停。** 禁止再扫组件库、再 crop 识图、为「更像」整文件推倒重来。

### 6. 回复用户

简短说明：对齐了哪些块、参考了哪个文件、接口/`financeType` 等假设。

## 反模式（禁止）

- 全库列 `bccp-business-front` vue 再开工；同时开 5+ 参考页
- 把「占位提示」写入 form 默认值当真数据
- 长文本仍塞三列 grid → 布局跑偏后再用 `span 3 !important` 补锅
- 用户要「加高度」却改宽度 / 跨列
- 详情页用通用 class 名导致全局覆盖，然后反复拧 `text-align`
- PowerShell 硬啃中文路径；识图冲突进入第三轮全局 OCR

## 示例触发语

- 「参考 template/图片样式，在 template/index_template_.vue 写页面，样式参考 bccp-business-front」
- 「再写一个查看详情页 template/查看模板详情页.vue」
- 「根据 credit/V1.15.0/我的模板.png 写列表」
- 「proto-to-vue 实现某某页」

## 附加

- 组件 / 栅格 / placeholder / class 隔离细则：[reference.md](reference.md)
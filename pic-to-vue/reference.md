# proto-to-vue 参考映射

配合 [SKILL.md](SKILL.md)。需要选参考页时只查本表，**不要**全库枚举。

## bccp-business-front 是什么

- 路径：工作区 `bccp-business-front/`
- 性质：**低代码可复用组件库**，不是信用证业务站
- 真业务页多在蜂搭 `.lcpage`；`src/components/<Name>/` 是积木
- `src/views/` 只有登录/首页壳，一般不当业务参考
- UI：`link-ui-web`，组件前缀 **`lls-*`**；全局 `Vue.use(LinkUI)`

## 怎么「参考样式」（实操）

1. **先定类型**（列表 / 多步表单 / 详情）→ 只打开上表对应 1～2 文件
2. **抄交互骨架，不抄业务字段**：steps 写法、灰头分区、底栏按钮 type、表单项 suffix、上传流转
3. **布局数字跟原型**：三列、顶标签、分区顺序；颜色主色可用 `#2664FD` / 工程 primary
4. **同目录兄弟页优先于远程参考**（`$api`、eventTriggers、headers）
5. 写完用 `vue-template-compiler` 对单文件做一次 compile 校验即可

```bash
# 在已安装 vue-template-compiler 的工程下
node -e "const fs=require('fs');const c=require('vue-template-compiler');const s=fs.readFileSync('<vue路径>','utf8');const p=c.parseComponent(s);const r=c.compile(p.template.content);if(r.errors.length){console.error(r.errors);process.exit(1)};new Function(p.script.content.replace(/export default/,'return'));console.log('OK')"
```

## 列表页

| 需求特征 | 打开这个 | 抄什么 |
|----------|----------|--------|
| 搜索 + 表 + 分页 + 行操作 | `components/contractTemplate/components/ContractList.vue` | 查询重置、`lls-table`、右操作列、`lls-pagination` |
| 页头 + 简单查询 | `components/emailManage/index.vue` | `lls-page-header`、inline form |
| 行内查询重置 | `components/saasSpUserManage/components/userInfo.vue` | 按钮排布 |
| 漏斗搜索条 | `bccpBasicComponents/llsLowcodeSearchs/lowcodeSearchs.vue` | form-box + btn-box；不能 import 则同等布局自绘 |

列表约定：行操作 `type="text" size="small"`；分页 `layout="total, prev, pager, next, sizes, jumper"`；空单元格 `--`。

## 多步表单 / 分区表单

| 需求特征 | 打开这个 | 抄什么 |
|----------|----------|--------|
| 三步向导壳 | `components/caServiceFeePayment/index.vue` | `lls-steps`、`v-if` 分步、底栏 |
| 返回 + 折叠分区 | `components/contractTemplate/components/AddTemplate.vue` | `lls-page-header`、`lls-collapse` |
| 金额后缀 / tooltip | `components/capitalPartnerRuleDynamicForm/components/RuleDynamicField.vue` | `slot="append"`、`lls-tooltip` |
| Excel 导入步骤 | `components/apaasInvoice/.../uploadImportDialog.vue` | alert 下载模板 + upload + 结果 |

### 三列顶标签栅格（推荐自绘）

```less
.form-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(220px, 1fr));
  column-gap: 46px;
}
.form-input, .lls-select { width: 100%; }
```

模板侧：`lls-form label-position="top"`，每个字段包一层 cell。

### 长文本字段（必守）

原型里的「受益人应提交单据」「其他条款」等：**不要**继续放在三列 `form-grid` 的下一个 cell。

- 编辑页：`presentationPeriod` 等短字段可留在 grid；长 textarea 挪到 grid **下方**独立块，宽度 100%
- `lls-input type="textarea"` 的多行 placeholder 经常不显示 → 空值时在 wrap 上叠一层 `.textarea-placeholder { white-space: pre-wrap; pointer-events: none; color: #c0c4cc }`
- **禁止**把提示文案赋进 `v-model`；`createEmptyForm` 里也不要写入默认长文

### financeType 预留

```js
filterFields(fields) {
  return fields.filter(f => {
    if (!Array.isArray(f.financeTypes) || !f.financeTypes.length) return true;
    return f.financeTypes.indexOf(this.currentFinanceType) >= 0;
  });
}
```

规则未定时全部展示；规则明确后再给字段加 `financeTypes: ['NBCB', ...]`。

### 用户措辞对照（防改错）

| 用户说 | 正确动作 | 错误动作 |
|--------|----------|----------|
| 不输入时展示某段说明 | placeholder / 浮层提示 | 写入 form 默认值 |
| 增加输入框高度 | `rows` / `min-height` | 改 width、跨列 |
| 跑到右边了 | 长文本移出三列 grid | 继续 `grid-column: span 3 !important` 硬撑 |
| 不用弹框 | 去掉边框容器 / 固定大框观感 | 做成 modal 或像输入框的灰框 |

## 只读详情页

优先：复制编辑页字段清单，去掉 steps 与表单控件。

| 点 | 做法 |
|----|------|
| 布局 | 各分区纵向叠放；灰头可折叠；无底栏或仅返回 |
| 普通字段 | 三列栅格；label 灰、值黑；空 → `--` |
| 交单/其他长文本 | **独立纵向 stack**，与费用三列同页但不同容器 |
| 字典 | select 值用 options 转 label |
| 多行 | `white-space: pre-wrap`，不要再画边框盒 |

### Class 命名隔离（本会话踩坑总结）

| 会踩雷 | 原因 | 正确 |
|--------|------|------|
| `.detail-value` `.detail-item` `.detail-grid` | 与 link-ui / 低代码全局同名，本地改了「不生效」、空值变居中 | `.lc-detail-value` `.lc-detail-item` … |
| 详情与编辑共用一套无前缀 class | 互相污染 | 编辑用 `meta-credit-*` / `field-cell`；详情用 `lc-detail-*` |
| 全局 `!important` 打补丁 | 越改越乱 | 换唯一前缀 + 根节点 `.lc-template-detail` 限定 |

## 组件库约定（lls）

| 用 | 不用（除非目录已全是 el） |
|----|---------------------------|
| `lls-page-header` / `lls-steps` / `lls-step` | `el-*` 同名 |
| `lls-input` / `lls-select` / `lls-option` | |
| `lls-form` / `lls-form-item` / `lls-button` | |
| `lls-table` / `lls-pagination` / `lls-checkbox` / `lls-radio` | |
| `lls-tooltip` + `lls-icon-question2` | 自造问号 |

金额后缀示例：

```html
<lls-input v-model="form.fee">
  <span slot="append">元</span>
</lls-input>
```

## 低代码草稿骨架（有兄弟页时对齐）

```js
export default {
  eventTriggers: [
    { label: '取消', value: 'handleCancel' },
    { label: '暂存', value: 'handleSave' },
  ],
  events: [
    { label: '取消', value: 'handleCancel', hasParams: false },
    { label: '暂存', value: 'handleSave', hasParams: true },
  ],
  props: {
    designMode: { type: [Object, String, Boolean], default: false },
    parent: { type: Object, default: () => ({}) },
    financeType: { type: String, default: '' },
    detailData: { type: Object, default: () => ({}) },
  },
};
```

普通业务页无设计器时，可省略 `eventTriggers`，用 `$emit('cancel'|'save'|'submit'|'back')`。

## 本会话范例收口

| 产物 | 类型 | 要点 |
|------|------|------|
| `template/index_template_.vue` | 多步编辑 | 步骤：开证→贸易→交单；分区灰头；三列 + 长文本独立块；placeholder 浮层 |
| `template/查看模板详情页.vue` | 只读详情 | 无 steps；全分区一页；空 `--`；`lc-detail-*` 防全局覆盖 |

参考上限：`caServiceFeePayment`（壳）+ `AddTemplate`（分区头）+ 同目录编辑页（字段）。写完即停。

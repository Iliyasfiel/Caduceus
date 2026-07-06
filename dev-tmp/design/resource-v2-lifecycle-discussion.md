# 资源库 v2 — 灯具维护场景讨论与方向草案

> **草案状态**：❌ 未批准。**仅供你和客户内部探讨**，不是终稿设计文档。
>
> 本文件来源于一次 brainstorming 讨论，目标是：
> 1. 厘清资源库 v2 应该干什么 / 不应该干什么（避免变成传统资产管理）；
> 2. 让资源实体的状态变化能融入"任务 ↔ 人 ↔ 资源"的信息流；
> 3. 给客户看的**可讨论版本**，不是已经决定的设计。
>
> 待与客户对齐后，再由本文件提炼出**终稿设计文档**（路径 `docs/superpowers/specs/YYYY-MM-DD-resource-v2-lifecycle-design.md`），并合并进 [`designingDocument/caduceus-design.md`](../../designingDocument/caduceus-design.md) 与 [`caduceus-prd.md`](../../designingDocument/caduceus-prd.md)。
>
> 存放原因：依项目规则 [`dev-tmp/design`](./README.md) 用于"待讨论的设计草稿"，不会污染正式文档，也不会推送到远程仓库。
>
> 顶层索引：[`dev-tmp/README.md`](../README.md)

---

## 1. 业务背景

**演艺公司的舞台灯光设备**，是这次讨论的具体场景。

- 灯具**单价贵**（动辄几千到几万）、**寿命有限**、**需要专业维护**
- 现状：客户用非常原始的方式管理（纸 / Excel / 微信群），**资产管理**和**维护业务**是断开的
- 客户希望："打通资产管理和灯具维护之间的链条"

**Caduceus 项目的定位是"轻量化、客制化的协同工作平台"**（[`caduceus-prd.md` §3.4](../../designingDocument/caduceus-prd.md)），资源库被定义为：

> "可复用的信息库，管理员可自定义资源类型和字段。资源库延续管线的用户自定义思想。"

也就是说：**资源库不应该是资产台账**，它应该是事件的载体、协作的中枢。

> 如果将来客户真的需要完整的资产管理（折旧、采购、备件库、供应商管理），系统应当引导他去用专业 EAM 系统，而不是让 Caduceus 越加越厚。

---

## 2. 已澄清的几条（讨论过程中明确下来的）

1. **资源库定位 = 事件流载体**，不做资产台账；管理员如果需要可加文本字段，但系统不假定、不背书、不索引、不校验。
2. **业务动作 = 任务**，走管线编辑器；不试图把"借用""编排""巡检"塞进资源库。
3. **资源状态变化 ≈ 业务动作的副产品**——**80%** 的状态变化由任务完成触发。
4. **剩下 20% 不是任务来的**：资产入库（人工登记）、太久没维护报警（系统自动）、超过使用寿命（系统自动）、外部信号（扫码枪/将来第三方对接）等。这些入口必须存在，且写出来的 ResourceLog 格式与任务触发**完全一致**。
5. **资源模板 = 客制化**，与管线模板同一种心智模型——**管理员画，不是系统预设**。
6. **整体关注三种交互**：任务 ↔ 人、任务 ↔ 资源、资源 ↔ 人。但**不预先合并数据模型**——具体怎么呈现等终稿设计时再明确。

> ⚠️ **讨论中未澄清的表述**："任务执行人的操作动作 ≈ 资源实体的状态变化，在信息流上等价"——这句话的具体含义在讨论中**几次都没有对齐**，建议先按本草案方向走，等客户反馈后再回头校准这句。

---

## 3. v1 草案：资源模板走"独立画布"（推荐方向 B）

> 草案给了三种走法（A 复用管线画布 / B 独立画布 / C 表单），**推荐 B**。下面只展开 B 的细节。A/C 放在 §6 备查。

### 3.1 资源模板结构（lifecycle_config 升级）

保留现有 `ResourceType.lifecycle_config` JSONB 字段，**新增结构**：

```jsonc
{
  "schema_version": 1,
  "states": [
    { "id": "available",  "name": "可用",     "tone": "success", "is_initial": true  },
    { "id": "in_use",     "name": "使用中",   "tone": "info"                       },
    { "id": "maintenance","name": "维修中",   "tone": "warning"                    },
    { "id": "retired",    "name": "已封存",   "tone": "muted"                      }
  ],
  "events": [
    {
      "id": "picked_up",
      "name": "出库使用",
      "from_states": ["available"],
      "to_state": "in_use",
      "triggers": {
        "from_task": true,
        "manual": true,
        "scheduled": false,           // 暂不实现，先占位
        "external": false             // 暂不实现，先占位
      },
      "notify_roles": ["equipment_admin", "operator"],
      "details_schema": [
        { "key": "borrower",          "label": "借用人",       "type": "user_picker" },
        { "key": "expected_return",   "label": "预计归还",     "type": "date"        }
      ]
    },
    {
      "id": "maintenance_started",
      "name": "进入维修",
      "from_states": ["in_use", "available"],
      "to_state": "maintenance",
      "triggers": { "from_task": true, "manual": true, "scheduled": false, "external": false },
      "notify_roles": ["equipment_admin", "maintainer"],
      "details_schema": [
        { "key": "fault_desc",  "label": "故障描述",  "type": "text"         },
        { "key": "maintainer",  "label": "维修人",    "type": "user_picker" }
      ]
    },
    {
      "id": "maintenance_done",
      "name": "维修完成",
      "from_states": ["maintenance"],
      "to_state": "available",
      "triggers": { "from_task": true, "manual": true, "scheduled": false, "external": false },
      "notify_roles": ["equipment_admin"],
      "details_schema": [
        { "key": "parts_used",       "label": "更换部件",  "type": "text" },
        { "key": "next_inspection",  "label": "下次巡检",  "type": "date" }
      ]
    }
  ]
}
```

**两个关键设计**：

1. **状态机声明式**：states + events 是一张图，管理员**画**出来（由画布自动生成 JSON），而不是手写。
2. **每种触发方式独立 flag**：`triggers.from_task / manual / scheduled / external`，未来加新触发器不影响现有数据。

### 3.2 画布 UI 怎么画（与管线编辑器一致）

- **画布**：Vue Flow（`@vue-flow/core`，现有依赖）
- **节点**：资源状态（圆角矩形，按 `tone` 着色）
- **边**：状态转移（线上有 `event_key` + 触发器配置）
- **右侧抽屉**：选中边后配置 → `from_states` / `to_state` / `notify_roles` / `details_schema`
- **保留**现有 `lifecycle_config` JSONB 字段——**不破坏已迁移的 v2 spec**，只是在结构上新增字段，老数据用默认迁移规则兜底。

---

## 4. 任务 ↔ 资源的双向耦合

### 4.1 主路径（80%）：任务完成 → 写 ResourceLog

```
任务 A 完成
  ↓ (signal: task_completed)
查 PipelineType P
  ↓
对所有挂在 A 上的 ResourceItem 查 ResourceType.lifecycle_config
  ↓
找出 "from_task=true 且 from_task_pipelines 包含 P" 的所有 events
  ↓
为每个 ResourceItem 各创建一笔 ResourceLog
  - event_key    = matched event.id
  - source       = "task"
  - source_task  = A
  - operator     = A.actual_executor（最后一个完成的人）
  - details      = A 的 field_values 过滤 details_schema 字段
  ↓
ResourceItem.status = event.to_state
  ↓
Signal → 通知 notify_roles 中所有用户
```

#### 4.1.1 "哪个管线类型的完成 → 触发哪个资源事件" 在哪里配置？

草案提供两个选项，**推荐 X**（配置集中在资源模板上）：

- **选项 X（推荐）**：在**资源模板的 event** 上配 `from_task_pipelines` 列表
- **选项 Y**：在**管线类型的"完成节点"** 上配"触发哪个资源事件"

> **为什么选 X**：管理员在画资源模板时已经知道"这个状态由哪类任务完成"，**配在资源侧更内聚**；管线模板保持简单，不背资源库的复杂度。

`event` 配置加一个字段：

```jsonc
{
  "id": "picked_up",
  ...
  "triggers": {
    "from_task": true,
    "from_task_pipelines": ["pipeline_abc123"]   // 新增
  }
}
```

#### 4.1.2 关键设计要点

- **一对多**：一个任务挂多个资源时，每个资源各写一笔日志。
- **多对多**：一个事件配置多个管线类型时，按管线类型触发。
- **幂等**：同一任务完成两次（重复提交）只写一次——加 `task_completion_id` 唯一约束。
- **降级**：管线类型不在白名单时，任务完成**不**自动写日志，**不**报错（因为任务本身可能跟资源无关）。

### 4.2 副路径（20%）：手动 / 系统 / 外部

- **手动**：管理员在资源详情页"记录新事件" → 弹表单 → POST ResourceLog
- **系统**（暂留接口，本期不实现）：`/api/resources/{id}/events/system/` 接收内部信号
- **外部**（暂留接口）：同上加 token 校验

**关键承诺**：所有路径写入的 ResourceLog **结构完全一致**，仅以 `source` 字段区分（`task` / `manual` / `system` / `external`），其他字段不区分。

---

## 5. 面向人的信息流呈现（保守版）

> 这部分草案**先不预设"等价"的含义**，给一个保守、**不合并数据模型**的呈现。

### 5.1 资源详情页 = 资源事件流（按时间倒序）

```
[射灯 A-001]  当前状态: 维修中 (warning)

▼ 事件时间线
─────────────────────────
2026-07-06 10:23  │ 维修完成
  维修人: 张师傅   任务: TF-238
  更换部件: 灯泡×1
  下次巡检: 2026-08-06
─────────────────────────
2026-07-05 14:11  │ 进入维修
  故障描述: 灯泡不亮  任务: TF-237
─────────────────────────
2026-07-01 09:00  │ 出库使用
  借用人: 王经理   任务: TF-225
─────────────────────────
```

**关键点**：每条事件显示**任务来源链接**（如果有），让人能从资源跳到任务，反之亦然。

### 5.2 通知收件箱（不合并数据）

- 任务通知：标题"任务「X」已派给您"
- 资源事件通知：标题"灯具「射灯 A-001」已进入维修"
- 两种通知走**同一套通知组件**（项目里已有），**不区分呈现样式**
- 用户在通知中心看到的都是"我今天参与的 N 条事件"，**视觉一致**

### 5.3 Dashboard

- 不做"统一事件流"（那是激进方案）
- 资源卡片：当前状态 + 最近一次事件时间
- 任务卡片：当前状态 + 最近一次操作时间
- 两个卡片用同样的 UI 组件、同样的色调 token（[`frontend/src/styles/tokens.css`](../../frontend/src/styles/tokens.css)）

---

## 6. 三种"客制化"走向（备查）

| 维度 | A 复用画布 | **B 独立画布（推荐）** | C 表单 |
|---|---|---|---|
| 心智一致性 | ★★★★★ | ★★★★ | ★★ |
| 复杂度 | 高（画布要承担两种） | 中 | 低 |
| 实现成本 | 中-高 | 中 | 低 |
| 未来扩展 | 容易（同一画布） | 容易 | 容易但形式受限 |
| 偏离你的"客制化模板" | 0 | 略 | 大 |

- **A**：复用管线编辑器画布，资源节点和任务节点同画布。一致性最高，但管线编辑器已经够复杂，叠加资源维度牵一发动全身——风险/回报不划算。
- **B（推荐）**：独立画布 + 资源-管线显式映射。心智模型清晰，边界不污染画布，迭代可控。
- **C**：资源类型管理就是一张表单（状态列表 + 通知角色）。实现最快，但和"延续管线编辑器自定义模板思想"不太契合。

---

## 7. 本期明确**不做**的事（YAGNI）

按规则 [`.trae/rules/project_rules.md`](../../.trae/rules/project_rules.md) 与 brainstorming 流程的 YAGNI 原则：

1. ❌ **不**做 SN 码、采购价、折旧、位置等标准资产字段（位置、备注允许管理员加文本字段，但不进默认 schema）。
2. ❌ **不**做备件库、保养合同、供应商管理。
3. ❌ **不**做 RFID / 二维码扫码（保留 `triggers.external` 接口位置）。
4. ❌ **不**做寿命预测 / 自动报警（保留 `triggers.scheduled` 接口位置）。
5. ❌ **不**做资源借用审批（借用 = 一个任务，业务动作在管线里管）。
6. ❌ **不**做资源报表 / 看板（先让事件流跑起来，看板后面再单独立项）。

---

## 8. 阶段拆分建议（暂定，等终稿设计时细化）

| 阶段 | 范围 | 说明 |
|---|---|---|
| **P-A** 后端基础 | lifecycle_config 新结构 + 新字段 + 数据迁移 | 不破坏 v2 spec，只**新增**字段，老数据用默认迁移 |
| **P-B** 后端：任务完成联动 | signal + service + 幂等约束 | 任务完成 → 自动写 ResourceLog |
| **P-C** 后端：手动 + 系统 + 外部入口 | ResourceLog 三种 source 的 POST 端点 | 共享 service，source 字段区分 |
| **P-D** 前端：资源模板画布 | 资源类型管理页加 Vue Flow 画布 | 复用现有 Vue Flow 组件 |
| **P-E** 前端：资源详情页 | 事件时间线 + 资源卡片 + 跳转任务 | 沿用现有 UI token |
| **P-F** 前端：任务详情页"触发的资源事件"区 | 完成任务时显示"本任务影响了哪些资源" | 让"任务→资源"显形 |
| **P-G** 测试 + 文档 + demo | 灯具类型的 demo + README 更新 | [`demo-data/`](../../demo-data/README.md) 加灯具类型示例 |

---

## 9. 待你和客户对齐的几个具体点

1. **资源模板画布**：B（独立画布）/ A（复用画布）/ C（表单）三选一，**草案推荐 B**。
2. **配置位置**："哪些管线类型的'完成'能触发本资源事件"，是**资源侧配**（草案方案 X）还是**管线侧配**（方案 Y）？还是两处都能配？
3. **本期是否包括** P-G 的"灯具类型 demo"？你想要 `demo-data/` 里有 `light-fixture-type.example.json` 这种东西吗？
4. **"等价"含义**：你那句"操作动作 ≈ 资源状态变化，在信息流上等价"——几次讨论里都没对齐到具体含义。拿这份草案跟客户聊完，**看客户反馈时他/她认为"等价"是哪种意思**，然后告诉我，再回头校准 §5 的呈现策略。
5. **是否需要把客户的资产台账字段也加进 field_schema**：很多客户会本能地要求加 SN 码、采购价之类的字段。本草案承诺"不加进默认 schema"，但**管理员加文本字段是允许的**。想跟客户明确这一点吗？

---

## 10. 和现有文档 / Spec 的关系

- 本草案在 [`designingDocument/caduceus-prd.md` §3.4](../../designingDocument/caduceus-prd.md) 的方向内（资源库 ≠ 资产管理）。
- 本草案后端部分**继承** [.trae/specs/phase-4-resource-lifecycle/spec.md](../../.trae/specs/phase-4-resource-lifecycle/spec.md)（`lifecycle_config` + `ResourceLog` + status 自动推导 + 通知联动）。  
  草案**新增**的字段 `triggers.from_task_pipelines` / `event.details_schema` / `source` 等**不破坏**该 spec。
- 本草案前端部分**覆盖** [.trae/specs/phase-4-resources-v2/spec.md](../../.trae/specs/phase-4-resources-v2/spec.md)（ResourceList / ResourceSelector / TaskDetail 集成）。草案新增了**资源模板画布**和**资源详情页**，是 v2 spec 的扩展。
- 终稿设计文档待与客户对齐后写到 `docs/superpowers/specs/YYYY-MM-DD-resource-v2-lifecycle-design.md`，并相应更新 [`designingDocument/caduceus-design.md`](../../designingDocument/caduceus-design.md) / [`caduceus-prd.md`](../../designingDocument/caduceus-prd.md) / [`caduceus-implementation.md`](../../designingDocument/caduceus-implementation.md)。

---

## 附录：讨论时间线摘要

- 客户提了一个具体场景（舞台灯光设备全生命周期管理）
- 讨论中明确了：**资源库 ≠ 资产管理**；**业务动作走管线**，**资源状态 ≈ 业务动作副产品**；**80/20 入口**；**客制化模板**
- 未对齐的表述："操作动作 == 资源状态变化，在信息流上等价"——几次讨论都未明确具体含义，**待客户反馈后回校**

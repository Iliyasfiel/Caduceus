# Exploration Archive（外部设计探索报告存档）

> **性质**：从外部环境搬运回来的设计讨论存档，**不属于 Caduceus 项目的正式产物**。
> **作用**：作为想法溯源、决策回顾的参考资料，不渗透到 `designingDocument/`、`README.md`、`backend/`、`frontend/` 等正式目录。

---

## 来源

- 原始文件：`caduceus-design-exploration.zip`（1.05 MB），于 2026-07-07 由用户在外部环境生成后拷贝进来
- 原始生成工具：Trae Work（另一实例）
- 解压时间：2026-07-08
- 原 zip 已删除，仅保留解压后的目录

## 内容

```
exploration-archive/
├── caduceus-design-exploration.html   主报告（15 章设计探索，约 64 KB）
├── assets/
│   └── charts.js                       报告内嵌的图表脚本
├── _shared/
│   └── js/
│       ├── echarts.min.js              ECharts 图表库（CDN 备援）
│       └── mermaid.min.js              Mermaid 流程图库
└── README.md                           本文件
```

## 报告主题

《**Caduceus 信息结构化协作平台 — 设计探索报告**》——从"信息共享"到"信息投递"的范式转换。

15 章结构（仅作索引，便于回查；详见 HTML 报告本体）：

1. 问题的提出
2. Caduceus 项目现状分析
3. 核心突破：从角色视图到视图预设
4. 信息透明度与角色差异化
5. 条件字段与渐进式信息披露
6. 动态日程与流转粒度
7. 替代范式与跨行业案例（Tana / 医疗 SBAR / 航空 CRM / ICS / BIM）
8. 竞品全景分析
9. 第一阶段结论
10. 人与物协同：任务信息逻辑的泛化
11. 同构性边界验证
12. 资源 View Preset 原型设计
13. 资源流转与任务流转的统一
14. 命名收敛：从"管线"到"流转"
15. 最终结论与完整图景

报告核心观点：

> Caduceus 的下一个阶段不是"任务协同平台"或"资产管理平台"，而是一个通用的"信息投递引擎"——无论信息载体是任务还是资源，让信息在正确的时间、以正确的形式、到达正确的人。

四个被点名的核心能力：**View Preset（投递规则）+ 条件字段（投递时机）+ 流转引擎（信息结构）+ Schedule Items（时间维度）**。

## 与项目内材料的关系

`dev-tmp/design/` 子目录里已有的设计稿（UiSelect v2、TaskList 优化、UI Roadmap、Resource 生命周期等）**与本报告同主题但不重叠**——前者是 UI 组件或单点模块层级的设计稿，本报告是**更上层（信息结构 / 范式 / 定位）**的讨论，粒度更高。

`designingDocument/` 下三份正式设计文档（caduceus-prd / caduceus-design / caduceus-implementation）是项目当前的权威设计基准；本报告**未纳入其中**，未与正式设计对齐，引用时需自行判断一致性。

## 使用规则

- ✅ **允许**：本地浏览、回查想法来源、与 `dev-tmp/design/` 中的细节稿对照
- ✅ **允许**：作为讨论起点引用（例如"参考 exploration-archive 第七章 Tana Supertag 思路"）
- ❌ **禁止**：未经讨论确认，直接把报告里的方案沉淀进 `designingDocument/`、`backend/`、`frontend/`
- ❌ **禁止**：在 `README.md`、`docs/` 等正式文档中无条件引用本报告为依据
- ⚠️ **引用原则**：报告中提到的能力（View Preset、条件字段、流转引擎扩展等）目前均为"待开发 / 需扩展"，**不是已实现功能**，不要误以为是现状。

## 清理规则

按 [tmp-files.md](../../.trae/rules/tmp-files.md) 的提交前清理提示：

- `exploration-archive/` 整体纳入 git 跟踪（含 HTML 与 JS 库）
- 不在本目录内编辑文件（编辑等于修改讨论存档）
- 如需基于本报告**提炼**新文档，迁移到 `dev-tmp/design/` 或 `designingDocument/`，并在此 README 中注明已迁移的位置
- 如整份报告失去参考价值（项目方向已收敛、报告已被消化），按删除确认流程征得用户同意后删除本目录

## 元数据

- 决策记录：与 `feature/task-list-ui-optimize` PR 合入同日（2026-07-08）
- 跨设备同步：本目录纳入 git 跟踪，详见 `dev-tmp/README.md` 与 `.gitignore` 注释
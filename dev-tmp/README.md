# dev-tmp — 临时文件目录

> 项目**唯一**的临时文件目录。所有开发过程中产生的临时内容（草稿、一次性脚本、临时操作指南等）**必须**集中放在本目录及其子目录，**严禁散落**到仓库其他位置。
>
> 完整规则见 [`.trae/rules/project_rules.md` §仓库治理 → 临时文件（dev-tmp）](../../.trae/rules/project_rules.md)。

## 目录结构

```
dev-tmp/
├── README.md                       ← 本文件（总览）
├── design/                         ← 设计文档相关临时草稿
│   ├── README.md
│   ├── ui-component-api-reference.md
│   ├── ui-design-principles-and-polish.md
│   ├── ui-roadmap-p1.md
│   └── resource-v2-lifecycle-discussion.md
└── git/                            ← 工程操作相关临时文件
    ├── README.md
    └── git-push-guide.md
```

## 当前内容索引

| 子目录 | 内容 | 状态 | 清理规则 |
|--------|------|------|----------|
| [`design/`](./design/README.md) | UI 组件 API 参考 / 设计原则 / Polish 记录 / 路线图 / 资源库 v2 讨论稿 | 长期保留（与正式设计文档互补） | 删除前需向用户确认 |
| [`git/`](./git/README.md) | Git 离线推送操作指南 | 一次性使用（推送后可删除） | 推送完成后向用户确认即可删除 |

## Git 跟踪策略

- **当前策略**：纳入 git 跟踪（`.gitignore` 不再忽略 `dev-tmp/`，于 2026-07-06 调整）。
- **理由**：临时草稿对后续开发可能有启发，纳入跟踪 + 开发者定期清理，**优于**隐式忽略导致草稿无法被找回。
- **回退指引**：若需恢复"全局忽略"，在 `.gitignore` 重新添加 `dev-tmp/` 行即可。

## 提交前清理提示（IMPORTANT）

每次准备把 `dev-tmp/` 下的内容**提交进 git** 之前，**必须**先停下：

1. 列出**待提交文件清单 + 每份文件的内容概要**（一行总结它在讨论什么）
2. 询问用户：
   - 有没有要**删除**的？
   - 有没有要**同步沉淀到正式文档**的（如 `designingDocument/` / `README.md` / `docs/`）？
3. 获得用户明确答复后再执行 `git add` + `git commit`

**例外**：纯 typo 修正、格式调整等显然无沉淀价值的小改动，**至少要在 commit message 里说明**。

**适用场景**：`git add dev-tmp/`、`git commit` 涉及 `dev-tmp/` 下任何文件 / 子目录时。

## 为什么要在根目录集中？

- **避免污染**：临时文件不放进 `backend/`、`frontend/`、`designingDocument/`、`demo-data/` 等正式目录
- **一眼可见**：任何临时内容都在 `dev-tmp/` 一目了然
- **易于清理**：定期 `ls dev-tmp/` 即可发现过期草稿
- **Git 隔离**（已不再严格隔离）：当前纳入跟踪，但**所有内容都是临时性的**，不影响正式产物的构建 / 运行

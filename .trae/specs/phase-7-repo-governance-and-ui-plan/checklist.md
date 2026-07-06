# Phase 7: 仓库治理 + UI 重新设计规划 Checklist

## 第一阶段：仓库治理与清理

- [x] `.trae/rules/project_rules.md` 末尾已追加"## 仓库治理"小节
- [x] 仓库治理小节包含"禁止将虚拟环境（`venv/`、`.venv/`、`env/`、`.env-virtual/` 等）提交到远程仓库"规则
- [x] 仓库治理小节包含"允许 `demo-data/` 目录提交到远程仓库"规则及内容规范
- [x] `.gitignore` 已追加 `venv/` 与 `.venv/` 两行
- [x] `.gitignore` **未**忽略 `demo-data/`
- [x] `git rm -r --cached backend/.venv/` 已执行
- [x] `git ls-files | grep -E "^\.venv/|/(\.venv|venv)/"` 返回 0 行
- [x] 本地 `backend/.venv/` 目录仍存在（未删除实体文件）
- [x] `demo-data/` 目录已创建
- [x] `demo-data/README.md` 已创建，描述用途、允许/禁止内容、加载/清理方式
- [x] 至少一个示例 fixture 文件已创建（如 `demo-data/resource-types.example.json`）
- [x] `README.md` 已追加"## 演示数据（demo-data）"小节
- [x] README 演示数据章节描述了位置、用途、新增时机、加载与清理方式
- [x] README 演示数据章节链接到 `demo-data/README.md`

## 第二阶段：UI 重新设计规划

- [x] `designingDocument/caduceus-ui-redesign.md` 已创建为独立的新文件
- [x] 文档包含五层内容：设计令牌、基础组件、复合组件、关键页面 Polish 顺序、体验细节
- [x] 文档末尾包含"任务拆分"小节，把"轻量级设计系统 + 关键页 polish"拆分为可独立交付的小任务
- [x] `caduceus-prd.md` 保持原样未修改
- [x] `caduceus-design.md` 保持原样未修改
- [x] `caduceus-implementation.md` 保持原样未修改

## 第三阶段：推送与分支

- [x] 所有变更（rules / .gitignore / demo-data / README / 设计文档 / .venv 解除跟踪）已通过 conventional commit 提交
- [x] 上述变更已成功推送到 `origin/main`
- [x] 远程 `origin/main` 不再包含 `backend/.venv/` 任何文件
- [x] 远程 `origin/main` 包含 `demo-data/` 与 `designingDocument/caduceus-ui-redesign.md`
- [x] 本地 `ui-redesign` 分支已创建，指向 main 最新 HEAD
- [x] 远程 `origin/ui-redesign` 分支已创建并与本地分支建立跟踪关系
- [x] 后续 UI 重新设计的实现工作在 `ui-redesign` 分支上进行（本次不实施）

# Tasks

- [ ] Task 0: 清理误提交的虚拟环境（前置任务）
  - [ ] SubTask 0.1: 在 `.gitignore` 末尾追加 `venv/` 与 `.venv/` 两行
  - [ ] SubTask 0.2: 执行 `git rm -r --cached backend/.venv/` 解除跟踪（不删除本地文件）
  - [ ] SubTask 0.3: 验证 `git ls-files | grep -E "^\.venv/|/(\.venv|venv)/"` 输出为 0
  - [ ] SubTask 0.4: `git commit` 提交 `.gitignore` 与 .venv 解除跟踪的变更

- [ ] Task 1: 撰写独立设计文档
  - [ ] SubTask 1.1: 新建 `designingDocument/caduceus-ui-redesign.md`，包含五层内容（设计令牌、基础组件、复合组件、关键页面 Polish 顺序、体验细节）+ 末尾的"任务拆分"小节
  - [ ] SubTask 1.2: 确认 `caduceus-prd.md` / `caduceus-design.md` / `caduceus-implementation.md` / `README.md` 在本次变更中**不被修改**

- [ ] Task 2: 提交并推送到 main
  - [ ] SubTask 2.1: `git add .gitignore designingDocument/caduceus-ui-redesign.md`
  - [ ] SubTask 2.2: `git commit` 使用 conventional 格式，commit message 描述"清理 .venv 误提交 + 新增 UI 重新设计规划独立设计文档"
  - [ ] SubTask 2.3: `git push origin main` 推送到 main

- [ ] Task 3: 创建 ui-redesign 隔离分支
  - [ ] SubTask 3.1: `git checkout -b ui-redesign` 基于当前 main HEAD 创建本地分支
  - [ ] SubTask 3.2: `git push -u origin ui-redesign` 创建并跟踪远程分支

# Task Dependencies
- Task 1 依赖 Task 0
- Task 2 依赖 Task 0、Task 1
- Task 3 依赖 Task 2（必须先把清理 + 规划推送到 main，才能基于其创建新分支）

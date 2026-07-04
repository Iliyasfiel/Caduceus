# Tasks

## 第一阶段：仓库治理与清理

- [x] Task 1: 更新 project_rules.md（仓库治理规则）
  - [x] SubTask 1.1: 在 `.trae/rules/project_rules.md` 末尾追加"## 仓库治理"小节
  - [x] SubTask 1.2: 写入"禁止将虚拟环境提交到远程仓库"规则，并说明处理方式
  - [x] SubTask 1.3: 写入"允许 `demo-data/` 目录提交到远程仓库"规则，并说明允许与禁止的内容类型

- [x] Task 2: 补全 .gitignore
  - [x] SubTask 2.1: 在 `.gitignore` 末尾追加 `venv/` 与 `.venv/` 两行
  - [x] SubTask 2.2: 确认 `demo-data/` **未**被加入忽略列表

- [x] Task 3: 解除 .venv 的 Git 跟踪
  - [x] SubTask 3.1: 执行 `git rm -r --cached backend/.venv/`
  - [x] SubTask 3.2: 验证 `git ls-files | grep -E "^\.venv/|/(\.venv|venv)/"` 输出为 0
  - [x] SubTask 3.3: 确认本地 `backend/.venv/` 目录仍存在

- [x] Task 4: 创建 demo-data 目录与说明
  - [x] SubTask 4.1: 新建 `demo-data/` 目录
  - [x] SubTask 4.2: 新建 `demo-data/README.md`，说明目录用途、允许/禁止内容、加载/清理方式
  - [x] SubTask 4.3: 至少新增一个示例 fixture 文件（如 `demo-data/resource-types.example.json`）作为使用范本

- [x] Task 5: 更新 README 增加演示数据章节
  - [x] SubTask 5.1: 在 `README.md` 末尾追加"## 演示数据（demo-data）"小节
  - [x] SubTask 5.2: 描述目录位置、用途、新增示例数据的时机、加载与清理方式
  - [x] SubTask 5.3: 添加 `demo-data/README.md` 的链接

## 第二阶段：UI 重新设计规划

- [x] Task 6: 撰写独立设计文档
  - [x] SubTask 6.1: 新建 `designingDocument/caduceus-ui-redesign.md`，包含五层内容（设计令牌、基础组件、复合组件、关键页面 Polish 顺序、体验细节）+ 末尾的"任务拆分"小节
  - [x] SubTask 6.2: 确认 `caduceus-prd.md` / `caduceus-design.md` / `caduceus-implementation.md` 在本次变更中**不被修改**

## 第三阶段：推送与分支

- [ ] Task 7: 提交并推送到 main
  - [ ] SubTask 7.1: `git add .gitignore .trae/rules/project_rules.md demo-data/ README.md designingDocument/caduceus-ui-redesign.md`
  - [ ] SubTask 7.2: `git rm -r --cached backend/.venv/` 已经在 Task 3 完成
  - [ ] SubTask 7.3: `git commit` 使用 conventional 格式，commit message 描述"仓库治理规则化、清理 .venv 误提交、新增 demo-data 目录、新增 UI 重新设计规划独立设计文档"
  - [ ] SubTask 7.4: `git push origin main` 推送到 main

- [ ] Task 8: 创建 ui-redesign 隔离分支
  - [ ] SubTask 8.1: `git checkout -b ui-redesign` 基于当前 main HEAD 创建本地分支
  - [ ] SubTask 8.2: `git push -u origin ui-redesign` 创建并跟踪远程分支

# Task Dependencies
- Task 1 与 Task 2 可并行
- Task 3 依赖 Task 2（必须先有 .gitignore 规则）
- Task 4 依赖 Task 1（规则里允许 demo-data 才能建）
- Task 5 依赖 Task 4
- Task 6 与 Task 4、Task 5 可并行
- Task 7 依赖 Task 1-6 全部完成
- Task 8 依赖 Task 7

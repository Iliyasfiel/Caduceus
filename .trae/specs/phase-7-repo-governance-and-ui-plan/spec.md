# Phase 7: 仓库治理 + UI 重新设计规划 Spec

## Why
经过 Phase 0-6 的迭代，目前有两个治理问题需要修正：
1. **虚拟环境被误提交**：`backend/.venv/`（161MB / 6985 个文件）已经在之前的推送中进入远程仓库；`.gitignore` 缺 `venv/` 和 `.venv/` 模式。
2. **缺乏"演示用临时数据"的归宿**：开发过程中需要演示数据（资源类型示例、任务示例等）来手动验证页面效果，但目前没有明确的"哪些数据可提交"约定，导致要么被加入 `.gitignore` 不可复现，要么被混入 `backend/` 污染业务代码。

同时 Phase 7 还有 UI 重新设计规划目标：把"如何重新设计"沉淀成独立文档推到 main 作为基线，再用 `ui-redesign` 隔离分支承载实现。

本 Spec 一次解决三件事：
1. **规则化仓库治理**（venv 不提交、demo-data 可以提交）
2. **清理 .venv 历史污染**（不删除本地，只解除跟踪）
3. **UI 重新设计规划文档 + 隔离分支**（避免污染 main）

## What Changes
- 修改 `.trae/rules/project_rules.md`：新增"仓库治理"小节，明确禁止提交虚拟环境、明确允许 `demo-data/` 目录存放开发演示数据
- 修改 `.gitignore`：补全 `venv/` 与 `.venv/` 模式；新增 `demo-data/` 之外允许/禁止规则（仅在 README 中说明语义，不在 .gitignore 中忽略）
- 新建 `demo-data/` 目录 + `demo-data/README.md` 说明该目录的用途、存放内容规范、加载/清理方式
- 修改 `README.md`：新增"演示数据（demo-data）"章节，说明该目录的位置、用途、典型内容、如何加载示例数据进行手动验证
- 从 Git 跟踪中移除 `backend/.venv/`（不删除本地文件，使用 `git rm -r --cached`）
- 新增 `designingDocument/caduceus-ui-redesign.md`：**唯一新增的设计文档**，独立于原有的 `caduceus-prd.md` / `caduceus-design.md` / `caduceus-implementation.md` 三份设计文档
  - 包含五层内容：设计令牌（Design Tokens）、基础组件（Base Components）、复合组件（Composite Components）、关键页面 Polish 顺序、体验细节
  - 末尾包含"任务拆分"小节，把"轻量级设计系统 + 关键页 polish"拆分为可分阶段执行的小任务，作为 ui-redesign 分支的待办基线
- 提交上述所有变更并推送到 `origin/main`
- 新建 `ui-redesign` 分支（基于当前 main）作为后续 UI 重新设计实现的隔离工作区

## Impact
- Affected specs: phase-6-stage-admin（本次只新增/修改治理规则 + 设计文档 + 建分支，不动其实现代码）
- Affected code:
  - `.trae/rules/project_rules.md`（追加"仓库治理"小节）
  - `.gitignore`（追加 `venv/` 与 `.venv/`）
  - Git 索引中移除 `backend/.venv/`（6985 个文件）
  - `demo-data/`（新目录，初始含 `README.md` + 一个示例 fixture）
  - `demo-data/README.md`（新）
  - `README.md`（追加"演示数据（demo-data）"章节）
  - `designingDocument/caduceus-ui-redesign.md`（**唯一**新增的设计文档）
- **明确不影响**的范围：
  - `designingDocument/caduceus-prd.md`（不动）
  - `designingDocument/caduceus-design.md`（不动）
  - `designingDocument/caduceus-implementation.md`（不动）
  - `backend/.venv/` 本地文件（不删除，只解除跟踪）
  - 后端业务代码、所有 Phase 0-6 的前端业务逻辑代码（均不动）

## ADDED Requirements

### Requirement: 仓库治理规则（写入 project_rules.md）
系统 SHALL 在 `.trae/rules/project_rules.md` 中明确以下仓库治理规则：

#### Scenario: 虚拟环境规则
- **WHEN** 读取 `project_rules.md` 的"仓库治理"小节
- **THEN** SHALL 包含明确陈述："禁止将任何 Python 虚拟环境（`venv/`、`.venv/`、`env/`、`.env-virtual/` 等）提交到远程仓库"
- **AND** SHALL 给出处理方式：使用 `requirements.txt` 或 `pyproject.toml` 管理依赖，clone 后本地重建虚拟环境

#### Scenario: 演示数据规则
- **WHEN** 读取 `project_rules.md` 的"仓库治理"小节
- **THEN** SHALL 包含明确陈述："根目录下的 `demo-data/` 目录用于存放开发演示用的临时数据，**允许提交**到远程仓库"
- **AND** SHALL 约定 `demo-data/` 内仅放"可在手动验证页面时复用的非敏感演示数据"，不放生产数据或用户隐私

### Requirement: .gitignore 补全
系统 SHALL 在 `.gitignore` 中追加 `venv/` 与 `.venv/` 模式。

#### Scenario: 模式完整
- **WHEN** 检查 `.gitignore`
- **THEN** SHALL 包含 `venv/` 与 `.venv/` 两行模式（覆盖根目录与任意子目录）
- **AND** 现有的 `__pycache__/`、`*.py[cod]`、`db.sqlite3`、`node_modules/` 等规则 SHALL 保持不变
- **AND** **不应**把 `demo-data/` 加入忽略列表（`demo-data/` 是允许提交的）

### Requirement: 演示数据目录
系统 SHALL 在仓库根目录提供 `demo-data/` 目录及配套说明文件。

#### Scenario: 目录与说明文件
- **WHEN** 检查 `demo-data/`
- **THEN** SHALL 存在 `demo-data/README.md`，说明该目录用途、允许存放的内容类型、不允许存放的内容类型
- **AND** SHALL 至少包含一个示例 fixture 文件（如 `demo-data/resources-types.example.json`）作为使用范本

#### Scenario: 内容规范
- **WHEN** 在 `demo-data/` 中新增文件
- **THEN** SHALL 遵循"非敏感、可复现、用于手动验证"原则
- **AND** SHALL 在 `demo-data/README.md` 的"加载方式"小节中描述如何将示例数据导入到本地开发数据库（使用 Django fixtures 或管理命令）

### Requirement: README 增加演示数据章节
系统 SHALL 在 `README.md` 中追加"演示数据（demo-data）"章节。

#### Scenario: 章节内容
- **WHEN** 阅读 `README.md`
- **THEN** SHALL 包含"演示数据（demo-data）"小节
- **AND** 描述目录位置、用途、何时新增示例数据、如何加载、清理方式
- **AND** 链接到 `demo-data/README.md` 详细规范

### Requirement: 清理误提交的虚拟环境
系统 SHALL 从 Git 跟踪中移除 `backend/.venv/`，并确保后续不会再被误提交。

#### Scenario: 解除 .venv 的 Git 跟踪
- **WHEN** 执行 `git rm -r --cached backend/.venv/`
- **THEN** Git 索引中 SHALL 不再包含 `backend/.venv/` 下任何文件
- **AND** 本地 `backend/.venv/` 目录 SHALL 保持存在（不删除实体文件，方便继续开发）
- **AND** 提交后 `git ls-files | grep -E "^\.venv/|/(\.venv|venv)/"` 返回 SHALL 为 0 行

#### Scenario: 推送清理后的 main
- **WHEN** 推送本次所有变更到 `origin/main`
- **THEN** 远程仓库 SHALL 不再包含 `backend/.venv/` 下的任何文件
- **AND** `.gitignore` SHALL 包含 `venv/` 与 `.venv/`
- **AND** `demo-data/` SHALL 出现在远程仓库

### Requirement: 独立设计文档
系统 SHALL 在 `designingDocument/caduceus-ui-redesign.md` 中提供完整的 UI 重新设计规划，**作为独立的新文件存在**，不与原有三份设计文档合并或互相引用。

#### Scenario: 文件独立存在
- **WHEN** 检查 `designingDocument/` 目录
- **THEN** SHALL 新增 `caduceus-ui-redesign.md` 这一个新文件
- **AND** `caduceus-prd.md` / `caduceus-design.md` / `caduceus-implementation.md` SHALL 保持原样不被修改

#### Scenario: 文档内容完整
- **WHEN** 阅读 `designingDocument/caduceus-ui-redesign.md`
- **THEN** 文档 SHALL 包含五个层次：设计令牌（Design Tokens）、基础组件（Base Components）、复合组件（Composite Components）、关键页面 Polish 顺序、体验细节
- **AND** 每个组件 SHALL 标注所属页面、优先级（P0/P1/P2）、关键变体
- **AND** 文档末尾 SHALL 包含"任务拆分"小节，按依赖顺序排列"轻量级设计系统 + 关键页 polish"的可独立交付小任务

### Requirement: 文档与 main 同步
系统 SHALL 把所有本次变更（治理规则、`.gitignore`、`.venv` 清理、`demo-data/`、`README.md`、设计文档）一次性推送到 `origin/main`。

#### Scenario: 推送成功
- **WHEN** 执行 `git push origin main`
- **THEN** 上述所有变更 SHALL 出现在 `origin/main` 的最新提交中
- **AND** 原有三份设计文档 SHALL 保持不变

### Requirement: 隔离分支 ui-redesign
系统 SHALL 基于当前 main 新建一个 `ui-redesign` 本地与远程分支，作为后续 UI 重新设计实现的隔离工作区。

#### Scenario: 分支创建
- **WHEN** 在 main 上完成本次所有变更的推送
- **THEN** SHALL 执行 `git checkout -b ui-redesign` 创建本地分支
- **AND** SHALL 执行 `git push -u origin ui-redesign` 创建远程分支
- **AND** 后续所有 UI 重新设计的代码变更 SHALL 在 `ui-redesign` 分支上进行，不直接 commit 到 main

## MODIFIED Requirements
无

## REMOVED Requirements
无

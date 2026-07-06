# Phase 7: UI 重新设计规划 Spec

## Why
当前前端（Phase 0-6）功能已完整但视觉层"能用但无体系"：所有样式散落在每个 .vue 的 `<style>` 里，没有统一的设计令牌（颜色/间距/字号/圆角/阴影），没有可复用的基础组件库。如果直接进入 UI 重新设计，存在"大改面广、回滚成本高"的风险；如果只做局部 polish，又会因为缺少规范而把代码越改越乱。

另外在之前的推送中，`backend/.venv/`（本地 Python 虚拟环境）被一并推到了远程仓库，导致 6985 个文件、约 161MB 的依赖被错误纳入版本控制——`venv` 不应在仓库中，应该用 `requirements.txt` + 本地重建的方式管理依赖。

本 Spec 的目标：
1. **先把脏数据清理掉**（把 `backend/.venv/` 从 Git 跟踪中移除，并补全 `.gitignore`），再
2. **把"如何重新设计 UI"沉淀成一份独立的设计文档推到 main 作为基线**，最后
3. **新建一个隔离分支**承载具体的重新设计实现，避免污染 main。

## What Changes
- 修复 `.gitignore`：新增 `venv/` / `.venv/` 模式，阻止后续误提交
- 从 Git 跟踪中移除 `backend/.venv/`（不删除本地文件，使用 `git rm -r --cached`）
- 新增 `designingDocument/caduceus-ui-redesign.md`：**唯一新增的设计文档**，独立于原有的 `caduceus-prd.md` / `caduceus-design.md` / `caduceus-implementation.md` 三份设计文档
  - 包含五层内容：设计令牌（Design Tokens）、基础组件（Base Components）、复合组件（Composite Components）、关键页面 Polish 顺序、体验细节
  - 末尾包含"任务拆分"小节，把"轻量级设计系统 + 关键页 polish"拆分为可分阶段执行的小任务，作为 ui-redesign 分支的待办基线
- 提交上述所有变更并推送到 `origin/main`
- 新建 `ui-redesign` 分支（基于当前 main）作为后续 UI 重新设计实现的隔离工作区
- 后续的 UI 重新设计实现（设计令牌落地、基础组件开发、页面替换）将另起 Spec 在 `ui-redesign` 分支上进行

## Impact
- Affected specs: phase-6-stage-admin（本次只新建独立设计文档 + 清理 .venv + 建分支，不动其实现代码）
- Affected code:
  - `.gitignore`（追加 `venv/` 与 `.venv/`）
  - Git 索引中移除 `backend/.venv/`（6985 个文件）
  - `designingDocument/caduceus-ui-redesign.md`（**唯一**新增）
- **明确不影响**的范围：
  - `designingDocument/caduceus-prd.md`（不动）
  - `designingDocument/caduceus-design.md`（不动）
  - `designingDocument/caduceus-implementation.md`（不动）
  - `README.md`（本次不修改；后续阶段需要再追加章节时另起 Spec）
  - `backend/.venv/` 本地文件（不删除，只解除跟踪）
  - 后端业务代码、所有 Phase 0-6 的前端业务逻辑代码（均不动）

## ADDED Requirements

### Requirement: 清理误提交的虚拟环境
系统 SHALL 从 Git 跟踪中移除 `backend/.venv/`，并确保后续不会再被误提交。

#### Scenario: .gitignore 补全
- **WHEN** 检查 `.gitignore`
- **THEN** SHALL 包含 `venv/` 与 `.venv/` 两行模式（覆盖根目录与任意子目录）
- **AND** 现有的 `__pycache__/`、`*.py[cod]`、`db.sqlite3`、`node_modules/` 等规则 SHALL 保持不变

#### Scenario: 解除 .venv 的 Git 跟踪
- **WHEN** 执行 `git rm -r --cached backend/.venv/`
- **THEN** Git 索引中 SHALL 不再包含 `backend/.venv/` 下任何文件
- **AND** 本地 `backend/.venv/` 目录 SHALL 保持存在（不删除实体文件，方便继续开发）
- **AND** 提交后 `git ls-files | grep -E "^\.venv/|/(\.venv|venv)/"` 返回 SHALL 为 0 行

#### Scenario: 推送清理后的 main
- **WHEN** 推送本次清理与设计文档到 `origin/main`
- **THEN** 远程仓库 SHALL 不再包含 `backend/.venv/` 下的任何文件
- **AND** `.gitignore` SHALL 包含 `venv/` 与 `.venv/`

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
系统 SHALL 把 `caduceus-ui-redesign.md` 推送到 `origin/main` 分支。

#### Scenario: 推送成功
- **WHEN** 执行 `git push origin main`
- **THEN** `designingDocument/caduceus-ui-redesign.md` SHALL 出现在 `origin/main` 的最新提交中
- **AND** 原有三份设计文档与 README SHALL 保持不变

### Requirement: 隔离分支 ui-redesign
系统 SHALL 基于当前 main 新建一个 `ui-redesign` 本地与远程分支，作为后续 UI 重新设计实现的隔离工作区。

#### Scenario: 分支创建
- **WHEN** 在 main 上完成本次清理与设计文档的推送
- **THEN** SHALL 执行 `git checkout -b ui-redesign` 创建本地分支
- **AND** SHALL 执行 `git push -u origin ui-redesign` 创建远程分支
- **AND** 后续所有 UI 重新设计的代码变更 SHALL 在 `ui-redesign` 分支上进行，不直接 commit 到 main

## MODIFIED Requirements
无

## REMOVED Requirements
无

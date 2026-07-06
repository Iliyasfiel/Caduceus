# Git 工作流（GitHub Flow）

> 详细流程与纪律。本节针对**单开发者 + 多环境**场景，目标是避免"本地主线领先云端 → 强制同步时大量冲突"的问题（2026-07-06 已发生此类事件并强制重置 main）。

## 主干保护
- 严禁直接在 `main` 分支上做开发；`main` 是只读的"金本"。
- 云端 `origin/main` 是唯一真相源，本地 `main` 始终保持与其同步。
- `feature/*`、`fix/*`、`docs/*`、`refactor/*`、`chore/*` 等短生命周期分支用于实际开发。

## 标准流程
1. **开工**：先切到 `main` 并拉取最新：
   ```bash
   git checkout main
   git pull origin main
   ```
2. **开分支**：基于最新 `main` 新建本地特性分支：
   ```bash
   git checkout -b feature/<scope>-<short-desc>
   # 例: feature/task-detail-timeline
   ```
3. **开发**：在分支上多次本地提交，遵守 Conventional Commit 规范。
4. **推送**：首次推送需加 `-u` 建立上游跟踪：
   ```bash
   git push -u origin feature/<scope>-<short-desc>
   # 此后只用 git push / git pull 即可
   ```
5. **合并**：通过 GitHub PR 合入 `main`，推荐 **Squash and merge** 保持主线历史线性。
6. **清理**：合并完成后删除该 feature 分支（本地 + 远端），避免分支列表堆积。

## 关键纪律
- 不允许"攒一堆本地提交再统一推送" → 每个独立改动完成后立刻 `git push`。
- 完工前如果主线上有更新，先 `git fetch origin main && git rebase origin/main` 再推送。
- 严禁使用 `git push --force`（含 `--force-with-lease`）推送到 `main`；如确需重写历史，仅限在私有 feature 分支上。
- 跨环境同步（含离线开发）请参考同目录下 `offline-bundle.md`。

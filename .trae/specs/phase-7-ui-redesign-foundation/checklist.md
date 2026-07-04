# Phase 7: UI 重新设计规划 Checklist

## 虚拟环境清理
- [ ] `.gitignore` 已追加 `venv/` 与 `.venv/` 模式
- [ ] `git rm -r --cached backend/.venv/` 已执行，本地 `backend/.venv/` 目录保留
- [ ] `git ls-files | grep -E "^\.venv/|/(\.venv|venv)/"` 返回 0 行
- [ ] `.gitignore` 与 .venv 解除跟踪的变更已通过 conventional commit 提交

## 设计文档
- [ ] `designingDocument/caduceus-ui-redesign.md` 已创建为独立的新文件
- [ ] 文档包含五层内容：设计令牌、基础组件、复合组件、关键页面 Polish 顺序、体验细节
- [ ] 文档末尾包含"任务拆分"小节，把"轻量级设计系统 + 关键页 polish"拆分为可独立交付的小任务
- [ ] `caduceus-prd.md` 保持原样未修改
- [ ] `caduceus-design.md` 保持原样未修改
- [ ] `caduceus-implementation.md` 保持原样未修改
- [ ] `README.md` 保持原样未修改

## 推送与分支
- [ ] `.gitignore` 变更、`caduceus-ui-redesign.md` 已通过 conventional commit 提交
- [ ] 上述变更已成功推送到 `origin/main`
- [ ] 远程 `origin/main` 不再包含 `backend/.venv/` 任何文件
- [ ] 本地 `ui-redesign` 分支已创建，指向 main 最新 HEAD
- [ ] 远程 `origin/ui-redesign` 分支已创建并与本地分支建立跟踪关系
- [ ] 后续 UI 重新设计的实现工作在 `ui-redesign` 分支上进行（本次不实施）

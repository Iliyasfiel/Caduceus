# Git 推送操作指南（离线 → 远程 ui-redesign）

> 📦 **临时文件**（位于 [`dev-tmp/`](./)）。这是离线开发 → 上线 GitHub 的**一次性操作指南**，推送完成后即可删除本文件。
>
> 按 `.trae/rules/project_rules.md` “临时文件（dev-tmp）” 一节，删除前先向用户确认。

---

## 0. 前置信息

| 项 | 值 |
|---|---|
| 远程仓库 | `https://github.com/Iliyasfiel/Caduceus.git` |
| **目标推送分支** | **`ui-redesign`**（用户要求：保留远程 ui-redesign 历史） |
| **绝不推送** | `main`（远程 main 不能被覆盖） |
| 当前本地分支 | `main`（本地唯一分支，含 commit `03359a1`） |
| 远程无 origin 配置 | 是（本地仓库尚未 push 过） |

---

## 1. 场景假设

你的工作环境是离线的，但有一台联网机器（或 AI agent）可以访问 GitHub。本指南假设你会把**整个项目目录**（含 `.git/`）拷贝到联网机器上执行推送。

如果你是用 `git bundle`（单文件方案），参见第 7 节附录。

---

## 2. 总体目标

**保留远程 ui-redesign 历史 + 保留本地 commit `03359a1`**，最终远程 ui-redesign 分支的历史形如：

```
远程 ui-redesign 最终状态：

A---B---C---D---E          ← 远程 ui-redesign 原有历史
            \
             F              ← 本地 commit 03359a1（"初始化项目基线"）
                              （实际上 F 是仓库第一个 commit，因为本地仓库是空仓库起步）
```

**注意**：因为你下载的 tar 包是从 ui-redesign 拉的，**本地 `03359a1` 的内容与远程 ui-redesign 高度重合**。这是一个**重复 commit**——理论上可以用 `git reset --hard origin/ui-redesign` 把它替换掉。

但为了**保留你这次“初始化”的痕迹**，本指南采用 **merge 策略**：把本地 commit 作为 merge commit 接进去。

---

## 3. 推送步骤（联网机器上执行）

### 3.1 进入项目目录

```bash
cd /path/to/Caduceus        # 把项目目录拷过来后进入
```

### 3.2 验证本地状态

```bash
git status                  # 应该输出：nothing to commit, working tree clean
git branch                  # 应该输出：* main（且只有 main）
git log --oneline           # 应该看到 03359a1 "chore: 初始化项目基线"
```

### 3.3 添加远程仓库

```bash
git remote add origin https://github.com/Iliyasfiel/Caduceus.git
git remote -v               # 验证：应显示 origin → https://github.com/Iliyasfiel/Caduceus.git
```

### 3.4 拉取远程所有引用（不切换）

```bash
git fetch origin
```

这一步骤只拉取远程所有分支 / tag 信息到本地，**不会修改你的工作目录**。

### 3.5 查看远程 ui-redesign 的历史

```bash
git log --oneline origin/ui-redesign | head -20
```

确认远程 ui-redesign 分支存在且有内容。**记下你看到的最早的 commit hash**，后续会用。

### 3.6 临时保存本地 commit

```bash
git branch tmp-local-03359a1 03359a1
```

这条命令把 `03359a1` 复制到一个**新的临时分支** `tmp-local-03359a1`，避免后续操作把它丢掉。

### 3.7 重置本地 main 到远程 ui-redesign（关键步骤）

```bash
git checkout main
git reset --hard origin/ui-redesign
```

**这一步做了什么**：
- 本地 `main` 分支现在指向远程 `ui-redesign` 的最新 commit
- 工作目录内容被同步为远程 ui-redesign 的内容
- 本地 commit `03359a1` 仍保留在 `tmp-local-03359a1` 分支上（没丢）

### 3.8 验证

```bash
git log --oneline | head -20          # 现在看到的是远程 ui-redesign 的历史
git log --oneline tmp-local-03359a1   # 这个分支仍包含 03359a1
git status                            # clean
```

### 3.9 推送本地 main 到远程 ui-redesign（不破坏 main）

```bash
git push -u origin main:ui-redesign
```

**这条命令的意思**：把本地 `main` 推上去，在远程命名为 `ui-redesign`。

**远程发生了什么**：
- 远程 `ui-redesign` 分支被更新成你本地 `main` 的内容（即远程历史 + 你后续可能有的本地 commit）
- 远程 `main` **完全不受影响** ✅

### 3.10 清理临时分支

```bash
git branch -D tmp-local-03359a1
```

---

## 4. 后续日常推送流程

之后每次本地有改动，按以下流程：

```bash
# 1. 修改文件...

# 2. 选择性 add
git add <specific files>

# 3. 提交（中文 + conventional commit 格式）
git commit -m "feat(xxx): 改动描述"

# 4. 推送到远程 ui-redesign（永不推 main）
git push origin main:ui-redesign
```

如果远程有人改过 ui-redesign，你需要先 pull：

```bash
git pull --rebase origin ui-redesign    # 把远程改动接到你本地 main 之前
# 如果有冲突，解决后：
git push origin main:ui-redesign
```

---

## 5. 错误处理

### 5.1 `git push` 报 non-fast-forward

说明远程 ui-redesign 上有本地没有的 commit。

```bash
# 先 pull rebase 再 push
git pull --rebase origin ui-redesign
git push origin main:ui-redesign
```

**绝对不要**用 `git push -f` 强制推送，这会**覆盖远程历史**！

### 5.2 误推到 main 分支

如果不小心执行了 `git push origin main`（不带 `:`），赶紧撤销：

```bash
# 在 GitHub 网页上操作：
# Settings → Branches → Restore branch from a commit
# 或者用 git reflog 找到 main 的旧 hash：
git reflog
git push origin <旧hash>:main --force-with-lease
```

**所以一定要用 `main:ui-redesign` 格式推**——这是命名空间限定。

### 5.3 merge 冲突（如果你有冲突解决需求）

如果 `git pull --rebase` 出现冲突：

```bash
# 1. 解决冲突文件（手动编辑）
# 2. 标记为已解决
git add <冲突文件>
# 3. 继续 rebase
git rebase --continue
# 4. 推送
git push origin main:ui-redesign
```

---

## 6. 一键脚本（直接复制执行）

把以下全部命令保存为 `push-to-ui-redesign.sh` 或 `.bat`，联网机器上一键执行：

```bash
#!/bin/bash
set -e

# === 配置 ===
REMOTE_URL="https://github.com/Iliyasfiel/Caduceus.git"
LOCAL_BRANCH="main"
REMOTE_BRANCH="ui-redesign"
LOCAL_COMMIT_TO_PRESERVE="03359a1"   # 你的本地 commit hash

# === 1. 检查本地状态 ===
echo "[1/7] 检查本地状态..."
git status

# === 2. 添加远程 ===
echo "[2/7] 添加远程仓库..."
git remote remove origin 2>/dev/null || true
git remote add origin "$REMOTE_URL"

# === 3. 拉取远程 ===
echo "[3/7] 拉取远程所有引用..."
git fetch origin

# === 4. 临时保存本地 commit ===
echo "[4/7] 临时保存本地 commit $LOCAL_COMMIT_TO_PRESERVE..."
git branch tmp-local-$(echo $LOCAL_COMMIT_TO_PRESERVE | cut -c1-7) $LOCAL_COMMIT_TO_PRESERVE || true

# === 5. 重置本地 main 到远程 ui-redesign ===
echo "[5/7] 重置本地 main 到远程 $REMOTE_BRANCH..."
git checkout $LOCAL_BRANCH
git reset --hard origin/$REMOTE_BRANCH

# === 6. 推送 ===
echo "[6/7] 推送到远程 $REMOTE_BRANCH..."
git push -u origin $LOCAL_BRANCH:$REMOTE_BRANCH

# === 7. 清理 ===
echo "[7/7] 清理临时分支..."
git branch -D tmp-local-$(echo $LOCAL_COMMIT_TO_PRESERVE | cut -c1-7) || true

echo "✅ 推送完成！请在 GitHub 上验证 https://github.com/Iliyasfiel/Caduceus/tree/ui-redesign"
```

**Windows PowerShell 版本**：

```powershell
# === 配置 ===
$REMOTE_URL = "https://github.com/Iliyasfiel/Caduceus.git"
$LOCAL_BRANCH = "main"
$REMOTE_BRANCH = "ui-redesign"
$LOCAL_COMMIT = "03359a1"

# === 执行 ===
Write-Host "[1/7] 检查本地状态..."
git status

Write-Host "[2/7] 添加远程仓库..."
git remote remove origin 2>$null
git remote add origin $REMOTE_URL

Write-Host "[3/7] 拉取远程所有引用..."
git fetch origin

Write-Host "[4/7] 临时保存本地 commit..."
git branch "tmp-local-03359a1" $LOCAL_COMMIT

Write-Host "[5/7] 重置本地 main 到远程 $REMOTE_BRANCH..."
git checkout $LOCAL_BRANCH
git reset --hard "origin/$REMOTE_BRANCH"

Write-Host "[6/7] 推送到远程 $REMOTE_BRANCH..."
git push -u origin "${LOCAL_BRANCH}:${REMOTE_BRANCH}"

Write-Host "[7/7] 清理临时分支..."
git branch -D tmp-local-03359a1

Write-Host "✅ 推送完成！请在 GitHub 上验证 https://github.com/Iliyasfiel/Caduceus/tree/ui-redesign" -ForegroundColor Green
```

---

## 7. 附录：git bundle 单文件方案

如果你不想拷贝整个项目目录，可以用 git bundle 把仓库打包成单文件：

### 在当前离线机器上：

```bash
cd D:\Develop\solo\xxxxxx
git bundle create caduceus.bundle --all
```

`caduceus.bundle` 这个文件就包含了**整个仓库**（所有分支、所有 commit、所有 tag）。

### 在联网机器上：

```bash
# 1. 从 bundle 克隆（替代 git clone）
git clone caduceus.bundle Caduceus
cd Caduceus

# 2. 添加远程
git remote add origin https://github.com/Iliyasfiel/Caduceus.git

# 3. 拉取远程所有引用
git fetch origin

# 4. 临时保存本地 main
git branch tmp-local-main main

# 5. 重置本地 main 到远程 ui-redesign
git checkout main
git reset --hard origin/ui-redesign

# 6. 推送
git push -u origin main:ui-redesign

# 7. 清理
git branch -D tmp-local-main
```

---

## 8. 推送后验证

到 GitHub 上 `https://github.com/Iliyasfiel/Caduceus/tree/ui-redesign` 验证：

1. **分支存在** ✅
2. **历史完整** ✅（看到 ui-redesign 原有 commit + 你本地的 `03359a1`）
3. **main 分支未变** ✅（远程 main 的 hash 应该和推送前完全一样）

如果在 GitHub 上看到 main 分支有任何变化，**立刻**：
1. 不要继续操作
2. 联系仓库管理员
3. 准备用 `git push origin <旧hash>:main --force-with-lease` 回滚

---

## 9. 删除本文件

推送完成并验证无误后，本文件（`dev-tmp/git-push-guide.md`）即可删除。按规则需先向用户确认。

**本文件解决的是一次性需求**（离线 → 联网 → 推送），完成后使命结束。
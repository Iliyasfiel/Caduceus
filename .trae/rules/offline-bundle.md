# 离线开发（git bundle）

> 针对**联网环境 B ↔ 离线环境 A** 来回切换的开发场景，必须使用 `git bundle` 同步，禁止直接拷贝整个目录（含 `.git/`）。

## 为什么用 bundle 而不是拷贝目录

| 方式 | 体积 | 校验 | 增量同步 | 备注 |
|---|---|---|---|---|
| 拷整目录 + `tar.gz` | 巨大（含 `node_modules` / `.venv` 可达 GB 级） | 损坏无感 | ❌ | Windows 上拷贝 `.git/` 易出现 unlink 警告 |
| `git bundle` | 极小（仅 git 对象，几 MB~几十 MB） | 自带 CRC，可用 `git bundle verify` 自检 | ✅ | 即"git-aware 单文件传输格式" |

## 标准双向流程

### 方向 1：环境 B（有网）→ 环境 A（离线，需带着代码过去）
```bash
# B 上：拉取最新 + 打包全部分支
cd caduceus
git checkout main && git pull origin main
git bundle create /media/usb/caduceus-$(date +%Y%m%d-%H%M%S)-from-B.bundle --all

# A 上：从 bundle 一键克隆（A 上仅需一个空目录）
mkdir -p /tmp/caduceus && cd /tmp/caduceus
git clone /media/usb/caduceus-from-B.bundle .
# 验证
git bundle verify /media/usb/caduceus-from-B.bundle
git log --oneline -5 && git branch -a
```

### 方向 2：环境 A（离线）→ 环境 B（有网，开发完要推送云端）
```bash
# A 上：先把所有改动 commit，工作区必须 clean
cd caduceus
git status                                  # 必须 nothing to commit
git add -A && git commit -m "..."
git bundle create /media/usb/caduceus-$(date +%Y%m%d-%H%M%S)-from-A.bundle --all

# B 上：fetch bundle → 可选 rebase → push
cd caduceus && git fetch origin             # 拉取云端在 A 离线期间的新提交
git fetch /media/usb/caduceus-from-A.bundle --all
git bundle verify /media/usb/caduceus-from-A.bundle
git checkout feature/<scope>-<short-desc>
git rebase origin/main                      # 处理可能的分叉/冲突
git push -u origin feature/<scope>-<short-desc>
```

## 关键纪律
- **打包前工作区必须 clean**：`git status` 输出必须是 "nothing to commit, working tree clean"，否则 bundle 不完整。
- **接收后先 verify**：`git bundle verify xxx.bundle` 第一件事做，损坏则重拷。
- **fetch 必须带 `--all`**：否则只 fetch 当前分支，离线上创建的 feature 分支会丢失。
- **二次回到 A 时做增量同步**：A 上已有完整仓库时，用 `git fetch bundle-file --all`，而不是再 `git clone` 一遍。
- **环境差异处理**：A 上首次跑代码需重新生成 `backend/.venv`（`python -m venv` + `pip install -r requirements.txt`）与 `frontend/node_modules`（`npm install`），这些不应进入 bundle。
- **备份命名约定**：bundle 文件名带时间戳（`caduceus-YYYYMMDD-HHMM-from-B.bundle`），便于事后追溯。
- **敏感信息**：bundle 内含完整 git 历史，**严禁**在 bundle 中包含数据库密码、API Key 等任何凭据；如需传敏感数据请单独用加密通道。

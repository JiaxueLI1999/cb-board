# 家庭看板发布 · 一次性配置（约5分钟）

目标：爸爸打开一个固定网址 → 输一次密码（浏览器记住）→ 随时看最新看板。
安全：整个看板用 AES-256-GCM 加密后才上网，没密码只是密文；密码只存在本目录 `.password` 文件里，永不入库（.gitignore 已排除）。

## 你要做的三步（在终端里，只做一次）

**第0步 设密码**：编辑本目录 `.password` 文件，把占位符改成你们的家庭密码（一行）。占位符不改，发布脚本会拒绝运行。

**第1步 建仓库**：登录 github.com（没账号先免费注册）→ 右上角 + → New repository → 名字随意（如 `cb-board`）→ **Public** → Create。
然后到 Settings → Pages → Source 选 `main` 分支 `/ (root)` → Save。

**第2步 连接并首推**（终端里逐行执行，`<用户名>`、`<仓库名>` 换成你的；会提示登录，用 GitHub 网页弹出的方式授权即可）：
```
cd /Users/lijiaxue/Documents/Claude/Projects/可转债量化/dashboard_publish
python3 -m pip install cryptography -q
python3 encrypt_dashboard.py <最新看板html路径>    # 用真密码重新加密
git remote add origin https://github.com/<用户名>/<仓库名>.git
git push -u origin main
```
（若推送要求登录：装 GitHub Desktop 登录一次，或用 `gh auth login`，凭据由 Git 自己保存，别写进任何文件。）

**完成**：网址就是 `https://<用户名>.github.io/<仓库名>/`，发给爸爸收藏。首次打开输密码勾选"记住"，以后免输。

## 日常（全自动，无需任何人操作）
每天 8:05 和 9:09 的定时任务在更新看板后，会自动：重新加密 → git commit → git push。爸爸刷新页面即是最新（GitHub Pages 生效约1分钟）。

## 备注
- 国内访问 github.io 大多数时候没问题；若爸爸那边打不开，告诉 Claude，切换备用通道（jsDelivr 镜像或腾讯云COS）。
- 换密码：改 `.password` → 重跑 encrypt_dashboard.py → push；爸爸端重新输一次。
- 密码只保护数据不被陌生人看，不要用银行等重要密码复用。

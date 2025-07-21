# 🚀 GitHub部署命令

## 在PowerShell中运行以下命令：

```powershell
# 1. 配置Git用户信息
git config user.email "velist@github.com"
git config user.name "velist"

# 2. 修复远程仓库地址
git remote remove origin
git remote add origin https://github.com/velist/ai-news-pusher.git

# 3. 提交所有更改
git add .
git commit -m "🚀 AI新闻自动推送系统 - 完整版本"

# 4. 创建仓库并推送（如果仓库不存在）
# 先在GitHub上创建名为 ai-news-pusher 的仓库，然后：
git push -u origin main
```

## 📋 GitHub Secrets 设置

在 https://github.com/velist/ai-news-pusher/settings/secrets/actions 添加：

| Name | Value |
|------|-------|
| `GNEWS_API_KEY` | `c3cb6fef0f86251ada2b515017b97143` |
| `FEISHU_APP_ID` | `cli_a8f4efb90f3a1013` |
| `FEISHU_APP_SECRET` | `lCVIsMEiXI6yaOCHa0OkFgOjWcCpy3t8` |
| `FEISHU_TABLE_URL` | `https://jcnew7lc4a8b.feishu.cn/base/TXkMb0FBwaD52ese70ScPLn5n5b` |

## ⚡ 快速执行

或者运行批处理文件：
```cmd
git_setup.bat
```
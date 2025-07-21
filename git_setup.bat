@echo off
echo 🔧 配置Git并推送到GitHub...
echo.

:: 配置Git用户信息
git config user.email "velist@github.com"
git config user.name "velist"

:: 检查并修复远程仓库地址
git remote remove origin 2>NUL
git remote add origin https://github.com/velist/ai-news-pusher.git

:: 添加所有文件并提交
git add .
git commit -m "🚀 AI新闻自动推送系统 - 完整版本"

:: 推送到GitHub
echo 📤 推送到GitHub仓库...
git push -u origin main

echo.
echo ✅ 如果推送成功，请继续设置GitHub Secrets
echo 📋 需要设置的Secrets:
echo    GNEWS_API_KEY: c3cb6fef0f86251ada2b515017b97143
echo    FEISHU_APP_ID: cli_a8f4efb90f3a1013
echo    FEISHU_APP_SECRET: lCVIsMEiXI6yaOCHa0OkFgOjWcCpy3t8
echo    FEISHU_TABLE_URL: https://jcnew7lc4a8b.feishu.cn/base/TXkMb0FBwaD52ese70ScPLn5n5b
echo.
echo 🔗 仓库地址: https://github.com/velist/ai-news-pusher
echo 📝 Secrets设置: https://github.com/velist/ai-news-pusher/settings/secrets/actions
pause
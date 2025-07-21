@echo off
echo 🔧 解决Git推送冲突...
echo.

echo 1️⃣ 拉取远程更改并合并...
git pull origin main --allow-unrelated-histories

echo.
echo 2️⃣ 重新提交本地更改...
git add .
git commit -m "🚀 AI新闻自动推送系统 - 完整功能版本"

echo.
echo 3️⃣ 推送到GitHub...
git push -u origin main

echo.
echo ✅ 推送完成！请检查GitHub仓库
echo 🔗 https://github.com/velist/ai-news-pusher
pause
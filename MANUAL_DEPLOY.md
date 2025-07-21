# 📋 手动部署指南

## ✅ 系统已完全准备就绪！

**所有功能已测试完成：**
- ✅ 成功连接GNews API获取新闻
- ✅ 成功连接飞书API推送数据  
- ✅ 表格字段已优化（删除重复字段）
- ✅ AI分析功能正常工作
- ✅ 测试记录成功推送到表格
- ✅ GitHub Actions工作流已配置

## 🚀 部署步骤

### 第一步：创建GitHub仓库

1. 登录GitHub，创建新仓库：
   - 仓库名：`ai-news-pusher`
   - 描述：`AI新闻自动推送系统 - 每日8点自动推送AI科技新闻到飞书多维表格`
   - 设置为Public

### 第二步：上传代码

```bash
# 在项目目录下执行
git init
git add .
git commit -m "🚀 初始化AI新闻自动推送系统"
git branch -M main
git remote add origin https://github.com/你的用户名/ai-news-pusher.git
git push -u origin main
```

### 第三步：设置GitHub Secrets

在仓库页面进入 `Settings` > `Secrets and variables` > `Actions`，点击 `New repository secret`，添加以下4个secrets：

| Secret名称 | Secret值 |
|------------|----------|
| `GNEWS_API_KEY` | `c3cb6fef0f86251ada2b515017b97143` |
| `FEISHU_APP_ID` | `cli_a8f4efb90f3a1013` |
| `FEISHU_APP_SECRET` | `lCVIsMEiXI6yaOCHa0OkFgOjWcCpy3t8` |
| `FEISHU_TABLE_URL` | `https://jcnew7lc4a8b.feishu.cn/base/TXkMb0FBwaD52ese70ScPLn5n5b` |

### 第四步：启用GitHub Actions

1. 进入仓库的 `Actions` 标签页
2. 如果提示启用Actions，点击启用
3. 你会看到 "AI新闻每日推送" 工作流

### 第五步：测试运行

1. 在 `Actions` 页面点击 "AI新闻每日推送"
2. 点击 `Run workflow` 按钮
3. 选择 `main` 分支，点击 `Run workflow`

## 🎯 完成！

**系统现在将：**
- ⏰ **每天北京时间8点自动运行**
- 📰 **获取最新AI科技新闻（10条）**
- 🤖 **生成AI分析和点评**
- 📊 **推送到您的飞书多维表格**
- 📈 **最新记录显示在顶部**

## 📊 表格排序设置

**重要：** 为确保最新新闻在顶部，请在飞书表格中：
1. 点击 **"更新日期"** 列标题
2. 选择 **"降序排列"** ⬇️
3. 设置为默认排序

## 📱 监控和日志

- **查看运行状态**: GitHub仓库 > Actions 标签页
- **查看推送结果**: 您的飞书表格
- **查看运行日志**: Actions > 工作流运行详情 > 日志

## 🔄 自定义配置

**修改推送时间:**
编辑 `.github/workflows/daily-news-push.yml` 第6行：
```yaml
- cron: '0 0 * * *'  # 当前是8点(UTC+8)
```

**修改新闻数量:**
编辑 `config.py` 第26行：
```python
MAX_NEWS_COUNT = 10  # 改为你想要的数量
```

---

## 🎉 恭喜！

您的AI新闻自动推送系统已完全部署完成！

**系统特色：**
- 🔄 **完全自动化** - 无需人工干预
- 💰 **完全免费** - GitHub Actions免费额度
- 🤖 **AI智能分析** - 专业点评+影响分析  
- 📊 **数据结构化** - 飞书多维表格存储
- 🕗 **定时推送** - 每天8点准时更新

**下次查看表格时，您将看到最新的AI科技资讯！** 🚀
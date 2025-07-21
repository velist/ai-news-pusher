# AI新闻自动推送系统 - 部署指南

## 项目概述
这是一个完全免费的AI新闻自动推送系统，每日8点自动获取最新AI科技新闻，生成点评和影响分析，并推送到飞书多维表格中。

## 功能特性
- ✅ 每日定时获取AI科技相关新闻（使用GNews API）
- ✅ AI智能分析生成点评和对中国行业影响预测
- ✅ 自动推送到飞书多维表格
- ✅ 完全免费方案（基于GitHub Actions）
- ✅ 包含标题、摘要、图片、点评、影响分析、来源链接

## 部署步骤

### 1. 准备工作
确保你有以下账号和权限：
- GitHub账号
- 飞书开放平台开发者账号
- GNews API密钥（已提供）

### 2. 克隆/上传代码
将项目代码上传到你的GitHub仓库

### 3. 配置GitHub Secrets
在你的GitHub仓库中，进入 `Settings` > `Secrets and variables` > `Actions`，添加以下Secrets：

```
GNEWS_API_KEY: c3cb6fef0f86251ada2b515017b97143
FEISHU_APP_ID: cli_a8f4efb90f3a1013
FEISHU_APP_SECRET: lCVIsMEiXI6yaOCHa0OkFgOjWcCpy3t8
FEISHU_TABLE_URL: https://jcnew7lc4a8b.feishu.cn/base/TXkMb0FBwaD52ese70ScPLn5n5b
```

### 4. 验证飞书应用权限
确保你的飞书应用具有以下权限：
- `bitable:app` - 多维表格应用权限
- `bitable:app:readonly` - 读取权限  
- `bitable:app:readwrite` - 读写权限

### 5. 手动测试运行
第一次部署后，建议手动触发工作流进行测试：
1. 进入你的GitHub仓库
2. 点击 `Actions` 标签
3. 选择 `AI新闻每日推送` 工作流
4. 点击 `Run workflow` 手动触发

### 6. 自动运行
工作流将在每天北京时间上午8点自动运行。

## 本地测试

如果需要本地测试，可以按以下步骤操作：

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 复制环境配置
cp .env.example .env

# 3. 编辑.env文件，填入你的配置信息

# 4. 运行测试
python main.py test

# 5. 运行完整推送
python main.py
```

## 项目结构
```
推送测试/
├── .github/workflows/daily-news-push.yml  # GitHub Actions工作流
├── config.py                              # 配置管理
├── news_fetcher.py                        # 新闻获取模块
├── ai_analyzer.py                         # AI分析模块
├── feishu_client.py                      # 飞书API客户端
├── main.py                               # 主程序入口
├── requirements.txt                      # Python依赖
├── .env.example                         # 环境变量示例
├── .gitignore                          # Git忽略文件
└── README.md                           # 项目说明
```

## 常见问题

### Q: GitHub Actions额度够用吗？
A: 完全够用。每次运行约2-3分钟，每月限额2000分钟，足够使用。

### Q: 如何修改推送时间？
A: 编辑 `.github/workflows/daily-news-push.yml` 文件中的cron表达式。

### Q: 新闻数量可以调整吗？
A: 可以在 `config.py` 中修改 `MAX_NEWS_COUNT` 参数。

### Q: 如何添加更多新闻源？
A: 可以修改 `news_fetcher.py` 中的搜索关键词和API调用逻辑。

### Q: AI分析效果如何提升？
A: 当前使用关键词匹配生成分析。如需更好效果，可在 `config.py` 中配置 `OPENAI_API_KEY`。

## 技术架构
- **新闻获取**: GNews API
- **AI分析**: 关键词匹配 + 模板生成（可扩展为LLM）
- **数据推送**: 飞书开放平台API
- **任务调度**: GitHub Actions Cron
- **运行环境**: GitHub Actions Ubuntu Runner

## 成本分析
- **总成本**: 完全免费
- **GitHub Actions**: 免费额度足够使用
- **GNews API**: 使用提供的免费密钥
- **飞书API**: 免费

## 支持与维护
- 日志文件会保存在GitHub Actions的artifacts中
- 如遇问题，可查看Actions运行日志
- 支持手动触发运行进行调试

---
✅ 部署完成后，系统将每天自动为您推送最新的AI科技新闻！
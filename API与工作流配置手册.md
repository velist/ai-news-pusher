# 🤖 AI新闻推送系统 - API与工作流配置手册

## 📋 项目简介

本手册详细介绍了如何配置和部署AI新闻推送系统，包括新闻API申请、翻译API配置、GitHub工作流设置等完整流程。该系统能够自动获取AI相关新闻、进行智能翻译并生成中文新闻网站。

**系统特点：**
- 🌍 支持多语言新闻源获取
- 🧠 AI智能翻译（成本降低80-95%）
- 🕐 中文时区本地化
- 📱 响应式H5界面
- ⚡ 自动化部署和更新
- 💰 成本优化（年节省¥276-1944）

---

## 🔑 第一步：新闻API配置

### 1.1 GNews API申请

**推荐指数：⭐⭐⭐⭐⭐**

GNews是本系统使用的主要新闻数据源，提供实时、多语言的新闻聚合服务。

#### 申请步骤：

1. **访问官网**
   ```
   https://gnews.io/
   ```

2. **注册账户**
   - 点击右上角"Sign Up"
   - 填写邮箱和密码
   - 验证邮箱地址

3. **获取API密钥**
   - 登录后进入Dashboard
   - 在"API Key"页面复制你的密钥
   - 格式示例：`c3cb6fef0f86251ada2b515017b97143`

#### 配额说明：
```
【免费套餐】
- 每月100次请求
- 每次最多10条新闻
- 适合测试和小规模使用

【付费套餐】
- Starter: $9/月，500次请求
- Pro: $29/月，2500次请求  
- Business: $99/月，25000次请求
```

#### API参数说明：
```javascript
// 基础参数
{
  "apikey": "你的API密钥",
  "q": "AI OR OpenAI OR ChatGPT",     // 搜索关键词
  "lang": "en",                        // 语言
  "country": "us",                     // 国家
  "max": "10",                         // 每次获取数量
  "sortby": "publishedAt",            // 排序方式
  "from": "2025-01-24"                // 起始日期
}
```

### 1.2 备用新闻API

#### NewsAPI（备选方案）
```
官网：https://newsapi.org/
免费配额：每月1000次请求
优点：数据质量高，更新及时
缺点：免费版有域名限制
```

#### Current API（经济选择）
```
官网：https://currentsapi.services/
免费配额：每月600次请求  
优点：无域名限制
缺点：新闻源相对较少
```

---

## 🌐 第二步：翻译API配置

### 2.1 硅基流动API（推荐⭐⭐⭐⭐⭐）

硅基流动是本系统的核心翻译服务，提供高质量AI翻译，成本仅为传统翻译API的5-20%。

#### 申请步骤：

1. **注册账户**
   ```
   官网：https://siliconflow.cn/
   ```
   - 使用手机号或邮箱注册
   - 完成实名认证（个人认证即可）

2. **获取API密钥**
   - 进入控制台 → API密钥管理
   - 创建新的API密钥
   - 复制密钥（格式：sk-xxxxxxxxxx）

3. **充值（建议）**
   ```
   最低充值：¥10
   推荐充值：¥50-100（够用1-2年）
   ```

#### 成本分析：
```
【硅基流动成本】
- 翻译费用：¥2-10/百万字符
- 年度成本：¥24-120（基于日均100条新闻）

【对比其他服务】
- 百度翻译：¥49-58/百万字符（贵5-25倍）
- 腾讯翻译：¥58/百万字符（贵6-29倍）
- Google翻译：¥140-280/百万字符（贵14-140倍）

【节省计算】
年度节省：¥276-1944（成本降低80-95%）
```

#### 推荐模型：
```javascript
// 性价比首选
"Qwen/Qwen2.5-7B-Instruct"

// 质量优先
"Qwen/Qwen2.5-14B-Instruct"

// 英文翻译特化
"meta-llama/Meta-Llama-3.1-8B-Instruct"

// 中文理解优化
"THUDM/glm-4-9b-chat"
```

### 2.2 备用翻译API

#### 百度翻译API
```
官网：https://fanyi-api.baidu.com/
免费额度：每月5万字符
申请难度：⭐⭐⭐
成本：中等
```

#### 腾讯翻译API
```
官网：https://cloud.tencent.com/product/tmt
免费额度：每月500万字符
申请难度：⭐⭐⭐⭐
成本：中等
```

#### 谷歌翻译API
```
官网：https://cloud.google.com/translate
免费额度：每月50万字符
申请难度：⭐⭐⭐⭐⭐
成本：较高
```

---

## ⚙️ 第三步：环境变量配置

### 3.1 创建.env文件

在项目根目录创建`.env`文件：

```bash
# 新闻API配置
GNEWS_API_KEY=你的GNews API密钥

# 翻译API配置
SILICONFLOW_API_KEY=你的硅基流动API密钥

# 备用翻译API（可选）
BAIDU_APP_ID=你的百度APP ID
BAIDU_SECRET_KEY=你的百度密钥
TENCENT_SECRET_ID=你的腾讯密钥ID
TENCENT_SECRET_KEY=你的腾讯密钥
GOOGLE_API_KEY=你的谷歌API密钥

# 部署配置（可选）
VERCEL_TOKEN=你的Vercel令牌
```

### 3.2 环境变量说明

| 变量名 | 必需 | 说明 | 示例 |
|--------|------|------|------|
| `GNEWS_API_KEY` | ✅ | GNews API密钥 | `c3cb6fef0f86...` |
| `SILICONFLOW_API_KEY` | ✅ | 硅基流动API密钥 | `sk-xxxxx...` |
| `BAIDU_APP_ID` | ❌ | 百度翻译APP ID | `20250124...` |
| `BAIDU_SECRET_KEY` | ❌ | 百度翻译密钥 | `abcdef...` |
| `TENCENT_SECRET_ID` | ❌ | 腾讯云密钥ID | `AKID...` |
| `TENCENT_SECRET_KEY` | ❌ | 腾讯云密钥 | `xyz123...` |
| `GOOGLE_API_KEY` | ❌ | 谷歌翻译API密钥 | `AIza...` |

---

## 🚀 第四步：GitHub工作流配置

### 4.1 创建GitHub仓库

1. **创建新仓库**
   ```
   仓库名称：ai-news-pusher（可自定义）
   可见性：Public（用于GitHub Pages）
   初始化：README、.gitignore（Python）
   ```

2. **克隆到本地**
   ```bash
   git clone https://github.com/你的用户名/ai-news-pusher.git
   cd ai-news-pusher
   ```

### 4.2 配置GitHub Secrets

进入仓库设置 → Secrets and variables → Actions：

```
1. 点击"New repository secret"
2. 添加以下密钥：

Name: GNEWS_API_KEY
Secret: 你的GNews API密钥

Name: SILICONFLOW_API_KEY  
Secret: 你的硅基流动API密钥

Name: BAIDU_APP_ID（可选）
Secret: 你的百度APP ID

Name: BAIDU_SECRET_KEY（可选）
Secret: 你的百度密钥
```

### 4.3 创建工作流文件

在仓库中创建`.github/workflows/daily-news-push.yml`：

```yaml
name: AI新闻每日推送

on:
  schedule:
    # 每小时北京时间整点 (UTC时间每小时)
    - cron: '0 * * * *'
  # 允许手动触发
  workflow_dispatch:

jobs:
  push-news:
    runs-on: ubuntu-latest
    timeout-minutes: 10
    
    steps:
    - name: 检出代码
      uses: actions/checkout@v4
      
    - name: 设置Python环境
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
        
    - name: 运行AI新闻推送
      env:
        GNEWS_API_KEY: ${{ secrets.GNEWS_API_KEY }}
        SILICONFLOW_API_KEY: ${{ secrets.SILICONFLOW_API_KEY }}
      run: |
        # 运行超简化版本（推荐生产环境）
        python ultra_simple_news.py
        
        # 或运行增强版本（功能更完整）
        # python enhanced_chinese_news_accumulator.py
        
    - name: 提交页面更新
      if: always()
      run: |
        git config --local user.email "action@github.com"
        git config --local user.name "GitHub Action"
        
        if [ -f "docs/index.html" ]; then
          git add docs/
          git commit -m "🚀 AI新闻推送更新 - $(date '+%Y-%m-%d %H:%M')" || echo "无需提交"
          git push || echo "推送失败"
          echo "✅ 新闻页面已更新"
        else
          echo "❌ 页面生成失败"
        fi
        
    - name: 显示结果
      if: always()
      run: |
        echo "=== AI新闻推送任务完成 ==="
        if [ -f "docs/index.html" ]; then
          echo "✅ 页面已生成: docs/index.html"
          echo "🌐 访问地址: https://$(echo ${{ github.repository }} | cut -d'/' -f1).github.io/$(echo ${{ github.repository }} | cut -d'/' -f2)/"
        else
          echo "❌ 页面生成失败"
        fi
```

### 4.4 GitHub Pages配置

1. **启用GitHub Pages**
   ```
   仓库设置 → Pages
   Source: Deploy from a branch
   Branch: main
   Folder: /docs
   ```

2. **自定义域名（可选）**
   ```
   Custom domain: 你的域名
   Enforce HTTPS: ✅
   ```

---

## 🌐 第五步：Vercel部署配置

### 5.1 Vercel账户设置

1. **注册Vercel**
   ```
   官网：https://vercel.com/
   使用GitHub账户登录
   ```

2. **导入项目**
   ```
   Dashboard → Add New → Project
   从GitHub导入你的仓库
   ```

### 5.2 创建vercel.json配置

在项目根目录创建`vercel.json`：

```json
{
  "version": 2,
  "cleanUrls": true,
  "trailingSlash": false,
  "rewrites": [
    {
      "source": "/",
      "destination": "/docs/index.html"
    },
    {
      "source": "/news/(.*)",
      "destination": "/docs/news/$1"
    }
  ],
  "headers": [
    {
      "source": "/docs/(.*)",
      "headers": [
        {
          "key": "Cache-Control",
          "value": "public, max-age=300, s-maxage=3600"
        }
      ]
    }
  ]
}
```

### 5.3 环境变量配置

在Vercel Dashboard中：
```
项目设置 → Environment Variables

添加：
- GNEWS_API_KEY: 你的API密钥
- SILICONFLOW_API_KEY: 你的API密钥
```

---

## 🔧 第六步：系统架构与工作机制

### 6.1 整体架构图

```
   ┌─────────────┐    ┌──────────────┐    ┌─────────────┐
   │  GNews API  │───▶│  新闻获取模块  │───▶│  数据预处理  │
   └─────────────┘    └──────────────┘    └─────────────┘
           │                  │                    │
           ▼                  ▼                    ▼
   ┌─────────────┐    ┌──────────────┐    ┌─────────────┐
   │ 硅基流动API │───▶│  AI翻译引擎   │───▶│  质量评估    │
   └─────────────┘    └──────────────┘    └─────────────┘
           │                  │                    │
           ▼                  ▼                    ▼
   ┌─────────────┐    ┌──────────────┐    ┌─────────────┐
   │  时区转换   │───▶│  中文本地化   │───▶│  HTML生成   │
   └─────────────┘    └──────────────┘    └─────────────┘
           │                  │                    │
           ▼                  ▼                    ▼
   ┌─────────────┐    ┌──────────────┐    ┌─────────────┐
   │GitHub Actions│───▶│  自动部署    │───▶│  网站更新   │
   └─────────────┘    └──────────────┘    └─────────────┘
```

### 6.2 工作流程详解

#### 步骤1：新闻数据获取
```python
# 多类别新闻获取
search_queries = [
    {
        'query': 'AI OR OpenAI OR ChatGPT OR "artificial intelligence"',
        'category': 'AI科技',
        'max': '15'
    },
    {
        'query': 'gaming OR PlayStation OR Xbox OR Nintendo',
        'category': '游戏资讯',
        'max': '10'
    },
    {
        'query': 'stock OR bitcoin OR finance OR cryptocurrency',
        'category': '经济新闻',
        'max': '10'
    }
]
```

#### 步骤2：AI智能翻译
```python
# 硅基流动翻译配置
translator = SiliconFlowTranslator(
    api_key=os.getenv('SILICONFLOW_API_KEY'),
    model="Qwen/Qwen2.5-7B-Instruct"
)

# 批量翻译优化
translation_result = translator.translate_text(
    text=article['title'],
    source_lang='en',
    target_lang='zh'
)
```

#### 步骤3：时区和本地化处理
```python
# 时区转换（UTC → 北京时间）
beijing_time = timezone_converter.format_news_time(article['publishedAt'])

# 中文本地化
localized_summary = chinese_localizer.format_news_summary(article)

# 新鲜度评分
freshness_score = freshness_manager.calculate_freshness_score(article)
```

#### 步骤4：HTML页面生成
```python
# 响应式HTML生成
html_content = generate_html(
    articles=processed_articles,
    categories=['全部', 'AI科技', '游戏资讯', '经济新闻'],
    update_time=datetime.now()
)
```

#### 步骤5：自动化部署
```yaml
# GitHub Actions定时任务
schedule:
  - cron: '0 * * * *'  # 每小时执行

# 双平台部署
# 1. GitHub Pages (主要)
# 2. Vercel (备用 + CDN)
```

### 6.3 数据流和缓存策略

#### 数据存储结构
```json
{
  "last_updated": "2025-01-27T10:30:00+08:00",
  "total_count": 45,
  "freshness_summary": {
    "fresh": 12,
    "recent": 18,
    "older": 15
  },
  "articles": [
    {
      "id": "ai_0_1753614821",
      "title": "OpenAI发布最新GPT模型",
      "ai_translation": {
        "translated_title": "OpenAI发布最新GPT模型，性能显著提升",
        "translated_description": "OpenAI今日发布了最新的GPT模型...",
        "translation_confidence": 0.92
      },
      "time_info": {
        "beijing_time": "2025-01-27T10:15:00+08:00",
        "relative": "15分钟前",
        "formatted": "2025年01月27日 10:15"
      },
      "freshness_score": 0.95,
      "category_chinese": "AI科技"
    }
  ]
}
```

#### 缓存机制
```python
# 三级缓存体系
1. 内存缓存：翻译结果实时缓存
2. 文件缓存：新闻数据本地存储  
3. CDN缓存：Vercel全球CDN加速
```

---

## 📊 第七步：监控与优化

### 7.1 监控指标

#### 核心性能指标
```
🔄 新闻获取成功率：>95%
🌐 翻译成功率：>90%
⏱️ 页面生成时间：<3分钟
🚀 部署成功率：>98%
💰 月运行成本：<¥10
```

#### 质量指标
```
📝 翻译质量评分：>0.85
🕐 时区转换准确率：100%
📱 移动端适配：完全支持
🔍 SEO优化得分：>90
```

### 7.2 成本优化策略

#### API调用优化
```python
# 智能调用策略
1. 新鲜度筛选：只对新鲜度>0.7的新闻生成AI点评
2. 批量翻译：多条新闻合并翻译，减少API调用
3. 缓存复用：相同内容避免重复翻译
4. 错误重试：失败自动重试，避免浪费配额
```

#### 运行时间优化
```python
# 并行处理优化
1. 多线程获取：不同分类新闻并行获取
2. 异步翻译：翻译任务异步处理
3. 增量更新：只处理新增和变更的新闻
4. 超时控制：设置合理的超时时间
```

### 7.3 故障排除指南

#### 常见问题及解决方案

**问题1：API配额超限**
```
症状：翻译失败，返回429错误
解决：
1. 检查API账户余额和配额
2. 启用备用翻译服务
3. 调整获取新闻数量
4. 增加API调用间隔
```

**问题2：GitHub Actions执行失败**
```
症状：工作流运行失败，页面未更新
解决：
1. 检查Secrets配置是否正确
2. 确认API密钥有效性
3. 查看Actions日志详细错误
4. 手动触发工作流测试
```

**问题3：Vercel部署失败**
```
症状：Vercel网站显示404或构建失败
解决：
1. 检查vercel.json配置语法
2. 确认docs目录存在且有内容
3. 检查环境变量配置
4. 查看Vercel构建日志
```

**问题4：翻译质量不佳**
```
症状：翻译结果不准确或格式混乱
解决：
1. 切换到更高质量的模型
2. 优化翻译提示词
3. 启用质量评估过滤
4. 使用备用翻译服务
```

### 7.4 性能调优建议

#### 系统性能优化
```python
# 建议配置
新闻获取数量：每类别10-15条
翻译并发数：3-5个
页面更新频率：每小时1次
数据保留时间：3天
```

#### 用户体验优化
```css
/* 响应式设计优化 */
@media (max-width: 768px) {
    .news-grid { grid-template-columns: 1fr; }
    .header h1 { font-size: 2em; }
}

/* 加载性能优化 */
- 图片懒加载
- CSS/JS压缩
- CDN加速
- 缓存策略
```

---

## 🎯 第八步：高级功能扩展

### 8.1 个性化设置

#### 新闻分类定制
```python
# 可扩展的分类配置
CUSTOM_CATEGORIES = {
    'ai_tech': {
        'name': 'AI科技',
        'query': 'AI OR OpenAI OR ChatGPT OR "artificial intelligence"',
        'max_articles': 15,
        'priority': 'high'
    },
    'blockchain': {
        'name': '区块链',
        'query': 'blockchain OR bitcoin OR cryptocurrency OR DeFi',
        'max_articles': 8,
        'priority': 'medium'
    },
    'startup': {
        'name': '创业投资',
        'query': 'startup OR venture capital OR IPO OR funding',
        'max_articles': 8,
        'priority': 'medium'
    }
}
```

#### 多语言支持
```python
# 支持的语言对
SUPPORTED_LANGUAGES = {
    'en-zh': {'source': 'en', 'target': 'zh', 'name': '英译中'},
    'ja-zh': {'source': 'ja', 'target': 'zh', 'name': '日译中'},
    'ko-zh': {'source': 'ko', 'target': 'zh', 'name': '韩译中'},
    'fr-zh': {'source': 'fr', 'target': 'zh', 'name': '法译中'}
}
```

### 8.2 AI功能增强

#### 智能摘要生成
```python
def generate_smart_summary(article):
    """生成智能摘要"""
    prompt = f"""
    请为以下新闻生成一个150字以内的中文摘要，要求：
    1. 突出关键信息和要点
    2. 保持客观中性的语调
    3. 适合中文读者阅读习惯
    
    新闻标题：{article['title']}
    新闻内容：{article['content']}
    """
    return ai_service.generate_summary(prompt)
```

#### 情感分析
```python
def analyze_sentiment(article):
    """分析新闻情感倾向"""
    return {
        'sentiment': 'positive|neutral|negative',
        'confidence': 0.85,
        'keywords': ['AI', '突破', '创新'],
        'tone': '乐观积极'
    }
```

### 8.3 数据分析功能

#### 新闻趋势分析
```python
class NewsAnalyzer:
    def analyze_trends(self, articles, days=7):
        """分析新闻趋势"""
        return {
            'hot_keywords': ['AI', 'ChatGPT', '元宇宙'],
            'category_distribution': {
                'AI科技': 45,
                '游戏资讯': 25,
                '经济新闻': 30
            },
            'sentiment_trend': 'increasing_positive',
            'coverage_analysis': {
                'most_covered': 'OpenAI新产品发布',
                'emerging_topics': ['AI安全', '监管政策']
            }
        }
```

---

## 🔐 第九步：安全性配置

### 9.1 API密钥安全

#### 最佳实践
```bash
# ✅ 正确做法
- 使用环境变量存储密钥
- 配置GitHub Secrets
- 定期轮换API密钥
- 设置API调用限制

# ❌ 避免做法
- 密钥硬编码在代码中
- 密钥提交到Git仓库
- 使用弱密钥或默认密钥
- 密钥明文存储
```

#### 密钥管理工具
```python
# 密钥验证和管理
class APIKeyManager:
    def validate_key(self, key, service):
        """验证API密钥有效性"""
        patterns = {
            'gnews': r'^[a-f0-9]{32}$',
            'siliconflow': r'^sk-[a-zA-Z0-9]{32,}$',
            'baidu': r'^\d{20}$'
        }
        return re.match(patterns.get(service, ''), key) is not None
    
    def rotate_keys(self):
        """密钥轮换提醒"""
        # 实现密钥到期提醒逻辑
        pass
```

### 9.2 数据安全

#### 敏感数据处理
```python
# 数据脱敏处理
def sanitize_data(data):
    """数据脱敏"""
    sensitive_patterns = [
        r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',  # 信用卡号
        r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # 邮箱
        r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'  # 电话号码
    ]
    
    for pattern in sensitive_patterns:
        data = re.sub(pattern, '***', data)
    
    return data
```

#### 访问控制
```yaml
# GitHub仓库安全设置
security:
  branch_protection: true
  required_reviews: 1
  dismiss_stale_reviews: true
  restrict_pushes: true
  required_status_checks: true
```

---

## 📚 第十步：文档和维护

### 10.1 使用文档

#### 用户快速开始指南
```markdown
# 5分钟快速部署

1. Fork本仓库
2. 配置GitHub Secrets（API密钥）
3. 启用GitHub Pages
4. 等待自动运行（每小时更新）
5. 访问你的新闻网站

网站地址：https://你的用户名.github.io/仓库名/
```

#### 开发者文档
```markdown
# 开发者指南

## 项目结构
- ultra_simple_news.py: 主程序（推荐生产环境）
- enhanced_chinese_news_accumulator.py: 增强版（功能完整）
- translation/: 翻译服务模块
- localization/: 本地化处理模块
- docs/: 生成的网站文件

## 自定义修改
- 修改新闻分类：编辑search_queries配置
- 调整界面样式：修改HTML模板中的CSS
- 添加新功能：扩展相应的处理模块
```

### 10.2 维护计划

#### 定期维护任务
```
每周任务：
- 检查API配额使用情况
- 监控翻译质量和成功率
- 查看GitHub Actions运行日志
- 更新新闻分类和关键词

每月任务：
- 更新依赖包版本
- 检查安全漏洞
- 分析成本和性能数据
- 备份重要配置和数据

每季度任务：
- 评估API服务性价比
- 优化系统架构
- 收集用户反馈
- 规划新功能开发
```

#### 故障响应流程
```
1. 故障检测：监控系统发现异常
2. 问题定位：查看日志和错误信息
3. 应急处理：启用备用方案
4. 根因分析：深入分析故障原因
5. 修复实施：部署修复方案
6. 验证测试：确认问题解决
7. 文档记录：更新故障处理文档
```

---

## 🎉 总结

通过本手册，你已经学会了：

✅ **API配置**：GNews新闻API + 硅基流动翻译API
✅ **环境搭建**：GitHub仓库 + Secrets配置
✅ **工作流设置**：自动化CI/CD流程
✅ **双平台部署**：GitHub Pages + Vercel
✅ **成本优化**：年节省¥276-1944
✅ **监控运维**：故障排除和性能优化

**项目优势：**
- 💰 **成本极低**：年运行成本<¥100
- 🔄 **全自动化**：无人值守自动更新
- 🌍 **多语言**：支持全球新闻源
- 📱 **响应式**：完美移动端体验
- 🔧 **易扩展**：模块化设计便于定制

**立即开始：**
1. Fork项目仓库
2. 按手册配置API密钥
3. 启用GitHub Actions
4. 享受你的AI新闻网站！

**获取支持：**
- 📖 详细文档：README.md
- 🐛 问题反馈：GitHub Issues
- 💡 功能建议：Discussion区
- 🔄 项目更新：Watch仓库获取通知

---

**最后更新：** 2025年1月27日  
**适用版本：** v2.0+  
**维护状态：** ✅ 积极维护中
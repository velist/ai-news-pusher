# 🤖 AI新闻推送H5系统

> 专为中国用户设计的AI科技资讯展示平台，智能翻译 + 本土化分析 + 现代化H5界面

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Vercel Status](https://img.shields.io/badge/Vercel-部署成功-brightgreen)](https://vercel.com)
[![Chinese](https://img.shields.io/badge/语言-中文友好-red)](README.md)

## ✨ 功能特色

- 🌏 **智能中文翻译**: AI技术术语本土化，符合中国用户阅读习惯
- 🇨🇳 **中国影响分析**: 深度解读AI资讯对国内市场的影响
- 💰 **投资视角**: 提供相关概念股分析和投资建议  
- 🎨 **Apple风格设计**: 采用苹果HIG设计规范，现代化H5界面
- 📱 **响应式布局**: 完美适配手机、平板、桌面端
- 🌙 **深色模式**: 自动适应系统主题
- ⚡ **高性能**: Vercel部署，全球CDN加速

## 🚀 在线预览

**主站地址**: [点击访问](https://your-project.vercel.app)

## 📱 界面展示

### 首页 - 新闻列表
- 🗂️ **智能分类**: OpenAI动态、谷歌AI、微软AI、AI硬件、投资动态
- ⭐ **重要性评级**: 5星评分系统，突出重要资讯
- 🎯 **一键筛选**: 按分类快速筛选感兴趣的内容

### 详情页 - 深度解读  
- 📄 **原文对照**: 中英文标题和内容对比
- 🇨🇳 **本土化分析**: 技术影响 + 市场机遇双重解读
- 💎 **投资洞察**: A股相关概念股推荐
- 🧭 **上下篇导航**: 便捷的文章间跳转

## 🛠️ 技术架构

### 前端技术栈
- **HTML5 + CSS3**: 现代化语义化标签
- **原生JavaScript**: 零依赖，高性能交互
- **CSS Grid + Flexbox**: 响应式布局方案
- **CSS Variables**: 主题色彩管理

### 后端技术栈  
- **Python 3.8+**: 核心业务逻辑
- **智能翻译引擎**: 自研中文本土化系统
- **新闻数据处理**: 多源数据聚合与清洗
- **HTML生成器**: 模板化页面生成

### 部署方案
- **Vercel**: 现代化部署平台
- **GitHub Actions**: 自动化CI/CD
- **全球CDN**: 访问加速优化

## 🏗️ 项目结构

```
📦 AI新闻推送H5系统
├── 📁 docs/                    # 前端静态文件
│   ├── 📄 index.html          # 首页 - 新闻列表
│   ├── 📁 news/               # 详情页目录  
│   └── 📊 news_data.json      # 新闻数据文件
├── 🐍 optimized_html_generator.py  # 核心H5生成器
├── 🐍 main.py                 # 主程序入口
├── 🐍 news_fetcher.py        # 新闻数据获取
├── 🐍 feishu_client.py       # 飞书推送功能
├── 🐍 wechat_push.py          # 微信推送功能
└── 📋 requirements.txt        # Python依赖
```

## 🚀 快速开始

### 环境要求
- Python 3.8+
- Git

### 本地运行
```bash
# 1. 克隆项目
git clone https://github.com/velist/ai-news-pusher.git
cd ai-news-pusher

# 2. 安装依赖
pip install -r requirements.txt

# 3. 生成H5页面
python optimized_html_generator.py

# 4. 本地预览
cd docs && python -m http.server 8000
# 访问: http://localhost:8000
```

### 部署到Vercel
1. Fork此项目到你的GitHub
2. 在 [Vercel](https://vercel.com) 导入项目  
3. 设置Output Directory为 `docs`
4. 点击Deploy，完成部署

## 🌟 核心特性详解

### 🌏 智能中文翻译
```python
# 技术术语本土化
'OpenAI' → 'OpenAI'
'Google' → '谷歌' 
'breakthrough' → '突破性进展'
'Large Language Model' → '大语言模型'

# 智能前缀识别
'breakthrough' → '🚀 重大突破：...'
'launch' → '🔥 最新发布：...'  
'investment' → '💰 投资动态：...'
```

### 🇨🇳 中国本土化分析
- **技术影响**: 分析对百度、阿里、腾讯等国内大厂的影响
- **市场机遇**: 识别合作机会和发展思路
- **概念股推荐**: 科大讯飞、汉王科技、寒武纪等相关标的

### 🎨 Apple设计语言
- **色彩系统**: 遵循Apple Human Interface Guidelines
- **交互动效**: 自然流畅的微动画  
- **信息层级**: 清晰的视觉层次和阅读体验

## 📈 项目历程

| 版本 | 日期 | 主要更新 |
|-----|------|---------|
| **v2.0.0** | 2025-07-22 | 🚀 完整H5系统 - 详情页+本土化分析 |
| **v1.5.0** | 2025-07-21 | 🎨 Apple风格界面设计 |  
| **v1.0.0** | 2025-07-20 | 🏗️ 基础系统架构搭建 |

详细更新日志请查看: [PROJECT_STATUS.md](PROJECT_STATUS.md)

## 🤝 贡献指南

欢迎参与项目贡献！

### 贡献方式
1. 🍴 Fork 项目
2. 🌿 创建功能分支 `git checkout -b feature/amazing-feature`
3. 💾 提交更改 `git commit -m 'Add: amazing feature'`
4. 📤 推送分支 `git push origin feature/amazing-feature`  
5. 🔀 创建 Pull Request

### 开发规范
- 📝 提交信息使用中文，格式: `类型: 描述`
- 🧪 新功能需要包含测试用例
- 📚 重要更改需要更新文档
- 🎨 遵循现有代码风格

## 📞 联系与支持

- **🏠 项目主页**: https://github.com/velist/ai-news-pusher
- **🌐 在线预览**: https://your-project.vercel.app  
- **🐛 问题反馈**: [GitHub Issues](https://github.com/velist/ai-news-pusher/issues)

## 📄 开源协议

本项目基于 [MIT License](LICENSE) 开源协议

---

<div align="center">

**⭐ 如果这个项目对你有帮助，请给个Star支持一下！**

Made with ❤️ by [velist](https://github.com/velist)

</div>
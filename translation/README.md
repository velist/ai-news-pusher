# 智能翻译服务系统

一个支持多种翻译API的统一翻译服务系统，特别针对新闻翻译场景优化。

## 🚀 特性

- **统一接口**: 所有翻译服务使用相同的接口，便于切换和管理
- **多服务支持**: 支持百度、腾讯、Google和硅基流动翻译API
- **智能降级**: 自动服务状态监控和故障转移
- **批量处理**: 高效的批量翻译功能
- **质量评估**: 翻译置信度评分和质量评估
- **成本优化**: 支持成本最优的硅基流动AI翻译

## 📦 支持的翻译服务

### 1. 传统翻译API
- **百度翻译**: 免费额度200万字符/月，¥49/百万字符
- **腾讯翻译**: 免费额度500万字符/月，¥58/百万字符  
- **Google翻译**: 免费额度50万字符/月，¥140-280/百万字符

### 2. AI大模型翻译 (推荐)
- **硅基流动**: ¥2-10/百万字符，支持多种先进AI模型
  - `Qwen/Qwen2.5-7B-Instruct` - 性价比最高
  - `Qwen/Qwen2.5-14B-Instruct` - 质量更好
  - `meta-llama/Meta-Llama-3.1-8B-Instruct` - 英文优势
  - `THUDM/glm-4-9b-chat` - 中文理解好

## 🛠️ 安装和配置

### 环境变量配置

```bash
# 百度翻译
export BAIDU_TRANSLATE_APP_ID="your_app_id"
export BAIDU_TRANSLATE_SECRET_KEY="your_secret_key"

# 腾讯翻译
export TENCENT_SECRET_ID="your_secret_id"
export TENCENT_SECRET_KEY="your_secret_key"

# Google翻译
export GOOGLE_TRANSLATE_API_KEY="your_api_key"

# 硅基流动 (推荐)
export SILICONFLOW_API_KEY="your_api_key"
```

## 💡 使用示例

### 基础使用

```python
from translation import SiliconFlowTranslator, BaiduTranslator

# 使用硅基流动翻译 (推荐)
translator = SiliconFlowTranslator()
result = translator.translate_text("Hello world", "en", "zh")
print(result.translated_text)  # 你好世界

# 使用百度翻译
baidu = BaiduTranslator()
result = baidu.translate_text("Hello world", "en", "zh")
print(result.translated_text)
```

### 批量翻译

```python
texts = [
    "OpenAI releases new ChatGPT model",
    "AI revolution transforms industries",
    "Tech breakthrough in quantum computing"
]

results = translator.translate_batch(texts, "en", "zh")
for result in results:
    print(f"{result.original_text} -> {result.translated_text}")
```

### 服务状态监控

```python
# 检查服务状态
status = translator.get_service_status()
print(f"服务状态: {status.value}")

# 详细健康检查
health = translator.check_health()
print(f"响应时间: {health['response_time']:.3f}秒")
print(f"功能支持: {health['features']}")
```

### 智能服务切换

```python
from translation import SiliconFlowTranslator, TencentTranslator, BaiduTranslator
from translation.core.interfaces import ServiceStatus

def get_best_translator():
    """获取最佳可用的翻译服务"""
    services = [
        ("硅基流动", SiliconFlowTranslator),
        ("腾讯翻译", TencentTranslator), 
        ("百度翻译", BaiduTranslator)
    ]
    
    for name, service_class in services:
        try:
            translator = service_class()
            if translator.get_service_status() == ServiceStatus.HEALTHY:
                print(f"使用 {name}")
                return translator
        except:
            continue
    
    raise Exception("没有可用的翻译服务")

# 使用最佳服务
translator = get_best_translator()
result = translator.translate_text("Hello", "en", "zh")
```

## 🎯 硅基流动优势

### 成本对比 (每百万字符)
- 硅基流动: ¥2-10 ⭐⭐⭐⭐⭐
- 百度翻译: ¥49-58
- 腾讯翻译: ¥58  
- Google翻译: ¥140-280

### 质量优势
- ✅ AI大模型理解能力强
- ✅ 上下文语境翻译更准确
- ✅ 专业术语处理更好
- ✅ 支持多种优化模型选择

### 使用建议
```python
# 大量日常翻译 - 成本最优
translator = SiliconFlowTranslator(model="Qwen/Qwen2.5-7B-Instruct")

# 重要内容翻译 - 质量优先  
translator = SiliconFlowTranslator(model="Qwen/Qwen2.5-14B-Instruct")

# 英文新闻专门 - 英文优势
translator = SiliconFlowTranslator(model="meta-llama/Meta-Llama-3.1-8B-Instruct")

# 中英互译 - 中文理解
translator = SiliconFlowTranslator(model="THUDM/glm-4-9b-chat")
```

## 🧪 测试

```bash
# 运行所有测试
python -m pytest translation/tests/ -v

# 运行特定服务测试
python -m pytest translation/tests/test_siliconflow_translator.py -v

# 运行示例
python translation/siliconflow_example.py
```

## 📊 性能对比

| 服务 | 成本 | 质量 | 速度 | 稳定性 | 推荐度 |
|------|------|------|------|--------|--------|
| 硅基流动 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 腾讯翻译 | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| 百度翻译 | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| Google翻译 | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |

## 🔧 扩展开发

### 添加新的翻译服务

```python
from translation.core.interfaces import ITranslationService, TranslationResult

class MyTranslator(ITranslationService):
    def translate_text(self, text: str, source_lang: str = 'en', target_lang: str = 'zh') -> TranslationResult:
        # 实现翻译逻辑
        pass
    
    def translate_batch(self, texts: List[str], source_lang: str = 'en', target_lang: str = 'zh') -> List[TranslationResult]:
        # 实现批量翻译
        pass
    
    def get_service_status(self) -> ServiceStatus:
        # 实现状态检查
        pass
    
    def get_service_name(self) -> str:
        return "my_translator"
```

## 📝 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📞 支持

如有问题，请创建 Issue 或联系维护者。
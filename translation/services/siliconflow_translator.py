#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
硅基流动AI翻译适配器
"""

import os
import json
import time
import urllib.request
import urllib.parse
from typing import List, Optional, Dict
from datetime import datetime

from ..core.interfaces import ITranslationService, TranslationResult, ServiceStatus


class SiliconFlowTranslator(ITranslationService):
    """硅基流动AI翻译适配器"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "Qwen/Qwen2.5-7B-Instruct"):
        """初始化硅基流动翻译服务
        
        Args:
            api_key: 硅基流动API密钥
            model: 使用的模型名称，推荐模型：
                - Qwen/Qwen2.5-7B-Instruct (性价比高)
                - Qwen/Qwen2.5-14B-Instruct (质量更好)
                - meta-llama/Meta-Llama-3.1-8B-Instruct (英文翻译优秀)
                - THUDM/glm-4-9b-chat (中文理解好)
        """
        self.api_key = api_key or os.getenv('SILICONFLOW_API_KEY')
        self.model = model
        self.base_url = "https://api.siliconflow.cn/v1/chat/completions"
        self.max_retries = 3
        self.retry_delay = 1.0
        
        if not self.api_key:
            raise ValueError("硅基流动API密钥未配置，请设置SILICONFLOW_API_KEY环境变量")
        
        # 语言映射
        self.language_names = {
            'en': '英文',
            'zh': '中文',
            'zh-cn': '简体中文',
            'zh-tw': '繁体中文',
            'ja': '日文',
            'ko': '韩文',
            'fr': '法文',
            'de': '德文',
            'es': '西班牙文',
            'ru': '俄文',
            'it': '意大利文',
            'pt': '葡萄牙文',
            'ar': '阿拉伯文',
            'th': '泰文',
            'vi': '越南文',
            'hi': '印地文',
            'tr': '土耳其文'
        }
    
    def get_service_name(self) -> str:
        """获取服务名称"""
        return f"siliconflow_{self.model.split('/')[-1]}"
    
    def _create_translation_prompt(self, text: str, source_lang: str, target_lang: str) -> str:
        """创建翻译提示词"""
        source_name = self.language_names.get(source_lang.lower(), source_lang)
        target_name = self.language_names.get(target_lang.lower(), target_lang)
        
        # 针对新闻翻译优化的提示词
        prompt = f"""你是一个专业的新闻翻译专家。请将以下{source_name}文本翻译成{target_name}，要求：

1. 保持新闻的准确性和客观性
2. 使用自然流畅的{target_name}表达
3. 保留专业术语和人名、地名的准确性
4. 适合新闻媒体的语言风格
5. 只返回翻译结果，不要添加任何解释

原文：{text}

翻译："""
        
        return prompt
    
    def _make_request(self, messages: List[Dict]) -> dict:
        """发起硅基流动API请求"""
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.3,  # 较低温度确保翻译一致性
            "max_tokens": 2048,
            "top_p": 0.9,
            "stream": False
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        for attempt in range(self.max_retries):
            try:
                data = json.dumps(payload).encode('utf-8')
                request = urllib.request.Request(
                    self.base_url,
                    data=data,
                    headers=headers
                )
                
                with urllib.request.urlopen(request, timeout=30) as response:
                    result = json.loads(response.read().decode('utf-8'))
                    
                if 'error' in result:
                    error = result['error']
                    error_msg = f"{error.get('type', 'Unknown')}: {error.get('message', 'Unknown error')}"
                    
                    if attempt < self.max_retries - 1:
                        print(f"硅基流动API错误 (尝试 {attempt + 1}/{self.max_retries}): {error_msg}")
                        time.sleep(self.retry_delay * (attempt + 1))
                        continue
                    else:
                        raise Exception(f"硅基流动API错误: {error_msg}")
                
                return result
                
            except Exception as e:
                if attempt < self.max_retries - 1:
                    print(f"硅基流动请求失败 (尝试 {attempt + 1}/{self.max_retries}): {str(e)}")
                    time.sleep(self.retry_delay * (attempt + 1))
                    continue
                else:
                    raise e
    
    def _calculate_confidence(self, original: str, translated: str, usage_info: dict = None) -> float:
        """计算翻译置信度"""
        base_confidence = 0.85  # AI模型基础置信度较高
        
        # 基于文本长度调整
        if len(original) < 10:
            base_confidence -= 0.1
        elif len(original) > 200:
            base_confidence += 0.05
        
        # 基于翻译质量简单评估
        if translated and len(translated) > 0:
            length_ratio = len(translated) / len(original)
            if 0.3 <= length_ratio <= 3.0:  # 合理的长度比例
                base_confidence += 0.05
            else:
                base_confidence -= 0.1
        
        # 基于模型使用情况调整（如果有的话）
        if usage_info:
            # 如果token使用合理，说明翻译质量可能更好
            if usage_info.get('completion_tokens', 0) > 0:
                base_confidence += 0.02
        
        return min(max(base_confidence, 0.0), 1.0)
    
    def translate_text(self, text: str, source_lang: str = 'en', target_lang: str = 'zh') -> TranslationResult:
        """翻译单个文本"""
        if not text or not text.strip():
            return TranslationResult(
                original_text=text,
                translated_text="",
                source_language=source_lang,
                target_language=target_lang,
                service_name=self.get_service_name(),
                confidence_score=0.0,
                timestamp=datetime.now(),
                error_message="输入文本为空"
            )
        
        try:
            prompt = self._create_translation_prompt(text, source_lang, target_lang)
            messages = [
                {"role": "user", "content": prompt}
            ]
            
            result = self._make_request(messages)
            
            if 'choices' in result and result['choices']:
                translated_text = result['choices'][0]['message']['content'].strip()
                
                # 清理可能的格式问题
                if translated_text.startswith('翻译：'):
                    translated_text = translated_text[3:].strip()
                
                # 计算置信度
                usage_info = result.get('usage', {})
                confidence_score = self._calculate_confidence(text, translated_text, usage_info)
                
                return TranslationResult(
                    original_text=text,
                    translated_text=translated_text,
                    source_language=source_lang,
                    target_language=target_lang,
                    service_name=self.get_service_name(),
                    confidence_score=confidence_score,
                    timestamp=datetime.now()
                )
            else:
                raise Exception("翻译结果为空")
                
        except Exception as e:
            return TranslationResult(
                original_text=text,
                translated_text="",
                source_language=source_lang,
                target_language=target_lang,
                service_name=self.get_service_name(),
                confidence_score=0.0,
                timestamp=datetime.now(),
                error_message=str(e)
            )
    
    def translate_batch(self, texts: List[str], source_lang: str = 'en', target_lang: str = 'zh') -> List[TranslationResult]:
        """批量翻译文本"""
        if not texts:
            return []
        
        # 对于较少的文本，可以尝试一次性翻译
        if len(texts) <= 5:
            try:
                return self._batch_translate_combined(texts, source_lang, target_lang)
            except Exception as e:
                print(f"批量翻译失败，回退到单个翻译: {str(e)}")
        
        # 回退到单个翻译
        results = []
        for text in texts:
            result = self.translate_text(text, source_lang, target_lang)
            results.append(result)
            # 添加小延迟避免频率限制
            time.sleep(0.1)
        
        return results
    
    def _batch_translate_combined(self, texts: List[str], source_lang: str, target_lang: str) -> List[TranslationResult]:
        """组合批量翻译"""
        source_name = self.language_names.get(source_lang.lower(), source_lang)
        target_name = self.language_names.get(target_lang.lower(), target_lang)
        
        # 构建批量翻译提示
        numbered_texts = []
        for i, text in enumerate(texts, 1):
            numbered_texts.append(f"{i}. {text}")
        
        combined_text = "\n".join(numbered_texts)
        
        prompt = f"""你是一个专业的新闻翻译专家。请将以下编号的{source_name}文本逐条翻译成{target_name}，要求：

1. 保持新闻的准确性和客观性
2. 使用自然流畅的{target_name}表达
3. 保留编号格式
4. 每条翻译独立成行
5. 只返回翻译结果，不要添加解释

原文：
{combined_text}

翻译："""
        
        messages = [{"role": "user", "content": prompt}]
        result = self._make_request(messages)
        
        if 'choices' in result and result['choices']:
            translated_content = result['choices'][0]['message']['content'].strip()
            
            # 解析批量翻译结果
            translated_lines = translated_content.split('\n')
            results = []
            
            for i, original_text in enumerate(texts):
                # 寻找对应编号的翻译
                translated_text = ""
                for line in translated_lines:
                    if line.strip().startswith(f"{i+1}."):
                        translated_text = line.strip()[len(f"{i+1}."):].strip()
                        break
                
                if not translated_text:
                    # 如果没找到对应翻译，回退到单个翻译
                    single_result = self.translate_text(original_text, source_lang, target_lang)
                    results.append(single_result)
                else:
                    confidence_score = self._calculate_confidence(original_text, translated_text)
                    results.append(TranslationResult(
                        original_text=original_text,
                        translated_text=translated_text,
                        source_language=source_lang,
                        target_language=target_lang,
                        service_name=self.get_service_name(),
                        confidence_score=confidence_score,
                        timestamp=datetime.now()
                    ))
            
            return results
        else:
            raise Exception("批量翻译结果为空")
    
    def get_service_status(self) -> ServiceStatus:
        """获取服务状态"""
        try:
            # 使用简单文本测试服务状态
            test_result = self.translate_text("hello", "en", "zh")
            
            if test_result.error_message:
                error_msg = test_result.error_message.lower()
                if any(keyword in error_msg for keyword in ['rate', 'limit', 'quota', 'throttle']):
                    return ServiceStatus.DEGRADED
                elif any(keyword in error_msg for keyword in ['unauthorized', 'forbidden', 'invalid']):
                    return ServiceStatus.UNAVAILABLE
                else:
                    return ServiceStatus.DEGRADED
            else:
                return ServiceStatus.HEALTHY
                
        except Exception:
            return ServiceStatus.UNAVAILABLE
    
    def get_model_info(self) -> dict:
        """获取当前使用的模型信息"""
        return {
            "model": self.model,
            "service": "siliconflow",
            "capabilities": ["translation", "batch_translation", "multilingual"],
            "languages": list(self.language_names.keys())
        }
    
    def check_health(self) -> dict:
        """检查服务健康状态"""
        try:
            start_time = time.time()
            test_result = self.translate_text("test", "en", "zh")
            response_time = time.time() - start_time
            
            return {
                "service": self.get_service_name(),
                "model": self.model,
                "status": self.get_service_status().value,
                "response_time": response_time,
                "last_check": datetime.now().isoformat(),
                "error": test_result.error_message,
                "features": {
                    "translation": test_result.error_message is None,
                    "batch_translation": True,
                    "multilingual": True,
                    "ai_powered": True
                }
            }
        except Exception as e:
            return {
                "service": self.get_service_name(),
                "model": self.model,
                "status": ServiceStatus.UNAVAILABLE.value,
                "response_time": None,
                "last_check": datetime.now().isoformat(),
                "error": str(e),
                "features": {
                    "translation": False,
                    "batch_translation": False,
                    "multilingual": False,
                    "ai_powered": True
                }
            }
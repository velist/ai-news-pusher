#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google翻译API适配器
"""

import os
import json
import time
import urllib.request
import urllib.parse
from typing import List, Optional
from datetime import datetime

from ..core.interfaces import ITranslationService, TranslationResult, ServiceStatus


class GoogleTranslator(ITranslationService):
    """Google翻译API适配器"""
    
    def __init__(self, api_key: Optional[str] = None, project_id: Optional[str] = None):
        """初始化Google翻译服务
        
        Args:
            api_key: Google Cloud Translation API密钥
            project_id: Google Cloud项目ID
        """
        self.api_key = api_key or os.getenv('GOOGLE_TRANSLATE_API_KEY')
        self.project_id = project_id or os.getenv('GOOGLE_CLOUD_PROJECT_ID')
        self.base_url = "https://translation.googleapis.com/language/translate/v2"
        self.detect_url = "https://translation.googleapis.com/language/translate/v2/detect"
        self.max_retries = 3
        self.retry_delay = 1.0
        
        if not self.api_key:
            raise ValueError("Google翻译API密钥未配置，请设置GOOGLE_TRANSLATE_API_KEY环境变量")
    
    def get_service_name(self) -> str:
        """获取服务名称"""
        return "google_translate"
    
    def _make_request(self, url: str, params: dict) -> dict:
        """发起Google翻译API请求"""
        params['key'] = self.api_key
        
        for attempt in range(self.max_retries):
            try:
                # 构建请求
                data = urllib.parse.urlencode(params).encode('utf-8')
                request = urllib.request.Request(
                    url,
                    data=data,
                    headers={'Content-Type': 'application/x-www-form-urlencoded'}
                )
                
                with urllib.request.urlopen(request, timeout=10) as response:
                    result = json.loads(response.read().decode('utf-8'))
                    
                if 'error' in result:
                    error = result['error']
                    error_msg = f"{error.get('code', 'Unknown')}: {error.get('message', 'Unknown error')}"
                    
                    if attempt < self.max_retries - 1:
                        print(f"Google翻译API错误 (尝试 {attempt + 1}/{self.max_retries}): {error_msg}")
                        time.sleep(self.retry_delay * (attempt + 1))
                        continue
                    else:
                        raise Exception(f"Google翻译API错误: {error_msg}")
                
                return result
                
            except Exception as e:
                if attempt < self.max_retries - 1:
                    print(f"Google翻译请求失败 (尝试 {attempt + 1}/{self.max_retries}): {str(e)}")
                    time.sleep(self.retry_delay * (attempt + 1))
                    continue
                else:
                    raise e
    
    def detect_language(self, text: str) -> Optional[str]:
        """检测文本语言"""
        try:
            params = {'q': text}
            result = self._make_request(self.detect_url, params)
            
            if 'data' in result and 'detections' in result['data']:
                detections = result['data']['detections'][0]
                if detections:
                    return detections[0]['language']
            return None
        except Exception:
            return None
    
    def _calculate_confidence(self, original: str, translated: str, detected_lang: str = None) -> float:
        """计算翻译置信度"""
        base_confidence = 0.8
        
        # 基于文本长度调整置信度
        if len(original) < 10:
            base_confidence -= 0.1
        elif len(original) > 100:
            base_confidence += 0.1
        
        # 基于语言检测结果调整置信度
        if detected_lang:
            base_confidence += 0.1
        
        # 基于翻译结果质量简单评估
        if translated and len(translated) > 0:
            if len(translated) / len(original) > 0.3:  # 翻译长度合理
                base_confidence += 0.05
        
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
            # Google翻译语言代码映射
            lang_map = {
                'zh': 'zh-cn',
                'zh-cn': 'zh-cn',
                'zh-tw': 'zh-tw',
                'en': 'en',
                'ja': 'ja',
                'ko': 'ko',
                'fr': 'fr',
                'de': 'de',
                'es': 'es',
                'ru': 'ru',
                'it': 'it',
                'pt': 'pt',
                'ar': 'ar',
                'th': 'th',
                'vi': 'vi',
                'hi': 'hi',
                'tr': 'tr',
                'pl': 'pl',
                'nl': 'nl',
                'sv': 'sv',
                'da': 'da',
                'no': 'no',
                'fi': 'fi'
            }
            
            source = lang_map.get(source_lang.lower(), source_lang)
            target = lang_map.get(target_lang.lower(), target_lang)
            
            # 检测源语言（可选）
            detected_lang = None
            if source_lang == 'auto' or source_lang == '':
                detected_lang = self.detect_language(text)
                if detected_lang:
                    source = detected_lang
            
            params = {
                'q': text,
                'source': source,
                'target': target,
                'format': 'text'
            }
            
            result = self._make_request(self.base_url, params)
            
            if 'data' in result and 'translations' in result['data']:
                translations = result['data']['translations']
                if translations:
                    translated_text = translations[0]['translatedText']
                    
                    # 计算置信度
                    confidence_score = self._calculate_confidence(
                        text, translated_text, detected_lang
                    )
                    
                    return TranslationResult(
                        original_text=text,
                        translated_text=translated_text,
                        source_language=source_lang,
                        target_language=target_lang,
                        service_name=self.get_service_name(),
                        confidence_score=confidence_score,
                        timestamp=datetime.now()
                    )
            
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
        
        try:
            # Google翻译支持批量翻译
            lang_map = {
                'zh': 'zh-cn',
                'zh-cn': 'zh-cn',
                'zh-tw': 'zh-tw',
                'en': 'en',
                'ja': 'ja',
                'ko': 'ko',
                'fr': 'fr',
                'de': 'de',
                'es': 'es',
                'ru': 'ru'
            }
            
            source = lang_map.get(source_lang.lower(), source_lang)
            target = lang_map.get(target_lang.lower(), target_lang)
            
            # 构建批量请求参数
            params = {
                'source': source,
                'target': target,
                'format': 'text'
            }
            
            # 添加多个q参数
            for text in texts:
                if 'q' not in params:
                    params['q'] = []
                if isinstance(params['q'], str):
                    params['q'] = [params['q']]
                params['q'].append(text)
            
            # 特殊处理多个q参数的URL编码
            query_parts = []
            query_parts.append(f"source={urllib.parse.quote(source)}")
            query_parts.append(f"target={urllib.parse.quote(target)}")
            query_parts.append("format=text")
            query_parts.append(f"key={urllib.parse.quote(self.api_key)}")
            
            for text in texts:
                query_parts.append(f"q={urllib.parse.quote(text)}")
            
            query_string = "&".join(query_parts)
            url = f"{self.base_url}?{query_string}"
            
            request = urllib.request.Request(url, method='GET')
            
            with urllib.request.urlopen(request, timeout=15) as response:
                result = json.loads(response.read().decode('utf-8'))
            
            if 'data' in result and 'translations' in result['data']:
                translations = result['data']['translations']
                results = []
                
                for i, (original, translation) in enumerate(zip(texts, translations)):
                    translated_text = translation['translatedText']
                    confidence_score = self._calculate_confidence(original, translated_text)
                    
                    results.append(TranslationResult(
                        original_text=original,
                        translated_text=translated_text,
                        source_language=source_lang,
                        target_language=target_lang,
                        service_name=self.get_service_name(),
                        confidence_score=confidence_score,
                        timestamp=datetime.now()
                    ))
                
                return results
            else:
                # 如果批量翻译失败，回退到单个翻译
                return [self.translate_text(text, source_lang, target_lang) for text in texts]
                
        except Exception as e:
            # 批量翻译失败时，回退到单个翻译
            print(f"Google批量翻译失败，回退到单个翻译: {str(e)}")
            return [self.translate_text(text, source_lang, target_lang) for text in texts]
    
    def get_service_status(self) -> ServiceStatus:
        """获取服务状态"""
        try:
            # 使用简单文本测试服务状态
            test_result = self.translate_text("hello", "en", "zh")
            
            if test_result.error_message:
                error_msg = test_result.error_message.lower()
                if any(keyword in error_msg for keyword in ['quota', 'limit', 'rate', 'exceeded']):
                    return ServiceStatus.DEGRADED
                elif any(keyword in error_msg for keyword in ['forbidden', 'unauthorized', 'invalid']):
                    return ServiceStatus.UNAVAILABLE
                else:
                    return ServiceStatus.DEGRADED
            else:
                return ServiceStatus.HEALTHY
                
        except Exception:
            return ServiceStatus.UNAVAILABLE
    
    def get_supported_languages(self) -> List[dict]:
        """获取支持的语言列表"""
        try:
            url = "https://translation.googleapis.com/language/translate/v2/languages"
            params = {'target': 'en'}  # 获取英文语言名称
            
            result = self._make_request(url, params)
            
            if 'data' in result and 'languages' in result['data']:
                return result['data']['languages']
            else:
                return []
                
        except Exception as e:
            print(f"获取支持语言列表失败: {str(e)}")
            return []
    
    def check_health(self) -> dict:
        """检查服务健康状态（扩展功能）"""
        try:
            start_time = time.time()
            test_result = self.translate_text("test", "en", "zh")
            response_time = time.time() - start_time
            
            # 额外检查语言检测功能
            detect_test = self.detect_language("Hello world")
            
            return {
                "service": self.get_service_name(),
                "status": self.get_service_status().value,
                "response_time": response_time,
                "last_check": datetime.now().isoformat(),
                "error": test_result.error_message,
                "features": {
                    "translation": test_result.error_message is None,
                    "language_detection": detect_test is not None,
                    "batch_translation": True
                }
            }
        except Exception as e:
            return {
                "service": self.get_service_name(),
                "status": ServiceStatus.UNAVAILABLE.value,
                "response_time": None,
                "last_check": datetime.now().isoformat(),
                "error": str(e),
                "features": {
                    "translation": False,
                    "language_detection": False,
                    "batch_translation": False
                }
            }
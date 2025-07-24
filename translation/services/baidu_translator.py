#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
百度翻译API适配器
"""

import os
import json
import time
import hashlib
import random
import urllib.request
import urllib.parse
from typing import List, Optional
from datetime import datetime

from ..core.interfaces import ITranslationService, TranslationResult, ServiceStatus


class BaiduTranslator(ITranslationService):
    """百度翻译API适配器"""
    
    def __init__(self, app_id: Optional[str] = None, secret_key: Optional[str] = None):
        """初始化百度翻译服务
        
        Args:
            app_id: 百度翻译API的APP ID
            secret_key: 百度翻译API的密钥
        """
        self.app_id = app_id or os.getenv('BAIDU_TRANSLATE_APP_ID')
        self.secret_key = secret_key or os.getenv('BAIDU_TRANSLATE_SECRET_KEY')
        self.base_url = "https://fanyi-api.baidu.com/api/trans/vip/translate"
        self.max_retries = 3
        self.retry_delay = 1.0
        
        if not self.app_id or not self.secret_key:
            raise ValueError("百度翻译API凭证未配置，请设置BAIDU_TRANSLATE_APP_ID和BAIDU_TRANSLATE_SECRET_KEY环境变量")
    
    def get_service_name(self) -> str:
        """获取服务名称"""
        return "baidu_translate"
    
    def _generate_sign(self, query: str, salt: str) -> str:
        """生成百度翻译API签名"""
        sign_str = f"{self.app_id}{query}{salt}{self.secret_key}"
        return hashlib.md5(sign_str.encode('utf-8')).hexdigest()
    
    def _make_request(self, query: str, from_lang: str = 'en', to_lang: str = 'zh') -> dict:
        """发起翻译API请求"""
        salt = str(random.randint(32768, 65536))
        sign = self._generate_sign(query, salt)
        
        params = {
            'q': query,
            'from': from_lang,
            'to': to_lang,
            'appid': self.app_id,
            'salt': salt,
            'sign': sign
        }
        
        data = urllib.parse.urlencode(params).encode('utf-8')
        
        for attempt in range(self.max_retries):
            try:
                request = urllib.request.Request(
                    self.base_url,
                    data=data,
                    headers={'Content-Type': 'application/x-www-form-urlencoded'}
                )
                
                with urllib.request.urlopen(request, timeout=10) as response:
                    result = json.loads(response.read().decode('utf-8'))
                    
                if 'error_code' in result:
                    error_msg = self._get_error_message(result['error_code'])
                    if attempt < self.max_retries - 1:
                        print(f"百度翻译API错误 (尝试 {attempt + 1}/{self.max_retries}): {error_msg}")
                        time.sleep(self.retry_delay * (attempt + 1))
                        continue
                    else:
                        raise Exception(f"百度翻译API错误: {error_msg}")
                
                return result
                
            except Exception as e:
                if attempt < self.max_retries - 1:
                    print(f"百度翻译请求失败 (尝试 {attempt + 1}/{self.max_retries}): {str(e)}")
                    time.sleep(self.retry_delay * (attempt + 1))
                    continue
                else:
                    raise e
    
    def _get_error_message(self, error_code: str) -> str:
        """获取错误码对应的错误信息"""
        error_messages = {
            '52001': 'APP ID无效',
            '52002': '签名错误',
            '52003': '访问频率受限',
            '54000': '必填参数为空',
            '54001': '签名错误',
            '54003': '访问频率受限',
            '54004': '账户余额不足',
            '54005': '长query请求频繁',
            '58000': '客户端IP非法',
            '58001': '译文语言方向不支持',
            '58002': '服务当前已关闭',
            '90107': '认证未通过或未生效'
        }
        return error_messages.get(error_code, f'未知错误: {error_code}')
    
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
            # 百度翻译语言代码映射
            lang_map = {
                'en': 'en',
                'zh': 'zh',
                'zh-cn': 'zh',
                'zh-tw': 'cht',
                'ja': 'jp',
                'ko': 'kor',
                'fr': 'fra',
                'de': 'de',
                'es': 'spa',
                'ru': 'ru'
            }
            
            from_lang = lang_map.get(source_lang.lower(), source_lang)
            to_lang = lang_map.get(target_lang.lower(), target_lang)
            
            result = self._make_request(text, from_lang, to_lang)
            
            if 'trans_result' in result and result['trans_result']:
                translated_text = result['trans_result'][0]['dst']
                confidence_score = 0.9  # 百度翻译不提供置信度，使用默认值
                
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
        results = []
        
        for text in texts:
            # 百度翻译API不支持真正的批量翻译，需要逐个调用
            result = self.translate_text(text, source_lang, target_lang)
            results.append(result)
            
            # 添加延迟避免频率限制
            if len(texts) > 1:
                time.sleep(0.1)
        
        return results
    
    def get_service_status(self) -> ServiceStatus:
        """获取服务状态"""
        try:
            # 使用简单文本测试服务状态
            test_result = self.translate_text("hello", "en", "zh")
            
            if test_result.error_message:
                if "频率" in test_result.error_message or "余额" in test_result.error_message:
                    return ServiceStatus.DEGRADED
                else:
                    return ServiceStatus.UNAVAILABLE
            else:
                return ServiceStatus.HEALTHY
                
        except Exception:
            return ServiceStatus.UNAVAILABLE
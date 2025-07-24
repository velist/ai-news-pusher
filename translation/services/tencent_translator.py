#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
腾讯翻译API适配器
"""

import os
import json
import time
import hashlib
import hmac
import urllib.request
import urllib.parse
from typing import List, Optional
from datetime import datetime

from ..core.interfaces import ITranslationService, TranslationResult, ServiceStatus


class TencentTranslator(ITranslationService):
    """腾讯翻译API适配器"""
    
    def __init__(self, secret_id: Optional[str] = None, secret_key: Optional[str] = None, region: str = "ap-beijing"):
        """初始化腾讯翻译服务
        
        Args:
            secret_id: 腾讯云API的Secret ID
            secret_key: 腾讯云API的Secret Key
            region: 服务地域
        """
        self.secret_id = secret_id or os.getenv('TENCENT_SECRET_ID')
        self.secret_key = secret_key or os.getenv('TENCENT_SECRET_KEY')
        self.region = region
        self.service = "tmt"
        self.host = "tmt.tencentcloudapi.com"
        self.endpoint = f"https://{self.host}"
        self.version = "2018-03-21"
        self.max_retries = 3
        self.retry_delay = 1.0
        
        if not self.secret_id or not self.secret_key:
            raise ValueError("腾讯翻译API凭证未配置，请设置TENCENT_SECRET_ID和TENCENT_SECRET_KEY环境变量")
    
    def get_service_name(self) -> str:
        """获取服务名称"""
        return "tencent_translate"
    
    def _sign(self, key: bytes, msg: str) -> bytes:
        """生成签名"""
        return hmac.new(key, msg.encode('utf-8'), hashlib.sha256).digest()
    
    def _get_signature_key(self, key: str, date_stamp: str, region_name: str, service_name: str) -> bytes:
        """获取签名密钥"""
        k_date = self._sign(('TC3' + key).encode('utf-8'), date_stamp)
        k_region = self._sign(k_date, region_name)
        k_service = self._sign(k_region, service_name)
        k_signing = self._sign(k_service, 'tc3_request')
        return k_signing
    
    def _make_request(self, action: str, payload: dict) -> dict:
        """发起腾讯云API请求"""
        timestamp = int(time.time())
        date = datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d')
        
        # 构建请求
        payload_json = json.dumps(payload, separators=(',', ':'))
        
        # 构建规范请求
        http_request_method = "POST"
        canonical_uri = "/"
        canonical_querystring = ""
        canonical_headers = f"content-type:application/json; charset=utf-8\nhost:{self.host}\n"
        signed_headers = "content-type;host"
        hashed_request_payload = hashlib.sha256(payload_json.encode('utf-8')).hexdigest()
        canonical_request = f"{http_request_method}\n{canonical_uri}\n{canonical_querystring}\n{canonical_headers}\n{signed_headers}\n{hashed_request_payload}"
        
        # 构建待签名字符串
        algorithm = "TC3-HMAC-SHA256"
        credential_scope = f"{date}/{self.region}/{self.service}/tc3_request"
        hashed_canonical_request = hashlib.sha256(canonical_request.encode('utf-8')).hexdigest()
        string_to_sign = f"{algorithm}\n{timestamp}\n{credential_scope}\n{hashed_canonical_request}"
        
        # 计算签名
        signing_key = self._get_signature_key(self.secret_key, date, self.region, self.service)
        signature = hmac.new(signing_key, string_to_sign.encode('utf-8'), hashlib.sha256).hexdigest()
        
        # 构建Authorization
        authorization = f"{algorithm} Credential={self.secret_id}/{credential_scope}, SignedHeaders={signed_headers}, Signature={signature}"
        
        # 构建请求头
        headers = {
            'Authorization': authorization,
            'Content-Type': 'application/json; charset=utf-8',
            'Host': self.host,
            'X-TC-Action': action,
            'X-TC-Timestamp': str(timestamp),
            'X-TC-Version': self.version,
            'X-TC-Region': self.region
        }
        
        for attempt in range(self.max_retries):
            try:
                request = urllib.request.Request(
                    self.endpoint,
                    data=payload_json.encode('utf-8'),
                    headers=headers
                )
                
                with urllib.request.urlopen(request, timeout=10) as response:
                    result = json.loads(response.read().decode('utf-8'))
                    
                if 'Error' in result.get('Response', {}):
                    error = result['Response']['Error']
                    error_msg = f"{error['Code']}: {error['Message']}"
                    
                    if attempt < self.max_retries - 1:
                        print(f"腾讯翻译API错误 (尝试 {attempt + 1}/{self.max_retries}): {error_msg}")
                        time.sleep(self.retry_delay * (attempt + 1))
                        continue
                    else:
                        raise Exception(f"腾讯翻译API错误: {error_msg}")
                
                return result
                
            except Exception as e:
                if attempt < self.max_retries - 1:
                    print(f"腾讯翻译请求失败 (尝试 {attempt + 1}/{self.max_retries}): {str(e)}")
                    time.sleep(self.retry_delay * (attempt + 1))
                    continue
                else:
                    raise e
    
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
            # 腾讯翻译语言代码映射
            lang_map = {
                'en': 'en',
                'zh': 'zh',
                'zh-cn': 'zh',
                'zh-tw': 'zh-TW',
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
                'vi': 'vi'
            }
            
            source = lang_map.get(source_lang.lower(), source_lang)
            target = lang_map.get(target_lang.lower(), target_lang)
            
            payload = {
                "SourceText": text,
                "Source": source,
                "Target": target,
                "ProjectId": 0
            }
            
            result = self._make_request("TextTranslate", payload)
            
            if 'Response' in result and 'TargetText' in result['Response']:
                translated_text = result['Response']['TargetText']
                confidence_score = 0.85  # 腾讯翻译不提供置信度，使用默认值
                
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
        
        try:
            # 腾讯翻译支持批量翻译
            lang_map = {
                'en': 'en',
                'zh': 'zh',
                'zh-cn': 'zh',
                'zh-tw': 'zh-TW',
                'ja': 'ja',
                'ko': 'ko',
                'fr': 'fr',
                'de': 'de',
                'es': 'es',
                'ru': 'ru'
            }
            
            source = lang_map.get(source_lang.lower(), source_lang)
            target = lang_map.get(target_lang.lower(), target_lang)
            
            payload = {
                "SourceTextList": texts,
                "Source": source,
                "Target": target,
                "ProjectId": 0
            }
            
            result = self._make_request("TextTranslateBatch", payload)
            
            if 'Response' in result and 'TargetTextList' in result['Response']:
                translated_texts = result['Response']['TargetTextList']
                results = []
                
                for i, (original, translated) in enumerate(zip(texts, translated_texts)):
                    results.append(TranslationResult(
                        original_text=original,
                        translated_text=translated,
                        source_language=source_lang,
                        target_language=target_lang,
                        service_name=self.get_service_name(),
                        confidence_score=0.85,
                        timestamp=datetime.now()
                    ))
                
                return results
            else:
                # 如果批量翻译失败，回退到单个翻译
                return [self.translate_text(text, source_lang, target_lang) for text in texts]
                
        except Exception as e:
            # 批量翻译失败时，回退到单个翻译
            print(f"批量翻译失败，回退到单个翻译: {str(e)}")
            return [self.translate_text(text, source_lang, target_lang) for text in texts]
    
    def get_service_status(self) -> ServiceStatus:
        """获取服务状态"""
        try:
            # 使用简单文本测试服务状态
            test_result = self.translate_text("hello", "en", "zh")
            
            if test_result.error_message:
                if any(keyword in test_result.error_message.lower() 
                       for keyword in ['limit', 'quota', 'throttle', 'rate']):
                    return ServiceStatus.DEGRADED
                else:
                    return ServiceStatus.UNAVAILABLE
            else:
                return ServiceStatus.HEALTHY
                
        except Exception:
            return ServiceStatus.UNAVAILABLE
    
    def check_health(self) -> dict:
        """检查服务健康状态（扩展功能）"""
        try:
            start_time = time.time()
            test_result = self.translate_text("test", "en", "zh")
            response_time = time.time() - start_time
            
            return {
                "service": self.get_service_name(),
                "status": self.get_service_status().value,
                "response_time": response_time,
                "last_check": datetime.now().isoformat(),
                "error": test_result.error_message
            }
        except Exception as e:
            return {
                "service": self.get_service_name(),
                "status": ServiceStatus.UNAVAILABLE.value,
                "response_time": None,
                "last_check": datetime.now().isoformat(),
                "error": str(e)
            }
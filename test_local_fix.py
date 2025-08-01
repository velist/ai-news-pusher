#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
本地测试脚本 - 验证修复效果
"""

import os
import sys

def test_api_key():
    """测试API密钥配置"""
    print("🔑 测试API密钥配置...")
    
    # 检查环境变量
    api_key = os.getenv('GNEWS_API_KEY')
    if not api_key:
        print("❌ GNEWS_API_KEY 环境变量未设置")
        print("💡 请设置: export GNEWS_API_KEY=你的密钥")
        return False
    
    print(f"✅ API密钥已设置: {api_key[:8]}...{api_key[-4:]}")
    
    # 验证格式
    if len(api_key) != 32:
        print(f"❌ API密钥长度错误: {len(api_key)} (应为32位)")
        return False
    
    if not all(c in '0123456789abcdef' for c in api_key.lower()):
        print("❌ API密钥格式错误: 应为32位十六进制字符")
        return False
    
    print("✅ API密钥格式正确")
    return True

def test_network():
    """测试网络连接"""
    print("\n🌐 测试网络连接...")
    
    try:
        import urllib.request
        import json
        
        # 测试基础连接
        req = urllib.request.Request("https://httpbin.org/ip")
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode())
            print(f"✅ 网络连接正常，IP: {data.get('origin', 'unknown')}")
            return True
    except Exception as e:
        print(f"❌ 网络连接失败: {e}")
        return False

def test_gnews_api():
    """测试GNews API"""
    print("\n📡 测试GNews API...")
    
    api_key = os.getenv('GNEWS_API_KEY')
    if not api_key:
        print("❌ 无API密钥，跳过测试")
        return False
    
    try:
        import urllib.request
        import urllib.parse
        import json
        
        # 简单测试请求
        params = {
            "q": "test",
            "max": 1,
            "apikey": api_key
        }
        
        query_string = urllib.parse.urlencode(params)
        url = f"https://gnews.io/api/v4/search?{query_string}"
        
        print(f"📡 测试URL: https://gnews.io/api/v4/search?q=test&max=1&apikey={api_key[:8]}...")
        
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (compatible; NewsBot/1.0)')
        
        with urllib.request.urlopen(req, timeout=10) as response:
            status = response.getcode()
            print(f"📊 HTTP状态: {status}")
            
            if status == 200:
                data = json.loads(response.read().decode())
                articles = data.get('articles', [])
                print(f"✅ API响应成功，返回 {len(articles)} 条新闻")
                print(f"📊 总文章数: {data.get('totalArticles', 0)}")
                return True
            else:
                print(f"❌ HTTP状态异常: {status}")
                return False
                
    except urllib.error.HTTPError as e:
        print(f"❌ HTTP错误: {e.code} - {e.reason}")
        if e.code == 401:
            print("   💡 API密钥可能无效")
        elif e.code == 403:
            print("   💡 可能是配额不足或访问被限制")
        elif e.code == 429:
            print("   💡 请求过于频繁")
        return False
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return False

def run_test():
    """运行完整测试"""
    print("🧪 开始本地环境测试...")
    print("=" * 50)
    
    # 测试API密钥
    api_ok = test_api_key()
    
    # 测试网络
    network_ok = test_network()
    
    # 测试API
    api_test_ok = False
    if api_ok and network_ok:
        api_test_ok = test_gnews_api()
    
    # 汇总结果
    print("\n" + "=" * 50)
    print("📊 测试结果汇总")
    print("=" * 50)
    print(f"🔑 API密钥配置: {'✅ 正常' if api_ok else '❌ 异常'}")
    print(f"🌐 网络连接: {'✅ 正常' if network_ok else '❌ 异常'}")
    print(f"📡 GNews API: {'✅ 正常' if api_test_ok else '❌ 异常'}")
    
    if api_ok and network_ok and api_test_ok:
        print("\n🎉 所有测试通过！修复版脚本应该能正常获取真实新闻")
        print("💡 建议: 直接运行 python github_pages_fix.py 测试完整功能")
    elif api_ok and network_ok:
        print("\n⚠️ API连接有问题，可能原因:")
        print("   - API密钥无效或过期")
        print("   - API配额已用完")
        print("   - GNews服务暂时不可用")
        print("💡 建议: 检查API密钥有效性和配额状态")
    else:
        print("\n❌ 基础环境有问题")
        if not api_ok:
            print("   - 请设置正确的GNEWS_API_KEY环境变量")
        if not network_ok:
            print("   - 请检查网络连接")
    
    return api_ok and network_ok and api_test_ok

if __name__ == "__main__":
    success = run_test()
    sys.exit(0 if success else 1)
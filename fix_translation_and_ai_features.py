#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复翻译功能和AI点评功能的脚本
"""

import os
import json
import urllib.request
import urllib.parse
from datetime import datetime

def load_env_file():
    """手动加载.env文件"""
    env_path = '.env'
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()
        print("✅ 已加载.env文件")
    else:
        print("⚠️ 未找到.env文件")

def test_siliconflow_api():
    """测试硅基流动API是否可用"""
    api_key = os.getenv('SILICONFLOW_API_KEY')
    if not api_key:
        print("❌ 未找到SILICONFLOW_API_KEY")
        return False
    
    print(f"🔑 测试API密钥: {api_key[:10]}...")
    
    try:
        # 测试翻译API
        url = "https://api.siliconflow.cn/v1/chat/completions"
        
        data = {
            "model": "Qwen/Qwen2.5-7B-Instruct",
            "messages": [
                {
                    "role": "user",
                    "content": "请将以下英文翻译成中文：Hello World"
                }
            ],
            "max_tokens": 100,
            "temperature": 0.3
        }
        
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        req = urllib.request.Request(
            url, 
            data=json.dumps(data).encode('utf-8'),
            headers=headers
        )
        
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode('utf-8'))
            
        if 'choices' in result and len(result['choices']) > 0:
            translated_text = result['choices'][0]['message']['content']
            print(f"✅ API测试成功，翻译结果: {translated_text}")
            return True
        else:
            print(f"❌ API响应格式异常: {result}")
            return False
            
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        print(f"❌ HTTP错误 {e.code}: {error_body}")
        return False
    except Exception as e:
        print(f"❌ API测试失败: {e}")
        return False

def run_enhanced_news_script():
    """运行增强版新闻脚本"""
    print("🚀 运行增强版新闻脚本...")
    
    try:
        # 运行enhanced_chinese_news_accumulator.py
        import subprocess
        result = subprocess.run(
            ['python', 'enhanced_chinese_news_accumulator.py'],
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        
        if result.returncode == 0:
            print("✅ 增强版新闻脚本运行成功")
            print("📊 输出:")
            print(result.stdout)
            return True
        else:
            print("❌ 增强版新闻脚本运行失败")
            print("错误信息:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ 运行脚本失败: {e}")
        return False

def check_translation_features():
    """检查翻译功能是否生效"""
    print("🔍 检查翻译功能...")
    
    try:
        # 检查enhanced_chinese_news_data.json
        if os.path.exists('docs/enhanced_chinese_news_data.json'):
            with open('docs/enhanced_chinese_news_data.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            translated_count = 0
            ai_commentary_count = 0
            
            for article in data:
                if article.get('chinese_title') or article.get('translated_title'):
                    translated_count += 1
                if article.get('ai_commentary') or article.get('commentary'):
                    ai_commentary_count += 1
            
            print(f"📊 翻译功能统计:")
            print(f"   - 总文章数: {len(data)}")
            print(f"   - 已翻译文章: {translated_count}")
            print(f"   - 有AI点评文章: {ai_commentary_count}")
            
            if translated_count > 0:
                print("✅ 翻译功能已生效")
            else:
                print("❌ 翻译功能未生效")
                
            if ai_commentary_count > 0:
                print("✅ AI点评功能已生效")
            else:
                print("❌ AI点评功能未生效")
                
            return translated_count > 0 and ai_commentary_count > 0
        else:
            print("❌ 未找到enhanced_chinese_news_data.json文件")
            return False
            
    except Exception as e:
        print(f"❌ 检查功能失败: {e}")
        return False

def create_fix_record():
    """创建修复记录"""
    print("📝 创建修复记录...")
    
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    record_content = f"""# AI新闻推送系统修复记录

## 修复时间
{current_time}

## 已修复问题

### 1. 环境变量加载问题 ✅
- **问题**: ultra_simple_news.py缺少环境变量加载功能
- **解决方案**: 添加load_env_file()函数手动加载.env文件
- **状态**: 已修复

### 2. 新闻卡片点击404错误 ✅
- **问题**: index.html中的data-article-id与news目录下的HTML文件名不匹配
- **解决方案**: 重新生成HTML文件，确保ID一致性
- **状态**: 已修复

### 3. 新闻数据累积机制 ✅
- **问题**: 每次运行都会覆盖之前的新闻数据
- **解决方案**: 实现新闻合并逻辑，保留3天内的新闻
- **状态**: 已修复

### 4. Vercel部署优化 ✅
- **问题**: 部署配置需要优化
- **解决方案**: 确保docs目录结构正确，静态文件部署
- **状态**: 已修复

## 当前修复中的问题

### 5. 翻译功能未生效 🔧
- **问题**: 翻译功能存在但未正常工作
- **原因分析**: 
  - SILICONFLOW_API_KEY配置问题
  - API调用逻辑错误
  - 翻译结果未正确保存
- **修复方案**: 
  - 测试API密钥有效性
  - 检查翻译服务调用
  - 验证翻译结果保存
- **状态**: 修复中

### 6. AI点评功能未生效 🔧
- **问题**: AI点评功能存在但未正常工作
- **原因分析**:
  - AI点评API调用失败
  - 点评结果未正确显示
  - 点评逻辑未集成到主流程
- **修复方案**:
  - 测试AI点评API
  - 检查点评生成逻辑
  - 验证点评结果显示
- **状态**: 修复中

## 技术细节

### 环境变量配置
```
GNEWS_API_KEY=已配置
SILICONFLOW_API_KEY=已配置
其他API密钥=已配置
```

### 文件结构
```
docs/
├── index.html (主页)
├── news/ (新闻详情页目录)
│   ├── ai_0_*.html
│   ├── ai_1_*.html
│   └── ...
├── news_data.json (新闻数据)
└── enhanced_chinese_news_data.json (增强版新闻数据)
```

### 脚本功能对比
- `ultra_simple_news.py`: 基础版本，无翻译和AI点评
- `enhanced_chinese_news_accumulator.py`: 增强版本，包含翻译和AI点评

## 下一步计划

1. 🔧 完成翻译功能修复
2. 🤖 完成AI点评功能修复
3. 🧪 全面功能测试
4. 📊 性能优化
5. 🚀 部署验证

## 修复验证

### 功能测试清单
- [ ] 翻译功能正常工作
- [ ] AI点评功能正常工作
- [ ] 新闻卡片点击正常
- [ ] 新闻数据累积正常
- [ ] 页面显示正常
- [ ] 部署功能正常

---
*本记录由修复脚本自动生成*
"""
    
    try:
        with open('修复记录_翻译和AI点评.md', 'w', encoding='utf-8') as f:
            f.write(record_content)
        print("✅ 修复记录已创建: 修复记录_翻译和AI点评.md")
        return True
    except Exception as e:
        print(f"❌ 创建修复记录失败: {e}")
        return False

def main():
    print("🔧 修复翻译功能和AI点评功能")
    print("=" * 50)
    
    # 1. 加载环境变量
    load_env_file()
    
    # 2. 测试硅基流动API
    print("\n🧪 测试硅基流动API...")
    api_works = test_siliconflow_api()
    
    # 3. 运行增强版新闻脚本
    if api_works:
        print("\n🚀 运行增强版新闻脚本...")
        script_success = run_enhanced_news_script()
        
        if script_success:
            # 4. 检查翻译功能
            print("\n🔍 检查翻译和AI点评功能...")
            features_work = check_translation_features()
            
            if features_work:
                print("\n🎉 翻译和AI点评功能修复成功！")
            else:
                print("\n⚠️ 翻译和AI点评功能仍需进一步调试")
        else:
            print("\n❌ 增强版脚本运行失败")
    else:
        print("\n❌ API测试失败，无法继续修复")
    
    # 5. 创建修复记录
    print("\n📝 创建修复记录...")
    create_fix_record()
    
    print("\n" + "=" * 50)
    print("🎯 修复总结:")
    print(f"1. API测试: {'✅ 成功' if api_works else '❌ 失败'}")
    print("2. 翻译功能: 🔧 修复中")
    print("3. AI点评功能: 🔧 修复中")
    print("4. 修复记录: ✅ 已创建")
    
    if api_works:
        print("\n🚀 建议下一步: 检查enhanced_chinese_news_accumulator.py的输出")
    else:
        print("\n⚠️ 建议下一步: 检查SILICONFLOW_API_KEY配置")

if __name__ == "__main__":
    main()
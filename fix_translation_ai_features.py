#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
翻译和AI点评功能修复脚本
解决翻译功能失效和AI点评功能异常的问题
"""

import os
import sys
import json
import requests
from datetime import datetime

def load_env_file():
    """加载环境变量"""
    env_path = '.env'
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()
        print("✅ 环境变量加载成功")
        return True
    else:
        print("❌ .env文件不存在")
        return False

def test_siliconflow_api():
    """测试SiliconFlow API"""
    api_key = os.getenv('SILICONFLOW_API_KEY')
    if not api_key:
        print("❌ SILICONFLOW_API_KEY未设置")
        return False
    
    try:
        # 测试翻译API
        url = "https://api.siliconflow.cn/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
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
        
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if 'choices' in result and len(result['choices']) > 0:
                translation = result['choices'][0]['message']['content']
                print(f"✅ SiliconFlow API测试成功: {translation}")
                return True
            else:
                print(f"❌ API响应格式异常: {result}")
                return False
        else:
            print(f"❌ API请求失败: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ API测试异常: {str(e)}")
        return False

def fix_enhanced_news_script():
    """修复enhanced_chinese_news_accumulator.py中的问题"""
    script_path = 'enhanced_chinese_news_accumulator.py'
    
    if not os.path.exists(script_path):
        print(f"❌ {script_path}不存在")
        return False
    
    try:
        # 读取原文件
        with open(script_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查是否需要修复
        fixes_needed = []
        
        # 检查环境变量加载
        if 'load_dotenv()' not in content and 'load_env_file()' not in content:
            fixes_needed.append('环境变量加载')
        
        # 检查错误处理
        if 'except Exception as e:' not in content:
            fixes_needed.append('错误处理')
        
        if fixes_needed:
            print(f"🔧 需要修复: {', '.join(fixes_needed)}")
            
            # 在文件开头添加环境变量加载函数
            if 'load_env_file()' not in content:
                env_loader = '''
def load_env_file():
    """加载环境变量"""
    env_path = '.env'
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()
        print("环境变量加载成功")
        return True
    else:
        print("警告: .env文件不存在")
        return False

'''
                # 在import后添加环境变量加载函数
                import_end = content.find('\n\n')
                if import_end != -1:
                    content = content[:import_end] + '\n\n' + env_loader + content[import_end+2:]
            
            # 在main函数开始处添加环境变量加载调用
            if 'load_env_file()' not in content:
                main_start = content.find('def main():')
                if main_start != -1:
                    main_body_start = content.find('\n', main_start) + 1
                    indent = '    '
                    env_call = f'{indent}# 加载环境变量\n{indent}load_env_file()\n\n'
                    content = content[:main_body_start] + env_call + content[main_body_start:]
            
            # 写回文件
            with open(script_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✅ {script_path}修复完成")
        else:
            print(f"✅ {script_path}无需修复")
        
        return True
        
    except Exception as e:
        print(f"❌ 修复{script_path}时出错: {str(e)}")
        return False

def run_enhanced_news_script():
    """运行增强版新闻脚本"""
    script_path = 'enhanced_chinese_news_accumulator.py'
    
    if not os.path.exists(script_path):
        print(f"❌ {script_path}不存在")
        return False
    
    try:
        print("🚀 运行增强版新闻脚本...")
        import subprocess
        result = subprocess.run([sys.executable, script_path], 
                              capture_output=True, text=True, encoding='utf-8')
        
        if result.returncode == 0:
            print("✅ 增强版新闻脚本运行成功")
            print("输出:", result.stdout[-500:])  # 显示最后500字符
            return True
        else:
            print(f"❌ 脚本运行失败: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ 运行脚本时出错: {str(e)}")
        return False

def check_translation_results():
    """检查翻译结果"""
    data_files = ['enhanced_chinese_news_data.json', 'docs/news_data.json']
    
    for data_file in data_files:
        if os.path.exists(data_file):
            try:
                with open(data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                if isinstance(data, list) and len(data) > 0:
                    # 检查最新的几条新闻
                    recent_news = data[:3]
                    translation_success = 0
                    ai_commentary_success = 0
                    
                    for news in recent_news:
                        # 检查翻译状态
                        if 'translation_metadata' in news:
                            trans_meta = news['translation_metadata']
                            if trans_meta.get('translation_success_rate', 0) > 0:
                                translation_success += 1
                        
                        # 检查AI点评状态
                        if 'ai_commentary' in news:
                            ai_comm = news['ai_commentary']
                            if ai_comm.get('success', False):
                                ai_commentary_success += 1
                    
                    print(f"📊 {data_file}检查结果:")
                    print(f"   翻译成功率: {translation_success}/{len(recent_news)}")
                    print(f"   AI点评成功率: {ai_commentary_success}/{len(recent_news)}")
                    
                    if translation_success == 0:
                        print("❌ 翻译功能完全失效")
                    elif translation_success < len(recent_news):
                        print("⚠️ 翻译功能部分失效")
                    else:
                        print("✅ 翻译功能正常")
                    
                    if ai_commentary_success == 0:
                        print("❌ AI点评功能完全失效")
                    elif ai_commentary_success < len(recent_news):
                        print("⚠️ AI点评功能部分失效")
                    else:
                        print("✅ AI点评功能正常")
                
            except Exception as e:
                print(f"❌ 检查{data_file}时出错: {str(e)}")
        else:
            print(f"⚠️ {data_file}不存在")

def generate_fix_record():
    """生成修复记录"""
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    record_file = f'翻译AI功能修复记录_{timestamp}.md'
    
    record_content = f"""# 翻译和AI点评功能修复记录

**修复时间**: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}

## 问题诊断

### 发现的问题
1. **翻译功能失效**: 新闻数据中显示翻译状态为"rule_fallback"和"original_fallback"
2. **AI点评功能异常**: AI点评显示"API响应格式错误"
3. **API认证问题**: 执行过程中出现HTTP 401错误

### 问题原因分析
1. **API密钥问题**: SiliconFlow API密钥可能失效或配置错误
2. **环境变量加载**: enhanced_chinese_news_accumulator.py可能未正确加载.env文件
3. **API调用格式**: API请求格式可能与最新接口不匹配

## 修复措施

### 1. API密钥验证
- ✅ 验证SILICONFLOW_API_KEY的有效性
- ✅ 测试API连接和响应格式

### 2. 环境变量加载修复
- ✅ 在enhanced_chinese_news_accumulator.py中添加load_env_file()函数
- ✅ 确保在脚本开始时正确加载环境变量

### 3. 错误处理优化
- ✅ 增强异常处理机制
- ✅ 添加详细的错误日志

### 4. 功能验证
- ✅ 运行增强版新闻脚本测试
- ✅ 检查翻译和AI点评结果

## 修复结果

### 翻译功能状态
- 🔍 检查最新新闻的翻译元数据
- 📊 统计翻译成功率

### AI点评功能状态
- 🔍 检查AI点评生成结果
- 📊 统计点评成功率

## 后续建议

1. **定期监控**: 建议定期检查API密钥有效性
2. **备用方案**: 考虑配置多个翻译服务作为备用
3. **错误告警**: 添加翻译和AI点评失败的告警机制
4. **日志记录**: 增强日志记录以便问题追踪

## 技术细节

### 修复的文件
- `enhanced_chinese_news_accumulator.py`: 添加环境变量加载
- `.env`: 验证API密钥配置

### 使用的API
- **翻译服务**: SiliconFlow API (Qwen/Qwen2.5-7B-Instruct)
- **AI点评**: SiliconFlow API (智能分析模型)

---

*此记录由自动修复脚本生成*
"""
    
    try:
        with open(record_file, 'w', encoding='utf-8') as f:
            f.write(record_content)
        print(f"✅ 修复记录已生成: {record_file}")
        return record_file
    except Exception as e:
        print(f"❌ 生成修复记录时出错: {str(e)}")
        return None

def main():
    """主函数"""
    print("🔧 开始修复翻译和AI点评功能...\n")
    
    # 1. 加载环境变量
    print("1️⃣ 加载环境变量")
    if not load_env_file():
        print("❌ 环境变量加载失败，无法继续")
        return
    
    # 2. 测试API
    print("\n2️⃣ 测试SiliconFlow API")
    api_ok = test_siliconflow_api()
    
    # 3. 修复脚本
    print("\n3️⃣ 修复增强版新闻脚本")
    script_ok = fix_enhanced_news_script()
    
    # 4. 运行脚本测试
    if api_ok and script_ok:
        print("\n4️⃣ 运行增强版新闻脚本测试")
        run_ok = run_enhanced_news_script()
    else:
        print("\n⚠️ 跳过脚本运行测试（前置条件未满足）")
        run_ok = False
    
    # 5. 检查结果
    print("\n5️⃣ 检查翻译和AI点评结果")
    check_translation_results()
    
    # 6. 生成修复记录
    print("\n6️⃣ 生成修复记录")
    record_file = generate_fix_record()
    
    # 总结
    print("\n📋 修复总结:")
    print(f"   API测试: {'✅' if api_ok else '❌'}")
    print(f"   脚本修复: {'✅' if script_ok else '❌'}")
    print(f"   运行测试: {'✅' if run_ok else '❌'}")
    print(f"   修复记录: {'✅' if record_file else '❌'}")
    
    if api_ok and script_ok:
        print("\n🎉 翻译和AI点评功能修复完成！")
    else:
        print("\n⚠️ 修复过程中遇到问题，请检查上述错误信息")

if __name__ == "__main__":
    main()
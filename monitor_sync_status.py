#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
监控Vercel和GitHub Pages同步状态
"""

import time
import urllib.request
import re
from datetime import datetime

def get_page_info(url, name):
    """获取页面信息"""
    try:
        with urllib.request.urlopen(url, timeout=15) as response:
            content = response.read().decode('utf-8')
            
        # 提取关键信息
        info = {
            'accessible': True,
            'has_title': 'AI科技日报' in content,
            'has_ai_features': any(keyword in content for keyword in ['硅基流动', 'AI翻译', 'siliconflow']),
            'content_length': len(content)
        }
        
        # 尝试提取时间戳
        timestamp_patterns = [
            r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})',
            r'(\d{4}-\d{2}-\d{2})',
            r'最后更新[：:]\s*(\d{4}-\d{2}-\d{2})'
        ]
        
        for pattern in timestamp_patterns:
            matches = re.findall(pattern, content)
            if matches:
                info['last_update'] = matches[-1]  # 取最后一个匹配
                break
        else:
            info['last_update'] = 'Unknown'
        
        return info
        
    except Exception as e:
        return {
            'accessible': False,
            'error': str(e),
            'has_title': False,
            'has_ai_features': False,
            'content_length': 0,
            'last_update': 'Unknown'
        }

def compare_platforms():
    """比较两个平台的状态"""
    print("🔍 检查平台同步状态...")
    print("=" * 60)
    
    # 检查Vercel
    print("🌐 检查Vercel状态...")
    vercel_info = get_page_info("https://ai-news-pusher.vercel.app", "Vercel")
    
    if vercel_info['accessible']:
        print("✅ Vercel可访问")
        print(f"   📋 包含标题: {'是' if vercel_info['has_title'] else '否'}")
        print(f"   🤖 AI功能: {'是' if vercel_info['has_ai_features'] else '否'}")
        print(f"   📏 内容长度: {vercel_info['content_length']:,} 字符")
        print(f"   ⏰ 最后更新: {vercel_info['last_update']}")
    else:
        print(f"❌ Vercel访问失败: {vercel_info.get('error', 'Unknown')}")
    
    print()
    
    # 检查GitHub Pages
    print("📱 检查GitHub Pages状态...")
    github_info = get_page_info("https://velist.github.io/ai-news-pusher/docs/", "GitHub Pages")
    
    if github_info['accessible']:
        print("✅ GitHub Pages可访问")
        print(f"   📋 包含标题: {'是' if github_info['has_title'] else '否'}")
        print(f"   🤖 AI功能: {'是' if github_info['has_ai_features'] else '否'}")
        print(f"   📏 内容长度: {github_info['content_length']:,} 字符")
        print(f"   ⏰ 最后更新: {github_info['last_update']}")
    else:
        print(f"❌ GitHub Pages访问失败: {github_info.get('error', 'Unknown')}")
    
    # 比较结果
    print("\n📊 同步状态分析:")
    print("=" * 60)
    
    if vercel_info['accessible'] and github_info['accessible']:
        # 比较内容长度
        length_diff = abs(vercel_info['content_length'] - github_info['content_length'])
        length_similarity = 1 - (length_diff / max(vercel_info['content_length'], github_info['content_length']))
        
        print(f"📏 内容长度差异: {length_diff:,} 字符")
        print(f"📊 内容相似度: {length_similarity:.2%}")
        
        # 功能对比
        features_match = vercel_info['has_ai_features'] == github_info['has_ai_features']
        print(f"🤖 AI功能一致: {'是' if features_match else '否'}")
        
        # 标题对比
        title_match = vercel_info['has_title'] == github_info['has_title']
        print(f"📋 标题一致: {'是' if title_match else '否'}")
        
        # 综合评估
        if length_similarity > 0.95 and features_match and title_match:
            print("🎉 同步状态: 完全同步")
            sync_status = "完全同步"
        elif length_similarity > 0.8:
            print("✅ 同步状态: 基本同步")
            sync_status = "基本同步"
        else:
            print("⚠️ 同步状态: 存在差异")
            sync_status = "存在差异"
    else:
        print("❌ 同步状态: 无法比较（部分平台不可访问）")
        sync_status = "无法比较"
    
    return {
        'vercel': vercel_info,
        'github': github_info,
        'sync_status': sync_status
    }

def monitor_deployment():
    """监控部署进度"""
    print("⏰ 开始监控部署进度...")
    print("=" * 60)
    
    start_time = datetime.now()
    max_wait_minutes = 10
    check_interval = 30  # 30秒检查一次
    
    for attempt in range(max_wait_minutes * 2):  # 每30秒检查一次，最多10分钟
        current_time = datetime.now()
        elapsed = (current_time - start_time).total_seconds() / 60
        
        print(f"\n🔍 检查 #{attempt + 1} (已等待 {elapsed:.1f} 分钟)")
        print(f"⏰ 当前时间: {current_time.strftime('%H:%M:%S')}")
        
        # 检查同步状态
        result = compare_platforms()
        
        if result['sync_status'] == "完全同步":
            print("\n🎉 同步完成！")
            print("✅ Vercel和GitHub Pages内容已完全同步")
            return True
        elif result['sync_status'] == "基本同步":
            print("\n✅ 基本同步完成！")
            print("💡 两个平台内容基本一致，可能存在细微差异")
            return True
        else:
            if attempt < max_wait_minutes * 2 - 1:
                print(f"⏳ 等待{check_interval}秒后继续检查...")
                time.sleep(check_interval)
            else:
                print("\n⚠️ 监控超时")
                print("💡 请手动检查Vercel控制台或稍后再试")
                return False
    
    return False

def provide_final_guidance():
    """提供最终指导"""
    print("\n🎯 最终指导建议:")
    print("=" * 60)
    
    print("🔍 如果同步仍有问题:")
    print("   1. 访问 https://vercel.com/dashboard")
    print("   2. 检查ai-news-pusher项目的部署历史")
    print("   3. 查看最新部署的日志和状态")
    print("   4. 确认部署时间是否为最近几分钟")
    
    print("\n🔧 手动解决方案:")
    print("   1. 在Vercel控制台点击'Redeploy'")
    print("   2. 选择最新的commit进行部署")
    print("   3. 等待部署完成后再次检查")
    
    print("\n🌐 验证方法:")
    print("   • 同时打开两个网站进行对比")
    print("   • 检查页面内容、更新时间、功能是否一致")
    print("   • 确认AI翻译功能在两个平台都正常工作")
    
    print("\n📞 如需进一步帮助:")
    print("   • 检查Vercel项目设置中的GitHub集成")
    print("   • 确认环境变量配置正确")
    print("   • 查看是否有构建错误或警告")

def main():
    """主监控流程"""
    print("🚀 监控Vercel和GitHub Pages同步状态")
    print("=" * 60)
    print(f"⏰ 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 初始检查
    print("\n📋 初始状态检查:")
    initial_result = compare_platforms()
    
    if initial_result['sync_status'] == "完全同步":
        print("\n🎉 已经完全同步！")
        print("✅ 无需等待，两个平台内容一致")
    else:
        print(f"\n⏳ 当前状态: {initial_result['sync_status']}")
        print("🔄 开始监控部署进度...")
        
        # 监控部署
        success = monitor_deployment()
        
        if not success:
            provide_final_guidance()
    
    # 最终状态检查
    print("\n📊 最终状态检查:")
    final_result = compare_platforms()
    
    print(f"\n🎯 最终结果: {final_result['sync_status']}")
    print("🌐 访问链接:")
    print("   📱 Vercel: https://ai-news-pusher.vercel.app")
    print("   📊 GitHub Pages: https://velist.github.io/ai-news-pusher/docs/")
    
    print(f"\n⏰ 完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
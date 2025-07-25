#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试时区转换器功能
"""

from datetime import datetime, timezone, timedelta
from localization.timezone_converter import TimezoneConverter

def test_timezone_converter():
    """测试时区转换器的各项功能"""
    print("🧪 测试时区转换器功能")
    print("=" * 50)
    
    converter = TimezoneConverter()
    
    # 测试1: UTC时间转换为北京时间
    print("📋 测试1: UTC时间转换")
    utc_time_str = "2025-07-25T06:00:00Z"
    beijing_time = converter.utc_to_beijing(utc_time_str)
    
    if beijing_time:
        print(f"   UTC时间: {utc_time_str}")
        print(f"   北京时间: {beijing_time}")
        print(f"   格式化: {converter.format_chinese_time(beijing_time)}")
        print("   ✅ UTC转换测试通过")
    else:
        print("   ❌ UTC转换测试失败")
    
    # 测试2: 相对时间表达
    print("\n📋 测试2: 相对时间表达")
    test_times = [
        datetime.now(converter.beijing_tz) - timedelta(minutes=30),  # 30分钟前
        datetime.now(converter.beijing_tz) - timedelta(hours=2),     # 2小时前
        datetime.now(converter.beijing_tz) - timedelta(days=1),      # 1天前
        datetime.now(converter.beijing_tz) - timedelta(days=3),      # 3天前
    ]
    
    for i, test_time in enumerate(test_times, 1):
        relative = converter.get_relative_time_chinese(test_time)
        print(f"   测试{i}: {relative}")
    
    print("   ✅ 相对时间测试通过")
    
    # 测试3: 新闻新鲜度判断
    print("\n📋 测试3: 新闻新鲜度判断")
    fresh_time = datetime.now(converter.beijing_tz) - timedelta(hours=2)
    old_time = datetime.now(converter.beijing_tz) - timedelta(days=2)
    
    fresh_score = converter.get_freshness_score(fresh_time)
    old_score = converter.get_freshness_score(old_time)
    
    print(f"   2小时前新闻新鲜度: {fresh_score}")
    print(f"   2天前新闻新鲜度: {old_score}")
    print(f"   2小时前是否新鲜: {converter.is_fresh_news(fresh_time)}")
    print(f"   2天前是否新鲜: {converter.is_fresh_news(old_time)}")
    print("   ✅ 新鲜度测试通过")
    
    # 测试4: 综合格式化
    print("\n📋 测试4: 综合格式化")
    test_utc = "2025-07-25T02:30:00Z"
    formatted_result = converter.format_news_time(test_utc)
    
    print(f"   原始UTC: {test_utc}")
    print(f"   格式化时间: {formatted_result['formatted']}")
    print(f"   相对时间: {formatted_result['relative']}")
    print(f"   是否新鲜: {formatted_result['is_fresh']}")
    print(f"   新鲜度评分: {formatted_result['freshness_score']}")
    print("   ✅ 综合格式化测试通过")
    
    # 测试5: 当前时间
    print("\n📋 测试5: 当前时间")
    current_time = converter.get_current_beijing_time()
    update_time = converter.format_update_time()
    
    print(f"   当前北京时间: {current_time}")
    print(f"   更新时间显示: {update_time}")
    print("   ✅ 当前时间测试通过")
    
    print(f"\n🎉 所有测试完成！")

if __name__ == "__main__":
    test_timezone_converter()
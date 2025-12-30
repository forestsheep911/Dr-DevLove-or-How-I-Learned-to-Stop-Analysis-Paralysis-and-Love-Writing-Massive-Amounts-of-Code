#!/usr/bin/env python3
"""测试新的时间范围参数"""

import sys
import os

# 添加 src 目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from gh_stats.utils import parse_date_range
import datetime

def test_range_params():
    """测试所有新的时间范围参数"""
    today = datetime.date.today()
    
    test_cases = [
        # 基础参数（向后兼容）
        ('today', 'Today'),
        ('week', 'This Week'),
        ('month', 'This Month'),
        ('year', 'This Year'),
        
        # 新的"this"系列参数
        ('thisweek', 'This Week'),
        ('thismonth', 'This Month'),
        ('thisyear', 'This Year'),
        
        # 新的历史参数
        ('yesterday', 'Yesterday'),
        ('lastweek', 'Last Week'),
        ('lastmonth', 'Last Month'),
        ('lastyear', 'Last Year'),
    ]
    
    print("=" * 70)
    print("Time Range Parameters Test Results")
    print("=" * 70)
    print(f"Test Date: {today}")
    print()
    
    success_count = 0
    fail_count = 0
    
    for param, desc in test_cases:
        try:
            start, end = parse_date_range(param)
            days = (end - start).days + 1
            print(f"[OK] {param:12} ({desc:15}) -> {start} to {end} ({days} days)")
            success_count += 1
        except Exception as e:
            print(f"[FAIL] {param:12} ({desc:15}) -> Error: {e}")
            fail_count += 1
    
    print()
    print("=" * 70)
    print(f"Test Complete! Success: {success_count}, Failed: {fail_count}")
    print("=" * 70)

if __name__ == '__main__':
    test_range_params()


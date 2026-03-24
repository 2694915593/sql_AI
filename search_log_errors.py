#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
搜索日志文件中的错误
"""

import os
import re

def search_log_errors():
    """搜索日志文件中的错误"""
    log_file = 'logs/sql_analyzer.log'
    
    if not os.path.exists(log_file):
        print("日志文件不存在")
        return
    
    print("=" * 70)
    print("搜索日志文件中的错误")
    print("=" * 70)
    
    with open(log_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 搜索各种错误模式
    error_patterns = [
        ('未找到记录', '未找到记录错误'),
        ('未找到SQL ID', 'SQL ID未找到错误'),
        ('更新失败', '更新失败错误'),
        ('ERROR', 'ERROR级别日志'),
        ('WARNING', 'WARNING级别日志'),
        ('失败', '失败相关日志'),
        ('错误', '错误相关日志'),
        ('Data truncated', '数据截断错误'),
        ('Connection', '连接相关错误'),
        ('timeout', '超时错误'),
        ('502', '502服务器错误'),
        ('500', '500服务器错误')
    ]
    
    for pattern, description in error_patterns:
        matches = re.finditer(pattern, content)
        match_list = list(matches)
        
        if match_list:
            print(f"\n{description} (找到 {len(match_list)} 处):")
            for match in match_list[:5]:  # 只显示前5个
                start = max(0, match.start() - 100)
                end = min(len(content), match.end() + 100)
                context = content[start:end]
                print(f"  ...{context}...")
            
            if len(match_list) > 5:
                print(f"  ... 还有 {len(match_list) - 5} 处")
    
    # 特别检查"未找到记录"错误
    print("\n" + "=" * 70)
    print("详细检查'未找到记录'错误")
    print("=" * 70)
    
    lines = content.split('\n')
    found = False
    
    for i, line in enumerate(lines):
        if '未找到记录' in line:
            found = True
            print(f"\n行 {i+1}: {line}")
            
            # 显示上下文
            print("上下文:")
            for j in range(max(0, i-3), min(len(lines), i+4)):
                prefix = '>>> ' if j == i else '    '
                print(f"{prefix}{lines[j]}")
    
    if not found:
        print("未找到'未找到记录'错误")
    
    # 检查最近的错误
    print("\n" + "=" * 70)
    print("最近的错误日志 (最后50行)")
    print("=" * 70)
    
    recent_lines = lines[-50:]
    error_count = 0
    
    for i, line in enumerate(recent_lines):
        if any(keyword in line for keyword in ['ERROR', 'WARNING', '失败', '错误', '未找到']):
            error_count += 1
            print(f"{line}")
    
    if error_count == 0:
        print("最近50行中没有错误日志")

if __name__ == '__main__':
    search_log_errors()
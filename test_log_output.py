#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试config_manager日志输出
"""
import sys
import io
import logging

sys.path.append('.')

# 捕获标准输出
old_stdout = sys.stdout
sys.stdout = io.StringIO()

try:
    from sql_ai_analyzer.config.config_manager import ConfigManager
    
    print("=== 测试ConfigManager日志输出 ===")
    
    # 创建一个ConfigManager实例
    cm = ConfigManager('sql_ai_analyzer/config/config.ini')
    
    # 调用会打印日志的方法
    print("\n调用get_all_target_db_aliases()...")
    aliases = cm.get_all_target_db_aliases()
    print(f"数据库别名: {aliases}")
    
    # 获取标准输出内容
    output = sys.stdout.getvalue()
    
finally:
    sys.stdout = old_stdout

print("=== 捕获的输出 ===")
print(output)
print("=== 结束 ===")

# 直接检查日志记录器配置
print("\n=== 检查日志记录器配置 ===")
logger = logging.getLogger('sql_ai_analyzer.config.config_manager')
print(f"日志记录器名称: {logger.name}")
print(f"日志记录器级别: {logger.level} ({logging.getLevelName(logger.level)})")
print(f"日志记录器处理器: {logger.handlers}")
if logger.handlers:
    for handler in logger.handlers:
        print(f"  处理器: {handler}, 级别: {handler.level}")
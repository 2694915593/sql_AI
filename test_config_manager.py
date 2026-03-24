#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试ConfigManager的get_optimization_config方法
"""

import os
import sys

# 添加项目根目录和sql_ai_analyzer目录到路径
project_root = os.path.dirname(os.path.abspath(__file__))
sql_ai_analyzer_dir = os.path.join(project_root, 'sql_ai_analyzer')
sys.path.insert(0, project_root)
sys.path.insert(0, sql_ai_analyzer_dir)

try:
    from sql_ai_analyzer.config.config_manager import ConfigManager
    print("成功导入ConfigManager")
    
    # 测试方法是否存在
    config_manager = ConfigManager()
    print(f"ConfigManager对象类型: {type(config_manager)}")
    
    # 检查是否有get_optimization_config方法
    if hasattr(config_manager, 'get_optimization_config'):
        print("✓ ConfigManager有get_optimization_config方法")
        result = config_manager.get_optimization_config()
        print(f"优化配置: {result}")
    else:
        print("✗ ConfigManager没有get_optimization_config方法")
        print(f"可用方法: {[m for m in dir(config_manager) if not m.startswith('_')]}")
        
except ImportError as e:
    print(f"导入失败: {e}")
    print(f"Python路径: {sys.path}")
except Exception as e:
    print(f"测试失败: {str(e)}")
    import traceback
    traceback.print_exc()
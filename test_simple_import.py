#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单测试模块导入问题
"""

import sys
import os

# 清理所有缓存
sys.path_importer_cache.clear()

# 删除所有相关的模块
for mod_name in list(sys.modules.keys()):
    if 'sql_ai_analyzer' in mod_name or 'config_manager' in mod_name:
        del sys.modules[mod_name]

# 重新设置路径
project_root = os.path.dirname(os.path.abspath(__file__))
sql_ai_analyzer_dir = os.path.join(project_root, 'sql_ai_analyzer')
sys.path.insert(0, project_root)
sys.path.insert(0, sql_ai_analyzer_dir)

print(f"项目根目录: {project_root}")
print(f"sql_ai_analyzer目录: {sql_ai_analyzer_dir}")
print(f"Python路径: {sys.path[:3]}")

# 测试1：直接导入ConfigManager
print("\n" + "="*50)
print("测试1：直接导入ConfigManager")
print("="*50)

try:
    from sql_ai_analyzer.config.config_manager import ConfigManager
    print("ConfigManager导入成功")
    
    # 检查方法
    cm = ConfigManager()
    print(f"ConfigManager实例类型: {type(cm)}")
    print(f"是否有get_optimization_config方法: {hasattr(cm, 'get_optimization_config')}")
    
    if hasattr(cm, 'get_optimization_config'):
        try:
            config = cm.get_optimization_config()
            print(f"优化配置: {config}")
        except Exception as e:
            print(f"调用get_optimization_config失败: {e}")
    else:
        print("可用方法:")
        methods = [m for m in dir(cm) if not m.startswith('_')]
        for method in methods:
            print(f"  {method}")
            
except ImportError as e:
    print(f"ConfigManager导入失败: {e}")
except Exception as e:
    print(f"其他错误: {e}")

# 测试2：导入DataValueFetcher
print("\n" + "="*50)
print("测试2：导入DataValueFetcher")
print("="*50)

try:
    from sql_ai_analyzer.data_collector.data_value_fetcher import DataValueFetcher
    print("DataValueFetcher导入成功")
    
    # 创建简单logger
    import logging
    logger = logging.getLogger('test')
    logger.setLevel(logging.INFO)
    
    # 创建ConfigManager
    cm = ConfigManager()
    
    # 尝试创建DataValueFetcher
    try:
        data_fetcher = DataValueFetcher(cm, logger)
        print("DataValueFetcher创建成功")
        print(f"enable_data_fetching: {data_fetcher.enable_data_fetching}")
    except Exception as e:
        print(f"DataValueFetcher创建失败: {e}")
        import traceback
        traceback.print_exc()
        
except ImportError as e:
    print(f"DataValueFetcher导入失败: {e}")
except Exception as e:
    print(f"其他错误: {e}")

# 测试3：检查模块文件位置
print("\n" + "="*50)
print("测试3：检查模块文件位置")
print("="*50)

# 检查重要文件是否存在
files_to_check = [
    'sql_ai_analyzer/config/config_manager.py',
    'sql_ai_analyzer/data_collector/data_value_fetcher.py',
    'sql_ai_analyzer/data_collector/dynamic_sql_parser.py'
]

for file_path in files_to_check:
    full_path = os.path.join(project_root, file_path)
    exists = os.path.exists(full_path)
    print(f"{file_path}: {'✓ 存在' if exists else '✗ 不存在'}")
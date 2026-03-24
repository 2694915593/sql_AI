#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试config_manager修复
"""
import sys
sys.path.append('.')

from sql_ai_analyzer.config.config_manager import ConfigManager

cm = ConfigManager('sql_ai_analyzer/config/config.ini')

print('1. 测试获取源数据库配置:')
db_config = cm.get_database_config()
print('   ', db_config)

print('2. 测试获取AI模型配置:')
ai_config = cm.get_ai_model_config()
print('   ', ai_config)

print('3. 测试获取日志配置:')
log_config = cm.get_log_config()
print('   ', log_config)

print('4. 测试获取ECUP数据库配置:')
try:
    ecup_configs = cm.get_all_target_db_configs('ECUP')
    print(f'   ECUP配置数量: {len(ecup_configs)}')
    for i, config in enumerate(ecup_configs):
        print(f'   实例{i+1}: {config.get("host")}:{config.get("port")}')
except Exception as e:
    print(f'   错误: {e}')

print('5. 测试获取第一个ECUP实例:')
try:
    ecup1 = cm.get_target_db_config('ECUP', 0)
    print(f'   实例1: {ecup1.get("host")}:{ecup1.get("port")}')
except Exception as e:
    print(f'   错误: {e}')

print('6. 测试获取第二个ECUP实例:')
try:
    ecup2 = cm.get_target_db_config('ECUP', 1)
    print(f'   实例2: {ecup2.get("host")}:{ecup2.get("port")}')
except Exception as e:
    print(f'   错误: {e}')

print('7. 测试获取所有数据库别名:')
try:
    aliases = cm.get_all_target_db_aliases()
    print(f'   数据库别名: {aliases}')
except Exception as e:
    print(f'   错误: {e}')

print('\n所有测试完成！')
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
查看am_solline_info表结构
"""

import sys
sys.path.append('e:/Code/sqlAnalize/sql_ai_analyzer')

try:
    from utils.db_connector_pymysql import DatabaseManager
    from config.config_manager import ConfigManager
    
    config_manager = ConfigManager()
    db_config = config_manager.get_database_config()
    db = DatabaseManager(db_config)
    
    # 查看表结构
    result = db.fetch_all('DESCRIBE am_solline_info')
    print('am_solline_info表结构:')
    print('-' * 80)
    for row in result:
        field = row.get('Field', '')
        type_ = row.get('Type', '')
        null = row.get('Null', '')
        key = row.get('Key', '')
        default = row.get('Default', '')
        extra = row.get('Extra', '')
        print(f'{field:20} {type_:20} {null:5} {key:5} {str(default):20} {extra:10}')
    print('-' * 80)
    
    # 查看现有数据示例
    print('\n现有数据示例（前5行）:')
    print('-' * 80)
    rows = db.fetch_all('SELECT ID, SQLLINE, analysis_status, error_message FROM am_solline_info LIMIT 5')
    for row in rows:
        sql_text = row.get('SQLLINE', '')
        if sql_text:
            sql_preview = sql_text[:50] + '...' if len(sql_text) > 50 else sql_text
        else:
            sql_preview = 'None'
        
        print(f'ID: {row.get("ID")}, SQL: {sql_preview}, 状态: {row.get("analysis_status")}, 错误: {row.get("error_message")}')
    
except Exception as e:
    import traceback
    print(f'错误: {str(e)}')
    traceback.print_exc()
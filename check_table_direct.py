#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直接查看am_solline_info表结构
"""

import sys
sys.path.append('e:/Code/sqlAnalize/sql_ai_analyzer')

try:
    import pymysql
    from config.config_manager import ConfigManager
    
    config_manager = ConfigManager()
    db_config = config_manager.get_database_config()
    
    # 直接连接数据库
    conn = pymysql.connect(
        host=db_config['host'],
        port=db_config['port'],
        user=db_config['username'],
        password=db_config['password'],
        database=db_config['database'],
        charset='utf8mb4'
    )
    
    with conn.cursor() as cursor:
        # 查看表结构
        cursor.execute('DESCRIBE am_solline_info')
        result = cursor.fetchall()
        
        print('am_solline_info表结构:')
        print('-' * 80)
        for row in result:
            print(f'{row[0]:20} {row[1]:20} {row[2]:5} {row[3]:5} {str(row[4]):20} {row[5]:10}')
        print('-' * 80)
        
        # 查看现有数据示例
        print('\n现有数据示例（前5行）:')
        print('-' * 80)
        cursor.execute('SELECT ID, SQLLINE, analysis_status, error_message FROM am_solline_info LIMIT 5')
        rows = cursor.fetchall()
        for row in rows:
            sql_text = row[1] if row[1] else ''
            if sql_text:
                sql_preview = sql_text[:50] + '...' if len(sql_text) > 50 else sql_text
            else:
                sql_preview = 'None'
            
            print(f'ID: {row[0]}, SQL: {sql_preview}, 状态: {row[2]}, 错误: {row[3]}')
    
    conn.close()
    
except Exception as e:
    import traceback
    print(f'错误: {str(e)}')
    traceback.print_exc()
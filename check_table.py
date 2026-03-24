#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查表是否存在
"""

import pymysql

def check_table():
    """检查am_solline_info表是否存在"""
    try:
        conn = pymysql.connect(
            host='localhost',
            port=3306,
            database='testdb',
            user='root',
            password='123456'
        )
        
        cursor = conn.cursor()
        
        # 检查表是否存在
        cursor.execute('SHOW TABLES LIKE "am_solline_info"')
        result = cursor.fetchone()
        
        if result:
            print('✓ am_solline_info表存在')
            
            # 检查表结构
            cursor.execute('DESCRIBE am_solline_info')
            columns = cursor.fetchall()
            print(f'表有 {len(columns)} 列')
            
            # 显示前几列
            print('\n表结构:')
            for i, col in enumerate(columns[:5], 1):
                print(f'  {i}. {col[0]} ({col[1]})')
            if len(columns) > 5:
                print(f'  ... 还有{len(columns)-5}列')
            
            # 检查是否有分析相关字段
            column_names = [col[0] for col in columns]
            analysis_fields = ['analysis_status', 'analysis_result', 'analysis_time', 'error_message']
            
            print('\n分析相关字段检查:')
            for field in analysis_fields:
                if field in column_names:
                    print(f'  ✓ {field}字段存在')
                else:
                    print(f'  ✗ {field}字段不存在')
                    
            # 检查是否有数据
            cursor.execute('SELECT COUNT(*) FROM am_solline_info')
            count = cursor.fetchone()[0]
            print(f'\n表中现有 {count} 条记录')
            
            if count > 0:
                # 显示前几条记录
                cursor.execute('SELECT ID, SQLLINE FROM am_solline_info LIMIT 3')
                records = cursor.fetchall()
                print('前几条记录:')
                for record in records:
                    print(f'  ID: {record[0]}, SQL: {record[1][:50]}...' if len(record[1]) > 50 else f'  ID: {record[0]}, SQL: {record[1]}')
        else:
            print('✗ am_solline_info表不存在')
            
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f'数据库错误: {e}')
    except Exception as e:
        print(f'错误: {e}')

if __name__ == '__main__':
    check_table()
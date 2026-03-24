#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
重置SQL记录状态
"""

import pymysql

def reset_sql_status():
    """重置SQL记录状态"""
    print("重置SQL记录状态...")
    
    try:
        conn = pymysql.connect(
            host='localhost',
            port=3306,
            database='testdb',
            user='root',
            password='123456',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        
        with conn.cursor() as cursor:
            # 重置ID为1的SQL记录状态
            cursor.execute("UPDATE am_solline_info SET analysis_status = 'pending', analysis_time = NULL WHERE ID = 1")
            conn.commit()
            
            print("✓ 已重置ID 1的SQL记录状态为pending")
            
            # 检查状态
            cursor.execute("SELECT ID, SQLLINE, SYSTEMID, analysis_status FROM am_solline_info WHERE ID = 1")
            record = cursor.fetchone()
            
            if record:
                print(f"ID {record['ID']}: {record['SQLLINE'][:50]}...")
                print(f"系统ID: {record['SYSTEMID']}, 状态: {record['analysis_status']}")
        
        conn.close()
        
    except Exception as e:
        print(f"重置失败: {e}")

if __name__ == '__main__':
    reset_sql_status()
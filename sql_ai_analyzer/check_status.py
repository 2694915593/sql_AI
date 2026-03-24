#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查数据库状态
"""

import pymysql

def check_database_status():
    """检查数据库状态"""
    print("=" * 60)
    print("数据库状态检查")
    print("=" * 60)
    
    try:
        conn = pymysql.connect(
            host='localhost',
            port=3306,
            database='testdb',
            user='root',
            password='123456'
        )
        cursor = conn.cursor(dictionary=True)
        
        # 检查待分析SQL
        cursor.execute('''
            SELECT 
                COUNT(*) as total,
                COUNT(CASE WHEN analysis_status = 'pending' THEN 1 END) as pending,
                COUNT(CASE WHEN analysis_status = 'analyzed' THEN 1 END) as analyzed,
                COUNT(CASE WHEN analysis_status = 'failed' THEN 1 END) as failed
            FROM am_solline_info
        ''')
        stats = cursor.fetchone()
        
        print("数据库状态:")
        print(f"总记录数: {stats['total']}")
        print(f"待分析(pending): {stats['pending']}")
        print(f"已分析(analyzed): {stats['analyzed']}")
        print(f"分析失败(failed): {stats['failed']}")
        
        # 查看具体记录
        cursor.execute('''
            SELECT ID, SQLLINE, TABLENAME, SYSTEMID, analysis_status, analysis_time
            FROM am_solline_info
            ORDER BY ID
        ''')
        records = cursor.fetchall()
        
        print("\n所有记录:")
        for record in records:
            print(f"ID {record['ID']}: {record['SQLLINE'][:50]}...")
            print(f"  表名: {record['TABLENAME']}, 系统ID: {record['SYSTEMID']}")
            print(f"  状态: {record['analysis_status']}, 时间: {record['analysis_time']}")
            print()
        
        cursor.close()
        conn.close()
        
        print("=" * 60)
        print("状态检查完成")
        print("=" * 60)
        
    except Exception as e:
        print(f"检查数据库状态失败: {e}")

if __name__ == '__main__':
    check_database_status()
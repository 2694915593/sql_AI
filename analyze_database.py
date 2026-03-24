#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库数据分析脚本
分析am_solline_info表中的所有数据
"""

import pymysql
import json

def analyze_database():
    """分析数据库中的所有数据"""
    print("=" * 70)
    print("AI-SQL质量分析系统 - 数据库数据分析报告")
    print("=" * 70)
    
    try:
        # 连接数据库
        conn = pymysql.connect(
            host='localhost',
            port=3306,
            database='testdb',
            user='root',
            password='123456'
        )
        cursor = conn.cursor(dictionary=True)
        
        # 1. 表结构分析
        print("\n1. 表结构分析")
        print("-" * 40)
        
        cursor.execute('DESCRIBE am_solline_info')
        columns = cursor.fetchall()
        print(f"表有 {len(columns)} 列:")
        for col in columns:
            print(f"  {col['Field']}: {col['Type']}")
        
        # 2. 数据统计
        print("\n2. 数据统计分析")
        print("-" * 40)
        
        cursor.execute('SELECT COUNT(*) as total FROM am_solline_info')
        total = cursor.fetchone()['total']
        print(f"总记录数: {total}")
        
        cursor.execute('''
            SELECT 
                COUNT(*) as pending_count,
                COUNT(CASE WHEN analysis_status = 'analyzed' THEN 1 END) as analyzed_count,
                COUNT(CASE WHEN analysis_status = 'failed' THEN 1 END) as failed_count,
                COUNT(CASE WHEN analysis_status IS NULL THEN 1 END) as null_count
            FROM am_solline_info
        ''')
        stats = cursor.fetchone()
        print(f"待分析(pending): {stats['pending_count']}")
        print(f"已分析(analyzed): {stats['analyzed_count']}")
        print(f"分析失败(failed): {stats['failed_count']}")
        print(f"状态为空(null): {stats['null_count']}")
        
        # 3. SQL类型分布
        print("\n3. SQL类型分布")
        print("-" * 40)
        
        cursor.execute('''
            SELECT 
                CASE 
                    WHEN UPPER(SQLLINE) LIKE 'SELECT%' THEN 'SELECT'
                    WHEN UPPER(SQLLINE) LIKE 'INSERT%' THEN 'INSERT'
                    WHEN UPPER(SQLLINE) LIKE 'UPDATE%' THEN 'UPDATE'
                    WHEN UPPER(SQLLINE) LIKE 'DELETE%' THEN 'DELETE'
                    WHEN UPPER(SQLLINE) LIKE 'CREATE%' THEN 'CREATE'
                    WHEN UPPER(SQLLINE) LIKE 'ALTER%' THEN 'ALTER'
                    WHEN UPPER(SQLLINE) LIKE 'DROP%' THEN 'DROP'
                    ELSE 'OTHER'
                END as sql_type,
                COUNT(*) as count
            FROM am_solline_info
            WHERE SQLLINE IS NOT NULL AND SQLLINE != ''
            GROUP BY sql_type
            ORDER BY count DESC
        ''')
        sql_types = cursor.fetchall()
        for row in sql_types:
            print(f"  {row['sql_type']}: {row['count']}")
        
        # 4. 表名分布
        print("\n4. 表名分布 (前15个)")
        print("-" * 40)
        
        cursor.execute('''
            SELECT 
                TABLENAME,
                COUNT(*) as count
            FROM am_solline_info
            WHERE TABLENAME IS NOT NULL AND TABLENAME != ''
            GROUP BY TABLENAME
            ORDER BY count DESC
            LIMIT 15
        ''')
        tables = cursor.fetchall()
        for row in tables:
            print(f"  {row['TABLENAME']}: {row['count']}")
        
        # 5. 操作类型分布
        print("\n5. 操作类型分布")
        print("-" * 40)
        
        cursor.execute('''
            SELECT 
                OPERATETYPE,
                COUNT(*) as count
            FROM am_solline_info
            WHERE OPERATETYPE IS NOT NULL
            GROUP BY OPERATETYPE
            ORDER BY count DESC
        ''')
        operations = cursor.fetchall()
        for row in operations:
            print(f"  操作类型 {row['OPERATETYPE']}: {row['count']}")
        
        # 6. 系统ID分布
        print("\n6. 系统ID分布")
        print("-" * 40)
        
        cursor.execute('''
            SELECT 
                SYSTEMID,
                COUNT(*) as count
            FROM am_solline_info
            WHERE SYSTEMID IS NOT NULL AND SYSTEMID != ''
            GROUP BY SYSTEMID
            ORDER BY count DESC
            LIMIT 10
        ''')
        systems = cursor.fetchall()
        for row in systems:
            print(f"  {row['SYSTEMID']}: {row['count']}")
        
        # 7. 时间范围分析
        print("\n7. 时间范围分析")
        print("-" * 40)
        
        cursor.execute('''
            SELECT 
                MIN(ID) as min_id,
                MAX(ID) as max_id,
                MIN(UPDTIME) as min_time,
                MAX(UPDTIME) as max_time
            FROM am_solline_info
        ''')
        time_range = cursor.fetchone()
        print(f"ID范围: {time_range['min_id']} - {time_range['max_id']}")
        print(f"更新时间范围: {time_range['min_time']} - {time_range['max_time']}")
        
        # 8. 分析结果质量检查
        print("\n8. 分析结果质量检查")
        print("-" * 40)
        
        cursor.execute('''
            SELECT 
                analysis_status,
                COUNT(*) as count,
                ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM am_solline_info), 2) as percentage
            FROM am_solline_info
            GROUP BY analysis_status
            ORDER BY count DESC
        ''')
        analysis_stats = cursor.fetchall()
        for row in analysis_stats:
            status = row['analysis_status'] if row['analysis_status'] else 'NULL'
            print(f"  状态 {status}: {row['count']} 条 ({row['percentage']}%)")
        
        # 9. 错误分析
        print("\n9. 错误分析")
        print("-" * 40)
        
        cursor.execute('''
            SELECT 
                error_message,
                COUNT(*) as count
            FROM am_solline_info
            WHERE error_message IS NOT NULL AND error_message != ''
            GROUP BY error_message
            ORDER BY count DESC
            LIMIT 5
        ''')
        errors = cursor.fetchall()
        if errors:
            for row in errors:
                error_msg = row['error_message'][:50] + "..." if len(row['error_message']) > 50 else row['error_message']
                print(f"  错误: {error_msg}")
                print(f"      出现次数: {row['count']}")
        else:
            print("  没有错误记录")
        
        # 10. 样本数据展示
        print("\n10. 样本数据展示 (最新5条)")
        print("-" * 40)
        
        cursor.execute('''
            SELECT 
                ID,
                SUBSTRING(SQLLINE, 1, 50) as sql_preview,
                TABLENAME,
                OPERATETYPE,
                SYSTEMID,
                analysis_status,
                analysis_time
            FROM am_solline_info
            ORDER BY ID DESC
            LIMIT 5
        ''')
        samples = cursor.fetchall()
        for row in samples:
            print(f"  ID: {row['ID']}")
            print(f"    SQL: {row['sql_preview']}...")
            print(f"    表名: {row['TABLENAME']}")
            print(f"    操作类型: {row['OPERATETYPE']}")
            print(f"    系统ID: {row['SYSTEMID']}")
            print(f"    分析状态: {row['analysis_status']}")
            print(f"    分析时间: {row['analysis_time']}")
            print()
        
        cursor.close()
        conn.close()
        
        print("=" * 70)
        print("数据库分析完成")
        print("=" * 70)
        
    except Exception as e:
        print(f"数据库分析失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    analyze_database()
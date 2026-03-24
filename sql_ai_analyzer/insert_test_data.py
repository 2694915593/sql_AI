#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
插入测试数据到am_solline_info表
"""

import pymysql

def insert_test_data():
    """插入测试数据"""
    try:
        conn = pymysql.connect(
            host='localhost',
            port=3306,
            database='testdb',
            user='root',
            password='123456'
        )
        
        cursor = conn.cursor()
        
        print("开始插入测试数据...")
        
        # 检查表中是否有数据
        cursor.execute("SELECT COUNT(*) FROM am_solline_info")
        count = cursor.fetchone()[0]
        print(f"表中现有 {count} 条记录")
        
        if count == 0:
            # 插入测试数据
            test_data = [
                ("SELECT * FROM users WHERE id = 1", "db_production", "users", "pending"),
                ("SELECT u.name, o.amount FROM users u JOIN orders o ON u.id = o.user_id", "db_production", "users,orders", "pending"),
                ("SELECT * FROM transaction_logs WHERE create_date > '2024-01-01'", "db_production", "transaction_logs", "pending"),
                ("UPDATE products SET price = price * 1.1 WHERE category = 'electronics'", "db_production", "products", "pending"),
                ("DELETE FROM temp_logs WHERE created_at < DATE_SUB(NOW(), INTERVAL 30 DAY)", "db_production", "temp_logs", "pending")
            ]
            
            insert_query = """
                INSERT INTO am_solline_info (SQLLINE, SYSTEMID, TABLENAME, analysis_status) 
                VALUES (%s, %s, %s, %s)
            """
            
            for data in test_data:
                cursor.execute(insert_query, data)
            
            conn.commit()
            print(f"✓ 插入 {len(test_data)} 条测试数据")
        else:
            print("✓ 表中已有数据，无需插入")
        
        # 显示插入的数据
        cursor.execute("SELECT ID, SQLLINE, TABLENAME, analysis_status FROM am_solline_info")
        records = cursor.fetchall()
        
        print("\n当前表中的数据:")
        for record in records:
            print(f"  ID: {record[0]}, 表名: {record[2]}, 状态: {record[3]}")
            print(f"    SQL: {record[1][:60]}..." if len(record[1]) > 60 else f"    SQL: {record[1]}")
            print()
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f'数据库错误: {e}')
    except Exception as e:
        print(f'错误: {e}')

if __name__ == '__main__':
    insert_test_data()
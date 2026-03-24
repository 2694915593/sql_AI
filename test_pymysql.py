#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试pymysql连接
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.db_connector_pymysql import DatabaseManager, create_db_connection

def test_pymysql_connection():
    """测试pymysql连接"""
    print("=" * 60)
    print("测试pymysql数据库连接")
    print("=" * 60)
    
    # 测试配置
    config = {
        'host': 'localhost',
        'port': 3306,
        'database': 'testdb',
        'username': 'root',
        'password': '123456',
        'db_type': 'mysql'
    }
    
    try:
        print("1. 测试简单连接...")
        conn = create_db_connection(config)
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1 as test")
            result = cursor.fetchone()
            print(f"   ✓ 连接成功: {result['test']}")
        conn.close()
        
        print("\n2. 测试DatabaseManager...")
        db_manager = DatabaseManager(config)
        
        # 测试查询
        print("   测试查询...")
        results = db_manager.fetch_all("SHOW DATABASES")
        print(f"   数据库数量: {len(results)}")
        for db in results[:5]:  # 只显示前5个
            print(f"     - {db['Database']}")
        
        # 测试testdb数据库
        print("\n   测试testdb数据库...")
        results = db_manager.fetch_all("SHOW TABLES")
        print(f"   表数量: {len(results)}")
        for table in results:
            print(f"     - {list(table.values())[0]}")
        
        # 测试am_solline_info表
        print("\n   测试am_solline_info表...")
        results = db_manager.fetch_all("SELECT COUNT(*) as count FROM am_solline_info")
        if results:
            print(f"   记录数: {results[0]['count']}")
        
        # 测试带参数的查询
        print("\n   测试带参数的查询...")
        results = db_manager.fetch_all("SELECT ID, SQLLINE FROM am_solline_info WHERE ID = %s", (1,))
        if results:
            print(f"   ID 1: {results[0]['SQLLINE'][:50]}...")
        
        print("\n3. 测试连接池...")
        # 多次查询测试连接池
        for i in range(3):
            result = db_manager.fetch_one("SELECT NOW() as current_time_value")
            print(f"   查询 {i+1}: {result['current_time_value']}")
        
        print("\n" + "=" * 60)
        print("✓ pymysql连接测试通过！")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_pymysql_connection()
    sys.exit(0 if success else 1)
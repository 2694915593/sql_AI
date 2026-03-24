#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试MySQL EXPLAIN语法
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.db_connector_pymysql import create_db_connection
from config.config_manager import ConfigManager

def test_explain_syntax():
    """测试EXPLAIN语法"""
    print("测试MySQL EXPLAIN语法")
    print("=" * 80)
    
    try:
        # 加载配置
        config = ConfigManager('config/config.ini')
        
        # 获取目标数据库配置
        target_config = config.get_target_db_config('db_production')
        
        # 创建数据库连接
        conn = create_db_connection(target_config)
        
        test_cases = [
            ("SELECT 1", "简单SELECT 1"),
            ("SELECT * FROM am_solline_info LIMIT 1", "查询实际表"),
            ("SELECT * FROM am_solline_info WHERE ID = 1", "带WHERE条件的查询"),
            ("SELECT * FROM am_solline_info WHERE SQLLINE LIKE '%SELECT%'", "带LIKE的查询"),
        ]
        
        for sql, description in test_cases:
            print(f"\n测试: {description}")
            print(f"SQL: {sql}")
            
            try:
                with conn.cursor() as cursor:
                    # 测试1: 直接执行SQL
                    print("1. 直接执行SQL:")
                    cursor.execute(sql)
                    result = cursor.fetchone()
                    print(f"   结果: {result}")
                    
                    # 测试2: 使用EXPLAIN
                    print("2. 使用EXPLAIN:")
                    explain_sql = f"EXPLAIN {sql}"
                    print(f"   EXPLAIN语句: {explain_sql}")
                    cursor.execute(explain_sql)
                    explain_result = cursor.fetchall()
                    print(f"   EXPLAIN结果行数: {len(explain_result)}")
                    if explain_result:
                        print(f"   第一行: {explain_result[0]}")
                    
                    # 测试3: 使用EXPLAIN EXTENDED
                    print("3. 使用EXPLAIN EXTENDED:")
                    explain_extended_sql = f"EXPLAIN EXTENDED {sql}"
                    print(f"   EXPLAIN EXTENDED语句: {explain_extended_sql}")
                    cursor.execute(explain_extended_sql)
                    explain_extended_result = cursor.fetchall()
                    print(f"   EXPLAIN EXTENDED结果行数: {len(explain_extended_result)}")
                    if explain_extended_result:
                        print(f"   第一行: {explain_extended_result[0]}")
                        
            except Exception as e:
                print(f"   错误: {str(e)}")
        
        conn.close()
        
    except Exception as e:
        print(f"测试EXPLAIN语法时发生错误: {str(e)}")

def test_dynamic_sql_explain():
    """测试动态SQL的EXPLAIN"""
    print("\n\n测试动态SQL的EXPLAIN")
    print("=" * 80)
    
    try:
        # 加载配置
        config = ConfigManager('config/config.ini')
        
        # 获取目标数据库配置
        target_config = config.get_target_db_config('db_production')
        
        # 创建数据库连接
        conn = create_db_connection(target_config)
        
        # 测试动态SQL
        dynamic_sql = "SELECT * FROM am_solline_info WHERE ID = 123"
        
        print(f"动态SQL: {dynamic_sql}")
        
        with conn.cursor() as cursor:
            # 测试EXPLAIN
            explain_sql = f"EXPLAIN {dynamic_sql}"
            print(f"EXPLAIN语句: {explain_sql}")
            
            try:
                cursor.execute(explain_sql)
                result = cursor.fetchall()
                print(f"EXPLAIN结果: {len(result)} 行")
                if result:
                    print(f"第一行: {result[0]}")
            except Exception as e:
                print(f"EXPLAIN错误: {str(e)}")
                
            # 测试EXPLAIN EXTENDED
            explain_extended_sql = f"EXPLAIN EXTENDED {dynamic_sql}"
            print(f"EXPLAIN EXTENDED语句: {explain_extended_sql}")
            
            try:
                cursor.execute(explain_extended_sql)
                result = cursor.fetchall()
                print(f"EXPLAIN EXTENDED结果: {len(result)} 行")
                if result:
                    print(f"第一行: {result[0]}")
            except Exception as e:
                print(f"EXPLAIN EXTENDED错误: {str(e)}")
        
        conn.close()
        
    except Exception as e:
        print(f"测试动态SQL EXPLAIN时发生错误: {str(e)}")

def main():
    """主函数"""
    print("MySQL EXPLAIN语法测试")
    print("=" * 80)
    
    test_explain_syntax()
    test_dynamic_sql_explain()
    
    print("\n" + "=" * 80)
    print("测试完成")

if __name__ == '__main__':
    main()
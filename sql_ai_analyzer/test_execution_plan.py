#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试获取执行计划功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.config_manager import ConfigManager
from data_collector.metadata_collector import MetadataCollector
from data_collector.sql_extractor import SQLExtractor

def test_sql_type_detection():
    """测试SQL类型检测"""
    print("测试SQL类型检测")
    print("=" * 80)
    
    collector = MetadataCollector(None)
    
    test_cases = [
        ("SELECT * FROM users", "DML"),
        ("INSERT INTO users (name) VALUES ('test')", "DML"),
        ("UPDATE users SET name = 'test' WHERE id = 1", "DML"),
        ("DELETE FROM users WHERE id = 1", "DML"),
        ("CREATE TABLE users (id INT)", "DDL"),
        ("ALTER TABLE users ADD COLUMN email VARCHAR(100)", "DDL"),
        ("DROP TABLE users", "DDL"),
        ("GRANT SELECT ON users TO user1", "DCL"),
        ("REVOKE SELECT ON users FROM user1", "DCL"),
        ("COMMIT", "TCL"),
        ("ROLLBACK", "TCL"),
        ("", "UNKNOWN"),
        ("-- 这是一个注释", "UNKNOWN"),
    ]
    
    for sql, expected_type in test_cases:
        detected_type = collector.detect_sql_type(sql)
        status = "✓" if detected_type == expected_type else "✗"
        print(f"{status} SQL: {sql[:50]}...")
        print(f"  期望: {expected_type}, 实际: {detected_type}")

def test_execution_plan_for_dml():
    """测试DML语句的执行计划获取"""
    print("\n\n测试DML语句的执行计划获取")
    print("=" * 80)
    
    try:
        # 加载配置
        config = ConfigManager('config/config.ini')
        
        # 创建元数据收集器
        collector = MetadataCollector(config)
        
        # 测试SQL - 使用实际存在的表
        test_sqls = [
            {
                "sql": "SELECT * FROM am_solline_info WHERE ID = 1",
                "description": "简单查询"
            },
            {
                "sql": "SELECT * FROM am_solline_info LIMIT 5",
                "description": "限制查询"
            },
            {
                "sql": "SELECT COUNT(*) as count FROM am_solline_info",
                "description": "计数查询"
            },
            {
                "sql": "SELECT * FROM am_solline_info WHERE SQLLINE LIKE '%SELECT%'",
                "description": "LIKE查询"
            }
        ]
        
        # 使用测试数据库别名（根据实际配置调整）
        db_alias = "db_production"
        
        for i, test_case in enumerate(test_sqls, 1):
            print(f"\n测试 {i}: {test_case['description']}")
            print(f"SQL: {test_case['sql']}")
            
            # 获取执行计划
            result = collector.get_execution_plan(db_alias, test_case['sql'])
            
            print(f"SQL类型: {result.get('sql_type', 'UNKNOWN')}")
            print(f"是否有执行计划: {result.get('has_execution_plan', False)}")
            
            if result.get('has_execution_plan'):
                execution_plan = result.get('execution_plan', {})
                print(f"执行计划类型: {type(execution_plan)}")
                
                if isinstance(execution_plan, list):
                    print(f"执行计划行数: {len(execution_plan)}")
                    if execution_plan:
                        print("第一行执行计划:")
                        for key, value in execution_plan[0].items():
                            print(f"  {key}: {value}")
                elif isinstance(execution_plan, dict):
                    print("执行计划内容:")
                    for key, value in execution_plan.items():
                        print(f"  {key}: {value}")
            else:
                print(f"消息: {result.get('message', '无消息')}")
                if 'error' in result:
                    print(f"错误: {result['error']}")
    
    except Exception as e:
        print(f"测试执行计划获取时发生错误: {str(e)}")

def test_non_dml_sql():
    """测试非DML语句的执行计划获取"""
    print("\n\n测试非DML语句的执行计划获取")
    print("=" * 80)
    
    try:
        # 加载配置
        config = ConfigManager('config/config.ini')
        
        # 创建元数据收集器
        collector = MetadataCollector(config)
        
        # 测试非DML SQL
        non_dml_sqls = [
            {
                "sql": "CREATE TABLE test_table (id INT PRIMARY KEY, name VARCHAR(100))",
                "description": "创建表语句"
            },
            {
                "sql": "ALTER TABLE test_table ADD COLUMN email VARCHAR(100)",
                "description": "修改表语句"
            },
            {
                "sql": "DROP TABLE test_table",
                "description": "删除表语句"
            },
            {
                "sql": "GRANT SELECT ON test_table TO user1",
                "description": "授权语句"
            },
            {
                "sql": "COMMIT",
                "description": "提交事务语句"
            }
        ]
        
        # 使用测试数据库别名
        db_alias = "db_production"
        
        for i, test_case in enumerate(non_dml_sqls, 1):
            print(f"\n测试 {i}: {test_case['description']}")
            print(f"SQL: {test_case['sql']}")
            
            # 获取执行计划
            result = collector.get_execution_plan(db_alias, test_case['sql'])
            
            print(f"SQL类型: {result.get('sql_type', 'UNKNOWN')}")
            print(f"是否有执行计划: {result.get('has_execution_plan', False)}")
            print(f"消息: {result.get('message', '无消息')}")
    
    except Exception as e:
        print(f"测试非DML语句时发生错误: {str(e)}")

def test_integration_with_dynamic_sql():
    """测试与动态SQL生成的集成"""
    print("\n\n测试与动态SQL生成的集成")
    print("=" * 80)
    
    try:
        # 加载配置
        config = ConfigManager('config/config.ini')
        
        # 创建SQL提取器
        extractor = SQLExtractor(config)
        
        # 测试带参数的SQL - 使用实际存在的表和列
        test_sql = "SELECT * FROM am_solline_info WHERE ID = #{id} AND PROJECTID = #{project}"
        
        print(f"原始SQL: {test_sql}")
        
        # 生成替换参数后的SQL
        replaced_sql, tables = extractor.generate_replaced_sql(test_sql)
        
        print(f"替换后SQL: {replaced_sql}")
        print(f"涉及的表: {tables}")
        
        # 创建元数据收集器
        collector = MetadataCollector(config)
        
        # 获取执行计划
        db_alias = "db_production"
        result = collector.get_execution_plan(db_alias, replaced_sql)
        
        print(f"SQL类型: {result.get('sql_type', 'UNKNOWN')}")
        print(f"是否有执行计划: {result.get('has_execution_plan', False)}")
        
        if result.get('has_execution_plan'):
            execution_plan = result.get('execution_plan', {})
            print(f"执行计划获取成功，类型: {type(execution_plan)}")
            if isinstance(execution_plan, list) and execution_plan:
                print("第一行执行计划:")
                for key, value in execution_plan[0].items():
                    print(f"  {key}: {value}")
        else:
            print(f"消息: {result.get('message', '无消息')}")
            if 'error' in result:
                print(f"错误: {result['error']}")
    
    except Exception as e:
        print(f"测试集成时发生错误: {str(e)}")

def main():
    """主函数"""
    print("执行计划获取功能测试")
    print("=" * 80)
    
    test_sql_type_detection()
    test_execution_plan_for_dml()
    test_non_dml_sql()
    test_integration_with_dynamic_sql()
    
    print("\n" + "=" * 80)
    print("测试完成")

if __name__ == '__main__':
    main()
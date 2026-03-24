#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试修复后的表名提取器
"""

import sys
import os

# 添加路径
sys.path.append('e:/Code/sqlAnalize/sql_ai_analyzer')

from data_collector.sql_extractor import SQLExtractor
from config.config_manager import ConfigManager
from utils.logger import setup_logger

def test_table_extraction():
    """测试表名提取"""
    print("测试表名提取修复")
    print("=" * 60)
    
    config = ConfigManager()
    logger = setup_logger('test_fixed', {'log_level': 'INFO'})
    extractor = SQLExtractor(config, logger)
    
    # 测试各种SQL
    test_cases = [
        {
            'sql': "SELECT * FROM users WHERE id = #{id}",
            'table_field': None,
            'expected': ['users']
        },
        {
            'sql': "SELECT * FROM db1.users WHERE id = #{id}",
            'table_field': None,
            'expected': ['db1.users']  # 注意：现在保留数据库前缀
        },
        {
            'sql': "SELECT a.* FROM table1 a JOIN table2 b ON a.id = b.ref_id",
            'table_field': None,
            'expected': ['table1', 'table2']
        },
        {
            'sql': "UPDATE products SET price = #{price}",
            'table_field': None,
            'expected': ['products']
        },
        {
            'sql': "INSERT INTO orders VALUES (#{id}, #{name})",
            'table_field': None,
            'expected': ['orders']
        },
        {
            'sql': "DELETE FROM logs WHERE id = #{id}",
            'table_field': None,
            'expected': ['logs']
        },
        {
            'sql': "SELECT * FROM `special-table`",
            'table_field': None,
            'expected': ['special-table']  # 移除反引号
        },
        {
            'sql': "SELECT * FROM 'another-table'",
            'table_field': None,
            'expected': ['another-table']  # 移除单引号
        },
        {
            'sql': "WITH cte AS (SELECT * FROM temp) SELECT * FROM cte",
            'table_field': None,
            'expected': []  # CTE暂时无法提取
        },
    ]
    
    all_passed = True
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n测试用例 {i}:")
        print(f"SQL: {test_case['sql'][:80]}...")
        
        tables = extractor.extract_table_names(
            test_case['sql'], 
            test_case['table_field']
        )
        
        print(f"提取结果: {tables}")
        print(f"期望结果: {test_case['expected']}")
        
        # 简单的比较（顺序可能不同）
        if set(tables) == set(test_case['expected']):
            print("✓ 通过")
        else:
            print("✗ 失败")
            all_passed = False
        
        # 检查表名类型
        for table in tables:
            if not isinstance(table, str):
                print(f"  警告: 表名不是字符串类型: {type(table)} = {table}")
                all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("所有测试通过!")
    else:
        print("部分测试失败")
    
    return all_passed

def test_table_field_parsing():
    """测试表名字段解析"""
    print("\n\n测试表名字段解析")
    print("=" * 60)
    
    config = ConfigManager()
    logger = setup_logger('test_field', {'log_level': 'INFO'})
    extractor = SQLExtractor(config, logger)
    
    test_cases = [
        ("users", ["users"]),
        ("users,orders", ["users", "orders"]),
        ("users;products", ["users", "products"]),
        ("users products", ["users", "products"]),
        ("users, orders, products", ["users", "orders", "products"]),
        (None, []),  # 测试None情况
        ("", []),    # 测试空字符串
        ("  ", []),  # 测试空白字符串
    ]
    
    all_passed = True
    
    for field_value, expected in test_cases:
        print(f"\n表名字段: {repr(field_value)}")
        
        try:
            tables = extractor.get_table_names_from_field(field_value)
            print(f"解析结果: {tables}")
            print(f"期望结果: {expected}")
            
            if tables == expected:
                print("✓ 通过")
            else:
                print("✗ 失败")
                all_passed = False
        except Exception as e:
            print(f"✗ 异常: {str(e)}")
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("表名字段解析测试通过!")
    else:
        print("表名字段解析测试失败")
    
    return all_passed

def main():
    """主函数"""
    print("测试修复后的表名提取器")
    print("=" * 60)
    
    test1_passed = test_table_extraction()
    test2_passed = test_table_field_parsing()
    
    print("\n" + "=" * 60)
    print("测试总结:")
    print(f"表名提取测试: {'通过' if test1_passed else '失败'}")
    print(f"表名字段解析测试: {'通过' if test2_passed else '失败'}")
    
    if test1_passed and test2_passed:
        print("\n所有测试通过!")
        return True
    else:
        print("\n部分测试失败，需要进一步调试")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
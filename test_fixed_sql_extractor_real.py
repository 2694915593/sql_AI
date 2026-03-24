#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试修复后的SQL提取器
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'sql_ai_analyzer'))

from sql_ai_analyzer.data_collector.sql_extractor import SQLExtractor
from sql_ai_analyzer.config.config_manager import ConfigManager

def test_extractor_with_complex_sql():
    """测试修复后的提取器"""
    print("测试修复后的SQL提取器")
    print("=" * 60)
    
    # 模拟配置管理器
    class MockConfigManager:
        def get_database_config(self):
            return {
                'host': 'localhost',
                'port': 3306,
                'user': 'test',
                'password': 'test',
                'database': 'test'
            }
    
    # 创建模拟日志器
    import logging
    logging.basicConfig(level=logging.WARNING)
    
    # 创建提取器
    config_manager = MockConfigManager()
    extractor = SQLExtractor(config_manager)
    
    # 用户提供的SQL（有问题的SQL）
    sql = """SELECT EVI_PLATENUM "PLATENUM", EVI_PLATECOLOR "PLATECOLOR", EVI_VIN "VIN", EVI_ENGINENUM "ENGINENUM", EVI_ISSUEDATE "ISSUEDATE", EVI_VEHICLEHOSTNAME "VEHICLEHOSTNAME", EVI_REGISTERDATE "REGISTERDATE", EVI_USECHARACTER "USECHARACTER", EVI_VEHICLETYPE "VEHICLETYPE", EVI_VEHICLESTDTYPE "VEHICLESTDTYPE", EVI_SECPLATENUM "SECPLATENUM", EVI_FILENUM "FILENUM", EVI_APPROVEDCOUNT "APPROVEDCOUNT", EVI_TOTALMASS "TOTALMASS", EVI_MAINTENACEMASS "MAINTENACEMASS", EVI_PERMITTEDWEIGHT "PERMITTEDWEIGHT", EVI_OUTSIDEDIMENSIONS "OUTSIDEDIMENSIONS", EVI_PERMITTEDTOWWEIGHT "PERMITTEDTOWWEIGHT", EVI_VEHICLEDOCID "VEHICLEDOCID", EVI_RMK1 "RMK1", EVI_RMK2 "RMK2", EII_OBUID "OBUID", EII_ETCCARDNO "ETCCARDNO", EAI_STATUS "SIGNSTT" FROM ( SELECT * FROM ( SELECT EAI_PLATENUM, EAI_PLATECOLOR, EAI_STATUS FROM BR_ETC_AGREEMENT_INFO WHERE EAI_AGREEMENTNUM = #{AGREEMENTNUM} ) A, BR_ETC_VEHICLE_INFO B WHERE A.EAI_PLATENUM = B.EVI_PLATENUM AND A.EAI_PLATECOLOR = B.EVI_PLATECOLOR ) C LEFT JOIN BR_ETC_ISSUE_INFO D ON C.EAI_PLATENUM = D.EII_PLATENUM AND C.EAI_PLATECOLOR = .EII_PLATECOLOR"""
    
    print(f"SQL长度: {len(sql)} 字符")
    print(f"SQL预览:\n{sql[:300]}...\n")
    
    # 提取表名
    tables = extractor.extract_table_names(sql)
    print(f"提取到的表名: {sorted(tables)}")
    
    # 预期的表名
    expected_tables = [
        'BR_ETC_AGREEMENT_INFO',
        'BR_ETC_VEHICLE_INFO', 
        'BR_ETC_ISSUE_INFO'
    ]
    print(f"预期表名: {sorted(expected_tables)}")
    
    # 检查结果
    missing = [t for t in expected_tables if t not in tables]
    extra = [t for t in tables if t not in expected_tables]
    
    print("\n" + "=" * 60)
    print("结果分析:")
    
    if not missing and not extra:
        print("✓ 修复成功！表名提取正确")
        print(f"  找到的表名: {sorted(tables)}")
    else:
        print("✗ 表名提取仍有问题")
        if missing:
            print(f"  缺失的表名: {missing}")
        if extra:
            print(f"  多余的表名: {extra}")
    
    # 测试其他复杂SQL
    print("\n" + "=" * 60)
    print("测试其他复杂SQL:")
    
    # 测试1: 子查询中的表名
    sql1 = """SELECT * FROM (SELECT * FROM users WHERE id = 1) t"""
    tables1 = extractor.extract_table_names(sql1)
    print(f"SQL1: 简单子查询")
    print(f"  提取表名: {tables1}")
    print(f"  预期表名: ['users']")
    print(f"  结果: {'正确' if 'users' in tables1 else '错误'}")
    
    # 测试2: 逗号分隔的表名
    sql2 = """SELECT a.*, b.* FROM table1 a, table2 b WHERE a.id = b.id"""
    tables2 = extractor.extract_table_names(sql2)
    print(f"\nSQL2: 逗号分隔的表名")
    print(f"  提取表名: {sorted(tables2)}")
    print(f"  预期表名: ['table1', 'table2']")
    print(f"  结果: {'正确' if set(['table1', 'table2']) == set(tables2) else '错误'}")
    
    # 测试3: JOIN 表名
    sql3 = """SELECT * FROM table1 t1 INNER JOIN table2 t2 ON t1.id = t2.id LEFT JOIN table3 t3 ON t2.id = t3.id"""
    tables3 = extractor.extract_table_names(sql3)
    print(f"\nSQL3: 多表JOIN")
    print(f"  提取表名: {sorted(tables3)}")
    print(f"  预期表名: ['table1', 'table2', 'table3']")
    print(f"  结果: {'正确' if set(['table1', 'table2', 'table3']) == set(tables3) else '错误'}")
    
    # 测试4: 带括号的子查询（原来的问题）
    sql4 = """SELECT * FROM (SELECT * FROM (SELECT * FROM main_table WHERE id = 1) t1, other_table t2 WHERE t1.id = t2.id) t3"""
    tables4 = extractor.extract_table_names(sql4)
    print(f"\nSQL4: 多层嵌套子查询")
    print(f"  提取表名: {sorted(tables4)}")
    print(f"  预期表名: ['main_table', 'other_table']")
    print(f"  结果: {'正确' if set(['main_table', 'other_table']) == set(tables4) else '错误'}")
    
    return not missing and not extra

def test_extractor_methods_directly():
    """直接测试提取器的方法"""
    print("\n" + "=" * 60)
    print("直接测试提取器方法:")
    
    # 模拟配置管理器
    class MockConfigManager:
        def get_database_config(self):
            return {
                'host': 'localhost',
                'port': 3306,
                'user': 'test',
                'password': 'test',
                'database': 'test'
            }
    
    import logging
    logging.basicConfig(level=logging.WARNING)
    
    config_manager = MockConfigManager()
    extractor = SQLExtractor(config_manager)
    
    # 测试_is_valid_table_name方法
    print("\n测试_is_valid_table_name方法:")
    
    test_cases = [
        ('users', True),
        ('users_table', True),
        ('db.users', True),
        ('`users`', True),
        ("'users'", True),
        ('"users"', True),
        ('(', False),  # 括号不应该被识别为表名
        (')', False),
        ('SELECT', False),  # SQL关键字
        ('FROM', False),
        ('table.column.another', False),  # 多个点号
        ('123table', True),  # 以数字开头，但正则表达式允许
        ('_table', True),  # 以下划线开头
    ]
    
    for table_name, expected in test_cases:
        result = extractor._is_valid_table_name(table_name)
        status = '✓' if result == expected else '✗'
        print(f"  {status} '{table_name}' -> {result} (预期: {expected})")
    
    # 测试_extract_tables_from_from_clause方法
    print("\n测试_extract_tables_from_from_clause方法:")
    
    test_cases = [
        ('users', ['users']),
        ('users u', ['users']),
        ('users AS u', ['users']),
        ('users u, products p', ['users', 'products']),
        ('users AS u, products AS p', ['users', 'products']),
        ('db.users u', ['db.users']),
        ('`user-table` u', ['user-table']),
    ]
    
    for from_clause, expected in test_cases:
        tables = []
        extractor._extract_tables_from_from_clause(from_clause, tables)
        status = '✓' if set(tables) == set(expected) else '✗'
        print(f"  {status} FROM {from_clause} -> {tables} (预期: {expected})")

def main():
    """主函数"""
    print("测试修复后的SQL提取器")
    print("=" * 60)
    
    # 测试复杂的SQL提取
    success1 = test_extractor_with_complex_sql()
    
    # 直接测试提取器方法
    test_extractor_methods_directly()
    
    print("\n" + "=" * 60)
    print("总结:")
    print("1. 修复的主要问题:")
    print("   - 当FROM后面是括号时，错误地将'('提取为表名")
    print("   - 没有正确处理逗号分隔的表名（FROM A, B WHERE）")
    print("   - 提取到列名（如EAI_PLATECOLOR）而不是表名")
    print("2. 修复方案:")
    print("   - 添加了_is_valid_table_name方法过滤无效表名")
    print("   - 改进了正则表达式，跳过子查询括号")
    print("   - 专门处理逗号分隔的表名格式")
    print("3. 修复效果:")
    print("   - 现在能正确提取嵌套子查询中的表名")
    print("   - 过滤掉括号和列名等无效标识符")
    print("   - 正确处理复杂SQL结构")
    
    return success1

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
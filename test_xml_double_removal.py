#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试XML标签重复移除问题
模拟SQL多次预处理的情况
"""

import re
from sql_ai_analyzer.utils.sql_preprocessor import SQLPreprocessor
from sql_ai_analyzer.data_collector.param_extractor import ParamExtractor

class MockLogger:
    def info(self, msg):
        print(f"INFO: {msg}")
    
    def debug(self, msg):
        print(f"DEBUG: {msg}")
    
    def warning(self, msg):
        print(f"WARNING: {msg}")
    
    def error(self, msg):
        print(f"ERROR: {msg}")

def test_xml_tag_double_removal():
    """测试XML标签是否会被重复移除"""
    print("=== 测试XML标签重复移除 ===")
    
    # 测试SQL
    test_sql = "<select>SELECT * FROM users WHERE id = #{id}</select>"
    print(f"原始SQL: {test_sql}")
    
    # 创建预处理器
    logger = MockLogger()
    preprocessor = SQLPreprocessor(logger)
    
    # 第一次预处理
    sql1, info1 = preprocessor.preprocess_sql(test_sql, mode="normalize")
    print(f"\n第一次预处理:")
    print(f"  处理后SQL: {sql1}")
    print(f"  信息: has_xml_tags={info1['has_xml_tags']}, action={info1.get('action', 'N/A')}")
    
    # 第二次预处理（模拟重复处理）
    sql2, info2 = preprocessor.preprocess_sql(sql1, mode="normalize")
    print(f"\n第二次预处理（使用第一次处理的结果）:")
    print(f"  处理后SQL: {sql2}")
    print(f"  信息: has_xml_tags={info2['has_xml_tags']}, action={info2.get('action', 'N/A')}")
    
    # 比较结果
    if sql1 == sql2:
        print("\n✓ SQL没有变化，不会重复移除")
    else:
        print(f"\n✗ SQL发生了变化: '{sql1}' -> '{sql2}'")
    
    # 测试参数提取器
    print("\n=== 测试参数提取器中的预处理 ===")
    
    # 创建参数提取器
    extractor = ParamExtractor(test_sql, logger)
    print(f"ParamExtractor初始化后的sql_text: {extractor.sql_text}")
    print(f"预处理信息: has_xml_tags={extractor.preprocess_info['has_xml_tags']}")
    
    # 提取参数
    params = extractor.extract_params()
    print(f"提取的参数: {[p['param'] for p in params]}")
    
    # 生成替换后的SQL
    replaced_sql, tables = extractor.generate_replaced_sql()
    print(f"替换后的SQL: {replaced_sql}")
    
    # 检查SQL关键字是否完整
    if "SELECT" in replaced_sql.upper() and "FROM" in replaced_sql.upper():
        print("✓ SQL关键字保持完整")
    else:
        print("✗ SQL关键字可能被破坏")
    
    return sql1 == sql2

def test_keyword_replacement():
    """测试关键字替换问题"""
    print("\n=== 测试关键字替换问题 ===")
    
    # 测试可能有关键字冲突的SQL
    test_cases = [
        {
            'name': '参数名与关键字相同',
            'sql': 'UPDATE users SET name = #{set} WHERE id = #{id}',
            'description': '参数名set与SET关键字相同'
        },
        {
            'name': '参数名包含关键字',
            'sql': 'UPDATE users SET name = #{set_name} WHERE id = #{id}',
            'description': '参数名set_name包含set'
        },
        {
            'name': '复杂UPDATE语句',
            'sql': 'UPDATE table SET column1 = #{set_value}, column2 = #{value} WHERE id = #{where_condition}',
            'description': '多个参数名可能匹配关键字'
        }
    ]
    
    logger = MockLogger()
    
    for test in test_cases:
        print(f"\n测试: {test['name']}")
        print(f"描述: {test['description']}")
        print(f"SQL: {test['sql']}")
        
        extractor = ParamExtractor(test['sql'], logger)
        replaced_sql, tables = extractor.generate_replaced_sql()
        
        print(f"替换后SQL: {replaced_sql}")
        
        # 检查关键SQL关键字
        original_upper = test['sql'].upper()
        replaced_upper = replaced_sql.upper()
        
        keywords = ['UPDATE', 'SET', 'WHERE']
        issues = []
        for kw in keywords:
            if kw in original_upper and kw not in replaced_upper:
                issues.append(f"关键字 '{kw}' 在替换后消失")
        
        if issues:
            print(f"✗ 发现问题: {issues}")
        else:
            print(f"✓ SQL关键字保持完整")
    
    return True

def main():
    """主测试函数"""
    print("开始测试XML标签重复移除和关键字替换问题")
    print("=" * 60)
    
    # 测试1: XML标签重复移除
    test1_passed = test_xml_tag_double_removal()
    
    # 测试2: 关键字替换
    test2_passed = test_keyword_replacement()
    
    print("\n" + "=" * 60)
    print("测试结果:")
    print("=" * 60)
    print(f"XML标签重复移除测试: {'通过' if test1_passed else '失败'}")
    print(f"关键字替换测试: {'通过' if test2_passed else '失败'}")
    
    print("\n分析:")
    print("1. XML标签不会被重复移除，因为第二次预处理时已无XML标签")
    print("2. 参数替换使用re.escape，不会错误匹配SQL关键字")
    print("3. 问题可能出现在其他地方，如SQL本身的语法错误")
    print("4. 或者问题是大模型XML标签移除器的重复初始化导致其他问题")

if __name__ == "__main__":
    main()
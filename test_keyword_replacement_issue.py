#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试SQL关键字替换问题
发现参数替换过程会错误地替换SQL关键字
"""

import re
import sys
import os

# 模拟LogMixin
class LogMixin:
    def __init__(self):
        self.logger = self
    
    def set_logger(self, logger):
        self.logger = logger
    
    def info(self, msg):
        print(f"INFO: {msg}")
    
    def debug(self, msg):
        print(f"DEBUG: {msg}")
    
    def warning(self, msg):
        print(f"WARNING: {msg}")
    
    def error(self, msg):
        print(f"ERROR: {msg}")

class SQLPreprocessor:
    def __init__(self, logger=None):
        self.logger = logger
    
    def preprocess_sql(self, sql_text, mode="normalize"):
        return sql_text, {'has_xml_tags': False, 'processed_length': len(sql_text), 'original_length': len(sql_text)}

# 模拟模块导入
sys.modules['utils.logger'] = type(sys)('utils.logger')
sys.modules['utils.logger'].LogMixin = LogMixin
sys.modules['utils.sql_preprocessor'] = type(sys)('utils.sql_preprocessor')
sys.modules['utils.sql_preprocessor'].SQLPreprocessor = SQLPreprocessor

# 导入ParamExtractor
from sql_ai_analyzer.data_collector.param_extractor import ParamExtractor

def test_keyword_replacement_issue():
    """测试SQL关键字被错误替换的问题"""
    print("=== 测试SQL关键字替换问题 ===")
    print()
    
    test_cases = [
        {
            'name': 'UPDATE语句，参数名包含"set"',
            'sql': 'UPDATE users SET name = #{set_name} WHERE id = #{id}',
            'description': '参数名set_name可能被错误匹配到SET关键字'
        },
        {
            'name': 'UPDATE语句，参数名就是"set"',
            'sql': 'UPDATE users SET name = #{set} WHERE id = #{id}',
            'description': '参数名set可能与SET关键字冲突'
        },
        {
            'name': 'WHERE子句，参数名包含"where"',
            'sql': 'SELECT * FROM users WHERE id = #{where_id}',
            'description': '参数名where_id可能被错误匹配'
        },
        {
            'name': '复杂UPDATE语句，参数名可能匹配多个关键字',
            'sql': 'UPDATE table SET column1 = #{set_value}, column2 = #{value} WHERE id = #{where_condition} AND status = #{set_status}',
            'description': '多个参数名可能匹配SQL关键字'
        },
        {
            'name': '用户提供的例子 - UPDATE语句缺少SET关键字',
            'sql': 'UPDATE MONTHLY_TRAN_MSG MTM_SEND =#{send,jdbcType=VARCHAR}, MTM_PARTY_NAME =#{partyName,jdbcType=VARCHAR} WHERE MTM_PARTY_NO =#{partyNo,jdbcType=VARCHAR}',
            'description': '这个SQL本身缺少SET关键字，参数替换可能会进一步破坏语法'
        }
    ]
    
    all_passed = True
    
    for i, test in enumerate(test_cases, 1):
        print(f"测试 {i}: {test['name']}")
        print(f"描述: {test['description']}")
        print(f"原始SQL: {test['sql'][:80]}...")
        
        try:
            # 创建参数提取器
            extractor = ParamExtractor(test['sql'])
            
            # 提取参数
            params = extractor.extract_params()
            param_names = [p['param'] for p in params]
            print(f"提取的参数: {param_names}")
            
            # 生成替换后的SQL
            replaced_sql, tables = extractor.generate_replaced_sql()
            print(f"替换后SQL: {replaced_sql[:100]}...")
            
            # 检查SQL关键字是否被破坏
            original_upper = test['sql'].upper()
            replaced_upper = replaced_sql.upper()
            
            # 检查关键SQL关键字
            sql_keywords = ['SELECT', 'FROM', 'WHERE', 'UPDATE', 'SET', 'INSERT', 'INTO', 'VALUES', 'DELETE']
            issues = []
            
            for keyword in sql_keywords:
                # 检查原始SQL中是否有关键字
                if keyword in original_upper:
                    # 检查替换后是否还有这个关键字
                    if keyword not in replaced_upper:
                        issues.append(f"关键字 '{keyword}' 在替换后消失")
                    # 检查关键字是否被部分替换
                    original_parts = original_upper.split(keyword)
                    replaced_parts = replaced_upper.split(keyword)
                    if len(original_parts) > len(replaced_parts):
                        issues.append(f"关键字 '{keyword}' 可能被部分替换")
            
            if issues:
                print(f"✗ 发现关键字替换问题:")
                for issue in issues:
                    print(f"   - {issue}")
                all_passed = False
            else:
                print(f"✓ SQL关键字保持完整")
            
            # 检查是否还有未替换的参数
            param_pattern = r'#\{([^}]+)\}'
            remaining_params = re.findall(param_pattern, replaced_sql)
            
            if remaining_params:
                print(f"✗ 仍有未替换的参数: {remaining_params}")
                all_passed = False
            else:
                print(f"✓ 所有参数都已替换")
            
            # 检查SQL语法基本结构
            if 'UPDATE' in original_upper and 'SET' not in replaced_upper:
                print(f"⚠️ 警告: UPDATE语句缺少SET关键字")
                # 尝试修复
                fixed_sql = re.sub(r'UPDATE\s+(\w+)\s+(\w+=)', r'UPDATE \1 SET \2', replaced_sql, flags=re.IGNORECASE)
                if 'SET' in fixed_sql.upper():
                    print(f"  可以自动修复: {fixed_sql[:100]}...")
            
            print()
            
        except Exception as e:
            print(f"✗ 测试失败: {str(e)}")
            import traceback
            traceback.print_exc()
            all_passed = False
            print()
    
    return all_passed

def analyze_replacement_logic():
    """分析替换逻辑的问题"""
    print("\n=== 分析参数替换逻辑 ===")
    print()
    
    # 创建测试SQL
    test_sql = 'UPDATE users SET name = #{set} WHERE id = #{id}'
    print(f"测试SQL: {test_sql}")
    
    # 手动模拟替换过程
    param_pattern = r'#\{([^}]+)\}'
    params = re.findall(param_pattern, test_sql)
    print(f"提取的参数: {params}")
    
    # 模拟ParamExtractor的替换逻辑
    replaced_sql = test_sql
    for param_name in params:
        # 模拟_get_preset_value方法
        if param_name == 'set':
            # 根据_param_matches_column逻辑，'set'可能被识别为字符串类型
            replaced_value = "'test_value'"
        elif param_name == 'id':
            replaced_value = "123"
        else:
            replaced_value = "'test_value'"
        
        print(f"参数 '{param_name}' 将被替换为: {replaced_value}")
        
        # 使用re.escape确保只替换准确的参数占位符
        escaped_pattern = re.escape(f"#{{{param_name}}}")
        replaced_sql = re.sub(escaped_pattern, replaced_value, replaced_sql)
    
    print(f"替换后SQL: {replaced_sql}")
    
    # 检查问题
    if 'SET' not in replaced_sql.upper():
        print("✗ 问题发现: SET关键字被错误替换!")
        # 分析原因
        # 当param_name='set'时，替换模式是"#{set}"，这可能会匹配:
        # 1. " SET " 中的 "SET"（不匹配，因为大小写不同）
        # 2. 但re.sub是大小写敏感的，所以不会匹配"SET"
        # 3. 除非原始SQL中是"#{set}"，这会被正确替换
        
    else:
        print("✓ SET关键字保持完整")
    
    print()
    
    # 测试另一个问题：参数名包含关键字
    test_sql2 = 'UPDATE users SET name = #{set_name} WHERE id = #{id}'
    print(f"测试SQL2: {test_sql2}")
    
    params2 = re.findall(param_pattern, test_sql2)
    print(f"提取的参数: {params2}")
    
    replaced_sql2 = test_sql2
    for param_name in params2:
        if param_name == 'set_name':
            replaced_value = "'john'"
        elif param_name == 'id':
            replaced_value = "123"
        
        escaped_pattern = re.escape(f"#{{{param_name}}}")
        replaced_sql2 = re.sub(escaped_pattern, replaced_value, replaced_sql2)
    
    print(f"替换后SQL2: {replaced_sql2}")
    
    # 检查是否有问题
    if 'SET_NAME' in replaced_sql2.upper() or 'SET' not in replaced_sql2.upper():
        print("✗ 可能的问题: 参数名包含'set'但不会影响SET关键字")
    else:
        print("✓ SQL结构正常")
    
    print()

def test_regex_escaping():
    """测试正则表达式转义问题"""
    print("\n=== 测试正则表达式转义 ===")
    print()
    
    test_cases = [
        ('#{set}', "UPDATE users SET name = #{set}"),
        ('#{set_name}', "UPDATE users SET name = #{set_name}"),
        ('#{where}', "SELECT * FROM users WHERE id = #{where}"),
        ('#{where_id}', "SELECT * FROM users WHERE id = #{where_id}"),
    ]
    
    for param_pattern, sql in test_cases:
        print(f"测试: {sql}")
        print(f"参数模式: {param_pattern}")
        
        # 测试是否会被错误匹配
        escaped_pattern = re.escape(param_pattern)
        print(f"转义后的模式: {escaped_pattern}")
        
        # 测试在SQL中查找
        match = re.search(escaped_pattern, sql)
        if match:
            print(f"✓ 正确匹配到参数: {match.group()}")
        else:
            print(f"✗ 未找到参数")
        
        # 测试是否会错误匹配关键字
        keyword_test = "UPDATE users SET name = 'test'"
        false_match = re.search(escaped_pattern, keyword_test)
        if false_match:
            print(f"⚠️ 警告: 错误匹配到关键字! 匹配到: {false_match.group()}")
        else:
            print(f"✓ 不会错误匹配关键字")
        
        print()

def main():
    """主测试函数"""
    print("开始测试SQL关键字替换问题")
    print("=" * 60)
    
    # 运行测试
    test_results = []
    
    # 测试1: 关键字替换问题
    print("\n[测试1] SQL关键字替换问题测试")
    result1 = test_keyword_replacement_issue()
    test_results.append(("关键字替换问题", result1))
    
    # 测试2: 分析替换逻辑
    print("\n[测试2] 替换逻辑分析")
    analyze_replacement_logic()
    
    # 测试3: 正则表达式转义测试
    print("\n[测试3] 正则表达式转义测试")
    test_regex_escaping()
    
    # 输出测试结果摘要
    print("\n" + "=" * 60)
    print("测试结果摘要:")
    print("=" * 60)
    
    all_passed = True
    for test_name, result in test_results:
        status = "通过" if result else "失败"
        all_passed = all_passed and result
        print(f"{test_name}: {status}")
    
    print("\n总体结果:", "所有测试通过" if all_passed else "有测试失败")
    
    print("\n" + "=" * 60)
    print("问题分析:")
    print("=" * 60)
    print("1. 参数替换使用 re.sub(re.escape(pattern), value, sql) 方法")
    print("2. re.escape确保只替换准确的参数占位符，不会错误匹配关键字")
    print("3. 问题可能出现在其他地方，如SQL预处理或关键字修复逻辑")
    print("4. 或者问题可能是参数值本身包含特殊字符，导致SQL语法错误")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
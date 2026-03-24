#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试参数替换功能，验证是否所有参数都被正确替换
"""

import sys
import os
import re

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 模拟缺失的模块
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

# 模拟配置管理器
class MockConfigManager:
    def __init__(self):
        pass
    
    def get_all_target_db_aliases(self):
        return ['test_db']
    
    def get_target_database_config(self, db_alias):
        return {
            'host': 'localhost',
            'port': 3306,
            'user': 'test',
            'password': 'test',
            'database': 'test'
        }
    
    def get_optimization_config(self):
        return {
            'enable_data_fetching': False,  # 测试中禁用数据获取，使用默认值
            'max_sample_size': 100,
            'use_cache': True
        }

# 模拟数据库连接器
class MockDatabaseManager:
    def __init__(self, db_config):
        pass
    
    def fetch_one(self, query):
        return {}
    
    def fetch_all(self, query):
        return []

# 模拟数据值获取器
class MockDataValueFetcher:
    def __init__(self, config_manager, logger=None):
        self.config_manager = config_manager
        self.logger = logger
        self.enable_data_fetching = False
    
    def find_matching_column(self, db_alias, table_name, param_name, metadata_list):
        # 返回一个匹配的列
        return table_name, param_name, {'name': param_name, 'type': 'varchar(255)'}
    
    def get_replacement_value(self, db_alias, table_name, column_name, column_type):
        # 根据列类型返回默认值
        column_type_lower = column_type.lower()
        if 'int' in column_type_lower or 'decimal' in column_type_lower or 'float' in column_type_lower:
            return 123
        elif 'date' in column_type_lower or 'time' in column_type_lower:
            return "'2025-01-01 00:00:00'"
        elif 'bool' in column_type_lower or 'bit' in column_type_lower:
            return 1
        else:
            return "'test_value'"
    
    def fetch_column_values(self, db_alias, table_name, column_name, column_type):
        return {}

# 添加模拟模块到sys.modules
sys.modules['utils.logger'] = type(sys)('utils.logger')
sys.modules['utils.logger'].LogMixin = LogMixin
sys.modules['utils.sql_preprocessor'] = type(sys)('utils.sql_preprocessor')
sys.modules['utils.sql_preprocessor'].SQLPreprocessor = SQLPreprocessor

# 替换DataValueFetcher模块
sys.modules['sql_ai_analyzer.data_collector.data_value_fetcher'] = type(sys)('sql_ai_analyzer.data_collector.data_value_fetcher')
sys.modules['sql_ai_analyzer.data_collector.data_value_fetcher'].DataValueFetcher = MockDataValueFetcher

from sql_ai_analyzer.data_collector.param_extractor import ParamExtractor

def test_param_replacement():
    """测试参数替换功能"""
    print("=== 测试参数替换功能 ===")
    
    # 创建模拟配置管理器
    config_manager = MockConfigManager()
    
    # 创建模拟元数据
    metadata_list = [
        {
            'table_name': 'users',
            'columns': [
                {'name': 'id', 'type': 'int'},
                {'name': 'name', 'type': 'varchar(255)'},
                {'name': 'status', 'type': 'int'}
            ]
        },
        {
            'table_name': 'orders',
            'columns': [
                {'name': 'order_id', 'type': 'int'},
                {'name': 'customer_id', 'type': 'int'},
                {'name': 'amount', 'type': 'decimal(10,2)'}
            ]
        },
        {
            'table_name': 'products',
            'columns': [
                {'name': 'id', 'type': 'int'},
                {'name': 'price', 'type': 'decimal(10,2)'},
                {'name': 'stock', 'type': 'int'}
            ]
        },
        {
            'table_name': 'logs',
            'columns': [
                {'name': 'user_id', 'type': 'int'},
                {'name': 'action', 'type': 'varchar(255)'}
            ]
        }
    ]
    
    test_cases = [
        {
            'name': '多个参数替换',
            'sql': 'SELECT * FROM users WHERE id = #{id} AND name = #{name} AND status = #{status}',
            'expected_params': ['id', 'name', 'status']
        },
        {
            'name': 'INSERT语句参数替换',
            'sql': 'INSERT INTO orders (order_id, customer_id, amount) VALUES (#{order_id}, #{customer_id}, #{amount})',
            'expected_params': ['order_id', 'customer_id', 'amount']
        },
        {
            'name': 'UPDATE语句参数替换',
            'sql': 'UPDATE products SET price = #{price}, stock = #{stock} WHERE id = #{id}',
            'expected_params': ['price', 'stock', 'id']
        },
        {
            'name': 'DELETE语句参数替换',
            'sql': 'DELETE FROM logs WHERE user_id = #{user_id} AND action = #{action}',
            'expected_params': ['user_id', 'action']
        }
    ]
    
    all_passed = True
    
    for test_case in test_cases:
        print(f"\n--- {test_case['name']} ---")
        print(f"原始SQL: {test_case['sql']}")
        
        try:
            # 创建参数提取器（传递config_manager和metadata_list）
            extractor = ParamExtractor(test_case['sql'], config_manager=config_manager, metadata_list=metadata_list)
            
            # 提取参数
            params = extractor.extract_params()
            extracted_param_names = [p['param'] for p in params]
            print(f"提取的参数: {extracted_param_names}")
            
            # 检查参数提取是否正确
            if set(extracted_param_names) == set(test_case['expected_params']):
                print("✓ 参数提取正确")
            else:
                print(f"✗ 参数提取错误，期望: {test_case['expected_params']}，实际: {extracted_param_names}")
                all_passed = False
            
            # 生成替换后的SQL
            replaced_sql, tables = extractor.generate_replaced_sql()
            print(f"替换后SQL: {replaced_sql}")
            
            # 检查是否还有未替换的参数
            param_pattern = r'#\{([^}]+)\}'
            remaining_params = re.findall(param_pattern, replaced_sql)
            
            if not remaining_params:
                print("✓ 所有参数都已成功替换")
            else:
                print(f"✗ 仍有未替换的参数: {remaining_params}")
                all_passed = False
            
            # 检查替换后的值是否正确
            # 对于没有元数据和配置管理器的情况，应该使用预设值
            for param in test_case['expected_params']:
                if f'#{{{param}}}' in replaced_sql:
                    print(f"✗ 参数 {param} 未被替换")
                    all_passed = False
            
            # 检查替换值类型
            # 数字参数应该被替换为数字
            if 'id' in extracted_param_names:
                # 检查是否替换为数字
                if "'123'" in replaced_sql or "123" in replaced_sql:
                    print("✓ 数字参数正确替换")
                else:
                    print("✗ 数字参数替换值类型可能不正确")
            
            # 字符串参数应该被替换为带引号的字符串
            if 'name' in extracted_param_names:
                if "'test_value'" in replaced_sql:
                    print("✓ 字符串参数正确替换")
                else:
                    print("✗ 字符串参数替换值类型可能不正确")
                    
        except Exception as e:
            print(f"✗ 测试失败: {str(e)}")
            import traceback
            traceback.print_exc()
            all_passed = False
    
    return all_passed

def test_insert_sql_parsing():
    """测试INSERT语句解析"""
    print("\n\n=== 测试INSERT语句解析 ===")
    
    # 创建模拟配置管理器
    config_manager = MockConfigManager()
    
    # 创建模拟元数据
    metadata_list = [
        {
            'table_name': 'users',
            'columns': [
                {'name': 'id', 'type': 'int'},
                {'name': 'name', 'type': 'varchar(255)'},
                {'name': 'email', 'type': 'varchar(255)'}
            ]
        },
        {
            'table_name': 'products',
            'columns': [
                {'name': 'id', 'type': 'int'},
                {'name': 'name', 'type': 'varchar(255)'},
                {'name': 'price', 'type': 'decimal(10,2)'}
            ]
        },
        {
            'table_name': 'orders',
            'columns': [
                {'name': 'order_id', 'type': 'int'},
                {'name': 'customer_id', 'type': 'int'},
                {'name': 'amount', 'type': 'decimal(10,2)'}
            ]
        },
        {
            'table_name': 'logs',
            'columns': [
                {'name': 'log_id', 'type': 'int'},
                {'name': 'message', 'type': 'varchar(255)'},
                {'name': 'timestamp', 'type': 'datetime'}
            ]
        }
    ]
    
    test_insert_sqls = [
        "INSERT INTO users (id, name, email) VALUES (#{id}, #{name}, #{email})",
        "INSERT INTO products VALUES (#{id}, #{name}, #{price})",
        "INSERT INTO orders(order_id, customer_id, amount) VALUES(#{order_id}, #{customer_id}, #{amount})",
        "INSERT INTO logs VALUES (#{log_id}, #{message}, #{timestamp})"
    ]
    
    all_passed = True
    
    for i, sql in enumerate(test_insert_sqls, 1):
        print(f"\n--- INSERT测试 {i} ---")
        print(f"原始SQL: {sql}")
        
        try:
            # 创建参数提取器（传递config_manager和metadata_list）
            extractor = ParamExtractor(sql, config_manager=config_manager, metadata_list=metadata_list)
            replaced_sql, tables = extractor.generate_replaced_sql()
            print(f"替换后SQL: {replaced_sql}")
            
            # 检查语法是否正确
            # INSERT语句应该以"INSERT INTO"开头
            if replaced_sql.startswith("INSERT INTO"):
                print("✓ INSERT语法结构正确")
            else:
                print("✗ INSERT语法结构可能有问题")
                all_passed = False
            
            # 检查是否有表名
            if tables:
                print(f"✓ 提取到表名: {tables}")
            else:
                print("✗ 未提取到表名")
                all_passed = False
            
            # 检查是否还有未替换的参数
            param_pattern = r'#\{([^}]+)\}'
            remaining_params = re.findall(param_pattern, replaced_sql)
            
            if not remaining_params:
                print("✓ 所有参数都已成功替换")
            else:
                print(f"✗ 仍有未替换的参数: {remaining_params}")
                all_passed = False
                
        except Exception as e:
            print(f"✗ INSERT语句解析失败: {str(e)}")
            import traceback
            traceback.print_exc()
            all_passed = False
    
    return all_passed

def main():
    """主测试函数"""
    print("开始测试参数替换功能")
    print("=" * 60)
    
    # 运行所有测试
    test_results = []
    
    # 测试1: 参数替换
    print("\n[测试1] 参数替换功能测试")
    result1 = test_param_replacement()
    test_results.append(("参数替换功能", result1))
    
    # 测试2: INSERT语句解析
    print("\n[测试2] INSERT语句解析测试")
    result2 = test_insert_sql_parsing()
    test_results.append(("INSERT语句解析", result2))
    
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
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
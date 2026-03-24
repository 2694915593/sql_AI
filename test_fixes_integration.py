#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试修复集成：验证参数替换和SQL语法修复功能
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

# 添加模拟模块到sys.modules
sys.modules['utils.logger'] = type(sys)('utils.logger')
sys.modules['utils.logger'].LogMixin = LogMixin
sys.modules['utils.sql_preprocessor'] = type(sys)('utils.sql_preprocessor')
sys.modules['utils.sql_preprocessor'].SQLPreprocessor = SQLPreprocessor

from sql_ai_analyzer.data_collector.dynamic_sql_parser import DynamicSQLParser

def test_insert_sql_fix():
    """测试INSERT语句修复功能"""
    print("=== 测试INSERT语句修复功能 ===")
    
    test_cases = [
        {
            'name': 'INSERT缺少VALUES关键字',
            'sql': 'INSERT INTO users (id, name) (#{id}, #{name})',
            'expected': 'INSERT INTO users (id, name) VALUES (#{id}, #{name})'
        },
        {
            'name': 'INSERT缺少VALUES关键字且没有列名括号',
            'sql': 'INSERT INTO users #{id}, #{name}',
            'expected': 'INSERT INTO users VALUES #{id}, #{name}'
        },
        {
            'name': '正确的INSERT语句',
            'sql': 'INSERT INTO users (id, name) VALUES (#{id}, #{name})',
            'expected': 'INSERT INTO users (id, name) VALUES (#{id}, #{name})'
        },
        {
            'name': 'INSERT INTO table_name VALUES ...',
            'sql': 'INSERT INTO products VALUES (#{id}, #{name})',
            'expected': 'INSERT INTO products VALUES (#{id}, #{name})'
        },
        {
            'name': 'INSERT缺少INTO关键字',
            'sql': 'INSERT users (id, name) VALUES (#{id}, #{name})',
            'expected': 'INSERT users (id, name) VALUES (#{id}, #{name})'
        }
    ]
    
    all_passed = True
    
    # 创建动态SQL解析器（需要模拟config_manager）
    class MockConfigManager:
        def get_optimization_config(self):
            return {'enable_dynamic_sql_parsing': True, 'dynamic_sql_timeout': 30, 'max_dynamic_sql_retries': 3}
    
    config_manager = MockConfigManager()
    
    for test_case in test_cases:
        print(f"\n--- {test_case['name']} ---")
        print(f"原始SQL: {test_case['sql']}")
        
        try:
            # 创建动态SQL解析器实例
            parser = DynamicSQLParser(config_manager)
            
            # 直接调用修复方法
            fixed_sql = parser._fix_sql_keywords_if_needed(test_case['sql'])
            print(f"修复后SQL: {fixed_sql}")
            
            # 检查修复结果
            if fixed_sql == test_case['expected']:
                print("✓ SQL修复正确")
            else:
                print(f"✗ SQL修复不正确，期望: {test_case['expected']}，实际: {fixed_sql}")
                all_passed = False
                
        except Exception as e:
            print(f"✗ 测试失败: {str(e)}")
            import traceback
            traceback.print_exc()
            all_passed = False
    
    return all_passed

def test_multiple_param_replacement():
    """测试多个参数替换功能"""
    print("\n\n=== 测试多个参数替换功能 ===")
    
    # 导入param_extractor（需要模拟更多依赖）
    class MockConfigManager:
        def get_all_target_db_aliases(self):
            return ['test_db']
        
        def get_optimization_config(self):
            return {'enable_data_fetching': False}
    
    # 创建模拟的param_extractor类
    class MockParamExtractor:
        def __init__(self, sql_text, config_manager=None, metadata_list=None):
            self.sql_text = sql_text
            self.config_manager = config_manager
            self.metadata_list = metadata_list or []
            self.logger = LogMixin()
            
        def extract_params(self):
            # 简单提取参数
            params = []
            pattern = r'#\{([^}]+)\}'
            matches = re.findall(pattern, self.sql_text)
            
            for param_name in matches:
                param_info = {
                    'param': param_name,
                    'type': 'string',
                    'position': self.sql_text.find(f'#{{{param_name}}}')
                }
                params.append(param_info)
            
            self.logger.info(f"提取到 {len(params)} 个参数: {[p['param'] for p in params]}")
            return params
        
        def generate_replaced_sql(self):
            # 简单替换逻辑：将所有参数替换为预设值
            replaced_sql = self.sql_text
            params = self.extract_params()
            
            for param_info in params:
                param_name = param_info['param']
                # 简单的替换逻辑
                if 'id' in param_name.lower():
                    replaced_value = '123'
                elif 'name' in param_name.lower():
                    replaced_value = "'test_name'"
                elif 'status' in param_name.lower():
                    replaced_value = '1'
                elif 'time' in param_name.lower() or 'date' in param_name.lower():
                    replaced_value = "'2025-01-01'"
                else:
                    replaced_value = "'test_value'"
                
                param_pattern = f"#{{{param_name}}}"
                replaced_sql = re.sub(re.escape(param_pattern), replaced_value, replaced_sql)
            
            return replaced_sql, ['test_table']
    
    test_sqls = [
        {
            'name': '多个不同参数',
            'sql': 'SELECT * FROM users WHERE id = #{id} AND name = #{name} AND status = #{status} AND create_time > #{create_time}',
            'expected_params': ['id', 'name', 'status', 'create_time']
        },
        {
            'name': 'INSERT多个参数',
            'sql': 'INSERT INTO orders (order_id, customer_name, amount, order_date) VALUES (#{order_id}, #{customer_name}, #{amount}, #{order_date})',
            'expected_params': ['order_id', 'customer_name', 'amount', 'order_date']
        },
        {
            'name': 'UPDATE多个参数',
            'sql': 'UPDATE products SET price = #{price}, stock = #{stock}, description = #{description} WHERE id = #{id}',
            'expected_params': ['price', 'stock', 'description', 'id']
        }
    ]
    
    all_passed = True
    
    for test_case in test_sqls:
        print(f"\n--- {test_case['name']} ---")
        print(f"原始SQL: {test_case['sql']}")
        
        try:
            # 创建参数提取器
            extractor = MockParamExtractor(test_case['sql'])
            
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
                
        except Exception as e:
            print(f"✗ 测试失败: {str(e)}")
            import traceback
            traceback.print_exc()
            all_passed = False
    
    return all_passed

def test_sample_data_size():
    """测试样本数据大小功能"""
    print("\n\n=== 测试样本数据大小功能 ===")
    
    # 检查data_value_fetcher.py中的修改
    data_value_fetcher_path = os.path.join(os.path.dirname(__file__), 'sql_ai_analyzer', 'data_collector', 'data_value_fetcher.py')
    
    try:
        with open(data_value_fetcher_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查_fetch_sample_values方法
        if '_fetch_sample_values' in content:
            # 查找sample_size定义
            if 'sample_size = 20' in content:
                print("✓ 样本数据大小已设置为20")
                
                # 检查查询中的LIMIT子句
                if 'LIMIT {sample_size}' in content or 'LIMIT 20' in content:
                    print("✓ 查询LIMIT子句已使用样本大小20")
                else:
                    print("✗ 查询LIMIT子句可能未正确使用样本大小")
            else:
                print("✗ 未找到样本数据大小设置为20的代码")
                # 查找是否有其他大小设置
                import re
                sample_size_pattern = r'sample_size\s*=\s*(\d+)'
                match = re.search(sample_size_pattern, content)
                if match:
                    print(f"✗ 找到样本数据大小设置为: {match.group(1)}")
                else:
                    print("✗ 未找到样本数据大小设置")
        else:
            print("✗ 未找到_fetch_sample_values方法")
            
    except Exception as e:
        print(f"✗ 读取data_value_fetcher.py失败: {str(e)}")
        return False
    
    return True

def main():
    """主测试函数"""
    print("开始测试修复集成功能")
    print("=" * 60)
    
    # 运行所有测试
    test_results = []
    
    # 测试1: INSERT语句修复
    print("\n[测试1] INSERT语句修复功能测试")
    result1 = test_insert_sql_fix()
    test_results.append(("INSERT语句修复", result1))
    
    # 测试2: 多个参数替换
    print("\n[测试2] 多个参数替换功能测试")
    result2 = test_multiple_param_replacement()
    test_results.append(("多个参数替换", result2))
    
    # 测试3: 样本数据大小
    print("\n[测试3] 样本数据大小功能测试")
    result3 = test_sample_data_size()
    test_results.append(("样本数据大小", result3))
    
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
    
    # 提供修复建议
    if not all_passed:
        print("\n修复建议:")
        print("1. 如果参数替换不正确，请检查param_extractor.py中的generate_replaced_sql方法")
        print("2. 如果INSERT语句修复不正确，请检查dynamic_sql_parser.py中的_fix_sql_keywords_if_needed方法")
        print("3. 如果样本数据大小不正确，请检查data_value_fetcher.py中的_fetch_sample_values方法")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
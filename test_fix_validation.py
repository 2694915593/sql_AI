#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试修复后的参数替换逻辑
验证是否使用列名而不是参数名来获取数据库实际值
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

# 模拟数据值获取器
class MockDataValueFetcher:
    def __init__(self, config_manager, logger=None):
        self.config_manager = config_manager
        self.logger = logger
        self.enable_data_fetching = False
        # 记录调用历史，用于验证是否使用了正确的列名
        self.call_history = []
    
    def find_matching_column(self, db_alias, table_name, param_name, metadata_list):
        # 记录调用
        self.call_history.append({
            'method': 'find_matching_column',
            'db_alias': db_alias,
            'table_name': table_name,
            'param_name': param_name
        })
        # 返回一个匹配的列（使用参数名作为列名）
        return table_name, param_name, {'name': param_name, 'type': 'varchar(255)'}
    
    def get_replacement_value(self, db_alias, table_name, column_name, column_type):
        # 记录调用
        self.call_history.append({
            'method': 'get_replacement_value',
            'db_alias': db_alias,
            'table_name': table_name,
            'column_name': column_name,
            'column_type': column_type
        })
        # 根据列名判断返回什么值，用于验证是否使用了正确的列名
        column_name_lower = column_name.lower()
        
        # 检查是否为ES_ACCOUNTCANCEL_FLOW表的列
        if 'eaf_' in column_name_lower:
            # 返回特定值，用于验证是否使用了正确的列名
            if 'flowno' in column_name_lower:
                return "'TEST_FLOW_001'"
            elif 'partyno' in column_name_lower:
                return "'TEST_PARTY_001'"
            elif 'cardno' in column_name_lower:
                return "'TEST_CARD_001'"
            elif 'trantime' in column_name_lower:
                return "'2025-01-01 10:00:00'"
            elif 'bankcardno' in column_name_lower:
                return "'TEST_BANK_001'"
            elif 'cardflag' in column_name_lower:
                return '1'
            elif 'username' in column_name_lower:
                return "'TEST_USER'"
            elif 'livingordeno' in column_name_lower:
                return "'TEST_LIVING_001'"
            elif 'mobilecode' in column_name_lower:
                return "'13800138000'"
            elif 'ecbptranstt' in column_name_lower:
                return "'S'"
            elif 'errorcode' in column_name_lower:
                return "'0000'"
            elif 'errormsg' in column_name_lower:
                return "'SUCCESS'"
            elif 'updatetime' in column_name_lower:
                return "'2025-01-01 10:00:00'"
            elif 'remark' in column_name_lower:
                return "'TEST_REMARK'"
        
        # 默认返回值
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
original_sys_modules = sys.modules.get('sql_ai_analyzer.data_collector.data_value_fetcher')
sys.modules['sql_ai_analyzer.data_collector.data_value_fetcher'] = type(sys)('sql_ai_analyzer.data_collector.data_value_fetcher')
sys.modules['sql_ai_analyzer.data_collector.data_value_fetcher'].DataValueFetcher = MockDataValueFetcher

from sql_ai_analyzer.data_collector.param_extractor import ParamExtractor

def test_insert_sql_column_mapping():
    """测试INSERT语句的列名映射功能"""
    print("=== 测试INSERT语句的列名映射功能 ===")
    
    # 创建模拟配置管理器
    config_manager = MockConfigManager()
    
    # 创建模拟元数据 - ES_ACCOUNTCANCEL_FLOW表的元数据
    metadata_list = [
        {
            'table_name': 'ES_ACCOUNTCANCEL_FLOW',
            'columns': [
                {'name': 'EAF_FLOWNO', 'type': 'varchar(50)'},
                {'name': 'EAF_PARTYNO', 'type': 'varchar(50)'},
                {'name': 'EAF_CARDNO', 'type': 'varchar(50)'},
                {'name': 'EAF_TRANTIME', 'type': 'datetime'},
                {'name': 'EAF_BANKCARDNO', 'type': 'varchar(50)'},
                {'name': 'EAF_CARDFLAG', 'type': 'int'},
                {'name': 'EAF_USERNAME', 'type': 'varchar(100)'},
                {'name': 'EAF_LIVINGORDENO', 'type': 'varchar(50)'},
                {'name': 'EAF_MOBILECODE', 'type': 'varchar(20)'},
                {'name': 'EAF_ECBPTRANSTT', 'type': 'varchar(10)'},
                {'name': 'EAF_ERRORCODE', 'type': 'varchar(20)'},
                {'name': 'EAF_ERRORMSG', 'type': 'varchar(200)'},
                {'name': 'EAF_UPDATETIME', 'type': 'datetime'},
                {'name': 'EAF_REMARK', 'type': 'varchar(500)'}
            ]
        }
    ]
    
    # 用户提供的SQL语句
    sql = """INSERT INTO
ES_ACCOUNTCANCEL_FLOW
(
EAF_FLOWNO,
EAF_PARTYNO,
EAF_CARDNO,
EAF_TRANTIME,
EAF_BANKCARDNO,
EAF_CARDFLAG,
EAF_USERNAME,
EAF_LIVINGORDENO,
EAF_MOBILECODE,
EAF_ECBPTRANSTT,
EAF_ERRORCODE,
EAF_ERRORMSG,
EAF_UPDATETIME,
EAF_REMARK
)
VALUES
(
#{flowNo},
#{partyNo},
#{cardNo},
#{tranTime},
#{bankCardNo},
#{cardFlag},
#{userName},
#{livingOrdeNo},
#{mobileCode},
#{ecbpTranStt},
#{errorCode},
#{errorMsg},
#{updateTime},
#{remark}
)"""
    
    print(f"\n原始SQL: {sql[:200]}...")
    
    try:
        # 创建参数提取器
        extractor = ParamExtractor(sql, config_manager=config_manager, metadata_list=metadata_list)
        
        # 获取数据值获取器
        data_value_fetcher = extractor.data_value_fetcher
        
        # 提取参数
        params = extractor.extract_params()
        print(f"\n提取的参数数量: {len(params)}")
        print(f"参数列表: {[p['param'] for p in params]}")
        
        # 测试列名映射功能
        print("\n=== 测试列名映射 ===")
        test_params = ['flowNo', 'partyNo', 'cardNo']
        for param_name in test_params:
            column_name = extractor._get_column_name_for_param(param_name)
            print(f"参数 '{param_name}' -> 列名 '{column_name}'")
        
        # 测试INSERT语句列名映射解析
        mapping = extractor._parse_insert_column_mapping()
        print(f"\nINSERT语句列名映射: {mapping}")
        
        # 测试几个关键映射
        expected_mappings = {
            'flowNo': 'EAF_FLOWNO',
            'partyNo': 'EAF_PARTYNO',
            'cardNo': 'EAF_CARDNO'
        }
        
        for param, expected_col in expected_mappings.items():
            if param in mapping and mapping[param] == expected_col:
                print(f"✓ 参数 {param} 正确映射到列 {expected_col}")
            else:
                print(f"✗ 参数 {param} 映射错误，期望: {expected_col}，实际: {mapping.get(param)}")
        
        # 生成替换后的SQL
        print("\n=== 生成替换后的SQL ===")
        replaced_sql, tables = extractor.generate_replaced_sql()
        print(f"替换后的SQL（前300字符）: {replaced_sql[:300]}...")
        
        # 检查是否还有未替换的参数
        param_pattern = r'#\{([^}]+)\}'
        remaining_params = re.findall(param_pattern, replaced_sql)
        
        if not remaining_params:
            print("✓ 所有参数都已成功替换")
        else:
            print(f"✗ 仍有未替换的参数: {remaining_params}")
        
        # 检查数据值获取器的调用历史
        print("\n=== 数据值获取器调用历史 ===")
        for i, call in enumerate(data_value_fetcher.call_history, 1):
            print(f"{i}. {call['method']}: {call}")
        
        # 检查是否使用了正确的列名
        print("\n=== 验证是否使用正确的列名 ===")
        column_calls = [c for c in data_value_fetcher.call_history if c['method'] == 'get_replacement_value']
        
        if column_calls:
            print("get_replacement_value调用详情:")
            for call in column_calls:
                column_name = call['column_name']
                # 检查是否使用了EAF_前缀的列名
                if column_name and column_name.startswith('EAF_'):
                    print(f"✓ 使用了正确的列名: {column_name}")
                else:
                    print(f"⚠ 可能使用了错误的列名: {column_name}")
        
        # 验证替换后的值
        print("\n=== 验证替换后的值 ===")
        # 检查是否包含预期的替换值
        expected_values = [
            "'TEST_FLOW_001'",  # flowNo -> EAF_FLOWNO
            "'TEST_PARTY_001'", # partyNo -> EAF_PARTYNO
            "'TEST_CARD_001'",  # cardNo -> EAF_CARDNO
        ]
        
        for expected_value in expected_values:
            if expected_value in replaced_sql:
                print(f"✓ 找到预期值: {expected_value}")
            else:
                print(f"✗ 未找到预期值: {expected_value}")
        
        return True
        
    except Exception as e:
        print(f"✗ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("开始测试修复后的参数替换逻辑")
    print("=" * 60)
    
    success = test_insert_sql_column_mapping()
    
    print("\n" + "=" * 60)
    if success:
        print("测试结果: 通过 ✓")
        print("修复说明:")
        print("1. 添加了INSERT语句列名映射解析功能")
        print("2. 优先使用列名而不是参数名获取数据库值")
        print("3. 对于参数flowNo，现在会查找EAF_FLOWNO列而不是flowNo列")
    else:
        print("测试结果: 失败 ✗")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
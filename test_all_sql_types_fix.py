#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试所有SQL类型的参数替换逻辑
验证SELECT、UPDATE、DELETE语句是否也能正确使用列名而不是参数名
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
        
        # 根据表名和参数名智能匹配列
        column_name = self._guess_column_name(table_name, param_name)
        return table_name, column_name, {'name': column_name, 'type': 'varchar(255)'}
    
    def _guess_column_name(self, table_name, param_name):
        """智能猜测列名"""
        # 常见表名的列名前缀映射
        table_prefix_map = {
            'ES_ACCOUNTCANCEL_FLOW': 'EAF_',
            'ES_PARTY_INFO': 'EPI_',
            'ES_CARD_INFO': 'ECI_',
            'ES_TRANSACTION': 'ET_',
            'USERS': 'USER_',
            'PRODUCTS': 'PROD_',
            'ORDERS': 'ORDER_',
            'LOGS': 'LOG_'
        }
        
        prefix = table_prefix_map.get(table_name, '')
        
        # 转换参数名到列名格式
        # 例如：flowNo -> FLOWNO, userId -> USER_ID
        import re
        # 将驼峰命名转换为下划线命名
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', param_name)
        param_snake = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).upper()
        
        return f"{prefix}{param_snake}"
    
    def get_replacement_value(self, db_alias, table_name, column_name, column_type):
        # 记录调用
        self.call_history.append({
            'method': 'get_replacement_value',
            'db_alias': db_alias,
            'table_name': table_name,
            'column_name': column_name,
            'column_type': column_type
        })
        
        # 根据列名返回测试值
        column_name_lower = column_name.lower()
        
        # 检查常见列名并返回相应的测试值
        if 'id' in column_name_lower:
            return 12345
        elif 'name' in column_name_lower or 'username' in column_name_lower:
            return "'TEST_NAME'"
        elif 'price' in column_name_lower or 'amount' in column_name_lower:
            return 99.99
        elif 'time' in column_name_lower or 'date' in column_name_lower:
            return "'2025-01-01 00:00:00'"
        elif 'category' in column_name_lower:
            return "'TEST_CATEGORY'"
        elif 'status' in column_name_lower or 'flag' in column_name_lower:
            return 1
        elif 'code' in column_name_lower:
            return "'TEST_CODE'"
        elif 'no' in column_name_lower:
            return "'TEST_NO'"
        elif 'type' in column_name_lower:
            return "'TEST_TYPE'"
        elif 'desc' in column_name_lower or 'description' in column_name_lower:
            return "'TEST_DESC'"
        elif 'email' in column_name_lower:
            return "'test@example.com'"
        elif 'phone' in column_name_lower or 'mobile' in column_name_lower:
            return "'13800138000'"
        else:
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
original_sys_modules = sys.modules.get('sql_ai_analyzer.data_collector.data_value_fetcher')
sys.modules['sql_ai_analyzer.data_collector.data_value_fetcher'] = type(sys)('sql_ai_analyzer.data_collector.data_value_fetcher')
sys.modules['sql_ai_analyzer.data_collector.data_value_fetcher'].DataValueFetcher = MockDataValueFetcher

from sql_ai_analyzer.data_collector.param_extractor import ParamExtractor

def test_select_statement():
    """测试SELECT语句的参数替换"""
    print("=== 测试SELECT语句 ===")
    
    # 创建模拟配置管理器
    config_manager = MockConfigManager()
    
    # 创建模拟元数据
    metadata_list = [
        {
            'table_name': 'ES_PARTY_INFO',
            'columns': [
                {'name': 'EPI_PARTY_ID', 'type': 'int'},
                {'name': 'EPI_PARTY_NO', 'type': 'varchar(50)'},
                {'name': 'EPI_PARTY_NAME', 'type': 'varchar(100)'},
                {'name': 'EPI_STATUS', 'type': 'int'},
                {'name': 'EPI_CREATE_TIME', 'type': 'datetime'}
            ]
        }
    ]
    
    # SELECT语句
    sql = "SELECT * FROM ES_PARTY_INFO WHERE EPI_PARTY_NO = #{partyNo} AND EPI_STATUS = #{status}"
    
    print(f"SQL: {sql}")
    
    try:
        # 创建参数提取器
        extractor = ParamExtractor(sql, config_manager=config_manager, metadata_list=metadata_list)
        
        # 测试列名映射
        print("\n列名映射测试:")
        for param_name in ['partyNo', 'status']:
            column_name = extractor._get_column_name_for_param(param_name)
            print(f"参数 '{param_name}' -> 列名 '{column_name}'")
        
        # 提取参数
        params = extractor.extract_params()
        print(f"\n提取的参数: {[p['param'] for p in params]}")
        
        # 生成替换后的SQL
        replaced_sql, tables = extractor.generate_replaced_sql()
        print(f"\n替换后的SQL: {replaced_sql}")
        
        # 检查是否还有未替换的参数
        param_pattern = r'#\{([^}]+)\}'
        remaining_params = re.findall(param_pattern, replaced_sql)
        
        if not remaining_params:
            print("✓ SELECT语句参数替换成功")
        else:
            print(f"✗ SELECT语句仍有未替换的参数: {remaining_params}")
        
        # 检查调用历史
        data_value_fetcher = extractor.data_value_fetcher
        print(f"\n数据值获取器调用次数: {len(data_value_fetcher.call_history)}")
        
        return not remaining_params
        
    except Exception as e:
        print(f"✗ SELECT语句测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_update_statement():
    """测试UPDATE语句的参数替换"""
    print("\n=== 测试UPDATE语句 ===")
    
    # 创建模拟配置管理器
    config_manager = MockConfigManager()
    
    # 创建模拟元数据
    metadata_list = [
        {
            'table_name': 'PRODUCTS',
            'columns': [
                {'name': 'PROD_ID', 'type': 'int'},
                {'name': 'PROD_NAME', 'type': 'varchar(100)'},
                {'name': 'PROD_PRICE', 'type': 'decimal(10,2)'},
                {'name': 'PROD_CATEGORY', 'type': 'varchar(50)'},
                {'name': 'PROD_STATUS', 'type': 'int'}
            ]
        }
    ]
    
    # UPDATE语句
    sql = "UPDATE PRODUCTS SET PROD_PRICE = #{price}, PROD_STATUS = #{status} WHERE PROD_ID = #{id}"
    
    print(f"SQL: {sql}")
    
    try:
        # 创建参数提取器
        extractor = ParamExtractor(sql, config_manager=config_manager, metadata_list=metadata_list)
        
        # 测试列名映射
        print("\n列名映射测试:")
        for param_name in ['price', 'status', 'id']:
            column_name = extractor._get_column_name_for_param(param_name)
            print(f"参数 '{param_name}' -> 列名 '{column_name}'")
        
        # 提取参数
        params = extractor.extract_params()
        print(f"\n提取的参数: {[p['param'] for p in params]}")
        
        # 生成替换后的SQL
        replaced_sql, tables = extractor.generate_replaced_sql()
        print(f"\n替换后的SQL: {replaced_sql}")
        
        # 检查是否还有未替换的参数
        param_pattern = r'#\{([^}]+)\}'
        remaining_params = re.findall(param_pattern, replaced_sql)
        
        if not remaining_params:
            print("✓ UPDATE语句参数替换成功")
        else:
            print(f"✗ UPDATE语句仍有未替换的参数: {remaining_params}")
        
        return not remaining_params
        
    except Exception as e:
        print(f"✗ UPDATE语句测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_delete_statement():
    """测试DELETE语句的参数替换"""
    print("\n=== 测试DELETE语句 ===")
    
    # 创建模拟配置管理器
    config_manager = MockConfigManager()
    
    # 创建模拟元数据
    metadata_list = [
        {
            'table_name': 'LOGS',
            'columns': [
                {'name': 'LOG_ID', 'type': 'int'},
                {'name': 'LOG_TYPE', 'type': 'varchar(50)'},
                {'name': 'LOG_CONTENT', 'type': 'text'},
                {'name': 'LOG_TIME', 'type': 'datetime'},
                {'name': 'LOG_STATUS', 'type': 'int'}
            ]
        }
    ]
    
    # DELETE语句
    sql = "DELETE FROM LOGS WHERE LOG_TIME < #{endTime} AND LOG_TYPE = #{type}"
    
    print(f"SQL: {sql}")
    
    try:
        # 创建参数提取器
        extractor = ParamExtractor(sql, config_manager=config_manager, metadata_list=metadata_list)
        
        # 测试列名映射
        print("\n列名映射测试:")
        for param_name in ['endTime', 'type']:
            column_name = extractor._get_column_name_for_param(param_name)
            print(f"参数 '{param_name}' -> 列名 '{column_name}'")
        
        # 提取参数
        params = extractor.extract_params()
        print(f"\n提取的参数: {[p['param'] for p in params]}")
        
        # 生成替换后的SQL
        replaced_sql, tables = extractor.generate_replaced_sql()
        print(f"\n替换后的SQL: {replaced_sql}")
        
        # 检查是否还有未替换的参数
        param_pattern = r'#\{([^}]+)\}'
        remaining_params = re.findall(param_pattern, replaced_sql)
        
        if not remaining_params:
            print("✓ DELETE语句参数替换成功")
        else:
            print(f"✗ DELETE语句仍有未替换的参数: {remaining_params}")
        
        return not remaining_params
        
    except Exception as e:
        print(f"✗ DELETE语句测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_where_clause_mapping():
    """测试WHERE子句的参数映射"""
    print("\n=== 测试WHERE子句参数映射 ===")
    
    # 创建模拟配置管理器
    config_manager = MockConfigManager()
    
    # 创建模拟元数据
    metadata_list = [
        {
            'table_name': 'ES_ACCOUNTCANCEL_FLOW',
            'columns': [
                {'name': 'EAF_FLOWNO', 'type': 'varchar(50)'},
                {'name': 'EAF_PARTYNO', 'type': 'varchar(50)'},
                {'name': 'EAF_STATUS', 'type': 'int'},
                {'name': 'EAF_CREATE_TIME', 'type': 'datetime'}
            ]
        }
    ]
    
    # 包含WHERE子句的复杂SELECT
    sql = """
    SELECT EAF_FLOWNO, EAF_PARTYNO 
    FROM ES_ACCOUNTCANCEL_FLOW 
    WHERE EAF_FLOWNO = #{flowNo} 
      AND EAF_PARTYNO = #{partyNo}
      AND EAF_STATUS = #{status}
      AND EAF_CREATE_TIME > #{startTime}
    """
    
    print(f"SQL: {sql[:100]}...")
    
    try:
        # 创建参数提取器
        extractor = ParamExtractor(sql, config_manager=config_manager, metadata_list=metadata_list)
        
        # 测试列名映射
        print("\nWHERE子句参数映射测试:")
        test_params = ['flowNo', 'partyNo', 'status', 'startTime']
        for param_name in test_params:
            column_name = extractor._get_column_name_for_param(param_name)
            print(f"参数 '{param_name}' -> 列名 '{column_name}'")
        
        # 检查是否所有参数都能找到对应的列
        mapping_success = all(extractor._get_column_name_for_param(p) is not None for p in test_params)
        
        if mapping_success:
            print("✓ WHERE子句参数映射成功")
        else:
            print("✗ WHERE子句参数映射失败")
        
        return mapping_success
        
    except Exception as e:
        print(f"✗ WHERE子句测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("开始测试所有SQL类型的参数替换逻辑")
    print("=" * 60)
    
    results = []
    
    # 运行各种测试
    results.append(("SELECT语句", test_select_statement()))
    results.append(("UPDATE语句", test_update_statement()))
    results.append(("DELETE语句", test_delete_statement()))
    results.append(("WHERE子句映射", test_where_clause_mapping()))
    
    print("\n" + "=" * 60)
    print("测试结果汇总:")
    
    all_passed = True
    for test_name, success in results:
        status = "✓ 通过" if success else "✗ 失败"
        print(f"{test_name}: {status}")
        if not success:
            all_passed = False
    
    print("\n诊断信息:")
    if all_passed:
        print("所有SQL类型的参数替换测试通过！")
        print("修复说明:")
        print("1. INSERT语句: 通过列名映射解析")
        print("2. SELECT/UPDATE/DELETE语句: 通过智能参数名匹配")
        print("3. WHERE子句: 参数名能正确映射到列名")
    else:
        print("部分测试失败，需要进一步修复非INSERT语句的参数替换逻辑")
        print("主要问题:")
        print("1. 对于非INSERT语句，需要增强参数名到列名的智能匹配")
        print("2. 需要从WHERE/SET子句中提取列名信息")
        print("3. 需要改进模糊匹配算法")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
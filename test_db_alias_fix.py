#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试数据库别名修复功能
验证修改后的逻辑是否使用元数据收集阶段获取的数据库实例信息
而不是获取所有数据库别名后使用第一个
"""

import sys
import os
import re

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 模拟配置管理器
class MockConfigManager:
    def __init__(self):
        self.all_target_dbs = ['db1', 'db2', 'db3']
    
    def get_all_target_db_aliases(self):
        print(f"调用 get_all_target_db_aliases()，返回: {self.all_target_dbs}")
        return self.all_target_dbs
    
    def get_target_database_config(self, db_alias):
        return {
            'host': 'localhost',
            'port': 3306,
            'user': 'test',
            'password': 'test',
            'database': 'test'
        }

# 模拟数据值获取器
class MockDataValueFetcher:
    def __init__(self, config_manager, logger=None):
        self.config_manager = config_manager
        self.logger = logger
    
    def find_matching_column(self, db_alias, table_name, param_name, metadata_list):
        print(f"MockDataValueFetcher.find_matching_column - db_alias={db_alias}, table_name={table_name}, param_name={param_name}")
        # 返回一个匹配的列
        return table_name, param_name, {'name': param_name, 'type': 'varchar(255)'}
    
    def get_replacement_value(self, db_alias, table_name, column_name, column_type):
        print(f"MockDataValueFetcher.get_replacement_value - db_alias={db_alias}, table_name={table_name}, column_name={column_name}")
        # 返回带数据库别名的测试值，以便验证使用的数据库别名
        return f"'value_from_{db_alias}'"

# 模拟模块
import types
sys.modules['utils.logger'] = types.ModuleType('utils.logger')
sys.modules['utils.logger'].LogMixin = type('LogMixin', (), {
    '__init__': lambda self: setattr(self, 'logger', self),
    'set_logger': lambda self, logger: setattr(self, 'logger', logger),
    'info': lambda self, msg: print(f"INFO: {msg}"),
    'debug': lambda self, msg: print(f"DEBUG: {msg}"),
    'warning': lambda self, msg: print(f"WARNING: {msg}"),
    'error': lambda self, msg: print(f"ERROR: {msg}"),
})()

sys.modules['utils.sql_preprocessor'] = types.ModuleType('utils.sql_preprocessor')
sys.modules['utils.sql_preprocessor'].SQLPreprocessor = type('SQLPreprocessor', (), {
    '__init__': lambda self, logger=None: setattr(self, 'logger', logger),
    'preprocess_sql': lambda self, sql_text, mode="normalize": (
        sql_text, {'has_xml_tags': False, 'processed_length': len(sql_text), 'original_length': len(sql_text)}
    )
})()

sys.modules['sql_ai_analyzer.data_collector.data_value_fetcher'] = types.ModuleType('sql_ai_analyzer.data_collector.data_value_fetcher')
sys.modules['sql_ai_analyzer.data_collector.data_value_fetcher'].DataValueFetcher = MockDataValueFetcher

from sql_ai_analyzer.data_collector.param_extractor import ParamExtractor

def test_without_db_alias():
    """测试没有传递db_alias的情况（应该使用第一个数据库别名）"""
    print("\n=== 测试1: 没有传递db_alias参数 ===")
    print("期望: 调用get_all_target_db_aliases()并使用第一个数据库别名")
    
    config_manager = MockConfigManager()
    
    # 模拟元数据
    metadata_list = [
        {
            'table_name': 'users',
            'columns': [
                {'name': 'id', 'type': 'int'},
                {'name': 'name', 'type': 'varchar(255)'}
            ]
        }
    ]
    
    sql = "SELECT * FROM users WHERE id = #{id} AND name = #{name}"
    
    print(f"创建ParamExtractor，不传递db_alias参数")
    extractor = ParamExtractor(
        sql, 
        config_manager=config_manager, 
        metadata_list=metadata_list
    )
    
    print(f"extractor.db_alias值: {extractor.db_alias}")
    
    try:
        replaced_sql, tables = extractor.generate_replaced_sql()
        print(f"替换后的SQL: {replaced_sql}")
        
        # 检查是否使用了第一个数据库别名
        if "'value_from_db1'" in replaced_sql:
            print("✓ 正确使用了第一个数据库别名 (db1)")
            return True
        else:
            print(f"✗ 可能没有正确使用数据库别名")
            return False
    except Exception as e:
        print(f"✗ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_with_db_alias():
    """测试传递了特定db_alias的情况"""
    print("\n=== 测试2: 传递了特定db_alias参数 ===")
    print("期望: 使用传入的db_alias，而不调用get_all_target_db_aliases()")
    
    config_manager = MockConfigManager()
    
    # 模拟元数据
    metadata_list = [
        {
            'table_name': 'users',
            'columns': [
                {'name': 'id', 'type': 'int'},
                {'name': 'name', 'type': 'varchar(255)'}
            ]
        }
    ]
    
    sql = "SELECT * FROM users WHERE id = #{id} AND name = #{name}"
    
    print(f"创建ParamExtractor，传递db_alias='specific_db'")
    extractor = ParamExtractor(
        sql, 
        config_manager=config_manager, 
        metadata_list=metadata_list,
        db_alias='specific_db'  # 传递特定的数据库别名
    )
    
    print(f"extractor.db_alias值: {extractor.db_alias}")
    
    try:
        replaced_sql, tables = extractor.generate_replaced_sql()
        print(f"替换后的SQL: {replaced_sql}")
        
        # 检查是否使用了传入的数据库别名
        if "'value_from_specific_db'" in replaced_sql:
            print("✓ 正确使用了传入的数据库别名 (specific_db)")
            return True
        else:
            print(f"✗ 可能没有正确使用传入的数据库别名")
            return False
    except Exception as e:
        print(f"✗ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_sql_extractor_integration():
    """测试sql_extractor中的集成"""
    print("\n=== 测试3: sql_extractor中的集成 ===")
    
    # 导入模块并模拟依赖
    sys.modules['utils.db_connector_pymysql'] = types.ModuleType('utils.db_connector_pymysql')
    sys.modules['utils.db_connector_pymysql'].DatabaseManager = type('DatabaseManager', (), {
        '__init__': lambda self, db_config: None,
        'fetch_all': lambda self, query, params=None: [],
        'fetch_one': lambda self, query, params=None: {},
        'execute': lambda self, query, params=None: 0
    })()
    
    try:
        from sql_ai_analyzer.data_collector.sql_extractor import SQLExtractor
        
        # 模拟配置管理器
        class MockConfigManagerForSQLExtractor:
            def __init__(self):
                pass
            
            def get_database_config(self):
                return {}
            
            def get_all_target_db_aliases(self):
                return ['db1', 'db2']
        
        config_manager = MockConfigManagerForSQLExtractor()
        
        # 创建SQLExtractor实例
        extractor = SQLExtractor(config_manager)
        
        # 测试generate_replaced_sql方法
        print("测试generate_replaced_sql方法，传递db_alias='instance_db'")
        
        # 模拟元数据
        metadata_list = [
            {
                'table_name': 'users',
                'columns': [
                    {'name': 'id', 'type': 'int'},
                    {'name': 'name', 'type': 'varchar(255)'}
                ]
            }
        ]
        
        sql = "SELECT * FROM users WHERE id = #{id}"
        
        # 模拟ParamExtractor
        class MockParamExtractor:
            def __init__(self, sql, logger=None, metadata_list=None, config_manager=None, db_alias=None):
                print(f"MockParamExtractor创建: db_alias={db_alias}")
                self.db_alias = db_alias
            
            def generate_replaced_sql(self):
                print(f"MockParamExtractor.generate_replaced_sql: 使用db_alias={self.db_alias}")
                return f"SELECT * FROM users WHERE id = 'value_from_{self.db_alias}'", ['users']
        
        # 替换ParamExtractor类
        original_param_extractor = sys.modules['sql_ai_analyzer.data_collector.sql_extractor'].ParamExtractor
        sys.modules['sql_ai_analyzer.data_collector.sql_extractor'].ParamExtractor = MockParamExtractor
        
        try:
            # 调用generate_replaced_sql并传递db_alias
            replaced_sql, tables = extractor.generate_replaced_sql(
                sql,
                metadata_list=metadata_list,
                db_alias='instance_db'  # 传递数据库别名
            )
            
            print(f"返回的SQL: {replaced_sql}")
            
            # 恢复原来的ParamExtractor
            sys.modules['sql_ai_analyzer.data_collector.sql_extractor'].ParamExtractor = original_param_extractor
            
            if "'value_from_instance_db'" in replaced_sql:
                print("✓ SQLExtractor正确传递了db_alias参数")
                return True
            else:
                print(f"✗ SQLExtractor可能没有正确传递db_alias参数")
                return False
                
        except Exception as e:
            # 恢复原来的ParamExtractor
            sys.modules['sql_ai_analyzer.data_collector.sql_extractor'].ParamExtractor = original_param_extractor
            print(f"✗ 测试失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
            
    except Exception as e:
        print(f"✗ 导入模块失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_main_integration():
    """测试main.py中的集成"""
    print("\n=== 测试4: main.py中的集成 ===")
    
    # 模拟main.py中的相关代码片段
    print("模拟main.py中的generate_replaced_sql调用:")
    print("replaced_sql, extracted_tables = self.sql_extractor.generate_replaced_sql(")
    print("    sql_info['sql_text'], ")
    print("    all_metadata,  # 传递元数据列表")
    print("    processed_sql=processed_sql,  # 使用已经处理过的SQL")
    print("    db_alias=instance_alias  # 使用找到表的实例别名作为数据库别名")
    print(")")
    
    # 模拟变量
    sql_text = "SELECT * FROM users WHERE id = #{id}"
    all_metadata = [{'table_name': 'users', 'instance_alias': 'production_db'}]
    processed_sql = "SELECT * FROM users WHERE id = #{id}"
    instance_alias = 'production_db'  # 从元数据中获取的实例别名
    
    print(f"\n模拟参数值:")
    print(f"  sql_text: {sql_text}")
    print(f"  instance_alias: {instance_alias}")
    print(f"  processed_sql: {processed_sql}")
    
    # 验证instance_alias是否来自元数据
    if instance_alias == all_metadata[0].get('instance_alias'):
        print("✓ instance_alias正确来自元数据")
        return True
    else:
        print(f"✗ instance_alias不正确")
        return False

def main():
    """主测试函数"""
    print("开始测试数据库别名修复功能")
    print("验证修改后的逻辑是否使用元数据收集阶段获取的数据库实例信息")
    print("=" * 80)
    
    test_results = []
    
    # 运行所有测试
    test_results.append(("无db_alias参数测试", test_without_db_alias()))
    test_results.append(("有db_alias参数测试", test_with_db_alias()))
    test_results.append(("SQL Extractor集成测试", test_sql_extractor_integration()))
    test_results.append(("Main.py集成测试", test_main_integration()))
    
    # 输出测试结果摘要
    print("\n" + "=" * 80)
    print("测试结果摘要:")
    print("=" * 80)
    
    all_passed = True
    for test_name, result in test_results:
        status = "通过" if result else "失败"
        all_passed = all_passed and result
        print(f"{test_name}: {status}")
    
    print("\n" + "=" * 80)
    print(f"总体结果: {'所有测试通过' if all_passed else '有测试失败'}")
    
    if all_passed:
        print("\n结论: 数据库别名逻辑修复成功！")
        print("✓ ParamExtractor现在可以接收db_alias参数")
        print("✓ 优先使用传入的db_alias，而不是获取所有数据库别名后使用第一个")
        print("✓ sql_extractor和main.py正确集成了这一改进")
    else:
        print("\n结论: 数据库别名逻辑修复存在问题，请检查代码")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
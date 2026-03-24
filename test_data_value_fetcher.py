#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试数据值获取器，验证从数据表获取随机实际值的功能
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sql_ai_analyzer.config.config_manager import ConfigManager
from sql_ai_analyzer.data_collector.data_value_fetcher import DataValueFetcher
from sql_ai_analyzer.data_collector.param_extractor import ParamExtractor

def test_data_value_fetcher_basic():
    """测试数据值获取器的基本功能"""
    print("=== 测试数据值获取器基本功能 ===")
    
    try:
        # 初始化配置管理器
        config = ConfigManager('sql_ai_analyzer/config/config.ini')
        
        # 初始化数据值获取器
        data_fetcher = DataValueFetcher(config)
        
        # 测试获取数据库连接配置
        target_dbs = config.get_all_target_db_aliases()
        print(f"目标数据库别名: {target_dbs}")
        
        if target_dbs:
            db_alias = target_dbs[0]
            print(f"使用数据库别名: {db_alias}")
            
            # 测试随机值获取
            print("\n=== 测试随机值获取 ===")
            
            # 测试示例：从已知表中获取随机值
            test_tables = ['users', 'products', 'orders']  # 假设的表名
            
            for table_name in test_tables:
                try:
                    # 模拟表结构信息（因为实际数据库可能没有这些表）
                    print(f"模拟表 '{table_name}' 的结构测试")
                    
                    # 模拟的列信息
                    mock_columns = [
                        {'name': 'id', 'type': 'int'},
                        {'name': 'name', 'type': 'varchar(100)'},
                        {'name': 'status', 'type': 'tinyint'},
                        {'name': 'created_at', 'type': 'datetime'}
                    ]
                    
                    print(f"表 '{table_name}' 的模拟结构: {len(mock_columns)} 个字段")
                    
                    # 测试每个字段获取随机值
                    for column in mock_columns:
                        column_name = column.get('name', '')
                        column_type = column.get('type', '')
                        
                        # 获取随机值（使用模拟参数）
                        replacement_value = data_fetcher.get_replacement_value(
                            db_alias, table_name, column_name, column_type, 'string'
                        )
                        
                        if replacement_value is not None:
                            print(f"  - {column_name} ({column_type}): {replacement_value}")
                        else:
                            print(f"  - {column_name} ({column_type}): 无法获取值")
                        
                except Exception as e:
                    print(f"处理表 '{table_name}' 时出错: {str(e)}")
        
        return True
        
    except Exception as e:
        print(f"测试数据值获取器时发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_param_extractor_with_data_fetcher():
    """测试参数提取器与数据值获取器的集成"""
    print("\n\n=== 测试参数提取器与数据值获取器集成 ===")
    
    try:
        # 初始化配置管理器
        config = ConfigManager('sql_ai_analyzer/config/config.ini')
        
        # 测试SQL语句（包含动态参数）
        test_sqls = [
            "SELECT * FROM users WHERE user_id = #{user_id} AND status = #{status}",
            "UPDATE products SET price = #{price} WHERE category = #{category}",
            "INSERT INTO orders (order_id, customer_id, amount) VALUES (#{order_id}, #{customer_id}, #{amount})"
        ]
        
        for i, sql_text in enumerate(test_sqls, 1):
            print(f"\n--- 测试SQL {i} ---")
            print(f"原始SQL: {sql_text}")
            
            # 创建参数提取器（带配置管理器以启用数据值获取）
            extractor = ParamExtractor(
                sql_text=sql_text,
                config_manager=config,
                metadata_list=[]  # 如果没有元数据，会尝试使用预设值
            )
            
            # 提取参数
            params = extractor.extract_params()
            print(f"提取到参数: {params}")
            
            # 生成替换后的SQL
            replaced_sql, tables = extractor.generate_replaced_sql()
            print(f"替换后SQL: {replaced_sql}")
            print(f"提取到的表名: {tables}")
            
            # 分析是否使用了数据库值
            if extractor.data_value_fetcher:
                print("数据值获取器已启用 - 尝试从数据库获取实际值")
            else:
                print("数据值获取器未启用 - 使用预设值")
        
        return True
        
    except Exception as e:
        print(f"测试参数提取器集成时发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_find_matching_column():
    """测试查找匹配列的功能"""
    print("\n\n=== 测试查找匹配列功能 ===")
    
    try:
        # 初始化配置管理器
        config = ConfigManager('sql_ai_analyzer/config/config.ini')
        
        # 初始化数据值获取器
        data_fetcher = DataValueFetcher(config)
        
        target_dbs = config.get_all_target_db_aliases()
        if not target_dbs:
            print("没有目标数据库配置，跳过测试")
            return False
        
        db_alias = target_dbs[0]
        
        # 模拟的元数据列表
        mock_metadata_list = [
            {
                'table_name': 'users',
                'columns': [
                    {'name': 'id', 'type': 'int'},
                    {'name': 'user_id', 'type': 'varchar(50)'},
                    {'name': 'username', 'type': 'varchar(100)'},
                    {'name': 'status', 'type': 'tinyint'},
                    {'name': 'created_at', 'type': 'datetime'}
                ]
            },
            {
                'table_name': 'products',
                'columns': [
                    {'name': 'product_id', 'type': 'int'},
                    {'name': 'product_name', 'type': 'varchar(200)'},
                    {'name': 'price', 'type': 'decimal(10,2)'},
                    {'name': 'category', 'type': 'varchar(50)'}
                ]
            }
        ]
        
        # 测试查找匹配列
        test_params = [
            ('user_id', 'users'),
            ('status', 'users'),
            ('price', 'products'),
            ('category', 'products'),
            ('nonexistent', 'users')  # 不存在的参数
        ]
        
        for param_name, table_name in test_params:
            result = data_fetcher.find_matching_column(
                db_alias, table_name, param_name, mock_metadata_list
            )
            
            if result:
                matched_table, matched_column, column_info = result
                print(f"参数 '{param_name}' 在表 '{table_name}' 中找到匹配: {matched_column} ({column_info.get('type')})")
            else:
                print(f"参数 '{param_name}' 在表 '{table_name}' 中未找到匹配列")
        
        return True
        
    except Exception as e:
        print(f"测试查找匹配列时发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("开始测试数据值获取功能")
    print("=" * 60)
    
    # 运行所有测试
    test_results = []
    
    # 测试1: 数据值获取器基本功能
    print("\n[测试1] 数据值获取器基本功能")
    result1 = test_data_value_fetcher_basic()
    test_results.append(("数据值获取器基本功能", result1))
    
    # 测试2: 查找匹配列功能
    print("\n[测试2] 查找匹配列功能")
    result2 = test_find_matching_column()
    test_results.append(("查找匹配列功能", result2))
    
    # 测试3: 参数提取器集成
    print("\n[测试3] 参数提取器与数据值获取器集成")
    result3 = test_param_extractor_with_data_fetcher()
    test_results.append(("参数提取器集成", result3))
    
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
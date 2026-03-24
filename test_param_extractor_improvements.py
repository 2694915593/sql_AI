#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试参数提取器的改进功能
"""

import sys
import os

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(current_dir, 'sql_ai_analyzer')
sys.path.insert(0, current_dir)
sys.path.insert(0, project_root)

from sql_ai_analyzer.data_collector.param_extractor import ParamExtractor

def test_param_type_detection():
    """测试参数类型检测"""
    print("测试参数类型检测")
    print("=" * 80)
    
    test_cases = [
        {
            "sql": "SELECT * FROM users WHERE id = #{user_id} AND name = #{user_name}",
            "description": "用户查询",
            "expected_params": [
                {"param": "user_id", "expected_type": "number"},
                {"param": "user_name", "expected_type": "string"}
            ]
        },
        {
            "sql": "UPDATE products SET price = #{product_price} WHERE category = #{category_name} AND is_active = #{active_flag}",
            "description": "产品更新",
            "expected_params": [
                {"param": "product_price", "expected_type": "number"},
                {"param": "category_name", "expected_type": "string"},
                {"param": "active_flag", "expected_type": "boolean"}
            ]
        },
        {
            "sql": "INSERT INTO orders (order_id, amount, order_time, status) VALUES (#{order_id}, #{order_amount}, #{order_time}, #{order_status})",
            "description": "订单插入",
            "expected_params": [
                {"param": "order_id", "expected_type": "number"},
                {"param": "order_amount", "expected_type": "number"},
                {"param": "order_time", "expected_type": "datetime"},
                {"param": "order_status", "expected_type": "string"}
            ]
        },
        {
            "sql": "DELETE FROM logs WHERE create_time = #{create_time} AND start_time = #{start_time} AND end_time = #{end_time}",
            "description": "日志删除",
            "expected_params": [
                {"param": "create_time", "expected_type": "datetime"},
                {"param": "start_time", "expected_type": "datetime"},
                {"param": "end_time", "expected_type": "datetime"}
            ]
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n测试 {i}: {test_case['description']}")
        print(f"SQL: {test_case['sql']}")
        
        extractor = ParamExtractor(test_case['sql'])
        params = extractor.extract_params()
        
        print(f"提取到的参数数量: {len(params)}")
        
        for j, (actual_param, expected_info) in enumerate(zip(params, test_case['expected_params']), 1):
            print(f"\n  参数 {j}:")
            print(f"    参数名: {actual_param['param']}")
            print(f"    检测类型: {actual_param['type']}")
            print(f"    期望类型: {expected_info['expected_type']}")
            
            if actual_param['param'] == expected_info['param']:
                print("    参数名匹配: ✓")
            else:
                print(f"    参数名匹配: ✗ (期望: {expected_info['param']}, 实际: {actual_param['param']})")
            
            if actual_param['type'] == expected_info['expected_type']:
                print("    类型匹配: ✓")
            else:
                print(f"    类型匹配: ✗ (期望: {expected_info['expected_type']}, 实际: {actual_param['type']})")

def test_param_replacement():
    """测试参数替换"""
    print("\n\n测试参数替换")
    print("=" * 80)
    
    test_cases = [
        {
            "sql": "SELECT * FROM users WHERE id = #{user_id} AND name = #{user_name}",
            "description": "用户查询参数替换"
        },
        {
            "sql": "UPDATE products SET price = #{price} WHERE category = #{category} AND is_active = #{active}",
            "description": "产品更新参数替换"
        },
        {
            "sql": "INSERT INTO orders (order_id, amount, order_time) VALUES (#{order_id}, #{amount}, #{order_time})",
            "description": "订单插入参数替换"
        },
        {
            "sql": "DELETE FROM logs WHERE batch_time = #{batch_time} AND start = #{start} AND end = #{end}",
            "description": "日志删除参数替换"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n测试 {i}: {test_case['description']}")
        print(f"原始SQL: {test_case['sql']}")
        
        extractor = ParamExtractor(test_case['sql'])
        replaced_sql, tables = extractor.generate_replaced_sql()
        
        print(f"替换后SQL: {replaced_sql}")
        print(f"涉及的表: {tables}")
        
        # 检查参数是否被正确替换
        if '#{' in replaced_sql:
            print("参数替换状态: ✗ (仍有未替换的参数)")
        else:
            print("参数替换状态: ✓ (所有参数已替换)")

def test_metadata_based_param_type():
    """测试基于元数据的参数类型检测"""
    print("\n\n测试基于元数据的参数类型检测")
    print("=" * 80)
    
    # 模拟表元数据
    metadata_list = [
        {
            'table_name': 'users',
            'columns': [
                {'name': 'id', 'type': 'int'},
                {'name': 'name', 'type': 'varchar'},
                {'name': 'email', 'type': 'varchar'},
                {'name': 'is_active', 'type': 'boolean'},
                {'name': 'created_at', 'type': 'datetime'}
            ]
        },
        {
            'table_name': 'orders',
            'columns': [
                {'name': 'order_id', 'type': 'int'},
                {'name': 'amount', 'type': 'decimal'},
                {'name': 'order_date', 'type': 'date'},
                {'name': 'status', 'type': 'varchar'}
            ]
        }
    ]
    
    test_cases = [
        {
            "sql": "SELECT * FROM users WHERE id = #{user_id} AND is_active = #{active_status}",
            "description": "使用元数据改进参数类型检测",
            "metadata": metadata_list
        },
        {
            "sql": "UPDATE orders SET amount = #{order_amount} WHERE order_id = #{order_id}",
            "description": "订单表参数类型检测",
            "metadata": metadata_list
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n测试 {i}: {test_case['description']}")
        print(f"SQL: {test_case['sql']}")
        
        extractor = ParamExtractor(test_case['sql'], metadata_list=test_case['metadata'])
        params = extractor.extract_params()
        
        print(f"提取到的参数数量: {len(params)}")
        
        for j, param in enumerate(params, 1):
            print(f"\n  参数 {j}:")
            print(f"    参数名: {param['param']}")
            print(f"    检测类型: {param['type']}")
            
            # 根据参数名猜测期望类型
            if 'id' in param['param'].lower():
                expected_type = 'number'
            elif 'amount' in param['param'].lower():
                expected_type = 'number'
            elif 'active' in param['param'].lower():
                expected_type = 'boolean'
            elif 'date' in param['param'].lower() or 'time' in param['param'].lower():
                expected_type = 'datetime'
            else:
                expected_type = 'string'
            
            print(f"    期望类型: {expected_type}")
            
            if param['type'] == expected_type:
                print("    类型匹配: ✓")
            else:
                print(f"    类型匹配: ✗")

def main():
    """主函数"""
    print("参数提取器改进功能测试")
    print("=" * 80)
    
    test_param_type_detection()
    test_param_replacement()
    test_metadata_based_param_type()
    
    print("\n" + "=" * 80)
    print("测试完成")

if __name__ == '__main__':
    main()
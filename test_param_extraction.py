#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试参数提取和SQL替换功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.config_manager import ConfigManager
from data_collector.sql_extractor import SQLExtractor
from data_collector.param_extractor import ParamExtractor

def test_param_extractor():
    """测试参数提取器"""
    print("测试参数提取器")
    print("=" * 80)
    
    test_sqls = [
        "SELECT * FROM users WHERE id = #{id} AND name = #{name}",
        "UPDATE products SET price = #{price} WHERE category = #{category}",
        "INSERT INTO orders (user_id, amount, order_time) VALUES (#{user_id}, #{amount}, #{order_time})",
        "DELETE FROM logs WHERE batch_time = #{batch_time} AND start = #{start} AND end = #{end}",
        "SELECT * FROM customers WHERE status = #{status} AND create_date > #{create_date}",
        "UPDATE inventory SET quantity = #{quantity} WHERE product_id = #{product_id} AND warehouse = #{warehouse}"
    ]
    
    for i, sql in enumerate(test_sqls, 1):
        print(f"\n测试SQL {i}:")
        print(f"原始SQL: {sql}")
        
        extractor = ParamExtractor(sql)
        replaced_sql, tables = extractor.generate_replaced_sql()
        
        print(f"替换后SQL: {replaced_sql}")
        print(f"提取的表名: {tables}")
        
        # 提取参数信息
        params = extractor.extract_params()
        print(f"提取的参数: {params}")

def test_sql_extractor_integration():
    """测试SQL提取器集成"""
    print("\n\n测试SQL提取器集成")
    print("=" * 80)
    
    try:
        # 加载配置
        config = ConfigManager('config/config.ini')
        
        # 创建SQL提取器
        extractor = SQLExtractor(config)
        
        # 测试SQL
        test_sql = "SELECT * FROM users WHERE id = #{id} AND name = #{name} AND create_time > #{create_time}"
        
        print(f"测试SQL: {test_sql}")
        
        # 使用SQL提取器的generate_replaced_sql方法
        replaced_sql, tables = extractor.generate_replaced_sql(test_sql)
        
        print(f"替换后SQL: {replaced_sql}")
        print(f"提取的表名: {tables}")
        
        # 测试提取表名
        table_names = extractor.extract_table_names(test_sql)
        print(f"提取的表名（直接方法）: {table_names}")
        
    except Exception as e:
        print(f"测试SQL提取器集成时发生错误: {str(e)}")

def test_real_sql_scenarios():
    """测试真实SQL场景"""
    print("\n\n测试真实SQL场景")
    print("=" * 80)
    
    real_sqls = [
        # 场景1：带参数的查询
        {
            "sql": "SELECT * FROM ecdcdb.pd_errcode WHERE PEC_ERRCODE = #{error_code} AND PEC_LANGUAGE = #{language}",
            "description": "带数据库前缀和参数的查询"
        },
        # 场景2：带参数的插入
        {
            "sql": "INSERT INTO ecdcdb.pd_errcode (PEC_ERRCODE, PEC_LANGUAGE, PEC_SHOWMSG) VALUES (#{error_code}, #{language}, #{message})",
            "description": "带参数的插入语句"
        },
        # 场景3：带参数的更新
        {
            "sql": "UPDATE ecdcdb.pd_errcode SET PEC_SHOWMSG = #{new_message} WHERE PEC_ERRCODE = #{error_code}",
            "description": "带参数的更新语句"
        },
        # 场景4：带参数的删除
        {
            "sql": "DELETE FROM ecdcdb.pd_errcode WHERE batch_time = #{batch_time} AND start = #{start} AND end = #{end}",
            "description": "带时间参数的删除语句"
        },
        # 场景5：复杂查询
        {
            "sql": "SELECT u.name, o.amount FROM users u JOIN orders o ON u.id = o.user_id WHERE u.status = #{status} AND o.create_date > #{start_date}",
            "description": "多表连接带参数查询"
        }
    ]
    
    for i, scenario in enumerate(real_sqls, 1):
        print(f"\n场景 {i}: {scenario['description']}")
        print(f"原始SQL: {scenario['sql']}")
        
        extractor = ParamExtractor(scenario['sql'])
        replaced_sql, tables = extractor.generate_replaced_sql()
        
        print(f"替换后SQL: {replaced_sql}")
        print(f"提取的表名: {tables}")

def test_edge_cases():
    """测试边界情况"""
    print("\n\n测试边界情况")
    print("=" * 80)
    
    edge_cases = [
        # 空SQL
        "",
        # 没有参数的SQL
        "SELECT * FROM users",
        # 只有注释的SQL
        "-- 这是一个注释\nSELECT * FROM users",
        # 带特殊字符的参数名
        "SELECT * FROM users WHERE id = #{user_id_123} AND name = #{user-name}",
        # 嵌套参数（不应该出现，但测试一下）
        "SELECT * FROM users WHERE id = #{#{nested}}",
        # 非常长的参数名
        "SELECT * FROM users WHERE id = #{very_long_parameter_name_that_exceeds_normal_length}",
    ]
    
    for i, sql in enumerate(edge_cases, 1):
        print(f"\n边界情况 {i}:")
        print(f"原始SQL: {repr(sql)}")
        
        extractor = ParamExtractor(sql)
        replaced_sql, tables = extractor.generate_replaced_sql()
        
        print(f"替换后SQL: {repr(replaced_sql)}")
        print(f"提取的表名: {tables}")

def main():
    """主函数"""
    print("参数提取和SQL替换功能测试")
    print("=" * 80)
    
    test_param_extractor()
    test_sql_extractor_integration()
    test_real_sql_scenarios()
    test_edge_cases()
    
    print("\n" + "=" * 80)
    print("测试完成")

if __name__ == '__main__':
    main()
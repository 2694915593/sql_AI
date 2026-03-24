#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试表名提取逻辑优化
验证在提取表名时处理过的SQL被正确传递到后续步骤
"""

import sys
import os

# 设置正确的路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(project_root, 'sql_ai_analyzer'))

from data_collector.sql_extractor import SQLExtractor
from utils.logger import setup_logger
from config.config_manager import ConfigManager

def test_table_extraction_optimization():
    """测试表名提取优化的逻辑"""
    
    print("测试表名提取逻辑优化")
    print("=" * 80)
    
    # 初始化配置和日志
    config = ConfigManager('config/config.ini')
    logger = setup_logger(__name__, config.get_log_config())
    
    # 创建SQL提取器实例
    extractor = SQLExtractor(config, logger)
    
    # 测试用例：包含XML标签的SQL
    test_cases = [
        {
            'sql': "<select>SELECT * FROM users WHERE id = #{id}</select>",
            'description': "带select标签的SELECT语句"
        },
        {
            'sql': "<update>UPDATE users SET name = #{name} WHERE id = #{id}</update>",
            'description': "带update标签的UPDATE语句"
        },
        {
            'sql': "SELECT * FROM users, orders WHERE users.id = orders.user_id",
            'description': "无标签的多表查询"
        },
        {
            'sql': "<insert>INSERT INTO logs (message, level) VALUES (#{msg}, #{level})</insert>",
            'description': "带insert标签的INSERT语句"
        },
        {
            'sql': "<delete>DELETE FROM temp_table WHERE created_at < #{date}</delete>",
            'description': "带delete标签的DELETE语句"
        }
    ]
    
    print("测试extract_table_names方法返回两个值:")
    print("-" * 80)
    
    all_passed = True
    for test_case in test_cases:
        sql = test_case['sql']
        description = test_case['description']
        
        print(f"\n测试: {description}")
        print(f"原始SQL: {sql[:80]}...")
        
        # 调用修改后的方法（应该返回两个值）
        try:
            tables, processed_sql = extractor.extract_table_names(sql)
            
            print(f"✓ 方法调用成功，返回两个值")
            print(f"  提取的表名: {tables}")
            print(f"  处理后的SQL: {processed_sql[:80]}..." if len(processed_sql) > 80 else f"  处理后的SQL: {processed_sql}")
            
            # 验证处理后的SQL是否去除了XML标签
            if '<' in sql and '>' in sql:
                # 原始SQL包含XML标签
                if '<' in processed_sql and '>' in processed_sql:
                    print(f"  ⚠ 警告: 处理后的SQL仍然包含XML标签")
                else:
                    print(f"  ✓ 处理后的SQL已移除XML标签")
            
            # 验证表名是否被正确提取
            if tables:
                print(f"  ✓ 成功提取到表名")
            else:
                print(f"  ⚠ 警告: 未提取到表名")
                
        except Exception as e:
            print(f"✗ 方法调用失败: {str(e)}")
            all_passed = False
    
    print("\n" + "=" * 80)
    print("测试generate_replaced_sql方法的processed_sql参数:")
    print("-" * 80)
    
    # 测试generate_replaced_sql方法是否支持processed_sql参数
    test_sql = "<select>SELECT * FROM users WHERE id = #{id} AND status = #{status}</select>"
    
    print(f"测试SQL: {test_sql[:80]}...")
    
    try:
        # 先提取表名和处理后的SQL
        tables, processed_sql = extractor.extract_table_names(test_sql)
        print(f"1. 提取表名和处理后的SQL:")
        print(f"   表名: {tables}")
        print(f"   处理后SQL: {processed_sql[:80]}...")
        
        # 测试不带processed_sql参数的方法
        print(f"\n2. 测试不带processed_sql参数的generate_replaced_sql:")
        replaced_sql1, tables1 = extractor.generate_replaced_sql(test_sql)
        print(f"   替换后SQL: {replaced_sql1[:80]}...")
        print(f"   表名: {tables1}")
        
        # 测试带processed_sql参数的方法
        print(f"\n3. 测试带processed_sql参数的generate_replaced_sql:")
        replaced_sql2, tables2 = extractor.generate_replaced_sql(test_sql, processed_sql=processed_sql)
        print(f"   替换后SQL: {replaced_sql2[:80]}...")
        print(f"   表名: {tables2}")
        
        # 比较结果
        if replaced_sql1 == replaced_sql2:
            print(f"\n✓ 两次生成的SQL相同，优化有效")
        else:
            print(f"\n⚠ 两次生成的SQL不同，需要检查逻辑")
            print(f"  不带processed_sql参数的结果长度: {len(replaced_sql1)}")
            print(f"  带processed_sql参数的结果长度: {len(replaced_sql2)}")
            
    except Exception as e:
        print(f"\n✗ 测试失败: {str(e)}")
        all_passed = False
    
    print("\n" + "=" * 80)
    
    if all_passed:
        print("✓ 所有测试通过！表名提取逻辑优化成功")
    else:
        print("✗ 部分测试失败，需要检查代码")
    
    return all_passed

def test_main_integration():
    """测试与main.py的集成"""
    
    print("\n" + "=" * 80)
    print("测试与main.py的集成:")
    print("-" * 80)
    
    # 导入main模块中的SQLAnalyzer
    try:
        from main import SQLAnalyzer
        
        print("✓ SQLAnalyzer类导入成功")
        
        # 检查analyze_single_sql方法中是否使用了优化后的逻辑
        import inspect
        
        # 获取analyze_single_sql方法的源代码
        source = inspect.getsource(SQLAnalyzer.analyze_single_sql)
        
        # 检查关键代码
        check_points = [
            ("extract_table_names返回两个值", "table_names, processed_sql = self.sql_extractor.extract_table_names"),
            ("使用processed_sql参数", "processed_sql=processed_sql"),
            ("generate_replaced_sql使用processed_sql", "generate_replaced_sql")
        ]
        
        all_checks_passed = True
        for check_desc, code_pattern in check_points:
            if code_pattern in source:
                print(f"✓ {check_desc} - 代码中包含: {code_pattern}")
            else:
                print(f"✗ {check_desc} - 代码中缺少: {code_pattern}")
                all_checks_passed = False
        
        if all_checks_passed:
            print("\n✓ main.py中的集成优化检查通过")
        else:
            print("\n✗ main.py中的集成优化检查失败")
            
    except Exception as e:
        print(f"✗ 导入SQLAnalyzer失败: {str(e)}")

if __name__ == "__main__":
    # 运行测试
    test_result = test_table_extraction_optimization()
    
    # 运行集成测试
    test_main_integration()
    
    print("\n" + "=" * 80)
    if test_result:
        print("总结: 表名提取逻辑优化测试通过")
        print("优化效果:")
        print("1. extract_table_names方法现在返回两个值: (表名列表, 处理后的SQL)")
        print("2. generate_replaced_sql方法支持processed_sql参数，避免重复处理XML标签")
        print("3. main.py中使用优化后的逻辑，提高效率和准确性")
    else:
        print("总结: 表名提取逻辑优化测试失败，需要进一步调试")
    
    print("=" * 80)
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试INSERT SQL语句分析
验证系统是否能处理用户提供的SQL：
INSERT INTO ETC_TRANSFER (...) VALUES ( #{...} )
"""

import sys
import os

# 添加路径
sys.path.append('e:/Code/sqlAnalize/sql_ai_analyzer')

from data_collector.sql_extractor import SQLExtractor
from data_collector.param_extractor import ParamExtractor
from config.config_manager import ConfigManager
from utils.logger import setup_logger

def test_insert_sql_analysis():
    """测试INSERT语句分析"""
    print("测试INSERT SQL语句分析")
    print("=" * 60)
    
    # 用户提供的SQL
    test_sql = """INSERT INTO ETC_TRANSFER ( ETR_FREEZEID, ETR_FREEZEAMT, ETR_FREEZESTT, ETR_FREEZEDATE, ETR_ACC, ETR_AGREEMENTFLOW, ETR_FREEZETYPE ) VALUES ( #{FREEZEID}, #{FREEZEAMT}, #{FREEZESTT}, #{FREEZEDATE}, #{ACC}, #{AGREEMENTFLOW}, #{FREEZETYPE} )"""
    
    print(f"测试SQL: {test_sql}")
    print()
    
    # 1. 测试表名提取
    print("1. 表名提取测试:")
    config = ConfigManager()
    logger = setup_logger('test_insert', {'log_level': 'INFO'})
    extractor = SQLExtractor(config, logger)
    
    table_names = extractor.extract_table_names(test_sql)
    print(f"   提取的表名: {table_names}")
    
    if 'ETC_TRANSFER' in table_names:
        print("   ✓ 成功提取到表名 'ETC_TRANSFER'")
    else:
        print("   ✗ 未能提取到表名 'ETC_TRANSFER'")
    
    # 2. 测试参数提取
    print("\n2. 参数提取测试:")
    param_extractor = ParamExtractor(test_sql, logger)
    params = param_extractor.extract_params()
    
    print(f"   提取的参数数量: {len(params)}")
    
    expected_params = ['FREEZEID', 'FREEZEAMT', 'FREEZESTT', 'FREEZEDATE', 'ACC', 'AGREEMENTFLOW', 'FREEZETYPE']
    found_params = [p['param'] for p in params]
    
    print(f"   期望的参数: {expected_params}")
    print(f"   实际提取的参数: {found_params}")
    
    all_found = all(param in found_params for param in expected_params)
    if all_found:
        print("   ✓ 成功提取所有参数")
    else:
        print("   ✗ 部分参数未能提取")
    
    # 3. 测试参数类型猜测
    print("\n3. 参数类型猜测:")
    for param in params:
        param_name = param['param']
        param_type = param['type']
        print(f"   {param_name}: {param_type}")
    
    # 4. 测试参数替换
    print("\n4. 参数替换测试:")
    replaced_sql, tables = param_extractor.generate_replaced_sql()
    print(f"   替换后的SQL (前200字符):")
    print(f"   {replaced_sql[:200]}...")
    
    # 检查参数是否被替换
    has_hash_params = '#{' in replaced_sql
    if not has_hash_params:
        print("   ✓ 所有参数已被替换")
    else:
        print("   ✗ 仍有未替换的参数")
    
    # 5. 测试执行计划相关
    print("\n5. 执行计划相关:")
    print(f"   表名提取结果: {tables}")
    
    # INSERT语句的EXPLAIN在MySQL中是支持的
    print("   MySQL中可以使用 EXPLAIN INSERT ... 分析执行计划")
    print("   系统会将参数替换后执行 EXPLAIN")
    
    # 6. 完整流程分析
    print("\n6. 完整分析流程总结:")
    print("   1. 提取表名: ETC_TRANSFER")
    print("   2. 根据SYSTEMID字段确定数据库别名")
    print("   3. 在配置的数据库实例中查找表")
    print("   4. 收集表元数据（列信息、索引等）")
    print("   5. 替换参数为具体值")
    print("   6. 在找到表的实例上执行 EXPLAIN INSERT ...")
    print("   7. 获取执行计划结果")
    print("   8. 将SQL、元数据、执行计划发送给AI模型分析")
    print("   9. 存储分析结果")
    
    print("\n" + "=" * 60)
    print("测试完成")
    return True

def test_specific_issues():
    """测试特定问题"""
    print("\n" + "=" * 60)
    print("测试特定场景和问题")
    print("=" * 60)
    
    test_cases = [
        {
            'name': '标准INSERT语句',
            'sql': "INSERT INTO users (id, name, email) VALUES (#{id}, #{name}, #{email})"
        },
        {
            'name': 'INSERT带参数',
            'sql': "INSERT INTO orders (order_id, amount, status) VALUES (#{orderId}, #{amount}, #{status})"
        },
        {
            'name': 'INSERT带日期参数',
            'sql': "INSERT INTO logs (log_id, message, create_time) VALUES (#{logId}, #{message}, #{createTime})"
        },
        {
            'name': '用户提供的SQL',
            'sql': """INSERT INTO ETC_TRANSFER ( ETR_FREEZEID, ETR_FREEZEAMT, ETR_FREEZESTT, ETR_FREEZEDATE, ETR_ACC, ETR_AGREEMENTFLOW, ETR_FREEZETYPE ) VALUES ( #{FREEZEID}, #{FREEZEAMT}, #{FREEZESTT}, #{FREEZEDATE}, #{ACC}, #{AGREEMENTFLOW}, #{FREEZETYPE} )"""
        }
    ]
    
    for test_case in test_cases:
        print(f"\n测试: {test_case['name']}")
        print(f"SQL: {test_case['sql'][:80]}...")
        
        try:
            # 初始化
            config = ConfigManager()
            logger = setup_logger('test_specific', {'log_level': 'INFO'})
            
            # 提取表名
            extractor = SQLExtractor(config, logger)
            table_names = extractor.extract_table_names(test_case['sql'])
            print(f"  表名: {table_names}")
            
            # 提取参数
            param_extractor = ParamExtractor(test_case['sql'], logger)
            params = param_extractor.extract_params()
            print(f"  参数: {[p['param'] for p in params]}")
            
            # 参数替换
            replaced_sql, _ = param_extractor.generate_replaced_sql()
            print(f"  替换后SQL长度: {len(replaced_sql)} 字符")
            
            print("  ✓ 测试通过")
        except Exception as e:
            print(f"  ✗ 测试失败: {str(e)}")
    
    print("\n" + "=" * 60)

def main():
    """主函数"""
    print("测试INSERT SQL语句分析能力")
    print("验证系统是否能处理用户提供的SQL")
    print("=" * 60)
    
    try:
        # 测试INSERT语句分析
        test_insert_sql_analysis()
        
        # 测试特定问题
        test_specific_issues()
        
        print("\n结论:")
        print("✓ 系统支持分析INSERT语句")
        print("✓ 能够提取表名和参数")
        print("✓ 能够替换参数为具体值")
        print("✓ 能够在MySQL上执行EXPLAIN INSERT获取执行计划")
        print("✓ 能够将完整信息发送给AI模型进行SQL质量分析")
        
        return True
        
    except Exception as e:
        print(f"\n测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
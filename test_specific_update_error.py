#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试特定UPDATE语句的问题
"""

import sys
import os

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(current_dir, 'sql_ai_analyzer')
sys.path.insert(0, current_dir)
sys.path.insert(0, project_root)

from sql_ai_analyzer.data_collector.param_extractor import ParamExtractor
from sql_ai_analyzer.config.config_manager import ConfigManager
from sql_ai_analyzer.data_collector.metadata_collector import MetadataCollector

def test_update_sql():
    """测试有问题的UPDATE语句"""
    print("测试特定UPDATE语句的问题")
    print("=" * 80)
    
    # 用户提供的SQL语句
    sql = "UPDATE CPWC_CUSTOMER_REMARK SET REMARK=#{REMARK}, DESCRIPION=#{DESCRIPTION}, REMARK_MOBILES=#{PHONE}, REMARK_CORP_NAME=#{REMARKCORPNAME},UPDATE_TIME=#{UPDATETIME},TYPE=#{TYPE} WHERE USER_EUIFID=#{USERID} AND EXTERNAL_USERID=#{EXTERNALUSERID}"
    
    print(f"原始SQL: {sql}")
    print("\n1. 检查SQL语法问题...")
    
    # 检查可能的语法问题
    # 1. 字段名DESCRIPION可能是拼写错误（应该是DESCRIPTION）
    if "DESCRIPION" in sql:
        print("警告: 字段名 'DESCRIPION' 可能是拼写错误，应该是 'DESCRIPTION'")
    
    # 2. 检查参数格式
    param_pattern = r'#\{([^}]+)\}'
    import re
    params = re.findall(param_pattern, sql)
    print(f"找到的参数: {params}")
    
    print("\n2. 测试参数提取...")
    extractor = ParamExtractor(sql)
    extracted_params = extractor.extract_params()
    print(f"提取的参数数量: {len(extracted_params)}")
    for p in extracted_params:
        print(f"  参数: {p['param']}, 类型: {p['type']}")
    
    print("\n3. 测试参数替换...")
    replaced_sql, tables = extractor.generate_replaced_sql()
    print(f"替换后SQL: {replaced_sql}")
    print(f"涉及的表: {tables}")
    
    # 检查替换后的SQL语法
    print("\n4. 检查替换后SQL的语法...")
    if '#{' in replaced_sql:
        print("错误: 替换后SQL中仍有未替换的参数")
    
    # 检查UPDATE语句的SET部分
    set_match = re.search(r'SET\s+(.+?)\s+WHERE', replaced_sql, re.IGNORECASE | re.DOTALL)
    if set_match:
        set_clause = set_match.group(1)
        print(f"SET子句: {set_clause}")
        
        # 检查SET子句中的字段赋值
        assignments = set_clause.split(',')
        print(f"赋值语句数量: {len(assignments)}")
        for i, assignment in enumerate(assignments):
            print(f"  赋值 {i+1}: {assignment.strip()}")
    
    print("\n5. 测试执行计划获取...")
    try:
        config = ConfigManager('sql_ai_analyzer/config/config.ini')
        collector = MetadataCollector(config)
        
        db_alias = "db_production"
        result = collector.get_execution_plan(db_alias, replaced_sql)
        
        print(f"SQL类型: {result.get('sql_type', 'UNKNOWN')}")
        print(f"是否有执行计划: {result.get('has_execution_plan', False)}")
        
        if result.get('has_execution_plan'):
            execution_plan = result.get('execution_plan', {})
            print(f"执行计划类型: {type(execution_plan)}")
            if isinstance(execution_plan, list) and execution_plan:
                print("第一行执行计划:")
                for key, value in execution_plan[0].items():
                    print(f"  {key}: {value}")
        else:
            print(f"消息: {result.get('message', '无消息')}")
            if 'error' in result:
                print(f"错误: {result['error']}")
    except Exception as e:
        print(f"获取执行计划时发生错误: {str(e)}")
        import traceback
        traceback.print_exc()

def test_fixed_sql():
    """测试修复后的SQL"""
    print("\n\n测试修复后的SQL")
    print("=" * 80)
    
    # 修复字段名拼写错误
    fixed_sql = "UPDATE CPWC_CUSTOMER_REMARK SET REMARK=#{REMARK}, DESCRIPTION=#{DESCRIPTION}, REMARK_MOBILES=#{PHONE}, REMARK_CORP_NAME=#{REMARKCORPNAME},UPDATE_TIME=#{UPDATETIME},TYPE=#{TYPE} WHERE USER_EUIFID=#{USERID} AND EXTERNAL_USERID=#{EXTERNALUSERID}"
    
    print(f"修复后SQL: {fixed_sql}")
    
    print("\n1. 测试参数提取...")
    extractor = ParamExtractor(fixed_sql)
    extracted_params = extractor.extract_params()
    print(f"提取的参数数量: {len(extracted_params)}")
    for p in extracted_params:
        print(f"  参数: {p['param']}, 类型: {p['type']}")
    
    print("\n2. 测试参数替换...")
    replaced_sql, tables = extractor.generate_replaced_sql()
    print(f"替换后SQL: {replaced_sql}")
    print(f"涉及的表: {tables}")

def main():
    """主函数"""
    print("分析UPDATE语句问题")
    print("=" * 80)
    
    test_update_sql()
    test_fixed_sql()
    
    print("\n" + "=" * 80)
    print("分析完成")

if __name__ == '__main__':
    main()
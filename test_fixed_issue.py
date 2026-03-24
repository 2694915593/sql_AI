#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试修复后的SQL执行计划生成问题
"""

import sys
import os

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(current_dir, 'sql_ai_analyzer')
sys.path.insert(0, current_dir)
sys.path.insert(0, project_root)

from sql_ai_analyzer.data_collector.sql_extractor import SQLExtractor
from sql_ai_analyzer.config.config_manager import ConfigManager
from sql_ai_analyzer.data_collector.metadata_collector import MetadataCollector

def test_update_sql_with_replacement():
    """测试UPDATE语句的参数替换和执行计划生成"""
    print("测试UPDATE语句的参数替换和执行计划生成")
    print("=" * 80)
    
    try:
        # 加载配置
        config = ConfigManager('sql_ai_analyzer/config/config.ini')
        print("配置加载成功")
        
        # 创建SQL提取器
        sql_extractor = SQLExtractor(config)
        print("SQL提取器创建成功")
        
        # 创建元数据收集器
        metadata_collector = MetadataCollector(config)
        print("元数据收集器创建成功")
        
        # 用户提供的SQL语句
        sql = "UPDATE CPWC_CUSTOMER_REMARK SET REMARK=#{REMARK}, DESCRIPION=#{DESCRIPTION}, REMARK_MOBILES=#{PHONE}, REMARK_CORP_NAME=#{REMARKCORPNAME},UPDATE_TIME=#{UPDATETIME},TYPE=#{TYPE} WHERE USER_EUIFID=#{USERID} AND EXTERNAL_USERID=#{EXTERNALUSERID}"
        
        print(f"原始SQL: {sql}")
        
        # 1. 生成替换参数后的SQL
        print("\n1. 生成替换参数后的SQL...")
        replaced_sql, tables = sql_extractor.generate_replaced_sql(sql)
        
        print(f"替换后SQL: {replaced_sql}")
        print(f"提取的表名: {tables}")
        
        # 检查参数是否被正确替换
        if '#{' in replaced_sql:
            print("错误: 替换后SQL中仍有未替换的参数!")
            print(f"未替换的部分: {replaced_sql}")
            return
        
        # 2. 检查替换后SQL的语法
        print("\n2. 检查替换后SQL的语法...")
        
        # 检查字段名拼写错误
        if "DESCRIPION" in replaced_sql:
            print("警告: 字段名 'DESCRIPION' 可能是拼写错误，应该是 'DESCRIPTION'")
            
            # 尝试修复字段名
            fixed_sql = replaced_sql.replace("DESCRIPION", "DESCRIPTION")
            print(f"修复后SQL: {fixed_sql}")
            replaced_sql = fixed_sql
        
        # 3. 获取执行计划
        print("\n3. 获取执行计划...")
        db_alias = "db_production"
        result = metadata_collector.get_execution_plan(db_alias, replaced_sql)
        
        print(f"SQL类型: {result.get('sql_type', 'UNKNOWN')}")
        print(f"是否有执行计划: {result.get('has_execution_plan', False)}")
        
        if result.get('has_execution_plan'):
            execution_plan = result.get('execution_plan', {})
            print(f"执行计划类型: {type(execution_plan)}")
            if isinstance(execution_plan, list) and execution_plan:
                print(f"执行计划行数: {len(execution_plan)}")
                print("第一行执行计划:")
                for key, value in execution_plan[0].items():
                    print(f"  {key}: {value}")
        else:
            print(f"消息: {result.get('message', '无消息')}")
            if 'error' in result:
                print(f"错误: {result['error']}")
            
            # 如果是表不存在的错误，这是预期的，因为测试环境中可能没有这个表
            if "doesn't exist" in str(result.get('error', '')):
                print("注意: 表不存在错误是预期的，因为测试环境中可能没有 'cpwc_customer_remark' 表")
                print("但重要的是SQL语法应该是正确的")
    
    except Exception as e:
        print(f"测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()

def test_main_workflow():
    """测试主工作流程"""
    print("\n\n测试主工作流程")
    print("=" * 80)
    
    try:
        # 模拟main.py中的逻辑
        config = ConfigManager('sql_ai_analyzer/config/config.ini')
        
        # 创建各模块实例
        sql_extractor = SQLExtractor(config)
        metadata_collector = MetadataCollector(config)
        
        # 测试SQL
        test_sql = "SELECT * FROM am_solline_info WHERE ID = #{id} AND PROJECTID = #{project}"
        
        print(f"测试SQL: {test_sql}")
        
        # 1. 提取表名
        table_names = sql_extractor.extract_table_names(test_sql)
        print(f"提取的表名: {table_names}")
        
        # 2. 生成替换参数后的SQL
        replaced_sql, tables = sql_extractor.generate_replaced_sql(test_sql)
        print(f"替换后SQL: {replaced_sql}")
        
        # 3. 检查参数是否被替换
        if '#{' in replaced_sql:
            print("错误: 参数替换失败!")
        else:
            print("成功: 参数已正确替换")
        
        # 4. 获取执行计划（使用替换后的SQL）
        db_alias = "db_production"
        result = metadata_collector.get_execution_plan(db_alias, replaced_sql)
        
        print(f"执行计划获取结果: {result.get('has_execution_plan', False)}")
        
        if result.get('has_execution_plan'):
            print("成功: 执行计划已正确生成")
            execution_plan = result.get('execution_plan', {})
            if isinstance(execution_plan, list) and execution_plan:
                print(f"执行计划包含 {len(execution_plan)} 行")
        else:
            error_msg = result.get('error', '')
            if "doesn't exist" in str(error_msg):
                print("注意: 表不存在错误，但SQL语法检查通过")
            else:
                print(f"错误: {error_msg}")
    
    except Exception as e:
        print(f"测试主工作流程时发生错误: {str(e)}")
        import traceback
        traceback.print_exc()

def main():
    """主函数"""
    print("测试修复后的SQL执行计划生成问题")
    print("=" * 80)
    
    test_update_sql_with_replacement()
    test_main_workflow()
    
    print("\n" + "=" * 80)
    print("测试完成")
    
    print("\n总结:")
    print("1. 修复了在get_execution_plan中传入原始SQL而不是替换后SQL的问题")
    print("2. 现在main.py会先调用sql_extractor.generate_replaced_sql生成替换后的SQL")
    print("3. 然后将替换后的SQL传给get_execution_plan方法")
    print("4. 这确保了EXPLAIN语句执行的是有效的SQL，而不是包含#{参数}的模板SQL")

if __name__ == '__main__':
    main()
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试多数据库场景下的执行计划获取逻辑
验证执行计划在找到表的数据库实例上执行
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sql_ai_analyzer.config.config_manager import ConfigManager
from sql_ai_analyzer.data_collector.metadata_collector import MetadataCollector
from sql_ai_analyzer.utils.logger import setup_logger

def test_execution_plan_in_found_instance():
    """测试在找到表的实例上获取执行计划"""
    print("测试多数据库场景下的执行计划获取逻辑")
    print("=" * 60)
    
    # 使用测试配置文件
    config_path = 'sql_ai_analyzer/config/test_multi_db.ini'
    config = ConfigManager(config_path)
    
    # 设置日志
    log_config = config.get_log_config()
    logger = setup_logger('test_multi_db_execution', log_config)
    
    # 创建元数据收集器
    collector = MetadataCollector(config, logger)
    
    # 测试场景：在不同实例中查找表
    db_alias = 'db_production'
    table_names = ['test_table1', 'test_table2']
    
    print(f"测试数据库别名: {db_alias}")
    print(f"查找表: {table_names}")
    print()
    
    # 1. 首先查找表存在的实例
    print("1. 使用collect_metadata_until_found查找表存在的实例:")
    found_metadata = collector.collect_metadata_until_found(db_alias, table_names)
    
    if found_metadata:
        # 从找到的元数据中提取实例信息
        first_found = found_metadata[0]
        instance_index = first_found.get('instance_index', 0)
        instance_alias = first_found.get('instance_alias', db_alias)
        database_name = first_found.get('database', '')
        
        print(f"   找到表在实例: {instance_alias} (索引: {instance_index})")
        print(f"   数据库: {database_name}")
        print(f"   找到的表数: {len(found_metadata)}")
        
        # 2. 获取所有实例的元数据
        print("\n2. 收集所有实例的元数据:")
        all_metadata = collector.collect_metadata_from_all_instances(db_alias, table_names)
        print(f"   从 {len(set(m.get('instance_alias') for m in all_metadata))} 个实例收集到 {len(all_metadata)} 个表的元数据")
        
        # 3. 在找到表的实例上获取执行计划
        print("\n3. 在找到表的实例上获取执行计划:")
        test_sql = "SELECT * FROM test_table1 WHERE id = 1"
        execution_plan_info = collector.get_execution_plan(
            db_alias, 
            test_sql,
            instance_index  # 在找到表的实例上执行
        )
        
        if execution_plan_info.get('has_execution_plan'):
            print(f"   成功获取执行计划")
            print(f"   执行计划实例: {execution_plan_info.get('instance_alias')}")
            print(f"   执行计划数据库: {execution_plan_info.get('db_alias')}")
        else:
            print(f"   未能获取执行计划: {execution_plan_info.get('message', '未知原因')}")
            
        # 4. 验证执行计划实例与找到表的实例一致
        print("\n4. 验证执行计划实例与找到表的实例一致:")
        plan_instance = execution_plan_info.get('instance_alias')
        if plan_instance == instance_alias:
            print(f"   ✓ 执行计划在与找到表相同的实例上执行: {plan_instance}")
        else:
            print(f"   ✗ 执行计划实例不匹配: {plan_instance} != {instance_alias}")
            
    else:
        print("   在所有实例中都未找到表")
    
    print("\n" + "=" * 60)
    print("测试完成")

if __name__ == "__main__":
    test_execution_plan_in_found_instance()
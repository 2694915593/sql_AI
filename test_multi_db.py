#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多数据库功能测试脚本
测试ConfigManager和MetadataCollector的多数据库支持
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.config_manager import ConfigManager
from data_collector.metadata_collector import MetadataCollector
from utils.logger import get_logger

def test_config_manager():
    """测试配置管理器"""
    print("=" * 60)
    print("测试配置管理器多数据库功能")
    print("=" * 60)
    
    # 使用测试配置文件
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config', 'test_multi_db.ini')
    config_manager = ConfigManager(config_path)
    
    # 测试获取所有数据库别名
    aliases = config_manager.get_all_target_db_aliases()
    print(f"所有数据库别名: {aliases}")
    
    # 测试获取单个数据库的所有配置
    db_alias = 'db_production'
    all_configs = config_manager.get_all_target_db_configs(db_alias)
    print(f"\n数据库 '{db_alias}' 的所有配置 ({len(all_configs)} 个实例):")
    for i, config in enumerate(all_configs):
        print(f"  实例 {i}: {config.get('instance_alias', 'N/A')}")
        print(f"    主机: {config.get('host')}")
        print(f"    端口: {config.get('port')}")
        print(f"    数据库: {config.get('database')}")
        print(f"    实例索引: {config.get('instance_index', 'N/A')}")
    
    # 测试按索引获取配置
    print(f"\n按索引获取数据库配置:")
    for i in range(len(all_configs)):
        config = config_manager.get_target_db_config(db_alias, i)
        print(f"  索引 {i}: {config.get('database')}")
    
    # 测试按索引获取配置（1开始）
    print(f"\n按索引获取数据库配置（1开始）:")
    for i in range(1, len(all_configs) + 1):
        config = config_manager.get_target_db_config_by_index(db_alias, i)
        print(f"  索引 {i}: {config.get('database')}")
    
    # 测试获取单个配置（默认索引0）
    default_config = config_manager.get_target_db_config(db_alias)
    print(f"\n默认配置（索引0）: {default_config.get('database')}")
    
    # 测试其他数据库别名
    test_db_config = config_manager.get_target_db_config('db_test')
    print(f"\n测试数据库配置: {test_db_config.get('database')}")
    
    ecup_config = config_manager.get_target_db_config('ECUP')
    print(f"ECUP数据库配置: {ecup_config.get('database')}")
    
    return config_manager

def test_metadata_collector(config_manager):
    """测试元数据收集器"""
    print("\n" + "=" * 60)
    print("测试元数据收集器多数据库功能")
    print("=" * 60)
    
    # 设置日志
    logger = get_logger('test_multi_db')
    
    # 创建元数据收集器
    metadata_collector = MetadataCollector(config_manager, logger)
    
    # 测试表名（仅用于演示，实际可能需要真实表名）
    table_names = ['test_table1', 'test_table2']
    
    # 测试从特定实例收集元数据
    print(f"测试从特定实例收集元数据:")
    for i in range(3):  # 测试前3个实例
        try:
            print(f"  尝试实例 {i}...")
            metadata_list = metadata_collector.collect_metadata('db_production', table_names, instance_index=i)
            if metadata_list:
                print(f"    实例 {i}: 成功收集到 {len(metadata_list)} 个表的元数据")
                for metadata in metadata_list:
                    table_name = metadata.get('table_name')
                    exists = metadata.get('table_exists', False)
                    print(f"      表 {table_name}: {'存在' if exists else '不存在'}")
            else:
                print(f"    实例 {i}: 未收集到元数据")
        except Exception as e:
            print(f"    实例 {i}: 错误 - {str(e)}")
    
    # 测试从所有实例收集元数据
    print(f"\n测试从所有实例收集元数据:")
    try:
        all_metadata = metadata_collector.collect_metadata_from_all_instances('db_production', table_names)
        print(f"  从所有实例共收集到 {len(all_metadata)} 个表的元数据")
        
        # 按实例分组统计
        instance_stats = {}
        for metadata in all_metadata:
            instance_alias = metadata.get('instance_alias', 'unknown')
            table_name = metadata.get('table_name', 'unknown')
            exists = metadata.get('table_exists', False)
            
            if instance_alias not in instance_stats:
                instance_stats[instance_alias] = {'total': 0, 'exists': 0}
            
            instance_stats[instance_alias]['total'] += 1
            if exists:
                instance_stats[instance_alias]['exists'] += 1
        
        for instance_alias, stats in instance_stats.items():
            print(f"    实例 {instance_alias}: {stats['exists']}/{stats['total']} 个表存在")
    except Exception as e:
        print(f"  错误: {str(e)}")
    
    # 测试依次尝试所有实例查找表
    print(f"\n测试依次尝试所有实例查找表:")
    try:
        metadata_list = metadata_collector.collect_metadata_until_found('db_production', table_names)
        if metadata_list:
            print(f"  找到表的实例: {metadata_list[0].get('instance_alias')}")
            print(f"  找到 {len(metadata_list)} 个表的元数据")
        else:
            print("  在所有实例中都未找到表")
    except Exception as e:
        print(f"  错误: {str(e)}")

def test_execution_plan(config_manager):
    """测试执行计划功能"""
    print("\n" + "=" * 60)
    print("测试执行计划多数据库功能")
    print("=" * 60)
    
    # 设置日志
    logger = get_logger('test_multi_db_plan')
    
    # 创建元数据收集器
    metadata_collector = MetadataCollector(config_manager, logger)
    
    # 测试SQL语句
    test_sql = "SELECT * FROM test_table WHERE id = 1"
    
    # 测试从特定实例获取执行计划
    print(f"测试从特定实例获取执行计划:")
    for i in range(2):  # 测试前2个实例
        try:
            print(f"  尝试实例 {i}...")
            plan_result = metadata_collector.get_execution_plan('db_production', test_sql, instance_index=i)
            
            if plan_result.get('has_execution_plan', False):
                print(f"    实例 {i}: 成功获取执行计划")
                print(f"      SQL类型: {plan_result.get('sql_type')}")
                print(f"      数据库类型: {plan_result.get('db_type')}")
                print(f"      实例别名: {plan_result.get('instance_alias')}")
                
                plan_summary = plan_result.get('plan_summary', {})
                if plan_summary:
                    print(f"      执行计划摘要:")
                    print(f"        是否有全表扫描: {plan_summary.get('has_full_scan', False)}")
                    print(f"        估计行数: {plan_summary.get('estimated_rows', 0)}")
                    print(f"        是否使用索引: {plan_summary.get('key_used', False)}")
                    print(f"        警告: {plan_summary.get('warnings', [])}")
            else:
                print(f"    实例 {i}: 未获取到执行计划 - {plan_result.get('message', '未知原因')}")
                
        except Exception as e:
            print(f"    实例 {i}: 错误 - {str(e)}")

def main():
    """主函数"""
    print("开始测试多数据库功能")
    print("=" * 60)
    
    try:
        # 测试配置管理器
        config_manager = test_config_manager()
        
        # 测试元数据收集器
        test_metadata_collector(config_manager)
        
        # 测试执行计划功能
        test_execution_plan(config_manager)
        
        print("\n" + "=" * 60)
        print("多数据库功能测试完成")
        print("=" * 60)
        
    except Exception as e:
        print(f"测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
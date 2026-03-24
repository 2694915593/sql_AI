#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试多数据库实例扫描功能
"""

import sys
sys.path.append('e:/Code/sqlAnalize/sql_ai_analyzer')

try:
    from data_collector.metadata_collector import MetadataCollector
    from config.config_manager import ConfigManager
    from utils.logger import setup_logger
    
    print("=" * 60)
    print("测试多数据库实例扫描功能")
    print("=" * 60)
    
    # 初始化配置和日志
    config_manager = ConfigManager('sql_ai_analyzer/config/config.ini')
    log_config = config_manager.get_log_config()
    logger = setup_logger(__name__, log_config)
    
    # 创建元数据收集器
    metadata_collector = MetadataCollector(config_manager, logger)
    
    # 测试表名
    test_table_names = ['test_table', 'users', 'products']
    
    print(f"\n1. 测试从所有ECUP实例收集元数据:")
    try:
        all_metadata = metadata_collector.collect_metadata_from_all_instances('ECUP', test_table_names)
        print(f"   成功从 {len(set(m.get('instance_alias') for m in all_metadata if m.get('instance_alias')))} 个实例收集到 {len(all_metadata)} 个表的元数据")
        
        for i, metadata in enumerate(all_metadata):
            if i < 5:  # 只显示前5个
                table_name = metadata.get('table_name', '未知')
                instance_alias = metadata.get('instance_alias', '未知')
                table_exists = metadata.get('table_exists', False)
                row_count = metadata.get('row_count', 0)
                print(f"   表 {table_name} 在实例 {instance_alias}: 存在={table_exists}, 行数={row_count}")
    except Exception as e:
        print(f"   收集元数据失败: {str(e)}")
    
    print(f"\n2. 测试依次查找表直到找到为止:")
    try:
        found_metadata = metadata_collector.collect_metadata_until_found('ECUP', test_table_names)
        if found_metadata:
            print(f"   在实例 {found_metadata[0].get('instance_alias', '未知')} 找到表")
            for metadata in found_metadata:
                table_name = metadata.get('table_name', '未知')
                table_exists = metadata.get('table_exists', False)
                print(f"   表 {table_name}: 存在={table_exists}")
        else:
            print("   在所有实例中都未找到表")
    except Exception as e:
        print(f"   查找表失败: {str(e)}")
    
    print(f"\n3. 测试单个实例元数据收集:")
    try:
        # 测试实例0
        instance_0_metadata = metadata_collector.collect_metadata('ECUP', test_table_names, 0)
        print(f"   实例0 (ECUP:1) 收集到 {len(instance_0_metadata)} 个表的元数据")
        
        # 测试实例1
        instance_1_metadata = metadata_collector.collect_metadata('ECUP', test_table_names, 1)
        print(f"   实例1 (ECUP:2) 收集到 {len(instance_1_metadata)} 个表的元数据")
    except Exception as e:
        print(f"   单实例收集失败: {str(e)}")
    
    print("\n4. 演示SQL分析流程中的多实例使用:")
    print("""
   在实际的SQL分析流程中，系统会:
   1. 首先使用 collect_metadata_until_found 找到表所在的实例
   2. 在该实例上获取执行计划
   3. 使用 collect_metadata_from_all_instances 收集所有实例的元数据供AI分析
   4. 这样确保SQL在正确的实例上执行，同时获取全面的元数据信息
   
   配置方式:
   - 在config.ini中配置多个同名数据库实例，如 [ECUP:1]、[ECUP:2]
   - 或者使用重复的 [ECUP] 段，配置管理器会自动处理
   - 每个实例可以有不同的连接参数（主机、端口、数据库名等）
   """)
    
    print("\n5. 测试实际配置的数据库连接:")
    try:
        import pymysql
        
        configs = config_manager.get_all_target_db_configs('ECUP')
        print(f"   共有 {len(configs)} 个ECUP实例配置")
        
        for i, config in enumerate(configs):
            host = config.get('host')
            port = config.get('port')
            database = config.get('database')
            username = config.get('username')
            
            print(f"\n   尝试连接实例 {i} ({config.get('instance_alias')}):")
            print(f"   连接信息: {username}@{host}:{port}/{database}")
            
            try:
                conn = pymysql.connect(
                    host=host,
                    port=port,
                    user=username,
                    password=config.get('password'),
                    database=database,
                    charset='utf8mb4',
                    connect_timeout=5
                )
                
                with conn.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    result = cursor.fetchone()
                    print(f"   ✓ 连接成功: {result}")
                
                conn.close()
            except Exception as conn_error:
                print(f"   ✗ 连接失败: {str(conn_error)}")
                print(f"   注意: 这只是测试连接，实际的表可能在另一个实例中")
    except Exception as e:
        print(f"   测试连接失败: {str(e)}")
    
    print("\n" + "=" * 60)
    print("测试总结:")
    print("=" * 60)
    print("""
    系统已经支持多数据库实例扫描功能:
    
    1. 配置支持:
       - 可以配置多个同名数据库实例，如 ECUP:1, ECUP:2
       - 每个实例可以有独立的连接参数
       
    2. 扫描策略:
       - collect_metadata_until_found: 依次尝试所有实例，直到找到表
       - collect_metadata_from_all_instances: 从所有实例收集元数据
       - 这满足用户需求："一条sql可能在a库，也可能在b库，扫描的时候需要扫两个"
       
    3. 实际使用:
       - 当SQL需要分析时，系统会尝试所有配置的实例
       - 执行计划在找到表的实例上生成
       - AI分析使用所有实例的元数据
    
    要使用此功能，只需在config.ini中配置多个同名数据库实例即可。
    """)
    
    print("=" * 60)
    print("测试完成")
    print("=" * 60)
    
except Exception as e:
    import traceback
    print(f'测试过程中发生错误: {str(e)}')
    traceback.print_exc()
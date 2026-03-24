#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试多数据库实例配置功能
"""

import sys
sys.path.append('e:/Code/sqlAnalize/sql_ai_analyzer')

try:
    from config.config_manager import ConfigManager
    
    print("=" * 60)
    print("测试多数据库实例配置功能")
    print("=" * 60)
    
    # 初始化配置管理器
    config_manager = ConfigManager('sql_ai_analyzer/config/config.ini')
    
    print("\n1. 检查当前配置文件中的数据库别名:")
    aliases = config_manager.get_all_target_db_aliases()
    print(f"   当前数据库别名: {aliases}")
    
    print("\n2. 检查ECUP数据库的配置情况:")
    try:
        ecup_configs = config_manager.get_all_target_db_configs('ECUP')
        print(f"   ECUP数据库配置数量: {len(ecup_configs)}")
        for i, config in enumerate(ecup_configs):
            print(f"   实例 {i}: {config.get('host')}:{config.get('port')}/{config.get('database')} (实例别名: {config.get('instance_alias')})")
    except Exception as e:
        print(f"   获取ECUP配置失败: {str(e)}")
    
    print("\n3. 测试多实例配置读取功能:")
    # 测试读取不存在的多实例配置
    try:
        non_existent_configs = config_manager.get_all_target_db_configs('db_nonexistent')
        print(f"   不存在的数据库配置数量: {len(non_existent_configs)}")
    except Exception as e:
        print(f"   读取不存在的数据库配置: {str(e)}")
    
    print("\n4. 测试按实例索引获取配置:")
    if ecup_configs:
        try:
            instance_0 = config_manager.get_target_db_config('ECUP', 0)
            print(f"   ECUP实例索引0: {instance_0.get('host')}:{instance_0.get('port')}")
        except Exception as e:
            print(f"   获取ECUP实例索引0失败: {str(e)}")
    
    print("\n5. 演示如何配置多实例ECUP数据库:")
    print("""
   在config.ini中添加以下配置可以实现多实例ECUP数据库:
   
   [ECUP:1]  # 第一个实例
   host = localhost
   port = 3306
   database = ecupdb_instance1
   username = root
   password = 123456
   db_type = mysql
   
   [ECUP:2]  # 第二个实例
   host = localhost
   port = 3307  # 不同端口
   database = ecupdb_instance2
   username = root
   password = 123456
   db_type = mysql
   
   或者使用重复的[ECUP]段（配置管理器会自动处理为ECUP__1和ECUP__2）:
   
   [ECUP]
   host = localhost
   port = 3306
   database = ecupdb_a
   username = root
   password = 123456
   db_type = mysql
   
   [ECUP]
   host = localhost
   port = 3307
   database = ecupdb_b
   username = root
   password = 123456
   db_type = mysql
   """)
    
    print("\n6. 当前配置文件内容预览:")
    try:
        with open('sql_ai_analyzer/config/config.ini', 'r', encoding='utf-8') as f:
            content = f.read()
            print("   " + "\n   ".join(content.split('\n')[:20]))
            if len(content.split('\n')) > 20:
                print("   ...")
    except Exception as e:
        print(f"   读取配置文件失败: {str(e)}")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)
    
except Exception as e:
    import traceback
    print(f'测试过程中发生错误: {str(e)}')
    traceback.print_exc()
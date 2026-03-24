#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试数据库连接
"""

import pymysql
from config.config_manager import ConfigManager

def test_database_connection():
    """测试数据库连接"""
    try:
        # 加载配置
        config = ConfigManager('config/test_config.ini')
        
        # 测试源数据库连接
        source_config = config.get_database_config()
        print("测试源数据库连接...")
        print(f"配置: host={source_config['host']}, database={source_config['database']}")
        
        try:
            conn = pymysql.connect(
                host=source_config['host'],
                port=source_config['port'],
                database=source_config['database'],
                user=source_config['username'],
                password=source_config['password']
            )
            
            if conn.is_connected():
                print("✓ 源数据库连接成功")
                
                # 测试查询
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                print(f"✓ 查询测试成功: {result}")
                
                cursor.close()
                conn.close()
                print("✓ 连接已关闭")
            else:
                print("✗ 源数据库连接失败")
                
        except Exception as e:
            print(f"✗ 源数据库连接错误: {e}")
        
        print("\n" + "="*50 + "\n")
        
        # 测试目标数据库连接
        target_config = config.get_target_db_config('db_production')
        print("测试目标数据库连接...")
        print(f"配置: host={target_config['host']}, database={target_config['database']}")
        
        try:
            conn = pymysql.connect(
                host=target_config['host'],
                port=target_config['port'],
                database=target_config['database'],
                user=target_config['username'],
                password=target_config['password']
            )
            
            if conn.is_connected():
                print("✓ 目标数据库连接成功")
                
                # 测试查询
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                print(f"✓ 查询测试成功: {result}")
                
                cursor.close()
                conn.close()
                print("✓ 连接已关闭")
            else:
                print("✗ 目标数据库连接失败")
                
        except Exception as e:
            print(f"✗ 目标数据库连接错误: {e}")
        
    except Exception as e:
        print(f"测试过程中发生错误: {e}")

if __name__ == '__main__':
    test_database_connection()
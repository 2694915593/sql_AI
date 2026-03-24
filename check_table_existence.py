#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查表是否存在
"""

import pymysql
import configparser

def check_table_existence():
    """检查表是否存在"""
    print("=" * 70)
    print("检查表存在性和配置")
    print("=" * 70)
    
    # 1. 检查ecupdb数据库
    print("\n1. 检查ecupdb数据库:")
    try:
        conn = pymysql.connect(
            host='localhost',
            port=3306,
            database='ecupdb',
            user='root',
            password='123456'
        )
        cursor = conn.cursor()
        
        cursor.execute("SHOW TABLES LIKE 'testtable'")
        result = cursor.fetchone()
        if result:
            print(f"   ✓ testtable表存在: {result[0]}")
            
            # 查看表结构
            cursor.execute('DESCRIBE testtable')
            columns = cursor.fetchall()
            print(f"   表结构 ({len(columns)}列):")
            for col in columns:
                print(f"     {col[0]}: {col[1]}")
                
            # 查看数据
            cursor.execute('SELECT COUNT(*) FROM testtable')
            count = cursor.fetchone()[0]
            print(f"   表中有 {count} 条数据")
        else:
            print("   ✗ testtable表不存在")
            
        # 查看所有表
        cursor.execute('SHOW TABLES')
        tables = cursor.fetchall()
        print(f"   ecupdb数据库中的所有表 ({len(tables)}个):")
        for table in tables:
            print(f"     - {table[0]}")
            
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"   连接ecupdb失败: {e}")
    
    # 2. 检查testdb数据库
    print("\n2. 检查testdb数据库:")
    try:
        conn = pymysql.connect(
            host='localhost',
            port=3306,
            database='testdb',
            user='root',
            password='123456'
        )
        cursor = conn.cursor()
        
        cursor.execute("SHOW TABLES LIKE 'testtable'")
        result = cursor.fetchone()
        if result:
            print(f"   ✓ testtable表存在: {result[0]}")
        else:
            print("   ✗ testtable表不存在")
            
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"   连接testdb失败: {e}")
    
    # 3. 检查配置文件
    print("\n3. 检查配置文件 (config/config.ini):")
    try:
        config = configparser.ConfigParser()
        config.read('config/config.ini')
        
        if 'database' in config:
            print("   [database] 配置:")
            for key in config['database']:
                print(f"     {key} = {config['database'][key]}")
        
        if 'db_production' in config:
            print("\n   [db_production] 配置:")
            for key in config['db_production']:
                print(f"     {key} = {config['db_production'][key]}")
        else:
            print("   ✗ [db_production] 配置不存在")
            
        if 'ECUP' in config:
            print("\n   [ECUP] 配置:")
            for key in config['ECUP']:
                print(f"     {key} = {config['ECUP'][key]}")
        else:
            print("   ✗ [ECUP] 配置不存在")
            
    except Exception as e:
        print(f"   读取配置失败: {e}")
    
    # 4. 检查SQL记录中的系统ID
    print("\n4. 检查SQL记录中的系统ID:")
    try:
        conn = pymysql.connect(
            host='localhost',
            port=3306,
            database='testdb',
            user='root',
            password='123456',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        cursor = conn.cursor()
        
        cursor.execute("SELECT DISTINCT SYSTEMID FROM am_solline_info")
        system_ids = cursor.fetchall()
        
        print("   所有系统ID:")
        for row in system_ids:
            system_id = row['SYSTEMID']
            print(f"     - {system_id}")
            
            # 检查每个系统ID对应的配置
            if system_id and system_id.strip():
                config_section = system_id.strip()
                if config_section in config:
                    print(f"       配置存在: database={config[config_section].get('database', '未设置')}")
                else:
                    print(f"       ✗ 配置不存在")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"   检查SQL记录失败: {e}")
    
    print("\n" + "=" * 70)
    print("检查完成")
    print("=" * 70)

if __name__ == '__main__':
    check_table_existence()
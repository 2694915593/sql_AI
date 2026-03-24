#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
在am_solline_info表中添加SQL问题记录字段
"""

import sys
sys.path.append('e:/Code/sqlAnalize/sql_ai_analyzer')

try:
    import pymysql
    from config.config_manager import ConfigManager
    
    config_manager = ConfigManager()
    db_config = config_manager.get_database_config()
    
    print(f"连接到数据库: {db_config['host']}:{db_config['port']}/{db_config['database']}")
    
    conn = pymysql.connect(
        host=db_config['host'],
        port=db_config['port'],
        user=db_config['username'],
        password=db_config['password'],
        database=db_config['database'],
        charset='utf8mb4'
    )
    
    with conn.cursor() as cursor:
        print("=" * 60)
        print("添加SQL问题记录字段")
        print("=" * 60)
        
        # 添加sql_issue_type字段
        try:
            # 先检查字段是否已存在
            cursor.execute("SHOW COLUMNS FROM am_solline_info LIKE 'sql_issue_type'")
            if cursor.fetchone():
                print('✓ sql_issue_type字段已存在')
            else:
                cursor.execute("""
                    ALTER TABLE am_solline_info 
                    ADD COLUMN sql_issue_type ENUM('none', 'db2_syntax', 'table_extraction_failed', 'execution_plan_failed', 'other') DEFAULT 'none' COMMENT 'SQL问题类型'
                """)
                print('✓ 添加sql_issue_type字段成功')
        except Exception as e:
            print(f'添加sql_issue_type字段时出错: {str(e)}')
        
        # 添加sql_issue_details字段
        try:
            # 先检查字段是否已存在
            cursor.execute("SHOW COLUMNS FROM am_solline_info LIKE 'sql_issue_details'")
            if cursor.fetchone():
                print('✓ sql_issue_details字段已存在')
            else:
                cursor.execute("""
                    ALTER TABLE am_solline_info 
                    ADD COLUMN sql_issue_details TEXT COMMENT 'SQL问题详情'
                """)
                print('✓ 添加sql_issue_details字段成功')
        except Exception as e:
            print(f'添加sql_issue_details字段时出错: {str(e)}')
        
        # 添加索引
        try:
            cursor.execute("SHOW INDEX FROM am_solline_info WHERE Key_name = 'idx_sql_issue_type'")
            if not cursor.fetchone():
                cursor.execute("""
                    CREATE INDEX idx_sql_issue_type ON am_solline_info (sql_issue_type)
                """)
                print('✓ 添加sql_issue_type索引成功')
            else:
                print('✓ idx_sql_issue_type索引已存在')
        except Exception as e:
            print(f'添加索引时出错: {str(e)}')
        
        conn.commit()
        print('\n✓ 表结构修改完成')
        
        # 验证表结构
        print("\n" + "=" * 60)
        print("验证表结构")
        print("=" * 60)
        cursor.execute("DESCRIBE am_solline_info")
        columns = cursor.fetchall()
        
        issue_type_exists = False
        issue_details_exists = False
        
        for col in columns:
            field_name = col[0]
            if field_name == 'sql_issue_type':
                issue_type_exists = True
                print(f"✓ sql_issue_type字段: {col[1]} (默认值: {col[4]})")
            elif field_name == 'sql_issue_details':
                issue_details_exists = True
                print(f"✓ sql_issue_details字段: {col[1]}")
        
        if not issue_type_exists:
            print("✗ sql_issue_type字段不存在")
        if not issue_details_exists:
            print("✗ sql_issue_details字段不存在")
            
        # 查看现有数据的问题类型分布
        print("\n" + "=" * 60)
        print("当前数据问题类型分布")
        print("=" * 60)
        try:
            cursor.execute("""
                SELECT 
                    COALESCE(sql_issue_type, '未设置') as issue_type,
                    COUNT(*) as count
                FROM am_solline_info 
                GROUP BY COALESCE(sql_issue_type, '未设置')
                ORDER BY count DESC
            """)
            result = cursor.fetchall()
            for row in result:
                print(f"问题类型: {row[0]:25} 数量: {row[1]}")
        except Exception as e:
            print(f"查询问题类型分布时出错: {str(e)}")
    
    conn.close()
    
except Exception as e:
    import traceback
    print(f'错误: {str(e)}')
    traceback.print_exc()
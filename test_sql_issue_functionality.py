#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试SQL问题记录功能
"""

import sys
sys.path.append('e:/Code/sqlAnalize/sql_ai_analyzer')

try:
    from data_collector.sql_extractor import SQLExtractor
    from config.config_manager import ConfigManager
    
    print("=" * 60)
    print("测试SQL问题记录功能")
    print("=" * 60)
    
    # 初始化配置和提取器
    config_manager = ConfigManager()
    sql_extractor = SQLExtractor(config_manager)
    
    # 测试1: 测试更新SQL问题类型
    print("\n测试1: 更新SQL问题类型")
    print("-" * 40)
    
    # 获取一个测试用的SQL ID
    pending_sqls = sql_extractor.get_pending_sqls(1)
    if pending_sqls:
        test_sql_id = pending_sqls[0]['id']
        print(f"找到测试SQL ID: {test_sql_id}")
        
        # 测试不同的SQL问题类型
        issue_types = [
            ('db2_syntax', 'DB2语法问题: SQL包含DB2特定语法'),
            ('table_extraction_failed', '表提取失败: 无法从SQL中提取表名'),
            ('execution_plan_failed', '执行计划失败: 无法生成执行计划'),
            ('other', '其他问题: 其他未知错误'),
            ('none', '无问题: 测试重置状态')
        ]
        
        for issue_type, issue_details in issue_types:
            print(f"\n尝试更新问题类型为: {issue_type}")
            result = sql_extractor.update_sql_issue(test_sql_id, issue_type, issue_details)
            if result:
                print(f"✓ 成功更新问题类型为: {issue_type}")
            else:
                print(f"✗ 更新问题类型失败: {issue_type}")
    else:
        print("没有找到待测试的SQL记录")
    
    # 测试2: 从数据库直接验证数据
    print("\n" + "=" * 60)
    print("测试2: 从数据库验证数据")
    print("-" * 40)
    
    try:
        import pymysql
        from config.config_manager import ConfigManager
        
        config_manager = ConfigManager()
        db_config = config_manager.get_database_config()
        
        conn = pymysql.connect(
            host=db_config['host'],
            port=db_config['port'],
            user=db_config['username'],
            password=db_config['password'],
            database=db_config['database'],
            charset='utf8mb4'
        )
        
        with conn.cursor() as cursor:
            # 查看问题类型分布
            cursor.execute("""
                SELECT 
                    sql_issue_type,
                    COUNT(*) as count,
                    GROUP_CONCAT(DISTINCT LEFT(sql_issue_details, 50) SEPARATOR '; ') as sample_details
                FROM am_solline_info 
                WHERE sql_issue_type IS NOT NULL AND sql_issue_type != 'none'
                GROUP BY sql_issue_type
                ORDER BY count DESC
            """)
            result = cursor.fetchall()
            
            if result:
                print("当前的问题类型分布:")
                for row in result:
                    print(f"  问题类型: {row[0]:25} 数量: {row[1]:4} 示例: {row[2][:80]}...")
            else:
                print("没有非'none'的问题类型记录")
            
            # 查看最新的5条记录
            cursor.execute("""
                SELECT 
                    ID, 
                    sql_issue_type,
                    LEFT(sql_issue_details, 100) as issue_preview,
                    analysis_status
                FROM am_solline_info 
                WHERE sql_issue_type IS NOT NULL
                ORDER BY ID DESC
                LIMIT 5
            """)
            recent_records = cursor.fetchall()
            
            if recent_records:
                print("\n最新的SQL问题记录:")
                for record in recent_records:
                    print(f"  ID: {record[0]:6} 问题类型: {record[1]:25} 状态: {record[3]:10} 详情: {record[2][:50]}...")
            else:
                print("\n没有SQL问题记录")
        
        conn.close()
        
    except Exception as e:
        print(f"数据库验证时出错: {str(e)}")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)
    
except Exception as e:
    import traceback
    print(f'测试过程中发生错误: {str(e)}')
    traceback.print_exc()
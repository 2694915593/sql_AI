#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试表不存在时的修复功能
验证查不到表时会正确更新SQL问题类型和状态
"""

import sys
sys.path.append('e:/Code/sqlAnalize/sql_ai_analyzer')

from data_collector.sql_extractor import SQLExtractor
from config.config_manager import ConfigManager
import pymysql

def test_table_extraction_failed():
    """测试表提取失败时的处理逻辑"""
    print("=" * 60)
    print("测试表提取失败修复功能")
    print("=" * 60)
    
    # 初始化配置和提取器
    config_manager = ConfigManager()
    sql_extractor = SQLExtractor(config_manager)
    
    print("\n1. 测试get_table_names_from_field方法")
    print("-" * 40)
    
    # 测试各种表名格式
    test_cases = [
        ("表1", ["表1"]),
        ("表1,表2", ["表1", "表2"]),
        ("表1;表2", ["表1", "表2"]),
        ("表1 表2", ["表1", "表2"]),
        ("表1, 表2, 表3", ["表1", "表2", "表3"]),
        ("", []),
        (None, []),
    ]
    
    for input_str, expected in test_cases:
        result = sql_extractor.get_table_names_from_field(input_str)
        status = "✓" if result == expected else "✗"
        print(f"{status} '{input_str}' -> {result} (预期: {expected})")
    
    print("\n2. 模拟不存在的表名")
    print("-" * 40)
    
    # 创建一个不存在的表名列表
    non_existent_tables = ["NON_EXISTENT_TABLE_1", "NON_EXISTENT_TABLE_2"]
    
    print(f"模拟不存在的表名: {non_existent_tables}")
    print("注意: 这些表实际上不会在数据库中存在")
    
    print("\n3. 检查数据库连接和现有表")
    print("-" * 40)
    
    try:
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
            # 检查am_solline_info表结构
            cursor.execute("SHOW COLUMNS FROM am_solline_info")
            columns = cursor.fetchall()
            
            print(f"am_solline_info表有 {len(columns)} 列")
            
            # 查找问题相关字段
            issue_fields = ['sql_issue_type', 'sql_issue_details', 'analysis_status', 'error_message']
            found_fields = []
            
            for col in columns:
                if col[0] in issue_fields:
                    found_fields.append(col[0])
            
            if found_fields:
                print(f"✓ 找到问题相关字段: {found_fields}")
            else:
                print("✗ 未找到问题相关字段，可能表结构不完整")
            
            # 检查是否有数据
            cursor.execute("SELECT COUNT(*) FROM am_solline_info")
            count = cursor.fetchone()[0]
            print(f"am_solline_info表中有 {count} 条记录")
            
            if count > 0:
                # 获取一条测试记录
                cursor.execute("""
                    SELECT ID, SQLLINE, sql_issue_type, analysis_status 
                    FROM am_solline_info 
                    WHERE analysis_status IS NULL OR analysis_status = 'pending'
                    LIMIT 1
                """)
                test_record = cursor.fetchone()
                
                if test_record:
                    print(f"\n找到测试记录:")
                    print(f"  ID: {test_record[0]}")
                    print(f"  SQL预览: {test_record[1][:100]}...")
                    print(f"  问题类型: {test_record[2]}")
                    print(f"  分析状态: {test_record[3]}")
                    
                    # 测试更新问题类型
                    print(f"\n测试更新问题类型为 'table_extraction_failed'")
                    result = sql_extractor.update_sql_issue(
                        test_record[0], 
                        'table_extraction_failed', 
                        f'测试表提取失败: {non_existent_tables}'
                    )
                    
                    if result:
                        print(f"✓ 成功更新SQL问题类型")
                        
                        # 验证更新结果
                        cursor.execute(f"SELECT sql_issue_type, sql_issue_details FROM am_solline_info WHERE ID = {test_record[0]}")
                        updated_record = cursor.fetchone()
                        
                        if updated_record:
                            print(f"  更新后的问题类型: {updated_record[0]}")
                            print(f"  更新后的问题详情: {updated_record[1][:100]}...")
                    else:
                        print(f"✗ 更新SQL问题类型失败")
        
        conn.close()
        
    except Exception as e:
        print(f"数据库操作出错: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print("\n4. 测试更新分析状态方法")
    print("-" * 40)
    
    try:
        # 再次连接数据库获取一个测试记录
        conn = pymysql.connect(
            host=db_config['host'],
            port=db_config['port'],
            user=db_config['username'],
            password=db_config['password'],
            database=db_config['database'],
            charset='utf8mb4'
        )
        
        with conn.cursor() as cursor:
            cursor.execute("SELECT ID FROM am_solline_info LIMIT 1")
            test_record = cursor.fetchone()
            
            if test_record:
                test_id = test_record[0]
                print(f"使用ID {test_id} 测试分析状态更新")
                
                # 测试更新为failed状态
                print(f"测试更新分析状态为 'failed'")
                result = sql_extractor.update_analysis_status(
                    test_id, 
                    'failed', 
                    '测试失败原因: 表不存在'
                )
                
                if result:
                    print(f"✓ 成功更新分析状态")
                    
                    # 验证更新结果
                    cursor.execute(f"SELECT analysis_status, error_message FROM am_solline_info WHERE ID = {test_id}")
                    updated_record = cursor.fetchone()
                    
                    if updated_record:
                        print(f"  更新后的分析状态: {updated_record[0]}")
                        print(f"  更新后的错误信息: {updated_record[1]}")
                else:
                    print(f"✗ 更新分析状态失败")
        
        conn.close()
        
    except Exception as e:
        print(f"数据库操作出错: {str(e)}")
    
    print("\n" + "=" * 60)
    print("测试总结:")
    print("修复的主要变化:")
    print("1. 当collect_metadata_until_found返回空列表时（表不存在）")
    print("2. 系统会调用sql_extractor.update_sql_issue更新问题类型")
    print("3. 同时调用sql_extractor.update_analysis_status更新分析状态")
    print("4. 返回明确的错误信息给调用者")
    print("=" * 60)

if __name__ == "__main__":
    test_table_extraction_failed()
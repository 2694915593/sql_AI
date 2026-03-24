#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试基本流程（不使用连接池）
"""

import pymysql
from config.config_manager import ConfigManager

def test_basic_flow():
    """测试基本流程"""
    try:
        # 加载配置
        config = ConfigManager('config/test_config.ini')
        
        print("1. 测试SQL提取...")
        
        # 直接连接数据库测试SQL提取
        source_config = config.get_database_config()
        conn = pymysql.connect(
            host=source_config['host'],
            port=source_config['port'],
            database=source_config['database'],
            user=source_config['username'],
            password=source_config['password']
        )
        
        cursor = conn.cursor(dictionary=True)
        
        # 提取SQL
        cursor.execute("""
            SELECT ID as id, SQLLINE as sql_text, SYSTEMID as system_id
            FROM am_solline_info 
            WHERE ID = 7360
        """)
        sql_info = cursor.fetchone()
        
        if sql_info:
            print(f"✓ 提取到SQL ID {sql_info['id']}: {sql_info['sql_text'][:50]}...")
            print(f"  system_id: {sql_info['system_id']}")
        else:
            print("✗ 未找到SQL记录")
            return
        
        print("\n2. 测试表名提取...")
        
        # 简单的表名提取
        sql_text = sql_info['sql_text']
        import re
        from_table = re.findall(r'\bFROM\s+([\w\.]+)', sql_text, re.IGNORECASE)
        print(f"✓ 提取到表名: {from_table}")
        
        print("\n3. 测试元数据收集...")
        
        # 连接目标数据库
        target_config = config.get_target_db_config('db_production')
        target_conn = pymysql.connect(
            host=target_config['host'],
            port=target_config['port'],
            database=target_config['database'],
            user=target_config['username'],
            password=target_config['password']
        )
        
        target_cursor = target_conn.cursor(dictionary=True)
        
        for table in from_table:
            # 获取表结构
            target_cursor.execute(f"DESCRIBE {table}")
            columns = target_cursor.fetchall()
            print(f"✓ 表 {table} 有 {len(columns)} 列")
            
            # 获取行数
            target_cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
            row_count = target_cursor.fetchone()['count']
            print(f"✓ 表 {table} 有 {row_count} 行数据")
            
            # 获取索引信息
            target_cursor.execute(f"SHOW INDEX FROM {table}")
            indexes = target_cursor.fetchall()
            print(f"✓ 表 {table} 有 {len(indexes)} 个索引")
        
        target_cursor.close()
        target_conn.close()
        
        print("\n4. 测试结果存储...")
        
        # 更新分析状态
        update_query = """
            UPDATE am_solline_info 
            SET analysis_status = 'analyzed', 
                analysis_result = %s,
                analysis_time = NOW()
            WHERE ID = %s
        """
        
        # 模拟分析结果
        mock_result = {
            "analysis_result": {
                "large_table_operation": {"status": "ok"},
                "index_analysis": {"has_index": True},
                "optimization_suggestions": ["建议添加索引"]
            }
        }
        
        import json
        cursor.execute(update_query, (json.dumps(mock_result), sql_info['id']))
        conn.commit()
        
        print(f"✓ 更新SQL ID {sql_info['id']} 状态为 analyzed")
        
        # 验证更新
        cursor.execute("SELECT analysis_status, analysis_result FROM am_solline_info WHERE ID = %s", (sql_info['id'],))
        updated = cursor.fetchone()
        print(f"✓ 验证: 状态={updated['analysis_status']}, 结果已保存")
        
        cursor.close()
        conn.close()
        
        print("\n✓ 基本流程测试完成！")
        
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_basic_flow()
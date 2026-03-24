#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化流程测试 - 不使用连接池
"""

import pymysql
import json

def test_simple_flow():
    """测试简化流程"""
    print("简化流程测试开始...")
    
    try:
        # 1. 连接源数据库
        source_conn = pymysql.connect(
            host='localhost',
            port=3306,
            database='testdb',
            user='root',
            password='123456'
        )
        source_cursor = source_conn.cursor(dictionary=True)
        
        print("1. 连接源数据库成功")
        
        # 2. 获取一条待分析的SQL
        source_cursor.execute("""
            SELECT ID as id, SQLLINE as sql_text, TABLENAME as table_name, SYSTEMID as system_id
            FROM am_solline_info 
            WHERE analysis_status = 'pending'
            LIMIT 1
        """)
        sql_info = source_cursor.fetchone()
        
        if not sql_info:
            print("没有待分析的SQL")
            return
        
        print(f"2. 获取到SQL ID {sql_info['id']}: {sql_info['sql_text'][:50]}...")
        print(f"   表名: {sql_info['table_name']}")
        print(f"   系统ID: {sql_info['system_id']}")
        
        # 3. 提取表名
        table_names = []
        if sql_info['table_name'] and sql_info['table_name'].strip():
            # 使用TABLENAME字段
            table_names = [t.strip() for t in sql_info['table_name'].split(',') if t.strip()]
        print(f"3. 提取到表名: {table_names}")
        
        # 4. 连接目标数据库收集元数据
        target_conn = pymysql.connect(
            host='localhost',
            port=3306,
            database='testdb',
            user='root',
            password='123456'
        )
        target_cursor = target_conn.cursor(dictionary=True)
        
        print("4. 连接目标数据库成功")
        
        metadata = []
        for table in table_names:
            try:
                # 获取表结构
                target_cursor.execute(f"DESCRIBE {table}")
                columns = target_cursor.fetchall()
                
                # 获取行数
                target_cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
                row_count = target_cursor.fetchone()['count']
                
                # 获取索引信息
                target_cursor.execute(f"SHOW INDEX FROM {table}")
                indexes = target_cursor.fetchall()
                
                table_metadata = {
                    'table_name': table,
                    'column_count': len(columns),
                    'row_count': row_count,
                    'index_count': len(indexes),
                    'is_large_table': row_count > 100000
                }
                metadata.append(table_metadata)
                
                print(f"   ✓ 表 {table}: {len(columns)}列, {row_count}行, {len(indexes)}个索引")
                
            except Exception as e:
                print(f"   ✗ 表 {table} 元数据收集失败: {e}")
        
        target_cursor.close()
        target_conn.close()
        
        # 5. 模拟API调用（实际项目中会调用真实API）
        print("5. 模拟API调用...")
        
        # 构建请求数据
        request_data = {
            "sql_statement": sql_info['sql_text'],
            "tables": metadata,
            "db_alias": sql_info.get('system_id', 'db_production')
        }
        
        print(f"   请求数据构建完成")
        
        # 模拟分析结果
        mock_result = {
            "analysis_result": {
                "large_table_operation": {"status": "ok"},
                "index_analysis": {"has_index": True},
                "optimization_suggestions": ["建议定期清理历史数据"]
            }
        }
        
        # 6. 更新分析状态
        update_query = """
            UPDATE am_solline_info 
            SET analysis_status = 'analyzed', 
                analysis_result = %s,
                analysis_time = NOW()
            WHERE ID = %s
        """
        
        source_cursor.execute(update_query, (json.dumps(mock_result), sql_info['id']))
        source_conn.commit()
        
        print(f"6. 更新SQL ID {sql_info['id']} 状态为 analyzed")
        
        # 验证更新
        source_cursor.execute("SELECT analysis_status FROM am_solline_info WHERE ID = %s", (sql_info['id'],))
        updated = source_cursor.fetchone()
        print(f"   验证: 状态={updated['analysis_status']}")
        
        source_cursor.close()
        source_conn.close()
        
        print("\n✓ 简化流程测试完成！")
        
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_simple_flow()
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整工作流程测试 - 演示用户的工作流程
"""

import pymysql
import json
import sys

def test_complete_workflow():
    """测试完整工作流程"""
    print("=" * 60)
    print("AI-SQL质量分析系统 - 完整工作流程演示")
    print("=" * 60)
    
    try:
        # 1. 检查数据库连接
        print("\n1. 检查数据库连接...")
        
        # 检查源数据库 (testdb)
        try:
            source_conn = pymysql.connect(
                host='localhost',
                port=3306,
                database='testdb',
                user='root',
                password='123456'
            )
            print("   ✓ 源数据库 (testdb) 连接成功")
            source_conn.close()
        except Exception as e:
            print(f"   ✗ 源数据库连接失败: {e}")
            return
        
        # 检查目标数据库 (ecupdb)
        try:
            target_conn = pymysql.connect(
                host='localhost',
                port=3306,
                database='ecupdb',
                user='root',
                password='123456'
            )
            print("   ✓ 目标数据库 (ecupdb) 连接成功")
            target_conn.close()
        except Exception as e:
            print(f"   ✗ 目标数据库连接失败: {e}")
            print("   注意: 如果ecupdb不存在，将使用testdb作为目标数据库")
        
        # 2. 获取最新一条待分析SQL
        print("\n2. 获取最新待分析SQL...")
        source_conn = pymysql.connect(
            host='localhost',
            port=3306,
            database='testdb',
            user='root',
            password='123456'
        )
        source_cursor = source_conn.cursor(dictionary=True)
        
        source_cursor.execute("""
            SELECT ID as id, SQLLINE as sql_text, TABLENAME as table_name, 
                   SYSTEMID as system_id, analysis_status
            FROM am_solline_info 
            WHERE analysis_status = 'pending'
            ORDER BY ID DESC
            LIMIT 1
        """)
        
        sql_info = source_cursor.fetchone()
        
        if not sql_info:
            print("   ✗ 没有待分析的SQL")
            source_cursor.close()
            source_conn.close()
            return
        
        print(f"   ✓ 找到SQL ID {sql_info['id']}")
        print(f"      SQL: {sql_info['sql_text']}")
        print(f"      表名: {sql_info['table_name']}")
        print(f"      系统ID: {sql_info['system_id']}")
        print(f"      状态: {sql_info['analysis_status']}")
        
        # 3. 提取表名
        print("\n3. 提取表名...")
        table_names = []
        if sql_info['table_name'] and str(sql_info['table_name']).strip():
            # 使用TABLENAME字段
            table_names = [t.strip() for t in str(sql_info['table_name']).split(',') if t.strip()]
            print(f"   ✓ 从TABLENAME字段提取表名: {table_names}")
        else:
            print("   ✗ TABLENAME字段为空")
        
        # 4. 收集元数据
        print("\n4. 收集表元数据...")
        
        # 确定目标数据库
        target_db = 'ecupdb'  # 优先使用ecupdb
        try:
            target_conn = pymysql.connect(
                host='localhost',
                port=3306,
                database=target_db,
                user='root',
                password='123456'
            )
            print(f"   ✓ 连接到目标数据库: {target_db}")
        except:
            # 如果ecupdb不存在，使用testdb
            target_db = 'testdb'
            target_conn = pymysql.connect(
                host='localhost',
                port=3306,
                database=target_db,
                user='root',
                password='123456'
            )
            print(f"   ✓ 连接到目标数据库: {target_db}")
        
        target_cursor = target_conn.cursor(dictionary=True)
        
        metadata = []
        for table in table_names:
            try:
                # 获取表结构
                target_cursor.execute(f"DESCRIBE {table}")
                columns = target_cursor.fetchall()
                
                # 获取行数
                target_cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
                row_result = target_cursor.fetchone()
                row_count = row_result['count'] if row_result else 0
                
                # 获取索引信息
                target_cursor.execute(f"SHOW INDEX FROM {table}")
                indexes = target_cursor.fetchall()
                
                # 获取表DDL
                target_cursor.execute(f"SHOW CREATE TABLE {table}")
                ddl_result = target_cursor.fetchone()
                ddl = ddl_result['Create Table'] if ddl_result else ""
                
                table_metadata = {
                    'table_name': table,
                    'database': target_db,
                    'ddl': ddl[:200] + "..." if len(ddl) > 200 else ddl,
                    'column_count': len(columns),
                    'row_count': row_count,
                    'index_count': len(indexes),
                    'is_large_table': row_count > 100000,
                    'columns': [{'name': col['Field'], 'type': col['Type'], 'nullable': col['Null'] == 'YES'} 
                               for col in columns[:3]]  # 只显示前3列
                }
                metadata.append(table_metadata)
                
                print(f"   ✓ 表 {table}:")
                print(f"      - 数据库: {target_db}")
                print(f"      - 列数: {len(columns)}")
                print(f"      - 行数: {row_count}")
                print(f"      - 索引数: {len(indexes)}")
                print(f"      - 是否大表: {row_count > 100000}")
                
            except Exception as e:
                print(f"   ✗ 表 {table} 元数据收集失败: {e}")
                metadata.append({
                    'table_name': table,
                    'database': target_db,
                    'error': str(e)
                })
        
        target_cursor.close()
        target_conn.close()
        
        # 5. 构建AI请求数据
        print("\n5. 构建AI分析请求...")
        request_data = {
            "sql_statement": sql_info['sql_text'],
            "tables": metadata,
            "db_alias": sql_info.get('system_id', 'db_production'),
            "sql_id": sql_info['id']
        }
        
        print(f"   ✓ 请求数据构建完成")
        print(f"      SQL类型: {'DELETE' if 'DELETE' in sql_info['sql_text'].upper() else '其他'}")
        print(f"      涉及表数: {len(metadata)}")
        print(f"      数据库别名: {sql_info.get('system_id', 'db_production')}")
        
        # 6. 模拟AI分析结果
        print("\n6. 模拟AI分析...")
        
        # 根据SQL类型生成不同的分析结果
        sql_upper = sql_info['sql_text'].upper()
        if 'DELETE' in sql_upper:
            analysis_result = {
                "analysis_result": {
                    "sql_type": "DELETE",
                    "risk_level": "MEDIUM",
                    "large_table_operation": {
                        "status": "warning",
                        "message": "DELETE操作可能影响大量数据，建议添加LIMIT或使用软删除"
                    },
                    "index_analysis": {
                        "has_appropriate_index": True,
                        "suggestion": "确保created_at字段有索引以提高删除性能"
                    },
                    "optimization_suggestions": [
                        "建议在业务低峰期执行",
                        "考虑分批删除避免锁表",
                        "建议添加WHERE条件限制删除范围"
                    ],
                    "performance_impact": "中等",
                    "data_impact": f"将删除30天前的数据"
                }
            }
        elif 'UPDATE' in sql_upper:
            analysis_result = {
                "analysis_result": {
                    "sql_type": "UPDATE",
                    "risk_level": "HIGH",
                    "optimization_suggestions": [
                        "建议添加WHERE条件索引",
                        "考虑使用事务确保数据一致性"
                    ]
                }
            }
        elif 'SELECT' in sql_upper:
            analysis_result = {
                "analysis_result": {
                    "sql_type": "SELECT",
                    "risk_level": "LOW",
                    "optimization_suggestions": [
                        "建议添加合适的索引",
                        "考虑分页查询避免大数据量"
                    ]
                }
            }
        else:
            analysis_result = {
                "analysis_result": {
                    "sql_type": "OTHER",
                    "risk_level": "UNKNOWN",
                    "optimization_suggestions": ["请人工审核此SQL语句"]
                }
            }
        
        print(f"   ✓ AI分析完成")
        print(f"      SQL类型: {analysis_result['analysis_result']['sql_type']}")
        print(f"      风险等级: {analysis_result['analysis_result']['risk_level']}")
        print(f"      优化建议数: {len(analysis_result['analysis_result'].get('optimization_suggestions', []))}")
        
        # 7. 存储分析结果
        print("\n7. 存储分析结果...")
        
        update_query = """
            UPDATE am_solline_info 
            SET analysis_status = 'analyzed', 
                analysis_result = %s,
                analysis_time = NOW()
            WHERE ID = %s
        """
        
        source_cursor.execute(update_query, (json.dumps(analysis_result), sql_info['id']))
        source_conn.commit()
        
        # 验证更新
        source_cursor.execute("""
            SELECT analysis_status, analysis_time 
            FROM am_solline_info 
            WHERE ID = %s
        """, (sql_info['id'],))
        updated = source_cursor.fetchone()
        
        print(f"   ✓ SQL ID {sql_info['id']} 分析完成")
        print(f"      状态: {updated['analysis_status']}")
        print(f"      时间: {updated['analysis_time']}")
        
        source_cursor.close()
        source_conn.close()
        
        # 8. 显示分析报告
        print("\n" + "=" * 60)
        print("分析报告摘要")
        print("=" * 60)
        print(f"SQL ID: {sql_info['id']}")
        print(f"SQL语句: {sql_info['sql_text']}")
        print(f"分析结果:")
        result = analysis_result['analysis_result']
        for key, value in result.items():
            if isinstance(value, list):
                print(f"  {key}:")
                for item in value:
                    print(f"    - {item}")
            elif isinstance(value, dict):
                print(f"  {key}:")
                for k, v in value.items():
                    print(f"    {k}: {v}")
            else:
                print(f"  {key}: {value}")
        
        print("\n" + "=" * 60)
        print("✓ 完整工作流程演示完成！")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ 工作流程测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_complete_workflow()
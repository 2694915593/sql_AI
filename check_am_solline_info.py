#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查am_solline_info表结构和数据
"""

import pymysql
from pymysql.cursors import DictCursor

def check_table():
    """检查表结构和数据"""
    print("=" * 70)
    print("检查am_solline_info表")
    print("=" * 70)
    
    try:
        # 连接数据库
        conn = pymysql.connect(
            host='localhost',
            port=3306,
            database='testdb',
            user='root',
            password='123456',
            charset='utf8mb4',
            cursorclass=DictCursor
        )
        
        cursor = conn.cursor()
        
        # 1. 检查表结构
        print("\n1. am_solline_info表结构:")
        cursor.execute('DESCRIBE am_solline_info')
        columns = cursor.fetchall()
        
        for col in columns:
            field = col['Field']
            field_type = col['Type']
            nullable = 'YES' if col['Null'] == 'YES' else 'NO'
            default = col['Default'] if col['Default'] is not None else 'NULL'
            print(f"  {field:20} {field_type:20} {nullable:5} 默认: {default}")
        
        # 2. 检查总记录数
        print("\n2. 数据统计:")
        cursor.execute('SELECT COUNT(*) as total FROM am_solline_info')
        total = cursor.fetchone()['total']
        print(f"   总记录数: {total}")
        
        cursor.execute("SELECT COUNT(*) as pending FROM am_solline_info WHERE analysis_status = 'pending' OR analysis_status IS NULL")
        pending = cursor.fetchone()['pending']
        print(f"   待分析记录: {pending}")
        
        cursor.execute("SELECT COUNT(*) as analyzed FROM am_solline_info WHERE analysis_status = 'analyzed'")
        analyzed = cursor.fetchone()['analyzed']
        print(f"   已分析记录: {analyzed}")
        
        cursor.execute("SELECT COUNT(*) as failed FROM am_solline_info WHERE analysis_status = 'failed'")
        failed = cursor.fetchone()['failed']
        print(f"   失败记录: {failed}")
        
        # 3. 检查前10条记录
        print("\n3. 前10条记录:")
        cursor.execute("""
            SELECT 
                ID, 
                SQLLINE, 
                SYSTEMID, 
                analysis_status,
                analysis_time,
                error_message
            FROM am_solline_info 
            ORDER BY ID ASC 
            LIMIT 10
        """)
        
        records = cursor.fetchall()
        
        for record in records:
            sql_id = record['ID']
            sql_text = record['SQLLINE'] or ''
            system_id = record['SYSTEMID'] or ''
            status = record['analysis_status'] or 'NULL'
            error = record['error_message'] or ''
            
            print(f"\n  ID: {sql_id}")
            print(f"    系统: {system_id}")
            print(f"    状态: {status}")
            print(f"    SQL: {sql_text[:80]}...")
            if error:
                print(f"    错误: {error[:50]}...")
        
        # 4. 检查ID为1的记录是否存在
        print("\n4. 检查ID为1的记录:")
        cursor.execute("SELECT ID, SQLLINE, SYSTEMID, analysis_status FROM am_solline_info WHERE ID = 1")
        record = cursor.fetchone()
        
        if record:
            print(f"   ✓ 找到ID 1: {record['SQLLINE'][:50]}...")
            print(f"     系统: {record['SYSTEMID']}, 状态: {record['analysis_status']}")
        else:
            print("   ✗ 未找到ID为1的记录")
            
            # 检查最小和最大ID
            cursor.execute("SELECT MIN(ID) as min_id, MAX(ID) as max_id FROM am_solline_info")
            ids = cursor.fetchone()
            print(f"   ID范围: {ids['min_id']} - {ids['max_id']}")
        
        # 5. 检查更新操作
        print("\n5. 测试更新操作:")
        if record:
            test_id = record['ID']
            print(f"   测试更新ID {test_id}...")
            
            # 尝试更新
            update_query = "UPDATE am_solline_info SET analysis_status = 'test' WHERE ID = %s"
            affected = cursor.execute(update_query, (test_id,))
            conn.commit()
            
            if affected > 0:
                print(f"   ✓ 更新成功，影响 {affected} 行")
                
                # 恢复原状态
                cursor.execute("UPDATE am_solline_info SET analysis_status = %s WHERE ID = %s", 
                             (record['analysis_status'], test_id))
                conn.commit()
                print("   ✓ 状态已恢复")
            else:
                print("   ✗ 更新失败，未找到记录")
        
        cursor.close()
        conn.close()
        
        print("\n" + "=" * 70)
        print("检查完成")
        print("=" * 70)
        
    except Exception as e:
        print(f"检查失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    check_table()
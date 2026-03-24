#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
添加分析相关字段到am_solline_info表
"""

import pymysql

def add_analysis_fields():
    """添加分析相关字段"""
    try:
        conn = pymysql.connect(
            host='localhost',
            port=3306,
            database='testdb',
            user='root',
            password='123456'
        )
        
        cursor = conn.cursor()
        
        print("开始添加分析相关字段...")
        
        # 首先检查字段是否已存在
        cursor.execute("DESCRIBE am_solline_info")
        columns = cursor.fetchall()
        column_names = [col[0] for col in columns]
        
        # 添加分析状态字段
        if 'analysis_status' not in column_names:
            try:
                cursor.execute("""
                    ALTER TABLE am_solline_info 
                    ADD COLUMN analysis_status ENUM('pending', 'analyzed', 'failed') DEFAULT 'pending' COMMENT '分析状态'
                """)
                print("✓ 添加analysis_status字段")
            except Exception as e:
                print(f"✗ 添加analysis_status字段失败: {e}")
        else:
            print("✓ analysis_status字段已存在")
        
        # 添加分析结果字段
        if 'analysis_result' not in column_names:
            try:
                cursor.execute("""
                    ALTER TABLE am_solline_info 
                    ADD COLUMN analysis_result JSON COMMENT '分析结果'
                """)
                print("✓ 添加analysis_result字段")
            except Exception as e:
                print(f"✗ 添加analysis_result字段失败: {e}")
        else:
            print("✓ analysis_result字段已存在")
        
        # 添加分析时间字段
        if 'analysis_time' not in column_names:
            try:
                cursor.execute("""
                    ALTER TABLE am_solline_info 
                    ADD COLUMN analysis_time TIMESTAMP NULL COMMENT '分析时间'
                """)
                print("✓ 添加analysis_time字段")
            except Exception as e:
                print(f"✗ 添加analysis_time字段失败: {e}")
        else:
            print("✓ analysis_time字段已存在")
        
        # 添加错误信息字段
        if 'error_message' not in column_names:
            try:
                cursor.execute("""
                    ALTER TABLE am_solline_info 
                    ADD COLUMN error_message TEXT COMMENT '错误信息'
                """)
                print("✓ 添加error_message字段")
            except Exception as e:
                print(f"✗ 添加error_message字段失败: {e}")
        else:
            print("✓ error_message字段已存在")
        
        # 检查索引是否存在
        cursor.execute("SHOW INDEX FROM am_solline_info")
        indexes = cursor.fetchall()
        index_names = [index[2] for index in indexes]
        
        # 添加索引
        if 'idx_analysis_status' not in index_names:
            try:
                cursor.execute("CREATE INDEX idx_analysis_status ON am_solline_info (analysis_status)")
                print("✓ 添加idx_analysis_status索引")
            except Exception as e:
                print(f"✗ 添加idx_analysis_status索引失败: {e}")
        else:
            print("✓ idx_analysis_status索引已存在")
        
        if 'idx_tablename' not in index_names:
            try:
                cursor.execute("CREATE INDEX idx_tablename ON am_solline_info (TABLENAME)")
                print("✓ 添加idx_tablename索引")
            except Exception as e:
                print(f"✗ 添加idx_tablename索引失败: {e}")
        else:
            print("✓ idx_tablename索引已存在")
        
        conn.commit()
        print("\n所有字段添加完成！")
        
        # 验证字段是否添加成功
        cursor.execute("DESCRIBE am_solline_info")
        columns = cursor.fetchall()
        column_names = [col[0] for col in columns]
        
        print("\n验证字段添加结果:")
        analysis_fields = ['analysis_status', 'analysis_result', 'analysis_time', 'error_message']
        for field in analysis_fields:
            if field in column_names:
                print(f"  ✓ {field}字段已存在")
            else:
                print(f"  ✗ {field}字段不存在")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f'数据库连接错误: {e}')
    except Exception as e:
        print(f'错误: {e}')

if __name__ == '__main__':
    add_analysis_fields()
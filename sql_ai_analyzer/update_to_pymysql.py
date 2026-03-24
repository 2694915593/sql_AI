#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量更新文件，将mysql.connector替换为pymysql
"""

import os
import re
import glob

def update_file(filepath):
    """更新单个文件"""
    print(f"处理文件: {filepath}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 替换导入语句
    original_content = content
    
    # 替换 import mysql.connector
    content = re.sub(r'^import mysql\.connector', 'import pymysql', content, flags=re.MULTILINE)
    
    # 替换 from mysql.connector import
    content = re.sub(r'^from mysql\.connector import', '# from mysql.connector import  # 已迁移到pymysql', content, flags=re.MULTILINE)
    
    # 替换 mysql.connector.connect
    content = re.sub(r'mysql\.connector\.connect\s*\(', 'pymysql.connect(', content)
    
    # 替换 mysql.connector.Error
    content = re.sub(r'mysql\.connector\.Error', 'Exception', content)
    
    # 替换 mysql.connector.pooling.MySQLConnectionPool
    content = re.sub(r'mysql\.connector\.pooling\.MySQLConnectionPool', '# mysql.connector.pooling.MySQLConnectionPool  # 已迁移到pymysql', content)
    
    # 替换 cursor.fetchone() 访问方式（元组到字典）
    # 这需要更复杂的处理，暂时只做简单替换
    
    if original_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  ✓ 已更新")
        return True
    else:
        print(f"  ⚠ 无需更新")
        return False

def main():
    """主函数"""
    print("开始批量更新文件到pymysql...")
    print("=" * 60)
    
    # 获取所有Python文件
    python_files = glob.glob("**/*.py", recursive=True)
    
    # 排除一些文件
    exclude_files = [
        'utils/db_connector_pymysql.py',  # 新的pymysql连接器
        'test_pymysql.py',  # pymysql测试文件
        'update_to_pymysql.py',  # 本文件
    ]
    
    updated_count = 0
    
    for filepath in python_files:
        # 检查是否在排除列表中
        skip = False
        for exclude in exclude_files:
            if exclude in filepath:
                skip = True
                break
        
        if skip:
            continue
        
        if update_file(filepath):
            updated_count += 1
    
    print("=" * 60)
    print(f"更新完成！共更新了 {updated_count} 个文件")
    print("\n注意：")
    print("1. 部分文件可能需要手动调整fetchone()的访问方式")
    print("2. 元组访问 (record[0]) 需要改为字典访问 (record['column_name'])")
    print("3. 建议运行测试验证更新效果")

if __name__ == '__main__':
    main()
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查分组存储数据为空的具体问题
"""

import json
import sys
import os

def main():
    print("=" * 80)
    print("检查分组存储数据为空的具体问题")
    print("=" * 80)
    
    print("1. 检查配置文件...")
    config_path = 'sql_ai_analyzer/config/config.ini'
    
    if os.path.exists(config_path):
        import configparser
        config = configparser.ConfigParser()
        config.read(config_path, encoding='utf-8')
        
        print(f"   - 配置文件: {config_path}")
        
        # 检查数据库配置
        if 'database' in config:
            db_config = config['database']
            print(f"   - 数据库配置:")
            print(f"     host: {db_config.get('source_host')}")
            print(f"     database: {db_config.get('source_database')}")
            print(f"     username: {db_config.get('source_username')}")
        else:
            print("   ❌ 配置文件中没有[database]配置节")
    else:
        print(f"   ❌ 配置文件不存在: {config_path}")
    
    print("\n2. 检查数据库连接...")
    
    try:
        import pymysql
        
        # 尝试连接数据库
        conn = pymysql.connect(
            host='localhost',
            port=3306,
            user='root',
            password='123456',
            database='testdb',
            charset='utf8mb4'
        )
        
        print(f"   ✅ 成功连接到 testdb 数据库")
        
        # 检查AM_COMMIT_SHELL_INFO表
        with conn.cursor() as cursor:
            # 检查表是否存在
            cursor.execute("SHOW TABLES LIKE 'AM_COMMIT_SHELL_INFO'")
            result = cursor.fetchone()
            
            if result:
                print(f"   ✅ AM_COMMIT_SHELL_INFO表存在")
                
                # 检查表结构
                cursor.execute("DESCRIBE AM_COMMIT_SHELL_INFO")
                columns = cursor.fetchall()
                
                print(f"   - 表结构 ({len(columns)}列):")
                column_names = []
                for col in columns:
                    column_names.append(col[0])
                    print(f"     {col[0]}: {col[1]} ({col[2]})")
                
                # 检查是否有AI_ANALYSE_RESULT字段
                if 'AI_ANALYSE_RESULT' in column_names:
                    print(f"   ✅ AI_ANALYSE_RESULT字段存在")
                else:
                    print(f"   ❌ AI_ANALYSE_RESULT字段不存在")
                    
                    # 尝试添加字段
                    print("   尝试添加AI_ANALYSE_RESULT字段...")
                    try:
                        cursor.execute("""
                            ALTER TABLE AM_COMMIT_SHELL_INFO 
                            ADD COLUMN AI_ANALYSE_RESULT TEXT NULL
                        """)
                        conn.commit()
                        print(f"   ✅ 成功添加AI_ANALYSE_RESULT字段")
                    except Exception as e:
                        print(f"   ❌ 添加字段失败: {e}")
                
                # 检查表中现有数据
                cursor.execute("SELECT COUNT(*) FROM AM_COMMIT_SHELL_INFO")
                count = cursor.fetchone()[0]
                print(f"   - 表中现有记录数: {count}")
                
                # 如果有数据，查看一条
                if count > 0:
                    cursor.execute("SELECT * FROM AM_COMMIT_SHELL_INFO LIMIT 1")
                    row = cursor.fetchone()
                    
                    # 获取列名
                    cursor.execute("SHOW COLUMNS FROM AM_COMMIT_SHELL_INFO")
                    col_names = [col[0] for col in cursor.fetchall()]
                    
                    print(f"   - 第一条记录:")
                    for i, col_name in enumerate(col_names):
                        if i < len(row):
                            value = row[i]
                            if col_name == 'AI_ANALYSE_RESULT':
                                if value:
                                    print(f"     {col_name}: [有内容，长度={len(str(value))}]")
                                else:
                                    print(f"     {col_name}: [空]")
                            else:
                                print(f"     {col_name}: {value}")
            else:
                print(f"   ❌ AM_COMMIT_SHELL_INFO表不存在")
                
                # 尝试创建表
                print("   尝试创建AM_COMMIT_SHELL_INFO表...")
                try:
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS AM_COMMIT_SHELL_INFO (
                            ID INT AUTO_INCREMENT PRIMARY KEY,
                            PROJECT_ID VARCHAR(100) NULL,
                            DEFAULT_VERSION VARCHAR(100) NULL,
                            CLASSPATH VARCHAR(500) NULL,
                            FILENAME VARCHAR(255) NULL,
                            AI_ANALYSE_RESULT TEXT NULL,
                            CREATE_TIME DATETIME DEFAULT CURRENT_TIMESTAMP,
                            UPDATE_TIME DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                        )
                    """)
                    conn.commit()
                    print(f"   ✅ 成功创建AM_COMMIT_SHELL_INFO表")
                except Exception as e:
                    print(f"   ❌ 创建表失败: {e}")
        
        conn.close()
        
    except Exception as e:
        print(f"   ❌ 数据库连接失败: {e}")
        print(f"   请检查数据库服务是否运行，以及配置是否正确")
    
    print("\n3. 检查group_processor_fixed_v2.py中的问题...")
    
    processor_path = 'sql_ai_analyzer/storage/group_processor_fixed_v2.py'
    if os.path.exists(processor_path):
        with open(processor_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查关键方法
        methods_to_check = [
            '_prepare_storage_data',
            'store_to_commit_shell_info',
            'combine_analysis_results'
        ]
        
        for method in methods_to_check:
            if method in content:
                print(f"   ✅ {method}方法存在")
            else:
                print(f"   ❌ {method}方法不存在")
        
        # 检查数据库操作错误处理
        error_handling_keywords = [
            'try:',
            'except Exception as e:',
            'self.logger.error',
            'return False'
        ]
        
        store_method_section = 'def store_to_commit_shell_info'
        start = content.find(store_method_section)
        if start != -1:
            # 找到方法结束位置
            end = content.find('def ', start + len(store_method_section))
            method_content = content[start:end] if end != -1 else content[start:]
            
            print(f"\n   - store_to_commit_shell_info方法内容摘要:")
            lines = method_content.split('\n')
            for i, line in enumerate(lines[:30]):  # 显示前30行
                if line.strip():
                    print(f"     {i+1}: {line[:100]}")
            
            # 检查错误处理
            has_try_except = 'try:' in method_content and 'except Exception' in method_content
            if has_try_except:
                print(f"   ✅ 方法中有错误处理")
            else:
                print(f"   ❌ 方法中缺少错误处理")
    else:
        print(f"   ❌ 文件不存在: {processor_path}")
    
    print("\n4. 问题分析和解决方案:")
    print("   a) 数据库表不存在 - 需要创建AM_COMMIT_SHELL_INFO表")
    print("   b) 字段不存在 - 需要添加AI_ANALYSE_RESULT字段")
    print("   c) 数据库连接失败 - 检查数据库服务是否运行")
    print("   d) 权限问题 - 检查数据库用户是否有读写权限")
    print("   e) 配置错误 - 检查config.ini中的数据库配置")
    
    print("\n5. 建议的SQL修复命令:")
    print("   -- 创建表")
    print("   CREATE TABLE IF NOT EXISTS AM_COMMIT_SHELL_INFO (")
    print("       ID INT AUTO_INCREMENT PRIMARY KEY,")
    print("       PROJECT_ID VARCHAR(100) NULL,")
    print("       DEFAULT_VERSION VARCHAR(100) NULL,")
    print("       CLASSPATH VARCHAR(500) NULL,")
    print("       FILENAME VARCHAR(255) NULL,")
    print("       AI_ANALYSE_RESULT TEXT NULL,")
    print("       CREATE_TIME DATETIME DEFAULT CURRENT_TIMESTAMP,")
    print("       UPDATE_TIME DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")
    print("   );")
    print("")
    print("   -- 添加字段（如果表存在但字段不存在）")
    print("   ALTER TABLE AM_COMMIT_SHELL_INFO ADD COLUMN AI_ANALYSE_RESULT TEXT NULL;")
    
    print("\n6. 测试存储数据...")
    
    # 创建测试数据
    test_data = {
        "summary": {
            "file_name": "TestService.java",
            "project_id": "test_project",
            "default_version": "feature/test",
            "sql_count": 1,
            "file_path": "/src/test/"
        },
        "key_issues": [
            {
                "category": "测试问题",
                "description": "这是测试数据",
                "severity": "中风险"
            }
        ],
        "combined_suggestions": ["测试建议"],
        "sql_summaries": [
            {
                "sql_id": 999,
                "sql_preview": "SELECT * FROM test",
                "sql_type": "查询",
                "score": 7.5
            }
        ],
        "normative_summary": {
            "total_angles": 15,
            "average_compliance_rate": 80.0,
            "failed_angles": []
        },
        "risk_stats": {
            "high_risk_count": 0,
            "medium_risk_count": 1,
            "low_risk_count": 0,
            "total_risk_count": 1
        }
    }
    
    # 保存测试数据
    with open("test_storage_data.json", "w", encoding="utf-8") as f:
        json.dump(test_data, f, ensure_ascii=False, indent=2)
    
    print(f"   ✅ 测试数据已保存到: test_storage_data.json")
    print(f"   数据大小: {len(json.dumps(test_data))} 字符")
    
    print("\n" + "=" * 80)
    print("检查完成！")
    print("=" * 80)

if __name__ == "__main__":
    main()
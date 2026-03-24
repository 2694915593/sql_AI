#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试数据库存储操作，检查为什么分组存储数据为空
"""

import json
import sys
import os
from typing import Dict, Any, List

def test_database_storage():
    """测试数据库存储操作"""
    
    print("=" * 80)
    print("测试数据库存储操作 - 检查为什么分组存储数据为空")
    print("=" * 80)
    
    try:
        # 导入必要的模块
        import pymysql
        
        print("1. 创建测试数据...")
        
        # 创建测试存储数据
        storage_data = {
            "summary": {
                "file_name": "TestService.java",
                "project_id": "test_project",
                "default_version": "feature/test",
                "sql_count": 2,
                "file_path": "/src/test/",
                "average_score": 7.5,
                "total_sqls": 2,
                "unique_files": 1,
                "unique_projects": 1,
                "success_rate": 100.0,
                "analysis_time": "2024-01-01 10:00:00"
            },
            "key_issues": [
                {
                    "category": "高风险问题",
                    "description": "全表扫描风险",
                    "severity": "高风险"
                }
            ],
            "combined_suggestions": [
                "建议1: 添加索引提高查询性能",
                "建议2: 避免全表扫描，添加WHERE条件"
            ],
            "sql_summaries": [
                {
                    "sql_id": 999,
                    "sql_preview": "SELECT * FROM test_table WHERE id = 1",
                    "sql_type": "查询",
                    "score": 7.5,
                    "has_critical_issues": True,
                    "suggestion_count": 3,
                    "compliance_score": 78.5
                },
                {
                    "sql_id": 1000,
                    "sql_preview": "UPDATE test_table SET name = 'test' WHERE id = 2",
                    "sql_type": "更新",
                    "score": 8.0,
                    "has_critical_issues": False,
                    "suggestion_count": 2,
                    "compliance_score": 85.0
                }
            ],
            "normative_summary": {
                "total_angles": 15,
                "average_compliance_rate": 81.75,
                "failed_angles": ["全表扫描"]
            },
            "risk_stats": {
                "high_risk_count": 1,
                "medium_risk_count": 1,
                "low_risk_count": 0,
                "total_risk_count": 2
            }
        }
        
        # 转换为JSON字符串
        json_data = json.dumps(storage_data, ensure_ascii=False, indent=2)
        print(f"✅ 存储数据准备完成，JSON大小: {len(json_data)} 字符")
        print(f"数据预览: {json_data[:500]}...")
        
        print("\n2. 测试数据库连接...")
        
        # 尝试连接数据库
        try:
            # 这里需要实际的数据库配置
            # 先从环境变量或配置文件中获取
            import configparser
            
            config_path = 'sql_ai_analyzer/config/config.ini'
            if os.path.exists(config_path):
                config = configparser.ConfigParser()
                config.read(config_path, encoding='utf-8')
                
                if 'source_db' in config:
                    db_config = config['source_db']
                    
                    host = db_config.get('host', 'localhost')
                    port = int(db_config.get('port', 3306))
                    user = db_config.get('user', 'root')
                    password = db_config.get('password', '')
                    database = db_config.get('database', 'test_db')
                    
                    print(f"   - 数据库配置: {database}@{host}:{port}")
                    
                    # 测试连接
                    try:
                        conn = pymysql.connect(
                            host=host,
                            port=port,
                            user=user,
                            password=password,
                            database=database,
                            charset='utf8mb4'
                        )
                        
                        print(f"✅ 数据库连接成功")
                        
                        # 检查AM_COMMIT_SHELL_INFO表是否存在
                        with conn.cursor() as cursor:
                            cursor.execute("SHOW TABLES LIKE 'AM_COMMIT_SHELL_INFO'")
                            result = cursor.fetchone()
                            
                            if result:
                                print(f"✅ AM_COMMIT_SHELL_INFO表存在")
                                
                                # 检查表结构
                                cursor.execute("DESCRIBE AM_COMMIT_SHELL_INFO")
                                columns = cursor.fetchall()
                                print(f"   - 表列数: {len(columns)}")
                                
                                # 打印列信息
                                print("\n   - 表结构:")
                                for col in columns:
                                    print(f"     {col[0]}: {col[1]} ({col[2]})")
                                
                                # 检查是否有AI_ANALYSE_RESULT字段
                                ai_field_exists = any(col[0] == 'AI_ANALYSE_RESULT' for col in columns)
                                if ai_field_exists:
                                    print(f"✅ AI_ANALYSE_RESULT字段存在")
                                else:
                                    print(f"❌ AI_ANALYSE_RESULT字段不存在！")
                                    
                                    # 尝试添加字段
                                    print("   尝试添加AI_ANALYSE_RESULT字段...")
                                    try:
                                        cursor.execute("""
                                            ALTER TABLE AM_COMMIT_SHELL_INFO 
                                            ADD COLUMN AI_ANALYSE_RESULT TEXT NULL
                                        """)
                                        conn.commit()
                                        print(f"   成功添加AI_ANALYSE_RESULT字段")
                                    except Exception as alter_err:
                                        print(f"   添加字段失败: {alter_err}")
                                        print("   可能需要手动添加字段: ALTER TABLE AM_COMMIT_SHELL_INFO ADD COLUMN AI_ANALYSE_RESULT TEXT NULL")
                            else:
                                print(f"❌ AM_COMMIT_SHELL_INFO表不存在！")
                                
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
                                    print(f"   成功创建AM_COMMIT_SHELL_INFO表")
                                except Exception as create_err:
                                    print(f"   创建表失败: {create_err}")
                                    print("   需要手动创建表")
                                
                        conn.close()
                        
                    except Exception as conn_err:
                        print(f"❌ 数据库连接失败: {conn_err}")
                        print("   请检查数据库配置和连接")
                else:
                    print(f"❌ 配置文件中没有source_db配置节")
            else:
                print(f"❌ 配置文件不存在: {config_path}")
                print(f"   请确保配置文件存在: {config_path}")
                
        except Exception as e:
            print(f"❌ 读取配置失败: {e}")
            print("   将使用模拟数据库操作")
        
        print("\n3. 模拟store_to_commit_shell_info方法...")
        
        # 模拟store_to_commit_shell_info方法
        def simulate_store_to_commit_shell_info(file_name, project_id, default_version, file_path, json_data):
            """模拟存储到AM_COMMIT_SHELL_INFO表的方法"""
            
            print(f"   存储数据:")
            print(f"     - 文件名: {file_name}")
            print(f"     - 项目ID: {project_id}")
            print(f"     - 分支版本: {default_version}")
            print(f"     - 文件路径: {file_path}")
            print(f"     - JSON数据大小: {len(json_data)} 字符")
            
            # 检查更新操作
            check_query = """
                SELECT ID 
                FROM AM_COMMIT_SHELL_INFO 
                WHERE PROJECT_ID = %s 
                AND DEFAULT_VERSION = %s 
                AND FILENAME = %s
            """
            
            print(f"   检查查询: {check_query}")
            print(f"   查询参数: ({project_id}, {default_version}, {file_name})")
            
            # 检查插入操作
            insert_query = """
                INSERT INTO AM_COMMIT_SHELL_INFO 
                (PROJECT_ID, DEFAULT_VERSION, CLASSPATH, FILENAME, AI_ANALYSE_RESULT, CREATE_TIME, UPDATE_TIME)
                VALUES (%s, %s, %s, %s, %s, NOW(), NOW())
            """
            
            print(f"   插入查询: {insert_query}")
            print(f"   插入参数: ({project_id}, {default_version}, {file_path}, {file_name}, [JSON数据...])")
            
            # 检查更新操作
            update_query = """
                UPDATE AM_COMMIT_SHELL_INFO 
                SET AI_ANALYSE_RESULT = %s, 
                    UPDATE_TIME = NOW()
                WHERE ID = %s
            """
            
            print(f"   更新查询: {update_query}")
            
            # 打印一些可能的错误原因
            print("\n4. 常见问题分析:")
            print("   a) 数据库连接失败 - 检查config.ini中的数据库配置")
            print("   b) 表不存在 - AM_COMMIT_SHELL_INFO表需要创建")
            print("   c) 字段不存在 - AI_ANALYSE_RESULT字段需要添加")
            print("   d) 权限问题 - 数据库用户需要有读写权限")
            print("   e) 数据太长 - TEXT字段可能有限制，考虑使用LONGTEXT")
            
            # 建议的修复SQL
            print("\n5. 建议的修复SQL:")
            print("   -- 创建表 (如果不存在)")
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
            print("   -- 添加字段 (如果字段不存在)")
            print("   ALTER TABLE AM_COMMIT_SHELL_INFO ADD COLUMN IF NOT EXISTS AI_ANALYSE_RESULT TEXT NULL;")
            print("")
            print("   -- 检查表结构")
            print("   DESCRIBE AM_COMMIT_SHELL_INFO;")
            
            return True
        
        # 调用模拟方法
        simulate_store_to_commit_shell_info(
            file_name="TestService.java",
            project_id="test_project",
            default_version="feature/test",
            file_path="/src/test/",
            json_data=json_data
        )
        
        print("\n6. 创建修复脚本...")
        
        # 创建修复脚本
        fix_script = """#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
        修复分组存储数据为空的问题

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def fix_group_processor():
    \"\"\"修复group_processor_fixed_v2.py中的存储问题\"\"\"
    
    file_path = "sql_ai_analyzer/storage/group_processor_fixed_v2.py"
    
    if not os.path.exists(file_path):
        print(f"文件不存在: {file_path}")
        return False
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 查找_store_to_commit_shell_info方法
        if "_prepare_storage_data" in content:
            print("✅ _prepare_storage_data方法存在")
        else:
            print("❌ _prepare_storage_data方法不存在")
            return False
        
        # 检查数据库操作逻辑
        if "store_to_commit_shell_info" in content:
            print("✅ store_to_commit_shell_info方法存在")
        else:
            print("❌ store_to_commit_shell_info方法不存在")
            return False
        
        print("\n修复建议:")
        print("1. 确保数据库连接配置正确")
        print("2. 确保AM_COMMIT_SHELL_INFO表存在且包含AI_ANALYSE_RESULT字段")
        print("3. 检查数据库权限")
        print("4. 检查SQL查询是否正确执行")
        
        return True
        
    except Exception as e:
        print(f"❌ 修复过程中发生错误: {e}")
        return False

def create_test_data():
    \"\"\"创建测试数据\"\"\"
    
    test_data = {
        "summary": {
            "file_name": "TestService.java",
            "project_id": "test_project",
            "default_version": "feature/test",
            "sql_count": 2,
            "file_path": "/src/test/"
        },
        "key_issues": [
            {
                "category": "测试问题",
                "description": "这是一个测试问题",
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
    
    import json
    json_data = json.dumps(test_data, ensure_ascii=False, indent=2)
    
    # 保存测试数据
    with open("test_storage_data_fixed.json", "w", encoding="utf-8") as f:
        f.write(json_data)
    
    print(f"✅ 测试数据已保存到: test_storage_data_fixed.json")
    print(f"数据大小: {len(json_data)} 字符")
    
    return test_data

if __name__ == "__main__":
    print("开始修复分组存储数据为空的问题...")
    
    # 创建测试数据
    test_data = create_test_data()
    
    # 尝试修复
    if fix_group_processor():
        print("\n✅ 修复分析完成")
        print("请按照上述建议检查数据库配置和表结构")
    else:
        print("\n❌ 修复分析失败")

"""
        
        with open("fix_storage_issue.py", "w", encoding="utf-8") as f:
            f.write(fix_script)
        
        print(f"✅ 修复脚本已创建: fix_storage_issue.py")
        
        print("\n✅ 测试完成！")
        return True
        
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("开始测试数据库存储操作...")
    
    success = test_database_storage()
    
    if success:
        print("\n✓ 测试完成！")
        return 0
    else:
        print("\n✗ 测试失败！")
        return 1

if __name__ == "__main__":
    sys.exit(main())
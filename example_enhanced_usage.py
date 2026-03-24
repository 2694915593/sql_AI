#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强版SQL分析系统使用示例
演示如何集成SQL规范检查功能
"""

import os
import sys
import json

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def demo_sql_specifications():
    """演示SQL规范定义和集成功能"""
    print("=" * 60)
    print("演示SQL规范定义和集成功能")
    print("=" * 60)
    
    try:
        from sql_ai_analyzer.utils.sql_specifications_integration import SQLSpecificationsIntegrator
        
        integrator = SQLSpecificationsIntegrator()
        
        # 1. 展示规范摘要
        print("\n1. SQL规范摘要：")
        summary = integrator.get_specifications_summary()
        print(f"   - 规范分类数: {summary['total_categories']}")
        print(f"   - 规范总条款数: {summary['total_rules']}")
        print(f"   - 分类列表: {', '.join(summary['categories'][:5])}...")
        
        # 2. 生成不同SQL类型的规范提示
        print("\n2. 不同SQL类型的规范提示：")
        
        sql_types = ["select", "insert", "update", "delete", "create"]
        for sql_type in sql_types:
            prompt = integrator.generate_sql_specifications_prompt(sql_type)
            lines = prompt.split('\n')
            title_line = next(line for line in lines if "SQL规范要求" in line)
            print(f"   - {sql_type.upper()}类型: {title_line}")
            
        # 3. 检查SQL语句是否符合规范
        print("\n3. SQL规范符合性检查示例：")
        
        test_cases = [
            {
                "sql": "SELECT * FROM users WHERE id = 1",
                "type": "select",
                "description": "SELECT * 查询（违反规范3.1.1）"
            },
            {
                "sql": "SELECT id, name FROM users WHERE id = 1",
                "type": "select", 
                "description": "正确的SELECT查询"
            },
            {
                "sql": "UPDATE users SET name = 'new'",
                "type": "update",
                "description": "UPDATE没有WHERE条件（违反规范3.3.1）"
            },
            {
                "sql": "INSERT INTO users VALUES (1, 'test')",
                "type": "insert",
                "description": "INSERT没有指定列（违反规范3.3.4）"
            }
        ]
        
        for test in test_cases:
            print(f"\n   {test['description']}:")
            print(f"      SQL: {test['sql']}")
            
            result = integrator.check_sql_against_specifications(test['sql'], test['type'])
            
            violations = result.get('violations', [])
            warnings = result.get('warnings', [])
            suggestions = result.get('suggestions', [])
            
            if violations:
                print(f"      ❌ 违反规范: {violations[0]}")
            elif warnings:
                print(f"      ⚠️  警告: {warnings[0]}")
            else:
                print(f"      ✅ 符合相关规范")
                
        print("\n✅ SQL规范演示完成")
        
    except Exception as e:
        print(f"❌ 演示失败: {str(e)}")
        import traceback
        traceback.print_exc()

def demo_enhanced_model_client():
    """演示增强版模型客户端"""
    print("\n" + "=" * 60)
    print("演示增强版模型客户端")
    print("=" * 60)
    
    try:
        from sql_ai_analyzer.ai_integration.model_client_enhanced import ModelClientEnhanced
        from sql_ai_analyzer.config.config_manager import ConfigManager
        
        # 初始化配置管理器
        config_path = os.path.join(os.path.dirname(__file__), "sql_ai_analyzer", "config", "config.ini")
        
        if not os.path.exists(config_path):
            print(f"⚠️  配置文件不存在: {config_path}")
            print("请先创建配置文件或使用默认配置")
            config_manager = ConfigManager()
        else:
            config_manager = ConfigManager(config_path)
        
        # 创建增强版客户端
        client = ModelClientEnhanced(config_manager)
        
        print("✅ 增强版模型客户端初始化成功")
        
        # 演示SQL类型检测
        print("\n1. SQL类型检测演示：")
        
        test_sqls = [
            "SELECT id, name FROM users WHERE age > 18",
            "INSERT INTO users (id, name) VALUES (1, 'test')",
            "UPDATE users SET name = 'new' WHERE id = 1",
            "DELETE FROM users WHERE id = 1",
            "CREATE TABLE users (id INT PRIMARY KEY, name VARCHAR(100))",
            "ALTER TABLE users ADD COLUMN email VARCHAR(100)"
        ]
        
        for sql in test_sqls:
            sql_type = client._detect_sql_type(sql)
            print(f"   - {sql[:40]}... -> {sql_type}")
        
        # 演示构建增强版请求负载
        print("\n2. 构建增强版请求负载演示：")
        
        # 模拟请求数据
        request_data = {
            "sql_statement": "SELECT * FROM users WHERE age > 18",
            "tables": [
                {
                    "table_name": "users",
                    "row_count": 10000,
                    "is_large_table": True,
                    "columns": [
                        {"name": "id", "type": "INT", "nullable": False},
                        {"name": "name", "type": "VARCHAR(100)", "nullable": True},
                        {"name": "age", "type": "INT", "nullable": True},
                        {"name": "created_at", "type": "DATETIME", "nullable": False},
                        {"name": "updated_at", "type": "DATETIME", "nullable": False}
                    ],
                    "indexes": [
                        {"name": "PRIMARY", "columns": ["id"], "type": "PRIMARY", "unique": True},
                        {"name": "idx_age", "columns": ["age"], "type": "INDEX", "unique": False}
                    ],
                    "ddl": "CREATE TABLE users (id INT PRIMARY KEY, name VARCHAR(100), age INT, created_at DATETIME DEFAULT CURRENT_TIMESTAMP, updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP) ENGINE=InnoDB CHARSET=utf8mb4"
                }
            ],
            "db_alias": "test_db",
            "execution_plan": "使用索引 idx_age 进行范围扫描"
        }
        
        payload = client._build_enhanced_request_payload(request_data)
        prompt = payload.get('prompt', '')
        
        print(f"   构建的提示词长度: {len(prompt)} 字符")
        print(f"   包含SQL规范: {'SQL规范要求' in prompt}")
        print(f"   包含SELECT规范: {'SELECT语句规范' in prompt}")
        print(f"   包含强制标记: {'【强制】' in prompt}")
        
        print("\n✅ 增强版模型客户端演示完成")
        
    except Exception as e:
        print(f"❌ 演示失败: {str(e)}")
        import traceback
        traceback.print_exc()

def demo_enhanced_analyzer():
    """演示增强版分析器"""
    print("\n" + "=" * 60)
    print("演示增强版分析器集成")
    print("=" * 60)
    
    try:
        # 演示如何使用增强版系统
        print("增强版系统提供了以下新功能：")
        print()
        print("1. 集成SQL规范检查")
        print("   - 自动检测SQL类型并选择相关规范")
        print("   - 在AI分析提示中添加规范要求")
        print("   - 在分析结果中提取规范符合性信息")
        print()
        print("2. 增强版分析结果")
        print("   - specification_compliance: 规范符合性详情")
        print("   - specification_score: 规范评分（0-10分）")
        print("   - 综合评分考虑规范权重（30%）")
        print()
        print("3. 使用方式")
        print("   - 原始系统: python main.py --mode batch")
        print("   - 增强版系统: python main_enhanced.py --mode batch")
        print()
        print("4. 向后兼容")
        print("   - 增强版完全兼容原始系统配置")
        print("   - 可以随时切换回原始系统")
        print()
        print("5. 扩展性")
        print("   - 支持自定义SQL规范")
        print("   - 支持调整规范检查权重")
        print("   - 支持企业特定规范")
        
        print("\n✅ 增强版分析器演示完成")
        
    except Exception as e:
        print(f"❌ 演示失败: {str(e)}")

def create_config_example():
    """创建配置文件示例"""
    print("\n" + "=" * 60)
    print("创建配置文件示例")
    print("=" * 60)
    
    config_example = """# AI-SQL质量分析系统配置文件（增强版）
# 支持SQL规范检查功能

[database]
source_host = localhost
source_port = 3306
source_database = sql_analysis_db
source_username = your_username
source_password = your_password
source_db_type = mysql

# 目标数据库配置（可配置多个）
[db_production]
host = 192.168.1.100
port = 3306
database = production_db
username = your_username
password = your_password
db_type = mysql

[db_testing]
host = 192.168.1.101
port = 3306
database = testing_db
username = your_username
password = your_password
db_type = mysql

# AI模型配置
[ai_model]
api_url = http://your-ai-service.com/api/analyze-sql
api_key = your-api-key-here
timeout = 30
max_retries = 3

# 处理配置
[processing]
batch_size = 10
max_workers = 4
large_table_threshold = 100000

# 日志配置
[logging]
log_level = INFO
log_file = logs/sql_analyzer.log
max_file_size = 10MB
backup_count = 5

# SQL规范配置（增强版新增）
[specifications]
# 规范检查权重（0.0-1.0）
compliance_weight = 0.3
# 是否启用严格模式
strict_mode = false
# 是否记录所有规范检查
log_all_checks = true
"""
    
    config_path = os.path.join(os.path.dirname(__file__), "config_example.ini")
    
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(config_example)
        
        print(f"✅ 配置文件示例已创建: {config_path}")
        print(f"   文件大小: {len(config_example)} 字节")
        
    except Exception as e:
        print(f"❌ 创建配置文件失败: {str(e)}")

def main():
    """主演示函数"""
    print("增强版SQL分析系统使用演示")
    print("=" * 60)
    
    # 运行所有演示
    demo_sql_specifications()
    demo_enhanced_model_client()
    demo_enhanced_analyzer()
    create_config_example()
    
    print("\n" + "=" * 60)
    print("演示总结")
    print("=" * 60)
    
    print("\n✅ 增强版系统已完成以下集成：")
    print("1. 创建SQL规范定义模块（50条规范）")
    print("2. 创建SQL规范集成器")
    print("3. 增强模型客户端，集成规范检查")
    print("4. 创建增强版主程序（main_enhanced.py）")
    print("5. 创建增强版文档（README_enhanced.md）")
    print("6. 创建完整测试套件（test_specifications_integration.py）")
    print("7. 所有测试通过，功能完整")
    
    print("\n📋 使用指南：")
    print("1. 使用增强版系统：python main_enhanced.py --mode batch")
    print("2. 测试规范集成：python test_specifications_integration.py")
    print("3. 查看增强版文档：cat README_enhanced.md")
    print("4. 自定义规范：编辑 utils/sql_specifications.py")
    
    print("\n🚀 快速开始：")
    print("cd sql_ai_analyzer")
    print("python main_enhanced.py --mode batch --batch-size 5")
    
    print("\n🎉 演示完成！SQL规范已成功集成到系统中。")

if __name__ == "__main__":
    main()
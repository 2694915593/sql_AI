#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SQL规范集成测试脚本
测试SQL规范集成到系统的效果
"""

import sys
import os
import json
from typing import Dict, Any

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_sql_specifications_module():
    """测试SQL规范模块"""
    print("=" * 60)
    print("测试SQL规范模块")
    print("=" * 60)
    
    try:
        from sql_ai_analyzer.utils.sql_specifications import SQLSpecificationsManager
        
        manager = SQLSpecificationsManager()
        
        # 测试1：获取规范摘要
        print("\n1. 测试获取规范摘要：")
        summary = manager.get_specifications_summary()
        print(f"规范分类数: {summary['total_categories']}")
        print(f"规范总条款数: {summary['total_rules']}")
        print(f"强制条款数: {summary['mandatory_rules']}")
        print(f"推荐条款数: {summary['recommended_rules']}")
        print(f"分类列表: {summary['categories'][:5]}...")
        
        # 测试2：按SQL类型获取规范
        print("\n2. 测试按SQL类型获取规范：")
        from sql_ai_analyzer.utils.sql_specifications import SQLType
        select_rules = manager.get_specifications_by_sql_type(SQLType.SELECT)
        print(f"SELECT相关规范数量: {len(select_rules)}")
        
        # 测试3：SQL类型检测
        print("\n3. 测试SQL类型检测：")
        test_sqls = [
            ("SELECT * FROM users", "select"),
            ("INSERT INTO users (id, name) VALUES (1, 'test')", "insert"),
            ("UPDATE users SET name = 'new' WHERE id = 1", "update"),
            ("CREATE TABLE users (id INT PRIMARY KEY)", "create")
        ]
        
        for sql, expected_type in test_sqls:
            detected_type = manager.detect_sql_type(sql)
            status = "✅" if detected_type.value == expected_type else "❌"
            print(f"  {status} SQL: {sql[:30]}... -> 检测类型: {detected_type.value} (期望: {expected_type})")
        
        # 测试4：生成详细规范报告
        print("\n4. 测试生成详细规范报告（前500字符）：")
        report = manager.generate_detailed_specifications_report()
        print(report[:500] + "..." if len(report) > 500 else report)
        
        # 测试5：规范检查
        print("\n5. 测试规范检查：")
        check_result = manager.check_sql_against_specifications("SELECT * FROM users")
        print(f"  合规规则数: {len(check_result['compliant_rules'])}")
        print(f"  违规规则数: {len(check_result['violated_rules'])}")
        print(f"  合规评分: {check_result['compliance_score']:.1f}%")
        
        print("\n✅ SQL规范模块测试通过")
        return True
        
    except Exception as e:
        print(f"❌ SQL规范模块测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_specifications_integration():
    """测试规范集成功能"""
    print("\n" + "=" * 60)
    print("测试规范集成功能")
    print("=" * 60)
    
    try:
        from sql_ai_analyzer.utils.sql_specifications import integrate_specifications_into_prompt, create_sql_specifications_checklist, SQLType
        
        # 测试1：集成规范到提示
        print("\n1. 测试集成规范到提示：")
        prompt_parts = ["SQL分析请求：", "请分析以下SQL语句："]
        enhanced_parts = integrate_specifications_into_prompt(prompt_parts, SQLType.SELECT)
        
        print(f"原始提示部分数: {len(prompt_parts)}")
        print(f"增强后提示部分数: {len(enhanced_parts)}")
        
        # 检查是否添加了规范内容
        has_specifications = any("SQL规范要求" in part for part in enhanced_parts)
        print(f"是否包含规范要求: {'是' if has_specifications else '否'}")
        
        # 测试2：创建检查清单
        print("\n2. 测试创建SQL规范检查清单：")
        checklist = create_sql_specifications_checklist(SQLType.SELECT)
        
        print(f"检查清单分类数: {len(checklist)}")
        for category, details in checklist.items():
            print(f"  - {category}: {details['description']} ({len(details['items'])}个检查项)")
        
        # 测试INSERT语句检查清单
        print("\n3. 测试INSERT语句检查清单：")
        insert_checklist = create_sql_specifications_checklist(SQLType.INSERT)
        print(f"INSERT检查清单分类数: {len(insert_checklist)}")
        
        print("\n✅ 规范集成功能测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 规范集成功能测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_enhanced_model_client():
    """测试增强版模型客户端"""
    print("\n" + "=" * 60)
    print("测试增强版模型客户端")
    print("=" * 60)
    
    try:
        from sql_ai_analyzer.ai_integration.model_client_enhanced import ModelClient
        from sql_ai_analyzer.config.config_manager import ConfigManager
        
        # 初始化配置管理器
        config_path = os.path.join(os.path.dirname(__file__), "sql_ai_analyzer", "config", "config.ini")
        config_manager = ConfigManager(config_path)
        
        # 创建增强版客户端
        client = ModelClient(config_manager)
        
        print("✅ 增强版模型客户端初始化成功")
        
        # 测试SQL类型检测
        print("\n测试SQL类型检测：")
        
        test_sqls = [
            ("SELECT * FROM users", "select"),
            ("INSERT INTO users (id, name) VALUES (1, 'test')", "insert"),
            ("UPDATE users SET name = 'new' WHERE id = 1", "update"),
            ("DELETE FROM users WHERE id = 1", "delete"),
            ("CREATE TABLE users (id INT PRIMARY KEY)", "create"),
            ("ALTER TABLE users ADD COLUMN email VARCHAR(100)", "alter"),
            ("DROP TABLE users", "drop"),
            ("TRUNCATE TABLE users", "truncate"),
            ("SHOW TABLES", "其他")
        ]
        
        for sql, expected_type in test_sqls:
            detected_type = client._detect_sql_type(sql)
            status = "✅" if detected_type == expected_type else "❌"
            print(f"  {status} SQL: {sql[:30]}... -> 检测类型: {detected_type} (期望: {expected_type})")
        
        print("\n✅ 增强版模型客户端测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 增强版模型客户端测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_sql_specifications_compliance():
    """测试SQL规范符合性检查"""
    print("\n" + "=" * 60)
    print("测试SQL规范符合性检查")
    print("=" * 60)
    
    try:
        from sql_ai_analyzer.utils.sql_specifications import SQLSpecificationsManager, SQLType
        
        manager = SQLSpecificationsManager()
        
        # 测试SQL语句
        test_cases = [
            {
                "sql": "SELECT * FROM users",
                "type": SQLType.SELECT,
                "description": "SELECT * 查询（违反规范3.1.1）"
            },
            {
                "sql": "SELECT id, name FROM users WHERE id = 1",
                "type": SQLType.SELECT,
                "description": "正确的SELECT查询"
            },
            {
                "sql": "INSERT INTO users VALUES (1, 'test', '2023-01-01')",
                "type": SQLType.INSERT,
                "description": "INSERT没有指定列（违反规范3.3.4）"
            },
            {
                "sql": "INSERT INTO users (id, name, created_at) VALUES (1, 'test', NOW())",
                "type": SQLType.INSERT,
                "description": "正确的INSERT语句"
            },
            {
                "sql": "UPDATE users SET name = 'new'",
                "type": SQLType.UPDATE,
                "description": "UPDATE没有WHERE条件（违反规范3.3.1）"
            },
            {
                "sql": "DELETE FROM users",
                "type": SQLType.DELETE,
                "description": "DELETE没有WHERE条件（违反规范3.3.1）"
            }
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n{i}. {test_case['description']}:")
            print(f"   SQL: {test_case['sql']}")
            
            result = manager.check_sql_against_specifications(test_case['sql'], test_case['type'])
            
            compliant_count = len(result.get('compliant_rules', []))
            violated_count = len(result.get('violated_rules', []))
            
            print(f"   符合规范数: {compliant_count}")
            print(f"   违反规范数: {violated_count}")
            
            if violated_count > 0:
                print(f"   违反的规范: {result.get('violated_rules', [])[:3]}...")
            else:
                print(f"   ✅ 符合所有相关规范")
        
        print("\n✅ SQL规范符合性检查测试通过")
        return True
        
    except Exception as e:
        print(f"❌ SQL规范符合性检查测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_complete_integration():
    """测试完整集成"""
    print("\n" + "=" * 60)
    print("测试完整集成")
    print("=" * 60)
    
    try:
        from sql_ai_analyzer.utils.sql_specifications import integrate_specifications_into_prompt, SQLType
        
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
                    "ddl": "CREATE TABLE users (\n  id INT PRIMARY KEY,\n  name VARCHAR(100),\n  age INT,\n  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,\n  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP\n) ENGINE=InnoDB CHARSET=utf8mb4"
                }
            ],
            "db_alias": "test_db",
            "execution_plan": "使用索引 idx_age 进行范围扫描",
            "execution_plan_info": {
                "has_execution_plan": True,
                "db_type": "MySQL",
                "plan_summary": {
                    "access_types": ["range_scan"],
                    "estimated_rows": 5000,
                    "key_used": True,
                    "has_full_scan": False,
                    "warnings": []
                }
            }
        }
        
        # 构建增强版提示
        prompt_parts = [
            f"SQL语句：\n{request_data['sql_statement']}\n",
            f"数据库：{request_data['db_alias']}\n",
            f"表信息：\n{json.dumps(request_data['tables'], indent=2, ensure_ascii=False)}\n"
        ]
        
        enhanced_parts = integrate_specifications_into_prompt(prompt_parts, SQLType.SELECT)
        enhanced_prompt = "\n".join(enhanced_parts)
        
        print("增强版提示构建成功")
        print(f"提示长度: {len(enhanced_prompt)} 字符")
        print(f"提示预览（前500字符）:\n{enhanced_prompt[:500]}...")
        
        # 检查关键内容
        checks = [
            ("SQL规范要求", "包含规范标题"),
            ("SELECT语句规范", "包含SELECT规范"),
            ("规范3.1.1", "包含具体规范编号"),
            ("【强制】", "包含强制标记"),
            ("基于以上SQL规范的分析要求", "包含分析要求")
        ]
        
        all_passed = True
        for keyword, description in checks:
            if keyword in enhanced_prompt:
                print(f"✅ {description}: 包含 '{keyword}'")
            else:
                print(f"❌ {description}: 缺少 '{keyword}'")
                all_passed = False
        
        if all_passed:
            print("\n✅ 完整集成测试通过")
            return True
        else:
            print("\n❌ 完整集成测试失败")
            return False
        
    except Exception as e:
        print(f"❌ 完整集成测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("开始SQL规范集成测试")
    print("=" * 60)
    
    test_results = []
    
    # 运行所有测试
    test_results.append(("SQL规范模块测试", test_sql_specifications_module()))
    test_results.append(("规范集成功能测试", test_specifications_integration()))
    test_results.append(("增强版模型客户端测试", test_enhanced_model_client()))
    test_results.append(("SQL规范符合性检查测试", test_sql_specifications_compliance()))
    test_results.append(("完整集成测试", test_complete_integration()))
    
    # 汇总测试结果
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    
    passed_count = 0
    total_count = len(test_results)
    
    for test_name, passed in test_results:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{test_name}: {status}")
        if passed:
            passed_count += 1
    
    print(f"\n总共 {total_count} 个测试，通过 {passed_count} 个")
    
    if passed_count == total_count:
        print("\n🎉 所有测试通过！SQL规范集成成功。")
        return 0
    else:
        print(f"\n⚠️  {total_count - passed_count} 个测试失败。")
        return 1

if __name__ == "__main__":
    sys.exit(main())
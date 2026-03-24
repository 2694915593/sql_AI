#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试分组存储数据为空的问题
"""

import json
import sys
from typing import Dict, Any, List

def create_test_data():
    """创建测试数据"""
    
    # 创建单个SQL分析结果（新格式）
    sql_analysis = {
        "summary": {
            "sql_type": "查询",
            "score": 7.5,
            "compliance_score": 78.5,
            "has_critical_issues": True,
            "suggestion_count": 3
        },
        "key_issues": [
            {
                "type": "规范性评审",
                "category": "全表扫描",
                "severity": "高风险",
                "description": "查询条件不充分可能导致全表扫描",
                "suggestion": "优化查询条件，添加索引"
            }
        ],
        "suggestions": [
            "建议1: 添加索引提高查询性能",
            "建议2: 避免全表扫描，添加WHERE条件"
        ],
        "normative_summary": {
            "total_angles": 15,
            "passed": 12,
            "failed": ["全表扫描"],
            "compliance_rate": 80.0
        },
        "optimized_sql": "SELECT id, name FROM users WHERE status = 'active'"
    }
    
    return sql_analysis

def test_prepare_storage_data():
    """测试_prepare_storage_data方法"""
    
    print("=" * 80)
    print("调试分组存储数据为空问题")
    print("=" * 80)
    
    try:
        # 导入必要的模块
        import os
        import sys
        
        # 添加项目路径
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        
        # 导入GroupProcessor
        from sql_ai_analyzer.storage.group_processor_fixed_v2 import GroupProcessor
        
        print("1. 创建测试数据...")
        
        # 创建测试分组数据
        group_data = {
            'file_name': 'TestService.java',
            'project_id': 'test_project',
            'default_version': 'feature/test',
            'file_path': '/src/test/',
            'sqls': [
                {
                    'sql_id': 999,
                    'sql_text': 'SELECT * FROM test_table WHERE id = 1',
                    'analysis_data': create_test_data(),
                    'sql_info': {
                        'project_id': 'test_project',
                        'default_version': 'feature/test',
                        'file_path': '/src/test/',
                        'file_name': 'TestService.java',
                        'system_id': 'test_system',
                        'author': '测试员',
                        'operate_type': 'select'
                    }
                }
            ]
        }
        
        # 创建组合分析结果
        combined_result = {
            "summary": {
                "total_sqls": 1,
                "unique_files": 1,
                "unique_projects": 1,
                "analysis_time": "2024-01-01 10:00:00",
                "average_score": 7.5,
                "success_rate": 100.0
            },
            "sql_list": [
                {
                    "sql_id": 999,
                    "sql_preview": "SELECT * FROM test_table WHERE id = 1",
                    "sql_type": "查询",
                    "score": 7.5,
                    "suggestion_count": 2
                }
            ],
            "combined_analysis": {
                "all_suggestions": [
                    {
                        "sql_id": 999,
                        "sql_preview": "SELECT * FROM test_table WHERE id = 1",
                        "suggestions": [
                            {"text": "建议1: 添加索引提高查询性能", "type": "general"},
                            {"text": "建议2: 避免全表扫描，添加WHERE条件", "type": "general"}
                        ]
                    }
                ],
                "risk_summary": {
                    "高风险问题数量": 1,
                    "中风险问题数量": 0,
                    "低风险问题数量": 0,
                    "详细问题": {
                        "高风险问题": ["全表扫描风险"],
                        "中风险问题": [],
                        "低风险问题": []
                    }
                },
                "performance_summary": {
                    "全表扫描次数": 1,
                    "索引缺失次数": 0,
                    "性能问题总数": 1
                },
                "security_summary": {
                    "sql注入风险": 0,
                    "权限问题": 0,
                    "安全风险总数": 0
                }
            }
        }
        
        print("2. 创建GroupProcessor实例...")
        
        # 创建模拟的config_manager和logger
        class MockConfigManager:
            def __init__(self):
                self.config = {}
        
        class MockLogger:
            def __init__(self):
                self.messages = []
            
            def info(self, msg):
                self.messages.append(("INFO", msg))
                print(f"INFO: {msg}")
            
            def warning(self, msg):
                self.messages.append(("WARNING", msg))
                print(f"WARNING: {msg}")
            
            def error(self, msg, exc_info=False):
                self.messages.append(("ERROR", msg))
                print(f"ERROR: {msg}")
                if exc_info:
                    import traceback
                    traceback.print_exc()
            
            def debug(self, msg):
                self.messages.append(("DEBUG", msg))
                print(f"DEBUG: {msg}")
        
        config_manager = MockConfigManager()
        logger = MockLogger()
        
        # 创建GroupProcessor实例
        processor = GroupProcessor(config_manager, logger)
        
        print("3. 调用_prepare_storage_data方法...")
        
        # 调用_prepare_storage_data方法
        storage_data = processor._prepare_storage_data(group_data, combined_result)
        
        print("4. 检查存储数据...")
        
        # 检查数据是否为空
        if not storage_data:
            print("❌ 存储数据为空！")
            return False
        
        print(f"✅ 存储数据不为空，字段数: {len(storage_data)}")
        
        # 转换为JSON字符串
        json_data = json.dumps(storage_data, ensure_ascii=False)
        print(f"✅ JSON数据大小: {len(json_data)} 字符")
        
        # 检查关键字段
        required_fields = ['summary', 'key_issues', 'combined_suggestions', 'sql_summaries', 'normative_summary', 'risk_stats']
        missing_fields = [field for field in required_fields if field not in storage_data]
        
        if missing_fields:
            print(f"❌ 缺少关键字段: {missing_fields}")
            return False
        
        print("✅ 所有关键字段都存在")
        
        # 检查字段内容
        print("\n5. 字段内容检查:")
        
        print(f"   - summary: {storage_data['summary'].get('file_name')}")
        print(f"   - key_issues数量: {len(storage_data['key_issues'])}")
        print(f"   - combined_suggestions数量: {len(storage_data['combined_suggestions'])}")
        print(f"   - sql_summaries数量: {len(storage_data['sql_summaries'])}")
        print(f"   - normative_summary.total_angles: {storage_data['normative_summary'].get('total_angles')}")
        print(f"   - risk_stats.total_risk_count: {storage_data['risk_stats'].get('total_risk_count')}")
        
        # 检查是否有空列表或空字典
        empty_fields = []
        
        if isinstance(storage_data.get('key_issues'), list) and len(storage_data['key_issues']) == 0:
            empty_fields.append('key_issues')
        
        if isinstance(storage_data.get('combined_suggestions'), list) and len(storage_data['combined_suggestions']) == 0:
            empty_fields.append('combined_suggestions')
        
        if isinstance(storage_data.get('sql_summaries'), list) and len(storage_data['sql_summaries']) == 0:
            empty_fields.append('sql_summaries')
        
        if empty_fields:
            print(f"❌ 以下字段为空: {empty_fields}")
            
            # 详细检查原因
            print("\n6. 详细调试信息:")
            
            # 检查combined_result中的risk_summary
            print(f"   - combined_result.risk_summary: {combined_result.get('combined_analysis', {}).get('risk_summary', {})}")
            
            # 检查all_suggestions
            print(f"   - combined_result.all_suggestions: {combined_result.get('combined_analysis', {}).get('all_suggestions', [])}")
            
            # 检查group_data中的analysis_data
            print(f"   - group_data.sqls[0].analysis_data.key_issues: {group_data['sqls'][0].get('analysis_data', {}).get('key_issues', [])}")
            print(f"   - group_data.sqls[0].analysis_data.suggestions: {group_data['sqls'][0].get('analysis_data', {}).get('suggestions', [])}")
            
            return False
        else:
            print("✅ 所有字段都有内容")
        
        print("\n7. 完整存储数据结构:")
        print(json.dumps(storage_data, ensure_ascii=False, indent=2)[:1000] + "..." if len(json.dumps(storage_data, ensure_ascii=False, indent=2)) > 1000 else json.dumps(storage_data, ensure_ascii=False, indent=2))
        
        # 保存测试结果
        with open("debug_storage_data.json", "w", encoding="utf-8") as f:
            json.dump(storage_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ 测试完成，数据已保存到: debug_storage_data.json")
        return True
        
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("开始调试分组存储数据为空问题...")
    
    success = test_prepare_storage_data()
    
    if success:
        print("\n✓ 调试完成！")
        return 0
    else:
        print("\n✗ 调试失败！")
        return 1

if __name__ == "__main__":
    sys.exit(main())
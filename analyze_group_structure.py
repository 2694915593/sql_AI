#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析分组分析的数据结构
"""

import json
from typing import Dict, Any, List

def create_sample_group_data():
    """创建分组分析的测试数据"""
    
    # 创建一个典型的SQL分析结果
    sql_analysis_result = {
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
            },
            {
                "type": "规范性评审", 
                "category": "索引设计",
                "severity": "中风险",
                "description": "缺少适当的索引，查询性能可能受影响",
                "suggestion": "添加合适的索引"
            }
        ],
        "suggestions": [
            "建议1: 添加索引提高查询性能",
            "建议2: 避免全表扫描，添加WHERE条件",
            "建议3: 检查字符集一致性"
        ],
        "normative_summary": {
            "total_angles": 15,
            "passed": 12,
            "failed": ["全表扫描", "索引设计", "字符集问题"],
            "compliance_rate": 80.0
        },
        "optimized_sql": "-- 优化建议\nSELECT id, name, email FROM users WHERE status = 'active' AND created_at > '2024-01-01'"
    }
    
    # 创建分组数据（模拟 group_data）
    group_data = {
        'file_name': 'UserService.java',
        'project_id': 'project_001',
        'default_version': 'feature/login',
        'file_path': '/src/main/java/com/example/service/',
        'sqls': [
            {
                'sql_id': 1001,
                'sql_text': 'SELECT * FROM users WHERE status = "active"',
                'analysis_data': sql_analysis_result,
                'sql_info': {
                    'project_id': 'project_001',
                    'default_version': 'feature/login',
                    'file_path': '/src/main/java/com/example/service/',
                    'file_name': 'UserService.java',
                    'system_id': 'system_001',
                    'author': '张三',
                    'operate_type': 'insert'
                }
            },
            {
                'sql_id': 1002,
                'sql_text': 'UPDATE users SET last_login = NOW() WHERE id = 123',
                'analysis_data': {
                    "summary": {
                        "sql_type": "更新",
                        "score": 8.0,
                        "compliance_score": 85.0,
                        "has_critical_issues": False,
                        "suggestion_count": 2
                    },
                    "key_issues": [
                        {
                            "type": "规范性评审",
                            "category": "字符集问题",
                            "severity": "中风险",
                            "description": "未指定字符集可能导致乱码问题",
                            "suggestion": "明确指定字符集如utf8mb4"
                        }
                    ],
                    "suggestions": [
                        "建议1: 添加字符集设置",
                        "建议2: 添加事务控制"
                    ],
                    "normative_summary": {
                        "total_angles": 15,
                        "passed": 14,
                        "failed": ["字符集问题"],
                        "compliance_rate": 93.3
                    },
                    "optimized_sql": "UPDATE users SET last_login = NOW() WHERE id = 123"
                },
                'sql_info': {
                    'project_id': 'project_001',
                    'default_version': 'feature/login',
                    'file_path': '/src/main/java/com/example/service/',
                    'file_name': 'UserService.java',
                    'system_id': 'system_001',
                    'author': '张三',
                    'operate_type': 'update'
                }
            }
        ]
    }
    
    # 模拟组合分析结果
    combined_result = {
        "summary": {
            "total_sqls": 2,
            "unique_files": 1,
            "unique_projects": 1,
            "analysis_time": "2024-01-01 10:00:00",
            "average_score": 7.75,
            "success_rate": 100.0
        },
        "sql_list": [
            {
                "sql_id": 1001,
                "sql_preview": "SELECT * FROM users WHERE status = 'active'",
                "sql_type": "查询",
                "score": 7.5,
                "suggestion_count": 3
            },
            {
                "sql_id": 1002,
                "sql_preview": "UPDATE users SET last_login = NOW() WHERE id = 123",
                "sql_type": "更新",
                "score": 8.0,
                "suggestion_count": 2
            }
        ],
        "combined_analysis": {
            "all_suggestions": [
                {
                    "sql_id": 1001,
                    "sql_preview": "SELECT * FROM users WHERE status = 'active'",
                    "suggestions": [
                        {"text": "建议1: 添加索引提高查询性能", "type": "general"},
                        {"text": "建议2: 避免全表扫描，添加WHERE条件", "type": "general"},
                        {"text": "建议3: 检查字符集一致性", "type": "general"}
                    ]
                },
                {
                    "sql_id": 1002,
                    "sql_preview": "UPDATE users SET last_login = NOW() WHERE id = 123",
                    "suggestions": [
                        {"text": "建议1: 添加字符集设置", "type": "general"},
                        {"text": "建议2: 添加事务控制", "type": "general"}
                    ]
                }
            ],
            "risk_summary": {
                "高风险问题数量": 1,
                "中风险问题数量": 2,
                "低风险问题数量": 0,
                "详细问题": {
                    "高风险问题": ["全表扫描风险"],
                    "中风险问题": ["索引设计问题", "字符集问题"]
                }
            },
            "performance_summary": {
                "全表扫描次数": 1,
                "索引缺失次数": 1,
                "性能问题总数": 2
            },
            "security_summary": {
                "sql注入风险": 0,
                "权限问题": 0,
                "安全风险总数": 0
            }
        }
    }
    
    return group_data, combined_result

def analyze_group_structure():
    """分析分组分析的数据结构"""
    
    print("=" * 80)
    print("分组分析数据结构分析")
    print("=" * 80)
    
    # 创建测试数据
    group_data, combined_result = create_sample_group_data()
    
    # 模拟 _prepare_storage_data 方法
    def simulate_prepare_storage_data(group_data, combined_result):
        """模拟 _prepare_storage_data 方法"""
        storage_data = {
            "file_info": {
                "file_name": group_data['file_name'],
                "project_id": group_data['project_id'],
                "default_version": group_data['default_version'],
                "file_path": group_data.get('file_path', ''),
                "sql_count": len(group_data['sqls'])
            },
            "analysis_summary": combined_result.get('summary', {}),
            "combined_analysis": combined_result.get('combined_analysis', {}),
            "sql_details": []
        }
        
        # 添加每个SQL的详细信息
        for sql_data in group_data['sqls']:
            sql_detail = {
                "sql_id": sql_data['sql_id'],
                "sql_preview": sql_data['sql_text'][:150] + "..." if len(sql_data['sql_text']) > 150 else sql_data['sql_text'],
                "analysis_data": sql_data['analysis_data']
            }
            storage_data["sql_details"].append(sql_detail)
        
        return storage_data
    
    # 生成存储数据
    storage_data = simulate_prepare_storage_data(group_data, combined_result)
    
    # 分析数据结构
    storage_json = json.dumps(storage_data, ensure_ascii=False)
    
    print(f"\n1. 当前分组分析数据结构:")
    print(f"   - 字段数: {len(storage_data)}")
    print(f"   - 总大小: {len(storage_json)} 字符")
    
    # 计算嵌套深度
    def get_max_depth(data, current_depth=1):
        if not isinstance(data, dict):
            return current_depth
        max_depth = current_depth
        for value in data.values():
            depth = get_max_depth(value, current_depth + 1)
            max_depth = max(max_depth, depth)
        return max_depth
    
    max_depth = get_max_depth(storage_data)
    print(f"   - 最大嵌套深度: {max_depth}")
    
    # 分析字段分布
    print(f"\n2. 字段分布分析:")
    
    def analyze_field_distribution(data, prefix=""):
        """递归分析字段分布"""
        results = []
        
        if isinstance(data, dict):
            for key, value in data.items():
                field_path = f"{prefix}.{key}" if prefix else key
                if isinstance(value, (dict, list)):
                    if isinstance(value, list):
                        results.append(f"  {field_path}: 列表，长度 {len(value)}")
                        if value and isinstance(value[0], (dict, list)):
                            results.extend(analyze_field_distribution(value[0], f"{field_path}[0]"))
                    else:
                        results.append(f"  {field_path}: 字典，{len(value)} 个字段")
                        results.extend(analyze_field_distribution(value, field_path))
                else:
                    results.append(f"  {field_path}: {type(value).__name__}")
        elif isinstance(data, list) and data and isinstance(data[0], dict):
            # 只分析列表的第一个元素作为示例
            results.extend(analyze_field_distribution(data[0], f"{prefix}[0]"))
        
        return results
    
    distribution = analyze_field_distribution(storage_data)
    for line in distribution[:20]:  # 显示前20行
        print(line)
    
    if len(distribution) > 20:
        print(f"  ... 还有 {len(distribution) - 20} 行未显示")
    
    print(f"\n3. 数据结构问题分析:")
    print(f"   a. 嵌套层级过深:")
    print(f"      - combined_analysis.risk_summary.详细问题 层级太深")
    print(f"      - sql_details[0].analysis_data.summary 层级深")
    print(f"   b. 字段冗余:")
    print(f"      - file_info 与 sql_details[0].sql_info 有重复信息")
    print(f"      - combined_analysis 与 sql_details 中的analysis_data有重复")
    print(f"   c. 存储空间过大:")
    print(f"      - 每个SQL的完整analysis_data都存储，导致重复存储")
    print(f"      - combined_analysis 可能包含冗余数据")
    print(f"   d. 查询效率低:")
    print(f"      - 需要解析多层嵌套才能获取基本信息")
    print(f"      - 关键信息分散在不同层级")
    
    print(f"\n4. 数据统计:")
    
    # 统计combined_analysis的大小
    combined_analysis_size = len(json.dumps(storage_data.get('combined_analysis', {}), ensure_ascii=False))
    print(f"   - combined_analysis 大小: {combined_analysis_size} 字符")
    
    # 统计sql_details的大小
    sql_details_size = len(json.dumps(storage_data.get('sql_details', []), ensure_ascii=False))
    print(f"   - sql_details 大小: {sql_details_size} 字符")
    
    # 统计file_info的大小
    file_info_size = len(json.dumps(storage_data.get('file_info', {}), ensure_ascii=False))
    print(f"   - file_info 大小: {file_info_size} 字符")
    
    # 统计analysis_summary的大小
    analysis_summary_size = len(json.dumps(storage_data.get('analysis_summary', {}), ensure_ascii=False))
    print(f"   - analysis_summary 大小: {analysis_summary_size} 字符")
    
    print(f"\n5. 优化建议:")
    print(f"   a. 扁平化数据结构:")
    print(f"      - 将combined_analysis的关键信息提取到顶层")
    print(f"      - 减少combined_analysis.risk_summary的嵌套层级")
    print(f"   b. 提取关键信息:")
    print(f"      - 将每个SQL的核心摘要信息单独存储")
    print(f"      - 去除analysis_data中的冗余字段")
    print(f"   c. 合并重复信息:")
    print(f"      - 合并file_info和sql_info中的重复字段")
    print(f"      - 提取公共信息到顶层")
    print(f"   d. 优化存储格式:")
    print(f"      - 分离摘要信息和详细数据")
    print(f"      - 使用引用关系而不是完全复制")
    
    # 设计优化的数据结构
    print(f"\n6. 优化后的数据结构设计:")
    
    optimized_structure = {
        "summary": {
            "file_name": group_data['file_name'],
            "project_id": group_data['project_id'],
            "default_version": group_data['default_version'],
            "sql_count": len(group_data['sqls']),
            "average_score": combined_result.get('summary', {}).get('average_score', 0),
            "critical_issue_count": combined_result.get('combined_analysis', {}).get('risk_summary', {}).get('高风险问题数量', 0)
        },
        "key_issues": [
            {
                "sql_id": 1001,
                "category": "全表扫描",
                "severity": "高风险",
                "description": "查询条件不充分可能导致全表扫描",
                "suggestion": "优化查询条件，添加索引"
            },
            {
                "sql_id": 1002,
                "category": "字符集问题",
                "severity": "中风险",
                "description": "未指定字符集可能导致乱码问题",
                "suggestion": "明确指定字符集如utf8mb4"
            }
        ],
        "combined_suggestions": [
            "添加索引提高查询性能",
            "避免全表扫描，添加WHERE条件",
            "检查字符集一致性",
            "添加字符集设置",
            "添加事务控制"
        ],
        "sql_summaries": [
            {
                "sql_id": 1001,
                "sql_type": "查询",
                "score": 7.5,
                "has_critical_issues": True,
                "suggestion_count": 3
            },
            {
                "sql_id": 1002,
                "sql_type": "更新",
                "score": 8.0,
                "has_critical_issues": False,
                "suggestion_count": 2
            }
        ],
        "normative_summary": {
            "total_angles": 15,
            "average_compliance_rate": 86.7,
            "failed_angles": ["全表扫描", "索引设计", "字符集问题"]
        }
    }
    
    optimized_json = json.dumps(optimized_structure, ensure_ascii=False)
    
    print(f"   优化后结构:")
    print(f"     - 字段数: {len(optimized_structure)}")
    print(f"     - 总大小: {len(optimized_json)} 字符")
    print(f"     - 减少空间: {len(storage_json) - len(optimized_json)} 字符")
    print(f"     - 减少比例: {(len(storage_json) - len(optimized_json)) / len(storage_json) * 100:.1f}%")
    
    # 计算优化后的嵌套深度
    optimized_depth = get_max_depth(optimized_structure)
    print(f"     - 最大嵌套深度: {optimized_depth} (减少 {max_depth - optimized_depth})")
    
    print(f"\n7. 优化措施:")
    print(f"   1. 修改 group_processor_fixed_v2.py 中的 _prepare_storage_data 方法")
    print(f"   2. 更新 combine_analysis_results 方法生成新格式数据")
    print(f"   3. 更新 store_to_commit_shell_info 方法适应新格式")
    print(f"   4. 确保向后兼容性")
    print(f"   5. 测试验证优化效果")
    
    return storage_data, optimized_structure

def main():
    """主函数"""
    try:
        print("开始分析分组分析的数据结构...")
        storage_data, optimized_structure = analyze_group_structure()
        
        # 保存分析结果
        with open("group_structure_current.json", "w", encoding="utf-8") as f:
            json.dump(storage_data, f, ensure_ascii=False, indent=2)
        
        with open("group_structure_optimized.json", "w", encoding="utf-8") as f:
            json.dump(optimized_structure, f, ensure_ascii=False, indent=2)
        
        print("\n分析结果已保存:")
        print("  - group_structure_current.json (当前结构)")
        print("  - group_structure_optimized.json (优化结构)")
        
        print("\n✓ 分析完成！")
        return True
        
    except Exception as e:
        print(f"分析过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    import sys
    sys.exit(0 if success else 1)
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化调试分组存储数据为空的问题
直接测试 _prepare_storage_data 方法逻辑
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

def _truncate_sql(sql_text: str, max_length: int = 100) -> str:
    """截断SQL文本"""
    if not sql_text:
        return ""
    
    if len(sql_text) <= max_length:
        return sql_text
    
    return sql_text[:max_length] + "..."

def test_prepare_storage_data_logic():
    """直接测试 _prepare_storage_data 方法的逻辑"""
    
    print("=" * 80)
    print("直接调试分组存储数据为空问题")
    print("=" * 80)
    
    try:
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
        
        print("2. 模拟 _prepare_storage_data 方法逻辑...")
        
        # 提取关键信息
        file_name = group_data['file_name']
        project_id = group_data['project_id']
        default_version = group_data['default_version']
        file_path = group_data.get('file_path', '')
        sql_count = len(group_data['sqls'])
        
        # 从combined_result中提取摘要信息
        analysis_summary = combined_result.get('summary', {})
        combined_analysis = combined_result.get('combined_analysis', {})
        
        print(f"   - analysis_summary: {analysis_summary}")
        print(f"   - combined_analysis 类型: {type(combined_analysis)}")
        print(f"   - combined_analysis 键: {list(combined_analysis.keys())}")
        
        # 构建优化后的存储数据
        storage_data: Dict[str, Any] = {
            "summary": {
                "file_name": file_name,
                "project_id": project_id,
                "default_version": default_version,
                "sql_count": sql_count,
                "file_path": file_path,
                "average_score": analysis_summary.get('average_score', 0),
                "total_sqls": analysis_summary.get('total_sqls', sql_count),
                "unique_files": analysis_summary.get('unique_files', 1),
                "unique_projects": analysis_summary.get('unique_projects', 1),
                "success_rate": analysis_summary.get('success_rate', 100.0 if sql_count > 0 else 0),
                "analysis_time": analysis_summary.get('analysis_time', 'NOW()')
            },
            "key_issues": [],  # 将初始化为列表
            "combined_suggestions": [],  # 将初始化为列表
            "sql_summaries": [],  # 将初始化为列表
            "normative_summary": {},  # 将初始化为字典
            "risk_stats": {}  # 将初始化为字典
        }
        
        print("\n3. 提取关键问题...")
        
        # 提取关键问题
        key_issues = []
        
        # 从combined_analysis的risk_summary中提取关键问题
        risk_summary = combined_analysis.get('risk_summary', {})
        print(f"   - risk_summary: {risk_summary}")
        print(f"   - risk_summary 类型: {type(risk_summary)}")
        
        detail_problems = risk_summary.get('详细问题', {})
        print(f"   - detail_problems: {detail_problems}")
        print(f"   - detail_problems 类型: {type(detail_problems)}")
        
        # 提取高风险问题
        high_risk_problems = detail_problems.get('高风险问题', [])
        print(f"   - high_risk_problems: {high_risk_problems}")
        print(f"   - high_risk_problems 类型: {type(high_risk_problems)}")
        
        for problem in high_risk_problems[:3]:  # 最多取3个
            print(f"   - 处理高风险问题: {problem}, 类型: {type(problem)}")
            if isinstance(problem, str):
                key_issues.append({
                    "category": "高风险问题",
                    "description": problem,
                    "severity": "高风险"
                })
        
        # 提取中风险问题
        medium_risk_problems = detail_problems.get('中风险问题', [])
        print(f"   - medium_risk_problems: {medium_risk_problems}")
        
        for problem in medium_risk_problems[:3]:  # 最多取3个
            if isinstance(problem, str):
                key_issues.append({
                    "category": "中风险问题",
                    "description": problem,
                    "severity": "中风险"
                })
        
        # 提取低风险问题
        low_risk_problems = detail_problems.get('低风险问题', [])
        print(f"   - low_risk_problems: {low_risk_problems}")
        
        for problem in low_risk_problems[:2]:  # 最多取2个
            if isinstance(problem, str):
                key_issues.append({
                    "category": "低风险问题",
                    "description": problem,
                    "severity": "低风险"
                })
        
        print(f"   - 从risk_summary提取的关键问题数量: {len(key_issues)}")
        
        # 如果从risk_summary中没有提取到问题，从每个SQL的分析结果中提取
        if not key_issues:
            print("   - 从risk_summary中没有提取到问题，尝试从SQL分析结果中提取")
            for sql_data in group_data['sqls'][:3]:  # 最多检查前3个SQL
                analysis_data = sql_data.get('analysis_data', {})
                print(f"   - SQL analysis_data 键: {list(analysis_data.keys())}")
                key_issues_from_sql = analysis_data.get('key_issues', [])
                print(f"   - key_issues_from_sql: {key_issues_from_sql}")
                if isinstance(key_issues_from_sql, list):
                    for issue in key_issues_from_sql[:2]:  # 每个SQL最多取2个
                        if isinstance(issue, dict):
                            key_issues.append({
                                "sql_id": sql_data.get('sql_id'),
                                "category": issue.get('category', '未知'),
                                "description": issue.get('description', ''),
                                "severity": issue.get('severity', '中风险'),
                                "suggestion": issue.get('suggestion', '')
                            })
        
        storage_data["key_issues"] = key_issues[:5]  # 最多5个关键问题
        print(f"   - 最终 key_issues: {storage_data['key_issues']}")
        
        print("\n4. 提取合并建议...")
        
        # 提取合并建议
        combined_suggestions = []
        all_suggestions = combined_analysis.get('all_suggestions', [])
        print(f"   - all_suggestions: {all_suggestions}")
        print(f"   - all_suggestions 类型: {type(all_suggestions)}")
        
        # 从all_suggestions中提取建议
        if isinstance(all_suggestions, list):
            print(f"   - all_suggestions 是列表，长度: {len(all_suggestions)}")
            for suggestion_item in all_suggestions[:5]:  # 最多取5个建议项
                print(f"   - 处理 suggestion_item: {suggestion_item}")
                if isinstance(suggestion_item, dict):
                    suggestions = suggestion_item.get('suggestions', [])
                    print(f"   - suggestions: {suggestions}")
                    if isinstance(suggestions, list):
                        for suggestion in suggestions[:3]:  # 每个项最多取3个建议
                            if isinstance(suggestion, dict):
                                text = suggestion.get('text', '')
                                print(f"   - 建议文本: {text}")
                                if text and isinstance(text, str):
                                    # 精简建议文本
                                    clean_text = text.strip()
                                    if len(clean_text) > 100:
                                        clean_text = clean_text[:97] + '...'
                                    combined_suggestions.append(clean_text)
        else:
            print(f"   - all_suggestions 不是列表")
        
        print(f"   - 从all_suggestions提取的建议数量: {len(combined_suggestions)}")
        
        # 如果从all_suggestions中没有提取到建议，从每个SQL中提取
        if not combined_suggestions:
            print("   - 从all_suggestions中没有提取到建议，尝试从SQL中提取")
            for sql_data in group_data['sqls'][:3]:  # 最多检查前3个SQL
                analysis_data = sql_data.get('analysis_data', {})
                suggestions = analysis_data.get('suggestions', [])
                print(f"   - SQL suggestions: {suggestions}")
                if isinstance(suggestions, list):
                    for suggestion in suggestions[:2]:  # 每个SQL最多取2个建议
                        if isinstance(suggestion, str):
                            # 精简建议文本
                            clean_suggestion = suggestion.strip()
                            if len(clean_suggestion) > 80:
                                clean_suggestion = clean_suggestion[:77] + '...'
                            if clean_suggestion not in combined_suggestions:
                                combined_suggestions.append(clean_suggestion)
        
        storage_data["combined_suggestions"] = combined_suggestions[:10]  # 最多10条合并建议
        print(f"   - 最终 combined_suggestions: {storage_data['combined_suggestions']}")
        
        print("\n5. 创建SQL摘要...")
        
        # 创建SQL摘要
        sql_summaries = []
        for sql_data in group_data['sqls']:
            sql_id = sql_data.get('sql_id')
            sql_text = sql_data.get('sql_text', '')
            analysis_data = sql_data.get('analysis_data', {})
            
            # 提取摘要信息
            summary = analysis_data.get('summary', {})
            if isinstance(summary, dict):
                sql_summary = {
                    "sql_id": sql_id,
                    "sql_preview": _truncate_sql(sql_text, 80),
                    "sql_type": summary.get('sql_type', '未知'),
                    "score": summary.get('score', 0),
                    "has_critical_issues": summary.get('has_critical_issues', False),
                    "suggestion_count": summary.get('suggestion_count', 0),
                    "compliance_score": summary.get('compliance_score', 0)
                }
            else:
                # 兼容旧格式
                sql_summary = {
                    "sql_id": sql_id,
                    "sql_preview": _truncate_sql(sql_text, 80),
                    "sql_type": analysis_data.get('SQL类型', '未知'),
                    "score": analysis_data.get('综合评分', 0),
                    "has_critical_issues": False,  # 默认值
                    "suggestion_count": len(analysis_data.get('建议', [])),
                    "compliance_score": analysis_data.get('规范符合性', {}).get('规范符合度', 0)
                }
            
            sql_summaries.append(sql_summary)
        
        storage_data["sql_summaries"] = sql_summaries
        print(f"   - SQL摘要数量: {len(sql_summaries)}")
        
        print("\n6. 添加规范性摘要...")
        
        # 添加规范性摘要
        normative_summary = {
            "total_angles": 15,
            "average_compliance_rate": 100.0,
            "failed_angles": []
        }
        
        # 从所有SQL中收集规范性失败的角度
        failed_angles_set = set()
        for sql_data in group_data['sqls']:
            analysis_data = sql_data.get('analysis_data', {})
            normative_summary_from_sql = analysis_data.get('normative_summary', {})
            if isinstance(normative_summary_from_sql, dict):
                failed_angles = normative_summary_from_sql.get('failed', [])
                if isinstance(failed_angles, list):
                    for angle in failed_angles:
                        if isinstance(angle, str):
                            failed_angles_set.add(angle)
        
        # 计算平均符合率
        total_compliance = 0
        count = 0
        for sql_data in group_data['sqls']:
            analysis_data = sql_data.get('analysis_data', {})
            summary = analysis_data.get('summary', {})
            if isinstance(summary, dict):
                compliance_score = summary.get('compliance_score', 100.0)
            else:
                compliance_score = analysis_data.get('规范符合性', {}).get('规范符合度', 100.0)
            
            if isinstance(compliance_score, (int, float)):
                total_compliance += compliance_score
                count += 1
        
        if count > 0:
            normative_summary["average_compliance_rate"] = total_compliance / count
        
        normative_summary["failed_angles"] = list(failed_angles_set)[:10]  # 最多10个失败角度
        
        storage_data["normative_summary"] = normative_summary
        print(f"   - 规范性摘要: {normative_summary}")
        
        print("\n7. 添加风险统计...")
        
        # 添加风险统计
        risk_stats = {
            "high_risk_count": risk_summary.get('高风险问题数量', 0),
            "medium_risk_count": risk_summary.get('中风险问题数量', 0),
            "low_risk_count": risk_summary.get('低风险问题数量', 0),
            "total_risk_count": risk_summary.get('高风险问题数量', 0) + 
                              risk_summary.get('中风险问题数量', 0) + 
                              risk_summary.get('低风险问题数量', 0)
        }
        
        # 如果risk_summary中没有统计数据，从key_issues中计算
        if risk_stats["total_risk_count"] == 0:
            high_count = sum(1 for issue in key_issues if issue.get('severity') == '高风险')
            medium_count = sum(1 for issue in key_issues if issue.get('severity') == '中风险')
            low_count = sum(1 for issue in key_issues if issue.get('severity') == '低风险')
            
            risk_stats["high_risk_count"] = high_count
            risk_stats["medium_risk_count"] = medium_count
            risk_stats["low_risk_count"] = low_count
            risk_stats["total_risk_count"] = high_count + medium_count + low_count
        
        storage_data["risk_stats"] = risk_stats
        print(f"   - 风险统计: {risk_stats}")
        
        print("\n8. 检查存储数据...")
        
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
        
        # 检查字段内容是否为空
        empty_fields = []
        
        if isinstance(storage_data.get('key_issues'), list) and len(storage_data['key_issues']) == 0:
            empty_fields.append('key_issues')
        
        if isinstance(storage_data.get('combined_suggestions'), list) and len(storage_data['combined_suggestions']) == 0:
            empty_fields.append('combined_suggestions')
        
        if isinstance(storage_data.get('sql_summaries'), list) and len(storage_data['sql_summaries']) == 0:
            empty_fields.append('sql_summaries')
        
        if empty_fields:
            print(f"❌ 以下字段为空: {empty_fields}")
            return False
        else:
            print("✅ 所有字段都有内容")
        
        print("\n9. 完整存储数据结构:")
        print(json.dumps(storage_data, ensure_ascii=False, indent=2))
        
        # 保存测试结果
        with open("debug_storage_simple_result.json", "w", encoding="utf-8") as f:
            json.dump(storage_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ 测试完成，数据已保存到: debug_storage_simple_result.json")
        return True
        
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("开始直接调试分组存储数据为空问题...")
    
    success = test_prepare_storage_data_logic()
    
    if success:
        print("\n✓ 调试完成！")
        return 0
    else:
        print("\n✗ 调试失败！")
        return 1

if __name__ == "__main__":
    sys.exit(main())
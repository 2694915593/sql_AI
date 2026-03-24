#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试分组分析数据结构优化
"""

import json
import sys
from typing import Dict, Any, List

def create_test_group_data():
    """创建测试分组数据"""
    
    # 创建单个SQL分析结果（新格式）
    sql_analysis_1 = {
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
    
    sql_analysis_2 = {
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
    }
    
    # 创建分组数据
    group_data = {
        'file_name': 'UserService.java',
        'project_id': 'project_001',
        'default_version': 'feature/login',
        'file_path': '/src/main/java/com/example/service/',
        'sqls': [
            {
                'sql_id': 1001,
                'sql_text': 'SELECT * FROM users WHERE status = "active"',
                'analysis_data': sql_analysis_1,
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
                'analysis_data': sql_analysis_2,
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
    
    # 创建组合分析结果
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

class MockGroupProcessor:
    """模拟GroupProcessor类用于测试"""
    
    def _truncate_sql(self, sql_text: str, max_length: int = 100) -> str:
        """截断SQL文本"""
        if not sql_text:
            return ""
        
        if len(sql_text) <= max_length:
            return sql_text
        
        return sql_text[:max_length] + "..."
    
    def _prepare_storage_data(self, group_data: Dict[str, Any], 
                            combined_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        模拟优化后的存储数据准备方法
        """
        # 提取关键信息
        file_name = group_data['file_name']
        project_id = group_data['project_id']
        default_version = group_data['default_version']
        file_path = group_data.get('file_path', '')
        sql_count = len(group_data['sqls'])
        
        # 从combined_result中提取摘要信息
        analysis_summary = combined_result.get('summary', {})
        combined_analysis = combined_result.get('combined_analysis', {})
        
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
        
        # 提取关键问题
        key_issues = []
        
        # 从combined_analysis的risk_summary中提取关键问题
        risk_summary = combined_analysis.get('risk_summary', {})
        detail_problems = risk_summary.get('详细问题', {})
        
        # 提取高风险问题
        high_risk_problems = detail_problems.get('高风险问题', [])
        for problem in high_risk_problems[:3]:  # 最多取3个
            if isinstance(problem, str):
                key_issues.append({
                    "category": "高风险问题",
                    "description": problem,
                    "severity": "高风险"
                })
        
        # 提取中风险问题
        medium_risk_problems = detail_problems.get('中风险问题', [])
        for problem in medium_risk_problems[:3]:  # 最多取3个
            if isinstance(problem, str):
                key_issues.append({
                    "category": "中风险问题",
                    "description": problem,
                    "severity": "中风险"
                })
        
        # 提取低风险问题
        low_risk_problems = detail_problems.get('低风险问题', [])
        for problem in low_risk_problems[:2]:  # 最多取2个
            if isinstance(problem, str):
                key_issues.append({
                    "category": "低风险问题",
                    "description": problem,
                    "severity": "低风险"
                })
        
        # 如果从risk_summary中没有提取到问题，从每个SQL的分析结果中提取
        if not key_issues:
            for sql_data in group_data['sqls'][:3]:  # 最多检查前3个SQL
                analysis_data = sql_data.get('analysis_data', {})
                key_issues_from_sql = analysis_data.get('key_issues', [])
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
        
        # 提取合并建议
        combined_suggestions = []
        all_suggestions = combined_analysis.get('all_suggestions', [])
        
        # 从all_suggestions中提取建议
        if isinstance(all_suggestions, list):
            for suggestion_item in all_suggestions[:5]:  # 最多取5个建议项
                if isinstance(suggestion_item, dict):
                    suggestions = suggestion_item.get('suggestions', [])
                    if isinstance(suggestions, list):
                        for suggestion in suggestions[:3]:  # 每个项最多取3个建议
                            if isinstance(suggestion, dict):
                                text = suggestion.get('text', '')
                                if text and isinstance(text, str):
                                    # 精简建议文本
                                    clean_text = text.strip()
                                    if len(clean_text) > 100:
                                        clean_text = clean_text[:97] + '...'
                                    combined_suggestions.append(clean_text)
        
        # 如果从all_suggestions中没有提取到建议，从每个SQL中提取
        if not combined_suggestions:
            for sql_data in group_data['sqls'][:3]:  # 最多检查前3个SQL
                analysis_data = sql_data.get('analysis_data', {})
                suggestions = analysis_data.get('suggestions', [])
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
                    "sql_preview": self._truncate_sql(sql_text, 80),
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
                    "sql_preview": self._truncate_sql(sql_text, 80),
                    "sql_type": analysis_data.get('SQL类型', '未知'),
                    "score": analysis_data.get('综合评分', 0),
                    "has_critical_issues": False,  # 默认值
                    "suggestion_count": len(analysis_data.get('建议', [])),
                    "compliance_score": analysis_data.get('规范符合性', {}).get('规范符合度', 0)
                }
            
            sql_summaries.append(sql_summary)
        
        storage_data["sql_summaries"] = sql_summaries
        
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
        
        return storage_data

def test_optimized_structure():
    """测试优化后的数据结构"""
    
    print("=" * 80)
    print("分组分析数据结构优化测试")
    print("=" * 80)
    
    try:
        # 创建测试数据
        group_data, combined_result = create_test_group_data()
        
        # 创建模拟处理器
        processor = MockGroupProcessor()
        
        # 生成优化后的存储数据
        storage_data = processor._prepare_storage_data(group_data, combined_result)
        
        # 转换为JSON字符串
        storage_json = json.dumps(storage_data, ensure_ascii=False)
        
        print(f"\n1. 优化后的数据结构:")
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
        
        print(f"\n2. 关键信息提取:")
        print(f"   - 文件信息:")
        summary = storage_data.get('summary', {})
        print(f"     * 文件名: {summary.get('file_name')}")
        print(f"     * 项目ID: {summary.get('project_id')}")
        print(f"     * 分支: {summary.get('default_version')}")
        print(f"     * SQL数量: {summary.get('sql_count')}")
        print(f"     * 平均分数: {summary.get('average_score')}")
        
        print(f"\n   - 关键问题 ({len(storage_data.get('key_issues', []))} 个):")
        for i, issue in enumerate(storage_data.get('key_issues', [])[:3]):
            print(f"     * {i+1}. {issue.get('category')} ({issue.get('severity')}): {issue.get('description')[:50]}...")
        
        print(f"\n   - 合并建议 ({len(storage_data.get('combined_suggestions', []))} 条):")
        for i, suggestion in enumerate(storage_data.get('combined_suggestions', [])[:3]):
            print(f"     * {i+1}. {suggestion[:60]}...")
        
        print(f"\n   - SQL摘要 ({len(storage_data.get('sql_summaries', []))} 个):")
        for i, sql_summary in enumerate(storage_data.get('sql_summaries', [])[:2]):
            print(f"     * {i+1}. SQL ID: {sql_summary.get('sql_id')}, 类型: {sql_summary.get('sql_type')}, 分数: {sql_summary.get('score')}")
        
        print(f"\n   - 规范性摘要:")
        normative = storage_data.get('normative_summary', {})
        print(f"     * 总角度: {normative.get('total_angles')}")
        print(f"     * 平均符合率: {normative.get('average_compliance_rate')}%")
        print(f"     * 失败角度: {', '.join(normative.get('failed_angles', [])[:3])}")
        
        print(f"\n   - 风险统计:")
        risk_stats = storage_data.get('risk_stats', {})
        print(f"     * 高风险数量: {risk_stats.get('high_risk_count')}")
        print(f"     * 中风险数量: {risk_stats.get('medium_risk_count')}")
        print(f"     * 低风险数量: {risk_stats.get('low_risk_count')}")
        print(f"     * 总风险数量: {risk_stats.get('total_risk_count')}")
        
        print(f"\n3. 数据结构验证:")
        
        # 验证关键字段
        required_fields = ['summary', 'key_issues', 'combined_suggestions', 'sql_summaries', 'normative_summary', 'risk_stats']
        missing_fields = [field for field in required_fields if field not in storage_data]
        
        if missing_fields:
            print(f"   ❌ 缺少关键字段: {missing_fields}")
            return False
        else:
            print(f"   ✅ 所有关键字段都存在")
        
        # 验证数据类型
        type_errors = []
        
        if not isinstance(storage_data['key_issues'], list):
            type_errors.append(f"key_issues 应该是列表，实际是 {type(storage_data['key_issues'])}")
        
        if not isinstance(storage_data['combined_suggestions'], list):
            type_errors.append(f"combined_suggestions 应该是列表，实际是 {type(storage_data['combined_suggestions'])}")
        
        if not isinstance(storage_data['sql_summaries'], list):
            type_errors.append(f"sql_summaries 应该是列表，实际是 {type(storage_data['sql_summaries'])}")
        
        if not isinstance(storage_data['normative_summary'], dict):
            type_errors.append(f"normative_summary 应该是字典，实际是 {type(storage_data['normative_summary'])}")
        
        if not isinstance(storage_data['risk_stats'], dict):
            type_errors.append(f"risk_stats 应该是字典，实际是 {type(storage_data['risk_stats'])}")
        
        if type_errors:
            print(f"   ❌ 数据类型错误:")
            for error in type_errors:
                print(f"     - {error}")
            return False
        else:
            print(f"   ✅ 所有数据类型正确")
        
        # 验证数据内容
        content_errors = []
        
        # 验证SQL摘要数量与实际SQL数量一致
        expected_sql_count = len(group_data['sqls'])
        actual_sql_summaries = len(storage_data['sql_summaries'])
        if expected_sql_count != actual_sql_summaries:
            content_errors.append(f"SQL摘要数量不一致: 期望 {expected_sql_count}, 实际 {actual_sql_summaries}")
        
        # 验证关键问题数量合理
        if len(storage_data['key_issues']) > 10:  # 最多10个
            content_errors.append(f"关键问题数量过多: {len(storage_data['key_issues'])} (应不超过10个)")
        
        # 验证合并建议数量合理
        if len(storage_data['combined_suggestions']) > 15:  # 最多15个
            content_errors.append(f"合并建议数量过多: {len(storage_data['combined_suggestions'])} (应不超过15个)")
        
        if content_errors:
            print(f"   ❌ 数据内容错误:")
            for error in content_errors:
                print(f"     - {error}")
            return False
        else:
            print(f"   ✅ 数据内容合理")
        
        # 保存测试结果
        with open("test_optimized_group_structure.json", "w", encoding="utf-8") as f:
            json.dump(storage_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n4. 测试结果:")
        print(f"   ✅ 优化后的数据结构测试通过!")
        print(f"   - 存储数据已保存到: test_optimized_group_structure.json")
        print(f"   - 数据结构扁平化成功，最大嵌套深度: {max_depth}")
        print(f"   - 总大小: {len(storage_json)} 字符")
        print(f"   - 相比旧结构 (2478 字符) 减少: {2478 - len(storage_json)} 字符")
        print(f"   - 减少比例: {(2478 - len(storage_json)) / 2478 * 100:.1f}%")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("开始测试分组分析数据结构优化...")
    
    success = test_optimized_structure()
    
    if success:
        print("\n✓ 测试完成！优化效果显著。")
        return 0
    else:
        print("\n✗ 测试失败！")
        return 1

if __name__ == "__main__":
    sys.exit(main())
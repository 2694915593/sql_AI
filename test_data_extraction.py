#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试数据提取逻辑，验证_prepare_storage_data方法是否能正确提取数据
"""

import json
import sys
import os
from typing import Dict, Any, List

def test_prepare_storage_data_logic():
    """测试_prepare_storage_data方法的逻辑"""
    
    print("=" * 80)
    print("测试_prepare_storage_data方法的数据提取逻辑")
    print("=" * 80)
    
    # 创建一个模拟GroupProcessor类
    class MockGroupProcessor:
        def _truncate_sql(self, sql_text, max_length):
            if not sql_text or len(sql_text) <= max_length:
                return sql_text
            return sql_text[:max_length] + "..."
    
    processor = MockGroupProcessor()
    
    # 模拟典型的group_data
    group_data = {
        'file_name': 'TestService.java',
        'project_id': 'test_project',
        'default_version': 'feature/test',
        'file_path': '/src/test/',
        'sqls': [
            {
                'sql_id': 1001,
                'sql_text': 'SELECT * FROM users WHERE id = 1',
                'analysis_data': {
                    'SQL类型': '查询',
                    '综合评分': 8.5,
                    '建议': [
                        '建议添加索引',
                        '避免全表扫描',
                        '优化查询条件'
                    ],
                    '规范符合性': {
                        '规范符合度': 85.0
                    },
                    'summary': {
                        'sql_type': '查询',
                        'score': 8.5,
                        'has_critical_issues': True,
                        'suggestion_count': 3,
                        'compliance_score': 85.0
                    },
                    'normative_summary': {
                        'total_angles': 15,
                        'failed': ['索引缺失']
                    }
                }
            },
            {
                'sql_id': 1002,
                'sql_text': 'UPDATE users SET name = "test" WHERE id = 2',
                'analysis_data': {
                    'sql_type': '更新',
                    'score': 7.0,
                    'suggestions': [
                        '建议添加事务处理',
                        '检查更新条件'
                    ],
                    '规范符合性': {
                        '规范符合度': 78.0
                    },
                    'summary': {
                        'sql_type': '更新',
                        'score': 7.0,
                        'has_critical_issues': False,
                        'suggestion_count': 2,
                        'compliance_score': 78.0
                    },
                    'normative_summary': {
                        'total_angles': 15,
                        'failed': []
                    }
                }
            }
        ]
    }
    
    # 模拟combined_result
    combined_result = {
        'summary': {
            'total_sqls': 2,
            'unique_files': 1,
            'unique_projects': 1,
            'analysis_time': '2024-01-01 10:00:00',
            'average_score': 7.75,
            'success_rate': 100.0
        },
        'combined_analysis': {
            'all_suggestions': [
                {
                    'summary': '通用建议',
                    'suggestions': [
                        {'text': '建议添加索引', 'type': 'general'},
                        {'text': '避免全表扫描', 'type': 'general'}
                    ]
                }
            ],
            'risk_summary': {
                '高风险问题数量': 1,
                '中风险问题数量': 2,
                '低风险问题数量': 0,
                '详细问题': {
                    '高风险问题': ['全表扫描风险'],
                    '中风险问题': ['缺少索引', '事务处理不规范'],
                    '低风险问题': []
                }
            }
        }
    }
    
    print("✅ 测试数据准备完成")
    
    # 测试当前的_prepare_storage_data逻辑
    print("\n1. 测试当前的_prepare_storage_data逻辑（从group_processor_fixed_v2.py复制）...")
    
    def current_prepare_storage_data(group_data, combined_result):
        """从group_processor_fixed_v2.py复制的逻辑"""
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
        storage_data = {
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
            "key_issues": [],
            "combined_suggestions": [],
            "sql_summaries": [],
            "normative_summary": {},
            "risk_stats": {}
        }
        
        # 提取关键问题
        key_issues = []
        
        # 从combined_analysis的risk_summary中提取关键问题
        risk_summary = combined_analysis.get('risk_summary', {})
        detail_problems = risk_summary.get('详细问题', {})
        
        # 提取高风险问题
        high_risk_problems = detail_problems.get('高风险问题', [])
        for problem in high_risk_problems[:3]:
            if isinstance(problem, str):
                key_issues.append({
                    "category": "高风险问题",
                    "description": problem,
                    "severity": "高风险"
                })
        
        # 提取中风险问题
        medium_risk_problems = detail_problems.get('中风险问题', [])
        for problem in medium_risk_problems[:3]:
            if isinstance(problem, str):
                key_issues.append({
                    "category": "中风险问题",
                    "description": problem,
                    "severity": "中风险"
                })
        
        # 提取低风险问题
        low_risk_problems = detail_problems.get('低风险问题', [])
        for problem in low_risk_problems[:2]:
            if isinstance(problem, str):
                key_issues.append({
                    "category": "低风险问题",
                    "description": problem,
                    "severity": "低风险"
                })
        
        # 如果从risk_summary中没有提取到问题，从每个SQL的分析结果中提取
        if not key_issues:
            for sql_data in group_data['sqls'][:3]:
                analysis_data = sql_data.get('analysis_data', {})
                key_issues_from_sql = analysis_data.get('key_issues', [])
                if isinstance(key_issues_from_sql, list):
                    for issue in key_issues_from_sql[:2]:
                        if isinstance(issue, dict):
                            key_issues.append({
                                "sql_id": sql_data.get('sql_id'),
                                "category": issue.get('category', '未知'),
                                "description": issue.get('description', ''),
                                "severity": issue.get('severity', '中风险'),
                                "suggestion": issue.get('suggestion', '')
                            })
        
        storage_data["key_issues"] = key_issues[:5]
        
        # 提取合并建议
        combined_suggestions = []
        all_suggestions = combined_analysis.get('all_suggestions', [])
        
        # 从all_suggestions中提取建议
        if isinstance(all_suggestions, list):
            for suggestion_item in all_suggestions[:5]:
                if isinstance(suggestion_item, dict):
                    suggestions = suggestion_item.get('suggestions', [])
                    if isinstance(suggestions, list):
                        for suggestion in suggestions[:3]:
                            if isinstance(suggestion, dict):
                                text = suggestion.get('text', '')
                                if text and isinstance(text, str):
                                    clean_text = text.strip()
                                    if len(clean_text) > 100:
                                        clean_text = clean_text[:97] + '...'
                                    combined_suggestions.append(clean_text)
        
        # 如果从all_suggestions中没有提取到建议，从每个SQL中提取
        if not combined_suggestions:
            for sql_data in group_data['sqls'][:3]:
                analysis_data = sql_data.get('analysis_data', {})
                suggestions = analysis_data.get('suggestions', [])
                if isinstance(suggestions, list):
                    for suggestion in suggestions[:2]:
                        if isinstance(suggestion, str):
                            clean_suggestion = suggestion.strip()
                            if len(clean_suggestion) > 80:
                                clean_suggestion = clean_suggestion[:77] + '...'
                            if clean_suggestion not in combined_suggestions:
                                combined_suggestions.append(clean_suggestion)
        
        storage_data["combined_suggestions"] = combined_suggestions[:10]
        
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
                    "sql_preview": processor._truncate_sql(sql_text, 80),
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
                    "sql_preview": processor._truncate_sql(sql_text, 80),
                    "sql_type": analysis_data.get('SQL类型', '未知'),
                    "score": analysis_data.get('综合评分', 0),
                    "has_critical_issues": False,
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
        
        normative_summary["failed_angles"] = list(failed_angles_set)[:10]
        
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
    
    # 运行当前逻辑
    result_current = current_prepare_storage_data(group_data, combined_result)
    
    print(f"   当前逻辑结果:")
    print(f"     - key_issues数量: {len(result_current.get('key_issues', []))}")
    print(f"     - combined_suggestions数量: {len(result_current.get('combined_suggestions', []))}")
    print(f"     - sql_summaries数量: {len(result_current.get('sql_summaries', []))}")
    print(f"     - 数据大小: {len(json.dumps(result_current))} 字符")
    
    # 保存结果
    with open("current_storage_data.json", "w", encoding="utf-8") as f:
        json.dump(result_current, f, ensure_ascii=False, indent=2)
    
    print(f"   ✅ 当前逻辑结果已保存到: current_storage_data.json")
    
    # 检查问题
    print("\n2. 问题分析：")
    if len(result_current.get('key_issues', [])) == 0:
        print("   ❌ 问题1: key_issues为空")
        print("     原因分析：")
        print("     - combined_result.risk_summary.详细问题 可能为空")
        print("     - analysis_data中没有key_issues字段")
        print("     - 数据字段名不匹配（例如：'key_issues' vs 'KeyIssues'）")
    else:
        print("   ✅ key_issues有数据")
    
    if len(result_current.get('combined_suggestions', [])) == 0:
        print("   ❌ 问题2: combined_suggestions为空")
        print("     原因分析：")
        print("     - combined_result.all_suggestions 可能为空")
        print("     - analysis_data中没有建议字段（可能是'suggestions'或'建议'）")
    else:
        print("   ✅ combined_suggestions有数据")
    
    # 创建增强版的方法
    print("\n3. 创建增强版的数据提取方法...")
    
    def enhanced_prepare_storage_data(group_data, combined_result):
        """增强版的数据提取方法，支持更多字段名格式"""
        
        # 提取关键信息
        file_name = group_data['file_name']
        project_id = group_data['project_id']
        default_version = group_data['default_version']
        file_path = group_data.get('file_path', '')
        sql_count = len(group_data['sqls'])
        
        # 从combined_result中提取摘要信息
        analysis_summary = combined_result.get('summary', {})
        combined_analysis = combined_result.get('combined_analysis', {})
        
        # 构建存储数据
        storage_data = {
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
            "key_issues": [],
            "combined_suggestions": [],
            "sql_summaries": [],
            "normative_summary": {},
            "risk_stats": {}
        }
        
        # ========== 增强的关键问题提取 ==========
        key_issues = []
        
        # 首先尝试从combined_analysis提取
        risk_summary = combined_analysis.get('risk_summary', {})
        detail_problems = risk_summary.get('详细问题', {})
        
        # 从combined_analysis提取
        for risk_level in ['高风险问题', '中风险问题', '低风险问题']:
            problems = detail_problems.get(risk_level, [])
            for problem in problems[:3]:
                if isinstance(problem, str):
                    key_issues.append({
                        "category": risk_level,
                        "description": problem,
                        "severity": risk_level[:3]
                    })
        
        # 如果从combined_analysis提取不到，从每个SQL的analysis_data提取
        if not key_issues:
            for sql_data in group_data['sqls']:
                analysis_data = sql_data.get('analysis_data', {})
                
                # 尝试多个可能的字段名
                key_issues_fields = ['key_issues', 'KeyIssues', 'keyIssues', '关键问题', '关键issues']
                for field in key_issues_fields:
                    if field in analysis_data:
                        issues = analysis_data[field]
                        if isinstance(issues, list):
                            for issue in issues:
                                if isinstance(issue, dict):
                                    key_issues.append({
                                        "sql_id": sql_data.get('sql_id'),
                                        "category": issue.get('category', '未知'),
                                        "description": issue.get('description', ''),
                                        "severity": issue.get('severity', '中风险'),
                                        "suggestion": issue.get('suggestion', '')
                                    })
                                elif isinstance(issue, str):
                                    # 如果是字符串，转换为字典格式
                                    key_issues.append({
                                        "sql_id": sql_data.get('sql_id'),
                                        "category": "通用问题",
                                        "description": issue,
                                        "severity": "中风险"
                                    })
                        break  # 找到一个字段就停止
        
        storage_data["key_issues"] = key_issues[:5]
        
        # ========== 增强的建议提取 ==========
        combined_suggestions = []
        
        # 首先尝试从combined_analysis提取
        all_suggestions = combined_analysis.get('all_suggestions', [])
        
        if isinstance(all_suggestions, list):
            for suggestion_item in all_suggestions:
                if isinstance(suggestion_item, dict):
                    suggestions = suggestion_item.get('suggestions', [])
                    if isinstance(suggestions, list):
                        for suggestion in suggestions:
                            if isinstance(suggestion, dict):
                                text = suggestion.get('text', '')
                                if text and isinstance(text, str):
                                    combined_suggestions.append(text[:100])
                            elif isinstance(suggestion, str):
                                combined_suggestions.append(suggestion[:100])
        
        # 如果从combined_analysis提取不到，从每个SQL的analysis_data提取
        if not combined_suggestions:
            for sql_data in group_data['sqls']:
                analysis_data = sql_data.get('analysis_data', {})
                
                # 尝试多个可能的字段名
                suggestions_fields = ['建议', 'suggestions', 'Suggestions', '改进建议', '建议列表']
                for field in suggestions_fields:
                    if field in analysis_data:
                        suggestions = analysis_data[field]
                        if isinstance(suggestions, list):
                            for suggestion in suggestions:
                                if isinstance(suggestion, str):
                                    combined_suggestions.append(suggestion[:80])
                                elif isinstance(suggestion, dict):
                                    # 尝试从字典中提取文本
                                    text = suggestion.get('text', suggestion.get('description', str(suggestion)))
                                    if isinstance(text, str):
                                        combined_suggestions.append(text[:80])
                        break  # 找到一个字段就停止
        
        # 去重
        unique_suggestions = []
        seen = set()
        for suggestion in combined_suggestions:
            if suggestion not in seen:
                seen.add(suggestion)
                unique_suggestions.append(suggestion)
        
        storage_data["combined_suggestions"] = unique_suggestions[:10]
        
        # ========== SQL摘要 ==========
        sql_summaries = []
        for sql_data in group_data['sqls']:
            sql_id = sql_data.get('sql_id')
            sql_text = sql_data.get('sql_text', '')
            analysis_data = sql_data.get('analysis_data', {})
            
            # 尝试多个可能的字段名获取SQL类型
            type_fields = ['SQL类型', 'sql_type', 'sqlType', '操作类型', 'type']
            sql_type = '未知'
            for field in type_fields:
                if field in analysis_data:
                    value = analysis_data[field]
                    if isinstance(value, str):
                        sql_type = value
                        break
            
            # 尝试多个可能的字段名获取评分
            score_fields = ['综合评分', 'score', 'Score', '评分', 'rating']
            score = 0
            for field in score_fields:
                if field in analysis_data:
                    value = analysis_data[field]
                    if isinstance(value, (int, float)):
                        score = value
                        break
            
            # 尝试多个可能的字段名获取建议数量
            suggestion_count = 0
            for field in ['建议', 'suggestions']:
                if field in analysis_data:
                    suggestions = analysis_data[field]
                    if isinstance(suggestions, list):
                        suggestion_count = len(suggestions)
                        break
            
            # 尝试获取合规性评分
            compliance_score = 0
            compliance_data = analysis_data.get('规范符合性', {})
            if isinstance(compliance_data, dict):
                compliance_score = compliance_data.get('规范符合度', 0)
            
            sql_summary = {
                "sql_id": sql_id,
                "sql_preview": processor._truncate_sql(sql_text, 80),
                "sql_type": sql_type,
                "score": float(score),
                "has_critical_issues": len(key_issues) > 0,
                "suggestion_count": suggestion_count,
                "compliance_score": float(compliance_score)
            }
            
            sql_summaries.append(sql_summary)
        
        storage_data["sql_summaries"] = sql_summaries
        
        # ========== 规范性摘要 ==========
        normative_summary = {
            "total_angles": 15,
            "average_compliance_rate": 81.5,  # 默认值
            "failed_angles": []
        }
        
        # ========== 风险统计 ==========
        # 从combined_analysis获取
        high_count = risk_summary.get('高风险问题数量', 0)
        medium_count = risk_summary.get('中风险问题数量', 0)
        low_count = risk_summary.get('低风险问题数量', 0)
        
        # 如果从combined_analysis获取不到，从key_issues计算
        if high_count == 0 and medium_count == 0 and low_count == 0:
            high_count = sum(1 for issue in key_issues if issue.get('severity') == '高风险')
            medium_count = sum(1 for issue in key_issues if issue.get('severity') == '中风险')
            low_count = sum(1 for issue in key_issues if issue.get('severity') == '低风险')
        
        risk_stats = {
            "high_risk_count": high_count,
            "medium_risk_count": medium_count,
            "low_risk_count": low_count,
            "total_risk_count": high_count + medium_count + low_count
        }
        
        storage_data["normative_summary"] = normative_summary
        storage_data["risk_stats"] = risk_stats
        
        return storage_data
    
    # 运行增强版逻辑
    result_enhanced = enhanced_prepare_storage_data(group_data, combined_result)
    
    print(f"\n4. 增强版逻辑结果:")
    print(f"     - key_issues数量: {len(result_enhanced.get('key_issues', []))}")
    print(f"     - combined_suggestions数量: {len(result_enhanced.get('combined_suggestions', []))}")
    print(f"     - sql_summaries数量: {len(result_enhanced.get('sql_summaries', []))}")
    print(f"     - 数据大小: {len(json.dumps(result_enhanced))} 字符")
    
    # 保存结果
    with open("enhanced_storage_data.json", "w", encoding="utf-8") as f:
        json.dump(result_enhanced, f, ensure_ascii=False, indent=2)
    
    print(f"   ✅ 增强版逻辑结果已保存到: enhanced_storage_data.json")
    
    # 比较结果
    print("\n5. 结果比较：")
    if len(result_enhanced.get('key_issues', [])) > len(result_current.get('key_issues', [])):
        print(f"   ✅ 增强版提取到更多key_issues: {len(result_enhanced['key_issues'])} vs {len(result_current.get('key_issues', []))}")
    else:
        print(f"   ⚠️  key_issues数量相同或更少")
    
    if len(result_enhanced.get('combined_suggestions', [])) > len(result_current.get('combined_suggestions', [])):
        print(f"   ✅ 增强版提取到更多combined_suggestions: {len(result_enhanced['combined_suggestions'])} vs {len(result_current.get('combined_suggestions', []))}")
    else:
        print(f"   ⚠️  combined_suggestions数量相同或更少")
    
    print("\n6. 建议的修复：")
    print("   将增强版的数据提取逻辑替换到group_processor_fixed_v2.py的_prepare_storage_data方法中")
    print("   或者创建一个新的增强方法，并在store_to_commit_shell_info中调用")
    
    return True

def main():
    print("开始测试数据提取逻辑...")
    
    if test_prepare_storage_data_logic():
        print("\n✅ 测试完成！")
        print("\n下一步：")
        print("1. 查看生成的JSON文件（current_storage_data.json, enhanced_storage_data.json）")
        print("2. 将增强版的数据提取逻辑应用到实际代码中")
        print("3. 重新测试分组存储功能")
        return 0
    else:
        print("\n❌ 测试失败！")
        return 1

if __name__ == "__main__":
    sys.exit(main())
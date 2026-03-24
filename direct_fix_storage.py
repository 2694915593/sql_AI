#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直接修复分组存储数据为空的问题
分析实际的数据流，找出问题所在
"""

import json
import sys
import os
from typing import Dict, Any, List

def analyze_data_flow():
    """分析数据流，找出问题所在"""
    
    print("=" * 80)
    print("分析分组存储数据为空的问题")
    print("=" * 80)
    
    print("1. 检查数据流中的关键节点...")
    
    # 分析_prepare_storage_data方法的输入输出
    print("\n2. 分析_prepare_storage_data方法：")
    print("   - 输入: group_data 和 combined_result")
    print("   - 输出: storage_data (用于存储到数据库)")
    
    print("\n3. 可能的问题点：")
    print("   a) combined_result 中没有期望的数据结构")
    print("   b) analysis_data 中没有完整的分析结果")
    print("   c) 数据库连接失败（cryptography包缺失）")
    print("   d) 数据库表或字段不存在")
    
    print("\n4. 创建测试数据流分析脚本...")
    
    test_analysis_script = """#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试数据流分析

import sys
import os
import json

def analyze_sample_data():
    \"\"\"分析样本数据流\"\"\"
    
    print("=" * 80)
    print("样本数据流分析")
    print("=" * 80)
    
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
                    'key_issues': [
                        {
                            'category': '性能问题',
                            'description': '缺少索引',
                            'severity': '中风险',
                            'suggestion': '为id字段添加索引'
                        }
                    ],
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
    print(f"   group_data 有 {len(group_data['sqls'])} 条SQL")
    print(f"   combined_result 有完整的结构")
    
    # 分析关键数据点
    print("\n5. 关键数据点分析：")
    
    # 检查analysis_data
    for i, sql_data in enumerate(group_data['sqls']):
        print(f"\n   SQL {i+1} (ID: {sql_data['sql_id']}):")
        analysis_data = sql_data['analysis_data']
        
        print(f"     - SQL类型: {analysis_data.get('SQL类型', analysis_data.get('sql_type', '未知'))}")
        print(f"     - 评分: {analysis_data.get('综合评分', analysis_data.get('score', 0))}")
        
        # 检查建议
        suggestions = analysis_data.get('建议', analysis_data.get('suggestions', []))
        print(f"     - 建议数量: {len(suggestions) if isinstance(suggestions, list) else 0}")
        
        # 检查key_issues
        key_issues = analysis_data.get('key_issues', [])
        print(f"     - 关键问题数量: {len(key_issues) if isinstance(key_issues, list) else 0}")
        
        # 检查summary
        summary = analysis_data.get('summary', {})
        print(f"     - summary存在: {'是' if summary else '否'}")
        
        # 检查规范符合性
        compliance_data = analysis_data.get('规范符合性', {})
        print(f"     - 规范符合度: {compliance_data.get('规范符合度', 0)}")
    
    # 检查combined_result
    print(f"\n   combined_result结构:")
    print(f"     - summary存在: {'是' if combined_result.get('summary') else '否'}")
    print(f"     - combined_analysis存在: {'是' if combined_result.get('combined_analysis') else '否'}")
    
    risk_summary = combined_result.get('combined_analysis', {}).get('risk_summary', {})
    print(f"     - risk_summary存在: {'是' if risk_summary else '否'}")
    
    if risk_summary:
        print(f"     - 高风险问题数量: {risk_summary.get('高风险问题数量', 0)}")
        print(f"     - 详细问题存在: {'是' if risk_summary.get('详细问题') else '否'}")
    
    # 模拟_prepare_storage_data的逻辑
    print("\n6. 模拟_prepare_storage_data方法执行...")
    
    # 创建一个简化的模拟方法
    def mock_prepare_storage_data(group_data, combined_result):
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
        
        # 提取关键问题
        key_issues = []
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
                        "severity": risk_level[:3]  # '高风险' etc.
                    })
        
        # 如果从combined_analysis提取不到，从analysis_data提取
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
                                "severity": issue.get('severity', '中风险')
                            })
        
        storage_data["key_issues"] = key_issues[:5]
        
        # 提取合并建议
        combined_suggestions = []
        all_suggestions = combined_analysis.get('all_suggestions', [])
        
        if isinstance(all_suggestions, list):
            for suggestion_item in all_suggestions[:5]:
                if isinstance(suggestion_item, dict):
                    suggestions = suggestion_item.get('suggestions', [])
                    if isinstance(suggestions, list):
                        for suggestion in suggestions[:3]:
                            if isinstance(suggestion, dict):
                                text = suggestion.get('text', '')
                                if text and isinstance(text, str):
                                    clean_text = text.strip()[:100]
                                    combined_suggestions.append(clean_text)
        
        # 如果从combined_analysis提取不到，从analysis_data提取
        if not combined_suggestions:
            for sql_data in group_data['sqls'][:3]:
                analysis_data = sql_data.get('analysis_data', {})
                suggestions = analysis_data.get('建议', analysis_data.get('suggestions', []))
                if isinstance(suggestions, list):
                    for suggestion in suggestions[:2]:
                        if isinstance(suggestion, str):
                            clean_suggestion = suggestion.strip()[:80]
                            if clean_suggestion not in combined_suggestions:
                                combined_suggestions.append(clean_suggestion)
        
        storage_data["combined_suggestions"] = combined_suggestions[:10]
        
        # 创建SQL摘要
        sql_summaries = []
        for sql_data in group_data['sqls']:
            sql_id = sql_data.get('sql_id')
            sql_text = sql_data.get('sql_text', '')
            analysis_data = sql_data.get('analysis_data', {})
            
            sql_summary = {
                "sql_id": sql_id,
                "sql_preview": sql_text[:80] + ('...' if len(sql_text) > 80 else ''),
                "sql_type": analysis_data.get('SQL类型', analysis_data.get('sql_type', '未知')),
                "score": float(analysis_data.get('综合评分', analysis_data.get('score', 0))),
                "has_critical_issues": len(key_issues) > 0,
                "suggestion_count": len(analysis_data.get('建议', analysis_data.get('suggestions', []))),
                "compliance_score": analysis_data.get('规范符合性', {}).get('规范符合度', 0)
            }
            
            sql_summaries.append(sql_summary)
        
        storage_data["sql_summaries"] = sql_summaries
        
        # 规范性摘要
        normative_summary = {
            "total_angles": 15,
            "average_compliance_rate": 81.5,
            "failed_angles": []
        }
        
        # 风险统计
        risk_stats = {
            "high_risk_count": risk_summary.get('高风险问题数量', len([i for i in key_issues if i.get('severity') == '高风险'])),
            "medium_risk_count": risk_summary.get('中风险问题数量', len([i for i in key_issues if i.get('severity') == '中风险'])),
            "low_risk_count": risk_summary.get('低风险问题数量', len([i for i in key_issues if i.get('severity') == '低风险'])),
            "total_risk_count": risk_summary.get('高风险问题数量', 0) + risk_summary.get('中风险问题数量', 0) + risk_summary.get('低风险问题数量', 0)
        }
        
        storage_data["normative_summary"] = normative_summary
        storage_data["risk_stats"] = risk_stats
        
        return storage_data
    
    # 执行模拟方法
    result = mock_prepare_storage_data(group_data, combined_result)
    
    print(f"✅ 模拟执行完成")
    print(f"   生成的数据大小: {len(json.dumps(result))} 字符")
    print(f"   key_issues数量: {len(result.get('key_issues', []))}")
    print(f"   combined_suggestions数量: {len(result.get('combined_suggestions', []))}")
    print(f"   sql_summaries数量: {len(result.get('sql_summaries', []))}")
    
    # 保存结果
    with open("mock_storage_data.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 模拟数据已保存到: mock_storage_data.json")
    
    # 检查结果
    print("\n7. 结果检查：")
    if len(result.get('key_issues', [])) == 0:
        print("   ⚠️  warning: key_issues为空！")
        print("     可能原因：")
        print("     - analysis_data中没有key_issues字段")
        print("     - combined_result.risk_summary.详细问题为空")
        print("     - 数据格式不匹配")
    else:
        print(f"   ✅ key_issues有 {len(result.get('key_issues', []))} 条数据")
    
    if len(result.get('combined_suggestions', [])) == 0:
        print("   ⚠️  warning: combined_suggestions为空！")
        print("     可能原因：")
        print("     - analysis_data中没有建议字段")
        print("     - combined_result.all_suggestions为空")
    else:
        print(f"   ✅ combined_suggestions有 {len(result.get('combined_suggestions', []))} 条数据")
    
    return True

def main():
    print("开始数据流分析...")
    
    if analyze_sample_data():
        print("\n✅ 分析完成！")
        print("\n建议的解决方案：")
        print("1. 检查analysis_data是否包含必要的字段（key_issues, 建议, SQL类型, 综合评分等）")
        print("2. 检查combined_result是否包含完整的combined_analysis结构")
        print("3. 安装cryptography包: pip install cryptography")
        print("4. 创建数据库表和字段（如果不存在）")
        return 0
    else:
        print("\n❌ 分析失败！")
        return 1

if __name__ == "__main__":
    sys.exit(main())

"""
    
    with open("analyze_data_flow.py", "w", encoding="utf-8") as f:
        f.write(test_analysis_script)
    
    print(f"✅ 数据流分析脚本已创建: analyze_data_flow.py")
    
    print("\n5. 创建实际的修复方案...")
    
    fix_solution = """#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
实际修复分组存储数据为空的解决方案

import sys
import os
import json

def implement_fix_solution():
    \"\"\"实施修复方案\"\"\"
    
    print("=" * 80)
    print("实施分组存储数据为空问题的修复方案")
    print("=" * 80)
    
    print("1. 第一步：安装必要的依赖包")
    print("   pip install cryptography")
    print("   这个包用于MySQL的sha256_password认证方式")
    
    print("\n2. 第二步：检查数据库表结构")
    print("   -- 检查AM_COMMIT_SHELL_INFO表是否存在")
    print("      SHOW TABLES LIKE 'AM_COMMIT_SHELL_INFO';")
    print("   ")
    print("   -- 如果不存在，创建表")
    print("      CREATE TABLE IF NOT EXISTS AM_COMMIT_SHELL_INFO (")
    print("          ID INT AUTO_INCREMENT PRIMARY KEY,")
    print("          PROJECT_ID VARCHAR(100) NULL,")
    print("          DEFAULT_VERSION VARCHAR(100) NULL,")
    print("          CLASSPATH VARCHAR(500) NULL,")
    print("          FILENAME VARCHAR(255) NULL,")
    print("          AI_ANALYSE_RESULT TEXT NULL,")
    print("          CREATE_TIME DATETIME DEFAULT CURRENT_TIMESTAMP,")
    print("          UPDATE_TIME DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")
    print("      );")
    
    print("\n3. 第三步：检查AI_ANALYSE_RESULT字段")
    print("   -- 检查字段是否存在")
    print("      DESCRIBE AM_COMMIT_SHELL_INFO;")
    print("   ")
    print("   -- 如果不存在，添加字段")
    print("      ALTER TABLE AM_COMMIT_SHELL_INFO ADD COLUMN IF NOT EXISTS AI_ANALYSE_RESULT TEXT NULL;")
    
    print("\n4. 第四步：修复_prepare_storage_data方法的数据提取逻辑")
    print("   - 确保从analysis_data中提取key_issues时，能处理不同的字段名")
    print("   - 确保从analysis_data中提取建议时，能处理中文和英文字段名")
    print("   - 确保有完整的错误处理")
    
    print("\n5. 第五步：实施数据提取增强")
    
    enhanced_code = '''
    def _prepare_storage_data_robust(self, group_data, combined_result):
        """增强版的数据准备方法"""
        
        storage_data = {
            "summary": {
                "file_name": group_data['file_name'],
                "project_id": group_data['project_id'],
                "default_version": group_data['default_version'],
                "sql_count": len(group_data['sqls']),
                "file_path": group_data.get('file_path', '')
            },
            "key_issues": [],
            "combined_suggestions": [],
            "sql_summaries": [],
            "normative_summary": {
                "total_angles": 15,
                "average_compliance_rate": 0,
                "failed_angles": []
            },
            "risk_stats": {
                "high_risk_count": 0,
                "medium_risk_count": 0,
                "low_risk_count": 0,
                "total_risk_count": 0
            }
        }
        
        # 增强的关键问题提取
        key_issues = []
        for sql_data in group_data['sqls']:
            analysis_data = sql_data.get('analysis_data', {})
            
            # 尝试多个可能的字段名
            issues_fields = ['key_issues', 'KeyIssues', 'keyIssues', '关键问题']
            for field in issues_fields:
                if field in analysis_data:
                    issues = analysis_data[field]
                    if isinstance(issues, list):
                        for issue in issues:
                            if isinstance(issue, dict):
                                key_issues.append({
                                    "sql_id": sql_data.get('sql_id'),
                                    "category": issue.get('category', '未知'),
                                    "description": issue.get('description', ''),
                                    "severity": issue.get('severity', '中风险')
                                })
        
        storage_data["key_issues"] = key_issues[:5]
        
        # 增强的建议提取
        combined_suggestions = []
        for sql_data in group_data['sqls']:
            analysis_data = sql_data.get('analysis_data', {})
            
            # 尝试多个可能的字段名
            suggestion_fields = ['建议', 'suggestions', 'Suggestions', '改进建议']
            for field in suggestion_fields:
                if field in analysis_data:
                    suggestions = analysis_data[field]
                    if isinstance(suggestions, list):
                        for suggestion in suggestions:
                            if isinstance(suggestion, str):
                                combined_suggestions.append(suggestion[:80])
        
        storage_data["combined_suggestions"] = list(set(combined_suggestions))[:10]
        
        # SQL摘要
        sql_summaries = []
        for sql_data in group_data['sqls']:
            sql_id = sql_data.get('sql_id')
            sql_text = sql_data.get('sql_text', '')
            analysis_data = sql_data.get('analysis_data', {})
            
            # 尝试多个可能的字段名获取SQL类型
            type_fields = ['SQL类型', 'sql_type', 'sqlType', '操作类型']
            sql_type = '未知'
            for field in type_fields:
                if field in analysis_data:
                    sql_type = analysis_data[field]
                    break
            
            # 尝试多个可能的字段名获取评分
            score_fields = ['综合评分', 'score', 'Score', '评分']
            score = 0
            for field in score_fields:
                if field in analysis_data:
                    score = analysis_data[field]
                    break
            
            sql_summary = {
                "sql_id": sql_id,
                "sql_preview": self._truncate_sql(sql_text, 80),
                "sql_type": sql_type,
                "score": float(score) if isinstance(score, (int, float)) else 0,
                "has_critical_issues": len(key_issues) > 0,
                "suggestion_count": len(combined_suggestions),
                "compliance_score": 0
            }
            
            sql_summaries.append(sql_summary)
        
        storage_data["sql_summaries"] = sql_summaries
        
        # 计算风险统计
        high_count = sum(1 for issue in key_issues if issue.get('severity') == '高风险')
        medium_count = sum(1 for issue in key_issues if issue.get('severity') == '中风险')
        low_count = sum(1 for issue in key_issues if issue.get('severity') == '低风险')
        
        storage_data["risk_stats"] = {
            "high_risk_count": high_count,
            "medium_risk_count": medium_count,
            "low_risk_count": low_count,
            "total_risk_count": high_count + medium_count + low_count
        }
        
        return storage_data
    '''
    
    print("   代码已准备好，可以添加到group_processor_fixed_v2.py中")
    
    print("\n6. 第六步：测试修复")
    print("   - 运行: python analyze_data_flow.py")
    print("   - 检查输出的mock_storage_data.json是否包含数据")
    print("   - 如果数据完整，说明_prepare_storage_data方法能正确工作")
    
    print("\n7. 第七步：实施完整的修复")
    print("   - 将上面的增强方法添加到group_processor_fixed_v2.py中")
    print("   - 修改store_to_commit_shell_info方法，使用增强版的数据准备方法")
    print("   - 或者直接修改现有的_prepare_storage_data方法")
    
    return True

if __name__ == "__main__":
    implement_fix_solution()
    print("\n✅ 修复方案已生成")
    print("\n执行步骤：")
    print("1. 运行: pip install cryptography")
    print("2. 运行: python analyze_data_flow.py")
    print("3. 根据分析结果修改代码")
    print("4. 创建数据库表和字段（如果需要）")
    print("5. 重新运行分组存储功能")

"""
    
    with open("fix_solution_guide.py", "w", encoding="utf-8") as f:
        f.write(fix_solution)
    
    print(f"✅ 修复方案指南已创建: fix_solution_guide.py")
    
    print("\n" + "=" * 80)
    print("问题分析完成！")
    print("=" * 80)
    print("\n核心问题：")
    print("1. 数据库连接需要 cryptography 包")
    print("2. _prepare_storage_data 方法可能因为数据格式问题提取不到数据")
    print("\n解决方案：")
    print("1. 安装 cryptography 包: pip install cryptography")
    print("2. 运行 analyze_data_flow.py 分析具体的数据流问题")
    print("3. 根据分析结果修改 _prepare_storage_data 方法")
    print("4. 确保数据库表和字段存在")
    
    return True

def main():
    print("开始分析分组存储数据为空的问题...")
    
    if analyze_data_flow():
        print("\n✅ 分析完成！")
        return 0
    else:
        print("\n❌ 分析失败！")
        return 1

if __name__ == "__main__":
    sys.exit(main())
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试数据流向：从大模型响应到分组入表
"""

import sys
import json
sys.path.append('sql_ai_analyzer')

# 模拟大模型响应数据（基于model_client_fixed.py的输出格式）
def simulate_model_response():
    """模拟大模型返回的响应数据"""
    return {
        'success': True,
        'score': 8.5,
        'sql_type': 'CREATE',
        'suggestions': ['建议添加主键', '检查字符集一致性'],
        'analysis_result': {
            '建议': ['建议添加主键', '检查字符集一致性'],
            'SQL类型': 'CREATE',
            '分析摘要': '该建表语句存在缺少主键和字符集不一致的问题',
            '综合评分': 8.5,
            '规范符合性': {
                '规范符合度': 85.0,
                '规范违反详情': []
            },
            '风险评估': {
                '高风险问题': ['缺少主键'],
                '中风险问题': ['字符集不一致'],
                '低风险问题': ['注释不完整']
            },
            '修改建议': {
                '高风险问题SQL': 'ALTER TABLE table1 ADD PRIMARY KEY (id)',
                '中风险问题SQL': 'ALTER TABLE table1 CONVERT TO CHARACTER SET utf8mb4',
                '低风险问题SQL': 'ALTER TABLE table1 MODIFY COLUMN name VARCHAR(100) COMMENT "用户姓名"',
                '性能优化SQL': ''
            }
        },
        'raw_response': {
            'RSP_BODY': {
                'answer': '{"建议": ["建议添加主键", "检查字符集一致性"], "SQL类型": "CREATE", "分析摘要": "该建表语句存在缺少主键和字符集不一致的问题", "综合评分": 8.5, "规范符合性": {"规范符合度": 85.0, "规范违反详情": []}, "风险评估": {"高风险问题": ["缺少主键"], "中风险问题": ["字符集不一致"], "低风险问题": ["注释不完整"]}, "修改建议": {"高风险问题SQL": "ALTER TABLE table1 ADD PRIMARY KEY (id)", "中风险问题SQL": "ALTER TABLE table1 CONVERT TO CHARACTER SET utf8mb4", "低风险问题SQL": "ALTER TABLE table1 MODIFY COLUMN name VARCHAR(100) COMMENT \\"用户姓名\\"", "性能优化SQL": ""}}'
            }
        }
    }

# 模拟结果处理器的处理
def simulate_result_processor(analysis_result):
    """模拟result_processor.py的_prepare_storage_data方法"""
    # 这是result_processor.py中_build_new_json_format方法的简化版本
    storage_data = {
        "建议": analysis_result.get('analysis_result', {}).get('建议', []),
        "SQL类型": analysis_result.get('analysis_result', {}).get('SQL类型', '未知'),
        "分析摘要": analysis_result.get('analysis_result', {}).get('分析摘要', ''),
        "综合评分": analysis_result.get('analysis_result', {}).get('综合评分', 0),
        "规范符合性": analysis_result.get('analysis_result', {}).get('规范符合性', {
            "规范符合度": 0.0,
            "规范违反详情": []
        }),
        "风险评估": analysis_result.get('analysis_result', {}).get('风险评估', {
            "高风险问题": [],
            "中风险问题": [],
            "低风险问题": []
        }),
        "修改建议": analysis_result.get('analysis_result', {}).get('修改建议', {
            "高风险问题SQL": "",
            "中风险问题SQL": "",
            "低风险问题SQL": "",
            "性能优化SQL": ""
        })
    }
    return storage_data

# 模拟分组处理器的处理
def simulate_group_processor(storage_data_list):
    """模拟group_processor.py的_prepare_storage_data方法"""
    # 这是group_processor.py中_prepare_storage_data方法的简化版本
    combined_result = {
        "combined_analysis": {
            "all_suggestions": [],
            "risk_summary": {},
            "performance_summary": {},
            "security_summary": {}
        }
    }
    
    # 确保combined_analysis有完整的结构
    if not combined_result["combined_analysis"]:
        combined_result["combined_analysis"] = {
            "all_suggestions": [],
            "risk_summary": {
                "高风险问题数量": 0,
                "中风险问题数量": 0,
                "低风险问题数量": 0,
                "详细问题": {
                    "高风险问题": [],
                    "中风险问题": [],
                    "低风险问题": []
                }
            },
            "performance_summary": {},
            "security_summary": {}
        }
    
    # 构建group_processor的_prepare_storage_data输出
    group_data = {
        'file_name': 'test.sql',
        'project_id': 'CBNK',
        'default_version': 'release-prd-2603.13',
        'file_path': 'db_cbnk/release/2603.13/037_BoCom07987930/V_001_BoCom07987930_CREATE_TABLE_PUB_BURIED.sql',
        'sqls': [
            {
                'sql_id': 21483,
                'sql_text': 'CREATE TABLE ...',
                'analysis_data': storage_data_list[0] if storage_data_list else {}
            },
            {
                'sql_id': 21485,
                'sql_text': 'CREATE TABLE ...',
                'analysis_data': storage_data_list[1] if len(storage_data_list) > 1 else {}
            }
        ]
    }
    
    final_result = {
        "file_info": {
            "file_name": group_data['file_name'],
            "project_id": group_data['project_id'],
            "default_version": group_data['default_version'],
            "file_path": group_data['file_path'],
            "sql_count": len(group_data['sqls'])
        },
        "analysis_summary": {
            "total_sqls": len(group_data['sqls']),
            "unique_files": 1,
            "unique_projects": 1,
            "analysis_time": "NOW()",
            "average_score": 0,
            "success_rate": 100.0
        },
        "combined_analysis": combined_result["combined_analysis"],
        "sql_details": []
    }
    
    # 添加每个SQL的详细信息
    for sql_data in group_data['sqls']:
        sql_detail = {
            "sql_id": sql_data['sql_id'],
            "sql_preview": sql_data['sql_text'][:150] + "..." if len(sql_data['sql_text']) > 150 else sql_data['sql_text'],
            "analysis_data": sql_data['analysis_data']
        }
        final_result["sql_details"].append(sql_detail)
    
    return final_result

def main():
    print("=" * 80)
    print("调试数据流向：从大模型响应到分组入表")
    print("=" * 80)
    
    # 步骤1: 模拟大模型响应
    print("\n1. 大模型响应数据:")
    model_response = simulate_model_response()
    print(json.dumps(model_response, ensure_ascii=False, indent=2)[:500] + "...")
    
    # 步骤2: 模拟结果处理器处理
    print("\n2. 结果处理器处理后数据:")
    storage_data = simulate_result_processor(model_response)
    print(json.dumps(storage_data, ensure_ascii=False, indent=2))
    
    # 检查关键字段
    print("\n关键字段检查:")
    print(f"  建议数量: {len(storage_data.get('建议', []))}")
    print(f"  SQL类型: {storage_data.get('SQL类型', '未知')}")
    print(f"  分析摘要: {storage_data.get('分析摘要', '')[:50]}...")
    print(f"  综合评分: {storage_data.get('综合评分', 0)}")
    
    risk_assessment = storage_data.get('风险评估', {})
    print(f"  风险评估存在: {'是' if risk_assessment else '否'}")
    if risk_assessment:
        print(f"    高风险问题: {len(risk_assessment.get('高风险问题', []))}")
        print(f"    中风险问题: {len(risk_assessment.get('中风险问题', []))}")
        print(f"    低风险问题: {len(risk_assessment.get('低风险问题', []))}")
    
    modification_suggestions = storage_data.get('修改建议', {})
    print(f"  修改建议存在: {'是' if modification_suggestions else '否'}")
    
    # 步骤3: 模拟分组处理器处理
    print("\n3. 分组处理器处理后数据:")
    final_data = simulate_group_processor([storage_data, storage_data])
    
    # 检查用户提到的问题
    print("\n用户提到的问题检查:")
    
    # 问题1: sql_details[].analysis_data 是否为空
    print("  问题1: sql_details[].analysis_data 是否为空?")
    for i, detail in enumerate(final_data.get('sql_details', [])):
        analysis_data = detail.get('analysis_data', {})
        is_empty = len(analysis_data) == 0 if isinstance(analysis_data, dict) else True
        print(f"    SQL {i+1}: {'是' if is_empty else '否'}")
        if not is_empty:
            print(f"      包含字段: {list(analysis_data.keys())}")
    
    # 问题2: combined_analysis.risk_summary.详细问题 是否存在
    print("\n  问题2: combined_analysis.risk_summary.详细问题 是否存在?")
    combined_analysis = final_data.get('combined_analysis', {})
    risk_summary = combined_analysis.get('risk_summary', {})
    has_detail = '详细问题' in risk_summary
    print(f"    存在: {'是' if has_detail else '否'}")
    if has_detail:
        detail_problems = risk_summary.get('详细问题', {})
        print(f"      高风险问题: {len(detail_problems.get('高风险问题', []))}")
        print(f"      中风险问题: {len(detail_problems.get('中风险问题', []))}")
        print(f"      低风险问题: {len(detail_problems.get('低风险问题', []))}")
    
    # 问题3: combined_analysis.performance_summary 和 security_summary 是否存在
    print("\n  问题3: combined_analysis.performance_summary 和 security_summary 是否存在?")
    has_perf = 'performance_summary' in combined_analysis
    has_security = 'security_summary' in combined_analysis
    print(f"    performance_summary: {'是' if has_perf else '否'}")
    print(f"    security_summary: {'是' if has_security else '否'}")
    
    # 输出最终数据结构
    print("\n最终数据结构预览:")
    final_json = json.dumps(final_data, ensure_ascii=False, indent=2)
    print(final_json[:800] + "..." if len(final_json) > 800 else final_json)
    
    print("\n" + "=" * 80)
    print("调试完成")
    
    # 与用户提供的示例对比
    print("\n与用户提供的示例对比:")
    user_example = {
        "file_info": {
            "file_name": "V_001_BoCom07987930_CREATE_TABLE_PUB_BURIED.sql",
            "project_id": "CBNK",
            "default_version": "release-prd-2603.13",
            "file_path": "db_cbnk/release/2603.13/037_BoCom07987930/V_001_BoCom07987930_CREATE_TABLE_PUB_BURIED.sql",
            "sql_count": 2
        },
        "analysis_summary": {
            "total_sqls": 2,
            "unique_files": 1,
            "unique_projects": 1,
            "analysis_time": "NOW()",
            "average_score": 0,
            "success_rate": 100.0
        },
        "combined_analysis": {
            "all_suggestions": [],
            "risk_summary": {
                "高风险问题数量": 0,
                "中风险问题数量": 0,
                "低风险问题数量": 0,
                "详细问题": {
                    "高风险问题": [],
                    "中风险问题": [],
                    "低风险问题": []
                }
            },
            "performance_summary": {},
            "security_summary": {}
        },
        "sql_details": [
            {
                "sql_id": 21483,
                "sql_preview": "",
                "analysis_data": {}
            },
            {
                "sql_id": 21485,
                "sql_preview": "",
                "analysis_data": {}
            }
        ]
    }
    
    print("用户示例中的问题:")
    print("  1. sql_details[].analysis_data: 空对象 {}")
    print("  2. combined_analysis.risk_summary.详细问题: 存在（但内容为空）")
    print("  3. performance_summary 和 security_summary: 存在（但内容为空）")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
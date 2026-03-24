#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试完整流程：从AI响应到入库的建议字段处理
"""

import json
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_full_flow():
    """测试完整流程"""
    
    print("测试完整流程：从AI响应到入库的建议字段处理")
    print("=" * 70)
    
    # 1. 模拟AI响应
    print("\n1. 模拟AI响应数据")
    print("-" * 40)
    
    # 完整的AI响应结构（模拟实际API返回）
    ai_response = {
        "success": True,
        "raw_response": {
            "RSP_BODY": {
                "head": {},
                "TRAN_PROCESS": "aiQA",
                "answer": json.dumps({
                    "建议": ["建议1: 添加索引", "建议2: 参数化查询", "建议3: 优化JOIN条件"],
                    "SQL类型": "查询",
                    "分析摘要": "这是一个测试分析摘要，包含性能优化建议",
                    "综合评分": 8,
                    "风险评估": {
                        "高风险问题": ["SQL注入风险"],
                        "中风险问题": ["性能问题"],
                        "低风险问题": ["可读性问题"]
                    },
                    "修改建议": {
                        "高风险问题SQL": "SELECT * FROM users WHERE id = ?",
                        "中风险问题SQL": "SELECT * FROM users WHERE name = ?",
                        "低风险问题SQL": "SELECT * FROM users WHERE email = ?",
                        "性能优化SQL": "SELECT id, name FROM users WHERE id = ?"
                    }
                }, ensure_ascii=False)
            },
            "RSP_HEAD": {}
        },
        "analysis_result": {}
    }
    
    print("AI响应结构:")
    print(json.dumps(ai_response, ensure_ascii=False, indent=2))
    
    # 2. 模拟ModelClient解析
    print("\n\n2. ModelClient解析AI响应")
    print("-" * 40)
    
    # 创建模拟的ModelClient解析逻辑
    def mock_model_client_parse(response):
        """模拟ModelClient的解析逻辑"""
        try:
            # 提取answer字段
            raw_response = response.get('raw_response', {})
            rsp_body = raw_response.get('RSP_BODY', {})
            answer_str = rsp_body.get('answer', '')
            
            print(f"   answer字符串长度: {len(answer_str)}")
            
            # 解析answer字段
            answer_data = json.loads(answer_str)
            print(f"   成功解析answer字段")
            
            # 提取各个字段（模拟更新后的逻辑）
            result = {
                'success': True,
                'raw_response': response,
                'analysis_result': answer_data
            }
            
            # 提取建议
            suggestion_fields = ['建议', 'suggestions', 'improvement_suggestions', 'recommendations']
            all_suggestions = []
            
            for field in suggestion_fields:
                if field in answer_data:
                    suggestions = answer_data[field]
                    if isinstance(suggestions, list):
                        all_suggestions.extend(suggestions)
                    elif isinstance(suggestions, dict):
                        for value in suggestions.values():
                            if isinstance(value, list):
                                all_suggestions.extend(value)
            
            # 清理建议
            cleaned_suggestions = []
            seen = set()
            for suggestion in all_suggestions:
                if isinstance(suggestion, str):
                    clean_suggestion = suggestion.strip()
                    if clean_suggestion and clean_suggestion not in seen:
                        seen.add(clean_suggestion)
                        cleaned_suggestions.append(clean_suggestion)
                elif suggestion is not None:
                    suggestion_str = str(suggestion).strip()
                    if suggestion_str and suggestion_str not in seen:
                        seen.add(suggestion_str)
                        cleaned_suggestions.append(suggestion_str)
            
            result['suggestions'] = cleaned_suggestions
            result['improvement_suggestions'] = cleaned_suggestions
            
            # 提取SQL类型
            sql_type_fields = ['SQL类型', 'sql_type', 'SQL类型', 'type']
            result['sql_type'] = '未知'
            for field in sql_type_fields:
                if field in answer_data:
                    sql_type_value = answer_data[field]
                    if sql_type_value and isinstance(sql_type_value, str):
                        result['sql_type'] = sql_type_value
                        break
            
            # 提取评分
            score_fields = ['综合评分', 'overall_score', 'score', 'quality_score']
            result['score'] = 5.0
            for field in score_fields:
                if field in answer_data:
                    score_value = answer_data[field]
                    if isinstance(score_value, (int, float)):
                        result['score'] = float(score_value)
                        break
                    elif isinstance(score_value, str):
                        try:
                            result['score'] = float(score_value)
                            break
                        except ValueError:
                            continue
            
            # 提取分析摘要
            summary_fields = ['分析摘要', 'summary', 'detailed_analysis', 'analysis_summary']
            result['summary'] = ''
            for field in summary_fields:
                if field in answer_data:
                    summary_value = answer_data[field]
                    if summary_value and isinstance(summary_value, str):
                        result['summary'] = summary_value
                        break
            
            return result
            
        except Exception as e:
            print(f"   ❌ 解析失败: {e}")
            return {
                'success': False,
                'error': str(e),
                'suggestions': [],
                'score': 0.0
            }
    
    # 模拟解析
    parsed_result = mock_model_client_parse(ai_response)
    print(f"   解析成功: {parsed_result['success']}")
    print(f"   提取到建议数量: {len(parsed_result.get('suggestions', []))}")
    print(f"   建议内容: {parsed_result.get('suggestions', [])}")
    print(f"   SQL类型: {parsed_result.get('sql_type', '未知')}")
    print(f"   评分: {parsed_result.get('score', 0)}")
    print(f"   分析摘要: {parsed_result.get('summary', '')[:50]}...")
    
    # 3. 模拟ResultProcessor处理
    print("\n\n3. ResultProcessor处理分析结果")
    print("-" * 40)
    
    def mock_result_processor_prepare(analysis_result, metadata):
        """模拟ResultProcessor的_prepare_storage_data方法"""
        # 提取关键信息
        raw_result = analysis_result.get('analysis_result', {})
        suggestions = analysis_result.get('suggestions', [])
        score = analysis_result.get('score', 0)
        
        print(f"   输入的suggestions: {suggestions}")
        print(f"   输入的score: {score}")
        
        # 清理建议
        def clean_suggestions(suggestions_list):
            cleaned = []
            for suggestion in suggestions_list:
                if isinstance(suggestion, dict):
                    if 'text' in suggestion:
                        cleaned.append(str(suggestion['text']))
                    elif 'suggestion' in suggestion:
                        cleaned.append(str(suggestion['suggestion']))
                    elif 'recommendation' in suggestion:
                        cleaned.append(str(suggestion['recommendation']))
                    else:
                        cleaned.append(str(suggestion))
                elif isinstance(suggestion, str):
                    clean_suggestion = suggestion.strip()
                    if clean_suggestion:
                        clean_suggestion = clean_suggestion.replace('**', '').replace('`', '')
                        cleaned.append(clean_suggestion)
                else:
                    cleaned.append(str(suggestion))
            
            # 去重
            unique_suggestions = []
            seen = set()
            for suggestion in cleaned:
                if suggestion and suggestion not in seen:
                    seen.add(suggestion)
                    unique_suggestions.append(suggestion)
            
            return unique_suggestions
        
        cleaned_suggestions = clean_suggestions(suggestions)
        print(f"   清理后suggestions: {cleaned_suggestions}")
        
        # 构建JSON格式
        def build_json_format(suggestions, sql_type, detailed_analysis, score, analysis_result, metadata):
            # 构建最终JSON
            result_json = {
                "建议": suggestions[:10],  # 最多取10条建议
                "SQL类型": sql_type,
                "分析摘要": detailed_analysis[:200] if len(detailed_analysis) > 200 else detailed_analysis,
                "综合评分": score,
                "风险评估": {},
                "修改建议": {}
            }
            return result_json
        
        # 获取SQL类型
        sql_type = analysis_result.get('sql_type', '未知')
        if sql_type == 'UNKNOWN':
            sql_type = '未知'
        
        # 处理详细分析
        summary = analysis_result.get('summary', '')
        if summary:
            detailed_analysis = summary
        else:
            detailed_analysis = ''
        
        # 构建存储数据
        storage_data = build_json_format(
            suggestions=cleaned_suggestions,
            sql_type=sql_type,
            detailed_analysis=detailed_analysis,
            score=score,
            analysis_result=analysis_result,
            metadata=metadata
        )
        
        return storage_data
    
    # 模拟元数据
    mock_metadata = []
    
    # 模拟处理
    storage_data = mock_result_processor_prepare(parsed_result, mock_metadata)
    
    print(f"\n   生成的存储数据:")
    print(json.dumps(storage_data, ensure_ascii=False, indent=2))
    
    # 检查建议字段
    suggestions_in_storage = storage_data.get('建议', [])
    print(f"\n   入库的建议字段数量: {len(suggestions_in_storage)}")
    print(f"   入库的建议字段内容: {suggestions_in_storage}")
    
    if len(suggestions_in_storage) == 0:
        print("   ❌ 问题：入库的建议字段为空！")
        
        # 分析原因
        print("\n   原因分析:")
        print(f"   1. 原始AI响应中的建议字段: {ai_response['raw_response']['RSP_BODY']['answer']}")
        print(f"   2. ModelClient解析后的建议: {parsed_result.get('suggestions', [])}")
        print(f"   3. ResultProcessor清理后的建议: {storage_data.get('建议', [])}")
        
        # 检查清理逻辑
        original_suggestions = parsed_result.get('suggestions', [])
        if original_suggestions:
            print(f"\n   原始建议不为空，但清理后为空，可能的原因:")
            print(f"   - _clean_suggestions方法可能过滤掉了所有建议")
            print(f"   - 建议内容可能被误判为无效")
        else:
            print(f"\n   原始建议为空，问题可能出现在ModelClient解析阶段")
    else:
        print("   ✅ 入库的建议字段不为空")
    
    print("\n" + "=" * 70)
    print("测试完成")

if __name__ == "__main__":
    test_full_flow()
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试建议字段为空的问题
"""

import json
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_suggestion_extraction():
    """测试建议字段提取"""
    
    # 模拟AI响应 - 用户反馈的格式问题
    sample_response = '''{
    "raw_response": {
        "RSP_BODY": {
            "head": {},
            "TRAN_PROCESS": "aiQA",
            "answer": "{\\n  \\"sql_type\\": \\"查询\\",\\n  \\"建议\\": [\\"建议1\\", \\"建议2\\", \\"建议3\\"],\\n  \\"分析摘要\\": \\"这是一个测试分析摘要\\",\\n  \\"综合评分\\": 8,\\n  \\"风险评估\\": {\\n    \\"高风险问题\\": [\\"高风险1\\"],\\n    \\"中风险问题\\": [\\"中风险1\\"],\\n    \\"低风险问题\\": [\\"低风险1\\"]\\n  },\\n  \\"修改建议\\": {\\n    \\"高风险问题SQL\\": \\"SELECT * FROM users WHERE id = ?\\",\\n    \\"中风险问题SQL\\": \\"SELECT * FROM users WHERE name = ?\\",\\n    \\"低风险问题SQL\\": \\"SELECT * FROM users WHERE email = ?\\",\\n    \\"性能优化SQL\\": \\"SELECT * FROM users WHERE id = ?\\"\\n  }\\n}"
        },
        "RSP_HEAD": {}
    },
    "analysis_result": {}
}'''
    
    print("测试建议字段提取逻辑")
    print("=" * 60)
    
    try:
        # 1. 解析JSON响应
        response_data = json.loads(sample_response)
        print("1. JSON解析成功")
        
        # 2. 提取answer字段
        raw_response = response_data.get('raw_response', {})
        rsp_body = raw_response.get('RSP_BODY', {})
        answer_str = rsp_body.get('answer', '')
        print(f"2. 提取answer字符串长度: {len(answer_str)}")
        print(f"   answer预览: {answer_str[:200]}...")
        
        # 3. 尝试解析answer字段
        try:
            answer_data = json.loads(answer_str)
            print("3. 成功解析answer字段中的JSON")
            print(f"   JSON类型: {type(answer_data)}")
            
            if isinstance(answer_data, dict):
                suggestions = answer_data.get('建议', [])
                print(f"4. 提取到建议字段: {suggestions}")
                print(f"   建议数量: {len(suggestions)}")
                
                if suggestions:
                    print("✅ 建议字段提取成功")
                else:
                    print("❌ 建议字段为空")
            else:
                print("❌ answer_data不是字典类型")
                
        except json.JSONDecodeError as e:
            print(f"❌ 解析answer字段失败: {e}")
            print(f"   answer字段可能有多层转义")
            
            # 尝试清理转义字符
            cleaned = answer_str.replace('\\n', '\n').replace('\\"', '"')
            print(f"   清理后预览: {cleaned[:200]}...")
            
            try:
                answer_data = json.loads(cleaned)
                print("✅ 清理后解析成功")
                suggestions = answer_data.get('建议', [])
                print(f"   建议: {suggestions}")
            except json.JSONDecodeError as e2:
                print(f"❌ 清理后解析仍然失败: {e2}")
    
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")

def test_model_client_parsing():
    """测试ModelClient中的解析逻辑"""
    print("\n\n测试ModelClient解析逻辑")
    print("=" * 60)
    
    # 导入model_client中的解析方法
    try:
        from sql_ai_analyzer.ai_integration.model_client import ModelClient
        
        # 创建模拟对象
        class MockConfigManager:
            def get_ai_model_config(self):
                return {}
        
        mock_config = MockConfigManager()
        
        # 创建ModelClient实例
        client = ModelClient(mock_config)
        
        # 测试_sanitize_response_text方法
        test_text = '{\"RSP_BODY\": {\"answer\": \"{\\\"建议\\\": [\\\"test\\\"]}\"}}'
        cleaned = client._sanitize_response_text(test_text)
        print(f"1. _sanitize_response_text测试:")
        print(f"   原始长度: {len(test_text)}")
        print(f"   清理后长度: {len(cleaned)}")
        
        # 测试_try_parse_json方法
        json_test = '{"key": "value"}'
        parsed = client._try_parse_json(json_test)
        print(f"2. _try_parse_json测试:")
        print(f"   解析结果: {parsed}")
        
        # 测试_safe_parse_llm_response_text方法
        print(f"3. _safe_parse_llm_response_text测试:")
        try:
            result = client._safe_parse_llm_response_text(sample_response if 'sample_response' in locals() else test_text)
            print(f"   解析成功: {type(result)}")
            if isinstance(result, dict):
                print(f"   是否包含建议字段: {'建议' in result}")
        except Exception as e:
            print(f"   解析失败: {e}")
    
    except Exception as e:
        print(f"❌ 导入ModelClient失败: {e}")
        import traceback
        traceback.print_exc()

def test_result_processor():
    """测试ResultProcessor中的建议字段处理"""
    print("\n\n测试ResultProcessor建议字段处理")
    print("=" * 60)
    
    try:
        from sql_ai_analyzer.storage.result_processor import ResultProcessor
        
        # 创建模拟对象
        class MockConfigManager:
            def get_ai_model_config(self):
                return {}
        
        class MockLogger:
            def info(self, msg): pass
            def warning(self, msg): pass
            def error(self, msg): pass
        
        mock_config = MockConfigManager()
        
        # 创建ResultProcessor实例
        processor = ResultProcessor(mock_config, MockLogger())
        
        # 测试_clean_suggestions方法
        test_suggestions = [
            "建议1: 添加索引",
            {"text": "建议2: 优化查询"},
            ["建议3"],
            None,
            "",
            "   "
        ]
        
        cleaned = processor._clean_suggestions(test_suggestions)
        print(f"1. _clean_suggestions测试:")
        print(f"   输入建议数量: {len(test_suggestions)}")
        print(f"   清理后建议数量: {len(cleaned)}")
        print(f"   清理后建议: {cleaned}")
        
        # 测试_build_new_json_format方法
        mock_metadata = []
        mock_analysis_result = {
            'suggestions': ['建议1', '建议2'],
            'sql_type': '查询',
            'score': 8,
            'original_sql': 'SELECT * FROM users'
        }
        
        print(f"\n2. _build_new_json_format测试:")
        
        # 模拟空的详细分析
        empty_analysis = ""
        result_json = processor._build_new_json_format(
            suggestions=['建议1', '建议2'],
            sql_type='查询',
            detailed_analysis=empty_analysis,
            score=8,
            analysis_result=mock_analysis_result,
            metadata=mock_metadata
        )
        
        print(f"   生成的JSON结构:")
        for key, value in result_json.items():
            if isinstance(value, list):
                print(f"   {key}: {len(value)}个元素")
            elif isinstance(value, dict):
                print(f"   {key}: {len(value)}个键")
            else:
                print(f"   {key}: {value}")
        
        # 检查建议字段
        suggestions_field = result_json.get('建议', [])
        print(f"   建议字段: {suggestions_field}")
        print(f"   建议字段是否为空: {len(suggestions_field) == 0}")
        
    except Exception as e:
        print(f"❌ 测试ResultProcessor失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("开始测试建议字段为空的问题")
    print("=" * 60)
    
    test_suggestion_extraction()
    test_model_client_parsing()
    test_result_processor()
    
    print("\n" + "=" * 60)
    print("测试完成")
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试大模型响应解析，特别是括号处理问题
"""

import sys
import os
import re
import json

# 设置路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'sql_ai_analyzer'))

print("测试大模型响应解析中的括号处理问题")
print("=" * 80)

# 模拟大模型可能返回的响应
test_responses = [
    # 情况1: 正常的JSON响应
    {
        "success": True,
        "raw_response": {
            "RSP_BODY": {
                "head": {},
                "TRAN_PROCESS": "aiQA",
                "answer": '{"建议": ["优化SQL结构"], "SQL类型": "插入", "分析摘要": "这是一个INSERT语句", "综合评分": 8.0, "风险评估": {"高风险问题": [], "中风险问题": [], "低风险问题": []}, "修改建议": {"高风险问题SQL": "insert into MONTHLY_TRAN_MSG (MTM_PARTY_NO, MTM_SEND) VALUES (\\"value1\\", \\"value2\\")"}}'
            },
            "RSP_HEAD": {}
        }
    },
    
    # 情况2: 用户提供的格式（可能有问题）
    {
        "success": True,
        "raw_response": {
            "RSP_BODY": {
                "head": {},
                "TRAN_PROCESS": "aiQA",
                "answer": 'insert into MONTHLY_TRAN_MSG MTM_PARTY_NO, MTM_SEND, MTM_PRODUCT_TYPE, MTM_PARTY_NAME, MTM_CREATE_TIME, MTM_UPDATE_TIME, MTM_remark1, MTM_remark2, #{partyNo,jdbcType=VARCHAR}, #{send,jdbcType=VARCHAR}, #{productType,jdbcType=VARCHAR}, #{partyName,jdbcType=VARCHAR}, #{createTime,jdbcType=TIMESTAMP}, #{updateTime,jdbcType=TIMESTAMP}, #{remark1,jdbcType=VARCHAR}, #{remark2,jdbcType=VARCHAR}'
            },
            "RSP_HEAD": {}
        }
    },
    
    # 情况3: 双重引号问题
    {
        "success": True,
        "raw_response": {
            "RSP_BODY": {
                "head": {},
                "TRAN_PROCESS": "aiQA",
                "answer": '"insert into MONTHLY_TRAN_MSG MTM_PARTY_NO, MTM_SEND, MTM_PRODUCT_TYPE, MTM_PARTY_NAME, MTM_CREATE_TIME, MTM_UPDATE_TIME, MTM_remark1, MTM_remark2, #{partyNo,jdbcType=VARCHAR}, #{send,jdbcType=VARCHAR}, #{productType,jdbcType=VARCHAR}, #{partyName,jdbcType=VARCHAR}, #{createTime,jdbcType=TIMESTAMP}, #{updateTime,jdbcType=TIMESTAMP}, #{remark1,jdbcType=VARCHAR}, #{remark2,jdbcType=VARCHAR}"'
            },
            "RSP_HEAD": {}
        }
    },
]

# 测试ModelClient的解析方法
try:
    from sql_ai_analyzer.ai_integration.model_client import ModelClient
    
    # 创建模拟的配置管理器
    class MockConfigManager:
        def get_ai_model_config(self):
            return {
                'api_url': 'http://test.com',
                'api_key': 'test',
                'timeout': 30,
                'max_retries': 3
            }
    
    # 创建简单的logger
    import logging
    logger = logging.getLogger('test')
    logger.setLevel(logging.WARNING)
    
    # 创建ModelClient实例
    config_manager = MockConfigManager()
    model_client = ModelClient(config_manager, logger)
    
    print("1. 测试清理提取的SQL方法 (_clean_extracted_sql):")
    test_sql = 'insert into MONTHLY_TRAN_MSG (MTM_PARTY_NO, MTM_SEND) VALUES (#{value1}, #{value2})'
    cleaned = model_client._clean_extracted_sql(test_sql)
    print(f"   原始SQL: {test_sql}")
    print(f"   清理后: {cleaned}")
    print(f"   括号是否保留: (原始={test_sql.count('(')}, 清理后={cleaned.count('(')})")
    print()
    
    print("2. 测试从响应中提取处理后的SQL (_extract_processed_sql_from_response):")
    for i, response_data in enumerate(test_responses, 1):
        print(f"\n   测试情况 {i}:")
        original_sql = 'insert into MONTHLY_TRAN_MSG (col1, col2) VALUES (val1, val2)'
        extracted_sql = model_client._extract_processed_sql_from_response(response_data, original_sql)
        print(f"     提取的SQL: {extracted_sql[:100] if extracted_sql else 'None'}")
        if extracted_sql:
            print(f"     括号数量: (={extracted_sql.count('(')}, )={extracted_sql.count(')')}")
            print(f"     是否包含VALUES: {'VALUES' in extracted_sql.upper()}")
    
    print("\n3. 测试安全解析大模型响应文本 (_safe_parse_llm_response_text):")
    # 测试各种可能的问题响应
    problem_responses = [
        # 响应1: 包含括号的SQL在answer中
        '{"raw_response": {"RSP_BODY": {"answer": "insert into MONTHLY_TRAN_MSG (MTM_PARTY_NO, MTM_SEND) VALUES (\\"value1\\", \\"value2\\")"}}}',
        
        # 响应2: 没有括号的SQL
        '{"raw_response": {"RSP_BODY": {"answer": "insert into MONTHLY_TRAN_MSG MTM_PARTY_NO, MTM_SEND VALUES \\"value1\\", \\"value2\\""}}}',
        
        # 响应3: 双重引号问题
        '{"raw_response": {"RSP_BODY": {"answer": ""insert into MONTHLY_TRAN_MSG (MTM_PARTY_NO, MTM_SEND) VALUES (\\"value1\\", \\"value2\\")""}}}',
    ]
    
    for i, response_text in enumerate(problem_responses, 1):
        print(f"\n   问题响应 {i}:")
        print(f"     响应文本: {response_text[:100]}...")
        try:
            parsed = model_client._safe_parse_llm_response_text(response_text)
            print(f"     解析结果类型: {type(parsed)}")
            if isinstance(parsed, dict):
                # 尝试提取SQL
                answer_sql = None
                if 'raw_response' in parsed and 'RSP_BODY' in parsed['raw_response']:
                    answer_sql = parsed['raw_response']['RSP_BODY'].get('answer', '')
                elif 'RSP_BODY' in parsed:
                    answer_sql = parsed['RSP_BODY'].get('answer', '')
                
                if answer_sql:
                    print(f"     提取的answer: {answer_sql[:100]}...")
                    print(f"     括号数量: (={answer_sql.count('(')}, )={answer_sql.count(')')}")
        except Exception as e:
            print(f"     解析失败: {e}")
    
    print("\n4. 测试深度清理响应文本 (_deep_clean_response_text):")
    problematic_texts = [
        '""{"raw_response": {"RSP_BODY": {"answer": "insert into MONTHLY_TRAN_MSG (col1, col2) VALUES (val1, val2)"}}}"',
        '"{\\"raw_response\\": {\\"RSP_BODY\\": {\\"answer\\": \\"insert into MONTHLY_TRAN_MSG (col1, col2) VALUES (val1, val2)\\"}}}"',
        '{"raw_response": {"RSP_BODY": {"answer": ""insert into MONTHLY_TRAN_MSG (col1, col2) VALUES (val1, val2)""}}}',
    ]
    
    for i, text in enumerate(problematic_texts, 1):
        print(f"\n   问题文本 {i}:")
        print(f"     原始: {text[:80]}...")
        cleaned = model_client._deep_clean_response_text(text)
        print(f"     清理后: {cleaned[:80]}...")
        # 尝试解析
        try:
            parsed = json.loads(cleaned)
            print(f"     可解析为JSON: 是")
            # 提取SQL
            if isinstance(parsed, dict):
                answer = parsed.get('raw_response', {}).get('RSP_BODY', {}).get('answer', '')
                if not answer and 'RSP_BODY' in parsed:
                    answer = parsed['RSP_BODY'].get('answer', '')
                print(f"     提取的SQL: {answer[:80] if answer else '无'}")
                if answer:
                    print(f"     括号: (={answer.count('(')}, )={answer.count(')')}")
        except:
            print(f"     可解析为JSON: 否")
    
    print("\n5. 测试修复常见格式问题 (_fix_common_format_issues):")
    problematic_jsons = [
        '{"answer":""{"sql":"insert into test (col1) values (val1)"}"}',
        '{"answer":"{\\"sql\\":\\"insert into test (col1) values (val1)\\"}"}',
    ]
    
    for i, json_text in enumerate(problematic_jsons, 1):
        print(f"\n   问题JSON {i}:")
        print(f"     原始: {json_text}")
        fixed = model_client._fix_common_format_issues(json_text)
        print(f"     修复后: {fixed}")
        try:
            parsed = json.loads(fixed)
            print(f"     可解析: 是")
            answer = parsed.get('answer', '')
            if answer:
                print(f"     answer: {answer[:80]}...")
                print(f"     括号: (={answer.count('(')}, )={answer.count(')')}")
        except Exception as e:
            print(f"     可解析: 否 ({e})")
    
except Exception as e:
    print(f"测试失败: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("测试完成")
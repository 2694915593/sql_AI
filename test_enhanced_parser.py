#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试增强后的解析器是否能正确处理用户提供的stripped字段
"""

import json
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_integration.model_client import ModelClient
from utils.logger import get_logger

class MockConfigManager:
    """模拟配置管理器"""
    def __init__(self):
        self.config = {
            'ai_model': {
                'api_url': 'http://mock-api',
                'api_key': 'mock-key',
                'timeout': 30,
                'max_retries': 3
            }
        }
    
    def get_ai_model_config(self):
        return self.config.get('ai_model', {})

def test_stripped_parser():
    """测试解析用户提供的stripped字段"""
    print("测试增强后的解析器")
    print("=" * 80)
    
    # 创建日志器
    logger = get_logger('test_parser')
    
    # 创建ModelClient实例
    config_manager = MockConfigManager()
    client = ModelClient(config_manager, logger)
    
    # 用户提供的stripped字符串（完整版本）
    stripped_str = '''{"RSP_BODY":{"head":{},"TRAN_PROCESS":"aiQA","answer":"\"{\\n  \\\"sql_type\\\": \\\"数据操作\\\",\\n  \\\"rule_analysis\\\": {\\n    \\\"建表规则\\\": {\\n      \\\"涉及历史表\\\": false,\\n      \\\"评估完全\\\": false,\\n      \\\"主键检查\\\": \\\"未通过\\\",\\n      \\\"索引检查\\\": \\\"未通过\\\",\\n      \\\"数据量评估\\\": \\\"合理\\\",\\n      \\\"注释检查\\\": \\\"不完整\\\",\\n      \\\"字段类型检查\\\": \\\"合理\\\"\\n    },\\n    \\\"表结构变更规则\\\": {\\n      \\\"涉及历史表\\\": false,\\n      \\\"评估完全\\\": false,\\n      \\\"影响范围评估\\\": \\\"不完整\\\",\\n      \\\"联机影响评估\\\": \\\"合理\\\",\\n      \\\"注释检查\\\": \\\"不完整\\\"\\n    },\\n    \\\"索引规则\\\": {\\n      \\\"索引冗余检查\\\": \\\"无冗余\\\",\\n      \\\"索引总数\\\": 0,\\n      \\\"索引设计合理性\\\": \\\"不合理\\\",\\n      \\\"执行计划分析\\\": \\\"无\\\"\\n    },\\n    \\\"数据量规则\\\": {\\n      \\\"数据量级别\\\": \\\"十万以下\\\",\\n      \\\"SQL耗时评估\\\": \\\"毫秒级\\\",\\n      \\\"备份策略\\\": \\\"无\\\",\\n      \\\"数据核对\\\": \\\"未核对\\\"\\n    }\\n  },\\n  \\\"risk_assessment\\\": {\\n    \\\"高风险问题\\\": [],\\n    \\\"中风险问题\\\": [\\\"表无主键和索引，可能影响查询性能\\\", \\\"未进行数据核对，可能导致数据不一致\\\"],\\n    \\\"低风险问题\\\": [\\\"表和字段注释不完整\\\", \\\"未提供备份策略\\\"]\\n  },\\n  \\\"improvement_suggestions\\\": [\\\"为表添加主键和必要的索引\\\", \\\"完善表和字段的注释\\\", \\\"制定数据核对流程\\\", \\\"考虑数据备份策略\\\"],\\n  \\\"overall_score\\\": 7,\\n  \\\"summary\\\": \\\"该SQL语句为数据插入操作，当前表无主键和索引，这可能会影响未来的查询性能。此外，表和字段的注释不完整，缺少数据核对和备份策略。建议改进上述方面以提高系统的稳定性和可维护性。\\\"\\n}\"","prompt":"prompt=SQL语句..."},"RSP_HEAD":{"TRAN_SUCCESS":"1","TRACE_NO":"SDSS118-38-115-7221128146"}}'''
    
    print(f"原始字符串长度: {len(stripped_str)}")
    print(f"前200字符: {stripped_str[:200]}")
    print()
    
    # 测试_safe_parse_llm_response_text方法
    print("测试_safe_parse_llm_response_text方法:")
    try:
        result = client._safe_parse_llm_response_text(stripped_str)
        print("✅ 解析成功!")
        print(f"解析结果类型: {type(result)}")
        
        # 检查解析结果
        if isinstance(result, dict):
            print(f"解析结果键: {list(result.keys())}")
            
            # 检查RSP_BODY
            if 'RSP_BODY' in result:
                rsp_body = result['RSP_BODY']
                print(f"RSP_BODY字段: {list(rsp_body.keys())}")
                
                # 检查answer字段
                if 'answer' in rsp_body:
                    answer = rsp_body['answer']
                    print(f"answer字段类型: {type(answer)}")
                    
                    # 如果answer是字符串，尝试进一步解析
                    if isinstance(answer, str):
                        print(f"answer字段长度: {len(answer)}")
                        print(f"answer前100字符: {answer[:100]}")
                    elif isinstance(answer, dict):
                        print("✅ answer字段已经是字典!")
                        print(f"SQL类型: {answer.get('sql_type')}")
                        print(f"综合评分: {answer.get('overall_score')}")
                        print(f"改进建议数量: {len(answer.get('improvement_suggestions', []))}")
                
                # 检查TRAN_PROCESS
                if 'TRAN_PROCESS' in rsp_body:
                    print(f"TRAN_PROCESS: {rsp_body['TRAN_PROCESS']}")
            
            # 检查RSP_HEAD
            if 'RSP_HEAD' in result:
                rsp_head = result['RSP_HEAD']
                print(f"TRAN_SUCCESS: {rsp_head.get('TRAN_SUCCESS')}")
                print(f"TRACE_NO: {rsp_head.get('TRACE_NO')}")
        
    except Exception as e:
        print(f"❌ 解析失败: {e}")
        import traceback
        traceback.print_exc()
    
    print()
    
    # 测试_parse_answer_from_dict方法
    print("测试_parse_answer_from_dict方法:")
    try:
        # 先尝试直接解析
        parsed_data = json.loads(stripped_str)
        print("✅ 直接JSON解析成功")
        
        # 测试_parse_answer_from_dict
        answer_data = client._parse_answer_from_dict(parsed_data)
        if answer_data:
            print("✅ _parse_answer_from_dict解析成功")
            print(f"SQL类型: {answer_data.get('sql_type')}")
            print(f"综合评分: {answer_data.get('overall_score')}")
            
            # 提取详细信息
            rule_analysis = answer_data.get('rule_analysis', {})
            if rule_analysis:
                print(f"\n规则分析:")
                for rule_type, rules in rule_analysis.items():
                    if isinstance(rules, dict):
                        print(f"  {rule_type}:")
                        for key, value in rules.items():
                            print(f"    - {key}: {value}")
            
            risk_assessment = answer_data.get('risk_assessment', {})
            if risk_assessment:
                print(f"\n风险评估:")
                for risk_level, issues in risk_assessment.items():
                    if isinstance(issues, list):
                        print(f"  {risk_level}: {len(issues)} 个问题")
                        for i, issue in enumerate(issues[:3], 1):
                            print(f"    {i}. {issue}")
            
            suggestions = answer_data.get('improvement_suggestions', [])
            if suggestions:
                print(f"\n改进建议 ({len(suggestions)} 条):")
                for i, suggestion in enumerate(suggestions, 1):
                    print(f"  {i}. {suggestion}")
            
            summary = answer_data.get('summary', '')
            if summary:
                print(f"\n总结 (前150字符):")
                print(f"  {summary[:150]}...")
        else:
            print("❌ _parse_answer_from_dict返回None")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
    
    print()
    
    # 测试多层清理方法
    print("测试_deep_clean_response_text方法:")
    try:
        cleaned = client._deep_clean_response_text(stripped_str)
        print(f"清理后长度: {len(cleaned)}")
        print(f"清理后前200字符: {cleaned[:200]}")
        
        # 尝试解析清理后的文本
        try:
            data = json.loads(cleaned)
            print("✅ 清理后JSON解析成功")
        except Exception as e:
            print(f"❌ 清理后JSON解析失败: {e}")
            
    except Exception as e:
        print(f"❌ 清理失败: {e}")
    
    print()
    
    # 测试修复格式问题方法
    print("测试_fix_common_format_issues方法:")
    try:
        fixed = client._fix_common_format_issues(stripped_str)
        print(f"修复后长度: {len(fixed)}")
        print(f"修复后前200字符: {fixed[:200]}")
        
        # 检查是否修复了双重引号问题
        if '""{' in stripped_str and '""{' not in fixed:
            print("✅ 修复了双重引号问题")
        else:
            print("❌ 未修复双重引号问题")
            
    except Exception as e:
        print(f"❌ 修复失败: {e}")

def test_simplified_case():
    """测试简化案例"""
    print("\n" + "=" * 80)
    print("测试简化案例")
    print("=" * 80)
    
    # 创建日志器
    logger = get_logger('test_simple')
    
    # 创建ModelClient实例
    config_manager = MockConfigManager()
    client = ModelClient(config_manager, logger)
    
    # 简化的测试案例
    simple_case = '''{"success": true, "raw_response": {"RSP_BODY": {"head": {}, "TRAN_PROCESS": "aiQA", "answer": "{\\"sql_type\\": \\"数据操作\\", \\"overall_score\\": 7}"}, "RSP_HEAD": {"TRAN_SUCCESS": "1", "TRACE_NO": "test123"}}}'''
    
    print(f"简化案例长度: {len(simple_case)}")
    print(f"前100字符: {simple_case[:100]}")
    
    try:
        result = client._safe_parse_llm_response_text(simple_case)
        print("✅ 简化案例解析成功")
        print(f"解析结果类型: {type(result)}")
        
        if isinstance(result, dict):
            # 检查是否有answer数据
            if 'raw_response' in result:
                raw_response = result['raw_response']
                if 'RSP_BODY' in raw_response:
                    answer = raw_response['RSP_BODY'].get('answer')
                    if isinstance(answer, dict):
                        print(f"SQL类型: {answer.get('sql_type')}")
                        print(f"综合评分: {answer.get('overall_score')}")
                    elif isinstance(answer, str):
                        print(f"answer字段是字符串: {answer[:50]}...")
            else:
                # 可能直接返回answer数据
                if 'sql_type' in result:
                    print(f"SQL类型: {result.get('sql_type')}")
                    print(f"综合评分: {result.get('overall_score')}")
                    
    except Exception as e:
        print(f"❌ 简化案例解析失败: {e}")
        import traceback
        traceback.print_exc()

def main():
    """主函数"""
    print("测试增强后的解析器")
    print("=" * 80)
    
    # 测试完整stripped字段
    test_stripped_parser()
    
    # 测试简化案例
    test_simplified_case()
    
    print("\n" + "=" * 80)
    print("测试完成")
    print("=" * 80)

if __name__ == '__main__':
    main()
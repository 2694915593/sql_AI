#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试API响应解析功能
"""

import json
from ai_integration.model_client import ModelClient
from config.config_manager import ConfigManager

def test_response_parsing():
    """测试响应解析"""
    print("测试API响应解析功能")
    print("=" * 80)
    
    try:
        # 加载配置
        config = ConfigManager('config/config.ini')
        
        # 创建模型客户端
        client = ModelClient(config)
        
        # 模拟用户提供的响应数据
        mock_response_data = {
            "success": True,
            "raw_response": {
                "RSP_BODY": {
                    "head": {},
                    "TRAN_PROCESS": "aiQA",
                    "answer": '"{\\n  \\"sql_type\\": \\"数据操作\\",\\n  \\"rule_analysis\\": {\\n    \\"建表规则\\": {\\n      \\"涉及历史表\\": false,\\n      \\"评估完全\\": false,\\n      \\"主键检查\\": \\"未通过\\",\\n      \\"索引检查\\": \\"未通过\\",\\n      \\"数据量评估\\": \\"合理\\",\\n      \\"注释检查\\": \\"不完整\\",\\n      \\"字段类型检查\\": \\"合理\\"\\n    },\\n    \\"表结构变更规则\\": {\\n      \\"涉及历史表\\": false,\\n      \\"评估完全\\": false,\\n      \\"影响范围评估\\": \\"不完整\\",\\n      \\"联机影响评估\\": \\"合理\\",\\n      \\"注释检查\\": \\"不完整\\"\\n    },\\n    \\"索引规则\\": {\\n      \\"索引冗余检查\\": \\"无冗余\\",\\n      \\"索引总数\\": 0,\\n      \\"索引设计合理性\\": \\"不合理\\",\\n      \\"执行计划分析\\": \\"无\\"\\n    },\\n    \\"数据量规则\\": {\\n      \\"数据量级别\\": \\"十万以下\\",\\n      \\"SQL耗时评估\\": \\"毫秒级\\",\\n      \\"备份策略\\": \\"无\\",\\n      \\"数据核对\\": \\"未核对\\"\\n    }\\n  },\\n  \\"risk_assessment\\": {\\n    \\"高风险问题\\": [\\"表缺少主键，可能导致数据重复或完整性问题\\"],\\n    \\"中风险问题\\": [\\"表无索引，可能影响查询性能\\", \\"未进行数据核对，可能导致数据错误\\"],\\n    \\"低风险问题\\": [\\"表和字段缺少注释，不利于维护\\"]\\n  },\\n  \\"improvement_suggestions\\": [\\"为表添加主键，确保数据唯一性和完整性\\", \\"根据业务需求添加合适的索引，提高查询性能\\", \\"为表和字段添加注释，便于后期维护\\", \\"执行数据操作后进行数据核对，确保数据正确性\\"],\\n  \\"overall_score\\": 5,\\n  \\"summary\\": \\"SQL语句主要涉及数据操作，但存在缺少主键、无索引等问题，可能影响数据完整性和查询性能。建议按照上述建议进行优化，以提高系统的稳定性和可维护性。\\"\\n}"'
                },
                "RSP_HEAD": {
                    "TRAN_SUCCESS": "1",
                    "TRACE_NO": "SDSS118-38-115-1882355925"
                }
            },
            "analysis_result": {}
        }
        
        print("1. 测试JSON解析...")
        # 尝试直接解析answer字段
        answer_str = mock_response_data['raw_response']['RSP_BODY']['answer']
        print(f"原始answer字符串长度: {len(answer_str)}")
        print(f"前200字符: {answer_str[:200]}")
        
        # 检查字符串是否以引号开头和结尾
        print(f"字符串以引号开头: {answer_str.startswith('\"')}")
        print(f"字符串以引号结尾: {answer_str.endswith('\"')}")
        
        # 尝试解析
        try:
            parsed_data = json.loads(answer_str)
            print("✓ 直接解析成功")
            print(f"解析后的数据类型: {type(parsed_data)}")
            
            # 检查解析结果是否是字符串（双重引号的情况）
            if isinstance(parsed_data, str):
                print("解析结果是字符串，需要再次解析")
                print(f"解析后的字符串长度: {len(parsed_data)}")
                print(f"解析后的字符串前200字符: {parsed_data[:200]}")
                
                # 再次解析
                try:
                    parsed_data = json.loads(parsed_data)
                    print("✓ 二次解析成功")
                    print(f"二次解析后的数据类型: {type(parsed_data)}")
                    print(f"SQL类型: {parsed_data.get('sql_type', '未知')}")
                    print(f"综合评分: {parsed_data.get('overall_score', '未知')}")
                except json.JSONDecodeError as e2:
                    print(f"✗ 二次解析失败: {e2}")
            else:
                # 直接是字典
                print(f"SQL类型: {parsed_data.get('sql_type', '未知')}")
                print(f"综合评分: {parsed_data.get('overall_score', '未知')}")
                
        except json.JSONDecodeError as e:
            print(f"✗ 直接解析失败: {e}")
            
            # 尝试清理后解析
            print("\n2. 尝试清理后解析...")
            try:
                # 移除多余的转义字符
                cleaned_answer = answer_str.replace('\\n', '\n').replace('\\"', '"')
                # 如果字符串以引号开头和结尾，移除它们
                if cleaned_answer.startswith('"') and cleaned_answer.endswith('"'):
                    cleaned_answer = cleaned_answer[1:-1]
                
                print(f"清理后字符串长度: {len(cleaned_answer)}")
                print(f"前200字符: {cleaned_answer[:200]}")
                
                parsed_data = json.loads(cleaned_answer)
                print("✓ 清理后解析成功")
                print(f"解析后的数据类型: {type(parsed_data)}")
                
                # 检查是否需要二次解析
                if isinstance(parsed_data, str):
                    print("解析结果是字符串，需要再次解析")
                    parsed_data = json.loads(parsed_data)
                    print("✓ 二次解析成功")
                    print(f"二次解析后的数据类型: {type(parsed_data)}")
                
                print(f"SQL类型: {parsed_data.get('sql_type', '未知')}")
                print(f"综合评分: {parsed_data.get('overall_score', '未知')}")
                
            except json.JSONDecodeError as e2:
                print(f"✗ 清理后解析也失败: {e2}")
        
        # 测试ModelClient的解析方法
        print("\n3. 测试ModelClient._parse_response方法...")
        
        # 创建一个模拟的requests.Response对象
        class MockResponse:
            def __init__(self, text):
                self.text = text
        
        # 将mock_response_data转换为JSON字符串
        response_text = json.dumps(mock_response_data)
        mock_response = MockResponse(response_text)
        
        try:
            result = client._parse_response(mock_response)
            print("✓ ModelClient解析成功")
            print(f"解析结果success: {result.get('success')}")
            print(f"SQL类型: {result.get('sql_type', '未知')}")
            print(f"综合评分: {result.get('score', '未知')}")
            print(f"建议数量: {len(result.get('suggestions', []))}")
            
            # 检查解析的详细内容
            if result.get('analysis_result'):
                analysis = result['analysis_result']
                print(f"\n解析的详细内容:")
                print(f"  - sql_type: {analysis.get('sql_type')}")
                print(f"  - overall_score: {analysis.get('overall_score')}")
                print(f"  - 高风险问题: {len(analysis.get('risk_assessment', {}).get('高风险问题', []))}个")
                print(f"  - 改进建议: {len(analysis.get('improvement_suggestions', []))}个")
            
        except Exception as e:
            print(f"✗ ModelClient解析失败: {e}")
            import traceback
            traceback.print_exc()
        
        print("\n" + "=" * 80)
        print("测试完成")
        
    except Exception as e:
        print(f"测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_response_parsing()
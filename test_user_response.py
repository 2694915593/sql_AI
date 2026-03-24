#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用用户提供的实际返回报文测试
"""

import json
from ai_integration.model_client import ModelClient
from config.config_manager import ConfigManager

def test_user_response():
    """测试用户提供的实际返回报文"""
    print("使用用户提供的实际返回报文测试")
    print("=" * 80)
    
    try:
        # 加载配置
        config = ConfigManager('config/config.ini')
        
        # 创建模型客户端
        client = ModelClient(config)
        
        # 用户提供的实际返回报文（从之前的反馈中提取）
        user_response_data = {
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
        
        print("1. 直接测试JSON解析...")
        answer_str = user_response_data['raw_response']['RSP_BODY']['answer']
        print(f"answer字符串长度: {len(answer_str)}")
        print(f"前100字符: {answer_str[:100]}")
        
        # 尝试解析
        try:
            # 第一次解析
            parsed1 = json.loads(answer_str)
            print(f"第一次解析结果类型: {type(parsed1)}")
            
            if isinstance(parsed1, str):
                print("第一次解析结果是字符串，需要第二次解析")
                # 第二次解析
                parsed2 = json.loads(parsed1)
                print(f"第二次解析结果类型: {type(parsed2)}")
                print(f"SQL类型: {parsed2.get('sql_type')}")
                print(f"综合评分: {parsed2.get('overall_score')}")
                print(f"改进建议数量: {len(parsed2.get('improvement_suggestions', []))}")
            else:
                print(f"SQL类型: {parsed1.get('sql_type')}")
                print(f"综合评分: {parsed1.get('overall_score')}")
                
        except json.JSONDecodeError as e:
            print(f"JSON解析失败: {e}")
        
        print("\n2. 测试ModelClient._parse_response方法...")
        
        # 创建一个模拟的requests.Response对象
        class MockResponse:
            def __init__(self, text):
                self.text = text
        
        # 将user_response_data转换为JSON字符串
        response_text = json.dumps(user_response_data)
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
                
                # 打印具体建议
                suggestions = analysis.get('improvement_suggestions', [])
                if suggestions:
                    print(f"\n具体改进建议:")
                    for i, suggestion in enumerate(suggestions, 1):
                        print(f"  {i}. {suggestion}")
            
        except Exception as e:
            print(f"✗ ModelClient解析失败: {e}")
            import traceback
            traceback.print_exc()
        
        print("\n3. 测试完整的analyze_sql方法...")
        
        # 创建一个模拟的请求数据
        request_data = {
            "sql_statement": "INSERT INTO ecdcdb.pd_errcode (PEC_ERRCODE, PEC_LANGUAGE, PEC_SHOWMSG, PEC_INNERMSG, PEC_CLASS, PEC_LASTUPDATE) VALUES('20070004AC0010', 'zh_CN', '命中金融惩戒名单，终止交易', '命中金融惩戒名单，终止交易', '1', '2024-10-18 18:55:53.615353');",
            "tables": [
                {
                    "table_name": "pd_errcode",
                    "row_count": 212,
                    "is_large_table": False,
                    "columns": [
                        {"name": "PEC_ERRCODE", "type": "char", "nullable": False},
                        {"name": "PEC_LANGUAGE", "type": "varchar", "nullable": False},
                        {"name": "PEC_SHOWMSG", "type": "varchar", "nullable": True},
                        {"name": "PEC_INNERMSG", "type": "varchar", "nullable": True},
                        {"name": "PEC_CLASS", "type": "varchar", "nullable": True}
                    ],
                    "indexes": [],
                    "ddl": "CREATE TABLE pd_errcode (PEC_ERRCODE char(14) NOT NULL, PEC_LANGUAGE varchar(10) NOT NULL, PEC_SHOWMSG varchar(200), PEC_INNERMSG varchar(200), PEC_CLASS varchar(6), PEC_LASTUPDATE timestamp(6) NOT NULL DEFAULT 'CURRENT_TIMESTAMP')"
                }
            ],
            "db_alias": "ECDC_SQL_SHELL_CTM"
        }
        
        print(f"请求数据:")
        print(f"  - SQL: {request_data['sql_statement'][:50]}...")
        print(f"  - 表数量: {len(request_data['tables'])}")
        print(f"  - 数据库: {request_data['db_alias']}")
        
        # 由于我们无法实际调用API，这里测试构建请求负载
        print("\n4. 测试构建请求负载...")
        try:
            payload = client._build_request_payload(request_data)
            print(f"✓ 构建请求负载成功")
            print(f"  - prompt长度: {len(payload.get('prompt', ''))}")
            print(f"  - prompt前100字符: {payload.get('prompt', '')[:100]}...")
        except Exception as e:
            print(f"✗ 构建请求负载失败: {e}")
        
        print("\n" + "=" * 80)
        print("测试完成")
        
    except Exception as e:
        print(f"测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_user_response()
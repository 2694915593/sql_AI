#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用用户提供的具体模拟返回报文进行测试
"""

import json
from ai_integration.model_client import ModelClient
from config.config_manager import ConfigManager

def test_specific_response():
    """测试用户提供的具体模拟返回报文"""
    print("使用用户提供的具体模拟返回报文进行测试")
    print("=" * 80)
    
    try:
        # 加载配置
        config = ConfigManager('config/config.ini')
        
        # 创建模型客户端
        client = ModelClient(config)
        
        # 用户提供的具体模拟返回报文
        user_response_data = {
            'success': True,
            'raw_response': {
                'RSP_BODY': {
                    'head': {},
                    'TRAN_PROCESS': 'aiQA',
                    'answer': '"{\\n  \\"sql_type\\": \\"数据操作\\",\\n  \\"rule_analysis\\": {\\n    \\"建表规则\\": {\\n      \\"涉及历史表\\": false,\\n      \\"评估完全\\": false,\\n      \\"主键检查\\": \\"未通过\\",\\n      \\"索引检查\\": \\"未通过\\",\\n      \\"数据量评估\\": \\"合理\\",\\n      \\"注释检查\\": \\"不完整\\",\\n      \\"字段类型检查\\": \\"合理\\"\\n    },\\n    \\"表结构变更规则\\": {\\n      \\"涉及历史表\\": false,\\n      \\"评估完全\\": false,\\n      \\"影响范围评估\\": \\"不完整\\",\\n      \\"联机影响评估\\": \\"合理\\",\\n      \\"注释检查\\": \\"不完整\\"\\n    },\\n    \\"索引规则\\": {\\n      \\"索引冗余检查\\": \\"无冗余\\",\\n      \\"索引总数\\": 0,\\n      \\"索引设计合理性\\": \\"不合理\\",\\n      \\"执行计划分析\\": \\"无\\"\\n    },\\n    \\"数据量规则\\": {\\n      \\"数据量级别\\": \\"十万以下\\",\\n      \\"SQL耗时评估\\": \\"毫秒级\\",\\n      \\"备份策略\\": \\"无\\",\\n      \\"数据核对\\": \\"未核对\\"\\n    }\\n  },\\n  \\"risk_assessment\\": {\\n    \\"高风险问题\\": [\\"表缺少主键，可能导致数据重复或完整性问题\\"],\\n    \\"中风险问题\\": [\\"表无索引，可能影响查询性能\\", \\"未进行数据核对，可能导致数据错误\\"],\\n    \\"低风险问题\\": [\\"表和字段缺少注释，不利于维护\\"]\\n  },\\n  \\"improvement_suggestions\\": [\\"为表添加主键，确保数据唯一性和完整性\\", \\"根据业务需求添加合适的索引，提高查询性能\\", \\"为表和字段添加注释，便于后期维护\\", \\"执行数据操作后进行数据核对，确保数据正确性\\"],\\n  \\"overall_score\\": 5,\\n  \\"summary\\": \\"SQL语句主要涉及数据操作，但存在缺少主键、无索引等问题，可能影响数据完整性和查询性能。建议按照上述建议进行优化，以提高系统的稳定性和可维护性。\\"\\n}"',
                    'prompt': 'prompt=SQL语句：\nINSERT INTO ecdcdb.pd_errcode\r\n(PEC_ERRCODE, PEC_LANGUAGE, PEC_SHOWMSG, PEC_INNERMSG, PEC_CLASS, PEC_LASTUPDATE)\r\nVALUES(\'20070004AC0010\', \'zh_CN\', \'命中金融惩戒名单，终止交易\', \'命中金融惩戒名单，终止交易\', \'1\', \'2024-10-18 18:55:53.615353\');\r\n\n\n数据库：ECDC_SQL_SHELL_CTM\n\n涉及的表信息：\n\n表1：pd_errcode\n  - 行数：212\n  - 是否大表：否\n  - 列数：6\n  - 索引数：0\n  - DDL：\n    CREATE TABLE pd_errcode (PEC_ERRCODE char(14) NOT NULL, PEC_LANGUAGE varchar(10) NOT NULL, PEC_SHOWMSG varchar(200), PEC_INNERMSG varchar(200), PEC_CLASS varchar(6), PEC_LASTUPDATE timestamp(6) NOT NULL DEFAULT \'CURRENT_TIMESTAMP\')\n  - 列信息：\n    * PEC_ERRCODE (char) 非空\n    * PEC_LANGUAGE (varchar) 非空\n    * PEC_SHOWMSG (varchar) 可空\n    * PEC_INNERMSG (varchar) 可空\n    * PEC_CLASS (varchar) 可空\n    * ... 还有1列\n\n动态SQL示例（用于判断SQL注入漏洞）：\n请分析以下动态SQL示例是否存在SQL注入风险：\n- 动态插入示例：INSERT INTO users (username, password) VALUES (\'${username}\', \'${password}\')\n- 参数化插入示例：INSERT INTO users (username, password) VALUES (?, ?)\n- 字符串拼接示例：SELECT * FROM products WHERE name LIKE \'%${search_term}%\'\n- 数字类型注入示例：SELECT * FROM orders WHERE id = ${order_id}\n- 时间类型注入示例：SELECT * FROM logs WHERE create_time > \'${start_time}\'\n\nSQL执行计划：未提供\n请基于表结构和索引信息分析SQL执行效率\n\n请根据以下SQL评审规则进行分析：\n\n1. 建表规则：\n   • 是否涉及历史表\n   • 联机、定时、批量是否评估完全\n   • 主键/索引：必须有主键\n   • 联机查询：联机查询走索引或主键\n   • 数据量：表预期数据量做好评估，以应对后续业务调用\n   • 注释：表、字段有注释\n   • 数据量增长：上线后，一周内数据量预估，如表增长较快，需要说明清理或归档策略\n   • 分组分区：建表前考虑使用场景，访问量大数据量大的是否可以分组分区\n   • 字段类型：金额类型字段用decimal\n\n2. 表结构变更规则：\n   • 是否涉及历史表\n   • 联机、定时、批量是否评估完全\n   • 影响范围：对应表的联机、定时、批量评估完全\n   • 联机影响：对应表是否为热点表，表结构修改的时间点是否影响联机（热点表24点后再变更），执行表结构变更耗时\n   • 注释：变更后类型定义合理（如字段类型调整），必须写注释\n\n3. 新建/修改索引规则：\n   • 索引无冗余\n   • 执行后索引总数\n   • 索引添加前后耗时对比\n   • 是否热点表\n   • 更新表结构时间\n   • 索引个数：不超过5个，组合索引：列的个数控制在3个字段及以内，不能超过5个\n   • 索引设计：考虑索引字段的顺序：结合业务场景，是否合理，能建联合索引的不建单列索引\n   • 执行计划：新建/修改索引前后执行计划\n\n4. 数据量规则：\n   • 生产表数据量（是否十万、百万级以上）\n   • 影响范围：应用中与索引相关的sql执行耗时\n   • SQL耗时：秒级\n   • 插入、更新、删除数据\n   • 是否已核对生产数据\n   • 大数据量变更：对表数据大量删除、导入、更新，且影响联机交易，需立即执行analyze提升SQL性能（OB3x默认每日2:00定时合并），执行后一直需要手动执行\n   • 备份：删除数据较大时，及时备份\n   • 变更前后核对：核对生产数据，是否与预期变更一致\n   • SQL耗时：插入、更新、删除数据，建表，耗时：毫秒级(或无感知)\n\n请基于以上规则分析SQL语句，重点关注：\n1. SQL类型识别：判断是建表、表结构变更、索引操作还是数据操作\n2. 规则符合性检查：根据SQL类型检查对应的规则\n3. 风险评估：识别潜在的风险和问题\n4. 建议改进：提供具体的改进建议\n5. 综合评分：给出综合评分（0-10分）\n\n请严格按照以下JSON格式回复，不要包含任何其他内容：\n{\n  "sql_type": "建表/表结构变更/索引操作/数据操作/查询",\n  "rule_analysis": {\n    "建表规则": {\n      "涉及历史表": true/false,\n      "评估完全": true/false,\n      "主键检查": "通过/未通过",\n      "索引检查": "通过/未通过",\n      "数据量评估": "合理/不合理",\n      "注释检查": "完整/不完整",\n      "字段类型检查": "合理/不合理"\n    },\n    "表结构变更规则": {\n      "涉及历史表": true/false,\n      "评估完全": true/false,\n      "影响范围评估": "完整/不完整",\n      "联机影响评估": "合理/不合理",\n      "注释检查": "完整/不完整"\n    },\n    "索引规则": {\n      "索引冗余检查": "无冗余/有冗余",\n      "索引总数": 数字,\n      "索引设计合理性": "合理/不合理",\n      "执行计划分析": "有/无"\n    },\n    "数据量规则": {\n      "数据量级别": "十万以下/十万级/百万级/千万级以上",\n      "SQL耗时评估": "毫秒级/秒级/分钟级",\n      "备份策略": "有/无",\n      "数据核对": "已核对/未核对"\n    }\n  },\n  "risk_assessment": {\n    "高风险问题": ["问题1", "问题2"],\n    "中风险问题": ["问题1", "问题2"],\n    "低风险问题": ["问题1", "问题2"]\n  },\n  "improvement_suggestions": ["建议1", "建议2", "建议3"],\n  "overall_score": 0-10,\n  "summary": "综合分析总结"\n}\n\n注意：请只回复JSON格式的内容，不要包含任何解释性文字。'
                },
                'RSP_HEAD': {
                    'TRAN_SUCCESS': '1',
                    'TRACE_NO': 'SDSS118-38-115-1882355925'
                }
            },
            'analysis_result': {}
        }
        
        print("1. 原始响应数据结构分析...")
        print(f"响应数据包含的键: {list(user_response_data.keys())}")
        print(f"raw_response类型: {type(user_response_data['raw_response'])}")
        print(f"RSP_BODY类型: {type(user_response_data['raw_response']['RSP_BODY'])}")
        print(f"RSP_BODY包含的键: {list(user_response_data['raw_response']['RSP_BODY'].keys())}")
        
        print("\n2. answer字段分析...")
        answer_str = user_response_data['raw_response']['RSP_BODY']['answer']
        print(f"answer字符串长度: {len(answer_str)}")
        print(f"前200字符: {answer_str[:200]}")
        print(f"字符串以引号开头: {answer_str.startswith('\"')}")
        print(f"字符串以引号结尾: {answer_str.endswith('\"')}")
        
        print("\n3. 直接JSON解析测试...")
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
                
                # 打印详细内容
                print(f"\n解析的详细内容:")
                print(f"  - sql_type: {parsed2.get('sql_type')}")
                print(f"  - overall_score: {parsed2.get('overall_score')}")
                
                # 规则分析
                rule_analysis = parsed2.get('rule_analysis', {})
                if rule_analysis:
                    print(f"  - 规则分析:")
                    for rule_name, rule_data in rule_analysis.items():
                        if isinstance(rule_data, dict):
                            print(f"    * {rule_name}:")
                            for key, value in rule_data.items():
                                print(f"      - {key}: {value}")
                
                # 风险评估
                risk_assessment = parsed2.get('risk_assessment', {})
                if risk_assessment:
                    print(f"  - 风险评估:")
                    for risk_level, risks in risk_assessment.items():
                        if isinstance(risks, list):
                            print(f"    * {risk_level}: {len(risks)}个")
                            for i, risk in enumerate(risks, 1):
                                print(f"      {i}. {risk}")
                
                # 改进建议
                suggestions = parsed2.get('improvement_suggestions', [])
                if suggestions:
                    print(f"  - 改进建议 ({len(suggestions)}个):")
                    for i, suggestion in enumerate(suggestions, 1):
                        print(f"    {i}. {suggestion}")
                
                # 总结
                summary = parsed2.get('summary', '')
                if summary:
                    print(f"  - 总结: {summary}")
                    
            else:
                print(f"SQL类型: {parsed1.get('sql_type')}")
                print(f"综合评分: {parsed1.get('overall_score')}")
                
        except json.JSONDecodeError as e:
            print(f"JSON解析失败: {e}")
            import traceback
            traceback.print_exc()
        
        print("\n4. 测试ModelClient._parse_response方法...")
        
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
            
            # 打印完整的解析结果
            print(f"\n完整的解析结果:")
            print(json.dumps(result, ensure_ascii=False, indent=2))
            
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
        
        print("\n" + "=" * 80)
        print("测试完成")
        
    except Exception as e:
        print(f"测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_specific_response()
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试解析用户提供的stripped字段
"""

import json
import ast

def parse_stripped_string():
    """解析用户提供的stripped字段"""
    stripped_str = '''{"RSP_BODY":{"head":{},"TRAN_PROCESS":"aiQA","answer":"\"{\\n  \\\"sql_type\\\": \\\"数据操作\\\",\\n  \\\"rule_analysis\\\": {\\n    \\\"建表规则\\\": {\\n      \\\"涉及历史表\\\": false,\\n      \\\"评估完全\\\": false,\\n      \\\"主键检查\\\": \\\"未通过\\\",\\n      \\\"索引检查\\\": \\\"未通过\\\",\\n      \\\"数据量评估\\\": \\\"合理\\\",\\n      \\\"注释检查\\\": \\\"不完整\\\",\\n      \\\"字段类型检查\\\": \\\"合理\\\"\\n    },\\n    \\\"表结构变更规则\\\": {\\n      \\\"涉及历史表\\\": false,\\n      \\\"评估完全\\\": false,\\n      \\\"影响范围评估\\\": \\\"不完整\\\",\\n      \\\"联机影响评估\\\": \\\"合理\\\",\\n      \\\"注释检查\\\": \\\"不完整\\\"\\n    },\\n    \\\"索引规则\\\": {\\n      \\\"索引冗余检查\\\": \\\"无冗余\\\",\\n      \\\"索引总数\\\": 0,\\n      \\\"索引设计合理性\\\": \\\"不合理\\\",\\n      \\\"执行计划分析\\\": \\\"无\\\"\\n    },\\n    \\\"数据量规则\\\": {\\n      \\\"数据量级别\\\": \\\"十万以下\\\",\\n      \\\"SQL耗时评估\\\": \\\"毫秒级\\\",\\n      \\\"备份策略\\\": \\\"无\\\",\\n      \\\"数据核对\\\": \\\"未核对\\\"\\n    }\\n  },\\n  \\\"risk_assessment\\\": {\\n    \\\"高风险问题\\\": [],\\n    \\\"中风险问题\\\": [\\\"表无主键和索引，可能影响查询性能\\\", \\\"未进行数据核对，可能导致数据不一致\\\"],\\n    \\\"低风险问题\\\": [\\\"表和字段注释不完整\\\", \\\"未提供备份策略\\\"]\\n  },\\n  \\\"improvement_suggestions\\\": [\\\"为表添加主键和必要的索引\\\", \\\"完善表和字段的注释\\\", \\\"制定数据核对流程\\\", \\\"考虑数据备份策略\\\"],\\n  \\\"overall_score\\\": 7,\\n  \\\"summary\\\": \\\"该SQL语句为数据插入操作，当前表无主键和索引，这可能会影响未来的查询性能。此外，表和字段的注释不完整，缺少数据核对和备份策略。建议改进上述方面以提高系统的稳定性和可维护性。\\\"\\n}\"","prompt":"prompt=SQL语句：\nINSERT INTO ecdcdb.pd_errcode\r\n(PEC_ERRCODE, PEC_LANGUAGE, PEC_SHOWMSG, PEC_INNERMSG, PEC_CLASS, PEC_LASTUPDATE)\r\nVALUES('20070004AC0010', 'zh_CN', '命中金融惩戒名单，终止交易', '命中金融惩戒名单，终止交易', '1', '2024-10-18 18:55:53.615353');\r\n\n\nSQL元信息：\n- SQL ID：514\n- 项目ID：ECDC\n- 系统ID：ECDC_SQL_SHELL_CTM\n- 作者：zhao.ziqing\n- 文件名：V_003_BoCom07656151_CREAT_CLOUD_APP_INFO.sql\n- 操作类型：2\n\n数据库：ECDC_SQL_SHELL_CTM\n\n表名来源信息：\n- SQL解析表名：pd_errcode\n\n涉及的表信息：\n\n表1：pd_errcode\n  - 行数：212\n  - 是否大表：否\n  - 列数：6\n  - 索引数：0\n  - DDL：\n    CREATE TABLE pd_errcode (PEC_ERRCODE char(14) NOT NULL, PEC_LANGUAGE varchar(10) NOT NULL, PEC_SHOWMSG varchar(200), PEC_INNERMSG varchar(200), PEC_CLASS varchar(6), PEC_LASTUPDATE timestamp(6) NOT NULL DEFAULT 'CURRENT_TIMESTAMP')\n  - 表存在性：是\n  - 列信息：\n    * PEC_ERRCODE (char) 非空\n    * PEC_LANGUAGE (varchar) 非空\n    * PEC_SHOWMSG (varchar) 可空\n    * PEC_INNERMSG (varchar) 可空\n    * PEC_CLASS (varchar) 可空\n    * ... 还有1列\n\n动态SQL示例（用于判断SQL注入漏洞）：\n请分析以下动态SQL示例是否存在SQL注入风险：\n- 动态插入示例：INSERT INTO pd_errcode (PEC_ERRCODE, PEC_LANGUAGE) VALUES ('${value1}', '${value2}')\n- 参数化插入示例：INSERT INTO pd_errcode (PEC_ERRCODE, PEC_LANGUAGE) VALUES (?, ?)\n- 批量插入注入示例：INSERT INTO pd_errcode VALUES ('${value1}', '${value2}'), ('${value3}', '${value4}')\n- 字符串拼接示例：SELECT * FROM pd_errcode WHERE PEC_LANGUAGE LIKE '%${search_term}%'\n- 数字类型注入示例：SELECT * FROM pd_errcode WHERE PEC_ERRCODE = ${id}\n- 时间类型注入示例：SELECT * FROM pd_errcode WHERE created_at > '${start_time}'\n- 布尔盲注示例：SELECT * FROM pd_errcode WHERE PEC_ERRCODE = ${id} AND 1=1 -- 正常\n- 时间盲注示例：SELECT * FROM pd_errcode WHERE PEC_ERRCODE = ${id} AND SLEEP(5) -- 延迟执行\n- 报错注入示例：SELECT * FROM pd_errcode WHERE PEC_ERRCODE = ${id} AND EXTRACTVALUE(1, CONCAT(0x7e, (SELECT @@version), 0x7e))\n- \n防护建议：\n- 1. 使用参数化查询（Prepared Statements）\n- 2. 使用存储过程\n- 3. 输入验证和过滤\n- 4. 最小权限原则\n- 5. 使用ORM框架\n\nSQL执行计划分析：\nSQL执行计划分析：\n==================================================\n\n1. SQL类型分析：\n   • 类型：插入语句 (INSERT)\n   • 操作：数据写入\n   • 性能关注点：写入速度、锁竞争\n\n2. 涉及表分析：\n\n   表1：pd_errcode\n     • 数据量：212 行\n     • 是否大表：否\n     • 列数：6\n     • 索引数：0\n     • 索引：无索引（全表扫描风险）\n\n3. 执行计划预测：\n   • 预测：单行插入，性能较好\n   • 建议：批量插入时考虑使用事务\n\n4. 性能优化建议：\n   • 确保WHERE条件使用索引\n   • 避免SELECT *，只选择需要的列\n   • 考虑查询结果集大小\n   • 注意JOIN操作的性能\n   • 考虑使用EXPLAIN分析实际执行计划\n\n5. 执行风险评估：\n   • ✅ 风险较低\n\n==================================================\n注意：以上为基于元数据的预测分析，实际执行计划需通过EXPLAIN命令获取\n\n请根据以下SQL评审规则进行分析：\n\n1. 建表规则：\n   • 是否涉及历史表\n   • 联机、定时、批量是否评估完全\n   • 主键/索引：必须有主键\n   • 联机查询：联机查询走索引或主键\n   • 数据量：表预期数据量做好评估，以应对后续业务调用\n   • 注释：表、字段有注释\n   • 数据量增长：上线后，一周内数据量预估，如表增长较快，需要说明清理或归档策略\n   • 分组分区：建表前考虑使用场景，访问量大数据量大的是否可以分组分区\n   • 字段类型：金额类型字段用decimal\n\n2. 表结构变更规则：\n   • 是否涉及历史表\n   • 联机、定时、批量是否评估完全\n   • 影响范围：对应表的联机、定时、批量评估完全\n   • 联机影响：对应表是否为热点表，表结构修改的时间点是否影响联机（热点表24点后再变更），执行表结构变更耗时\n   • 注释：变更后类型定义合理（如字段类型调整），必须写注释\n\n3. 新建/修改索引规则：\n   • 索引无冗余\n   • 执行后索引总数\n   • 索引添加前后耗时对比\n   • 是否热点表\n   • 更新表结构时间\n   • 索引个数：不超过5个，组合索引：列的个数控制在3个字段及以内，不能超过5个\n   • 索引设计：考虑索引字段的顺序：结合业务场景，是否合理，能建联合索引的不建单列索引\n   • 执行计划：新建/修改索引前后执行计划\n\n4. 数据量规则：\n   • 生产表数据量（是否十万、百万级以上）\n   • 影响范围：应用中与索引相关的sql执行耗时\n   • SQL耗时：秒级\n   • 插入、更新、删除数据\n   • 是否已核对生产数据\n   • 大数据量变更：对表数据大量删除、导入、更新，且影响联机交易，需立即执行analyze提升SQL性能（OB3x默认每日2:00定时合并），执行后一直需要手动执行\n   • 备份：删除数据较大时，及时备份\n   • 变更前后核对：核对生产数据，是否与预期变更一致\n   • SQL耗时：插入、更新、删除数据，建表，耗时：毫秒级(或无感知)\n\n请基于以上规则分析SQL语句，重点关注：\n1. SQL类型识别：判断是建表、表结构变更、索引操作还是数据操作\n2. 规则符合性检查：根据SQL类型检查对应的规则\n3. 风险评估：识别潜在的风险和问题\n4. 建议改进：提供具体的改进建议\n5. 综合评分：给出综合评分（0-10分）\n\n请严格按照以下JSON格式回复，不要包含任何其他内容：\n{\n  \"sql_type\": \"建表/表结构变更/索引操作/数据操作/查询\",\n  \"rule_analysis\": {\n    \"建表规则\": {\n      \"涉及历史表\": true/false,\n      \"评估完全\": true/false,\n      \"主键检查\": \"通过/未通过\",\n      \"索引检查\": \"通过/未通过\",\n      \"数据量评估\": \"合理/不合理\",\n      \"注释检查\": \"完整/不完整\",\n      \"字段类型检查\": \"合理/不合理\"\n    },\n    \"表结构变更规则\": {\n      \"涉及历史表\": true/false,\n      \"评估完全\": true/false,\n      \"影响范围评估\": \"完整/不完整\",\n      \"联机影响评估\": \"合理/不合理\",\n      \"注释检查\": \"完整/不完整\"\n    },\n    \"索引规则\": {\n      \"索引冗余检查\": \"无冗余/有冗余\",\n      \"索引总数\": 数字,\n      \"索引设计合理性\": \"合理/不合理\",\n      \"执行计划分析\": \"有/无\"\n    },\n    \"数据量规则\": {\n      \"数据量级别\": \"十万以下/十万级/百万级/千万级以上\",\n      \"SQL耗时评估\": \"毫秒级/秒级/分钟级\",\n      \"备份策略\": \"有/无\",\n      \"数据核对\": \"已核对/未核对\"\n    }\n  },\n  \"risk_assessment\": {\n    \"高风险问题\": [\"问题1\", \"问题2\"],\n    \"中风险问题\": [\"问题1\", \"问题2\"],\n    \"低风险问题\": [\"问题1\", \"问题2\"]\n  },\n  \"improvement_suggestions\": [\"建议1\", \"建议2\", \"建议3\"],\n  \"overall_score\": 0-10,\n  \"summary\": \"综合分析总结\"\n}\n\n注意：请只回复JSON格式的内容，不要包含任何解释性文字。"},"RSP_HEAD":{"TRAN_SUCCESS":"1","TRACE_NO":"SDSS118-38-115-7221128146"}}'''
    
    print("=" * 80)
    print("测试解析stripped字符串")
    print("=" * 80)
    
    # 方法1: 直接JSON解析
    print("\n方法1: 直接JSON解析")
    try:
        data = json.loads(stripped_str)
        print("✅ 直接JSON解析成功")
        print(f"外层结构: {list(data.keys())}")
        print(f"RSP_BODY字段: {list(data.get('RSP_BODY', {}).keys())}")
        
        # 检查answer字段
        rsp_body = data.get('RSP_BODY', {})
        answer_str = rsp_body.get('answer', '')
        print(f"answer字段类型: {type(answer_str)}")
        print(f"answer字段前200字符: {answer_str[:200]}")
        
        # 尝试解析answer字段
        if answer_str:
            print("\n尝试解析answer字段:")
            # 清理answer字段 - 移除最外层的引号
            cleaned_answer = answer_str
            if cleaned_answer.startswith('"') and cleaned_answer.endswith('"'):
                cleaned_answer = cleaned_answer[1:-1]
            
            # 替换转义字符
            cleaned_answer = cleaned_answer.replace('\\n', '\n').replace('\\"', '"').replace('\\\\', '\\')
            print(f"清理后前200字符: {cleaned_answer[:200]}")
            
            try:
                answer_data = json.loads(cleaned_answer)
                print("✅ 成功解析answer字段中的JSON")
                print(f"SQL类型: {answer_data.get('sql_type')}")
                print(f"综合评分: {answer_data.get('overall_score')}")
                print(f"改进建议数量: {len(answer_data.get('improvement_suggestions', []))}")
                return data
            except json.JSONDecodeError as e:
                print(f"❌ 解析answer字段失败: {e}")
                print(f"尝试ast.literal_eval...")
                try:
                    answer_data = ast.literal_eval(cleaned_answer)
                    print("✅ 使用ast.literal_eval成功解析answer字段")
                    print(f"SQL类型: {answer_data.get('sql_type')}")
                    print(f"综合评分: {answer_data.get('overall_score')}")
                    return data
                except Exception as e2:
                    print(f"❌ ast.literal_eval也失败: {e2}")
        
        return data
    except json.JSONDecodeError as e:
        print(f"❌ 直接JSON解析失败: {e}")
    
    # 方法2: 使用ast.literal_eval
    print("\n方法2: 使用ast.literal_eval")
    try:
        data = ast.literal_eval(stripped_str)
        print("✅ ast.literal_eval解析成功")
        print(f"外层结构: {list(data.keys())}")
        return data
    except Exception as e:
        print(f"❌ ast.literal_eval解析失败: {e}")
    
    # 方法3: 手动清理后解析
    print("\n方法3: 手动清理后解析")
    try:
        # 先清理一些明显的转义问题
        cleaned = stripped_str.replace('\\n', '\n').replace('\\"', '"')
        # 处理双重转义
        cleaned = cleaned.replace('\\\\', '\\')
        
        # 尝试解析
        data = json.loads(cleaned)
        print("✅ 手动清理后JSON解析成功")
        return data
    except Exception as e:
        print(f"❌ 手动清理后解析失败: {e}")
    
    return None

def test_extract_answer_parser():
    """测试从answer字段中提取解析器"""
    print("\n" + "=" * 80)
    print("测试answer字段解析器")
    print("=" * 80)
    
    # 模拟answer字段的内容
    answer_str = '''"{\\n  \\"sql_type\\": \\"数据操作\\",\\n  \\"rule_analysis\\": {\\n    \\"建表规则\\": {\\n      \\"涉及历史表\\": false,\\n      \\"评估完全\\": false,\\n      \\"主键检查\\": \\"未通过\\",\\n      \\"索引检查\\": \\"未通过\\",\\n      \\"数据量评估\\": \\"合理\\",\\n      \\"注释检查\\": \\"不完整\\",\\n      \\"字段类型检查\\": \\"合理\\"\\n    },\\n    \\"表结构变更规则\\": {\\n      \\"涉及历史表\\": false,\\n      \\"评估完全\\": false,\\n      \\"影响范围评估\\": \\"不完整\\",\\n      \\"联机影响评估\\": \\"合理\\",\\n      \\"注释检查\\": \\"不完整\\"\\n    },\\n    \\"索引规则\\": {\\n      \\"索引冗余检查\\": \\"无冗余\\",\\n      \\"索引总数\\": 0,\\n      \\"索引设计合理性\\": \\"不合理\\",\\n      \\"执行计划分析\\": \\"无\\"\\n    },\\n    \\"数据量规则\\": {\\n      \\"数据量级别\\": \\"十万以下\\",\\n      \\"SQL耗时评估\\": \\"毫秒级\\",\\n      \\"备份策略\\": \\"无\\",\\n      \\"数据核对\\": \\"未核对\\"\\n    }\\n  },\\n  \\"risk_assessment\\": {\\n    \\"高风险问题\\": [],\\n    \\"中风险问题\\\": [\\"表无主键和索引，可能影响查询性能\\", \\"未进行数据核对，可能导致数据不一致\\"],\\n    \\"低风险问题\\": [\\"表和字段注释不完整\\", \\"未提供备份策略\\"]\\n  },\\n  \\"improvement_suggestions\\": [\\"为表添加主键和必要的索引\\", \\"完善表和字段的注释\\", \\"制定数据核对流程\\", \\"考虑数据备份策略\\"],\\n  \\"overall_score\\": 7,\\n  \\"summary\\": \\"该SQL语句为数据插入操作，当前表无主键和索引，这可能会影响未来的查询性能。此外，表和字段的注释不完整，缺少数据核对和备份策略。建议改进上述方面以提高系统的稳定性和可维护性。\\"\\n}"'''
    
    print(f"原始answer字符串长度: {len(answer_str)}")
    print(f"前100字符: {answer_str[:100]}")
    
    # 测试解析逻辑
    for i in range(3):
        print(f"\n第{i+1}次解析尝试:")
        try:
            # 如果是字符串，尝试解析
            current_str = answer_str
            
            # 如果以引号开头和结尾，去掉它们
            if current_str.startswith('"') and current_str.endswith('"'):
                current_str = current_str[1:-1]
                print(f"去掉外层引号后: {current_str[:50]}...")
            
            # 替换转义字符
            current_str = current_str.replace('\\n', '\n').replace('\\"', '"').replace('\\\\', '\\')
            print(f"替换转义字符后: {current_str[:50]}...")
            
            # 尝试解析
            data = json.loads(current_str)
            print(f"✅ 第{i+1}次解析成功!")
            print(f"SQL类型: {data.get('sql_type')}")
            print(f"综合评分: {data.get('overall_score')}")
            return data
        except json.JSONDecodeError as e:
            print(f"❌ 第{i+1}次解析失败: {e}")
            # 如果是字符串，继续尝试
            if isinstance(answer_str, str):
                answer_str = answer_str.replace('\\n', '\n').replace('\\"', '"')
                print(f"重新处理转义字符后前50字符: {answer_str[:50]}")
    
    return None

def main():
    """主函数"""
    print("测试解析stripped字段")
    print("=" * 80)
    
    # 测试完整stripped字符串解析
    data = parse_stripped_string()
    
    if data:
        print("\n✅ 解析成功!")
        print("\n提取的关键信息:")
        
        rsp_body = data.get('RSP_BODY', {})
        rsp_head = data.get('RSP_HEAD', {})
        
        print(f"TRAN_PROCESS: {rsp_body.get('TRAN_PROCESS')}")
        print(f"TRAN_SUCCESS: {rsp_head.get('TRAN_SUCCESS')}")
        print(f"TRACE_NO: {rsp_head.get('TRACE_NO')}")
        
        # 尝试提取answer字段数据
        answer_str = rsp_body.get('answer', '')
        if answer_str:
            print("\n尝试最终解析answer字段:")
            # 最简化的解析方法
            try:
                # 去掉最外层引号
                if answer_str.startswith('"') and answer_str.endswith('"'):
                    answer_str = answer_str[1:-1]
                
                # 处理转义字符
                answer_str = answer_str.replace('\\n', '\n').replace('\\"', '"').replace('\\\\', '\\')
                
                # 尝试解析
                answer_data = json.loads(answer_str)
                print("✅ 最终解析成功!")
                print(f"SQL类型: {answer_data.get('sql_type')}")
                print(f"综合评分: {answer_data.get('overall_score')}")
                
                # 提取规则分析
                rule_analysis = answer_data.get('rule_analysis', {})
                if rule_analysis:
                    print(f"\n规则分析:")
                    for rule_type, rules in rule_analysis.items():
                        if isinstance(rules, dict):
                            print(f"  {rule_type}:")
                            for key, value in rules.items():
                                print(f"    - {key}: {value}")
                
                # 提取风险评估
                risk_assessment = answer_data.get('risk_assessment', {})
                if risk_assessment:
                    print(f"\n风险评估:")
                    for risk_level, issues in risk_assessment.items():
                        if isinstance(issues, list):
                            print(f"  {risk_level}: {len(issues)} 个问题")
                            for issue in issues[:2]:
                                print(f"    - {issue}")
                
                # 提取改进建议
                suggestions = answer_data.get('improvement_suggestions', [])
                if suggestions:
                    print(f"\n改进建议 ({len(suggestions)} 条):")
                    for i, suggestion in enumerate(suggestions, 1):
                        print(f"  {i}. {suggestion}")
                
                # 提取总结
                summary = answer_data.get('summary', '')
                if summary:
                    print(f"\n总结 (前100字符):")
                    print(f"  {summary[:100]}...")
                
            except Exception as e:
                print(f"❌ 最终解析失败: {e}")
    
    # 测试answer字段解析器
    test_extract_answer_parser()

if __name__ == '__main__':
    main()
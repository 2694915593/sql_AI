import ast
import json
import re
from typing import Dict, Any

def clean_and_parse_response_text(response_text: str) -> Dict[str, Any]:
    """
    清理并解析响应文本，处理各种格式问题
    """
    try:
        # 第一步：清理响应文本，修复可能的截断问题
        # 确保字符串以完整的字典结构结束
        if not response_text.endswith('}'):
            # 尝试找到最后一个完整的字典结束符
            last_bracket = response_text.rfind('}')
            if last_bracket > 0:
                response_text = response_text[:last_bracket + 1]
            else:
                # 如果连}都找不到，尝试修复
                response_text = response_text.rstrip() + '}'
        
        # 第二步：解析最外层
        try:
            data = ast.literal_eval(response_text)
        except SyntaxError:
            # 尝试修复常见的语法错误
            # 1. 修复未闭合的字符串
            response_text = re.sub(r"'[^']*$", "'", response_text)
            # 2. 修复未闭合的括号
            open_count = response_text.count('{')
            close_count = response_text.count('}')
            if open_count > close_count:
                response_text += '}' * (open_count - close_count)
            data = ast.literal_eval(response_text)
        
        # 第三步：提取answer字段
        answer = None
        try:
            answer = (
                data.get("raw_response", {})
                .get("RSP_BODY", {})
                .get("answer", "")
            )
        except (AttributeError, KeyError):
            # 如果路径不存在，返回原始数据
            data['analysis_result'] = {}
            return data
        
        if not answer or not isinstance(answer, str):
            data['analysis_result'] = {}
            return data
        
        # 第四步：清理和解析answer字段
        try:
            # 方法1：直接处理转义字符
            # 去除最外层的双引号
            if answer.startswith('"') and answer.endswith('"'):
                cleaned = answer[1:-1]
            else:
                cleaned = answer
            
            # 处理转义字符
            cleaned = cleaned.replace('\\"', '"')
            cleaned = cleaned.replace('\\n', '\n')
            cleaned = cleaned.replace('\\t', '\t')
            cleaned = cleaned.replace('\\\\', '\\')
            
            # 尝试解析JSON
            answer_json = json.loads(cleaned)
            data['analysis_result'] = answer_json
            data['raw_response']['RSP_BODY']['answer'] = answer_json
            
        except json.JSONDecodeError as e1:
            # 方法2：使用ast.literal_eval处理嵌套字符串
            try:
                # 先尝试直接解析
                if answer.startswith('"') and answer.endswith('"'):
                    # 这是双重引号的情况
                    inner_str = ast.literal_eval(answer)  # 这会去除一层引号
                    answer_json = json.loads(inner_str)
                else:
                    # 可能只有一层转义
                    cleaned = answer.replace('\\"', '"').replace('\\\\', '\\')
                    answer_json = json.loads(cleaned)
                
                data['analysis_result'] = answer_json
                data['raw_response']['RSP_BODY']['answer'] = answer_json
                
            except Exception as e2:
                print(f"解析answer字段失败: {e2}")
                print(f"原始answer前500字符: {answer[:500]}")
                # 尝试最后的方法：手动修复JSON
                try:
                    # 查找第一个{和最后一个}
                    start = answer.find('{')
                    end = answer.rfind('}')
                    if start != -1 and end != -1 and end > start:
                        json_str = answer[start:end+1]
                        # 清理转义字符
                        json_str = json_str.replace('\\"', '"').replace('\\\\', '\\')
                        answer_json = json.loads(json_str)
                        data['analysis_result'] = answer_json
                        data['raw_response']['RSP_BODY']['answer'] = answer_json
                    else:
                        data['analysis_result'] = {"error": "无法解析answer字段", "raw": answer[:200]}
                except Exception as e3:
                    print(f"最终解析尝试也失败: {e3}")
                    data['analysis_result'] = {"error": "解析失败", "exception": str(e3), "raw": answer[:200]}
        
        return data
        
    except Exception as e:
        print(f"整体解析失败: {e}")
        # 尝试返回尽可能多的信息
        return {
            "error": "解析失败",
            "exception": str(e),
            "original_text": response_text[:200] if len(response_text) > 200 else response_text
        }

def parse_complete_response(response_text: str) -> Dict[str, Any]:
    """
    完整的响应解析函数，整合了所有修复逻辑
    """
    # 首先修复常见的截断问题
    # 1. 确保字符串以单引号开始和结束
    response_text = response_text.strip()
    if not response_text.startswith("'") and not response_text.startswith('"'):
        # 尝试添加单引号
        response_text = "'" + response_text
    if not response_text.endswith("'") and not response_text.endswith('"'):
        response_text = response_text + "'"
    
    # 2. 修复可能的多余字符
    # 去除可能的多余空格和换行
    response_text = re.sub(r'\s+', ' ', response_text)
    
    # 3. 尝试解析
    return clean_and_parse_response_text(response_text)

# 测试代码（使用您提供的可能被截断的文本）
response_text = """{'success': True, 'raw_response': {'RSP_BODY': {'head': {}, 'TRAN_PROCESS': 'aiQA', 'answer': '"{\\n  \\"sql_type\\": \\"数据操作\\",\\n  \\"rule_analysis\\": {\\n    \\"建表
则\\": {\\n      \\"涉及历史表\\": false,\\n      \\"评估完全\\": false,\\n      \\"主键检查\\": \\"未通过\\",\\n      \\"索引检查\\": \\"未通过\\",\\n      \\"数据量评估\\": \\"合理\\",\\n      \\"注释检查\\": \\"不完整\\",\\ \\
n      \\"字段类型检查\\": \\"合理\\"\\n    },\\n    \\"表结构变更规则\\": {\\n      \\"涉及历史表\\": false,\\n      \\"评估完全\\": false,\\n      \\"影响范围评估\\": \\"不完整\\",\\n      \\"联机影响评估\\": \\"合理\\",\\n   
   \\"注释检查\\": \\"不完整\\"\\n    },\\n    \\"索引规则\\": {\\n      \\"索引冗余检查\\": \\"无冗余\\",\\n      \\"索引总数\\": 0,\\n      \\"索引设计合理性\\": \\"不合理\\",\\n      \\"执行计划分析\\": \\"无\\"\\n    },\\n  
  \\"数据量规则\\": {\\n      \\"数据量级别\\": \\"十万以下\\",\\n      \\"SQL耗时评估\\": \\"毫秒级\\",\\n      \\"备份策略\\": \\"无\\",\\n      \\"数据核对\\": \\"未核对\\"\\n    }\\n  },\\n  \\"risk_assessment\\": {\\n    \\
"高风险问题\\": [\\"表缺少主键，可能导致数据重复或完整性问题\\"],\\n    \\"中风险问题\\": [\\"表无索引，可能影响查询性能\\", \\"未进行数据核对，可能导致数据错误\\"],\\n    \\"低风险问题\\": [\\"表和字段缺少注释，不利于维护\\"]\\
n  },\\n  \\"improvement_suggestions\\": [\\"为表添加主键，确保数据唯一性和完整性\\", \\"根据业务需求添加合适的索引，提高查询性能\\", \\"为表和字段添加注释，便于后期维护\\", \\"执行数据操作后进行数据核对，确保数据正确性\\"],\\n 
 \\"overall_score\\": 5,\\n  \\"summary\\": \\"SQL语句主要涉及数据操作，但存在缺少主键、无索引等问题，可能影响数据完整性和查询性能。建议按照上述建议进行优化，以提高系统的稳定性和可维护性。\\"\\n}"', 'prompt': 'prompt=SQL语句：\n
INSERT INTO ecdcdb.pd_errcode\r\n(PEC_ERRCODE, PEC_LANGUAGE, PEC_SHOWMSG, PEC_INNERMSG, PEC_CLASS, PEC_LASTUPDATE)\r\nVALUES(\'20070004AC0010\', \'zh_CN\', \'命中金融惩戒名单，终止交易\', \'命中金融惩戒名单，终止交易\', \'1\', \
'2024-10-18 18:55:53.615353\');\r\n\n\n数据库：ECDC_SQL_SHELL_CTM\n\n涉及的表信息：\n\n表1：pd_errcode\n  - 行数：212\n  - 是否大表：否\n  - 列数：6\n  - 索引数：0\n  - DDL：\n    CREATE TABLE pd_errcode (PEC_ERRCODE char(14) NO
T NULL, PEC_LANGUAGE varchar(10) NOT NULL, PEC_SHOWMSG varchar(200), PEC_INNERMSG varchar(200), PEC_CLASS varchar(6), PEC_LASTUPDATE timestamp(6) NOT NULL DEFAULT \'CURRENT_TIMESTAMP\')\n  - 列信息：\n    * PEC_ERRCODE (char) 非
\n    * PEC_LANGUAGE (varchar) 非空\n    * PEC_SHOWMSG (varchar) 可空\n    * PEC_INNERMSG (varchar) 可空\n    * PEC_CLASS (varchar) 可空\n    * ... 还有1列\n\n动态SQL示例（用于判断SQL注入漏洞）：\n请分析以下动态SQL示例是否存在在
QL注入风险：\n- 动态插入示例：INSERT INTO users (username, password) VALUES (\'${username}\', \'${password}\')\n- 参数化插入示例：INSERT INTO users (username, password) VALUES (?, ?)\n- 字符串拼接示例：SELECT * FROM products WHH
ERE name LIKE \'%${search_term}%\'\n- 数字类型注入示例：SELECT * FROM orders WHERE id = ${order_id}\n- 时间类型注入示例：SELECT * FROM logs WHERE create_time > \'${start_time}\'\n\nSQL执行计划：未提供\n请基于表结构和索引信息分析
QL执行效率\n\n请根据以下SQL评审规则进行分析：\n\n1. 建表规则：\n   • 是否涉及历史表\n   • 联机、定时、批量是否评估完全\n   • 主键/索引：必须有主键\n   • 联机查询：联机查询走索引或主键\n   • 数据量：表预期数据量做好评估，以应对  
后续业务调用\n   • 注释：表、字段有注释\n   • 数据量增长：上线后，一周内数据量预估，如表增长较快，需要说明清理或归档策略\n   • 分组分区：建表前考虑使用场景，访问量大数据量大的是否可以分组分区\n   • 字段类型：金额类型字段用decima
l\n\n2. 表结构变更规则：\n   • 是否涉及历史表\n   • 联机、定时、批量是否评估完全\n   • 影响范围：对应表的联机、定时、批量评估完全\n   • 联机影响：对应表是否为热点表，表结构修改的时间点是否影响联机（热点表24点后再变更），执行表结
变更耗时\n   • 注释：变更后类型定义合理（如字段类型调整），必须写注释\n\n3. 新建/修改索引规则：\n   • 索引无冗余\n   • 执行后索引总数\n   • 索引添加前后耗时对比\n   • 是否热点表\n   • 更新表结构时间\n   • 索引个数：不超过5个，，
合索引：列的个数控制在3个字段及以内，不能超过5个\n   • 索引设计：考虑索引字段的顺序：结合业务场景，是否合理，能建联合索引的不建单列索引\n   • 执行计划：新建/修改索引前后执行计划\n\n4. 数据量规则：\n   • 生产表数据量（是否十万   
、百万级以上）\n   • 影响范围：应用中与索引相关的sql执行耗时\n   • SQL耗时：秒级\n   • 插入、更新、删除数据\n   • 是否已核对生产数据\n   • 大数据量变更：对表数据大量删除、导入、更新，且影响联机交易，需立即执行analyze提升SQL性能 
（OB3x默认每日2:00定时合并），执行后一直需要手动执行\n   • 备份：删除数据较大时，及时备份\n   • 变更前后核对：核对生产数据，是否与预期变更一致\n   • SQL耗时：插入、更新、删除数据，建表，耗时：毫秒级(或无感知)\n\n请基于以上规则分
SQL语句，重点关注：\n1. SQL类型识别：判断是建表、表结构变更、索引操作还是数据操作\n2. 规则符合性检查：根据SQL类型检查对应的规则\n3. 风险评估：识别潜在的风险和问题\n4. 建议改进：提供具体的改进建议\n5. 综合评分：给出综合评分（0- -
10分）\n\n请严格按照以下JSON格式回复，不要包含任何其他内容：\n{\n  "sql_type": "建表/表结构变更/索引操作/数据操作/查询",\n  "rule_analysis": {\n    "建表规则": {\n      "涉及历史表": true/false,\n      "评估完全": true/false,\n 
     "主键检查": "通过/未通过",\n      "索引检查": "通过/未通过",\n      "data['raw_response']['RSP_BODY']['answer'] = answer_json量评估": "合理/不合理",\n      "注释检查": "完整/不完整",\n      "字段类型检查": "合理/不合理"\n    },\n    "表结构变更规则": {\n      "涉及历史表": t
rue/false,\n      "评估完全": true/false,\n      "影响范围评估": "完整/不完整",\n      "联机影响评估": "合理/不合理",\n      "注释检查": "完整/不完整"\n    },\n    "索引规则": {\n      "索引冗余检查": "无冗余/有冗余",\n      "索
总数": 数字,\n      "索引设计合理性": "合理/不合理",\n      "执行计划分析": "有/无"\n    },\n    "data['raw_response']['RSP_BODY']['answer'] = answer_json量规则": {\n      "data['raw_response']['RSP_BODY']['answer'] = answer_json量级别": "十万以下/十万级/百万级/千万级以上",\n      "SQL耗时评估": "毫秒级/秒级/分钟级",\n      "备   
份策略": "有/无",\n      "data['raw_response']['RSP_BODY']['answer'] = answer_json核对": "已核对/未核对"\n    }\n  },\n  "risk_assessment": {\n    "高风险问题": ["问题1", "问题2"],\n    "中风险问题": ["问题1", "问题2"],\n    "低风险问题": ["问题1", "问题2"]\n  },\n  "improvement_
suggestions": ["建议1", "建议2", "建议3"],\n  "overall_score": 0-10,\n  "summary": "综合分析总结"\n}\n\n注意：请只回复JSON格式的内容，不要包含任何解释性文字。'}, 'RSP_HEAD': {'TRAN_SUCCESS': '1', 'TRACE_NO': 'SDSS118-38-115-1882355925'}}, 'analysis_result': {}}"""

print("开始解析...")
print("=" * 80)

# 使用完整的解析函数
response_data = parse_complete_response(response_text)

# 检查结果
import pprint

if 'error' in response_data:
    print(f"❌ 解析失败: {response_data['error']}")
    print(f"异常: {response_data.get('exception')}")
    print(f"原始文本前200字符: {response_data.get('original_text')}")
else:
    print("✅ 整体解析成功！")
    
    # 检查analysis_result
    analysis_result = response_data.get('analysis_result', {})
    
    if isinstance(analysis_result, dict) and analysis_result:
        print(f"✅ analysis_result 解析成功，包含 {len(analysis_result)} 个键")
        
        # 打印关键信息
        print(f"\n关键信息:")
        print(f"SQL类型: {analysis_result.get('sql_type', '未找到')}")
        print(f"综合评分: {analysis_result.get('overall_score', '未找到')}")
        
        # 如果有总结，打印前100字符
        summary = analysis_result.get('summary', '')
        if summary:
            print(f"总结: {summary[:100]}...")
        
        # 打印完整的analysis_result（前几层）
        print(f"\n完整的analysis_result结构:")
        pprint.pprint(analysis_result, indent=2, depth=2)
    else:
        print("❌ analysis_result 为空或不是字典")
        print(f"analysis_result 内容: {analysis_result}")

print("\n" + "=" * 80)
print("解析完成！")

# 如果需要将结果保存或进一步处理
# 现在response_data包含了完全解析的JSON数据
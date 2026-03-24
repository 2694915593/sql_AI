#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试model_client_enhanced.py中的INSERT语句修复问题
"""

import re
import sys
sys.path.append('sql_ai_analyzer')

# 模拟一个简单的配置管理器
class MockConfigManager:
    def __init__(self):
        self.ai_config = {
            'api_url': 'http://test.ai.com/api'
        }

# 创建一个模拟的ModelClient类，只测试相关方法
class MockModelClient:
    def __init__(self):
        pass
    
    def _clean_extracted_sql(self, sql_text: str) -> str:
        """模拟_clean_extracted_sql方法"""
        if not sql_text:
            return ""

        cleaned = sql_text

        # 1. 移除代码块标记（但要小心不要移除括号）
        cleaned = re.sub(r'```[\w]*\s*', '', cleaned)
        cleaned = re.sub(r'```', '', cleaned)

        # 2. 移除XML标签（但要小心不要移除括号）
        cleaned = re.sub(r'<[^>]+>', ' ', cleaned)

        # 3. 移除CDATA标记
        cleaned = re.sub(r'<!\[CDATA\[', '', cleaned)
        cleaned = re.sub(r'\]\]>', '', cleaned)

        # 4. 压缩多余空格，但保留换行符
        lines = cleaned.split('\n')
        cleaned_lines = []
        for line in lines:
            line = re.sub(r'\s+', ' ', line.strip())
            if line:
                cleaned_lines.append(line)

        cleaned = '\n'.join(cleaned_lines)

        # 5. 修复SQL语句结构（如果缺少关键部分）
        # 注意：这里没有_fix_sql_structure_if_needed方法，会报错
        # cleaned = self._fix_sql_structure_if_needed(cleaned)

        # 6. 移除首尾空白
        cleaned = cleaned.strip()

        return cleaned
    
    def _fix_insert_structure_if_needed(self, sql_text: str) -> str:
        """模拟model_client_fixed.py中的_fix_insert_structure_if_needed方法"""
        if not sql_text:
            return sql_text

        # 检查是否是INSERT语句
        sql_lower = sql_text.lower().strip()
        if not sql_lower.startswith('insert'):
            return sql_text

        # 检查括号数量
        open_paren = sql_text.count('(')
        close_paren = sql_text.count(')')

        # 如果括号数量为0，尝试修复
        if open_paren == 0 and close_paren == 0:
            print("检测到INSERT语句缺少括号，尝试修复")

            # 查找表名结束位置
            table_name_end = -1
            insert_match = re.search(r'insert\s+into\s+([^\s(]+)', sql_lower)
            if insert_match:
                table_name = insert_match.group(1)
                table_name_end = sql_lower.find(table_name) + len(table_name)

                # 查找VALUES关键字
                values_pos = sql_lower.find('values', table_name_end)

                # 如果没有VALUES关键字，尝试推断列名和值的分界
                if values_pos <= 0:
                    # 分析SQL结构
                    lines = sql_text.split('\n')

                    # 寻找可能的列名部分和值部分
                    column_lines = []
                    value_lines = []
                    in_value_section = False

                    for line in lines:
                        line = line.strip()
                        if not line:
                            continue

                        # 检查是否是值部分（包含参数占位符）
                        if '#{' in line:
                            in_value_section = True

                        if in_value_section:
                            value_lines.append(line)
                        else:
                            # 跳过表名行
                            if not line.lower().startswith('insert') and not line.lower().startswith('into'):
                                column_lines.append(line)

                    if column_lines and value_lines:
                        # 重建SQL
                        columns_part = ', '.join([col.strip().rstrip(',') for col in column_lines])
                        values_part = ', '.join([val.strip().rstrip(',') for val in value_lines])

                        # 移除列名部分末尾可能的多余逗号
                        if columns_part.endswith(','):
                            columns_part = columns_part[:-1]
                        if values_part.endswith(','):
                            values_part = values_part[:-1]

                        # 添加括号和VALUES关键字
                        table_part = sql_text[:table_name_end].strip()
                        fixed_sql = f'{table_part} ({columns_part}) VALUES ({values_part})'

                        print(f"智能修复INSERT语句结构（无VALUES关键字）")
                        return fixed_sql

        return sql_text

# 测试用例
test_sql = """insert into PB_ACCOUNT
ID,
ORG_CODE,
MOBILE,
NAME,
CERT_TYPE,
CERT_NO,
ACCOUNT_NO,
ACCOUNT_TYPE,
STATUS,
CTIME,
MODULE_TYPE,
CHANNEL_TYPE,
MAIN_TYPE,
SCENCE_TYPE,
ACCOUNT_JNL,
CHECK_ACTIVE_PATH,
CHECK_ACTIVE_DOCID,
CHECK_ACTIVE_CTIME,
CHECK_OCR_DOCID,
TRACE_NO
#{id,jdbcType=BIGINT},
#{orgCode,jdbcType=VARCHAR},
#{mobile,jdbcType=VARCHAR},
#{name,jdbcType=VARCHAR},
#{certType,jdbcType=VARCHAR},
#{certNo,jdbcType=VARCHAR},
#{accountNo,jdbcType=VARCHAR},
#{accountType,jdbcType=VARCHAR},
#{status,jdbcType=VARCHAR},
#{ctime,jdbcType=TIMESTAMP},
#{moduleType,jdbcType=VARCHAR},
#{channelType,jdbcType=VARCHAR},
#{mainType,jdbcType=VARCHAR},
#{scenceType,jdbcType=VARCHAR},
#{accountJnl,jdbcType=VARCHAR},
#{checkActivePath,jdbcType=VARCHAR},
#{checkActiveDocId,jdbcType=VARCHAR},
#{checkActiveCtime,jdbcType=TIMESTAMP},
#{checkOcrDocId,jdbcType=VARCHAR},
#{traceNo,jdbcType=VARCHAR},"""

print("原始SQL:")
print(test_sql)
print("\n" + "="*80 + "\n")

# 测试_clean_extracted_sql
client = MockModelClient()
cleaned_sql = client._clean_extracted_sql(test_sql)
print("清理后SQL:")
print(cleaned_sql)
print("\n" + "="*80 + "\n")

# 测试_fix_insert_structure_if_needed
fixed_sql = client._fix_insert_structure_if_needed(cleaned_sql)
print("修复后SQL:")
print(fixed_sql)
print("\n" + "="*80 + "\n")

# 期望的SQL格式
expected_sql = """INSERT INTO PB_ACCOUNT
(ID, ORG_CODE, MOBILE, NAME, CERT_TYPE, CERT_NO, ACCOUNT_NO, ACCOUNT_TYPE, STATUS, CTIME, MODULE_TYPE, CHANNEL_TYPE, MAIN_TYPE, SCENCE_TYPE, ACCOUNT_JNL, CHECK_ACTIVE_PATH, CHECK_ACTIVE_DOCID, CHECK_ACTIVE_CTIME, CHECK_OCR_DOCID, TRACE_NO)
VALUES
(#{id,jdbcType=BIGINT}, #{orgCode,jdbcType=VARCHAR}, #{mobile,jdbcType=VARCHAR}, #{name,jdbcType=VARCHAR}, #{certType,jdbcType=VARCHAR}, #{certNo,jdbcType=VARCHAR}, #{accountNo,jdbcType=VARCHAR}, #{accountType,jdbcType=VARCHAR}, #{status,jdbcType=VARCHAR}, #{ctime,jdbcType=TIMESTAMP}, #{moduleType,jdbcType=VARCHAR}, #{channelType,jdbcType=VARCHAR}, #{mainType,jdbcType=VARCHAR}, #{scenceType,jdbcType=VARCHAR}, #{accountJnl,jdbcType=VARCHAR}, #{checkActivePath,jdbcType=VARCHAR}, #{checkActiveDocId,jdbcType=VARCHAR}, #{checkActiveCtime,jdbcType=TIMESTAMP}, #{checkOcrDocId,jdbcType=VARCHAR}, #{traceNo,jdbcType=VARCHAR})"""

print("期望的SQL格式:")
print(expected_sql)
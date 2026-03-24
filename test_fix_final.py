#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试修复后的INSERT语句处理逻辑
"""

import sys
import os
sys.path.append('sql_ai_analyzer')

# 创建一个模拟的ModelClient类，只测试相关方法
class MockModelClient:
    def __init__(self):
        import logging
        logging.basicConfig(level=logging.DEBUG)
        self.logger = logging.getLogger(__name__)
    
    def _fix_insert_structure_if_needed(self, sql_text: str) -> str:
        """
        模拟_fix_insert_structure_if_needed方法
        """
        if not sql_text:
            return sql_text

        sql_lower = sql_text.lower().strip()
        if not sql_lower.startswith('insert'):
            return sql_text

        # 检查括号
        open_paren = sql_text.count('(')
        close_paren = sql_text.count(')')

        # 如果没有括号
        if open_paren == 0 and close_paren == 0:
            print("检测到INSERT语句缺少括号，尝试修复")

            # 尝试找到表名
            import re
            table_match = re.search(r'insert\s+into\s+([^\s(]+)', sql_lower)
            if table_match:
                table_name = table_match.group(1)
                table_end = sql_lower.find(table_name) + len(table_name)

                # 查找可能的列名部分（以列名特征开头）
                # 假设列名以大写字母或下划线开头
                after_table = sql_text[table_end:].strip()

                # 查找第一个参数（#{）作为列名和值的分界
                param_start = after_table.find('#{')
                if param_start > 0:
                    columns_part = after_table[:param_start].strip()
                    values_part = after_table[param_start:].strip()

                    # 清理列名部分 - 移除末尾的逗号
                    columns_clean = re.sub(r'\s+', ' ', columns_part).strip()
                    # 移除列名部分末尾的逗号
                    if columns_clean.endswith(','):
                        columns_clean = columns_clean[:-1].strip()

                    # 清理值部分
                    values_clean = re.sub(r'\s+', ' ', values_part).strip()

                    # 移除值部分的末尾逗号
                    if values_clean.endswith(','):
                        values_clean = values_clean[:-1].strip()

                    # 检查是否需要添加VALUES关键字
                    has_values = 'values' in sql_lower
                    if not has_values:
                        print("缺少VALUES关键字，将添加")

                    # 添加括号
                    columns_fixed = f'({columns_clean})'
                    values_fixed = f'({values_clean})'

                    # 重构SQL
                    table_part = sql_text[:table_end].strip()
                    if has_values:
                        # 如果已经有VALUES，保持原样
                        fixed_sql = f'{table_part} {columns_fixed} VALUES {values_fixed}'
                    else:
                        # 如果没有VALUES，添加
                        fixed_sql = f'{table_part} {columns_fixed} VALUES {values_fixed}'

                    print(f"修复INSERT语句结构: 原始长度={len(sql_text)}, 修复后长度={len(fixed_sql)}")
                    return fixed_sql
                else:
                    print("未找到参数分界点，无法修复")

        # 如果只有一对括号，但INSERT语句应该有两对括号
        elif open_paren == 1 and close_paren == 1:
            print("检测到INSERT语句只有一对括号，尝试修复")

            # 检查括号位置
            first_paren = sql_text.find('(')
            last_paren = sql_text.rfind(')')

            # 查找VALUES关键字
            values_pos = sql_lower.find('values')

            import re
            if values_pos > 0 and first_paren < values_pos < last_paren:
                # 括号在VALUES之前，这可能是列名括号
                # 需要添加值括号

                # 在VALUES后面添加括号
                # 找到VALUES后的内容
                after_values = sql_text[values_pos + 5:].strip()

                # 如果VALUES后的内容没有括号，添加
                if not after_values.startswith('('):
                    # 找到值的结束位置
                    # 如果是参数形式，可能以逗号或分号结束
                    end_pos = len(sql_text)
                    for end_char in [',', ';', '\n']:
                        pos = sql_text.find(end_char, values_pos + 5)
                        if pos > 0 and pos < end_pos:
                            end_pos = pos

                    values_content = sql_text[values_pos + 5:end_pos].strip()
                    # 添加括号
                    values_fixed = f'({values_content})'

                    # 重新组合
                    before_values = sql_text[:values_pos + 5].strip()
                    fixed_sql = f'{before_values} {values_fixed}'
                    if end_pos < len(sql_text):
                        fixed_sql += sql_text[end_pos:]

                    print(f"为INSERT语句添加值括号: 原始长度={len(sql_text)}, 修复后长度={len(fixed_sql)}")
                    return fixed_sql

        return sql_text
    
    def _clean_extracted_sql(self, sql_text: str) -> str:
        """模拟_clean_extracted_sql方法"""
        if not sql_text:
            return ""

        cleaned = sql_text

        # 1. 移除代码块标记（但要小心不要移除括号）
        import re
        cleaned = re.sub(r'```[\w]*\s*', '', cleaned)
        cleaned = re.sub(r'```', '', cleaned)

        # 2. 移除XML标签（但要小心不要移除括号）
        # 使用更保守的方法，只移除真正的XML标签
        cleaned = re.sub(r'<[^>]+>', ' ', cleaned)

        # 3. 移除CDATA标记
        cleaned = re.sub(r'<!\[CDATA\[', '', cleaned)
        cleaned = re.sub(r'\]\]>', '', cleaned)

        # 4. 压缩多余空格，但保留换行符（对多行SQL很重要）
        # 先分割为行，单独处理每行
        lines = cleaned.split('\n')
        cleaned_lines = []
        for line in lines:
            line = re.sub(r'\s+', ' ', line.strip())
            if line:
                cleaned_lines.append(line)

        # 重新组合，保留换行符（对多行SQL很重要）
        cleaned = '\n'.join(cleaned_lines)

        # 5. 移除首尾空白
        cleaned = cleaned.strip()

        return cleaned

# 测试用例 - 与用户提供的完全相同的SQL
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

print("=" * 80)
print("原始SQL:")
print(test_sql)
print("\n" + "=" * 80)

# 测试清理功能
client = MockModelClient()
cleaned_sql = client._clean_extracted_sql(test_sql)
print("清理后SQL:")
print(cleaned_sql)
print("\n" + "=" * 80)

# 测试修复功能
fixed_sql = client._fix_insert_structure_if_needed(cleaned_sql)
print("修复后SQL:")
print(fixed_sql)
print("\n" + "=" * 80)

# 期望的结果
expected_sql = """INSERT INTO PB_ACCOUNT
(ID, ORG_CODE, MOBILE, NAME, CERT_TYPE, CERT_NO, ACCOUNT_NO, ACCOUNT_TYPE, STATUS, CTIME, MODULE_TYPE, CHANNEL_TYPE, MAIN_TYPE, SCENCE_TYPE, ACCOUNT_JNL, CHECK_ACTIVE_PATH, CHECK_ACTIVE_DOCID, CHECK_ACTIVE_CTIME, CHECK_OCR_DOCID, TRACE_NO)
VALUES
(#{id,jdbcType=BIGINT}, #{orgCode,jdbcType=VARCHAR}, #{mobile,jdbcType=VARCHAR}, #{name,jdbcType=VARCHAR}, #{certType,jdbcType=VARCHAR}, #{certNo,jdbcType=VARCHAR}, #{accountNo,jdbcType=VARCHAR}, #{accountType,jdbcType=VARCHAR}, #{status,jdbcType=VARCHAR}, #{ctime,jdbcType=TIMESTAMP}, #{moduleType,jdbcType=VARCHAR}, #{channelType,jdbcType=VARCHAR}, #{mainType,jdbcType=VARCHAR}, #{scenceType,jdbcType=VARCHAR}, #{accountJnl,jdbcType=VARCHAR}, #{checkActivePath,jdbcType=VARCHAR}, #{checkActiveDocId,jdbcType=VARCHAR}, #{checkActiveCtime,jdbcType=TIMESTAMP}, #{checkOcrDocId,jdbcType=VARCHAR}, #{traceNo,jdbcType=VARCHAR})"""

print("期望的SQL格式:")
print(expected_sql)
print("\n" + "=" * 80)

# 验证修复是否成功
if fixed_sql:
    # 检查是否添加了括号
    if '(' in fixed_sql and ')' in fixed_sql:
        print("✓ 修复成功：已添加括号")
    else:
        print("✗ 修复失败：缺少括号")
    
    # 检查是否添加了VALUES关键字
    if 'values' in fixed_sql.lower():
        print("✓ 修复成功：已添加VALUES关键字")
    else:
        print("✗ 修复失败：缺少VALUES关键字")
    
    # 检查参数是否正确
    if '#{' in fixed_sql:
        print("✓ 修复成功：参数保留完整")
    else:
        print("✗ 修复失败：参数丢失")
else:
    print("✗ 修复失败：返回为空")
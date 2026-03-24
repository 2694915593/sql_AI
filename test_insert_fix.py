#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试INSERT语句修复逻辑
"""

import re

def fix_insert_sql_structure(sql_text: str) -> str:
    """
    修复INSERT语句结构，解决以下问题：
    1. 缺少INSERT INTO关键字
    2. 缺少VALUES关键字
    3. 缺少括号
    4. 列名和值部分格式错误
    5. 末尾逗号问题
    
    Args:
        sql_text: SQL文本
        
    Returns:
        修复后的SQL文本
    """
    if not sql_text:
        return sql_text
    
    sql_lower = sql_text.lower().strip()
    if not sql_lower.startswith('insert'):
        return sql_text
    
    print(f"原始SQL: {sql_text}")
    
    # 1. 检查是否有INSERT INTO
    if 'insert into' not in sql_lower:
        # 如果只有INSERT，添加INTO
        if sql_lower.startswith('insert ') and not sql_lower.startswith('insert into'):
            # 在INSERT后面添加INTO
            lines = sql_text.split('\n')
            if lines:
                first_line = lines[0]
                if first_line.lower().startswith('insert '):
                    # 在INSERT后添加INTO
                    insert_pos = first_line.lower().find('insert')
                    if insert_pos >= 0:
                        before_insert = first_line[:insert_pos]
                        after_insert = first_line[insert_pos + 6:]  # 6是"insert"的长度
                        first_line = before_insert + 'INSERT INTO' + after_insert
                        lines[0] = first_line
                        sql_text = '\n'.join(lines)
    
    # 重新获取小写版本
    sql_lower = sql_text.lower().strip()
    
    # 2. 检查是否有VALUES关键字
    has_values = 'values' in sql_lower
    
    # 3. 分析SQL结构
    lines = sql_text.split('\n')
    
    # 查找表名
    table_name = None
    for line in lines:
        line_lower = line.lower().strip()
        if line_lower.startswith('insert into'):
            # 提取表名
            parts = line_lower.split('insert into')
            if len(parts) > 1:
                table_part = parts[1].strip()
                # 表名可能后面有换行或空格
                table_name_match = re.search(r'([a-zA-Z_][a-zA-Z0-9_]*)', table_part)
                if table_name_match:
                    table_name = table_name_match.group(1)
                    # 找到原始大小写的表名
                    original_line = line.strip()
                    insert_into_pos = original_line.lower().find('insert into')
                    if insert_into_pos >= 0:
                        after_insert_into = original_line[insert_into_pos + 10:]  # 10是"insert into"的长度
                        table_name_match_original = re.search(r'([a-zA-Z_][a-zA-Z0-9_]*)', after_insert_into)
                        if table_name_match_original:
                            table_name = table_name_match_original.group(1)
            break
    
    # 如果没有找到表名，使用默认值
    if not table_name:
        table_name = 'PB_ACCOUNT'
    
    # 4. 分析列和值
    in_column_section = False
    in_value_section = False
    column_lines = []
    value_lines = []
    
    for line in lines:
        line_stripped = line.strip()
        if not line_stripped:
            continue
        
        # 跳过INSERT INTO行
        if line_stripped.lower().startswith('insert into'):
            continue
        
        # 检查是否是列名（大写或包含下划线）
        if line_stripped.isupper() or ('_' in line_stripped and not '#{' in line_stripped):
            # 可能是列名
            if not in_value_section:
                in_column_section = True
                column_lines.append(line_stripped)
            else:
                # 已经在值部分，但遇到大写行，可能是列名错误地放在值部分
                pass
        
        # 检查是否是参数值（包含#{}）
        elif '#{' in line_stripped:
            in_value_section = True
            in_column_section = False
            value_lines.append(line_stripped)
        
        # 检查是否是VALUES关键字
        elif line_stripped.lower() == 'values':
            has_values = True
            continue
    
    print(f"列行: {column_lines}")
    print(f"值行: {value_lines}")
    print(f"有VALUES: {has_values}")
    
    # 5. 重构SQL
    if column_lines or value_lines:
        result_parts = []
        
        # 添加INSERT INTO表名
        insert_line_found = False
        for line in lines:
            if line.lower().strip().startswith('insert into'):
                result_parts.append(line.rstrip())
                insert_line_found = True
                break
        
        # 如果没有找到INSERT INTO行，创建一行
        if not insert_line_found:
            result_parts.append(f"INSERT INTO {table_name}")
        
        # 添加列名部分
        if column_lines:
            # 清理列名：移除末尾逗号
            clean_columns = []
            for col in column_lines:
                col = col.rstrip()
                if col.endswith(','):
                    col = col[:-1].rstrip()
                clean_columns.append(col)
            
            # 组合列名
            columns_str = ', '.join(clean_columns)
            result_parts.append(f"({columns_str})")
        
        # 添加VALUES关键字
        if not has_values:
            result_parts.append("VALUES")
        
        # 添加值部分
        if value_lines:
            # 清理值：移除末尾逗号
            clean_values = []
            for val in value_lines:
                val = val.rstrip()
                if val.endswith(','):
                    val = val[:-1].rstrip()
                clean_values.append(val)
            
            # 组合值
            values_str = ', '.join(clean_values)
            result_parts.append(f"({values_str})")
        
        # 构建最终的SQL
        fixed_sql = '\n'.join(result_parts)
        
        # 确保最后一个字符不是逗号
        if fixed_sql.endswith(','):
            fixed_sql = fixed_sql[:-1]
        
        print(f"修复后SQL: {fixed_sql}")
        return fixed_sql
    
    # 如果没有分析出结构，尝试其他修复方法
    # 检查括号情况
    open_paren = sql_text.count('(')
    close_paren = sql_text.count(')')
    
    # 如果没有括号，添加括号
    if open_paren == 0 and close_paren == 0:
        # 查找参数开始位置
        param_start = sql_text.find('#{')
        if param_start > 0:
            before_params = sql_text[:param_start].strip()
            params_part = sql_text[param_start:].strip()
            
            # 清理
            before_clean = re.sub(r'\s+', ' ', before_params).strip()
            params_clean = re.sub(r'\s+', ' ', params_part).strip()
            
            # 移除末尾逗号
            if before_clean.endswith(','):
                before_clean = before_clean[:-1].strip()
            if params_clean.endswith(','):
                params_clean = params_clean[:-1].strip()
            
            # 添加括号和VALUES关键字
            if not has_values:
                fixed_sql = f"{before_clean} VALUES ({params_clean})"
            else:
                fixed_sql = f"{before_clean} ({params_clean})"
            
            print(f"添加括号后SQL: {fixed_sql}")
            return fixed_sql
    
    return sql_text

# 测试用例
test_cases = [
    # 原始问题案例
    """insert into PB_ACCOUNT
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
#{traceNo,jdbcType=VARCHAR},""",
    
    # 正确格式的SQL作为对比
    """INSERT INTO PB_ACCOUNT
(ID, ORG_CODE, MOBILE, NAME, CERT_TYPE, 
CERT_NO, ACCOUNT_NO, ACCOUNT_TYPE, STATUS, CTIME, MODULE_TYPE, CHANNEL_TYPE, MAIN_TYPE, SCENCE_TYPE, ACCOUNT_JNL, CHECK_ACTIVE_PATH, CHECK_ACTIVE_DOCID, CHECK_ACTIVE_CTIME, CHECK_OCR_DOCID, TRACE_NO)
VALUES
(#{id,jdbcType=BIGINT}, #{orgCode,jdbcType=VARCHAR}, #{mobile,jdbcType=VARCHAR}, #{name,jdbcType=VARCHAR}, #{certType,jdbcType=VARCHAR}, #{certNo,jdbcType=VARCHAR}, #{accountNo,jdbcType=VARCHAR}, #{accountType,jdbcType=VARCHAR}, #{status,jdbcType=VARCHAR}, #{ctime,jdbcType=TIMESTAMP}, #{moduleType,jdbcType=VARCHAR}, #{channelType,jdbcType=VARCHAR}, #{mainType,jdbcType=VARCHAR}, #{scenceType,jdbcType=VARCHAR}, #{accountJnl,jdbcType=VARCHAR}, #{checkActivePath,jdbcType=VARCHAR}, #{checkActiveDocId,jdbcType=VARCHAR}, #{checkActiveCtime,jdbcType=TIMESTAMP}, #{checkOcrDocId,jdbcType=VARCHAR}, #{traceNo,jdbcType=VARCHAR})""",
]

print("=" * 80)
print("测试INSERT语句修复")
print("=" * 80)

for i, test_sql in enumerate(test_cases):
    print(f"\n测试用例 {i+1}:")
    print("-" * 40)
    fixed = fix_insert_sql_structure(test_sql)
    print(f"修复成功: {fixed != test_sql}")
    print()
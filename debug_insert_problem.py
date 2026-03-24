#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试INSERT语句问题
"""

import sys
import os
import re

# 设置路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'sql_ai_analyzer'))

print("调试INSERT语句问题")
print("=" * 80)

# 用户提供的原始SQL
original_sql = """insert into MONTHLY_TRAN_MSG
(
    MTM_PARTY_NO, 
    MTM_SEND, 
    MTM_PRODUCT_TYPE, 
    MTM_PARTY_NAME, 
    MTM_CREATE_TIME, 
    MTM_UPDATE_TIME, 
    MTM_remark1, 
    MTM_remark2
)
values 
(
    #{partyNo,jdbcType=VARCHAR}, 
    #{send,jdbcType=VARCHAR}, 
    #{productType,jdbcType=VARCHAR}, 
    #{partyName,jdbcType=VARCHAR}, 
    #{createTime,jdbcType=TIMESTAMP}, 
    #{updateTime,jdbcType=TIMESTAMP}, 
    #{remark1,jdbcType=VARCHAR}, 
    #{remark2,jdbcType=VARCHAR}
)"""

# 解析出来的SQL（有问题）
parsed_sql = """insert into MONTHLY_TRAN_MSG

            MTM_PARTY_NO, MTM_SEND, MTM_PRODUCT_TYPE, MTM_PARTY_NAME,

                MTM_CREATE_TIME,


                MTM_UPDATE_TIME,


                MTM_remark1,


                MTM_remark2,



            #{partyNo,jdbcType=VARCHAR}, #{send,jdbcType=VARCHAR}, #{productType,jdbcType=VARCHAR}, #{partyName,jdbcType=VARCHAR},

                #{createTime,jdbcType=TIMESTAMP},


                #{updateTime,jdbcType=TIMESTAMP},


                #{remark1,jdbcType=VARCHAR},


                #{remark2,jdbcType=VARCHAR},"""

print("1. 分析解析出来的SQL格式问题:")
print(f"  以'insert into MONTHLY_TRAN_MSG'开头: {parsed_sql.startswith('insert into MONTHLY_TRAN_MSG')}")
print(f"  包含'(': {parsed_sql.count('(')} 次")
print(f"  包含')': {parsed_sql.count(')')} 次")
print(f"  包含'VALUES': {'VALUES' in parsed_sql.upper()}")
print(f"  包含'values': {'values' in parsed_sql.lower()}")

# 检查解析出来的SQL是否缺少括号
print(f"\n2. 括号匹配检查:")
open_paren = parsed_sql.count('(')
close_paren = parsed_sql.count(')')
print(f"  原始SQL: (={original_sql.count('(')}, )={original_sql.count(')')}")
print(f"  解析SQL: (={open_paren}, )={close_paren}")

# 检查结构
print(f"\n3. SQL结构分析:")
lines = parsed_sql.split('\n')
print(f"  总行数: {len(lines)}")
print(f"  前10行:")
for i, line in enumerate(lines[:10]):
    print(f"    [{i:2}] {repr(line)}")

# 查找可能的问题来源
print(f"\n4. 查找问题可能出现在哪个处理环节:")

# 测试各种可能的处理函数
try:
    from sql_ai_analyzer.utils.sql_preprocessor import SQLPreprocessor
    
    preprocessor = SQLPreprocessor()
    
    # 测试预处理
    print(f"  测试SQL预处理器:")
    processed_sql, info = preprocessor.preprocess_sql(original_sql, mode="normalize")
    print(f"    原始长度: {len(original_sql)}")
    print(f"    处理后长度: {len(processed_sql)}")
    print(f"    是否包含XML标签: {info['has_xml_tags']}")
    
    # 检查括号是否被保留
    print(f"    处理后括号: (={processed_sql.count('(')}, )={processed_sql.count(')')}")
    
    # 检查是否有多余空格
    print(f"    处理后前100字符: {repr(processed_sql[:100])}")
    
except Exception as e:
    print(f"  导入SQLPreprocessor失败: {e}")

# 分析正则表达式匹配问题
print(f"\n5. 正则表达式匹配测试:")

# 测试可能出问题的正则表达式
# 1. 提取表名的正则
insert_table_pattern = r'\bINSERT\s+(?:INTO\s+)?([a-zA-Z_][\w\.]*|`[^`]+`|\'[^\']+\'|"[^"]+")(?=\s*(?:\([^)]+\)\s+VALUES|VALUES|SELECT|;|$))'
matches = re.findall(insert_table_pattern, original_sql, re.IGNORECASE)
print(f"  表名提取: {matches}")

# 2. 提取列名和值的正则
# 问题可能出现在这里 - 没有正确处理多行和嵌套括号
print(f"\n6. 测试INSERT语句解析:")
def parse_insert_structure(sql):
    """解析INSERT语句结构"""
    # 移除注释和标准化
    sql_clean = re.sub(r'--.*?$|/\*.*?\*/', '', sql, flags=re.MULTILINE | re.DOTALL)
    sql_clean = re.sub(r'\s+', ' ', sql_clean).strip()
    
    # 提取表名
    table_match = re.search(r'INSERT\s+INTO\s+([^\s(]+)', sql_clean, re.IGNORECASE)
    table_name = table_match.group(1) if table_match else None
    
    # 尝试提取列名部分和值部分
    # 查找第一个括号对（列名）
    col_start = sql_clean.find('(')
    col_end = -1
    if col_start > 0:
        # 找到匹配的右括号
        paren_count = 0
        for i in range(col_start, len(sql_clean)):
            if sql_clean[i] == '(':
                paren_count += 1
            elif sql_clean[i] == ')':
                paren_count -= 1
                if paren_count == 0:
                    col_end = i
                    break
    
    # 查找VALUES关键字
    values_pos = sql_clean.upper().find('VALUES')
    
    # 查找值括号
    val_start = -1
    val_end = -1
    if values_pos > 0:
        val_start = sql_clean.find('(', values_pos)
        if val_start > 0:
            paren_count = 0
            for i in range(val_start, len(sql_clean)):
                if sql_clean[i] == '(':
                    paren_count += 1
                elif sql_clean[i] == ')':
                    paren_count -= 1
                    if paren_count == 0:
                        val_end = i
                        break
    
    print(f"  表名: {table_name}")
    print(f"  列名括号位置: {col_start} 到 {col_end} (长度: {col_end - col_start if col_end > col_start else -1})")
    print(f"  VALUES位置: {values_pos}")
    print(f"  值括号位置: {val_start} 到 {val_end} (长度: {val_end - val_start if val_end > val_start else -1})")
    
    return table_name, col_start, col_end, values_pos, val_start, val_end

table_name, col_start, col_end, values_pos, val_start, val_end = parse_insert_structure(original_sql)

# 分析解析出来的SQL
print(f"\n7. 分析解析出来的SQL结构:")
table_name2, col_start2, col_end2, values_pos2, val_start2, val_end2 = parse_insert_structure(parsed_sql)

print(f"\n8. 问题总结:")
print(f"  原始SQL有正确的括号结构")
print(f"  解析出来的SQL缺少括号")
print(f"  这可能是由于:")
print(f"    a) 正则表达式没有正确处理多行SQL")
print(f"    b) 括号匹配算法有问题")
print(f"    c) 在处理过程中丢失了括号")

# 测试修复方案
print(f"\n9. 测试修复方案:")

def fix_insert_parsing(sql):
    """修复INSERT语句解析"""
    # 先移除可能的XML标签
    sql = re.sub(r'<[^>]+>', ' ', sql)
    
    # 标准化空格，但保留基本结构
    # 保留换行符，但压缩连续空格
    lines = sql.split('\n')
    cleaned_lines = []
    for line in lines:
        line = re.sub(r'\s+', ' ', line.strip())
        if line:
            cleaned_lines.append(line)
    
    # 重新组合，但我们需要确保括号结构完整
    result = ' '.join(cleaned_lines)
    
    # 检查是否缺少必要的括号
    if result.count('(') < 2 or result.count(')') < 2:
        # 尝试修复：确保有表名后的括号和VALUES后的括号
        # 查找INSERT INTO表名
        insert_match = re.search(r'INSERT\s+INTO\s+([^\s(]+)', result, re.IGNORECASE)
        if insert_match:
            table_name = insert_match.group(1)
            # 查找列名部分
            after_table = result[insert_match.end():].strip()
            
            # 如果缺少第一个括号，添加
            if not after_table.startswith('('):
                # 查找列名和VALUES
                values_pos = after_table.upper().find('VALUES')
                if values_pos > 0:
                    # 在VALUES前添加括号
                    columns_part = after_table[:values_pos].strip()
                    values_part = after_table[values_pos:].strip()
                    
                    # 确保列名部分有括号
                    if not columns_part.startswith('(') or not columns_part.endswith(')'):
                        # 添加括号
                        columns_part = f'({columns_part})'
                    
                    # 确保值部分有括号
                    values_match = re.search(r'VALUES\s+(.+)', values_part, re.IGNORECASE)
                    if values_match:
                        values_content = values_match.group(1).strip()
                        if not values_content.startswith('(') or not values_content.endswith(')'):
                            values_content = f'({values_content})'
                        values_part = f'VALUES {values_content}'
                    
                    result = f'INSERT INTO {table_name} {columns_part} {values_part}'
    
    return result

fixed_sql = fix_insert_parsing(parsed_sql)
print(f"  修复后的SQL: {fixed_sql[:100]}...")
print(f"  修复后括号: (={fixed_sql.count('(')}, )={fixed_sql.count(')')}")

print("\n" + "=" * 80)
print("调试完成")
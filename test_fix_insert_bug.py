#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试INSERT语句修复功能
"""

import re
import sys
sys.path.insert(0, '.')

# 测试函数（模拟修复后的逻辑）
def test_fixed_fix_insert_structure_if_needed(sql_text):
    """测试修复函数"""
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
        print('检测到INSERT语句缺少括号，尝试修复')
        
        # 查找表名结束位置
        table_name_end = -1
        # 匹配INSERT INTO table_name
        insert_match = re.search(r'insert\s+into\s+([^\s(]+)', sql_lower)
        if insert_match:
            table_name = insert_match.group(1)
            table_name_end = sql_lower.find(table_name) + len(table_name)
            
            # 查找VALUES关键字
            values_pos = sql_lower.find('values', table_name_end)
            
            # 如果没有VALUES关键字，尝试推断列名和值的分界
            if values_pos <= 0:
                print('没有VALUES关键字，尝试智能分析')
                # 分析SQL结构，尝试找到列名和值的分界点
                # 列名通常是字段名（大写、下划线分隔）
                # 值通常是参数（#{...}）或字面值
                
                # 按行分割SQL
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
                        # 跳过表名行（已经处理过表名）
                        if not line.lower().startswith('insert') and not line.lower().startswith('into'):
                            column_lines.append(line)
                
                if column_lines and value_lines:
                    print(f'找到列名行: {len(column_lines)} 行')
                    print(f'找到值行: {len(value_lines)} 行')
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
                    
                    print(f'智能修复完成')
                    return fixed_sql
                else:
                    print('未能智能分析列名和值部分')
            
            # 如果有VALUES关键字，使用原来的逻辑
            if values_pos > 0:
                print('有VALUES关键字，使用标准修复逻辑')
                # 列名部分（表名后到VALUES前）
                columns_part = sql_text[table_name_end:values_pos].strip()
                # 值部分（VALUES后）
                values_part = sql_text[values_pos + 5:].strip()
                
                # 清理列名部分（移除多余空格和换行）
                columns_clean = re.sub(r'\s+', ' ', columns_part).strip()
                # 清理值部分
                values_clean = re.sub(r'\s+', ' ', values_part).strip()
                
                # 检查列名部分是否看起来像列名（包含逗号）
                if ',' in columns_clean or any(keyword in columns_clean.lower() for keyword in ['mtm_', 'col', 'field', 'id']):
                    # 在列名部分前后添加括号
                    columns_fixed = f'({columns_clean})'
                else:
                    # 如果列名部分不包含逗号，可能是一个列名
                    columns_fixed = f'({columns_clean})'
                
                # 检查值部分是否看起来像值（包含逗号或参数）
                if ',' in values_clean or '#{' in values_clean or 'value' in values_clean.lower():
                    # 在值部分前后添加括号
                    # 但要注意可能已经有引号或其他字符
                    values_fixed = f'({values_clean})'
                else:
                    values_fixed = f'({values_clean})'
                
                # 重新组合SQL
                table_part = sql_text[:table_name_end].strip()
                fixed_sql = f'{table_part} {columns_fixed} VALUES {values_fixed}'
                
                print(f'标准修复完成')
                return fixed_sql
    
    return sql_text

# 测试数据
# 有问题的SQL（用户提供的例子）
problematic_sql = '''insert into PB_ACCOUNT
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
#{traceNo,jdbcType=VARCHAR},'''

# 原始正确的SQL（作为对比）
original_correct_sql = '''INSERT INTO PB_ACCOUNT
(ID, ORG_CODE, MOBILE, NAME, CERT_TYPE, 
CERT_NO, ACCOUNT_NO, ACCOUNT_TYPE, STATUS, CTIME, MODULE_TYPE, CHANNEL_TYPE, MAIN_TYPE, SCENCE_TYPE, ACCOUNT_JNL, CHECK_ACTIVE_PATH, CHECK_ACTIVE_DOCID, CHECK_ACTIVE_CTIME, CHECK_OCR_DOCID, TRACE_NO)
VALUES
(#{id,jdbcType=BIGINT}, #{orgCode,jdbcType=VARCHAR}, #{mobile,jdbcType=VARCHAR}, #{name,jdbcType=VARCHAR}, #{certType,jdbcType=VARCHAR}, #{certNo,jdbcType=VARCHAR}, #{accountNo,jdbcType=VARCHAR}, #{accountType,jdbcType=VARCHAR}, #{status,jdbcType=VARCHAR}, #{ctime,jdbcType=TIMESTAMP}, #{moduleType,jdbcType=VARCHAR}, #{channelType,jdbcType=VARCHAR}, #{mainType,jdbcType=VARCHAR}, #{scenceType,jdbcType=VARCHAR}, #{accountJnl,jdbcType=VARCHAR}, #{checkActivePath,jdbcType=VARCHAR}, #{checkActiveDocId,jdbcType=VARCHAR}, #{checkActiveCtime,jdbcType=TIMESTAMP}, #{checkOcrDocId,jdbcType=VARCHAR}, #{traceNo,jdbcType=VARCHAR})'''

print('=' * 80)
print('测试INSERT语句修复功能')
print('=' * 80)

print('\n1. 测试有问题的SQL:')
print('-' * 40)
print('输入SQL（前200字符）:')
print(problematic_sql[:200] + '...')

result = test_fixed_fix_insert_structure_if_needed(problematic_sql)

print('\n修复结果:')
print('-' * 40)
print(result)

print('\n括号检查:')
print(f'括号数量: (={result.count("(")}, )={result.count(")")}')
print(f'包含VALUES: {"VALUES" in result.upper()}')

print('\n2. 对比原始正确的SQL:')
print('-' * 40)
print('原始正确SQL（前200字符）:')
print(original_correct_sql[:200] + '...')

print('\n3. SQL结构分析:')
print('-' * 40)
print('修复后的SQL结构:')
lines = result.split('\n')
for i, line in enumerate(lines[:5]):
    print(f'  [{i}] {line}')

# 检查是否是有效的INSERT语句
if 'VALUES' in result.upper() and result.count('(') >= 2 and result.count(')') >= 2:
    print('\n✅ 修复成功: INSERT语句结构正确')
else:
    print('\n❌ 修复失败: INSERT语句结构不正确')
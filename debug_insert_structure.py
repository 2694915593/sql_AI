#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试INSERT语句结构分析
"""

import re

# 用户提供的解析出来的SQL（有问题）
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

print("调试INSERT语句结构分析")
print("=" * 80)

# 1. 基本分析
print("1. 基本分析:")
print(f"  长度: {len(parsed_sql)}")
print(f"  括号: (={parsed_sql.count('(')}, )={parsed_sql.count(')')}")
print(f"  包含VALUES: {'VALUES' in parsed_sql.upper()}")
print(f"  包含#{{: {'#{' in parsed_sql}")
print()

# 2. 查找表名
print("2. 查找表名:")
table_match = re.search(r'insert\s+into\s+([^\s(]+)', parsed_sql.lower())
if table_match:
    table_name = table_match.group(1)
    table_end = parsed_sql.lower().find(table_name) + len(table_name)
    print(f"  表名: {table_name}")
    print(f"  表名结束位置: {table_end}")
    
    # 表名后的内容
    after_table = parsed_sql[table_end:].strip()
    print(f"  表名后内容前100字符: {after_table[:100]}...")
else:
    print("  未找到表名")

# 3. 查找第一个参数位置
print("\n3. 查找参数位置:")
first_param = parsed_sql.find('#{')
if first_param > 0:
    print(f"  第一个参数位置: {first_param}")
    
    # 分割列名和值
    columns_part = parsed_sql[:first_param].strip()
    values_part = parsed_sql[first_param:].strip()
    
    print(f"  列名部分长度: {len(columns_part)}")
    print(f"  值部分长度: {len(values_part)}")
    
    # 提取列名部分（移除表名）
    if columns_part.startswith('insert into'):
        # 找到表名结束
        table_match2 = re.search(r'insert\s+into\s+([^\s]+)', columns_part.lower())
        if table_match2:
            table_name2 = table_match2.group(1)
            table_end2 = columns_part.lower().find(table_name2) + len(table_name2)
            columns_only = columns_part[table_end2:].strip()
            print(f"  纯列名部分: {columns_only[:100]}...")
            
            # 分析列名格式
            print(f"  列名是否包含逗号: {',' in columns_only}")
            print(f"  列名是否包含MTM_: {'MTM_' in columns_only}")
            
            # 分割列名
            columns_list = [col.strip() for col in re.split(r'\s*,\s*', columns_only) if col.strip()]
            print(f"  列名数量: {len(columns_list)}")
            print(f"  列名列表: {columns_list[:5]}...")
    
    # 分析值部分
    print(f"\n  值部分前100字符: {values_part[:100]}...")
    
    # 清理值部分
    values_clean = re.sub(r'\s+', ' ', values_part).strip()
    if values_clean.endswith(','):
        values_clean = values_clean[:-1].strip()
    
    print(f"  清理后值部分: {values_clean[:100]}...")
    
    # 分割值
    values_list = []
    # 简单的分割逻辑：按逗号分割，但要注意参数中的逗号
    temp = ''
    depth = 0  # 大括号深度
    for char in values_clean:
        if char == '{':
            depth += 1
        elif char == '}':
            depth -= 1
        
        if char == ',' and depth == 0:
            if temp.strip():
                values_list.append(temp.strip())
            temp = ''
        else:
            temp += char
    
    if temp.strip():
        values_list.append(temp.strip())
    
    print(f"  值数量: {len(values_list)}")
    print(f"  值列表前5个: {values_list[:5]}")
    
    # 检查列名和值数量是否匹配
    if 'columns_only' in locals() and columns_list and values_list:
        print(f"\n  列名数量: {len(columns_list)}, 值数量: {len(values_list)}")
        if len(columns_list) == len(values_list):
            print(f"  ✅ 列名和值数量匹配")
        else:
            print(f"  ⚠️ 列名和值数量不匹配")

# 4. 尝试修复
print("\n4. 尝试修复:")
def enhanced_fix_insert(sql_text):
    """增强的INSERT语句修复"""
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
        print("  ⚠️ 检测到INSERT语句缺少括号")
        
        # 尝试找到表名
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
                
                print(f"    列名部分: {columns_part[:50]}...")
                print(f"    值部分: {values_part[:50]}...")
                
                # 清理列名部分
                columns_clean = re.sub(r'\s+', ' ', columns_part).strip()
                # 清理值部分
                values_clean = re.sub(r'\s+', ' ', values_part).strip()
                
                # 移除值部分的末尾逗号
                if values_clean.endswith(','):
                    values_clean = values_clean[:-1].strip()
                
                # 检查是否需要添加VALUES关键字
                has_values = 'values' in sql_lower
                if not has_values:
                    print(f"    ⚠️ 缺少VALUES关键字，将添加")
                
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
                
                print(f"    修复后SQL: {fixed_sql[:100]}...")
                return fixed_sql
            else:
                print(f"    ❌ 未找到参数分界点")
    
    return sql_text

fixed_sql = enhanced_fix_insert(parsed_sql)
print(f"  修复后SQL长度: {len(fixed_sql)}")
print(f"  修复后SQL括号: (={fixed_sql.count('(')}, )={fixed_sql.count(')')}")
print(f"  修复后SQL前150字符: {fixed_sql[:150]}")

# 5. 最终验证
print("\n5. 最终验证:")
if fixed_sql.count('(') >= 2 and fixed_sql.count(')') >= 2:
    print(f"  ✅ 修复成功")
    print(f"    开括号: {fixed_sql.count('(')}, 闭括号: {fixed_sql.count(')')}")
    print(f"    包含VALUES: {'VALUES' in fixed_sql.upper()}")
    
    # 检查结构
    first_paren = fixed_sql.find('(')
    last_paren = fixed_sql.rfind(')')
    values_pos = fixed_sql.lower().find('values')
    
    print(f"    第一个括号位置: {first_paren}")
    print(f"    VALUES位置: {values_pos}")
    print(f"    最后一个括号位置: {last_paren}")
    
    if first_paren < last_paren and values_pos > 0:
        print(f"  ✅ 结构正确")
else:
    print(f"  ❌ 修复失败")

print("\n" + "=" * 80)
print("调试完成")
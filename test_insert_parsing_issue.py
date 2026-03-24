#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试INSERT语句解析问题
重现用户报告的问题
"""

import sys
import os
import re

# 设置路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'sql_ai_analyzer'))

print("测试INSERT语句解析问题")
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

print("1. 原始SQL:")
print(original_sql)
print("\n" + "-" * 80)

print("\n2. 解析出来的SQL（有问题）:")
print(parsed_sql)
print("\n" + "-" * 80)

# 分析问题
print("\n3. 问题分析:")
print("原始SQL结构:")
print("  - INSERT INTO table_name (col1, col2, ...) VALUES (val1, val2, ...)")
print("解析出来的SQL问题:")
print("  - 列名和值混在一起，没有正确的括号分隔")
print("  - 格式混乱，有多余的空行和缩进")
print("  - 结尾有逗号")

# 测试正则表达式匹配
print("\n4. 测试正则表达式匹配:")

# 测试INSERT语句表名提取
insert_pattern = r'\bINSERT\s+(?:INTO\s+)?([a-zA-Z_][\w\.]*|`[^`]+`|\'[^\']+\'|"[^"]+")(?=\s*(?:\([^)]+\)\s+VALUES|VALUES|SELECT|;|$))'
matches = re.findall(insert_pattern, original_sql, re.IGNORECASE)
print(f"  表名提取: {matches} (期望: ['MONTHLY_TRAN_MSG'])")

# 测试参数提取
param_pattern = r'#\{([^}]+)\}'
params = re.findall(param_pattern, original_sql)
print(f"  参数提取: {params}")
print(f"  参数数量: {len(params)} (期望: 8)")

# 测试列名提取
print("\n5. 测试列名提取:")
# 提取括号内的列名
col_match = re.search(r'\(([^)]+)\)', original_sql.split('\n(')[1] if '\n(' in original_sql else original_sql)
if col_match:
    col_text = col_match.group(1)
    # 清理列名
    columns = [col.strip() for col in re.split(r',\s*', col_text) if col.strip()]
    print(f"  列名: {columns}")
    print(f"  列数量: {len(columns)} (期望: 8)")

# 测试值提取
print("\n6. 测试值提取:")
# 提取VALUES后面的括号内容
values_section = re.search(r'VALUES\s*\(([^)]+)\)', original_sql, re.IGNORECASE | re.DOTALL)
if values_section:
    values_text = values_section.group(1)
    # 清理值
    values = [val.strip() for val in re.split(r',\s*', values_text) if val.strip()]
    print(f"  值: {values}")
    print(f"  值数量: {len(values)} (期望: 8)")

# 检查列和值是否对应
if 'columns' in locals() and 'values' in locals():
    print(f"\n7. 列值对应检查:")
    if len(columns) == len(values):
        print(f"  列和值数量匹配: {len(columns)} = {len(values)}")
        for i, (col, val) in enumerate(zip(columns, values)):
            print(f"    {col} -> {val}")
    else:
        print(f"  列和值数量不匹配: 列={len(columns)}, 值={len(values)}")

# 测试参数提取器
print("\n8. 测试参数提取器逻辑:")
try:
    from sql_ai_analyzer.data_collector.param_extractor import ParamExtractor
    
    # 创建简单的logger
    import logging
    logger = logging.getLogger('test')
    logger.setLevel(logging.WARNING)
    
    extractor = ParamExtractor(original_sql, logger)
    
    # 提取参数
    params = extractor.extract_params()
    print(f"  提取到的参数: {[p['param'] for p in params]}")
    
    # 生成替换后的SQL
    replaced_sql, tables = extractor.generate_replaced_sql()
    print(f"  替换后的SQL前100字符: {replaced_sql[:100]}...")
    print(f"  提取的表名: {tables}")
    
    # 检查替换是否正确
    original_params = re.findall(r'#\{([^}]+)\}', original_sql)
    replaced_params = re.findall(r'#\{([^}]+)\}', replaced_sql)
    print(f"  原始参数数量: {len(original_params)}")
    print(f"  替换后剩余参数数量: {len(replaced_params)}")
    
except Exception as e:
    print(f"  导入ParamExtractor失败: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("测试完成")

# 总结问题
print("\n总结:")
print("1. 原始INSERT语句结构正确")
print("2. 解析出来的SQL格式混乱，列名和值没有正确对应")
print("3. 问题可能出现在:")
print("   - SQL解析器没有正确处理多行SQL")
print("   - 参数提取器在处理INSERT语句时有问题")
print("   - 预处理过程中格式被破坏")
print("\n需要修复SQL解析器以正确处理INSERT语句的结构")
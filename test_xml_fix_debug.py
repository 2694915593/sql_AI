#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试XML标签移除问题
"""

import re
import sys
import os

print("调试XML标签移除问题")
print("=" * 80)

# 测试正则表达式
test_sqls = [
    "<select>SELECT * FROM users</select>",
    "<select>\nSELECT * FROM users\n</select>",
    "<query><select>SELECT * FROM users</select></query>",
    "<insert>INSERT INTO users VALUES (1, 'test')</insert>",
    "<update>UPDATE users SET name = 'test' WHERE id = 1</update>",
    "<delete>DELETE FROM users WHERE id = 1</delete>",
    "<sql><select>SELECT * FROM users WHERE id = 1</select></sql>",
    "<statement type=\"select\">SELECT * FROM users</statement>",
    "<select id=\"query1\">SELECT * FROM users</select>",
    "<select><![CDATA[SELECT * FROM users]]></select>",
    "<sql type=\"query\"><select>SELECT name FROM users</select></sql>",
    "SELECT * FROM users",  # 没有标签
    "<select>SELECT * FROM users",  # 没有闭合标签
    "SELECT * FROM users</select>",  # 没有开始标签
]

print("正则表达式测试:")
print("-" * 80)

pattern1 = r'<[^>]+>'
pattern2 = r'<[^>]+/>'

for sql in test_sqls:
    print(f"\n原始SQL: {sql[:60]}...")
    
    # 测试第一个正则表达式
    result1 = re.sub(pattern1, ' ', sql)
    print(f"  移除<tag>后: {result1[:60]}...")
    
    # 测试第二个正则表达式
    result2 = re.sub(pattern2, ' ', result1)
    print(f"  移除自闭合后: {result2[:60]}...")
    
    # 压缩空格
    result3 = re.sub(r'\s+', ' ', result2).strip()
    print(f"  压缩空格后: {result3[:60]}...")
    
    # 检查是否以SELECT等关键字开头
    if result3:
        sql_upper = result3.upper()
        dml_keywords = ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'MERGE', 'CALL', 'EXPLAIN']
        found = False
        for keyword in dml_keywords:
            if sql_upper.startswith(keyword):
                print(f"  ✓ 检测为: {keyword}")
                found = True
                break
        if not found:
            print(f"  ✗ 未识别为DML，开头为: {result3[:20]}")
    else:
        print("  ✗ 处理后的SQL为空")

print("\n\n分析detect_sql_type方法:")
print("-" * 80)

# 从文件读取方法
metadata_collector_path = os.path.join('sql_ai_analyzer', 'data_collector', 'metadata_collector.py')
try:
    with open(metadata_collector_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 查找detect_sql_type方法
    import re as regex
    method_pattern = r'def detect_sql_type\(self, sql_text: str\) -> str:.*?(?=\n    def|\n\n)'
    match = regex.search(method_pattern, content, regex.DOTALL)
    
    if match:
        method_text = match.group(0)
        print("找到detect_sql_type方法:")
        print("-" * 40)
        print(method_text[:500])
        print("..." if len(method_text) > 500 else "")
    else:
        print("未找到detect_sql_type方法")
        
except Exception as e:
    print(f"读取文件失败: {e}")

print("\n\n手动测试XML标签移除逻辑:")
print("-" * 80)

def manual_detect_sql_type(sql_text: str) -> str:
    """手动实现detect_sql_type逻辑"""
    if not sql_text:
        return "UNKNOWN"
    
    # 移除XML标签（如<select>、<insert>等）
    import re
    
    print(f"  输入: {sql_text[:60]}...")
    
    # 移除所有<tag>...</tag>格式的XML标签，但保留标签内的内容
    sql_text = re.sub(r'<[^>]+>', ' ', sql_text)
    print(f"  移除<tag>后: {sql_text[:60]}...")
    
    # 移除自闭合标签
    sql_text = re.sub(r'<[^>]+/>', ' ', sql_text)
    print(f"  移除自闭合后: {sql_text[:60]}...")
    
    # 压缩多余空格
    sql_text = re.sub(r'\s+', ' ', sql_text).strip()
    print(f"  压缩空格后: {sql_text[:60]}...")
    
    if not sql_text:
        print("  → 结果为: UNKNOWN (处理后的SQL为空)")
        return "UNKNOWN"
    
    sql_upper = sql_text.strip().upper()
    print(f"  大写后: {sql_upper[:60]}...")
    
    # DML语句 (数据操作语言)
    dml_keywords = ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'MERGE', 'CALL', 'EXPLAIN']
    for keyword in dml_keywords:
        if sql_upper.startswith(keyword):
            print(f"  → 匹配到关键字: {keyword}")
            return "DML"
    
    # DDL语句 (数据定义语言)
    ddl_keywords = ['CREATE', 'ALTER', 'DROP', 'TRUNCATE', 'RENAME', 'COMMENT']
    for keyword in ddl_keywords:
        if sql_upper.startswith(keyword):
            print(f"  → 匹配到关键字: {keyword}")
            return "DDL"
    
    # DCL语句 (数据控制语言)
    dcl_keywords = ['GRANT', 'REVOKE']
    for keyword in dcl_keywords:
        if sql_upper.startswith(keyword):
            print(f"  → 匹配到关键字: {keyword}")
            return "DCL"
    
    # TCL语句 (事务控制语言)
    tcl_keywords = ['COMMIT', 'ROLLBACK', 'SAVEPOINT', 'SET TRANSACTION']
    for keyword in tcl_keywords:
        if sql_upper.startswith(keyword):
            print(f"  → 匹配到关键字: {keyword}")
            return "TCL"
    
    print(f"  → 结果为: UNKNOWN")
    return "UNKNOWN"

print("\n测试几个关键案例:")
test_cases = [
    "<select>SELECT * FROM users</select>",
    "<select>\nSELECT * FROM users\n</select>",
    "<query><select>SELECT * FROM users</select></query>",
    "SELECT * FROM users",  # 正常情况
]

for sql in test_cases:
    print(f"\n{'='*60}")
    print(f"测试: {sql[:50]}...")
    result = manual_detect_sql_type(sql)
    print(f"最终结果: {result}")

print("\n\n测试更复杂的XML嵌套:")
complex_cases = [
    ("<select><![CDATA[SELECT * FROM users]]></select>", "SELECT"),
    ("<sql type=\"query\"><select>SELECT name FROM users</select></sql>", "SELECT"),
    ("<statement><select>SELECT * FROM users</select></statement>", "SELECT"),
]

for sql, expected in complex_cases:
    print(f"\n{'='*60}")
    print(f"测试复杂XML: {sql[:50]}...")
    result = manual_detect_sql_type(sql)
    print(f"结果: {result}, 期望: {expected}, {'✓' if result == 'DML' else '✗'}")
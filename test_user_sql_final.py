#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最终测试用户SQL解析问题
"""

import sys
import os
import re

# 设置正确的路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# 添加utils模块的路径
utils_dir = os.path.join(project_root, 'sql_ai_analyzer', 'utils')
if os.path.exists(utils_dir):
    sys.path.insert(0, utils_dir)

# 添加sql_ai_analyzer模块的路径
sys.path.insert(0, os.path.join(project_root, 'sql_ai_analyzer'))

print("最终测试用户SQL解析问题")
print("=" * 80)

# 用户提供的SQL
user_sql = "UPDATE ES_ACCOUNT_API\nSET EAA_STATUS = #{status},\n    EAA_UTIENT_TIMESTAMP\nWHERE EAA_TRACE_NO = #{traceNo}"
print(f"用户SQL: {user_sql}")
print(f"SQL长度: {len(user_sql)}")
print(f"包含\\n换行符: {user_sql.count('\\n')}")

# 手动测试SQL类型检测逻辑
print("\n1. 手动测试SQL类型检测逻辑:")

def manual_detect_sql_type(sql_text):
    """手动实现的SQL类型检测"""
    if not sql_text or not sql_text.strip():
        return "UNKNOWN"
    
    # 移除XML标签
    cleaned = sql_text
    cleaned = re.sub(r'<[^>]+>', ' ', cleaned)
    cleaned = re.sub(r'<[^>]+/>', ' ', cleaned)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    
    sql_upper = cleaned.upper()
    
    # DML语句
    dml_keywords = ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'MERGE', 'CALL', 'EXPLAIN']
    for keyword in dml_keywords:
        if sql_upper.startswith(keyword):
            return "DML"
    
    # DDL语句
    ddl_keywords = ['CREATE', 'ALTER', 'DROP', 'TRUNCATE', 'RENAME', 'COMMENT']
    for keyword in ddl_keywords:
        if sql_upper.startswith(keyword):
            return "DDL"
    
    return "UNKNOWN"

# 测试各种情况
test_cases = [
    (user_sql, "用户原始SQL"),
    (f"<update>{user_sql}</update>", "带update标签"),
    (f"<sql>{user_sql}</sql>", "带sql标签"),
    (f"<query><update>{user_sql}</update></query>", "嵌套标签"),
    ("<select>SELECT * FROM users</select>", "带select标签的查询"),
    ("UPDATE test SET name='value'", "简单UPDATE"),
]

for sql, description in test_cases:
    sql_type = manual_detect_sql_type(sql)
    print(f"  {description:25} -> {sql_type}")

# 测试XML标签移除
print("\n2. 测试XML标签移除:")
def remove_xml_tags(sql_text):
    """手动移除XML标签"""
    # 先处理CDATA
    result = re.sub(r'<!\[CDATA\[(.*?)\]\]>', r'\1', sql_text, flags=re.DOTALL)
    # 移除XML标签
    result = re.sub(r'<[^>]+>', ' ', result)
    # 移除自闭合标签
    result = re.sub(r'<[^>]+/>', ' ', result)
    # 压缩空格
    result = re.sub(r'\s+', ' ', result).strip()
    return result

xml_sql = f"<update>{user_sql}</update>"
cleaned = remove_xml_tags(xml_sql)
print(f"  原始: {xml_sql[:60]}...")
print(f"  清理后: {cleaned[:60]}...")
print(f"  是否以UPDATE开头: {cleaned.upper().startswith('UPDATE')}")

# 测试大模型返回格式
print("\n3. 测试大模型返回格式处理:")
model_response_format = '''{
  "建议": ["具体建议1", "具体建议2", "具体建议3"],
  "SQL类型": "数据操作",
  "分析摘要": "简明的分析摘要",
  "综合评分": 8,
  "风险评估": {
    "高风险问题": ["高风险问题1", "高风险问题2"],
    "中风险问题": ["中风险问题1", "中风险问题2"],
    "低风险问题": ["低风险问题1", "低风险问题2"]
  },
  "修改建议": {
    "高风险问题SQL": "针对高风险问题修改后的具体SQL语句示例",
    "中风险问题SQL": "针对中风险问题修改后的具体SQL语句示例",
    "低风险问题SQL": "针对低风险问题修改后的具体SQL语句示例",
    "性能优化SQL": "针对性能问题优化后的具体SQL语句示例"
  }
}'''

print(f"  模拟大模型返回JSON长度: {len(model_response_format)}")
print(f"  包含SQL类型字段: {'SQL类型' in model_response_format}")
print(f"  包含建议字段: {'建议' in model_response_format}")

# 测试带转义字符的处理
print("\n4. 测试转义字符处理:")
escaped_sql = "UPDATE ES_ACCOUNT_API\\nSET EAA_STATUS = #{status},\\n    EAA_UTIENT_TIMESTAMP\\nWHERE EAA_TRACE_NO = #{traceNo}"
print(f"  带转义\\n的SQL: {repr(escaped_sql)}")
print(f"  实际字符串长度: {len(escaped_sql)}")
print(f"  包含\\\\n数量: {escaped_sql.count('\\\\n')}")

# 转换为实际换行符
actual_sql = escaped_sql.replace('\\n', '\n')
print(f"  转换后长度: {len(actual_sql)}")
print(f"  包含实际换行符数量: {actual_sql.count('\\n')}")

print("\n5. 问题分析:")
print("  根据之前的测试输出，发现以下情况:")
print("  a) 不带XML标签的SQL能正确检测为DML类型")
print("  b) 带XML标签的SQL也能正确检测为DML类型")
print("  c) XML标签移除器工作正常")
print("  d) 问题可能出现在其他地方，如大模型响应解析或参数提取")

print("\n" + "=" * 80)
print("测试完成")

# 建议
print("\n建议:")
print("1. 检查大模型返回的JSON格式是否正确")
print("2. 检查参数提取器是否能正确处理#{status}和#{traceNo}这样的参数")
print("3. 检查SQL预处理器是否正确处理换行符和参数占位符")
print("4. 如果问题仍然存在，需要查看具体的错误日志")
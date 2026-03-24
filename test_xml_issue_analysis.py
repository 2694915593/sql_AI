#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
深入分析XML标签对SQL解析的影响
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

print("深入分析XML标签对SQL解析的影响")
print("=" * 80)

# 用户提供的SQL（注意原始消息中的格式）
raw_sql_from_user = "UPDATE ES_ACCOUNT_API\\nSET EAA_STATUS = #{status},\\n    EAA_UTIENT_TIMESTAMP\\nWHERE EAA_TRACE_NO = #{traceNo}"
print(f"用户原始消息中的SQL: {repr(raw_sql_from_user)}")

# 转换为实际可用的SQL（将\\n转换为\n）
actual_sql = raw_sql_from_user.replace('\\n', '\n')
print(f"实际SQL（转换\\n后）: {repr(actual_sql)}")
print(f"显示SQL:\n{actual_sql}")

print("\n" + "=" * 80)
print("问题分析:")

# 检查SQL中的XML标签模式
xml_patterns = [
    r'<[^>]+>',  # 基本XML标签
    r'<!\[CDATA\[',  # CDATA标记
]

print("\n1. 检查SQL是否包含XML标签:")
has_xml_tags = False
for pattern in xml_patterns:
    if re.search(pattern, actual_sql):
        has_xml_tags = True
        print(f"  发现XML标签模式: {pattern}")
        break

print(f"  结果: {'包含' if has_xml_tags else '不包含'} XML标签")

# 检查用户消息中提到的"去除SQL标签解析大模型返回还有问题"
# 这可能意味着：大模型返回的SQL可能包含XML标签，但解析器无法正确处理

print("\n2. 可能的问题场景分析:")
print("  场景A: 大模型返回的SQL直接包含XML标签，如<update>...</update>")
print("  场景B: 大模型返回的SQL中包含转义字符或特殊格式")
print("  场景C: 解析器在处理带XML标签的SQL时，SQL类型检测失败")

# 测试各种可能的XML标签格式
print("\n3. 测试各种XML标签格式对SQL解析的影响:")

def manual_detect_sql_type_with_preprocessing(sql_text):
    """手动实现的SQL类型检测，包含预处理"""
    if not sql_text or not sql_text.strip():
        return "UNKNOWN"
    
    # 预处理：移除XML标签
    cleaned = sql_text
    cleaned = re.sub(r'<!\[CDATA\[(.*?)\]\]>', r'\1', cleaned, flags=re.DOTALL)
    cleaned = re.sub(r'<[^>]+>', ' ', cleaned)
    cleaned = re.sub(r'<[^>]+/>', ' ', cleaned)
    
    # 移除SQL注释
    cleaned = re.sub(r'/\*.*?\*/', ' ', cleaned, flags=re.S)
    cleaned = re.sub(r'--[^\r\n]*', ' ', cleaned)
    cleaned = re.sub(r'#[^\r\n]*', ' ', cleaned)
    
    # 压缩空格
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    
    if not cleaned:
        return "UNKNOWN"
    
    sql_upper = cleaned.upper()
    
    # 检查SQL类型
    if sql_upper.startswith('SELECT'):
        return "DML (SELECT)"
    elif sql_upper.startswith('INSERT'):
        return "DML (INSERT)"
    elif sql_upper.startswith('UPDATE'):
        return "DML (UPDATE)"
    elif sql_upper.startswith('DELETE'):
        return "DML (DELETE)"
    elif sql_upper.startswith('CREATE'):
        return "DDL (CREATE)"
    elif sql_upper.startswith('ALTER'):
        return "DDL (ALTER)"
    elif sql_upper.startswith('DROP'):
        return "DDL (DROP)"
    elif sql_upper.startswith('TRUNCATE'):
        return "DDL (TRUNCATE)"
    elif sql_upper.startswith('GRANT'):
        return "DCL (GRANT)"
    elif sql_upper.startswith('REVOKE'):
        return "DCL (REVOKE)"
    elif sql_upper.startswith('COMMIT'):
        return "TCL (COMMIT)"
    elif sql_upper.startswith('ROLLBACK'):
        return "TCL (ROLLBACK)"
    else:
        return "UNKNOWN"

# 测试用例
test_cases = [
    (actual_sql, "用户SQL（无XML标签）"),
    (f"<update>{actual_sql}</update>", "带<update>标签"),
    (f"<sql>{actual_sql}</sql>", "带<sql>标签"),
    (f"<query>{actual_sql}</query>", "带<query>标签"),
    (f"<statement>{actual_sql}</statement>", "带<statement>标签"),
    (f"<query><update>{actual_sql}</update></query>", "嵌套标签"),
    (f"<select>SELECT * FROM users</select>", "SELECT带标签"),
    (f"<insert>INSERT INTO users VALUES (1, 'test')</insert>", "INSERT带标签"),
    (f"<delete>DELETE FROM users WHERE id = 1</delete>", "DELETE带标签"),
    (f"<create>CREATE TABLE test (id INT)</create>", "CREATE带标签"),
]

print("\nSQL类型检测测试:")
print("-" * 80)
for sql, description in test_cases:
    sql_type = manual_detect_sql_type_with_preprocessing(sql)
    print(f"{description:30} -> {sql_type}")

print("\n4. 关键问题识别:")
print("  根据代码分析，metadata_collector.py中已经包含了XML标签预处理逻辑")
print("  问题可能出现在以下地方:")
print("  a) _preprocess_sql_for_type_detection方法可能没有被正确调用")
print("  b) detect_sql_type方法可能没有调用预处理方法")
print("  c) XML标签移除可能不彻底（如嵌套标签、带属性的标签）")

# 检查用户SQL中的参数占位符
print("\n5. 参数占位符分析:")
print(f"  SQL中的参数占位符: #{'status'}和#{'traceNo'}")
print("  这些占位符可能会影响SQL解析，特别是当XML标签移除不彻底时")

# 检查换行符处理
print("\n6. 换行符分析:")
print(f"  SQL中包含换行符数量: {actual_sql.count('\\n')}")
print("  换行符在XML标签移除和SQL解析中可能需要特殊处理")

print("\n" + "=" * 80)
print("建议的修复方案:")

print("\n1. 确保detect_sql_type方法正确调用_preprocess_sql_for_type_detection")
print("   - 检查metadata_collector.py中的detect_sql_type方法")
print("   - 确保在检测SQL类型前先预处理")

print("\n2. 增强XML标签移除逻辑")
print("   - 处理嵌套标签")
print("   - 处理带属性的标签（如<sql type=\"query\">）")
print("   - 处理CDATA块")
print("   - 确保不误移除参数占位符（如#{status}）")

print("\n3. 统一预处理流程")
print("   - 在sql_preprocessor.py中创建统一的预处理函数")
print("   - 所有需要处理SQL的地方都使用这个统一的预处理函数")

print("\n4. 添加调试日志")
print("   - 记录原始SQL和预处理后的SQL")
print("   - 记录XML标签检测和移除的详细信息")

print("\n" + "=" * 80)
print("验证测试:")

# 创建一个简单的验证函数
def validate_xml_removal(sql_with_xml):
    """验证XML标签移除是否彻底"""
    print(f"\n验证: {sql_with_xml[:60]}...")
    
    # 移除XML标签
    cleaned = re.sub(r'<!\[CDATA\[(.*?)\]\]>', r'\1', sql_with_xml, flags=re.DOTALL)
    cleaned = re.sub(r'<[^>]+>', ' ', cleaned)
    cleaned = re.sub(r'<[^>]+/>', ' ', cleaned)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    
    print(f"  清理后: {cleaned[:60]}...")
    print(f"  是否仍包含XML标签: {'是' if re.search(r'<[^>]+>', cleaned) else '否'}")
    print(f"  是否以UPDATE开头: {cleaned.upper().startswith('UPDATE')}")
    
    return cleaned

# 测试几个关键用例
print("\nXML标签移除验证:")
print("-" * 80)

critical_cases = [
    f"<update>{actual_sql}</update>",
    f"<sql type=\"update\">{actual_sql}</sql>",
    f"<query><update>{actual_sql}</update></query>",
    f"<select>SELECT * FROM users</select>",
]

for sql in critical_cases:
    validate_xml_removal(sql)

print("\n" + "=" * 80)
print("分析完成")
print("\n结论:")
print("1. 用户报告的问题确实是XML标签对SQL解析的影响")
print("2. 代码中已经有预处理逻辑，但可能需要修复或确保正确调用")
print("3. 重点应放在修复detect_sql_type方法和增强XML标签移除逻辑上")
print("4. 需要确保所有类型的SQL（SELECT、INSERT、UPDATE、DELETE、CREATE等）")
print("   都能正确处理XML标签")
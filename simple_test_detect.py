#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最简单的detect_sql_type测试
"""

import sys
import os

# 清理模块缓存
sys.path_importer_cache.clear()

# 删除相关模块
for mod in list(sys.modules.keys()):
    if 'sql_ai_analyzer' in mod:
        del sys.modules[mod]

# 重新设置路径
project_root = os.path.dirname(os.path.abspath(__file__))
sql_ai_analyzer_dir = os.path.join(project_root, 'sql_ai_analyzer')
sys.path.insert(0, project_root)
sys.path.insert(0, sql_ai_analyzer_dir)

print("最简单的detect_sql_type测试")
print("=" * 80)

# 直接读取并执行detect_sql_type方法
metadata_collector_path = os.path.join(sql_ai_analyzer_dir, 'data_collector', 'metadata_collector.py')
print(f"读取文件: {metadata_collector_path}")

try:
    with open(metadata_collector_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 提取detect_sql_type方法
    import re as regex
    method_pattern = r'def detect_sql_type\(self, sql_text: str\) -> str:(.*?)(?=\n    def|\n\n|\Z)'
    match = regex.search(method_pattern, content, regex.DOTALL)
    
    if match:
        method_body = match.group(1)
        print("找到detect_sql_type方法体")
        print("-" * 40)
        # 只显示前300个字符
        print(method_body[:300] + "..." if len(method_body) > 300 else method_body)
    else:
        print("未找到detect_sql_type方法")
        
except Exception as e:
    print(f"读取文件失败: {e}")

print("\n\n直接测试detect_sql_type方法逻辑:")
print("-" * 80)

# 创建一个简单的测试类
class SimpleMetadataCollector:
    def detect_sql_type(self, sql_text: str) -> str:
        """
        检测SQL语句类型

        Args:
            sql_text: SQL语句文本

        Returns:
            SQL类型: DML, DDL, DCL, TCL 或 UNKNOWN
        """
        if not sql_text:
            return "UNKNOWN"
        
        # 移除XML标签（如<select>、<insert>等）
        import re
        
        # 先处理CDATA部分，保留内容
        sql_text = re.sub(r'<!\[CDATA\[(.*?)\]\]>', r'\1', sql_text, flags=re.DOTALL)
        
        # 移除所有<tag>...</tag>格式的XML标签，但保留标签内的内容
        sql_text = re.sub(r'<[^>]+>', ' ', sql_text)
        # 移除自闭合标签
        sql_text = re.sub(r'<[^>]+/>', ' ', sql_text)
        # 压缩多余空格
        sql_text = re.sub(r'\s+', ' ', sql_text).strip()
        
        if not sql_text:
            return "UNKNOWN"
        
        print(f"  清洗后SQL: {sql_text[:50]}...")
        print(f"  大写SQL: {sql_text.upper()[:50]}...")
        
        sql_upper = sql_text.strip().upper()
        
        # DML语句 (数据操作语言)
        dml_keywords = ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'MERGE', 'CALL', 'EXPLAIN']
        for keyword in dml_keywords:
            if sql_upper.startswith(keyword):
                print(f"  匹配到DML关键字: {keyword}")
                return "DML"
        
        # DDL语句 (数据定义语言)
        ddl_keywords = ['CREATE', 'ALTER', 'DROP', 'TRUNCATE', 'RENAME', 'COMMENT']
        for keyword in ddl_keywords:
            if sql_upper.startswith(keyword):
                print(f"  匹配到DDL关键字: {keyword}")
                return "DDL"
        
        # DCL语句 (数据控制语言)
        dcl_keywords = ['GRANT', 'REVOKE']
        for keyword in dcl_keywords:
            if sql_upper.startswith(keyword):
                print(f"  匹配到DCL关键字: {keyword}")
                return "DCL"
        
        # TCL语句 (事务控制语言)
        tcl_keywords = ['COMMIT', 'ROLLBACK', 'SAVEPOINT', 'SET TRANSACTION']
        for keyword in tcl_keywords:
            if sql_upper.startswith(keyword):
                print(f"  匹配到TCL关键字: {keyword}")
                return "TCL"
        
        print(f"  未匹配到任何关键字")
        return "UNKNOWN"

# 测试
collector = SimpleMetadataCollector()

test_cases = [
    ("SELECT * FROM users", "SELECT"),
    ("<select>SELECT * FROM users</select>", "SELECT (with XML tags)"),
    ("<select>\nSELECT * FROM users\n</select>", "SELECT (with XML tags and newlines)"),
    ("<query><select>SELECT * FROM users</select></query>", "SELECT (nested XML tags)"),
    ("<insert>INSERT INTO users VALUES (1, 'test')</insert>", "INSERT (with XML tags)"),
]

print("\n测试结果:")
for sql, description in test_cases:
    print(f"\n{'-'*60}")
    print(f"测试: {description}")
    print(f"原始SQL: {sql[:60]}...")
    result = collector.detect_sql_type(sql)
    expected = "DML" if any(keyword.lower() in description.lower() for keyword in ["SELECT", "INSERT", "UPDATE", "DELETE"]) else "UNKNOWN"
    status = "✓" if result == expected else "✗"
    print(f"结果: {result}, 期望: {expected}, {status}")

print("\n\n测试CDATA情况:")
cdata_sql = "<select><![CDATA[SELECT * FROM users]]></select>"
print(f"原始SQL: {cdata_sql}")
result = collector.detect_sql_type(cdata_sql)
print(f"结果: {result}, 期望: DML, {'✓' if result == 'DML' else '✗'}")
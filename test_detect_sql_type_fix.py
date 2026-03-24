#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直接测试detect_sql_type方法的修复
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

print("直接测试detect_sql_type方法的修复")
print("=" * 80)

try:
    # 导入MetadataCollector
    from sql_ai_analyzer.config.config_manager import ConfigManager
    from sql_ai_analyzer.data_collector.metadata_collector import MetadataCollector
    
    # 创建ConfigManager和MetadataCollector
    cm = ConfigManager()
    
    import logging
    logger = logging.getLogger('test')
    logger.setLevel(logging.INFO)
    
    collector = MetadataCollector(cm, logger)
    
    # 直接调用detect_sql_type方法
    print("直接调用detect_sql_type方法:")
    print("-" * 80)
    
    test_cases = [
        ("SELECT * FROM users", "SELECT"),
        ("<select>SELECT * FROM users</select>", "SELECT (with XML tags)"),
        ("<select>\nSELECT * FROM users\n</select>", "SELECT (with XML tags and newlines)"),
        ("<query><select>SELECT * FROM users</select></query>", "SELECT (nested XML tags)"),
        ("<insert>INSERT INTO users VALUES (1, 'test')</insert>", "INSERT (with XML tags)"),
        ("<update>UPDATE users SET name = 'test' WHERE id = 1</update>", "UPDATE (with XML tags)"),
        ("<delete>DELETE FROM users WHERE id = 1</delete>", "DELETE (with XML tags)"),
        ("<sql><select>SELECT * FROM users WHERE id = 1</select></sql>", "SELECT (nested in sql tag)"),
        ("<statement type=\"select\">SELECT * FROM users</statement>", "SELECT (with attributes)"),
        ("<select id=\"query1\">SELECT * FROM users</select>", "SELECT (with attribute)"),
        ("<select><![CDATA[SELECT * FROM users]]></select>", "SELECT (with CDATA)"),
    ]
    
    for sql, description in test_cases:
        result = collector.detect_sql_type(sql)
        expected = "DML" if any(keyword.lower() in description.lower() for keyword in ["SELECT", "INSERT", "UPDATE", "DELETE"]) else "UNKNOWN"
        
        status = "✓" if result == expected else "✗"
        print(f"{status} {description:50} -> {result:8} (期望: {expected})")
        
        # 如果是失败的情况，显示更多信息
        if result != expected:
            print(f"    原始SQL: {sql[:80]}...")
            # 手动测试XML标签移除
            import re
            cleaned = re.sub(r'<[^>]+>', ' ', sql)
            cleaned = re.sub(r'<[^>]+/>', ' ', cleaned)
            cleaned = re.sub(r'\s+', ' ', cleaned).strip()
            print(f"    清洗后: {cleaned[:80]}...")
            print(f"    大写后: {cleaned.upper()[:80]}...")
    
    print("\n\n分析CDATA问题:")
    print("-" * 80)
    
    # 特别测试CDATA情况
    cdata_sql = "<select><![CDATA[SELECT * FROM users]]></select>"
    print(f"原始SQL: {cdata_sql}")
    
    # 测试正则表达式
    import re
    
    # 当前的正则表达式
    pattern1 = r'<[^>]+>'
    result1 = re.sub(pattern1, ' ', cdata_sql)
    print(f"使用 <[^>]+> 后: {result1}")
    
    # 更复杂的正则表达式，需要正确处理CDATA
    # 先处理CDATA部分
    # 方法：先移除CDATA标记，保留内容
    text = cdata_sql
    text = re.sub(r'<!\[CDATA\[(.*?)\]\]>', r'\1', text, flags=re.DOTALL)
    print(f"移除CDATA标记后: {text}")
    
    # 然后移除XML标签
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'<[^>]+/>', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    print(f"移除XML标签后: {text}")
    
    # 更好的正则表达式：先处理CDATA，再处理普通XML标签
    def clean_xml_tags(sql_text):
        if not sql_text:
            return ""
        
        # 先处理CDATA部分，保留内容
        sql_text = re.sub(r'<!\[CDATA\[(.*?)\]\]>', r'\1', sql_text, flags=re.DOTALL)
        
        # 然后移除XML标签
        sql_text = re.sub(r'<[^>]+>', ' ', sql_text)
        sql_text = re.sub(r'<[^>]+/>', ' ', sql_text)
        
        # 压缩多余空格
        sql_text = re.sub(r'\s+', ' ', sql_text).strip()
        
        return sql_text
    
    print(f"\n使用clean_xml_tags函数:")
    for sql, description in test_cases:
        cleaned = clean_xml_tags(sql)
        print(f"{description:50} -> {cleaned[:40]}...")
    
except Exception as e:
    print(f"测试失败: {e}")
    import traceback
    traceback.print_exc()
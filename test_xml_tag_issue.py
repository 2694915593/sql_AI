#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试XML标签对SQL类型检测的影响
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

print("测试XML标签对SQL类型检测的影响")
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
    
    # 测试用例
    test_cases = [
        ("SELECT * FROM users", "SELECT"),
        ("select * from users", "SELECT"),
        ("INSERT INTO users VALUES (1, 'test')", "INSERT"),
        ("UPDATE users SET name = 'test' WHERE id = 1", "UPDATE"),
        ("DELETE FROM users WHERE id = 1", "DELETE"),
        ("<select>SELECT * FROM users</select>", "SELECT (with XML tags)"),
        ("<select>\nSELECT * FROM users\n</select>", "SELECT (with XML tags and newlines)"),
        ("<query><select>SELECT * FROM users</select></query>", "SELECT (nested XML tags)"),
        ("<insert>INSERT INTO users VALUES (1, 'test')</insert>", "INSERT (with XML tags)"),
        ("<update>UPDATE users SET name = 'test' WHERE id = 1</update>", "UPDATE (with XML tags)"),
        ("<delete>DELETE FROM users WHERE id = 1</delete>", "DELETE (with XML tags)"),
        ("<sql><select>SELECT * FROM users WHERE id = 1</select></sql>", "SELECT (nested in sql tag)"),
        ("<statement type=\"select\">SELECT * FROM users</statement>", "SELECT (with attributes)"),
        ("<!-- comment -->SELECT * FROM users", "SELECT (with SQL comment)"),
        ("<select>SELECT * FROM users</select> -- SQL comment", "SELECT (with XML tags and SQL comment)"),
    ]
    
    print("\n当前detect_sql_type方法测试结果:")
    print("-" * 80)
    
    for sql, description in test_cases:
        sql_type = collector.detect_sql_type(sql)
        print(f"{description:50} -> {sql_type}")
    
    # 检查_normalize_sql_for_explain方法
    print("\n\n_normalize_sql_for_explain方法测试结果:")
    print("-" * 80)
    
    for sql, description in test_cases[:5]:  # 只测试前几个
        normalized = collector._normalize_sql_for_explain(sql)
        print(f"{description:50} -> {normalized[:50]}...")
    
    # 测试带XML标签的
    print("\n\n带XML标签的_normalize_sql_for_explain测试:")
    print("-" * 80)
    
    xml_sqls = [
        "<select>SELECT * FROM users</select>",
        "<query><select>SELECT * FROM users</select></query>",
        "<select>SELECT * FROM users</select> -- comment",
    ]
    
    for sql in xml_sqls:
        normalized = collector._normalize_sql_for_explain(sql)
        print(f"{sql[:50]:50} -> {normalized[:50]}...")
    
except Exception as e:
    print(f"测试失败: {e}")
    import traceback
    traceback.print_exc()
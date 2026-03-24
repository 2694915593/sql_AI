#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试用户报告的UPDATE SQL解析问题
大模型返回的SQL：
UPDATE ES_ACCOUNT_API\nSET EAA_STATUS = #{status},\n    EAA_UTIENT_TIMESTAMP\nWHERE EAA_TRACE_NO = #{traceNo}
"""

import re
import sys
import os

# 添加路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sql_ai_analyzer'))

try:
    from utils.sql_preprocessor import SQLPreprocessor
    from ai_integration.xml_tag_remover import XmlTagRemover
except ImportError as e:
    print(f"导入错误: {e}")
    # 尝试直接导入
    import sql_ai_analyzer.utils.sql_preprocessor as preprocessor_module
    import sql_ai_analyzer.ai_integration.xml_tag_remover as xml_remover_module
    SQLPreprocessor = preprocessor_module.SQLPreprocessor
    XmlTagRemover = xml_remover_module.XmlTagRemover

def test_sql_preprocessor():
    """测试SQL预处理器"""
    print("=" * 80)
    print("测试SQL预处理器处理用户报告的SQL")
    print("=" * 80)
    
    # 用户提供的SQL（注意：\n需要处理）
    user_sql = "UPDATE ES_ACCOUNT_API\nSET EAA_STATUS = #{status},\n    EAA_UTIENT_TIMESTAMP\nWHERE EAA_TRACE_NO = #{traceNo}"
    
    # 也测试带XML标签的情况
    test_cases = [
        (user_sql, "用户原始SQL"),
        ("<update>" + user_sql + "</update>", "带<update>标签"),
        ("<sql>" + user_sql + "</sql>", "带<sql>标签"),
        ("<select>SELECT * FROM users</select>", "对照：带<select>标签"),
    ]
    
    preprocessor = SQLPreprocessor()
    
    for sql, description in test_cases:
        print(f"\n测试: {description}")
        print(f"原始SQL:")
        print(repr(sql))
        print(f"显示SQL:")
        print(sql)
        
        # 检查是否包含XML标签
        has_xml = preprocessor.contains_xml_tags(sql)
        print(f"包含XML标签: {has_xml}")
        
        # 预处理
        processed_sql, info = preprocessor.preprocess_sql(sql, mode="normalize")
        print(f"处理后SQL:")
        print(repr(processed_sql))
        print(f"显示处理后SQL:")
        print(processed_sql)
        print(f"预处理信息: {info.get('action', 'unknown')}")
        
        # 检测SQL类型
        sql_type = preprocessor.safe_detect_sql_type(sql)
        print(f"SQL类型: {sql_type}")

def test_xml_tag_remover():
    """测试XML标签移除器"""
    print("\n" + "=" * 80)
    print("测试XML标签移除器")
    print("=" * 80)
    
    # 创建简单的配置管理器模拟
    class MockConfigManager:
        def get_database_config(self):
            return {
                'host': None,
                'port': None,
                'user': None,
                'password': None,
                'database': None
            }
    
    config = MockConfigManager()
    remover = XmlTagRemover(config)
    
    # 测试用例
    test_cases = [
        ("UPDATE ES_ACCOUNT_API\nSET EAA_STATUS = #{status},\n    EAA_UTIENT_TIMESTAMP\nWHERE EAA_TRACE_NO = #{traceNo}", "用户原始SQL"),
        ("<update>UPDATE ES_ACCOUNT_API\nSET EAA_STATUS = #{status},\n    EAA_UTIENT_TIMESTAMP\nWHERE EAA_TRACE_NO = #{traceNo}</update>", "带update标签"),
        ("<sql>UPDATE ES_ACCOUNT_API\nSET EAA_STATUS = #{status},\n    EAA_UTIENT_TIMESTAMP\nWHERE EAA_TRACE_NO = #{traceNo}</sql>", "带sql标签"),
        ("<query><update>UPDATE ES_ACCOUNT_API\nSET EAA_STATUS = #{status},\n    EAA_UTIENT_TIMESTAMP\nWHERE EAA_TRACE_NO = #{traceNo}</update></query>", "嵌套标签"),
    ]
    
    for sql, description in test_cases:
        print(f"\n测试: {description}")
        print(f"原始SQL: {repr(sql[:100])}...")
        
        # 检查是否包含XML标签
        has_xml = remover._contains_xml_tags_regex(sql)
        print(f"包含XML标签: {has_xml}")
        
        if has_xml:
            # 使用正则表达式移除标签（因为可能没有实际的大模型连接）
            processed_sql, info = remover._remove_xml_tags_regex(sql, "normalize", {})
            print(f"处理后SQL: {repr(processed_sql[:100])}...")
            print(f"处理信息: {info.get('action', 'unknown')}")
            
            # 验证结果
            is_valid = remover._validate_model_result(processed_sql, sql)
            print(f"验证结果: {is_valid}")
        else:
            print("无需处理")

def test_regex_patterns():
    """测试正则表达式模式"""
    print("\n" + "=" * 80)
    print("测试正则表达式模式")
    print("=" * 80)
    
    test_strings = [
        "UPDATE ES_ACCOUNT_API\nSET EAA_STATUS = #{status},\n    EAA_UTIENT_TIMESTAMP\nWHERE EAA_TRACE_NO = #{traceNo}",
        "<update>UPDATE ES_ACCOUNT_API\nSET EAA_STATUS = #{status},\n    EAA_UTIENT_TIMESTAMP\nWHERE EAA_TRACE_NO = #{traceNo}</update>",
        "<sql>UPDATE ES_ACCOUNT_API\nSET EAA_STATUS = #{status},\n    EAA_UTIENT_TIMESTAMP\nWHERE EAA_TRACE_NO = #{traceNo}</sql>",
        "<query><update>UPDATE ES_ACCOUNT_API\nSET EAA_STATUS = #{status},\n    EAA_UTIENT_TIMESTAMP\nWHERE EAA_TRACE_NO = #{traceNo}</update></query>",
    ]
    
    # XML标签模式
    xml_pattern = r'<[^>]+>'
    
    for test_str in test_strings:
        print(f"\n测试字符串: {repr(test_str[:80])}...")
        
        # 查找所有XML标签
        matches = re.findall(xml_pattern, test_str)
        print(f"找到的XML标签: {matches}")
        
        # 移除标签
        cleaned = re.sub(xml_pattern, ' ', test_str)
        print(f"移除标签后: {repr(cleaned[:80])}...")
        
        # 压缩空格
        compressed = re.sub(r'\s+', ' ', cleaned).strip()
        print(f"压缩空格后: {repr(compressed[:80])}...")
        
        # 检查是否以UPDATE开头
        if compressed.upper().startswith('UPDATE'):
            print("✓ 以UPDATE开头")
        else:
            print(f"✗ 不以UPDATE开头，实际开头: {compressed[:20]}")

def test_issue_specific():
    """测试具体问题"""
    print("\n" + "=" * 80)
    print("测试具体问题：可能的问题分析")
    print("=" * 80)
    
    # 用户原始SQL（注意：用户消息中是\\n，在Python字符串中是\n）
    user_sql = "UPDATE ES_ACCOUNT_API\\nSET EAA_STATUS = #{status},\\n    EAA_UTIENT_TIMESTAMP\\nWHERE EAA_TRACE_NO = #{traceNo}"
    
    print(f"用户提供的SQL（带\\n转义）: {user_sql}")
    
    # 实际处理时，\\n会被视为两个字符：\和n
    # 我们需要将其转换为实际的换行符
    actual_sql = user_sql.replace('\\n', '\n')
    print(f"实际换行符的SQL: {repr(actual_sql)}")
    print(f"显示SQL:")
    print(actual_sql)
    
    # 分析SQL结构
    print(f"\nSQL分析:")
    print(f"长度: {len(actual_sql)}")
    print(f"行数: {actual_sql.count(chr(10)) + 1}")
    print(f"包含参数占位符: #{'status' in actual_sql}和#{'traceNo' in actual_sql}")
    
    # 测试预处理
    preprocessor = SQLPreprocessor()
    processed_sql, info = preprocessor.preprocess_sql(actual_sql, mode="normalize")
    print(f"\n预处理结果:")
    print(f"处理后SQL: {repr(processed_sql)}")
    print(f"预处理信息: {info}")
    
    # 检查是否有问题
    if processed_sql != actual_sql:
        print(f"注意：SQL被修改了！")
        print(f"原始: {repr(actual_sql)}")
        print(f"处理: {repr(processed_sql)}")
        
        # 检查修改了什么
        if processed_sql.strip() == actual_sql.strip():
            print(f"差异只是空白字符")
        else:
            print(f"有实际内容差异")

if __name__ == "__main__":
    print("测试用户报告的UPDATE SQL解析问题")
    print("问题描述: 去除SQL标签解析大模型返回还有问题")
    print("=" * 80)
    
    test_sql_preprocessor()
    test_xml_tag_remover()
    test_regex_patterns()
    test_issue_specific()
    
    print("\n" + "=" * 80)
    print("测试完成")
    print("=" * 80)
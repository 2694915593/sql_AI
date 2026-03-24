#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试用户提供的SQL解析问题
用户报告：大模型返回的SQL解析有问题
SQL: UPDATE ES_ACCOUNT_API\\nSET EAA_STATUS = #{status},\\n    EAA_UTIENT_TIMESTAMP\\nWHERE EAA_TRACE_NO = #{traceNo}
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

print("测试用户报告的SQL解析问题")
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
    
    # 用户提供的SQL（注意：用户消息中是\\n，在Python字符串中是\n）
    user_sql = "UPDATE ES_ACCOUNT_API\nSET EAA_STATUS = #{status},\n    EAA_UTIENT_TIMESTAMP\nWHERE EAA_TRACE_NO = #{traceNo}"
    
    print(f"用户原始SQL: {repr(user_sql)}")
    print(f"显示SQL: {user_sql}")
    
    # 测试SQL类型检测
    print("\n1. 测试SQL类型检测:")
    sql_type = collector.detect_sql_type(user_sql)
    print(f"   SQL类型: {sql_type}")
    
    # 测试预处理方法
    print("\n2. 测试SQL预处理:")
    processed_sql = collector._preprocess_sql_for_type_detection(user_sql)
    print(f"   预处理后SQL: {repr(processed_sql)}")
    print(f"   显示预处理后SQL: {processed_sql}")
    
    # 测试带XML标签的情况
    print("\n3. 测试带XML标签的情况:")
    xml_sql = f"<update>{user_sql}</update>"
    print(f"   带XML标签SQL: {repr(xml_sql)}")
    print(f"   显示带XML标签SQL: {xml_sql}")
    
    xml_sql_type = collector.detect_sql_type(xml_sql)
    print(f"   带XML标签的SQL类型: {xml_sql_type}")
    
    xml_processed_sql = collector._preprocess_sql_for_type_detection(xml_sql)
    print(f"   带XML标签预处理后SQL: {repr(xml_processed_sql)}")
    print(f"   显示带XML标签预处理后SQL: {xml_processed_sql}")
    
    # 测试各种XML标签
    print("\n4. 测试各种XML标签变体:")
    test_cases = [
        (f"<update>{user_sql}</update>", "带update标签"),
        (f"<sql>{user_sql}</sql>", "带sql标签"),
        (f"<query>{user_sql}</query>", "带query标签"),
        (f"<statement>{user_sql}</statement>", "带statement标签"),
        (f"<query><update>{user_sql}</update></query>", "嵌套标签"),
    ]
    
    for sql, description in test_cases:
        sql_type = collector.detect_sql_type(sql)
        processed_sql = collector._preprocess_sql_for_type_detection(sql)
        print(f"   {description:30} -> 类型: {sql_type:8}, 预处理后长度: {len(processed_sql)}")
        # 检查预处理是否移除了XML标签
        if '<' in processed_sql and '>' in processed_sql:
            print(f"     警告：预处理后仍然包含XML标签: {processed_sql[:50]}...")
    
    # 测试_normalize_sql_for_explain方法
    print("\n5. 测试_normalize_sql_for_explain方法:")
    normalized_sql = collector._normalize_sql_for_explain(user_sql)
    print(f"   标准化后SQL: {repr(normalized_sql)}")
    print(f"   显示标准化后SQL: {normalized_sql}")
    
    # 测试带XML标签的标准化
    xml_normalized = collector._normalize_sql_for_explain(f"<update>{user_sql}</update>")
    print(f"   带XML标签标准化后SQL: {repr(xml_normalized)}")
    print(f"   显示带XML标签标准化后SQL: {xml_normalized}")
    
    print("\n6. 测试_is_explain_supported_sql方法:")
    is_supported = collector._is_explain_supported_sql(user_sql)
    print(f"   用户SQL是否支持EXPLAIN: {is_supported}")
    
    is_supported_xml = collector._is_explain_supported_sql(f"<update>{user_sql}</update>")
    print(f"   带XML标签SQL是否支持EXPLAIN: {is_supported_xml}")
    
    print("\n" + "=" * 80)
    print("测试完成")
    
    # 总结
    print("\n总结:")
    print(f"1. 用户SQL类型检测: {collector.detect_sql_type(user_sql)} (期望: DML)")
    print(f"2. 带<update>标签SQL类型检测: {collector.detect_sql_type(f'<update>{user_sql}</update>')} (期望: DML)")
    print(f"3. 预处理功能是否移除XML标签: {'是' if '<' not in collector._preprocess_sql_for_type_detection(f'<update>{user_sql}</update>') else '否'}")
    print(f"4. SQL是否支持EXPLAIN: {collector._is_explain_supported_sql(user_sql)} (期望: True)")
    
except Exception as e:
    print(f"测试失败: {e}")
    import traceback
    traceback.print_exc()
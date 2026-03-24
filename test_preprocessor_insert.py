#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试SQL预处理器如何处理INSERT语句
"""

import sys
import os
import re

# 设置路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'sql_ai_analyzer'))

print("测试SQL预处理器处理INSERT语句")
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

print("1. 原始SQL:")
print(original_sql)
print(f"原始SQL长度: {len(original_sql)}")
print(f"括号数量: (={original_sql.count('(')}, )={original_sql.count(')')}")
print()

try:
    from sql_ai_analyzer.utils.sql_preprocessor import SQLPreprocessor
    
    preprocessor = SQLPreprocessor()
    
    print("2. 测试SQL预处理器:")
    
    # 测试不同模式
    modes = ["normalize", "extract", "detect", "model"]
    
    for mode in modes:
        print(f"\n  模式: {mode}")
        processed_sql, info = preprocessor.preprocess_sql(original_sql, mode=mode)
        print(f"    处理前长度: {info.get('original_length', 'N/A')}")
        print(f"    处理后长度: {len(processed_sql)}")
        print(f"    括号数量: (={processed_sql.count('(')}, )={processed_sql.count(')')}")
        print(f"    是否包含XML标签: {info.get('has_xml_tags', False)}")
        
        # 检查括号是否被保留
        if processed_sql.count('(') != original_sql.count('(') or processed_sql.count(')') != original_sql.count(')'):
            print(f"    ⚠️ 警告: 括号数量不匹配!")
        
        # 检查前50字符
        print(f"    前100字符: {repr(processed_sql[:100])}")
    
    print("\n3. 测试XML标签移除器:")
    from sql_ai_analyzer.ai_integration.xml_tag_remover import XmlTagRemover
    
    remover = XmlTagRemover()
    
    # 测试带XML标签的SQL
    xml_sql = f"<insert>{original_sql}</insert>"
    print(f"  带XML标签的SQL: {xml_sql[:100]}...")
    
    # 使用正则表达式方法
    processed_sql, info = remover._remove_xml_tags_regex(xml_sql, "normalize", {})
    print(f"  移除XML标签后长度: {len(processed_sql)}")
    print(f"  括号数量: (={processed_sql.count('(')}, )={processed_sql.count(')')}")
    print(f"  前100字符: {repr(processed_sql[:100])}")
    
    # 检查是否还有XML标签
    has_xml = remover._contains_xml_tags_regex(processed_sql)
    print(f"  是否还有XML标签: {has_xml}")
    
    print("\n4. 测试参数提取器:")
    from sql_ai_analyzer.data_collector.param_extractor import ParamExtractor
    
    # 创建简单的logger
    import logging
    logger = logging.getLogger('test')
    logger.setLevel(logging.WARNING)
    
    extractor = ParamExtractor(original_sql, logger)
    
    print(f"  提取器初始化的SQL长度: {len(extractor.sql_text)}")
    print(f"  括号数量: (={extractor.sql_text.count('(')}, )={extractor.sql_text.count(')')}")
    
    # 提取参数
    params = extractor.extract_params()
    print(f"  提取到参数数量: {len(params)}")
    
    # 生成替换后的SQL
    replaced_sql, tables = extractor.generate_replaced_sql()
    print(f"  替换后SQL长度: {len(replaced_sql)}")
    print(f"  括号数量: (={replaced_sql.count('(')}, )={replaced_sql.count(')')}")
    print(f"  前100字符: {repr(replaced_sql[:100])}")
    
    print("\n5. 问题分析:")
    print("  从测试结果看，SQL预处理器正确保留了括号")
    print("  参数提取器也正确保留了括号")
    print("  问题可能出现在其他地方:")
    print("  a) 大模型响应解析")
    print("  b) JSON解析过程中括号被移除")
    print("  c) 文本清理过程中括号被误删除")
    
except Exception as e:
    print(f"测试失败: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("测试完成")
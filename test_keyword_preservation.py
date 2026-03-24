#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试SQL关键字保留问题
主要检查UPDATE语句中SET关键字是否被保留
"""

import re
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sql_ai_analyzer.ai_integration.model_client_fixed import ModelClient

def test_clean_extracted_sql():
    """测试_clean_extracted_sql方法是否能保留SQL关键字"""
    
    # 模拟ModelClient对象（由于依赖config_manager，我们需要创建一个简单的mock）
    class MockConfigManager:
        def get_ai_model_config(self):
            return {}
    
    # 创建ModelClient实例
    config_manager = MockConfigManager()
    client = ModelClient(config_manager)
    
    # 测试用例1：正常的UPDATE语句
    test_sql_1 = """UPDATE MONTHLY_TRAN_MSG
SET
    MTM_SEND = #{send,jdbcType=VARCHAR},
    MTM_PARTY_NAME = #{partyName,jdbcType=VARCHAR},
    MTM_CREATE_TIME = #{createTime,jdbcType=TIMESTAMP},
    MTM_UPDATE_TIME = #{updateTime,jdbcType=TIMESTAMP},
    MTM_REMARK1 = #{remark1,jdbcType=VARCHAR},
    MTM_REMARK2 = #{remark2,jdbcType=VARCHAR}
WHERE
    MTM_PARTY_NO = #{partyNo,jdbcType=VARCHAR}
    AND MTM_PRODUCT_TYPE = #{productType,jdbcType=VARCHAR}"""
    
    print("测试用例1：正常的UPDATE语句")
    print("原始SQL:")
    print(test_sql_1[:200] + "..." if len(test_sql_1) > 200 else test_sql_1)
    print()
    
    # 调用_clean_extracted_sql方法
    cleaned_sql = client._clean_extracted_sql(test_sql_1)
    
    print("清理后的SQL:")
    print(cleaned_sql[:200] + "..." if len(cleaned_sql) > 200 else cleaned_sql)
    print()
    
    # 检查是否保留了SET关键字
    if "SET" in cleaned_sql.upper():
        print("✅ 测试通过：SET关键字被保留")
    else:
        print("❌ 测试失败：SET关键字丢失")
        print("清理后的SQL中缺少SET关键字")
    
    print("-" * 80)
    
    # 测试用例2：带XML标签的SQL（模拟大模型返回）
    test_sql_2 = """sql\\nUPDATE MONTHLY_TRAN_MSG\\nSET\\n    MTM_SEND = #{send,jdbcType=VA
RCHAR},\\n    MTM_PARTY_NAME = #{partyName,jdbcType=VARCHAR},\\n    MTM_CREATE_TIME = #{createTime,jdbcType=TIMESTAMP},\\n    MTM_UPDATE_TIME = #{updateTime,jdbcType=TIMESTAMP},\\n    MTM_REMARK1 = #{remark1,jdbcType=VARCHAR},\\
n    MTM_REMARK2 = #{remark2,jdbcType=VARCHAR}\\nWHERE\\n    MTM_PARTY_NO = #{partyNo,jdbcType=VARCHAR}\\n    AND MTM_PRODUCT_TYPE = #{productType,jdbcType=VARCHAR}"""
    
    print("测试用例2：带转义字符的SQL（模拟大模型返回格式）")
    print("原始SQL（简化显示）:")
    print(test_sql_2.replace('\\n', '\n')[:200] + "..." if len(test_sql_2) > 200 else test_sql_2.replace('\\n', '\n'))
    print()
    
    # 调用_clean_extracted_sql方法
    cleaned_sql_2 = client._clean_extracted_sql(test_sql_2)
    
    print("清理后的SQL:")
    print(cleaned_sql_2[:200] + "..." if len(cleaned_sql_2) > 200 else cleaned_sql_2)
    print()
    
    # 检查是否保留了SET关键字
    if "SET" in cleaned_sql_2.upper():
        print("✅ 测试通过：SET关键字被保留")
    else:
        print("❌ 测试失败：SET关键字丢失")
        print("清理后的SQL中缺少SET关键字")
        print("问题可能出现在清理过程中")
    
    print("-" * 80)
    
    # 测试用例3：各种SQL语句的关键字保留
    test_cases = [
        ("UPDATE table SET col1 = 'value' WHERE id = 1", ["UPDATE", "SET", "WHERE"]),
        ("SELECT * FROM table WHERE condition = 'test'", ["SELECT", "FROM", "WHERE"]),
        ("INSERT INTO table (col1, col2) VALUES ('val1', 'val2')", ["INSERT", "INTO", "VALUES"]),
        ("DELETE FROM table WHERE id = 1", ["DELETE", "FROM", "WHERE"]),
        ("CREATE TABLE table_name (id INT, name VARCHAR(50))", ["CREATE", "TABLE"]),
        ("ALTER TABLE table_name ADD COLUMN new_col VARCHAR(50)", ["ALTER", "TABLE", "ADD", "COLUMN"]),
    ]
    
    print("测试用例3：各种SQL语句的关键字保留")
    for sql, expected_keywords in test_cases:
        cleaned = client._clean_extracted_sql(sql)
        missing_keywords = [kw for kw in expected_keywords if kw not in cleaned.upper()]
        
        if missing_keywords:
            print(f"❌ '{sql[:30]}...' - 缺少关键字: {missing_keywords}")
        else:
            print(f"✅ '{sql[:30]}...' - 所有关键字都被保留")
    
    print("-" * 80)
    
    # 测试用例4：检查清理过程中可能的问题
    print("测试用例4：检查清理过程中可能的问题")
    
    # 测试XML标签移除是否影响关键字
    xml_sql = "<update>UPDATE table SET value = 1 WHERE id = 1</update>"
    cleaned_xml = client._clean_extracted_sql(xml_sql)
    
    if "SET" in cleaned_xml.upper() and "WHERE" in cleaned_xml.upper():
        print(f"✅ XML标签移除测试通过，关键字保留完整")
    else:
        print(f"❌ XML标签移除测试失败")
        print(f"原始: {xml_sql}")
        print(f"清理后: {cleaned_xml}")
    
    # 测试代码块标记移除是否影响关键字
    codeblock_sql = "```sql\nUPDATE table SET value = 1 WHERE id = 1\n```"
    cleaned_codeblock = client._clean_extracted_sql(codeblock_sql)
    
    if "SET" in cleaned_codeblock.upper() and "WHERE" in cleaned_codeblock.upper():
        print(f"✅ 代码块标记移除测试通过，关键字保留完整")
    else:
        print(f"❌ 代码块标记移除测试失败")
        print(f"原始: {codeblock_sql}")
        print(f"清理后: {cleaned_codeblock}")

def analyze_issue():
    """分析问题根源"""
    print("=" * 80)
    print("问题分析")
    print("=" * 80)
    
    # 用户提供的示例
    original_sql = """sql\\nUPDATE MONTHLY_TRAN_MSG\\nSET\\n    MTM_SEND = #{send,jdbcType=VA
RCHAR},\\n    MTM_PARTY_NAME = #{partyName,jdbcType=VARCHAR},\\n    MTM_CREATE_TIME = #{createTime,jdbcType=TIMESTAMP},\\n    MTM_UPDATE_TIME = #{updateTime,jdbcType=TIMESTAMP},\\n    MTM_REMARK1 = #{remark1,jdbcType=VARCHAR},\\
n    MTM_REMARK2 = #{remark2,jdbcType=VARCHAR}\\nWHERE\\n    MTM_PARTY_NO = #{partyNo,jdbcType=VARCHAR}\\n    AND MTM_PRODUCT_TYPE = #{productType,jdbcType=VARCHAR}"""
    
    processed_sql = """update MONTHLY_TRAN_MSG
MTM_SEND =#{send,jdbcType=VARCHAR}, MTM_PARTY_NAME =#{partyName,jdbcType=VARCHAR},
MTM_CREATE_TIME =#{createTime,jdbcType=TIMESTAMP},
MTM_UPDATE_TIME =#{updateTime,jdbcType=TIMESTAMP},
MTM_REMARK1 = #{remark1,jdbcType=VARCHAR},
MTM_REMARK2 = #{remark2,jdbcType=VARCHAR},
WHERE MTM_PARTY_NO =#{partyNo,jdbcType=VARCHAR} AND MTM_PRODUCT_TYPE =#{productType,jdbcType=VARCHAR}"""
    
    print("用户提供的原始SQL（简化）:")
    print(original_sql.replace('\\n', '\n')[:300] + "..." if len(original_sql) > 300 else original_sql.replace('\\n', '\n'))
    print()
    
    print("用户提供的处理后SQL:")
    print(processed_sql)
    print()
    
    # 分析问题
    print("问题分析:")
    print("1. 原始SQL包含 'UPDATE MONTHLY_TRAN_MSG\\nSET\\n'")
    print("2. 处理后SQL变为 'update MONTHLY_TRAN_MSG\\nMTM_SEND =...'")
    print("3. 'SET'关键字丢失了")
    print()
    
    print("可能的原因:")
    print("1. 清理过程中误将'SET'识别为XML标签或标记")
    print("2. 正则表达式匹配时过度清理")
    print("3. 文本处理时意外删除了关键字")
    print()
    
    # 检查当前_clean_extracted_sql的实现
    print("当前_clean_extracted_sql方法的主要清理步骤:")
    print("1. 移除代码块标记 (```sql 和 ```)")
    print("2. 移除XML标签 (<[^>]+>)")
    print("3. 移除CDATA标记 (<!\[CDATA\[ 和 \]\]>)")
    print("4. 压缩多余空格但保留换行符")
    print("5. 修复INSERT语句结构（如果缺少括号）")
    print("6. 移除首尾空白")
    print()
    
    # 测试原始正则表达式
    print("测试XML标签移除正则表达式:")
    test_text = "UPDATE table SET value = 1 WHERE id = 1"
    xml_pattern = r'<[^>]+>'
    result = re.sub(xml_pattern, ' ', test_text)
    print(f"输入: {test_text}")
    print(f"XML标签移除后: {result}")
    print(f"是否影响'SET'关键字: {'是' if 'SET' not in result else '否'}")
    print()
    
    # 测试代码块标记移除
    print("测试代码块标记移除:")
    codeblock_pattern = r'```[\w]*\s*'
    test_with_codeblock = "```sql\nUPDATE table SET value = 1 WHERE id = 1\n```"
    result = re.sub(codeblock_pattern, '', test_with_codeblock)
    result = re.sub(r'```', '', result)
    print(f"输入: {test_with_codeblock}")
    print(f"代码块移除后: {result}")
    print(f"是否影响'SET'关键字: {'是' if 'SET' not in result else '否'}")

if __name__ == "__main__":
    print("开始测试SQL关键字保留问题")
    print("=" * 80)
    
    try:
        test_clean_extracted_sql()
        print()
        analyze_issue()
    except Exception as e:
        print(f"测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
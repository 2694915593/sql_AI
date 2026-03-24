#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试SET关键字丢失问题的根本原因
"""

import re
import json

def analyze_set_keyword_issue():
    print("分析SET关键字丢失问题")
    print("=" * 80)
    
    # 用户提供的原始SQL格式
    original_with_prefix = '''sql\\nUPDATE MONTHLY_TRAN_MSG\\nSET\\n    MTM_SEND = #{send,jdbcType=VA
RCHAR},\\n    MTM_PARTY_NAME = #{partyName,jdbcType=VARCHAR},\\n    MTM_CREATE_TIME = #{createTime,jdbcType=TIMESTAMP},\\n    MTM_UPDATE_TIME = #{updateTime,jdbcType=TIMESTAMP},\\n    MTM_REMARK1 = #{remark1,jdbcType=VARCHAR},\\
n    MTM_REMARK2 = #{remark2,jdbcType=VARCHAR}\\nWHERE\\n    MTM_PARTY_NO = #{partyNo,jdbcType=VARCHAR}\\n    AND MTM_PRODUCT_TYPE = #{productType,jdbcType=VARCHAR}'''
    
    print("1. 分析原始SQL格式")
    print(f"原始字符串: {repr(original_with_prefix[:200])}...")
    
    # 反转义处理
    unescaped = original_with_prefix.replace('\\n', '\n')
    print(f"\n反转义后: {repr(unescaped[:200])}...")
    
    # 检查是否以"sql"开头
    if unescaped.lower().startswith('sql'):
        print("⚠️ SQL以'sql'开头")
        
        # 查看"sql"后面的内容
        lines = unescaped.split('\n')
        print(f"\n按行分析:")
        for i, line in enumerate(lines):
            print(f"  行{i}: '{line}'")
            
            # 如果是第0行，检查是否是"sql"
            if i == 0 and line.lower() == 'sql':
                print(f"    第0行是'sql'，可能被误处理")
                
        # 检查是否有SET行
        set_found = False
        for i, line in enumerate(lines):
            if 'SET' in line.upper():
                set_found = True
                print(f"\n✅ 在第{i}行找到SET: '{line}'")
                break
        
        if not set_found:
            print(f"\n❌ 在所有行中都没有找到SET关键字")
            
            # 检查是否SET在"sql"后面但在同一行？
            # 如果是"sqlUPDATE ... SET..."这样的格式
            if 'SET' in unescaped.upper():
                set_index = unescaped.upper().find('SET')
                print(f"但在字符串位置{set_index}找到了SET")
                context = unescaped[max(0, set_index-20):min(len(unescaped), set_index+30)]
                print(f"上下文: ...{context}...")
    
    print("\n" + "=" * 80)
    print("2. 模拟可能的错误处理场景")
    
    # 场景1: 如果"sql"被误认为是XML标签的一部分
    test_case_1 = "sql\nUPDATE table SET col = 1 WHERE id = 1"
    print(f"\n场景1 - 简单测试: '{test_case_1}'")
    
    # 检查是否有XML标签移除逻辑会误删SET
    xml_pattern = r'<[^>]+>'
    result1 = re.sub(xml_pattern, ' ', test_case_1)
    print(f"  XML标签移除后: '{result1}'")
    print(f"  SET是否保留: {'SET' in result1.upper()}")
    
    # 场景2: 如果"sql"前缀被错误地移除
    # 查看_clean_extracted_sql方法中的代码块标记移除逻辑
    print(f"\n场景2 - 代码块标记移除:")
    codeblock_pattern = r'```[\w]*\s*'
    test_case_2 = "```sql\nUPDATE table SET col = 1 WHERE id = 1\n```"
    result2 = re.sub(codeblock_pattern, '', test_case_2)
    result2 = re.sub(r'```', '', result2)
    print(f"  输入: '{test_case_2}'")
    print(f"  输出: '{result2}'")
    print(f"  SET是否保留: {'SET' in result2.upper()}")
    
    # 场景3: 如果"sql"本身被误移除
    print(f"\n场景3 - 'sql'前缀可能被误处理:")
    
    # 模拟可能的问题：如果代码错误地将"sql"当作标记移除
    def problematic_clean(sql_text):
        """模拟可能有问题的清理逻辑"""
        cleaned = sql_text
        
        # 错误逻辑：移除以"sql"开头的行
        lines = cleaned.split('\n')
        cleaned_lines = []
        for line in lines:
            if line.strip().lower() == 'sql':
                # 错误地跳过这一行
                continue
            cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    test_case_3 = "sql\nUPDATE table SET col = 1 WHERE id = 1"
    result3 = problematic_clean(test_case_3)
    print(f"  输入: '{test_case_3}'")
    print(f"  输出: '{result3}'")
    print(f"  问题: 'sql'行被移除，但SET在下一行，应该没问题")
    print(f"  SET是否保留: {'SET' in result3.upper()}")
    
    # 场景4: 如果SET在"sql"后面的同一行
    test_case_4 = "sqlUPDATE table SET col = 1 WHERE id = 1"
    print(f"\n场景4 - 'sql'和SQL在同一行: '{test_case_4}'")
    
    # 如果错误地移除"sql"前缀
    if test_case_4.lower().startswith('sql'):
        result4 = test_case_4[3:]  # 移除"sql"
        print(f"  移除'sql'后: '{result4}'")
        print(f"  SET是否保留: {'SET' in result4.upper()}")
    
    print("\n" + "=" * 80)
    print("3. 分析实际代码中的问题")
    
    # 查看_clean_extracted_sql方法
    print("\n_clean_extracted_sql方法分析:")
    print("该方法主要步骤:")
    print("1. 移除代码块标记 (```sql 和 ```)")
    print("2. 移除XML标签 (<[^>]+>)")
    print("3. 移除CDATA标记")
    print("4. 压缩空格，保留换行符")
    print("5. 修复INSERT语句结构（如果缺少括号）")
    print("6. 移除首尾空白")
    
    print("\n这些步骤不应该删除SET关键字，除非:")
    print("1. SET被错误地识别为XML标签")
    print("2. 有其他处理步骤在调用_clean_extracted_sql之前就修改了SQL")
    
    print("\n" + "=" * 80)
    print("4. 验证假设：问题可能在解析过程中")
    
    # 模拟大模型响应解析
    print("\n模拟大模型响应解析过程:")
    
    # 假设大模型返回这样的响应
    mock_response = {
        "raw_response": {
            "RSP_BODY": {
                "answer": original_with_prefix  # 包含"sql\\n"前缀的SQL
            }
        }
    }
    
    print(f"模拟响应中的answer字段: {repr(mock_response['raw_response']['RSP_BODY']['answer'][:100])}...")
    
    # 在解析过程中，这个answer字段可能会被多次处理
    # 问题可能出现在JSON解析或字符串处理过程中
    
    print("\n" + "=" * 80)
    print("5. 建议的修复方案")
    
    print("\n可能的修复方案:")
    print("1. 在_clean_extracted_sql方法中添加保护逻辑，确保SQL关键字不被移除")
    print("2. 在解析answer字段时，检查并修复可能被损坏的SQL结构")
    print("3. 特别处理'sql'前缀问题")
    print("4. 添加SQL语法验证，确保关键部分（如UPDATE语句的SET）存在")

def test_fix_proposal():
    print("\n" + "=" * 80)
    print("测试修复方案")
    print("=" * 80)
    
    def enhanced_clean_extracted_sql(sql_text: str) -> str:
        """
        增强的SQL清理方法，保护SQL关键字
        """
        if not sql_text:
            return ""
        
        cleaned = sql_text
        
        # 1. 移除代码块标记
        cleaned = re.sub(r'```[\w]*\s*', '', cleaned)
        cleaned = re.sub(r'```', '', cleaned)
        
        # 2. 移除XML标签
        cleaned = re.sub(r'<[^>]+>', ' ', cleaned)
        
        # 3. 移除CDATA标记
        cleaned = re.sub(r'<!\[CDATA\[', '', cleaned)
        cleaned = re.sub(r'\]\]>', '', cleaned)
        
        # 4. 压缩多余空格，但保留换行符
        lines = cleaned.split('\n')
        cleaned_lines = []
        for line in lines:
            line = re.sub(r'\s+', ' ', line.strip())
            if line:
                cleaned_lines.append(line)
        
        cleaned = '\n'.join(cleaned_lines)
        
        # 5. 新增：修复UPDATE语句缺少SET关键字的问题
        cleaned = fix_update_statement_if_needed(cleaned)
        
        # 6. 移除首尾空白
        cleaned = cleaned.strip()
        
        return cleaned
    
    def fix_update_statement_if_needed(sql_text: str) -> str:
        """
        修复UPDATE语句缺少SET关键字的问题
        """
        if not sql_text:
            return sql_text
        
        sql_upper = sql_text.upper()
        
        # 检查是否是UPDATE语句
        if sql_upper.startswith('UPDATE'):
            # 检查是否有SET关键字
            if 'SET' not in sql_upper:
                print(f"⚠️ 检测到UPDATE语句缺少SET关键字")
                
                # 尝试在UPDATE后添加SET
                # 找到UPDATE后面的第一个单词（表名）
                words = sql_text.split()
                if len(words) >= 2:
                    # UPDATE table_name ... 
                    # 在表名后插入SET
                    result_parts = []
                    result_parts.append(words[0])  # UPDATE
                    result_parts.append(words[1])  # table_name
                    result_parts.append('SET')
                    
                    # 添加剩余部分
                    if len(words) > 2:
                        result_parts.extend(words[2:])
                    
                    fixed_sql = ' '.join(result_parts)
                    print(f"  修复后: {fixed_sql[:100]}...")
                    return fixed_sql
        
        return sql_text
    
    # 测试用例
    test_cases = [
        ("update MONTHLY_TRAN_MSG\nMTM_SEND =#{send}", "缺少SET的UPDATE"),
        ("UPDATE table SET col = 1 WHERE id = 1", "正常的UPDATE"),
        ("sql\nUPDATE table SET col = 1 WHERE id = 1", "带'sql'前缀的UPDATE"),
    ]
    
    for sql, description in test_cases:
        print(f"\n测试: {description}")
        print(f"  输入: {sql[:80]}...")
        result = enhanced_clean_extracted_sql(sql)
        print(f"  输出: {result[:80]}...")
        print(f"  是否有SET: {'SET' in result.upper()}")

if __name__ == "__main__":
    analyze_set_keyword_issue()
    test_fix_proposal()
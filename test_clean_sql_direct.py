#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直接测试SQL清理逻辑，不依赖导入
"""

import re

def clean_extracted_sql(sql_text: str) -> str:
    """
    清理提取的SQL文本，特别保护INSERT语句的括号结构
    
    Args:
        sql_text: 提取的SQL文本
        
    Returns:
        清理后的SQL文本
    """
    if not sql_text:
        return ""
    
    cleaned = sql_text
    
    # 1. 移除代码块标记（但要小心不要移除括号）
    cleaned = re.sub(r'```[\w]*\s*', '', cleaned)
    cleaned = re.sub(r'```', '', cleaned)
    
    # 2. 移除XML标签（但要小心不要移除括号）
    # 使用更保守的方法，只移除真正的XML标签
    cleaned = re.sub(r'<[^>]+>', ' ', cleaned)
    
    # 3. 移除CDATA标记
    cleaned = re.sub(r'<!\[CDATA\[', '', cleaned)
    cleaned = re.sub(r'\]\]>', '', cleaned)
    
    # 4. 压缩多余空格，但保留换行符（对多行SQL很重要）
    # 先分割为行，单独处理每行
    lines = cleaned.split('\n')
    cleaned_lines = []
    for line in lines:
        line = re.sub(r'\s+', ' ', line.strip())
        if line:
            cleaned_lines.append(line)
    
    # 重新组合，保留换行符（对多行SQL很重要）
    cleaned = '\n'.join(cleaned_lines)
    
    # 5. 修复INSERT语句结构（如果缺少括号）
    # 这里省略_fix_insert_structure_if_needed方法，因为它与SET关键字无关
    
    # 6. 移除首尾空白
    cleaned = cleaned.strip()
    
    return cleaned

def test_case_1():
    """测试用户提供的案例"""
    print("测试用例1：用户提供的原始SQL")
    
    # 用户提供的原始SQL（简化版）
    original_sql = """sql\nUPDATE MONTHLY_TRAN_MSG\nSET\n    MTM_SEND = #{send,jdbcType=VA
RCHAR},\n    MTM_PARTY_NAME = #{partyName,jdbcType=VARCHAR},\n    MTM_CREATE_TIME = #{createTime,jdbcType=TIMESTAMP},\n    MTM_UPDATE_TIME = #{updateTime,jdbcType=TIMESTAMP},\n    MTM_REMARK1 = #{remark1,jdbcType=VARCHAR},\
n    MTM_REMARK2 = #{remark2,jdbcType=VARCHAR}\nWHERE\n    MTM_PARTY_NO = #{partyNo,jdbcType=VARCHAR}\n    AND MTM_PRODUCT_TYPE = #{productType,jdbcType=VARCHAR}"""
    
    print("原始SQL:")
    print(repr(original_sql))
    print("\n清理过程跟踪:")
    
    # 逐步跟踪清理过程
    cleaned = original_sql
    
    # 步骤1: 移除代码块标记
    before_step1 = cleaned
    cleaned = re.sub(r'```[\w]*\s*', '', cleaned)
    cleaned = re.sub(r'```', '', cleaned)
    if before_step1 != cleaned:
        print(f"步骤1后: {repr(cleaned[:100])}...")
    
    # 步骤2: 移除XML标签
    before_step2 = cleaned
    cleaned = re.sub(r'<[^>]+>', ' ', cleaned)
    if before_step2 != cleaned:
        print(f"步骤2后: {repr(cleaned[:100])}...")
    
    # 步骤3: 移除CDATA标记
    before_step3 = cleaned
    cleaned = re.sub(r'<!\[CDATA\[', '', cleaned)
    cleaned = re.sub(r'\]\]>', '', cleaned)
    if before_step3 != cleaned:
        print(f"步骤3后: {repr(cleaned[:100])}...")
    
    # 步骤4: 压缩多余空格
    before_step4 = cleaned
    lines = cleaned.split('\n')
    cleaned_lines = []
    for i, line in enumerate(lines):
        original_line = line
        line = re.sub(r'\s+', ' ', line.strip())
        if line:
            cleaned_lines.append(line)
        if original_line != line:
            print(f"  行{i}: '{original_line}' -> '{line}'")
    
    cleaned = '\n'.join(cleaned_lines)
    if before_step4 != cleaned:
        print(f"步骤4后: {repr(cleaned[:100])}...")
    
    # 步骤6: 移除首尾空白
    before_step6 = cleaned
    cleaned = cleaned.strip()
    if before_step6 != cleaned:
        print(f"步骤6后: {repr(cleaned[:100])}...")
    
    print(f"\n最终清理结果:")
    print(cleaned)
    
    # 检查SET关键字
    if "SET" in cleaned.upper():
        print("\n✅ SET关键字被保留")
    else:
        print("\n❌ SET关键字丢失!")
        
        # 进一步分析为什么丢失
        print("\n分析原因:")
        lines = original_sql.split('\n')
        for i, line in enumerate(lines):
            if 'SET' in line.upper():
                print(f"  原始行{i}: '{line}'")
                # 检查清理后的行
                cleaned_line = re.sub(r'\s+', ' ', line.strip())
                print(f"  清理后行{i}: '{cleaned_line}'")
    
    return cleaned

def test_case_2():
    """测试简化案例"""
    print("\n\n测试用例2：简化UPDATE语句")
    
    test_sql = "UPDATE table SET col = 'value' WHERE id = 1"
    cleaned = clean_extracted_sql(test_sql)
    
    print(f"原始: {test_sql}")
    print(f"清理后: {cleaned}")
    
    if "SET" in cleaned.upper():
        print("✅ SET关键字被保留")
    else:
        print("❌ SET关键字丢失!")

def test_case_3():
    """测试带换行符的SQL"""
    print("\n\n测试用例3：带换行符的UPDATE语句")
    
    test_sql = """UPDATE table
SET
    col1 = 'value1',
    col2 = 'value2'
WHERE
    id = 1"""
    
    cleaned = clean_extracted_sql(test_sql)
    
    print(f"原始:")
    print(test_sql)
    print(f"\n清理后:")
    print(cleaned)
    
    if "SET" in cleaned.upper():
        print("\n✅ SET关键字被保留")
    else:
        print("\n❌ SET关键字丢失!")

def test_case_4():
    """测试带'sql\\n'前缀的SQL"""
    print("\n\n测试用例4：带'sql\\n'前缀的SQL")
    
    test_sql = """sql
UPDATE table
SET col = 'value'
WHERE id = 1"""
    
    cleaned = clean_extracted_sql(test_sql)
    
    print(f"原始:")
    print(repr(test_sql))
    print(f"\n清理后:")
    print(repr(cleaned))
    
    if "SET" in cleaned.upper():
        print("\n✅ SET关键字被保留")
    else:
        print("\n❌ SET关键字丢失!")
        
    # 检查'sql'前缀是否被移除
    if cleaned.lower().startswith('sql'):
        print("⚠️ 'sql'前缀仍然存在")

if __name__ == "__main__":
    print("开始测试SQL清理逻辑")
    print("=" * 80)
    
    test_case_1()
    test_case_2()
    test_case_3()
    test_case_4()
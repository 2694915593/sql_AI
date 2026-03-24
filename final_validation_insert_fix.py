#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最终验证INSERT语句修复功能
"""

import re
import sys
sys.path.insert(0, '.')

# 模拟实际的清理和修复流程
def test_full_clean_and_fix_process():
    """测试完整的清理和修复流程"""
    
    # 用户提供的案例
    # 大模型返回的正确SQL
    original_correct_sql = '''INSERT INTO PB_ACCOUNT
(ID, ORG_CODE, MOBILE, NAME, CERT_TYPE, 
CERT_NO, ACCOUNT_NO, ACCOUNT_TYPE, STATUS, CTIME, MODULE_TYPE, CHANNEL_TYPE, MAIN_TYPE, SCENCE_TYPE, ACCOUNT_JNL, CHECK_ACTIVE_PATH, CHECK_ACTIVE_DOCID, CHECK_ACTIVE_CTIME, CHECK_OCR_DOCID, TRACE_NO)
VALUES
(#{id,jdbcType=BIGINT}, #{orgCode,jdbcType=VARCHAR}, #{mobile,jdbcType=VARCHAR}, #{name,jdbcType=VARCHAR}, #{certType,jdbcType=VARCHAR}, #{certNo,jdbcType=VARCHAR}, #{accountNo,jdbcType=VARCHAR}, #{accountType,jdbcType=VARCHAR}, #{status,jdbcType=VARCHAR}, #{ctime,jdbcType=TIMESTAMP}, #{moduleType,jdbcType=VARCHAR}, #{channelType,jdbcType=VARCHAR}, #{mainType,jdbcType=VARCHAR}, #{scenceType,jdbcType=VARCHAR}, #{accountJnl,jdbcType=VARCHAR}, #{checkActivePath,jdbcType=VARCHAR}, #{checkActiveDocId,jdbcType=VARCHAR}, #{checkActiveCtime,jdbcType=TIMESTAMP}, #{checkOcrDocId,jdbcType=VARCHAR}, #{traceNo,jdbcType=VARCHAR})'''
    
    # 处理后的错误SQL（用户报告的问题）
    problematic_sql = '''insert into PB_ACCOUNT
ID,
ORG_CODE,
MOBILE,
NAME,
CERT_TYPE,
CERT_NO,
ACCOUNT_NO,
ACCOUNT_TYPE,
STATUS,
CTIME,
MODULE_TYPE,
CHANNEL_TYPE,
MAIN_TYPE,
SCENCE_TYPE,
ACCOUNT_JNL,
CHECK_ACTIVE_PATH,
CHECK_ACTIVE_DOCID,
CHECK_ACTIVE_CTIME,
CHECK_OCR_DOCID,
TRACE_NO
#{id,jdbcType=BIGINT},
#{orgCode,jdbcType=VARCHAR},
#{mobile,jdbcType=VARCHAR},
#{name,jdbcType=VARCHAR},
#{certType,jdbcType=VARCHAR},
#{certNo,jdbcType=VARCHAR},
#{accountNo,jdbcType=VARCHAR},
#{accountType,jdbcType=VARCHAR},
#{status,jdbcType=VARCHAR},
#{ctime,jdbcType=TIMESTAMP},
#{moduleType,jdbcType=VARCHAR},
#{channelType,jdbcType=VARCHAR},
#{mainType,jdbcType=VARCHAR},
#{scenceType,jdbcType=VARCHAR},
#{accountJnl,jdbcType=VARCHAR},
#{checkActivePath,jdbcType=VARCHAR},
#{checkActiveDocId,jdbcType=VARCHAR},
#{checkActiveCtime,jdbcType=TIMESTAMP},
#{checkOcrDocId,jdbcType=VARCHAR},
#{traceNo,jdbcType=VARCHAR},'''
    
    print("=" * 80)
    print("最终验证: INSERT语句修复功能")
    print("=" * 80)
    
    print("\n1. 原始正确的SQL（大模型返回）:")
    print("-" * 40)
    print(f"长度: {len(original_correct_sql)} 字符")
    print(f"括号数量: (={original_correct_sql.count('(')}, )={original_correct_sql.count(')')}")
    print(f"包含VALUES: {'VALUES' in original_correct_sql.upper()}")
    print(f"包含#{{: {'#{' in original_correct_sql}")
    print(f"预览前100字符: {original_correct_sql[:100]}...")
    
    print("\n2. 处理后的错误SQL（用户报告的问题）:")
    print("-" * 40)
    print(f"长度: {len(problematic_sql)} 字符")
    print(f"括号数量: (={problematic_sql.count('(')}, )={problematic_sql.count(')')}")
    print(f"包含VALUES: {'VALUES' in problematic_sql.upper()}")
    print(f"包含#{{: {'#{' in problematic_sql}")
    print(f"预览前100字符: {problematic_sql[:100]}...")
    
    print("\n3. 分析问题:")
    print("-" * 40)
    
    # 分析问题SQL的特征
    sql_lower = problematic_sql.lower().strip()
    
    # 检查是否是INSERT语句
    is_insert = sql_lower.startswith('insert')
    print(f"是否是INSERT语句: {is_insert}")
    
    # 检查是否有括号
    has_parens = '(' in problematic_sql and ')' in problematic_sql
    print(f"是否有括号: {has_parens}")
    
    # 检查是否有VALUES关键字
    has_values = 'values' in sql_lower
    print(f"是否有VALUES关键字: {has_values}")
    
    # 检查是否有参数占位符
    has_params = '#{' in problematic_sql
    print(f"是否有参数占位符#{{...}}: {has_params}")
    
    if has_params:
        param_pos = problematic_sql.find('#{')
        print(f"第一个参数位置: {param_pos}")
        before_param = problematic_sql[:param_pos]
        print(f"参数前内容（前50字符）: {before_param[:50]}...")
    
    print("\n4. 修复方案验证:")
    print("-" * 40)
    
    # 模拟修复函数
    def fixed_fix_insert_structure_if_needed(sql_text):
        """增强的修复函数"""
        if not sql_text:
            return sql_text
        
        # 检查是否是INSERT语句
        sql_lower = sql_text.lower().strip()
        if not sql_lower.startswith('insert'):
            return sql_text
        
        # 检查括号数量
        open_paren = sql_text.count('(')
        close_paren = sql_text.count(')')
        
        # 如果括号数量为0，尝试修复
        if open_paren == 0 and close_paren == 0:
            print("  ✅ 检测到INSERT语句缺少括号，将尝试修复")
            
            # 查找表名结束位置
            table_name_end = -1
            # 匹配INSERT INTO table_name
            import re
            insert_match = re.search(r'insert\s+into\s+([^\s(]+)', sql_lower)
            if insert_match:
                table_name = insert_match.group(1)
                table_name_end = sql_lower.find(table_name) + len(table_name)
                
                # 查找VALUES关键字
                values_pos = sql_lower.find('values', table_name_end)
                
                # 如果没有VALUES关键字，尝试推断列名和值的分界
                if values_pos <= 0:
                    print("  ℹ️ 没有VALUES关键字，使用参数#{}作为分界点")
                    
                    # 查找第一个参数（#{）作为列名和值的分界
                    param_start = sql_text.find('#{', table_name_end)
                    if param_start > 0:
                        # 列名部分（表名后到第一个参数前）
                        columns_part = sql_text[table_name_end:param_start].strip()
                        # 值部分（第一个参数后）
                        values_part = sql_text[param_start:].strip()
                        
                        # 清理列名部分
                        columns_clean = re.sub(r'\s+', ' ', columns_part).strip()
                        # 清理值部分
                        values_clean = re.sub(r'\s+', ' ', values_part).strip()
                        
                        # 移除列名部分末尾的逗号
                        if columns_clean.endswith(','):
                            columns_clean = columns_clean[:-1].strip()
                        
                        # 移除值部分末尾的逗号
                        if values_clean.endswith(','):
                            values_clean = values_clean[:-1].strip()
                        
                        # 检查列名部分是否包含多个列名（有逗号分隔）
                        if ',' in columns_clean or re.search(r'[A-Z_]+', columns_clean):
                            # 有多个列名或大写字母，可能是有效的列名列表
                            columns_fixed = f'({columns_clean})'
                        else:
                            # 单个列名或无逗号，也添加括号
                            columns_fixed = f'({columns_clean})'
                        
                        # 值部分添加括号
                        values_fixed = f'({values_clean})'
                        
                        # 重构SQL
                        table_part = sql_text[:table_name_end].strip()
                        fixed_sql = f'{table_part} {columns_fixed} VALUES {values_fixed}'
                        
                        print(f"  ✅ 修复成功: 添加了括号和VALUES关键字")
                        return fixed_sql
                    else:
                        print("  ❌ 未找到参数分界点，无法修复")
                        return sql_text
                
                # 如果有VALUES关键字，使用标准修复逻辑
                if values_pos > 0:
                    print("  ℹ️ 有VALUES关键字，使用标准修复逻辑")
                    # 列名部分（表名后到VALUES前）
                    columns_part = sql_text[table_name_end:values_pos].strip()
                    # 值部分（VALUES后）
                    values_part = sql_text[values_pos + 5:].strip()
                    
                    # 清理列名部分（移除多余空格和换行）
                    columns_clean = re.sub(r'\s+', ' ', columns_part).strip()
                    # 清理值部分
                    values_clean = re.sub(r'\s+', ' ', values_part).strip()
                    
                    # 检查列名部分是否看起来像列名
                    if ',' in columns_clean or any(keyword in columns_clean.lower() for keyword in ['mtm_', 'col', 'field', 'id']):
                        columns_fixed = f'({columns_clean})'
                    else:
                        columns_fixed = f'({columns_clean})'
                    
                    # 检查值部分是否看起来像值
                    if ',' in values_clean or '#{' in values_clean:
                        values_fixed = f'({values_clean})'
                    else:
                        values_fixed = f'({values_clean})'
                    
                    # 重新组合SQL
                    table_part = sql_text[:table_name_end].strip()
                    fixed_sql = f'{table_part} {columns_fixed} VALUES {values_fixed}'
                    
                    print(f"  ✅ 修复成功: 确保了括号结构")
                    return fixed_sql
            
            return sql_text
        
        # 如果只有一对括号，但INSERT语句应该有两对括号
        elif open_paren == 1 and close_paren == 1:
            print("  ℹ️ 检测到INSERT语句只有一对括号，尝试修复")
            
            # 检查括号位置
            first_paren = sql_text.find('(')
            last_paren = sql_text.rfind(')')
            
            # 查找VALUES关键字
            values_pos = sql_lower.find('values')
            
            import re
            if values_pos > 0 and first_paren < values_pos < last_paren:
                # 括号在VALUES之前，这可能是列名括号
                # 需要添加值括号
                
                # 在VALUES后面添加括号
                # 找到VALUES后的内容
                after_values = sql_text[values_pos + 5:].strip()
                
                # 如果VALUES后的内容没有括号，添加
                if not after_values.startswith('('):
                    # 找到值的结束位置
                    end_pos = len(sql_text)
                    for end_char in [',', ';', '\n']:
                        pos = sql_text.find(end_char, values_pos + 5)
                        if pos > 0 and pos < end_pos:
                            end_pos = pos
                    
                    values_content = sql_text[values_pos + 5:end_pos].strip()
                    # 添加括号
                    values_fixed = f'({values_content})'
                    
                    # 重新组合
                    before_values = sql_text[:values_pos + 5].strip()
                    fixed_sql = f'{before_values} {values_fixed}'
                    if end_pos < len(sql_text):
                        fixed_sql += sql_text[end_pos:]
                    
                    print(f"  ✅ 修复成功: 添加了值括号")
                    return fixed_sql
        
        return sql_text
    
    # 测试修复
    print("\n对问题SQL应用修复函数:")
    result = fixed_fix_insert_structure_if_needed(problematic_sql)
    
    print("\n修复结果:")
    print("-" * 40)
    print(f"长度: {len(result)} 字符")
    print(f"括号数量: (={result.count('(')}, )={result.count(')')}")
    print(f"包含VALUES: {'VALUES' in result.upper()}")
    print(f"预览前200字符: {result[:200]}...")
    
    # 验证修复结果
    print("\n5. 修复验证:")
    print("-" * 40)
    
    is_valid = True
    issues = []
    
    if not ('VALUES' in result.upper()):
        is_valid = False
        issues.append("缺少VALUES关键字")
    
    if result.count('(') < 2 or result.count(')') < 2:
        is_valid = False
        issues.append(f"括号数量不足 (={result.count('(')}, )={result.count(')')}")
    
    if not ('#{' in result):
        is_valid = False
        issues.append("丢失了参数占位符")
    
    if is_valid:
        print("✅ 修复成功: INSERT语句结构正确")
        print(f"   - 括号数量: (={result.count('(')}, )={result.count(')')}")
        print(f"   - 包含VALUES: {'VALUES' in result.upper()}")
        print(f"   - 包含参数占位符: {'#{' in result}")
    else:
        print("❌ 修复失败")
        for issue in issues:
            print(f"   - {issue}")
    
    print("\n6. 修复建议:")
    print("-" * 40)
    print("1. 在 model_client.py 的 _fix_insert_structure_if_needed 函数中")
    print("2. 增强对缺少VALUES关键字情况的处理")
    print("3. 使用参数占位符 #{...} 作为列名和值的分界点")
    print("4. 确保保留原始SQL的格式和参数")
    print("5. 添加适当的括号和VALUES关键字")
    
    print("\n7. 具体修改:")
    print("-" * 40)
    print("在 model_client.py 的 _fix_insert_structure_if_needed 函数中:")
    print("添加以下逻辑处理缺少VALUES关键字的情况:")
    print("""
    # 如果没有VALUES关键字，尝试推断列名和值的分界
    if values_pos <= 0:
        # 查找第一个参数（#{）作为列名和值的分界
        param_start = sql_text.find('#{', table_name_end)
        if param_start > 0:
            # 列名部分（表名后到第一个参数前）
            columns_part = sql_text[table_name_end:param_start].strip()
            # 值部分（第一个参数后）
            values_part = sql_text[param_start:].strip()
            
            # 清理和修复...
            # 添加括号和VALUES关键字
            fixed_sql = f'{table_part} ({columns_clean}) VALUES ({values_clean})'
            return fixed_sql
    """)
    
    return result

if __name__ == "__main__":
    test_full_clean_and_fix_process()
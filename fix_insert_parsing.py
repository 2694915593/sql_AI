#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复INSERT语句解析问题
主要修复大模型响应解析中的括号处理问题
"""

import sys
import os
import re
import json

# 设置路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'sql_ai_analyzer'))

print("修复INSERT语句解析问题")
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

# 解析出来的SQL（有问题）
parsed_sql = """insert into MONTHLY_TRAN_MSG

            MTM_PARTY_NO, MTM_SEND, MTM_PRODUCT_TYPE, MTM_PARTY_NAME,

                MTM_CREATE_TIME,


                MTM_UPDATE_TIME,


                MTM_remark1,


                MTM_remark2,



            #{partyNo,jdbcType=VARCHAR}, #{send,jdbcType=VARCHAR}, #{productType,jdbcType=VARCHAR}, #{partyName,jdbcType=VARCHAR},

                #{createTime,jdbcType=TIMESTAMP},


                #{updateTime,jdbcType=TIMESTAMP},


                #{remark1,jdbcType=VARCHAR},


                #{remark2,jdbcType=VARCHAR},"""

print("1. 分析问题:")
print(f"  原始SQL括号: (={original_sql.count('(')}, )={original_sql.count(')')}")
print(f"  解析SQL括号: (={parsed_sql.count('(')}, )={parsed_sql.count(')')}")
print(f"  解析SQL是否包含VALUES: {'VALUES' in parsed_sql.upper()}")
print()

# 定义修复方法
def fix_insert_structure(sql_text: str) -> str:
    """
    修复INSERT语句结构，确保括号完整
    """
    if not sql_text:
        return sql_text
    
    # 检查是否是INSERT语句
    sql_lower = sql_text.lower().strip()
    if not sql_lower.startswith('insert'):
        return sql_text
    
    print(f"  处理INSERT语句: {sql_text[:50]}...")
    
    # 检查括号数量
    open_paren = sql_text.count('(')
    close_paren = sql_text.count(')')
    
    # 如果括号数量为0，尝试修复
    if open_paren == 0 and close_paren == 0:
        print(f"  ⚠️ 检测到INSERT语句缺少括号")
        
        # 查找表名结束位置
        table_name_end = -1
        # 匹配INSERT INTO table_name
        insert_match = re.search(r'insert\s+into\s+([^\s(]+)', sql_lower)
        if insert_match:
            table_name = insert_match.group(1)
            table_name_end = sql_lower.find(table_name) + len(table_name)
            
            # 查找VALUES关键字
            values_pos = sql_lower.find('values', table_name_end)
            if values_pos > 0:
                # 列名部分（表名后到VALUES前）
                columns_part = sql_text[table_name_end:values_pos].strip()
                # 值部分（VALUES后）
                values_part = sql_text[values_pos + 5:].strip()
                
                print(f"    列名部分: {columns_part[:50]}...")
                print(f"    值部分: {values_part[:50]}...")
                
                # 清理列名部分（移除多余空格和换行）
                columns_clean = re.sub(r'\s+', ' ', columns_part).strip()
                # 清理值部分
                values_clean = re.sub(r'\s+', ' ', values_part).strip()
                
                # 检查列名部分是否看起来像列名（包含逗号）
                if ',' in columns_clean:
                    # 在列名部分前后添加括号
                    columns_fixed = f'({columns_clean})'
                else:
                    # 如果列名部分不包含逗号，可能是一个列名
                    columns_fixed = f'({columns_clean})'
                
                # 检查值部分是否看起来像值（包含逗号或参数）
                if ',' in values_clean or '#{' in values_clean:
                    # 在值部分前后添加括号
                    # 但要注意可能已经有引号或其他字符
                    values_fixed = f'({values_clean})'
                else:
                    values_fixed = f'({values_clean})'
                
                # 重新组合SQL
                table_part = sql_text[:table_name_end].strip()
                fixed_sql = f'{table_part} {columns_fixed} VALUES {values_fixed}'
                
                print(f"    修复后SQL: {fixed_sql[:100]}...")
                print(f"    修复后括号: (={fixed_sql.count('(')}, )={fixed_sql.count(')')}")
                
                return fixed_sql
    
    # 如果只有一对括号，但INSERT语句应该有两对括号
    elif open_paren == 1 and close_paren == 1:
        print(f"  ⚠️ 检测到INSERT语句只有一对括号")
        
        # 检查括号位置
        first_paren = sql_text.find('(')
        last_paren = sql_text.rfind(')')
        
        # 查找VALUES关键字
        values_pos = sql_lower.find('values')
        
        if values_pos > 0 and first_paren < values_pos < last_paren:
            # 括号在VALUES之前，这可能是列名括号
            # 需要添加值括号
            print(f"    只有列名括号，缺少值括号")
            
            # 在VALUES后面添加括号
            # 找到VALUES后的内容
            after_values = sql_text[values_pos + 5:].strip()
            
            # 如果VALUES后的内容没有括号，添加
            if not after_values.startswith('('):
                # 找到值的结束位置
                # 如果是参数形式，可能以逗号或分号结束
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
                
                print(f"    修复后SQL: {fixed_sql[:100]}...")
                print(f"    修复后括号: (={fixed_sql.count('(')}, )={fixed_sql.count(')')}")
                
                return fixed_sql
    
    return sql_text

def enhanced_clean_extracted_sql(sql_text: str) -> str:
    """
    增强版的清理提取的SQL方法，特别保护INSERT语句的括号
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
    
    # 5. 修复INSERT语句结构
    cleaned = fix_insert_structure(cleaned)
    
    # 6. 移除首尾空白
    cleaned = cleaned.strip()
    
    return cleaned

# 测试修复方法
print("2. 测试修复方法:")
test_cases = [
    ("原始SQL", original_sql),
    ("解析出来的SQL（有问题）", parsed_sql),
    ("没有括号的INSERT", "insert into MONTHLY_TRAN_MSG MTM_PARTY_NO, MTM_SEND VALUES value1, value2"),
    ("只有列名括号", "insert into MONTHLY_TRAN_MSG (MTM_PARTY_NO, MTM_SEND) VALUES value1, value2"),
    ("只有值括号", "insert into MONTHLY_TRAN_MSG MTM_PARTY_NO, MTM_SEND VALUES (value1, value2)"),
    ("带XML标签", "<insert>insert into test (col1, col2) values (#{val1}, #{val2})</insert>"),
    ("带代码块标记", "```sql\ninsert into test (col1) values (#{val})\n```"),
]

for name, test_sql in test_cases:
    print(f"\n  {name}:")
    print(f"    原始: {test_sql[:60]}...")
    fixed = enhanced_clean_extracted_sql(test_sql)
    print(f"    修复后: {fixed[:60]}...")
    print(f"    括号: (={fixed.count('(')}, )={fixed.count(')')}")

print("\n3. 应用到ModelClient:")
# 我们需要修改model_client_enhanced.py中的_clean_extracted_sql方法
model_client_path = os.path.join(project_root, 'sql_ai_analyzer', 'ai_integration', 'model_client_enhanced.py')
model_client_original_path = os.path.join(project_root, 'sql_ai_analyzer', 'ai_integration', 'model_client.py')

print(f"  主要文件: {model_client_path}")
print(f"  原始文件: {model_client_original_path}")

# 检查文件是否存在
if os.path.exists(model_client_path):
    print(f"  model_client_enhanced.py 存在")
    
    # 备份原始文件
    import shutil
    backup_path = model_client_path + '.backup'
    shutil.copy2(model_client_path, backup_path)
    print(f"  已创建备份: {backup_path}")
    
    # 读取文件内容
    with open(model_client_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 查找_clean_extracted_sql方法
    method_start = content.find('def _clean_extracted_sql(self, sql_text: str) -> str:')
    if method_start == -1:
        # 可能在父类中
        method_start = content.find('def _clean_extracted_sql(')
    
    if method_start != -1:
        print(f"  找到_clean_extracted_sql方法")
        
        # 找到方法结束（下一个def或文件结束）
        next_def = content.find('\ndef ', method_start + 1)
        if next_def == -1:
            next_def = len(content)
        
        method_content = content[method_start:next_def]
        print(f"  原始方法内容（前200字符）: {method_content[:200]}...")
        
        # 替换为增强版方法
        new_method = '''    def _clean_extracted_sql(self, sql_text: str) -> str:
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
        cleaned = re.sub(r'```[\\w]*\\s*', '', cleaned)
        cleaned = re.sub(r'```', '', cleaned)
        
        # 2. 移除XML标签（但要小心不要移除括号）
        # 使用更保守的方法，只移除真正的XML标签
        cleaned = re.sub(r'<[^>]+>', ' ', cleaned)
        
        # 3. 移除CDATA标记
        cleaned = re.sub(r'<!\\[CDATA\\[', '', cleaned)
        cleaned = re.sub(r'\\]\\]>', '', cleaned)
        
        # 4. 压缩多余空格，但保留换行符（对多行SQL很重要）
        # 先分割为行，单独处理每行
        lines = cleaned.split('\\n')
        cleaned_lines = []
        for line in lines:
            line = re.sub(r'\\s+', ' ', line.strip())
            if line:
                cleaned_lines.append(line)
        
        # 重新组合，保留换行符（对多行SQL很重要）
        cleaned = '\\n'.join(cleaned_lines)
        
        # 5. 修复INSERT语句结构（如果缺少括号）
        cleaned = self._fix_insert_structure_if_needed(cleaned)
        
        # 6. 移除首尾空白
        cleaned = cleaned.strip()
        
        return cleaned'''
        
        # 添加辅助方法
        new_helper_method = '''
    def _fix_insert_structure_if_needed(self, sql_text: str) -> str:
        """
        如果需要，修复INSERT语句结构，确保括号完整
        
        Args:
            sql_text: SQL文本
            
        Returns:
            修复后的SQL文本
        """
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
            self.logger.debug("检测到INSERT语句缺少括号，尝试修复")
            
            # 查找表名结束位置
            table_name_end = -1
            # 匹配INSERT INTO table_name
            import re
            insert_match = re.search(r'insert\\s+into\\s+([^\\s(]+)', sql_lower)
            if insert_match:
                table_name = insert_match.group(1)
                table_name_end = sql_lower.find(table_name) + len(table_name)
                
                # 查找VALUES关键字
                values_pos = sql_lower.find('values', table_name_end)
                if values_pos > 0:
                    # 列名部分（表名后到VALUES前）
                    columns_part = sql_text[table_name_end:values_pos].strip()
                    # 值部分（VALUES后）
                    values_part = sql_text[values_pos + 5:].strip()
                    
                    # 清理列名部分（移除多余空格和换行）
                    columns_clean = re.sub(r'\\s+', ' ', columns_part).strip()
                    # 清理值部分
                    values_clean = re.sub(r'\\s+', ' ', values_part).strip()
                    
                    # 检查列名部分是否看起来像列名（包含逗号）
                    if ',' in columns_clean or any(keyword in columns_clean.lower() for keyword in ['mtm_', 'col', 'field', 'id']):
                        # 在列名部分前后添加括号
                        columns_fixed = f'({columns_clean})'
                    else:
                        # 如果列名部分不包含逗号，可能是一个列名
                        columns_fixed = f'({columns_clean})'
                    
                    # 检查值部分是否看起来像值（包含逗号或参数）
                    if ',' in values_clean or '#{' in values_clean or 'value' in values_clean.lower():
                        # 在值部分前后添加括号
                        # 但要注意可能已经有引号或其他字符
                        values_fixed = f'({values_clean})'
                    else:
                        values_fixed = f'({values_clean})'
                    
                    # 重新组合SQL
                    table_part = sql_text[:table_name_end].strip()
                    fixed_sql = f'{table_part} {columns_fixed} VALUES {values_fixed}'
                    
                    self.logger.debug(f"修复INSERT语句结构: 原始长度={len(sql_text)}, 修复后长度={len(fixed_sql)}")
                    return fixed_sql
        
        # 如果只有一对括号，但INSERT语句应该有两对括号
        elif open_paren == 1 and close_paren == 1:
            self.logger.debug("检测到INSERT语句只有一对括号，尝试修复")
            
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
                    # 如果是参数形式，可能以逗号或分号结束
                    end_pos = len(sql_text)
                    for end_char in [',', ';', '\\n']:
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
                    
                    self.logger.debug(f"为INSERT语句添加值括号: 原始长度={len(sql_text)}, 修复后长度={len(fixed_sql)}")
                    return fixed_sql
        
        return sql_text'''
        
        # 替换方法
        new_content = content[:method_start] + new_method + '\n\n' + new_helper_method + content[next_def:]
        
        # 写回文件
        with open(model_client_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"  已更新_clean_extracted_sql方法")
        print(f"  已添加_fix_insert_structure_if_needed辅助方法")
        
        # 也更新原始model_client.py文件
        if os.path.exists(model_client_original_path):
            with open(model_client_original_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            # 查找_clean_extracted_sql方法
            orig_method_start = original_content.find('def _clean_extracted_sql(self, sql_text: str) -> str:')
            if orig_method_start == -1:
                orig_method_start = original_content.find('def _clean_extracted_sql(')
            
            if orig_method_start != -1:
                # 找到方法结束
                orig_next_def = original_content.find('\ndef ', orig_method_start + 1)
                if orig_next_def == -1:
                    orig_next_def = len(original_content)
                
                # 备份原始文件
                orig_backup_path = model_client_original_path + '.backup'
                shutil.copy2(model_client_original_path, orig_backup_path)
                print(f"  已创建原始文件备份: {orig_backup_path}")
                
                # 替换
                new_original_content = original_content[:orig_method_start] + new_method + '\n\n' + new_helper_method + original_content[orig_next_def:]
                
                with open(model_client_original_path, 'w', encoding='utf-8') as f:
                    f.write(new_original_content)
                
                print(f"  已更新原始model_client.py文件")
    else:
        print(f"  未找到_clean_extracted_sql方法")
else:
    print(f"  model_client_enhanced.py 不存在")

print("\n" + "=" * 80)
print("修复完成")
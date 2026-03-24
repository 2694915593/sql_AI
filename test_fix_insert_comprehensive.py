#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
综合测试INSERT语句解析修复
"""

import sys
import os
import re

# 设置路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'sql_ai_analyzer'))

print("综合测试INSERT语句解析修复")
print("=" * 80)

# 用户提供的解析出来的SQL（有问题）
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

print("1. 原始解析SQL分析:")
print(f"  长度: {len(parsed_sql)}")
print(f"  括号: (={parsed_sql.count('(')}, )={parsed_sql.count(')')}")
print(f"  包含VALUES: {'VALUES' in parsed_sql.upper()}")
print(f"  包含#{{: {'#{' in parsed_sql}")
print()

# 尝试使用修复后的ModelClient方法
try:
    from sql_ai_analyzer.ai_integration.model_client_enhanced import ModelClient
    
    # 创建模拟的配置管理器
    class MockConfigManager:
        def get_ai_model_config(self):
            return {
                'api_url': 'http://test.com',
                'api_key': 'test',
                'timeout': 30,
                'max_retries': 3
            }
    
    # 创建简单的logger
    import logging
    logger = logging.getLogger('test')
    logger.setLevel(logging.WARNING)
    
    # 创建ModelClient实例
    config_manager = MockConfigManager()
    model_client = ModelClient(config_manager, logger)
    
    print("2. 测试修复后的_clean_extracted_sql方法:")
    
    # 直接调用_clean_extracted_sql方法
    cleaned_sql = model_client._clean_extracted_sql(parsed_sql)
    print(f"  清理后SQL: {cleaned_sql[:100]}...")
    print(f"  长度: {len(cleaned_sql)}")
    print(f"  括号: (={cleaned_sql.count('(')}, )={cleaned_sql.count(')')}")
    
    # 调用_fix_insert_structure_if_needed方法
    print("\n3. 直接测试_fix_insert_structure_if_needed方法:")
    fixed_sql = model_client._fix_insert_structure_if_needed(parsed_sql)
    print(f"  修复后SQL: {fixed_sql[:100]}...")
    print(f"  长度: {len(fixed_sql)}")
    print(f"  括号: (={fixed_sql.count('(')}, )={fixed_sql.count(')')}")
    
    # 分析SQL结构
    print("\n4. 详细分析SQL结构:")
    
    # 检查是否有VALUES关键字
    sql_lower = parsed_sql.lower()
    values_pos = sql_lower.find('values')
    print(f"  VALUES位置: {values_pos}")
    
    if values_pos == -1:
        print("  ⚠️ 未找到VALUES关键字")
        
        # 尝试找到列名和值的分界点
        # 列名以MTM_开头，值以#{开头
        # 查找第一个#{的位置
        first_param = parsed_sql.find('#{')
        print(f"  第一个参数位置: {first_param}")
        
        if first_param > 0:
            columns_part = parsed_sql[:first_param].strip()
            values_part = parsed_sql[first_param:].strip()
            
            print(f"  列名部分前100字符: {columns_part[:100]}...")
            print(f"  值部分前100字符: {values_part[:100]}...")
            
            # 清理列名部分
            columns_clean = re.sub(r'\s+', ' ', columns_part)
            # 移除表名
            if columns_clean.startswith('insert into'):
                # 找到表名结束
                table_match = re.search(r'insert\s+into\s+([^\s]+)', columns_clean.lower())
                if table_match:
                    table_name = table_match.group(1)
                    table_end = columns_clean.lower().find(table_name) + len(table_name)
                    columns_only = columns_clean[table_end:].strip()
                    print(f"  纯列名部分: {columns_only[:100]}...")
                    
                    # 检查是否有逗号分隔
                    if ',' in columns_only or 'MTM_' in columns_only:
                        # 添加VALUES关键字和括号
                        table_part = columns_clean[:table_end].strip()
                        columns_fixed = f'({columns_only})'
                        # 清理值部分
                        values_clean = re.sub(r'\s+', ' ', values_part)
                        # 移除末尾的逗号
                        if values_clean.endswith(','):
                            values_clean = values_clean[:-1]
                        values_fixed = f'({values_clean})'
                        
                        reconstructed = f'{table_part} {columns_fixed} VALUES {values_fixed}'
                        print(f"  重构后SQL: {reconstructed[:100]}...")
                        print(f"  括号: (={reconstructed.count('(')}, )={reconstructed.count(')')}")
    
    # 测试增强修复方法
    print("\n5. 测试增强修复方法:")
    
    def enhanced_fix_insert(sql_text):
        """增强的INSERT语句修复"""
        if not sql_text:
            return sql_text
        
        sql_lower = sql_text.lower().strip()
        if not sql_lower.startswith('insert'):
            return sql_text
        
        # 检查括号
        open_paren = sql_text.count('(')
        close_paren = sql_text.count(')')
        
        # 如果没有括号
        if open_paren == 0 and close_paren == 0:
            # 尝试找到表名
            table_match = re.search(r'insert\s+into\s+([^\s(]+)', sql_lower)
            if table_match:
                table_name = table_match.group(1)
                table_end = sql_lower.find(table_name) + len(table_name)
                
                # 查找可能的列名部分（以列名特征开头）
                # 假设列名以大写字母或下划线开头
                after_table = sql_text[table_end:].strip()
                
                # 查找第一个参数（#{）作为列名和值的分界
                param_start = after_table.find('#{')
                if param_start > 0:
                    columns_part = after_table[:param_start].strip()
                    values_part = after_table[param_start:].strip()
                    
                    # 清理列名部分
                    columns_clean = re.sub(r'\s+', ' ', columns_part).strip()
                    # 清理值部分
                    values_clean = re.sub(r'\s+', ' ', values_part).strip()
                    
                    # 移除值部分的末尾逗号
                    if values_clean.endswith(','):
                        values_clean = values_clean[:-1].strip()
                    
                    # 添加括号
                    columns_fixed = f'({columns_clean})'
                    values_fixed = f'({values_clean})'
                    
                    # 重构SQL
                    table_part = sql_text[:table_end].strip()
                    return f'{table_part} {columns_fixed} VALUES {values_fixed}'
        
        return sql_text
    
    enhanced_fixed = enhanced_fix_insert(parsed_sql)
    print(f"  增强修复后SQL: {enhanced_fixed[:100]}...")
    print(f"  括号: (={enhanced_fixed.count('(')}, )={enhanced_fixed.count(')')}")
    
    # 将增强修复方法应用到ModelClient
    print("\n6. 更新ModelClient的修复方法:")
    
    # 读取修改后的文件
    model_client_path = os.path.join(project_root, 'sql_ai_analyzer', 'ai_integration', 'model_client_enhanced.py')
    with open(model_client_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 查找_fix_insert_structure_if_needed方法
    method_start = content.find('def _fix_insert_structure_if_needed')
    if method_start != -1:
        # 找到方法结束
        next_def = content.find('\ndef ', method_start + 1)
        if next_def == -1:
            next_def = len(content)
        
        # 新的增强方法
        new_method = '''    def _fix_insert_structure_if_needed(self, sql_text: str) -> str:
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
            
            # 尝试找到表名
            import re
            table_match = re.search(r'insert\\s+into\\s+([^\\s(]+)', sql_lower)
            if table_match:
                table_name = table_match.group(1)
                table_end = sql_lower.find(table_name) + len(table_name)
                
                # 查找可能的列名部分（以列名特征开头）
                # 假设列名以大写字母或下划线开头
                after_table = sql_text[table_end:].strip()
                
                # 查找第一个参数（#{）作为列名和值的分界
                param_start = after_table.find('#{')
                if param_start > 0:
                    columns_part = after_table[:param_start].strip()
                    values_part = after_table[param_start:].strip()
                else:
                    # 如果没有参数，尝试用逗号或其他方式分割
                    # 简单起见，假设从表名后到第一个逗号是列名
                    first_comma = after_table.find(',')
                    if first_comma > 0:
                        columns_part = after_table[:first_comma].strip()
                        values_part = after_table[first_comma + 1:].strip()
                    else:
                        # 无法分割，返回原样
                        return sql_text
                
                # 清理列名部分
                columns_clean = re.sub(r'\\s+', ' ', columns_part).strip()
                # 清理值部分
                values_clean = re.sub(r'\\s+', ' ', values_part).strip()
                
                # 移除值部分的末尾逗号
                if values_clean.endswith(','):
                    values_clean = values_clean[:-1].strip()
                
                # 添加括号
                columns_fixed = f'({columns_clean})'
                values_fixed = f'({values_clean})'
                
                # 重构SQL
                table_part = sql_text[:table_end].strip()
                fixed_sql = f'{table_part} {columns_fixed} VALUES {values_fixed}'
                
                self.logger.debug(f"修复INSERT语句结构: 原始长度={len(sql_text)}, 修复后长度={len(fixed_sql)}")
                return fixed_sunk
        
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
        new_content = content[:method_start] + new_method + content[next_def:]
        
        # 写回文件
        with open(model_client_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("  已更新ModelClient的_fix_insert_structure_if_needed方法")
        
        # 重新测试
        print("\n7. 重新测试更新后的方法:")
        # 重新创建ModelClient实例（重新加载模块）
        import importlib
        import sys
        if 'sql_ai_analyzer.ai_integration.model_client_enhanced' in sys.modules:
            del sys.modules['sql_ai_analyzer.ai_integration.model_client_enhanced']
        
        from sql_ai_analyzer.ai_integration.model_client_enhanced import ModelClient
        model_client2 = ModelClient(config_manager, logger)
        
        fixed_sql2 = model_client2._fix_insert_structure_if_needed(parsed_sql)
        print(f"  修复后SQL: {fixed_sql2[:100]}...")
        print(f"  括号: (={fixed_sql2.count('(')}, )={fixed_sql2.count(')')}")
        
    else:
        print("  未找到_fix_insert_structure_if_needed方法")
    
except Exception as e:
    print(f"测试失败: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("测试完成")
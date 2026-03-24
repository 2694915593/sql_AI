#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最终测试INSERT语句解析修复
"""

import sys
import os
import re

# 设置路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'sql_ai_analyzer'))

print("最终测试INSERT语句解析修复")
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

print("1. 测试ModelClient的修复方法:")
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
    
    # 测试_clean_extracted_sql方法
    print(f"  原始SQL长度: {len(parsed_sql)}")
    print(f"  原始SQL括号: (={parsed_sql.count('(')}, )={parsed_sql.count(')')}")
    
    cleaned_sql = model_client._clean_extracted_sql(parsed_sql)
    print(f"  清理后SQL长度: {len(cleaned_sql)}")
    print(f"  清理后SQL括号: (={cleaned_sql.count('(')}, )={cleaned_sql.count(')')}")
    
    # 显示前200字符
    print(f"  清理后SQL前200字符: {cleaned_sql[:200]}")
    
    # 测试_fix_insert_structure_if_needed方法
    print("\n2. 直接测试_fix_insert_structure_if_needed方法:")
    fixed_sql = model_client._fix_insert_structure_if_needed(parsed_sql)
    print(f"  修复后SQL长度: {len(fixed_sql)}")
    print(f"  修复后SQL括号: (={fixed_sql.count('(')}, )={fixed_sql.count(')')}")
    print(f"  修复后SQL前200字符: {fixed_sql[:200]}")
    
    # 检查修复是否成功
    print("\n3. 修复结果分析:")
    if fixed_sql.count('(') >= 2 and fixed_sql.count(')') >= 2:
        print(f"  ✅ 修复成功: SQL现在有{fixed_sql.count('(')}个开括号和{fixed_sql.count(')')}个闭括号")
        
        # 检查是否包含VALUES关键字
        if 'VALUES' in fixed_sql.upper() or 'values' in fixed_sql.lower():
            print(f"  ✅ 包含VALUES关键字")
        else:
            print(f"  ⚠️  缺少VALUES关键字")
            
        # 检查SQL结构
        if fixed_sql.count('(') == 2 and fixed_sql.count(')') == 2:
            # 查找括号位置
            first_paren = fixed_sql.find('(')
            last_paren = fixed_sql.rfind(')')
            second_paren = fixed_sql.find('(', first_paren + 1)
            
            if first_paren < second_paren < last_paren:
                print(f"  ✅ 括号结构正确: 第一个括号在{first_paren}, 第二个括号在{second_paren}, 最后一个括号在{last_paren}")
                
                # 提取列名部分和值部分
                columns_part = fixed_sql[first_paren:second_paren + 1] if second_paren > first_paren else "N/A"
                values_part = fixed_sql[second_paren:last_paren + 1] if last_paren > second_paren else "N/A"
                
                print(f"  列名部分: {columns_part[:100]}...")
                print(f"  值部分: {values_part[:100]}...")
    else:
        print(f"  ❌ 修复失败: SQL仍然缺少括号 (={fixed_sql.count('(')}, )={fixed_sql.count(')')})")
    
    # 手动修复测试
    print("\n4. 手动修复测试:")
    
    def manual_fix_insert(sql_text):
        """手动修复INSERT语句"""
        # 清理多余空格和换行
        sql_text = re.sub(r'\s+', ' ', sql_text).strip()
        
        # 查找表名
        import re
        match = re.search(r'insert\s+into\s+([^\s]+)', sql_text.lower())
        if not match:
            return sql_text
            
        table_name = match.group(1)
        table_end = sql_text.lower().find(table_name) + len(table_name)
        
        # 查找第一个#{参数
        param_start = sql_text.find('#{', table_end)
        if param_start == -1:
            return sql_text
            
        # 分割列名和值
        columns_part = sql_text[table_end:param_start].strip()
        values_part = sql_text[param_start:].strip()
        
        # 清理末尾逗号
        if values_part.endswith(','):
            values_part = values_part[:-1].strip()
            
        # 添加括号
        columns_fixed = f'({columns_part})'
        values_fixed = f'({values_part})'
        
        # 重构SQL
        table_part = sql_text[:table_end].strip()
        return f'{table_part} {columns_fixed} VALUES {values_fixed}'
    
    manual_fixed = manual_fix_insert(parsed_sql)
    print(f"  手动修复后SQL: {manual_fixed[:150]}")
    print(f"  手动修复括号: (={manual_fixed.count('(')}, )={manual_fixed.count(')')}")
    
except Exception as e:
    print(f"测试失败: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("测试完成")
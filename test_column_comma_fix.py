#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试列名末尾逗号修复
"""

import sys
import os

# 设置路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'sql_ai_analyzer'))

print("测试列名末尾逗号修复")
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
    
    print(f"  原始SQL长度: {len(parsed_sql)}")
    print(f"  原始SQL括号: (={parsed_sql.count('(')}, )={parsed_sql.count(')')}")
    
    # 测试_clean_extracted_sql方法
    cleaned_sql = model_client._clean_extracted_sql(parsed_sql)
    print(f"  清理后SQL长度: {len(cleaned_sql)}")
    print(f"  清理后SQL括号: (={cleaned_sql.count('(')}, )={cleaned_sql.count(')')}")
    
    # 测试_fix_insert_structure_if_needed方法
    fixed_sql = model_client._fix_insert_structure_if_needed(parsed_sql)
    print(f"  修复后SQL长度: {len(fixed_sql)}")
    print(f"  修复后SQL括号: (={fixed_sql.count('(')}, )={fixed_sql.count(')')}")
    
    # 检查是否有列名末尾逗号
    print("\n2. 检查列名末尾逗号:")
    
    # 查找第一个括号内的内容（列名部分）
    first_paren = fixed_sql.find('(')
    second_paren = fixed_sql.find('(', first_paren + 1) if first_paren != -1 else -1
    
    if first_paren != -1 and second_paren != -1:
        columns_part = fixed_sql[first_paren:second_paren + 1] if second_paren > first_paren else fixed_sql[first_paren:]
        print(f"  列名部分: {columns_part}")
        
        # 检查末尾逗号
        if columns_part.endswith(',)'):
            print(f"  ❌ 列名部分末尾有逗号: {columns_part[-20:]}")
            print(f"    需要修复")
        else:
            print(f"  ✅ 列名部分末尾无逗号")
            
        # 检查语法
        if '()' in columns_part:
            print(f"  ⚠️  列名部分包含空括号")
        else:
            print(f"  ✅ 列名部分语法正确")
            
        # 检查完整SQL
        print(f"\n3. 完整的修复后SQL:")
        print(f"{fixed_sql}")
        
        # 检查是否有语法错误
        print(f"\n4. SQL语法检查:")
        if fixed_sql.endswith(','):
            print(f"  ⚠️  SQL以逗号结束")
        else:
            print(f"  ✅ SQL结尾正常")
            
        # 检查列名部分是否以逗号结尾
        if columns_part.endswith(',)'):
            # 手动修复
            print(f"\n5. 手动修复列名末尾逗号:")
            fixed_columns = columns_part[:-2] + ')'
            print(f"  修复前: {columns_part}")
            print(f"  修复后: {fixed_columns}")
            
            # 重建完整SQL
            if second_paren > first_paren:
                before_columns = fixed_sql[:first_paren]
                after_columns = fixed_sql[second_paren:]
                final_sql = before_columns + fixed_columns + after_columns
            else:
                final_sql = fixed_sql[:first_paren] + fixed_columns + fixed_sql[first_paren + len(columns_part):]
            
            print(f"  最终修复后SQL: {final_sql}")
    
except Exception as e:
    print(f"测试失败: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("测试完成")
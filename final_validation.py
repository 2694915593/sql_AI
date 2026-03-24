#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最终验证INSERT语句解析修复
"""

import sys
import os

# 设置路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'sql_ai_analyzer'))

print("最终验证INSERT语句解析修复")
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

print("1. 原始SQL分析:")
print(f"  长度: {len(parsed_sql)}")
print(f"  括号: (={parsed_sql.count('(')}, )={parsed_sql.count(')')}")
print(f"  包含VALUES: {'VALUES' in parsed_sql.upper()}")
print(f"  包含#{{: {'#{' in parsed_sql}")
print()

# 测试修复后的方法
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
    
    print("2. 测试_clean_extracted_sql方法:")
    cleaned_sql = model_client._clean_extracted_sql(parsed_sql)
    print(f"  清理后SQL长度: {len(cleaned_sql)}")
    print(f"  清理后SQL括号: (={cleaned_sql.count('(')}, )={cleaned_sql.count(')')}")
    print(f"  清理后SQL前100字符: {cleaned_sql[:100]}")
    
    print("\n3. 测试_fix_insert_structure_if_needed方法:")
    fixed_sql = model_client._fix_insert_structure_if_needed(parsed_sql)
    print(f"  修复后SQL长度: {len(fixed_sql)}")
    print(f"  修复后SQL括号: (={fixed_sql.count('(')}, )={fixed_sql.count(')')}")
    print(f"  修复后SQL前150字符: {fixed_sql[:150]}")
    
    print("\n4. 修复结果分析:")
    if fixed_sql.count('(') >= 2 and fixed_sql.count(')') >= 2:
        print(f"  ✅ 修复成功: SQL现在有{fixed_sql.count('(')}个开括号和{fixed_sql.count(')')}个闭括号")
        
        # 检查是否包含VALUES关键字
        if 'VALUES' in fixed_sql.upper() or 'values' in fixed_sql.lower():
            print(f"  ✅ 包含VALUES关键字")
        else:
            print(f"  ⚠️ 缺少VALUES关键字")
            
        # 检查SQL结构
        if fixed_sql.count('(') == 2 and fixed_sql.count(')') == 2:
            print(f"  ✅ 括号结构正确 (两对括号)")
            
            # 提取完整SQL
            print(f"\n5. 完整的修复后SQL:")
            print(f"{fixed_sql}")
    else:
        print(f"  ❌ 修复失败: SQL仍然缺少括号 (={fixed_sql.count('(')}, )={fixed_sql.count(')')})")
    
    # 比较原始SQL和修复后SQL
    print("\n6. 修复前后对比:")
    print(f"  原始SQL长度: {len(parsed_sql)}")
    print(f"  修复后SQL长度: {len(fixed_sql)}")
    print(f"  括号修复: (={parsed_sql.count('(')}->{fixed_sql.count('(')}, )={parsed_sql.count(')')}->{fixed_sql.count(')')})")
    
except Exception as e:
    print(f"测试失败: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("验证完成")
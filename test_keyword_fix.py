#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试SQL关键字修复功能
"""

import re
import sys
import os

# 模拟 dynamic_sql_parser 中的修复方法
def fix_sql_keywords_if_needed(sql):
    """
    修复SQL关键字丢失问题
    
    Args:
        sql: SQL语句
        
    Returns:
        修复后的SQL语句
    """
    if not sql:
        return sql
    
    sql_upper = sql.upper()
    
    # 修复UPDATE语句缺少SET关键字的问题
    if sql_upper.startswith('UPDATE'):
        if 'SET' not in sql_upper:
            # 找到UPDATE后面的表名
            words = sql.split()
            if len(words) >= 2:
                # UPDATE table_name ... 
                # 在表名后插入SET
                result_parts = []
                for i, word in enumerate(words):
                    result_parts.append(word)
                    # 在第二个单词（表名）后插入SET
                    if i == 1:  # 表名位置
                        # 检查下一个单词是否是SET（以防万一）
                        if i + 1 < len(words) and words[i + 1].upper() != 'SET':
                            result_parts.append('SET')
                
                fixed_sql = ' '.join(result_parts)
                
                # 如果仍然没有SET，确保在表名后添加
                if 'SET' not in fixed_sql.upper():
                    # 简单的修复：在UPDATE table_name后添加SET
                    pattern = r'(UPDATE\s+\w+)'
                    fixed_sql = re.sub(pattern, r'\1 SET', fixed_sql, flags=re.IGNORECASE)
                
                return fixed_sql
    
    # TODO: 可以在这里添加其他SQL语句的修复
    # 例如：INSERT语句缺少VALUES，SELECT语句缺少FROM等
    
    return sql


def test_fix_sql_keywords():
    """测试SQL关键字修复"""
    
    print("=== 测试SQL关键字修复功能 ===")
    print()
    
    # 用户提供的例子
    test_case_1 = {
        'description': '用户提供的UPDATE例子 - 缺少SET关键字',
        'original': 'UPDATE MONTHLY_TRAN_MSG MTM_SEND =#{send,jdbcType=VARCHAR}, MTM_PARTY_NAME =#{partyName,jdbcType=VARCHAR}, MTM_CREATE_TIME =#{createTime,jdbcType=TIMESTAMP}, MTM_UPDATE_TIME =#{updateTime,jdbcType=TIMESTAMP}, MTM_REMARK1 = #{remark1,jdbcType=VARCHAR}, MTM_REMARK2 = #{remark2,jdbcType=VARCHAR}, WHERE MTM_PARTY_NO =#{partyNo,jdbcType=VARCHAR} AND MTM_PRODUCT_TYPE =#{productType,jdbcType=VARCHAR}',
        'expected_contains_set': True
    }
    
    test_case_2 = {
        'description': '简单UPDATE例子 - 缺少SET关键字',
        'original': 'UPDATE table col = 1 WHERE id = 1',
        'expected_contains_set': True
    }
    
    test_case_3 = {
        'description': 'UPDATE已有SET关键字 - 不应修改',
        'original': 'UPDATE table SET col = 1 WHERE id = 1',
        'expected_contains_set': True
    }
    
    test_case_4 = {
        'description': 'SELECT语句 - 不应修改',
        'original': 'SELECT * FROM table',
        'expected_contains_set': False
    }
    
    test_case_5 = {
        'description': 'INSERT语句 - 测试（当前不修复）',
        'original': 'INSERT INTO users (id, name) VALUES (1, "John")',
        'expected_contains_set': False
    }
    
    test_case_6 = {
        'description': 'UPDATE表名后直接WHERE（边界情况）',
        'original': 'UPDATE table WHERE id = 1',
        'expected_contains_set': True  # 应该添加SET
    }
    
    test_cases = [test_case_1, test_case_2, test_case_3, test_case_4, test_case_5, test_case_6]
    
    all_passed = True
    
    for i, test in enumerate(test_cases, 1):
        print(f"测试 {i}: {test['description']}")
        print(f"原始SQL: {test['original'][:60]}...")
        
        original_has_set = 'SET' in test['original'].upper()
        fixed = fix_sql_keywords_if_needed(test['original'])
        fixed_has_set = 'SET' in fixed.upper()
        
        print(f"原始包含SET: {original_has_set}")
        print(f"修复后包含SET: {fixed_has_set}")
        print(f"期望包含SET: {test['expected_contains_set']}")
        
        # 检查测试是否通过
        if test['expected_contains_set']:
            passed = fixed_has_set
        else:
            passed = fixed_has_set == original_has_set
        
        if passed:
            print(f"结果: ✓ 通过")
        else:
            print(f"结果: ✗ 失败")
            all_passed = False
        
        print(f"修复后SQL: {fixed[:70]}...")
        print()
    
    # 专门测试用户提供的例子
    print("=== 详细测试用户提供的例子 ===")
    user_sql = test_case_1['original']
    print(f"原始SQL长度: {len(user_sql)}")
    print(f"原始SQL是否包含SET: {'SET' in user_sql.upper()}")
    
    fixed_sql = fix_sql_keywords_if_needed(user_sql)
    print(f"修复后SQL长度: {len(fixed_sql)}")
    print(f"修复后SQL是否包含SET: {'SET' in fixed_sql.upper()}")
    
    # 检查修复是否正确
    if 'UPDATE MONTHLY_TRAN_MSG SET' in fixed_sql:
        print("✓ 修复成功：在表名后正确添加了SET关键字")
    else:
        print("✗ 修复失败：未正确添加SET关键字")
        all_passed = False
    
    print()
    print(f"原始SQL前100字符: {user_sql[:100]}")
    print(f"修复后SQL前100字符: {fixed_sql[:100]}")
    
    print()
    print("=== 测试总结 ===")
    if all_passed:
        print("✓ 所有测试通过！")
    else:
        print("✗ 部分测试失败！")
    
    return all_passed


if __name__ == '__main__':
    success = test_fix_sql_keywords()
    sys.exit(0 if success else 1)
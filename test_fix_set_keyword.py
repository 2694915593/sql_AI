#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试修复SET关键字丢失问题
"""

import sys
import os
import re

# 添加路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sql_ai_analyzer'))

try:
    from sql_ai_analyzer.ai_integration.model_client import ModelClient
except ImportError as e:
    print(f"导入错误: {e}")
    # 尝试直接导入
    import sql_ai_analyzer.ai_integration.model_client as model_client_module
    ModelClient = model_client_module.ModelClient

def create_mock_model_client():
    """创建模拟的ModelClient实例"""
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
    return ModelClient(config_manager, logger)

def test_clean_extracted_sql():
    """测试_clean_extracted_sql方法"""
    print("测试_clean_extracted_sql方法")
    print("=" * 80)
    
    client = create_mock_model_client()
    
    test_cases = [
        # (输入SQL, 描述, 预期输出包含SET)
        (
            "update MONTHLY_TRAN_MSG\nMTM_SEND =#{send,jdbcType=VARCHAR}, MTM_PARTY_NAME =#{partyName,jdbcType=VARCHAR},\nMTM_CREATE_TIME =#{createTime,jdbcType=TIMESTAMP},\nMTM_UPDATE_TIME =#{updateTime,jdbcType=TIMESTAMP},\nMTM_REMARK1 = #{remark1,jdbcType=VARCHAR},\nMTM_REMARK2 = #{remark2,jdbcType=VARCHAR},\nWHERE MTM_PARTY_NO =#{partyNo,jdbcType=VARCHAR} AND MTM_PRODUCT_TYPE =#{productType,jdbcType=VARCHAR}",
            "用户提供的缺少SET的UPDATE语句",
            True
        ),
        (
            "UPDATE MONTHLY_TRAN_MSG\nSET\n    MTM_SEND = #{send,jdbcType=VARCHAR},\n    MTM_PARTY_NAME = #{partyName,jdbcType=VARCHAR},\n    MTM_CREATE_TIME = #{createTime,jdbcType=TIMESTAMP},\n    MTM_UPDATE_TIME = #{updateTime,jdbcType=TIMESTAMP},\n    MTM_REMARK1 = #{remark1,jdbcType=VARCHAR},\n    MTM_REMARK2 = #{remark2,jdbcType=VARCHAR}\nWHERE\n    MTM_PARTY_NO = #{partyNo,jdbcType=VARCHAR}\n    AND MTM_PRODUCT_TYPE = #{productType,jdbcType=VARCHAR}",
            "标准的UPDATE语句（有SET）",
            True
        ),
        (
            "sql\nUPDATE MONTHLY_TRAN_MSG\nSET\n    MTM_SEND = #{send,jdbcType=VARCHAR},\n    MTM_PARTY_NAME = #{partyName,jdbcType=VARCHAR},\n    MTM_CREATE_TIME = #{createTime,jdbcType=TIMESTAMP},\n    MTM_UPDATE_TIME = #{updateTime,jdbcType=TIMESTAMP},\n    MTM_REMARK1 = #{remark1,jdbcType=VARCHAR},\n    MTM_REMARK2 = #{remark2,jdbcType=VARCHAR}\nWHERE\n    MTM_PARTY_NO = #{partyNo,jdbcType=VARCHAR}\n    AND MTM_PRODUCT_TYPE = #{productType,jdbcType=VARCHAR}",
            "带'sql'前缀的UPDATE语句",
            True
        ),
        (
            "```sql\nUPDATE MONTHLY_TRAN_MSG\nSET\n    MTM_SEND = #{send,jdbcType=VARCHAR},\n    MTM_PARTY_NAME = #{partyName,jdbcType=VARCHAR},\n    MTM_CREATE_TIME = #{createTime,jdbcType=TIMESTAMP},\n    MTM_UPDATE_TIME = #{updateTime,jdbcType=TIMESTAMP},\n    MTM_REMARK1 = #{remark1,jdbcType=VARCHAR},\n    MTM_REMARK2 = #{remark2,jdbcType=VARCHAR}\nWHERE\n    MTM_PARTY_NO = #{partyNo,jdbcType=VARCHAR}\n    AND MTM_PRODUCT_TYPE = #{productType,jdbcType=VARCHAR}\n```",
            "带代码块标记的UPDATE语句",
            True
        ),
        (
            "<update>UPDATE MONTHLY_TRAN_MSG\nSET\n    MTM_SEND = #{send,jdbcType=VARCHAR},\n    MTM_PARTY_NAME = #{partyName,jdbcType=VARCHAR},\n    MTM_CREATE_TIME = #{createTime,jdbcType=TIMESTAMP},\n    MTM_UPDATE_TIME = #{updateTime,jdbcType=TIMESTAMP},\n    MTM_REMARK1 = #{remark1,jdbcType=VARCHAR},\n    MTM_REMARK2 = #{remark2,jdbcType=VARCHAR}\nWHERE\n    MTM_PARTY_NO = #{partyNo,jdbcType=VARCHAR}\n    AND MTM_PRODUCT_TYPE = #{productType,jdbcType=VARCHAR}</update>",
            "带XML标签的UPDATE语句",
            True
        ),
        (
            "UPDATE table SET col = 1 WHERE id = 1",
            "简单的UPDATE语句",
            True
        ),
        (
            "UPDATE table col = 1 WHERE id = 1",
            "缺少SET的简单UPDATE语句",
            True
        ),
        (
            "UPDATE table\ncol1 = 1,\ncol2 = 2\nWHERE id = 1",
            "缺少SET的多行UPDATE语句",
            True
        ),
    ]
    
    all_passed = True
    
    for sql_text, description, expected_has_set in test_cases:
        print(f"\n测试: {description}")
        print(f"输入长度: {len(sql_text)}")
        
        try:
            # 调用清理方法
            cleaned = client._clean_extracted_sql(sql_text)
            print(f"输出长度: {len(cleaned)}")
            
            # 检查是否包含SET关键字
            has_set = 'SET' in cleaned.upper()
            print(f"是否包含SET: {has_set} (期望: {expected_has_set})")
            
            # 检查其他SQL关键字是否保留
            has_update = 'UPDATE' in cleaned.upper()
            has_where = 'WHERE' in cleaned.upper()
            print(f"是否包含UPDATE: {has_update}")
            print(f"是否包含WHERE: {has_where}")
            
            if has_set != expected_has_set:
                print(f"❌ 失败: SET关键字检查不符合预期")
                print(f"清理前: {sql_text[:100]}...")
                print(f"清理后: {cleaned[:100]}...")
                all_passed = False
            else:
                print(f"✅ 通过")
                
        except Exception as e:
            print(f"❌ 异常: {e}")
            import traceback
            traceback.print_exc()
            all_passed = False
    
    print(f"\n{'=' * 80}")
    if all_passed:
        print("✅ 所有测试通过")
    else:
        print("❌ 部分测试失败")
    
    return all_passed

def test_fix_update_statement_if_needed():
    """测试_fix_update_statement_if_needed方法"""
    print("\n\n测试_fix_update_statement_if_needed方法")
    print("=" * 80)
    
    client = create_mock_model_client()
    
    test_cases = [
        # (输入SQL, 描述, 预期修复后包含SET)
        (
            "UPDATE MONTHLY_TRAN_MSG MTM_SEND = 1 WHERE id = 1",
            "缺少SET的简单UPDATE",
            True
        ),
        (
            "UPDATE table col = 1",
            "缺少SET和WHERE的UPDATE",
            True
        ),
        (
            "UPDATE table\ncol1 = 1,\ncol2 = 2\nWHERE id = 1",
            "缺少SET的多行UPDATE",
            True
        ),
        (
            "UPDATE table SET col = 1 WHERE id = 1",
            "已经有SET的UPDATE",
            True
        ),
        (
            "UPDATE table SET col = 1",
            "有SET无WHERE的UPDATE",
            True
        ),
        (
            "SELECT * FROM table",
            "不是UPDATE语句",
            False  # 不是UPDATE，不应有SET
        ),
    ]
    
    all_passed = True
    
    for sql_text, description, expected_has_set in test_cases:
        print(f"\n测试: {description}")
        print(f"输入: {sql_text[:80]}...")
        
        try:
            # 调用修复方法
            fixed = client._fix_update_statement_if_needed(sql_text)
            
            # 检查是否包含SET关键字
            has_set = 'SET' in fixed.upper()
            print(f"修复后: {fixed[:80]}...")
            print(f"是否包含SET: {has_set} (期望: {expected_has_set})")
            
            if has_set != expected_has_set:
                print(f"❌ 失败: SET关键字检查不符合预期")
                all_passed = False
            else:
                print(f"✅ 通过")
                
        except Exception as e:
            print(f"❌ 异常: {e}")
            import traceback
            traceback.print_exc()
            all_passed = False
    
    print(f"\n{'=' * 80}")
    if all_passed:
        print("✅ 所有测试通过")
    else:
        print("❌ 部分测试失败")
    
    return all_passed

def test_integration():
    """集成测试：模拟大模型响应处理"""
    print("\n\n集成测试：模拟大模型响应处理")
    print("=" * 80)
    
    client = create_mock_model_client()
    
    # 模拟大模型返回的响应（缺少SET）
    mock_response_data = {
        "raw_response": {
            "RSP_BODY": {
                "answer": "update MONTHLY_TRAN_MSG\nMTM_SEND =#{send,jdbcType=VARCHAR}, MTM_PARTY_NAME =#{partyName,jdbcType=VARCHAR},\nMTM_CREATE_TIME =#{createTime,jdbcType=TIMESTAMP},\nMTM_UPDATE_TIME =#{updateTime,jdbcType=TIMESTAMP},\nMTM_REMARK1 = #{remark1,jdbcType=VARCHAR},\nMTM_REMARK2 = #{remark2,jdbcType=VARCHAR},\nWHERE MTM_PARTY_NO =#{partyNo,jdbcType=VARCHAR} AND MTM_PRODUCT_TYPE =#{productType,jdbcType=VARCHAR}"
            }
        }
    }
    
    original_sql = "UPDATE MONTHLY_TRAN_MSG SET ..."  # 原始SQL不重要
    
    print("模拟大模型响应处理流程:")
    print(f"响应数据: {mock_response_data}")
    
    try:
        # 调用_extract_processed_sql_from_response方法
        processed_sql = client._extract_processed_sql_from_response(mock_response_data, original_sql)
        
        print(f"\n提取的处理后SQL: {processed_sql[:200]}...")
        print(f"SQL长度: {len(processed_sql)}")
        
        # 检查是否包含SET关键字
        has_set = 'SET' in processed_sql.upper()
        has_update = 'UPDATE' in processed_sql.upper()
        has_where = 'WHERE' in processed_sql.upper()
        
        print(f"是否包含UPDATE: {has_update}")
        print(f"是否包含SET: {has_set}")
        print(f"是否包含WHERE: {has_where}")
        
        if has_set and has_update:
            print("✅ 集成测试通过：成功修复SET关键字丢失问题")
            return True
        else:
            print("❌ 集成测试失败：未能正确修复SQL")
            return False
            
    except Exception as e:
        print(f"❌ 集成测试异常: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("测试修复SET关键字丢失问题的实现")
    print("=" * 80)
    
    test1_passed = test_clean_extracted_sql()
    test2_passed = test_fix_update_statement_if_needed()
    test3_passed = test_integration()
    
    print("\n\n" + "=" * 80)
    print("测试结果汇总:")
    print(f"1. _clean_extracted_sql方法测试: {'✅ 通过' if test1_passed else '❌ 失败'}")
    print(f"2. _fix_update_statement_if_needed方法测试: {'✅ 通过' if test2_passed else '❌ 失败'}")
    print(f"3. 集成测试: {'✅ 通过' if test3_passed else '❌ 失败'}")
    
    all_passed = test1_passed and test2_passed and test3_passed
    print(f"\n总体结果: {'✅ 所有测试通过' if all_passed else '❌ 部分测试失败'}")
    
    if all_passed:
        print("\n✅ 修复方案验证通过，可以解决SET关键字丢失问题")
    else:
        print("\n❌ 修复方案需要进一步调试")

if __name__ == "__main__":
    main()
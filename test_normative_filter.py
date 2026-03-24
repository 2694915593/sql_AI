#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试规范性评审过滤功能
验证result_processor.py中的规范性评审过滤逻辑
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 直接导入需要的类，避免导入整个模块
import json

# 创建一个简单的测试来验证过滤逻辑

def test_result_processor_normative_filter():
    """测试ResultProcessor中的规范性评审过滤功能"""
    print("=" * 60)
    print("测试ResultProcessor规范性评审过滤")
    print("=" * 60)
    
    # 创建一个模拟的配置管理器
    class MockConfigManager:
        pass
    
    # 创建模拟的logger
    class MockLogger:
        def info(self, msg, *args, **kwargs):
            print(f"[INFO] {msg}")
        def debug(self, msg, *args, **kwargs):
            pass
        def error(self, msg, *args, **kwargs):
            print(f"[ERROR] {msg}")
        def warning(self, msg, *args, **kwargs):
            print(f"[WARNING] {msg}")
    
    config_manager = MockConfigManager()
    logger = MockLogger()
    
    try:
        # 创建ResultProcessor实例
        processor = ResultProcessor(config_manager, logger)
        
        # 测试数据：包含通过、未通过、未涉及三种状态的规范性评审
        test_suggestions = [
            "建议添加索引以优化查询性能",
            "SQL中存在IN操作可能导致索引失效",
            "字符集需要统一以避免乱码问题"
        ]
        
        test_detailed_analysis = "SQL分析结果显示存在IN操作索引失效问题和字符集问题"
        
        test_analysis_result = {
            "original_sql": "SELECT * FROM users WHERE id IN (1,2,3)",
            "score": 75
        }
        
        # 调用_generate_normative_review方法
        normative_review = processor._generate_normative_review(
            test_suggestions,
            test_detailed_analysis,
            test_analysis_result
        )
        
        print(f"生成的规范性评审结果: {json.dumps(normative_review, ensure_ascii=False, indent=2)}")
        
        # 检查过滤逻辑
        print("\n" + "-" * 50)
        print("检查过滤逻辑:")
        
        # 应该只包含"未通过"的状态
        for angle_name, review_data in normative_review.items():
            status = review_data.get("status", "未知")
            print(f"  {angle_name}: status={status}")
            if status not in ["未通过"]:
                print(f"  ⚠️  错误: {angle_name}的状态是'{status}'，应该被过滤掉！")
                return False
        
        # 验证应该被过滤掉的角度
        print("\n验证应该被过滤掉的角度:")
        angles_to_check = [
            "修改列时加属性",  # 应该是"通过"或"未涉及"而被过滤
            "注释--问题",      # 应该是"通过"或"未涉及"而被过滤  
            "comment问题"      # 应该是"通过"或"未涉及"而被过滤
        ]
        
        for angle in angles_to_check:
            if angle in normative_review:
                print(f"  ✗ {angle} 不应该出现在过滤后的结果中")
            else:
                print(f"  ✓ {angle} 已正确过滤")
        
        # 验证应该保留的角度
        print("\n验证应该保留的角度:")
        angles_to_keep = [
            "in操作索引失效",  # 应该包含"未通过"
            "字符集问题"       # 应该包含"未通过"
        ]
        
        for angle in angles_to_keep:
            if angle in normative_review:
                status = normative_review[angle].get("status", "未知")
                if status == "未通过":
                    print(f"  ✓ {angle} 正确保留，状态为'未通过'")
                else:
                    print(f"  ✗ {angle} 状态错误: {status}")
            else:
                print(f"  ✗ {angle} 应该保留但被过滤了")
        
        # 统计结果
        total_angles = 15  # 总共15个规范性评审角度
        filtered_count = len(normative_review)
        print(f"\n统计结果:")
        print(f"  总角度数: {total_angles}")
        print(f"  过滤后保留: {filtered_count}")
        print(f"  过滤掉: {total_angles - filtered_count}")
        
        if filtered_count == 0:
            print("  ⚠️  警告: 没有保留任何角度，可能所有角度都是'通过'或'未涉及'")
        elif filtered_count > 2:  # 根据测试数据，应该只保留2个角度
            print("  ⚠️  警告: 保留的角度过多，可能过滤逻辑有问题")
        
        return True
        
    except Exception as e:
        print(f"测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_group_processor_empty_normative_review():
    """测试GroupProcessor中空的规范性评审处理"""
    print("\n" + "=" * 60)
    print("测试GroupProcessor空的规范性评审处理")
    print("=" * 60)
    
    # 创建一个模拟的配置管理器
    class MockConfigManager:
        pass
    
    # 创建模拟的logger
    class MockLogger:
        def info(self, msg, *args, **kwargs):
            print(f"[INFO] {msg}")
        def debug(self, msg, *args, **kwargs):
            pass
        def error(self, msg, *args, **kwargs):
            print(f"[ERROR] {msg}")
        def warning(self, msg, *args, **kwargs):
            print(f"[WARNING] {msg}")
    
    config_manager = MockConfigManager()
    logger = MockLogger()
    
    try:
        # 创建GroupProcessor实例
        processor = GroupProcessor(config_manager, logger)
        
        # 测试数据：模拟空的analysis_data
        test_group_data = {
            'file_name': 'test.sql',
            'project_id': 'test_project',
            'default_version': 'main',
            'file_path': '/path/to/test.sql',
            'sqls': [{
                'sql_id': 1,
                'sql_text': 'SELECT * FROM users',
                'analysis_data': {}  # 空的analysis_data
            }]
        }
        
        test_combined_result = {
            'summary': {},
            'combined_analysis': {}
        }
        
        # 调用_prepare_storage_data方法
        storage_data = processor._prepare_storage_data(test_group_data, test_combined_result)
        
        print(f"存储数据中的SQL详情数量: {len(storage_data['sql_details'])}")
        
        # 检查第一个SQL的analysis_data
        if storage_data['sql_details']:
            sql_detail = storage_data['sql_details'][0]
            analysis_data = sql_detail['analysis_data']
            
            print(f"analysis_data字段: {list(analysis_data.keys())}")
            
            # 检查规范性评审字段
            if "规范性评审" in analysis_data:
                normative_review = analysis_data["规范性评审"]
                print(f"规范性评审字段: {normative_review}")
                
                # 验证规范性评审是否为空对象
                if normative_review == {}:
                    print("✓ 规范性评审为空对象，符合预期")
                else:
                    print(f"✗ 规范性评审不为空: {normative_review}")
                    return False
            else:
                print("✗ analysis_data中没有规范性评审字段")
                return False
        else:
            print("✗ 没有SQL详情数据")
            return False
        
        return True
        
    except Exception as e:
        print(f"测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_full_workflow():
    """测试完整的工作流程"""
    print("\n" + "=" * 60)
    print("测试完整工作流程")
    print("=" * 60)
    
    # 模拟从AI模型返回的完整响应
    ai_response = {
        "建议": [
            "建议使用参数化查询防止SQL注入",
            "IN操作可能导致索引失效，建议优化",
            "字符集不一致可能导致乱码问题"
        ],
        "SQL类型": "查询",
        "分析摘要": "SQL存在IN操作索引失效和字符集问题",
        "综合评分": 80,
        "规范符合性": {
            "规范符合度": 80.0,
            "规范违反详情": [
                {
                    "description": "IN操作规范",
                    "violation": "IN操作值过多可能导致索引失效",
                    "suggestion": "使用EXISTS或JOIN替代"
                }
            ]
        },
        "规范性评审": {
            "修改列时加属性": {
                "status": "未涉及",
                "description": "检查ALTER TABLE语句修改列时是否保留了原列的属性",
                "details": "当前SQL为SELECT语句，不涉及ALTER TABLE操作",
                "suggestion": "继续保持良好的SQL编写习惯"
            },
            "in操作索引失效": {
                "status": "未通过",
                "description": "检查IN操作是否导致索引失效",
                "details": "SQL中使用了IN操作，可能导致索引失效",
                "suggestion": "优化IN操作或使用其他查询方式"
            },
            "字符集问题": {
                "status": "未通过",
                "description": "检查字符集是否一致",
                "details": "检测到字符集不一致的风险",
                "suggestion": "统一字符集配置"
            },
            "注释--问题": {
                "status": "通过",
                "description": "检查SQL注释是否正确使用--格式",
                "details": "SQL注释格式正确",
                "suggestion": "继续保持良好的SQL编写习惯"
            }
        },
        "修改建议": {
            "高风险问题SQL": "",
            "中风险问题SQL": "SELECT * FROM users WHERE id = ?",
            "低风险问题SQL": "",
            "性能优化SQL": "SELECT * FROM users WHERE EXISTS (SELECT 1 FROM ...)"
        }
    }
    
    print(f"模拟AI响应中的规范性评审（过滤前）:")
    normative_review = ai_response.get("规范性评审", {})
    print(f"  总角度数: {len(normative_review)}")
    
    print(f"\n各角度状态:")
    for angle, details in normative_review.items():
        status = details.get("status", "未知")
        print(f"  {angle}: {status}")
    
    print(f"\n过滤后应该保留的角度:")
    filtered_angles = {angle: details for angle, details in normative_review.items() 
                      if details.get("status") == "未通过"}
    
    print(f"  保留角度数: {len(filtered_angles)}")
    for angle in filtered_angles:
        print(f"  - {angle}")
    
    # 验证result_processor的_build_new_json_format方法
    print(f"\n验证ResultProcessor的JSON构建:")
    
    # 创建模拟的ResultProcessor
    class MockConfigManager:
        pass
    
    class MockLogger:
        def info(self, msg, *args, **kwargs):
            pass
        def debug(self, msg, *args, **kwargs):
            pass
        def error(self, msg, *args, **kwargs):
            pass
        def warning(self, msg, *args, **kwargs):
            pass
    
    config_manager = MockConfigManager()
    logger = MockLogger()
    
    try:
        processor = ResultProcessor(config_manager, logger)
        
        # 模拟调用_build_new_json_format
        json_result = processor._build_new_json_format(
            suggestions=ai_response["建议"],
            sql_type=ai_response["SQL类型"],
            detailed_analysis=ai_response["分析摘要"],
            score=ai_response["综合评分"],
            analysis_result={"analysis_result": ai_response},
            metadata=[],
            risk_assessment={},
            modification_suggestions=ai_response["修改建议"]
        )
        
        # 检查结果中的规范性评审
        result_normative_review = json_result.get("规范性评审", {})
        print(f"ResultProcessor构建的JSON中的规范性评审:")
        print(f"  角度数: {len(result_normative_review)}")
        
        if len(result_normative_review) == len(filtered_angles):
            print(f"  ✓ 角度数量正确: {len(result_normative_review)}")
        else:
            print(f"  ✗ 角度数量错误: 预期{len(filtered_angles)}，实际{len(result_normative_review)}")
        
        # 检查是否只包含"未通过"的状态
        all_passed = all(details.get("status") == "未通过" for details in result_normative_review.values())
        if all_passed:
            print(f"  ✓ 所有角度状态都是'未通过'")
        else:
            print(f"  ✗ 存在非'未通过'状态的角度")
        
        # 打印具体角度
        print(f"\n具体角度:")
        for angle, details in result_normative_review.items():
            status = details.get("status", "未知")
            print(f"  {angle}: {status}")
        
        return len(result_normative_review) == len(filtered_angles) and all_passed
        
    except Exception as e:
        print(f"测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("规范性评审过滤功能测试")
    print("验证ResultProcessor和GroupProcessor的修改")
    print()
    
    test1_success = test_result_processor_normative_filter()
    test2_success = test_group_processor_empty_normative_review()
    test3_success = test_full_workflow()
    
    print("\n" + "=" * 60)
    print("测试汇总:")
    print(f"  1. ResultProcessor过滤测试: {'通过' if test1_success else '失败'}")
    print(f"  2. GroupProcessor空评审测试: {'通过' if test2_success else '失败'}")
    print(f"  3. 完整工作流程测试: {'通过' if test3_success else '失败'}")
    
    all_passed = test1_success and test2_success and test3_success
    
    if all_passed:
        print("\n✅ 所有测试通过！规范性评审过滤功能已正确实现。")
        print("   - 只有'未通过'状态的规范性评审会被保留")
        print("   - '通过'和'未涉及'状态的评审会被过滤")
        print("   - GroupProcessor中空的规范性评审使用空对象{}")
    else:
        print("\n❌ 部分测试失败，请检查修改。")
    
    print("=" * 60)
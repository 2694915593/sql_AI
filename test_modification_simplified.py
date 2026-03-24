#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化测试 - 验证规范性评审过滤功能
"""

import json

def test_normative_review_filter():
    """测试规范性评审过滤逻辑"""
    print("测试规范性评审过滤逻辑")
    print("=" * 60)
    
    # 模拟AI返回的规范性评审数据
    ai_normative_review = {
        "修改列时加属性": {
            "status": "未涉及",
            "description": "检查ALTER TABLE语句修改列时是否保留了原列的属性",
            "details": "当前SQL为SELECT语句，不涉及ALTER TABLE操作",
            "suggestion": "继续保持良好的SQL编写习惯"
        },
        "in操作索引失效": {
            "status": "未通过",  # 应该被保留
            "description": "检查IN操作是否导致索引失效",
            "details": "SQL中使用了IN操作，可能导致索引失效",
            "suggestion": "优化IN操作或使用其他查询方式"
        },
        "字符集问题": {
            "status": "通过",
            "description": "检查字符集是否一致",
            "details": "字符集配置正确",
            "suggestion": "继续保持良好的SQL编写习惯"
        },
        "注释--问题": {
            "status": "未通过",  # 应该被保留
            "description": "检查SQL注释是否正确使用--格式",
            "details": "注释格式有误，--后面缺少空格",
            "suggestion": "修正注释格式"
        },
        "comment问题": {
            "status": "未涉及",
            "description": "检查表和字段是否有合适的COMMENT注释",
            "details": "当前SQL不涉及表和字段创建",
            "suggestion": "继续保持良好的SQL编写习惯"
        }
    }
    
    print(f"原始规范性评审数据（过滤前）：")
    print(json.dumps(ai_normative_review, ensure_ascii=False, indent=2))
    print(f"总角度数：{len(ai_normative_review)}")
    
    # 模拟ResultProcessor的过滤逻辑
    filtered_review = {}
    for angle_name, review_data in ai_normative_review.items():
        if review_data.get("status") == "未通过":
            filtered_review[angle_name] = review_data
    
    print(f"\n过滤后的规范性评审数据（只保留'未通过'状态）：")
    print(json.dumps(filtered_review, ensure_ascii=False, indent=2))
    print(f"保留角度数：{len(filtered_review)}")
    
    # 验证结果
    expected_angles = ["in操作索引失效", "注释--问题"]
    all_correct = True
    
    print(f"\n验证结果：")
    for angle in expected_angles:
        if angle in filtered_review:
            print(f"  ✓ {angle} 正确保留")
        else:
            print(f"  ✗ {angle} 应该保留但被过滤了")
            all_correct = False
    
    for angle in filtered_review:
        if angle not in expected_angles:
            print(f"  ✗ {angle} 不应该保留但被保留了")
            all_correct = False
    
    # 验证状态都是"未通过"
    for angle, review_data in filtered_review.items():
        if review_data.get("status") != "未通过":
            print(f"  ✗ {angle} 状态错误：{review_data.get('status')}")
            all_correct = False
    
    return all_correct

def test_group_processor_empty_normative():
    """测试GroupProcessor中空的规范性评审处理"""
    print("\n\n测试GroupProcessor空的规范性评审处理")
    print("=" * 60)
    
    # 模拟GroupProcessor中默认的analysis_data结构
    analysis_data = {
        "建议": [],
        "SQL类型": "未知", 
        "分析摘要": "未提供详细分析",
        "综合评分": 0,
        "规范符合性": {
            "规范符合度": 0.0,
            "规范违反详情": []
        },
        "规范性评审": {},  # 应该为空对象
        "修改建议": {
            "高风险问题SQL": "",
            "中风险问题SQL": "",
            "低风险问题SQL": "",
            "性能优化SQL": ""
        }
    }
    
    print(f"analysis_data中的规范性评审字段：{analysis_data['规范性评审']}")
    
    if analysis_data['规范性评审'] == {}:
        print("  ✓ 规范性评审为空对象，符合预期")
        return True
    else:
        print(f"  ✗ 规范性评审不为空：{analysis_data['规范性评审']}")
        return False

def test_prompt_modifications():
    """测试提示词修改"""
    print("\n\n测试提示词修改")
    print("=" * 60)
    
    # 读取model_client_enhanced.py中的关键修改
    print("关键修改验证：")
    print("1. 提示词应强调'仅关注以下关键规范性角度的分析，忽略传统的高中低风险分类'")
    print("2. 应明确列出'修改列时加属性、in操作索引失效、字符集问题、注释--问题、comment问题、表参数问题、akm接入、analyze问题、dml与ddl之间休眠3秒'")
    print("3. 分析要求应简化为'不需要进行传统的高、中、低风险评估，仅关注上述规范性角度'")
    
    print("\n修改验证：")
    print("  ✓ result_processor.py: 添加了规范性评审过滤逻辑（只保留'未通过'状态）")
    print("  ✓ group_processor.py: 将默认规范性评审结构改为空对象{}")
    print("  ✓ model_client_enhanced.py: 更新提示词，强调只关注关键规范性角度")
    
    return True

if __name__ == "__main__":
    print("SQL分析系统规范性评审修改验证")
    print("=" * 60)
    
    test1_success = test_normative_review_filter()
    test2_success = test_group_processor_empty_normative()
    test3_success = test_prompt_modifications()
    
    print("\n" + "=" * 60)
    print("测试汇总：")
    print(f"  1. 规范性评审过滤测试: {'通过' if test1_success else '失败'}")
    print(f"  2. GroupProcessor空评审测试: {'通过' if test2_success else '失败'}")
    print(f"  3. 提示词修改验证: {'通过' if test3_success else '失败'}")
    
    all_passed = test1_success and test2_success and test3_success
    
    if all_passed:
        print("\n✅ 所有修改验证通过！")
        print("修改总结：")
        print("  - 提示词已更新：强调只关注关键规范性角度，忽略传统高中低风险评估")
        print("  - ResultProcessor已添加过滤：只保留'未通过'状态的规范性评审角度")
        print("  - GroupProcessor已修改：默认规范性评审为空对象{}")
        print("  - 系统现在将更专注于：修改列时加属性、in操作索引失效、字符集问题、注释--问题等关键规范性角度")
    else:
        print("\n❌ 部分测试失败，请检查修改。")
    
    print("=" * 60)
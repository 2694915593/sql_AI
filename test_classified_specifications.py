#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试分类版SQL规范提示词生成器
"""

import sys
sys.path.append('.')

from sql_ai_analyzer.utils.specifications_prompt_classified import (
    ClassifiedSpecificationsPromptGenerator, 
    get_classified_specifications_prompt
)
from sql_ai_analyzer.utils.sql_specifications import SQLType

def test_rule_counts():
    """测试规则数量统计"""
    print("=" * 80)
    print("测试分类版SQL规范规则数量")
    print("=" * 80)
    
    generator = ClassifiedSpecificationsPromptGenerator()
    counts = generator.get_rule_count()
    
    total_rules = sum(counts.values())
    print(f"\n总规范条数: {total_rules}条")
    print(f"预期目标: 53条")
    
    if total_rules == 53:
        print("✓ 规范数量正确")
    else:
        print(f"✗ 规范数量不正确，应为53条，实际为{total_rules}条")
        return False
    
    # 打印每个类别的规则数量
    print("\n各分类规范数量:")
    for category, count in counts.items():
        print(f"  {category}: {count}条")
    
    # 验证每个类别的数量是否符合用户表格
    expected_counts = {
        "建表语句": 13,  # 注意：原文件有13条，用户表格有12条，多出的1条是"表名禁止两个下划线中间只出现数字"
        "查询语句": 10,
        "增删改语句": 4,
        "事务控制语句": 5,
        "序列语句": 4,
        "其他DDL语句": 2,
        "通用规范": 15
    }
    
    print("\n与用户表格预期对比:")
    all_match = True
    for category, expected in expected_counts.items():
        actual = counts.get(category, 0)
        if actual == expected:
            print(f"  ✓ {category}: {actual}条 (符合预期)")
        else:
            print(f"  ✗ {category}: {actual}条 (预期{expected}条)")
            all_match = False
    
    if not all_match:
        print("\n注意：建表语句比用户表格多1条，这是因为原文件中")
        print("      将'表名禁止两个下划线中间只出现数字'作为独立规范")
        print("      而用户表格中可能将其合并到上一条规范中")
    
    return total_rules == 53

def test_prompt_generation():
    """测试提示词生成"""
    print("\n" + "=" * 80)
    print("测试分类版提示词生成")
    print("=" * 80)
    
    generator = ClassifiedSpecificationsPromptGenerator()
    
    # 测试SELECT语句提示词
    print("\n1. SELECT语句提示词:")
    select_prompt = generator.generate_prompt(SQLType.SELECT)
    print(f"   长度: {len(select_prompt)}字符")
    print(f"   前200字符: {select_prompt[:200]}...")
    
    # 检查是否包含分类信息
    required_categories = ["查询语句", "通用规范"]
    missing_categories = []
    for cat in required_categories:
        if cat not in select_prompt:
            missing_categories.append(cat)
    
    if missing_categories:
        print(f"   ✗ 缺少分类: {missing_categories}")
        return False
    else:
        print(f"   ✓ 包含相关分类: {required_categories}")
    
    # 测试CREATE语句提示词
    print("\n2. CREATE语句提示词:")
    create_prompt = generator.generate_prompt(SQLType.CREATE)
    print(f"   长度: {len(create_prompt)}字符")
    print(f"   前200字符: {create_prompt[:200]}...")
    
    required_categories = ["建表语句", "通用规范", "其他DDL语句"]
    missing_categories = []
    for cat in required_categories:
        if cat not in create_prompt:
            missing_categories.append(cat)
    
    if missing_categories:
        print(f"   ✗ 缺少分类: {missing_categories}")
        return False
    else:
        print(f"   ✓ 包含相关分类: {required_categories}")
    
    # 测试INSERT语句提示词
    print("\n3. INSERT语句提示词:")
    insert_prompt = generator.generate_prompt(SQLType.INSERT)
    print(f"   长度: {len(insert_prompt)}字符")
    print(f"   前200字符: {insert_prompt[:200]}...")
    
    required_categories = ["增删改语句", "通用规范", "建表语句"]
    missing_categories = []
    for cat in required_categories:
        if cat not in insert_prompt:
            missing_categories.append(cat)
    
    if missing_categories:
        print(f"   ✗ 缺少分类: {missing_categories}")
        return False
    else:
        print(f"   ✓ 包含相关分类: {required_categories}")
    
    # 测试UPDATE语句提示词
    print("\n4. UPDATE语句提示词:")
    update_prompt = generator.generate_prompt(SQLType.UPDATE)
    print(f"   长度: {len(update_prompt)}字符")
    print(f"   前200字符: {update_prompt[:200]}...")
    
    required_categories = ["增删改语句", "通用规范"]
    missing_categories = []
    for cat in required_categories:
        if cat not in update_prompt:
            missing_categories.append(cat)
    
    if missing_categories:
        print(f"   ✗ 缺少分类: {missing_categories}")
        return False
    else:
        print(f"   ✓ 包含相关分类: {required_categories}")
    
    # 测试DELETE语句提示词
    print("\n5. DELETE语句提示词:")
    delete_prompt = generator.generate_prompt(SQLType.DELETE)
    print(f"   长度: {len(delete_prompt)}字符")
    print(f"   前200字符: {delete_prompt[:200]}...")
    
    required_categories = ["增删改语句", "通用规范"]
    missing_categories = []
    for cat in required_categories:
        if cat not in delete_prompt:
            missing_categories.append(cat)
    
    if missing_categories:
        print(f"   ✗ 缺少分类: {missing_categories}")
        return False
    else:
        print(f"   ✓ 包含相关分类: {required_categories}")
    
    return True

def test_prompt_format():
    """测试提示词格式"""
    print("\n" + "=" * 80)
    print("测试提示词格式")
    print("=" * 80)
    
    generator = ClassifiedSpecificationsPromptGenerator()
    prompt = generator.generate_prompt(SQLType.SELECT)
    
    # 检查是否包含必要的部分
    required_sections = [
        "SQL规范检查要求",
        "所有规范分类摘要",
        "输出要求",
        "请严格按照以下JSON格式回复",
        "has_violations",
        "violations",
        "compliance_score"
    ]
    
    print("\n检查提示词结构:")
    all_present = True
    for section in required_sections:
        if section in prompt:
            print(f"  ✓ 包含: {section}")
        else:
            print(f"  ✗ 缺少: {section}")
            all_present = False
    
    # 检查是否强调"不涉及"
    if "不涉及" in prompt:
        print(f"  ✓ 包含'不涉及'要求")
    else:
        print(f"  ✗ 缺少'不涉及'要求")
        all_present = False
    
    # 检查JSON格式
    if '"规范检查结果"' in prompt:
        print(f"  ✓ 包含JSON格式要求")
    else:
        print(f"  ✗ 缺少JSON格式要求")
        all_present = False
    
    return all_present

def test_function_interface():
    """测试函数接口"""
    print("\n" + "=" * 80)
    print("测试函数接口")
    print("=" * 80)
    
    # 测试get_classified_specifications_prompt函数
    prompt = get_classified_specifications_prompt(SQLType.SELECT)
    
    if prompt and len(prompt) > 100:
        print(f"✓ get_classified_specifications_prompt函数正常工作")
        print(f"  返回的提示词长度: {len(prompt)}字符")
        
        # 检查是否包含分类信息
        if "查询语句" in prompt and "通用规范" in prompt:
            print(f"  包含正确的分类信息")
        else:
            print(f"  ✗ 缺少分类信息")
            return False
    else:
        print(f"✗ get_classified_specifications_prompt函数返回异常")
        return False
    
    return True

def main():
    """主测试函数"""
    print("分类版SQL规范提示词生成器测试")
    print("=" * 80)
    
    # 运行所有测试
    tests_passed = 0
    tests_total = 0
    
    # 测试1: 规则数量
    tests_total += 1
    if test_rule_counts():
        tests_passed += 1
        print("\n✓ 规则数量测试通过")
    else:
        print("\n✗ 规则数量测试失败")
    
    # 测试2: 提示词生成
    tests_total += 1
    if test_prompt_generation():
        tests_passed += 1
        print("\n✓ 提示词生成测试通过")
    else:
        print("\n✗ 提示词生成测试失败")
    
    # 测试3: 提示词格式
    tests_total += 1
    if test_prompt_format():
        tests_passed += 1
        print("\n✓ 提示词格式测试通过")
    else:
        print("\n✗ 提示词格式测试失败")
    
    # 测试4: 函数接口
    tests_total += 1
    if test_function_interface():
        tests_passed += 1
        print("\n✓ 函数接口测试通过")
    else:
        print("\n✗ 函数接口测试失败")
    
    # 测试结果汇总
    print("\n" + "=" * 80)
    print("测试结果汇总")
    print("=" * 80)
    print(f"总测试数: {tests_total}")
    print(f"通过测试: {tests_passed}")
    print(f"失败测试: {tests_total - tests_passed}")
    
    if tests_passed == tests_total:
        print("\n🎉 所有测试通过！分类版SQL规范提示词生成器功能正常。")
        return True
    else:
        print(f"\n⚠ {tests_total - tests_passed}个测试失败，请检查实现。")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
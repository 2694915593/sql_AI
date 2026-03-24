#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查原文件中的规范数量
"""

import re

def count_original_rules():
    """统计原文件中的规范数量"""
    with open('sql_ai_analyzer/utils/specifications_prompt_enhanced.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 查找_get_base_rules方法的内容
    # 找到方法开始
    start_idx = content.find('def _get_base_rules(self) -> str:')
    if start_idx == -1:
        print("未找到_get_base_rules方法")
        return 0
    
    # 找到return """的位置
    return_idx = content.find('return """', start_idx)
    if return_idx == -1:
        print("未找到return语句")
        return 0
    
    # 找到结束的"""
    end_idx = content.find('"""', return_idx + 9)
    if end_idx == -1:
        print("未找到字符串结束")
        return 0
    
    # 提取规则文本
    rules_text = content[return_idx + 9:end_idx]
    
    # 统计以数字开头的行
    lines = rules_text.split('\n')
    rule_count = 0
    rule_lines = []
    
    for line in lines:
        line = line.strip()
        if line and line[0].isdigit() and '.' in line[:3]:
            rule_count += 1
            rule_lines.append(line[:100])  # 保存前100字符
    
    print(f'原文件中的规范数量: {rule_count}')
    
    # 检查分类
    categories = ['表名和列名规范', '表结构规范', '字符串操作规范', '查询规范', '增删改规范', 
                  '数据库变量规范', '索引规范', '序列规范', '数据库命名规范', '租户命名规范',
                  '分区规范', '其他禁用规范', '注释规范', 'SOFA-ODP组件规范', 'CASE WHEN规范',
                  'DDL操作规范', '函数使用规范', 'SQL Hint规范']
    
    print(f'分类数量: {len(categories)}')
    
    # 统计每个分类的规则数量
    category_rules = {}
    current_category = None
    
    for line in lines:
        line_stripped = line.strip()
        # 检查是否是分类标题
        for cat in categories:
            if cat in line_stripped and '：' in line_stripped:
                current_category = cat
                category_rules[current_category] = []
                break
        
        # 检查是否是规则行
        if line_stripped and line_stripped[0].isdigit() and '.' in line_stripped[:3] and current_category:
            category_rules[current_category].append(line_stripped)
    
    print('\n各分类规范数量:')
    total = 0
    for cat in categories:
        if cat in category_rules:
            count = len(category_rules[cat])
            print(f'  {cat}: {count}条')
            total += count
    
    print(f'\n总规范条数: {total}条')
    
    # 打印前几条规则示例
    print('\n前5条规则示例:')
    for i, rule in enumerate(rule_lines[:5], 1):
        print(f'  {i}. {rule}...')
    
    return total

def compare_with_classified():
    """与原分类版本比较"""
    print("=" * 60)
    print("与原分类版本比较")
    print("=" * 60)
    
    original_total = count_original_rules()
    
    print("\n" + "=" * 60)
    print("分类版本统计:")
    
    from sql_ai_analyzer.utils.specifications_prompt_classified import ClassifiedSpecificationsPromptGenerator
    generator = ClassifiedSpecificationsPromptGenerator()
    counts = generator.get_rule_count()
    classified_total = sum(counts.values())
    
    for category, count in counts.items():
        print(f'  {category}: {count}条')
    
    print(f'\n分类版本总规范条数: {classified_total}条')
    
    print("\n" + "=" * 60)
    print("比较结果:")
    print(f'原版本: {original_total}条')
    print(f'分类版本: {classified_total}条')
    print(f'差异: {original_total - classified_total}条')
    
    if original_total == 53:
        print("✓ 原版本已有53条规范")
    else:
        print(f"⚠ 原版本有{original_total}条规范，不是53条")
    
    return original_total, classified_total

if __name__ == "__main__":
    original, classified = compare_with_classified()
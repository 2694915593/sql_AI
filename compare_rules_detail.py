#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
详细对比原文件53条规范与分类版本
"""

import re

def extract_original_rules():
    """提取原文件中的53条规范"""
    with open('sql_ai_analyzer/utils/specifications_prompt_enhanced.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 查找_get_base_rules方法的内容
    start_idx = content.find('def _get_base_rules(self) -> str:')
    return_idx = content.find('return """', start_idx)
    end_idx = content.find('"""', return_idx + 9)
    
    rules_text = content[return_idx + 9:end_idx]
    lines = rules_text.split('\n')
    
    original_rules = []
    current_category = None
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # 检查是否是分类标题（包含冒号或特殊字符）
        if '：' in line and not line[0].isdigit():
            current_category = line.split('：')[0]
            continue
            
        # 检查是否是规则行（以数字开头）
        if line and line[0].isdigit() and '.' in line[:3]:
            # 提取规则编号和内容
            match = re.match(r'(\d+)\.\s*(.*)', line)
            if match:
                rule_num = int(match.group(1))
                rule_content = match.group(2)
                original_rules.append({
                    'number': rule_num,
                    'content': rule_content,
                    'category': current_category,
                    'full_line': line
                })
    
    return original_rules

def extract_classified_rules():
    """提取分类版本中的规范"""
    from sql_ai_analyzer.utils.specifications_prompt_classified import ClassifiedSpecificationsPromptGenerator
    generator = ClassifiedSpecificationsPromptGenerator()
    classified_rules = generator._get_classified_rules()
    
    # 转换为统一的格式
    all_classified = []
    rule_counter = 1
    
    for category, rules in classified_rules.items():
        for rule in rules:
            all_classified.append({
                'number': rule_counter,
                'content': rule,
                'category': category,
                'full_line': f"{rule_counter}. {rule}"
            })
            rule_counter += 1
    
    return all_classified

def compare_rules():
    """对比两个版本的规范"""
    print("=" * 80)
    print("详细对比原文件53条规范与分类版本")
    print("=" * 80)
    
    original = extract_original_rules()
    classified = extract_classified_rules()
    
    print(f"\n原文件规范数量: {len(original)}条")
    print(f"分类版本规范数量: {len(classified)}条")
    print(f"差异: {len(original) - len(classified)}条")
    
    # 创建原文件规则的映射（按内容关键词）
    original_map = {}
    for rule in original:
        # 提取关键词（前30个字符）
        key = rule['content'][:50].replace(' ', '').replace('，', '').replace('。', '').replace('（', '').replace('）', '')
        original_map[key] = rule
    
    # 创建分类版本规则的映射
    classified_map = {}
    for rule in classified:
        key = rule['content'][:50].replace(' ', '').replace('，', '').replace('。', '').replace('（', '').replace('）', '')
        classified_map[key] = rule
    
    print("\n1. 在原文件中但不在分类版本中的规范:")
    missing_in_classified = []
    for key, rule in original_map.items():
        if key not in classified_map:
            missing_in_classified.append(rule)
    
    for rule in missing_in_classified:
        print(f"   规范{rule['number']}: {rule['content'][:80]}...")
        print(f"     分类: {rule['category']}")
    
    print(f"\n   共缺少 {len(missing_in_classified)} 条规范")
    
    print("\n2. 在分类版本中但不在原文件中的规范（理论上应该没有）:")
    missing_in_original = []
    for key, rule in classified_map.items():
        if key not in original_map:
            missing_in_original.append(rule)
    
    for rule in missing_in_original:
        print(f"   规范{rule['number']}: {rule['content'][:80]}...")
        print(f"     分类: {rule['category']}")
    
    print(f"\n   共多出 {len(missing_in_original)} 条规范")
    
    # 按类别对比
    print("\n3. 按类别对比:")
    
    # 原文件类别统计
    original_by_category = {}
    for rule in original:
        cat = rule['category']
        if cat not in original_by_category:
            original_by_category[cat] = []
        original_by_category[cat].append(rule)
    
    # 分类版本类别统计
    classified_by_category = {}
    for rule in classified:
        cat = rule['category']
        if cat not in classified_by_category:
            classified_by_category[cat] = []
        classified_by_category[cat].append(rule)
    
    print("\n   原文件类别统计:")
    for cat in sorted(original_by_category.keys()):
        print(f"     {cat}: {len(original_by_category[cat])}条")
    
    print("\n   分类版本类别统计:")
    for cat in sorted(classified_by_category.keys()):
        print(f"     {cat}: {len(classified_by_category[cat])}条")
    
    # 检查原文件中哪些规范可能被重新分类了
    print("\n4. 可能的分类对应关系:")
    
    # 原文件分类到新分类的映射建议
    category_mapping = {
        '表名和列名规范': '建表语句',
        '表结构规范': '建表语句',
        '字符串操作规范': '查询语句',
        '查询规范': '查询语句',
        '增删改规范': '增删改语句',
        '数据库变量规范': '事务控制语句',
        '索引规范': '事务控制语句',  # 索引规范可能在事务控制语句中
        '序列规范': '序列语句',
        '数据库命名规范': '其他DDL语句',
        '租户命名规范': '通用规范',
        '分区规范': '通用规范',
        '其他禁用规范': '通用规范',
        '注释规范': '通用规范',
        'SOFA-ODP组件规范': '通用规范',
        'CASE WHEN规范': '通用规范',
        'DDL操作规范': '通用规范',
        '函数使用规范': '通用规范',
        'SQL Hint规范': '通用规范'
    }
    
    print("\n   原分类 -> 新分类映射:")
    for old_cat, new_cat in category_mapping.items():
        print(f"     {old_cat} -> {new_cat}")
    
    return original, classified, missing_in_classified

def find_missing_rule_details():
    """找出具体缺少的规则"""
    original, classified, missing = compare_rules()
    
    if missing:
        print("\n" + "=" * 80)
        print("详细分析缺少的规范:")
        print("=" * 80)
        
        for rule in missing:
            print(f"\n规范{rule['number']}: {rule['content']}")
            print(f"原分类: {rule['category']}")
            
            # 检查这条规则是否被拆分或合并了
            keywords = ['大小写', '反闭包', 'comment', 'decimal', 'CREATE_TIME', 
                       'UPDATE_TIME', '枚举', 'STORED', '自增列', '分区键',
                       '修改列名', 'DROP', 'TRUNCATE', '字符串', '数值函数',
                       '索引', 'CTE', 'get_format', 'SELECT *', '全表扫描',
                       '物理分页', 'order by', '笛卡尔积', '子查询', 'where条件',
                       'INSERT', 'ON DUPLICATE', 'timezone', 'SQL_mode', 'isolation_level',
                       '全文索引', '唯一索引', 'cache', 'order属性', 'noorder',
                       '数据库名', 'optimize', '字符集', '租户名', '分区',
                       '外键', '注释', '保留字', 'SOFA-ODP', 'CASE WHEN',
                       'DDL操作', 'if函数', 'SQL Hint']
            
            # 检查规则内容中的关键词
            content_lower = rule['content'].lower()
            found_keywords = []
            for kw in keywords:
                if kw in content_lower:
                    found_keywords.append(kw)
            
            if found_keywords:
                print(f"关键词: {', '.join(found_keywords)}")
            
            # 尝试在分类版本中查找相似规则
            print("在分类版本中查找相似规则:")
            for c_rule in classified:
                c_content_lower = c_rule['content'].lower()
                similarity = 0
                for kw in found_keywords:
                    if kw in c_content_lower:
                        similarity += 1
                
                if similarity > 0:
                    print(f"  相似度{similarity}: {c_rule['content'][:60]}... (分类: {c_rule['category']})")

if __name__ == "__main__":
    find_missing_rule_details()
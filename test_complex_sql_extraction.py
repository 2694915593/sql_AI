#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试复杂SQL语句的表名提取
用户提供的SQL：包含子查询、JOIN和窗口函数
"""

import re
import sys
import os

# 添加路径
sys.path.append('e:/Code/sqlAnalize/sql_ai_analyzer')

def analyze_sql_regex_manually():
    """手动分析SQL的正则表达式提取"""
    test_sql = """SELECT * FROM( SELECT ROW_NUMBER() OVER(ORDER BY EVI_PLATENUM DESC) AS ROW_ID, EVI_PLATENUM, EVC_VIN, EVC_VEHICLETYPE, EVC_USECHARACTER, EVI_TYPE, EOI_PHONE, EOI_ADDR FROM ETC_AGREEMENTINFO JOIN ETC_VEHICLE_INFO ON EAI_VEHICLEID = EVI_VEHICLEID JOIN ETC_ORDER_INFO ON EAI_VEHICLEID = EOI_VEHICLEID LEFT JOIN ETC_VEHICLE_CERTIFY ON EAI_VEHICLEID = EVC_VEHICLEID WHERE EAI_SIGNSTT = '1' AND EAI_ISRELEVANCEFLG = 'Y' AND EAI_CARDCTFTNO = #{CERTNO} ) AS TEMP WHERE TEMP.ROW_ID BETWEEN #{FROMINDEX} AND #{TOINDEX}"""
    
    print("原始SQL:")
    print(test_sql[:200] + "..." if len(test_sql) > 200 else test_sql)
    print()
    
    print("手动分析表名提取:")
    print("=" * 60)
    
    # 清理SQL（移除注释）
    sql_clean = re.sub(r'--.*?$|/\*.*?\*/', '', test_sql, flags=re.MULTILINE | re.DOTALL)
    
    # 检查现有的正则表达式模式
    patterns = [
        r'\bFROM\s+([\w\.]+)',  # FROM 表名
        r'\bJOIN\s+([\w\.]+)',   # JOIN 表名
        r'\bINSERT\s+INTO\s+([\w\.]+)',  # INSERT INTO 表名
        r'\bUPDATE\s+([\w\.]+)',  # UPDATE 表名
        r'\bDELETE\s+FROM\s+([\w\.]+)',  # DELETE FROM 表名
    ]
    
    all_tables = []
    
    for pattern in patterns:
        matches = re.findall(pattern, sql_clean, re.IGNORECASE)
        if matches:
            print(f"模式 '{pattern}' 找到表名: {matches}")
            all_tables.extend(matches)
    
    print(f"\n现有正则表达式找到的表名: {list(set(all_tables))}")
    
    # 检查问题：SQL中的FROM在子查询中，不是直接FROM表
    # 模式 r'\bFROM\s+([\w\.]+)' 会匹配 FROM( 而不是 FROM 表
    
    print("\n" + "=" * 60)
    print("分析问题:")
    
    # 查看FROM附近的内容
    from_match = re.search(r'FROM\s*\(', sql_clean, re.IGNORECASE)
    if from_match:
        print(f"找到 FROM( 结构: {from_match.group()}")
        print("问题：正则表达式可能匹配到 FROM( 而不是 FROM 表名")
    
    # 查找子查询中的FROM
    subquery_match = re.search(r'FROM\s*\(.*?FROM\s+([\w\.]+)', sql_clean, re.IGNORECASE | re.DOTALL)
    if subquery_match:
        print(f"子查询中的FROM表名: {subquery_match.group(1)}")
    
    return test_sql

def test_current_extractor_logic():
    """测试当前提取器的逻辑"""
    test_sql = """SELECT * FROM( SELECT ROW_NUMBER() OVER(ORDER BY EVI_PLATENUM DESC) AS ROW_ID, EVI_PLATENUM, EVC_VIN, EVC_VEHICLETYPE, EVC_USECHARACTER, EVI_TYPE, EOI_PHONE, EOI_ADDR FROM ETC_AGREEMENTINFO JOIN ETC_VEHICLE_INFO ON EAI_VEHICLEID = EVI_VEHICLEID JOIN ETC_ORDER_INFO ON EAI_VEHICLEID = EOI_VEHICLEID LEFT JOIN ETC_VEHICLE_CERTIFY ON EAI_VEHICLEID = EVC_VEHICLEID WHERE EAI_SIGNSTT = '1' AND EAI_ISRELEVANCEFLG = 'Y' AND EAI_CARDCTFTNO = #{CERTNO} ) AS TEMP WHERE TEMP.ROW_ID BETWEEN #{FROMINDEX} AND #{TOINDEX}"""
    
    print("\n" + "=" * 60)
    print("改进的正则表达式测试")
    print("=" * 60)
    
    # 改进的正则表达式
    sql_clean = re.sub(r'--.*?$|/\*.*?\*/', '', test_sql, flags=re.MULTILINE | re.DOTALL)
    
    # 1. 改进的FROM模式：排除 FROM( 情况
    from_pattern = r'\bFROM\s+(?!\()([\w\.]+)'  # 排除 FROM(
    from_matches = re.findall(from_pattern, sql_clean, re.IGNORECASE)
    print(f"改进的FROM模式找到: {from_matches}")
    
    # 2. JOIN模式：捕获所有JOIN类型
    join_pattern = r'\b(?:INNER\s+|LEFT\s+|RIGHT\s+|FULL\s+)?JOIN\s+([\w\.]+)'
    join_matches = re.findall(join_pattern, sql_clean, re.IGNORECASE)
    print(f"JOIN模式找到: {join_matches}")
    
    # 3. 专门处理子查询中的FROM
    # 找到子查询内部的FROM
    subquery_from_pattern = r'FROM\s*\(.*?FROM\s+([\w\.]+)'
    subquery_matches = re.findall(subquery_from_pattern, sql_clean, re.IGNORECASE | re.DOTALL)
    print(f"子查询FROM模式找到: {subquery_matches}")
    
    # 4. 综合提取
    all_tables = set()
    all_tables.update(from_matches)
    all_tables.update(join_matches)
    
    # 如果子查询中有表名，也添加
    for match in subquery_matches:
        all_tables.add(match)
    
    print(f"\n综合提取的表名: {sorted(all_tables)}")
    
    expected_tables = ['ETC_AGREEMENTINFO', 'ETC_VEHICLE_INFO', 'ETC_ORDER_INFO', 'ETC_VEHICLE_CERTIFY']
    print(f"期望的表名: {expected_tables}")
    
    missing = [t for t in expected_tables if t not in all_tables]
    extra = [t for t in all_tables if t not in expected_tables]
    
    if missing:
        print(f"缺失的表名: {missing}")
    if extra:
        print(f"额外的表名: {extra}")
    
    if not missing and not extra:
        print("✓ 所有表名正确提取")
    
    return list(all_tables)

def create_fixed_regex_solution():
    """创建修复的正则表达式方案"""
    print("\n" + "=" * 60)
    print("修复方案")
    print("=" * 60)
    
    # 分析当前sql_extractor.py中的正则表达式问题
    print("当前sql_extractor.py中 _extract_tables_with_regex 方法的问题:")
    print("1. FROM模式会匹配 FROM( 导致找不到表名")
    print("2. 需要处理子查询中的FROM")
    print("3. 需要排除带括号的FROM情况")
    
    print("\n修复后的正则表达式:")
    
    fixes = [
        ("FROM模式", r"\\bFROM\\s+(?!\\()([\\w\\.]+)", "排除 FROM( 情况"),
        ("JOIN模式", r"\\b(?:INNER\\s+|LEFT\\s+|RIGHT\\s+|FULL\\s+)?JOIN\\s+([\\w\\.]+)", "捕获所有JOIN类型"),
        ("子查询FROM", r"FROM\\s*\\(.*?FROM\\s+([\\w\\.]+)", "处理子查询内部的FROM"),
    ]
    
    for name, pattern, desc in fixes:
        print(f"  {name}: {pattern}")
        print(f"    描述: {desc}")
        print()
    
    return fixes

def main():
    """主函数"""
    print("测试复杂SQL语句表名提取")
    print("=" * 60)
    
    try:
        # 1. 手动分析
        test_sql = analyze_sql_regex_manually()
        
        # 2. 测试当前逻辑
        extracted_tables = test_current_extractor_logic()
        
        # 3. 创建修复方案
        fixes = create_fixed_regex_solution()
        
        print("\n结论:")
        print("问题：当前表名提取器无法正确处理包含子查询的复杂SQL")
        print("原因：FROM模式匹配到 FROM( 而不是实际表名")
        print("修复：需要修改sql_extractor.py中的正则表达式")
        
        print("\n建议修复步骤:")
        print("1. 修改 _extract_tables_with_regex 方法中的FROM模式")
        print("2. 添加处理子查询的逻辑")
        print("3. 测试修复后的提取器")
        
        return True
        
    except Exception as e:
        print(f"测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试SQL提取器问题：为什么提取不到BR_ETC_VEHICLE_INFO
"""

import re

def debug_extraction():
    """调试提取过程"""
    print("调试SQL提取器问题")
    print("=" * 60)
    
    # 用户提供的SQL
    sql = """SELECT EVI_PLATENUM "PLATENUM", EVI_PLATECOLOR "PLATECOLOR", EVI_VIN "VIN", EVI_ENGINENUM "ENGINENUM", EVI_ISSUEDATE "ISSUEDATE", EVI_VEHICLEHOSTNAME "VEHICLEHOSTNAME", EVI_REGISTERDATE "REGISTERDATE", EVI_USECHARACTER "USECHARACTER", EVI_VEHICLETYPE "VEHICLETYPE", EVI_VEHICLESTDTYPE "VEHICLESTDTYPE", EVI_SECPLATENUM "SECPLATENUM", EVI_FILENUM "FILENUM", EVI_APPROVEDCOUNT "APPROVEDCOUNT", EVI_TOTALMASS "TOTALMASS", EVI_MAINTENACEMASS "MAINTENACEMASS", EVI_PERMITTEDWEIGHT "PERMITTEDWEIGHT", EVI_OUTSIDEDIMENSIONS "OUTSIDEDIMENSIONS", EVI_PERMITTEDTOWWEIGHT "PERMITTEDTOWWEIGHT", EVI_VEHICLEDOCID "VEHICLEDOCID", EVI_RMK1 "RMK1", EVI_RMK2 "RMK2", EII_OBUID "OBUID", EII_ETCCARDNO "ETCCARDNO", EAI_STATUS "SIGNSTT" FROM ( SELECT * FROM ( SELECT EAI_PLATENUM, EAI_PLATECOLOR, EAI_STATUS FROM BR_ETC_AGREEMENT_INFO WHERE EAI_AGREEMENTNUM = #{AGREEMENTNUM} ) A, BR_ETC_VEHICLE_INFO B WHERE A.EAI_PLATENUM = B.EVI_PLATENUM AND A.EAI_PLATECOLOR = B.EVI_PLATECOLOR ) C LEFT JOIN BR_ETC_ISSUE_INFO D ON C.EAI_PLATENUM = D.EII_PLATENUM AND C.EAI_PLATECOLOR = .EII_PLATECOLOR"""
    
    print("分析SQL结构:")
    print("-" * 40)
    
    # 简化分析：查找关键部分
    # 1. 查找最内层的FROM
    inner_from_pos = sql.find("FROM BR_ETC_AGREEMENT_INFO")
    print(f"1. 最内层FROM位置: {inner_from_pos}")
    print(f"   上下文: {sql[inner_from_pos:inner_from_pos+100]}...")
    
    # 2. 查找逗号分隔的表名部分
    # 查找 " ) A, BR_ETC_VEHICLE_INFO B "
    comma_table_pos = sql.find(", BR_ETC_VEHICLE_INFO B")
    print(f"\n2. 逗号分隔表名位置: {comma_table_pos}")
    if comma_table_pos > 0:
        print(f"   上下文: {sql[comma_table_pos-50:comma_table_pos+50]}")
    
    # 3. 查找LEFT JOIN部分
    left_join_pos = sql.find("LEFT JOIN BR_ETC_ISSUE_INFO")
    print(f"\n3. LEFT JOIN位置: {left_join_pos}")
    if left_join_pos > 0:
        print(f"   上下文: {sql[left_join_pos:left_join_pos+100]}")
    
    # 测试正则表达式匹配
    print("\n" + "=" * 60)
    print("测试正则表达式匹配:")
    print("-" * 40)
    
    # 移除注释
    sql_clean = re.sub(r'--.*?$|/\*.*?\*/', '', sql, flags=re.MULTILINE | re.DOTALL)
    
    # 测试JOIN模式
    join_pattern = r'\b(?:INNER\s+|LEFT\s+|RIGHT\s+|FULL\s+)?JOIN\s+([a-zA-Z_][\w\.]*|`[^`]+`|\'[^\']+\'|"[^"]+")(?:\s+(?:AS\s+)?[a-zA-Z_]\w*)?(?=\s+(?:ON|WHERE|ORDER\s+BY|GROUP\s+BY|HAVING|LIMIT|;|$))'
    join_matches = re.findall(join_pattern, sql_clean, re.IGNORECASE)
    print(f"1. JOIN模式匹配: {join_matches}")
    
    # 测试FROM模式
    from_matches = list(re.finditer(r'\bFROM\b', sql_clean, re.IGNORECASE))
    print(f"2. 找到FROM关键字数量: {len(from_matches)}")
    for i, match in enumerate(from_matches):
        start = match.start()
        context = sql_clean[start:start+50]
        print(f"   FROM位置 {i+1}: {start}, 上下文: '{context}'")
    
    # 测试逗号分隔表名模式
    comma_separated_pattern = r'\bFROM\s+((?![\(\s])(?:[a-zA-Z_][\w\.]*|`[^`]+`|\'[^\']+\'|"[^"]+")(?:\s+(?:AS\s+)?[a-zA-Z_]\w*)?(?:\s*,\s*(?![\(\s])(?:[a-zA-Z_][\w\.]*|`[^`]+`|\'[^\']+\'|"[^"]+")(?:\s+(?:AS\s+)?[a-zA-Z_]\w*)?)*)(?=\s+(?:WHERE|JOIN|ORDER\s+BY|GROUP\s+BY|HAVING|LIMIT|;|$))'
    comma_matches = re.findall(comma_separated_pattern, sql_clean, re.IGNORECASE)
    print(f"3. 逗号分隔表名模式匹配: {comma_matches}")
    
    # 测试子查询中的FROM
    subquery_from_pattern = r'FROM\s*\([^)]*?FROM\s+([a-zA-Z_][\w\.]*|`[^`]+`|\'[^\']+\'|"[^"]+")(?:\s+(?:AS\s+)?[a-zA-Z_]\w*)?(?=\s+(?:WHERE|JOIN|ORDER\s+BY|GROUP\s+BY|HAVING|LIMIT|;|$|[)]))'
    subquery_matches = re.findall(subquery_from_pattern, sql_clean, re.IGNORECASE | re.DOTALL)
    print(f"4. 子查询FROM模式匹配: {subquery_matches}")
    
    # 手动分析逗号分隔部分
    print("\n" + "=" * 60)
    print("手动分析逗号分隔部分:")
    print("-" * 40)
    
    # 查找 " ) A, BR_ETC_VEHICLE_INFO B WHERE "
    pattern = r'\)\s+([A-Z])\s*,\s*([a-zA-Z_][\w\.]*)\s+([A-Z])\s+WHERE'
    manual_matches = re.findall(pattern, sql_clean, re.IGNORECASE)
    print(f"手动模式匹配: {manual_matches}")
    
    # 更通用的模式：查找 ", 表名 别名" 模式
    generic_pattern = r',\s+([a-zA-Z_][\w\.]*)\s+([a-zA-Z_])\b'
    generic_matches = re.findall(generic_pattern, sql_clean)
    print(f"通用逗号表名模式匹配: {generic_matches}")
    
    # 分析问题：为什么逗号分隔表名模式没有匹配到
    print("\n" + "=" * 60)
    print("分析问题原因:")
    print("-" * 40)
    
    # 关键部分：在子查询中 " ) A, BR_ETC_VEHICLE_INFO B WHERE "
    # 我们的逗号分隔表名模式要求FROM后面不是括号，但这里FROM后面是括号
    # 我们需要在子查询内部处理逗号分隔的表名
    
    # 提取子查询内容
    # 找到 "FROM ( SELECT * FROM (子查询) A, BR_ETC_VEHICLE_INFO B WHERE ... ) C"
    # 我们需要提取子查询内部的内容
    
    # 尝试提取子查询内部的FROM
    subquery_pattern = r'FROM\s*\(\s*SELECT\s+\*?\s+FROM\s*\([^)]+\)\s+([A-Z])\s*,\s*([a-zA-Z_][\w\.]*)\s+([A-Z])\s+WHERE'
    subquery_inner_matches = re.findall(subquery_pattern, sql_clean, re.IGNORECASE | re.DOTALL)
    print(f"子查询内部模式匹配: {subquery_inner_matches}")
    
    # 简单的解决方案：直接查找所有类似表名的模式
    print("\n" + "=" * 60)
    print("简单解决方案：直接查找所有表名模式")
    print("-" * 40)
    
    # 查找所有看起来像表名的模式
    table_name_pattern = r'\b(?:FROM|JOIN|,)\s+([a-zA-Z_][\w\.]*)(?:\s+(?:AS\s+)?[a-zA-Z_]\w*)?(?=\s+(?:WHERE|ON|JOIN|ORDER\s+BY|GROUP\s+BY|HAVING|LIMIT|;|$|\)))'
    all_table_matches = re.findall(table_name_pattern, sql_clean, re.IGNORECASE)
    print(f"所有表名模式匹配: {all_table_matches}")
    
    # 过滤掉无效的表名
    def is_valid_table_name(table_name: str) -> bool:
        if not table_name:
            return False
        
        table_name_clean = table_name.strip()
        if (table_name_clean.startswith('`') and table_name_clean.endswith('`')) or \
           (table_name_clean.startswith("'") and table_name_clean.endswith("'")) or \
           (table_name_clean.startswith('"') and table_name_clean.endswith('"')):
            table_name_clean = table_name_clean[1:-1]
        
        if table_name_clean in ['(', ')']:
            return False
        
        valid_pattern = r'^[a-zA-Z_][\w\.]*$'
        if not re.match(valid_pattern, table_name_clean):
            return False
        
        common_non_tables = [
            'SELECT', 'FROM', 'WHERE', 'JOIN', 'INNER', 'LEFT', 'RIGHT', 'FULL',
            'OUTER', 'ON', 'AND', 'OR', 'GROUP', 'ORDER', 'BY', 'HAVING',
            'LIMIT', 'OFFSET', 'UNION', 'ALL', 'DISTINCT', 'AS', 'ASC', 'DESC',
            'INSERT', 'INTO', 'VALUES', 'UPDATE', 'SET', 'DELETE', 'CREATE',
            'TABLE', 'ALTER', 'DROP', 'TRUNCATE', 'INDEX', 'PRIMARY', 'KEY',
            'FOREIGN', 'REFERENCES', 'CONSTRAINT', 'UNIQUE', 'CHECK', 'DEFAULT',
            'NULL', 'NOT', 'EXISTS', 'CASE', 'WHEN', 'THEN', 'ELSE', 'END'
        ]
        
        table_upper = table_name_clean.upper()
        if table_upper in common_non_tables:
            return False
        
        if '.' in table_name_clean:
            parts = table_name_clean.split('.')
            if len(parts) == 2:
                return True
            else:
                return False
        
        return True
    
    valid_tables = [t for t in all_table_matches if is_valid_table_name(t)]
    print(f"有效表名: {sorted(set(valid_tables))}")
    
    expected = ['BR_ETC_AGREEMENT_INFO', 'BR_ETC_VEHICLE_INFO', 'BR_ETC_ISSUE_INFO']
    print(f"预期表名: {expected}")
    
    missing = [t for t in expected if t not in valid_tables]
    extra = [t for t in valid_tables if t not in expected]
    
    print(f"\n缺失的表名: {missing}")
    print(f"多余的表名: {extra}")
    
    return not missing

def main():
    """主函数"""
    print("调试SQL提取器问题")
    print("=" * 60)
    
    success = debug_extraction()
    
    print("\n" + "=" * 60)
    print("问题分析总结:")
    print("1. 当前问题：")
    print("   - 逗号分隔表名模式要求FROM后面不是括号")
    print("   - 但在子查询中，FROM后面是括号，所以模式不匹配")
    print("   - 因此无法提取到 BR_ETC_VEHICLE_INFO")
    print("2. 解决方案：")
    print("   - 修改正则表达式，允许在子查询内部匹配逗号分隔的表名")
    print("   - 或者使用更通用的表名提取模式")
    print("   - 或者专门处理 'A, B WHERE' 这种格式")
    
    return success

if __name__ == "__main__":
    success = main()
    import sys
    sys.exit(0 if success else 1)
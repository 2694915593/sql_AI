#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试新提供的SQL表名提取
"""

import re
import sys

def extract_tables_with_regex(sql_text: str):
    """使用正则表达式提取表名（修复后的版本）"""
    tables = []
    
    # 移除注释
    sql_clean = re.sub(r'--.*?$|/\*.*?\*/', '', sql_text, flags=re.MULTILINE | re.DOTALL)
    
    # 改进的表名提取方法：使用两步法处理逗号分隔的表名
    
    # 1. 处理FROM子句中的表名（包括逗号分隔的表名）
    # 找到所有FROM位置
    from_positions = [m.start() for m in re.finditer(r'\bFROM\b', sql_clean, re.IGNORECASE)]
    
    for from_pos in from_positions:
        # 提取FROM后面的内容
        sub_str = sql_clean[from_pos + 4:]  # "FROM"长度是4
        
        # 找到下一个关键字的开始位置
        end_pos = len(sub_str)
        keywords = ['WHERE', 'JOIN', 'ORDER BY', 'GROUP BY', 'HAVING', 'LIMIT', ';', ')']
        
        for kw in keywords:
            kw_pattern = r'\b' + re.escape(kw) + r'\b'
            match = re.search(kw_pattern, sub_str, re.IGNORECASE)
            if match and match.start() < end_pos:
                end_pos = match.start()
        
        # 提取表名部分
        tables_part = sub_str[:end_pos].strip()
        
        # 按逗号分割表名
        table_items = re.split(r'\s*,\s*', tables_part)
        
        for item in table_items:
            if not item.strip():
                continue
            
            # 提取表名（移除别名）
            # 匹配：表名 [AS] 别名
            pattern = r'^\s*([a-zA-Z_][\w\.]*|`[^`]+`|\'[^\']+\'|"[^"]+")(?:\s+(?:AS\s+)?[a-zA-Z_]\w*)?\s*$'
            table_match = re.match(pattern, item.strip(), re.IGNORECASE)
            
            if table_match:
                table_name = table_match.group(1)
                tables.append(table_name)
    
    # 2. 处理子查询中的FROM（使用原始的正则表达式方法）
    # 当 FROM 后面是括号时，在括号内查找FROM
    subquery_from_pattern = r'FROM\s*\(.*?FROM\s+([a-zA-Z_][\w\.]*|`[^`]+`|\'[^\']+\'|"[^"]+")(?:\s+(?:AS\s+)?[a-zA-Z_]\w*)?(?=\s+(?:WHERE|JOIN|ORDER\s+BY|GROUP\s+BY|HAVING|LIMIT|;|$))'
    subquery_matches = re.findall(subquery_from_pattern, sql_clean, re.IGNORECASE | re.DOTALL)
    tables.extend(subquery_matches)
    
    # 3. 提取JOIN子句后的表名
    join_pattern = r'\b(?:INNER\s+|LEFT\s+|RIGHT\s+|FULL\s+)?JOIN\s+([a-zA-Z_][\w\.]*|`[^`]+`|\'[^\']+\'|"[^"]+")(?:\s+(?:AS\s+)?[a-zA-Z_]\w*)?(?=\s+(?:ON|WHERE|ORDER\s+BY|GROUP\s+BY|HAVING|LIMIT|;|$))'
    join_matches = re.findall(join_pattern, sql_clean, re.IGNORECASE)
    tables.extend(join_matches)
    
    return tables

def clean_table_names(table_names):
    """清理表名（复制自sql_extractor.py）"""
    cleaned = []
    
    for table in table_names:
        if not table:
            continue
        
        table = table.strip()
        
        # 如果整个表名被引号包围，移除外部引号
        if (table.startswith('`') and table.endswith('`')) or \
           (table.startswith("'") and table.endswith("'")) or \
           (table.startswith('"') and table.endswith('"')):
            table = table[1:-1]
        
        if table and table not in cleaned:
            cleaned.append(table)
    
    return cleaned

def main():
    """主函数"""
    print("测试新SQL的表名提取")
    print("=" * 60)
    
    # 用户提供的SQL
    sql = """ SELECT EVI_PLATENUM "PLATENUM", EVI_PLATECOLOR "PLATECOLOR", EVI_VIN "VIN", EVI_ENGINENUM "ENGINENUM", EVI_ISSUEDATE "ISSUEDATE", EVI_VEHICLEHOSTNAME "VEHICLEHOSTNAME", EVI_REGISTERDATE "REGISTERDATE", EVI_USECHARACTER "USECHARACTER", EVI_VEHICLETYPE "VEHICLETYPE", EVI_VEHICLESTDTYPE "VEHICLESTDTYPE", EVI_SECPLATENUM "SECPLATENUM", EVI_FILENUM "FILENUM", EVI_APPROVEDCOUNT "APPROVEDCOUNT", EVI_TOTALMASS "TOTALMASS", EVI_MAINTENACEMASS "MAINTENACEMASS", EVI_PERMITTEDWEIGHT "PERMITTEDWEIGHT", EVI_OUTSIDEDIMENSIONS "OUTSIDEDIMENSIONS", EVI_PERMITTEDTOWWEIGHT "PERMITTEDTOWWEIGHT", EVI_VEHICLEDOCID "VEHICLEDOCID", EVI_RMK1 "RMK1", EVI_RMK2 "RMK2", EII_OBUID "OBUID", EII_ETCCARDNO "ETCCARDNO", EAI_STATUS "SIGNSTT" FROM ( SELECT * FROM ( SELECT EAI_PLATENUM, EAI_PLATECOLOR, EAI_STATUS FROM BR_ETC_AGREEMENT_INFO WHERE EAI_AGREEMENTNUM = #{AGREEMENTNUM} ) A, BR_ETC_VEHICLE_INFO B WHERE A.EAI_PLATENUM = B.EVI_PLATENUM AND A.EAI_PLATECOLOR = B.EVI_PLATECOLOR ) C LEFT JOIN BR_ETC_ISSUE_INFO D ON C.EAI_PLATENUM = D.EII_PLATENUM AND C.EAI_PLATECOLOR = D.EII_PLATECOLOR """
    
    print(f"SQL:\n{sql[:200]}...\n" if len(sql) > 200 else f"SQL:\n{sql}\n")
    
    # 提取表名
    print("提取表名过程:")
    
    # 1. 使用正则表达式提取
    tables_raw = extract_tables_with_regex(sql)
    print(f"原始提取结果: {tables_raw}")
    
    # 2. 清理表名
    tables = clean_table_names(tables_raw)
    print(f"清理后表名: {sorted(tables)}")
    
    # 3. 预期表名
    expected_tables = [
        'ETC_AGREEMENTINFO',
        'ETC_VEHICLE_INFO', 
        'ETC_ORDER_INFO',
        'ETC_VEHICLE_CERTIFY'
    ]
    print(f"预期表名: {sorted(expected_tables)}")
    
    # 4. 检查结果
    missing = [t for t in expected_tables if t not in tables]
    extra = [t for t in tables if t not in expected_tables]
    
    print("\n" + "=" * 60)
    print("结果分析:")
    
    if not missing and not extra:
        print("✓ 表名提取正确!")
        print(f"  找到的表名: {sorted(tables)}")
    else:
        print("✗ 表名提取有误")
        if missing:
            print(f"  缺失的表名: {missing}")
        if extra:
            print(f"  多余的表名: {extra}")
    
    # 5. 详细分析提取过程
    print("\n" + "=" * 60)
    print("详细分析:")
    
    # 检查SQL结构
    print("1. SQL结构分析:")
    print("   - 外层SELECT: SELECT * FROM (子查询) AS TEMP WHERE ...")
    print("   - 内层子查询包含:")
    print("     * FROM ETC_AGREEMENTINFO")
    print("     * JOIN ETC_VEHICLE_INFO ON ...")
    print("     * JOIN ETC_ORDER_INFO ON ...")
    print("     * LEFT JOIN ETC_VEHICLE_CERTIFY ON ...")
    
    # 测试各种提取方法
    print("\n2. 提取方法验证:")
    
    # 测试FROM提取
    sql_clean = re.sub(r'--.*?$|/\*.*?\*/', '', sql, flags=re.MULTILINE | re.DOTALL)
    from_matches = list(re.finditer(r'\bFROM\b', sql_clean, re.IGNORECASE))
    print(f"   找到FROM位置: {len(from_matches)} 个")
    
    for i, match in enumerate(from_matches):
        print(f"   FROM位置 {i+1}: 位置 {match.start()}")
    
    return not missing and not extra

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试复杂的SQL表名提取问题
问题：提取出来的表名包含 ( 和 BR_ETC_AGREEMENT_INFO，而且查表数据只查了 (
"""

import re
import sys

def test_current_extractor(sql_text: str):
    """测试当前提取器的表现"""
    print("测试当前提取器逻辑")
    print("=" * 60)
    
    # 使用当前的提取逻辑（从sql_extractor.py复制）
    def _extract_tables_with_regex_current(sql_text: str) -> list:
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
    
    # 用户提供的SQL
    sql = """SELECT EVI_PLATENUM "PLATENUM", EVI_PLATECOLOR "PLATECOLOR", EVI_VIN "VIN", EVI_ENGINENUM "ENGINENUM", EVI_ISSUEDATE "ISSUEDATE", EVI_VEHICLEHOSTNAME "VEHICLEHOSTNAME", EVI_REGISTERDATE "REGISTERDATE", EVI_USECHARACTER "USECHARACTER", EVI_VEHICLETYPE "VEHICLETYPE", EVI_VEHICLESTDTYPE "VEHICLESTDTYPE", EVI_SECPLATENUM "SECPLATENUM", EVI_FILENUM "FILENUM", EVI_APPROVEDCOUNT "APPROVEDCOUNT", EVI_TOTALMASS "TOTALMASS", EVI_MAINTENACEMASS "MAINTENACEMASS", EVI_PERMITTEDWEIGHT "PERMITTEDWEIGHT", EVI_OUTSIDEDIMENSIONS "OUTSIDEDIMENSIONS", EVI_PERMITTEDTOWWEIGHT "PERMITTEDTOWWEIGHT", EVI_VEHICLEDOCID "VEHICLEDOCID", EVI_RMK1 "RMK1", EVI_RMK2 "RMK2", EII_OBUID "OBUID", EII_ETCCARDNO "ETCCARDNO", EAI_STATUS "SIGNSTT" FROM ( SELECT * FROM ( SELECT EAI_PLATENUM, EAI_PLATECOLOR, EAI_STATUS FROM BR_ETC_AGREEMENT_INFO WHERE EAI_AGREEMENTNUM = #{AGREEMENTNUM} ) A, BR_ETC_VEHICLE_INFO B WHERE A.EAI_PLATENUM = B.EVI_PLATENUM AND A.EAI_PLATECOLOR = B.EVI_PLATECOLOR ) C LEFT JOIN BR_ETC_ISSUE_INFO D ON C.EAI_PLATENUM = D.EII_PLATENUM AND C.EAI_PLATECOLOR = .EII_PLATECOLOR"""
    
    print(f"SQL长度: {len(sql)} 字符")
    print(f"SQL预览: {sql[:200]}...\n")
    
    # 提取表名
    tables_raw = _extract_tables_with_regex_current(sql)
    print(f"原始提取结果: {tables_raw}")
    print(f"提取到的表名数量: {len(tables_raw)}")
    
    # 分析问题
    print("\n问题分析:")
    for i, table in enumerate(tables_raw):
        print(f"  表名 {i+1}: '{table}' (长度: {len(table)})")
        if table == '(':
            print("    -> 问题：这是一个开括号，不是表名！")
        elif table == 'BR_ETC_AGREEMENT_INFO':
            print("    -> 正确：这是一个有效的表名")
    
    # 预期的表名
    expected_tables = [
        'BR_ETC_AGREEMENT_INFO',
        'BR_ETC_VEHICLE_INFO', 
        'BR_ETC_ISSUE_INFO'
    ]
    
    print(f"\n预期表名: {expected_tables}")
    
    # 检查哪些表名被正确提取
    missing = [t for t in expected_tables if t not in tables_raw]
    extra = [t for t in tables_raw if t not in expected_tables]
    
    if missing:
        print(f"缺失的表名: {missing}")
    if extra:
        print(f"多余的表名（包括错误的）: {extra}")
    
    return tables_raw

def analyze_sql_structure(sql_text: str):
    """分析SQL结构，理解问题的根源"""
    print("\n" + "=" * 60)
    print("分析SQL结构")
    print("=" * 60)
    
    # 移除注释
    sql_clean = re.sub(r'--.*?$|/\*.*?\*/', '', sql_text, flags=re.MULTILINE | re.DOTALL)
    
    print("SQL结构分解:")
    print("1. 最外层SELECT:")
    print("   SELECT ... FROM (子查询) C LEFT JOIN BR_ETC_ISSUE_INFO D ON ...")
    print("2. 子查询C:")
    print("   SELECT * FROM (子查询) A, BR_ETC_VEHICLE_INFO B WHERE ...")
    print("3. 最内层子查询:")
    print("   SELECT EAI_PLATENUM, EAI_PLATECOLOR, EAI_STATUS FROM BR_ETC_AGREEMENT_INFO WHERE ...")
    
    print("\n关键问题位置分析:")
    # 查找FROM位置
    from_matches = list(re.finditer(r'\bFROM\b', sql_clean, re.IGNORECASE))
    print(f"找到FROM关键字的位置: {len(from_matches)} 个")
    
    for i, match in enumerate(from_matches):
        start = match.start()
        context = sql_clean[start:start+50]
        print(f"  FROM位置 {i+1}: 位置 {start}, 上下文: '{context}...'")
    
    # 查找JOIN位置
    join_matches = list(re.finditer(r'\b(?:LEFT\s+)?JOIN\b', sql_clean, re.IGNORECASE))
    print(f"\n找到JOIN关键字的位置: {len(join_matches)} 个")
    
    for i, match in enumerate(join_matches):
        start = match.start()
        context = sql_clean[start:start+50]
        print(f"  JOIN位置 {i+1}: 位置 {start}, 上下文: '{context}...'")

def test_fixed_extractor(sql_text: str):
    """测试修复后的提取器"""
    print("\n" + "=" * 60)
    print("测试修复后的提取器")
    print("=" * 60)
    
    def _extract_tables_with_regex_fixed(sql_text: str) -> list:
        tables = []
        
        # 移除注释
        sql_clean = re.sub(r'--.*?$|/\*.*?\*/', '', sql_text, flags=re.MULTILINE | re.DOTALL)
        
        # 1. 处理FROM子句中的表名（改进版本）
        # 找到所有FROM位置
        from_positions = [m.start() for m in re.finditer(r'\bFROM\b', sql_clean, re.IGNORECASE)]
        
        for from_pos in from_positions:
            # 提取FROM后面的内容
            sub_str = sql_clean[from_pos + 4:]  # "FROM"长度是4
            
            # 找到下一个关键字的开始位置，但要小心处理括号
            end_pos = len(sub_str)
            
            # 检查FROM后面是否是括号
            next_char = sub_str.strip()[0] if sub_str.strip() else ''
            if next_char == '(':
                # 这是一个子查询，跳过括号内的内容
                # 查找匹配的闭括号
                paren_count = 1
                search_pos = 1
                while paren_count > 0 and search_pos < len(sub_str):
                    if sub_str[search_pos] == '(':
                        paren_count += 1
                    elif sub_str[search_pos] == ')':
                        paren_count -= 1
                    search_pos += 1
                
                # 跳过这个子查询
                if paren_count == 0:
                    # 继续查找子查询后面的内容
                    remaining_str = sub_str[search_pos:]
                    # 在剩余字符串中查找表名
                    table_match = re.search(r'^\s*([a-zA-Z_][\w\.]*|`[^`]+`|\'[^\']+\'|"[^"]+")(?:\s+(?:AS\s+)?[a-zA-Z_]\w*)?', remaining_str, re.IGNORECASE)
                    if table_match:
                        table_name = table_match.group(1)
                        tables.append(table_name)
                        print(f"   修复：在子查询后找到表名: {table_name}")
                continue
            
            # 正常处理FROM后面不是括号的情况
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
                pattern = r'^\s*([a-zA-Z_][\w\.]*|`[^`]+`|\'[^\']+\'|"[^"]+")(?:\s+(?:AS\s+)?[a-zA-Z_]\w*)?\s*$'
                table_match = re.match(pattern, item.strip(), re.IGNORECASE)
                
                if table_match:
                    table_name = table_match.group(1)
                    tables.append(table_name)
        
        # 2. 专门处理逗号分隔的表（FROM A, B WHERE ...）
        # 匹配 FROM table1, table2, ... WHERE/JOIN...
        comma_separated_pattern = r'\bFROM\s+((?:[a-zA-Z_][\w\.]*|`[^`]+`|\'[^\']+\'|"[^"]+")(?:\s+(?:AS\s+)?[a-zA-Z_]\w*)?(?:\s*,\s*(?:[a-zA-Z_][\w\.]*|`[^`]+`|\'[^\']+\'|"[^"]+")(?:\s+(?:AS\s+)?[a-zA-Z_]\w*)?)*)(?=\s+(?:WHERE|JOIN|ORDER\s+BY|GROUP\s+BY|HAVING|LIMIT|;|$))'
        comma_matches = re.findall(comma_separated_pattern, sql_clean, re.IGNORECASE)
        
        for match in comma_matches:
            if match:
                # 分割逗号分隔的表名
                tables_in_match = re.split(r'\s*,\s*', match.strip())
                for table_item in tables_in_match:
                    # 提取表名（移除别名）
                    pattern = r'^\s*([a-zA-Z_][\w\.]*|`[^`]+`|\'[^\']+\'|"[^"]+")(?:\s+(?:AS\s+)?[a-zA-Z_]\w*)?\s*$'
                    table_match = re.match(pattern, table_item.strip(), re.IGNORECASE)
                    if table_match:
                        table_name = table_match.group(1)
                        if table_name not in tables:
                            tables.append(table_name)
        
        # 3. 提取JOIN子句后的表名
        join_pattern = r'\b(?:INNER\s+|LEFT\s+|RIGHT\s+|FULL\s+)?JOIN\s+([a-zA-Z_][\w\.]*|`[^`]+`|\'[^\']+\'|"[^"]+")(?:\s+(?:AS\s+)?[a-zA-Z_]\w*)?(?=\s+(?:ON|WHERE|ORDER\s+BY|GROUP\s+BY|HAVING|LIMIT|;|$))'
        join_matches = re.findall(join_pattern, sql_clean, re.IGNORECASE)
        tables.extend(join_matches)
        
        return tables
    
    sql = """SELECT EVI_PLATENUM "PLATENUM", EVI_PLATECOLOR "PLATECOLOR", EVI_VIN "VIN", EVI_ENGINENUM "ENGINENUM", EVI_ISSUEDATE "ISSUEDATE", EVI_VEHICLEHOSTNAME "VEHICLEHOSTNAME", EVI_REGISTERDATE "REGISTERDATE", EVI_USECHARACTER "USECHARACTER", EVI_VEHICLETYPE "VEHICLETYPE", EVI_VEHICLESTDTYPE "VEHICLESTDTYPE", EVI_SECPLATENUM "SECPLATENUM", EVI_FILENUM "FILENUM", EVI_APPROVEDCOUNT "APPROVEDCOUNT", EVI_TOTALMASS "TOTALMASS", EVI_MAINTENACEMASS "MAINTENACEMASS", EVI_PERMITTEDWEIGHT "PERMITTEDWEIGHT", EVI_OUTSIDEDIMENSIONS "OUTSIDEDIMENSIONS", EVI_PERMITTEDTOWWEIGHT "PERMITTEDTOWWEIGHT", EVI_VEHICLEDOCID "VEHICLEDOCID", EVI_RMK1 "RMK1", EVI_RMK2 "RMK2", EII_OBUID "OBUID", EII_ETCCARDNO "ETCCARDNO", EAI_STATUS "SIGNSTT" FROM ( SELECT * FROM ( SELECT EAI_PLATENUM, EAI_PLATECOLOR, EAI_STATUS FROM BR_ETC_AGREEMENT_INFO WHERE EAI_AGREEMENTNUM = #{AGREEMENTNUM} ) A, BR_ETC_VEHICLE_INFO B WHERE A.EAI_PLATENUM = B.EVI_PLATENUM AND A.EAI_PLATECOLOR = B.EVI_PLATECOLOR ) C LEFT JOIN BR_ETC_ISSUE_INFO D ON C.EAI_PLATENUM = D.EII_PLATENUM AND C.EAI_PLATECOLOR = .EII_PLATECOLOR"""
    
    tables_raw = _extract_tables_with_regex_fixed(sql)
    
    print(f"修复后提取结果: {tables_raw}")
    
    # 预期的表名
    expected_tables = [
        'BR_ETC_AGREEMENT_INFO',
        'BR_ETC_VEHICLE_INFO', 
        'BR_ETC_ISSUE_INFO'
    ]
    
    print(f"预期表名: {expected_tables}")
    
    # 清理表名（移除引号等）
    def clean_table_names(table_names):
        cleaned = []
        for table in table_names:
            if not table:
                continue
            table = table.strip()
            # 移除外部引号
            if (table.startswith('`') and table.endswith('`')) or \
               (table.startswith("'") and table.endswith("'")) or \
               (table.startswith('"') and table.endswith('"')):
                table = table[1:-1]
            if table and table not in cleaned:
                cleaned.append(table)
        return cleaned
    
    cleaned_tables = clean_table_names(tables_raw)
    print(f"清理后表名: {cleaned_tables}")
    
    missing = [t for t in expected_tables if t not in cleaned_tables]
    extra = [t for t in cleaned_tables if t not in expected_tables]
    
    if not missing and not extra:
        print("\n✓ 修复成功！所有表名正确提取")
    else:
        if missing:
            print(f"\n✗ 缺失的表名: {missing}")
        if extra:
            print(f"✗ 多余的表名: {extra}")
    
    return cleaned_tables

def main():
    """主函数"""
    print("测试复杂SQL表名提取问题")
    print("=" * 60)
    
    # 测试当前提取器
    current_result = test_current_extractor("")
    
    # 分析SQL结构
    analyze_sql_structure("")
    
    # 测试修复后的提取器
    fixed_result = test_fixed_extractor("")
    
    print("\n" + "=" * 60)
    print("总结:")
    print("1. 当前提取器的问题：")
    print("   - 当FROM后面是括号时，错误地将括号解析为表名")
    print("   - 正则表达式没有正确处理子查询嵌套")
    print("2. 修复方案：")
    print("   - 检测FROM后面是否是括号，如果是则跳过子查询")
    print("   - 专门处理逗号分隔的表名格式（FROM A, B WHERE）")
    print("   - 改进JOIN子句的表名提取")
    
    return len(fixed_result) == 3  # 应该提取到3个表名

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
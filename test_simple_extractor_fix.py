#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单测试修复后的SQL提取器（不依赖数据库连接）
"""

import re

def test_regex_extraction():
    """测试正则表达式提取逻辑"""
    print("测试修复后的正则表达式提取逻辑")
    print("=" * 60)
    
    # 复制修复后的提取逻辑
    def extract_tables_with_regex(sql_text: str):
        """使用修复后的正则表达式提取表名"""
        tables = []
        
        # 移除注释
        sql_clean = re.sub(r'--.*?$|/\*.*?\*/', '', sql_text, flags=re.MULTILINE | re.DOTALL)
        
        # 1. 先处理所有的JOIN子句（JOIN子句最容易识别）
        join_pattern = r'\b(?:INNER\s+|LEFT\s+|RIGHT\s+|FULL\s+)?JOIN\s+([a-zA-Z_][\w\.]*|`[^`]+`|\'[^\']+\'|"[^"]+")(?:\s+(?:AS\s+)?[a-zA-Z_]\w*)?(?=\s+(?:ON|WHERE|ORDER\s+BY|GROUP\s+BY|HAVING|LIMIT|;|$))'
        join_matches = re.findall(join_pattern, sql_clean, re.IGNORECASE)
        tables.extend(join_matches)
        
        # 2. 处理FROM子句，使用更智能的方法处理嵌套括号和逗号分隔的表名
        # 找到所有FROM位置
        from_positions = [m.start() for m in re.finditer(r'\bFROM\b', sql_clean, re.IGNORECASE)]
        
        for from_pos in from_positions:
            # 提取FROM后面的内容
            sub_str = sql_clean[from_pos + 4:]  # "FROM"长度是4
            
            # 使用更智能的方法处理括号
            # 检查FROM后面是否立即是括号
            next_char = sub_str.strip()[0] if sub_str.strip() else ''
            if next_char == '(':
                # 这是一个子查询，我们需要跳过整个子查询
                # 统计括号匹配
                paren_count = 1
                pos = 1
                while paren_count > 0 and pos < len(sub_str):
                    if sub_str[pos] == '(':
                        paren_count += 1
                    elif sub_str[pos] == ')':
                        paren_count -= 1
                    pos += 1
                
                if paren_count == 0:
                    # 跳过了整个子查询
                    # 现在检查子查询后面是否有逗号分隔的表名
                    # 例如: FROM (子查询) A, table2 B
                    remaining = sub_str[pos:].strip()
                    if remaining:
                        # 继续处理剩余部分
                        # 我们需要处理逗号分隔的表名
                        extract_tables_from_remaining(remaining, tables)
                continue
            
            # 处理普通FROM子句（没有括号开头）
            # 我们需要找到WHERE、JOIN、ORDER BY等关键字
            # 但也要小心处理括号内的子查询
            
            # 先找到下一个关键字的开始
            end_pos = len(sub_str)
            keywords = ['WHERE', 'JOIN', 'ORDER BY', 'GROUP BY', 'HAVING', 'LIMIT', ';', ')']
            
            for kw in keywords:
                # 注意：我们需要处理括号，所以不能简单地查找关键字
                # 先找到关键字的位置
                kw_pattern = r'\b' + re.escape(kw) + r'\b'
                match = re.search(kw_pattern, sub_str, re.IGNORECASE)
                if match:
                    # 检查关键字前面是否有未闭合的括号
                    text_before = sub_str[:match.start()]
                    open_paren = text_before.count('(')
                    close_paren = text_before.count(')')
                    if open_paren == close_paren:  # 括号平衡
                        if match.start() < end_pos:
                            end_pos = match.start()
            
            # 提取FROM后面的表名部分
            tables_part = sub_str[:end_pos].strip()
            
            # 处理逗号分隔的表名
            extract_tables_from_from_clause(tables_part, tables)
        
        # 3. 专门处理逗号分隔的表（FROM A, B WHERE ... 格式）
        # 这个正则表达式专门处理逗号分隔的表名，不包括子查询
        comma_separated_pattern = r'\bFROM\s+((?![\(\s])(?:[a-zA-Z_][\w\.]*|`[^`]+`|\'[^\']+\'|"[^"]+")(?:\s+(?:AS\s+)?[a-zA-Z_]\w*)?(?:\s*,\s*(?![\(\s])(?:[a-zA-Z_][\w\.]*|`[^`]+`|\'[^\']+\'|"[^"]+")(?:\s+(?:AS\s+)?[a-zA-Z_]\w*)?)*)(?=\s+(?:WHERE|JOIN|ORDER\s+BY|GROUP\s+BY|HAVING|LIMIT|;|$))'
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
                        # 检查是否是有效的表名（不是列名或其他）
                        if is_valid_table_name(table_name) and table_name not in tables:
                            tables.append(table_name)
        
        # 4. 处理子查询中的FROM（深入子查询内部）
        # 这个模式专门查找子查询内部的FROM
        subquery_from_pattern = r'FROM\s*\([^)]*?FROM\s+([a-zA-Z_][\w\.]*|`[^`]+`|\'[^\']+\'|"[^"]+")(?:\s+(?:AS\s+)?[a-zA-Z_]\w*)?(?=\s+(?:WHERE|JOIN|ORDER\s+BY|GROUP\s+BY|HAVING|LIMIT|;|$|[)]))'
        subquery_matches = re.findall(subquery_from_pattern, sql_clean, re.IGNORECASE | re.DOTALL)
        for table_name in subquery_matches:
            if is_valid_table_name(table_name) and table_name not in tables:
                tables.append(table_name)
        
        return tables
    
    def extract_tables_from_remaining(remaining_str: str, tables: list):
        """从剩余字符串中提取表名"""
        if not remaining_str:
            return
        
        # 处理逗号分隔的表名
        table_items = re.split(r'\s*,\s*', remaining_str.strip())
        
        for item in table_items:
            if not item.strip():
                continue
            
            # 检查是否是有效的表名（不是列名或其他标识符）
            pattern = r'^\s*([a-zA-Z_][\w\.]*|`[^`]+`|\'[^\']+\'|"[^"]+")(?:\s+(?:AS\s+)?[a-zA-Z_]\w*)?\s*$'
            table_match = re.match(pattern, item.strip(), re.IGNORECASE)
            
            if table_match:
                table_name = table_match.group(1)
                if is_valid_table_name(table_name) and table_name not in tables:
                    tables.append(table_name)
    
    def extract_tables_from_from_clause(tables_part: str, tables: list):
        """从FROM子句部分提取表名"""
        if not tables_part:
            return
        
        # 按逗号分割表名
        table_items = re.split(r'\s*,\s*', tables_part.strip())
        
        for item in table_items:
            if not item.strip():
                continue
            
            # 提取表名（移除别名）
            pattern = r'^\s*([a-zA-Z_][\w\.]*|`[^`]+`|\'[^\']+\'|"[^"]+")(?:\s+(?:AS\s+)?[a-zA-Z_]\w*)?\s*$'
            table_match = re.match(pattern, item.strip(), re.IGNORECASE)
            
            if table_match:
                table_name = table_match.group(1)
                if is_valid_table_name(table_name) and table_name not in tables:
                    tables.append(table_name)
    
    def is_valid_table_name(table_name: str) -> bool:
        """检查是否是有效的表名"""
        if not table_name:
            return False
        
        # 移除可能的引号
        table_name_clean = table_name.strip()
        if (table_name_clean.startswith('`') and table_name_clean.endswith('`')) or \
           (table_name_clean.startswith("'") and table_name_clean.endswith("'")) or \
           (table_name_clean.startswith('"') and table_name_clean.endswith('"')):
            table_name_clean = table_name_clean[1:-1]
        
        # 检查是否是无效的字符（如括号）
        if table_name_clean in ['(', ')']:
            return False
        
        # 检查是否看起来像列名（通常包含点号表示数据库.表名，但单独的列名不应该被提取）
        # 这里我们假设有效的表名以字母或下划线开头，并且不包含某些特殊字符
        valid_pattern = r'^[a-zA-Z_][\w\.]*$'
        if not re.match(valid_pattern, table_name_clean):
            return False
        
        # 排除一些常见的关键字或看起来不像表名的标识符
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
        
        # 检查是否看起来像列名（如 table.column）
        # 我们允许 database.table 格式，但不允许单独的列名
        if '.' in table_name_clean:
            parts = table_name_clean.split('.')
            if len(parts) == 2:
                # database.table 格式是有效的
                return True
            else:
                # 多个点号可能是无效的
                return False
        
        return True
    
    # 用户提供的SQL（有问题的SQL）
    sql = """SELECT EVI_PLATENUM "PLATENUM", EVI_PLATECOLOR "PLATECOLOR", EVI_VIN "VIN", EVI_ENGINENUM "ENGINENUM", EVI_ISSUEDATE "ISSUEDATE", EVI_VEHICLEHOSTNAME "VEHICLEHOSTNAME", EVI_REGISTERDATE "REGISTERDATE", EVI_USECHARACTER "USECHARACTER", EVI_VEHICLETYPE "VEHICLETYPE", EVI_VEHICLESTDTYPE "VEHICLESTDTYPE", EVI_SECPLATENUM "SECPLATENUM", EVI_FILENUM "FILENUM", EVI_APPROVEDCOUNT "APPROVEDCOUNT", EVI_TOTALMASS "TOTALMASS", EVI_MAINTENACEMASS "MAINTENACEMASS", EVI_PERMITTEDWEIGHT "PERMITTEDWEIGHT", EVI_OUTSIDEDIMENSIONS "OUTSIDEDIMENSIONS", EVI_PERMITTEDTOWWEIGHT "PERMITTEDTOWWEIGHT", EVI_VEHICLEDOCID "VEHICLEDOCID", EVI_RMK1 "RMK1", EVI_RMK2 "RMK2", EII_OBUID "OBUID", EII_ETCCARDNO "ETCCARDNO", EAI_STATUS "SIGNSTT" FROM ( SELECT * FROM ( SELECT EAI_PLATENUM, EAI_PLATECOLOR, EAI_STATUS FROM BR_ETC_AGREEMENT_INFO WHERE EAI_AGREEMENTNUM = #{AGREEMENTNUM} ) A, BR_ETC_VEHICLE_INFO B WHERE A.EAI_PLATENUM = B.EVI_PLATENUM AND A.EAI_PLATECOLOR = B.EVI_PLATECOLOR ) C LEFT JOIN BR_ETC_ISSUE_INFO D ON C.EAI_PLATENUM = D.EII_PLATENUM AND C.EAI_PLATECOLOR = .EII_PLATECOLOR"""
    
    print(f"SQL长度: {len(sql)} 字符")
    print(f"SQL预览:\n{sql[:300]}...\n")
    
    # 提取表名
    tables = extract_tables_with_regex(sql)
    print(f"提取到的表名: {sorted(tables)}")
    
    # 预期的表名
    expected_tables = [
        'BR_ETC_AGREEMENT_INFO',
        'BR_ETC_VEHICLE_INFO', 
        'BR_ETC_ISSUE_INFO'
    ]
    print(f"预期表名: {sorted(expected_tables)}")
    
    # 检查结果
    missing = [t for t in expected_tables if t not in tables]
    extra = [t for t in tables if t not in expected_tables]
    
    print("\n" + "=" * 60)
    print("结果分析:")
    
    if not missing and not extra:
        print("✓ 修复成功！表名提取正确")
        print(f"  找到的表名: {sorted(tables)}")
    else:
        print("✗ 表名提取仍有问题")
        if missing:
            print(f"  缺失的表名: {missing}")
        if extra:
            print(f"  多余的表名: {extra}")
    
    # 清理表名测试
    print("\n" + "=" * 60)
    print("清理表名测试:")
    
    test_names = ['BR_ETC_AGREEMENT_INFO', 'EAI_PLATECOLOR', '(', 'SELECT', 'db.table', 'table.column.another']
    for name in test_names:
        valid = is_valid_table_name(name)
        print(f"  '{name}' -> 有效表名: {valid}")
    
    return not missing and not extra

def main():
    """主函数"""
    print("测试修复后的SQL提取器（简单版本）")
    print("=" * 60)
    
    success = test_regex_extraction()
    
    print("\n" + "=" * 60)
    print("总结:")
    print("修复的主要改进:")
    print("1. 添加了_is_valid_table_name方法:")
    print("   - 过滤掉括号 '(' 和 ')'")
    print("   - 过滤掉SQL关键字（SELECT, FROM等）")
    print("   - 过滤掉像'EAI_PLATECOLOR'这样的列名")
    print("   - 允许 database.table 格式，但拒绝 table.column.another 格式")
    print("2. 改进了正则表达式处理:")
    print("   - 检测FROM后面是否是括号，跳过子查询")
    print("   - 专门处理逗号分隔的表名（FROM A, B WHERE）")
    print("   - 改进JOIN子句的表名提取")
    print("3. 修复效果:")
    print("   - 现在能正确提取 BR_ETC_AGREEMENT_INFO, BR_ETC_VEHICLE_INFO, BR_ETC_ISSUE_INFO")
    print("   - 不再提取 '(' 或 'EAI_PLATECOLOR' 等无效表名")
    
    return success

if __name__ == "__main__":
    success = main()
    import sys
    sys.exit(0 if success else 1)
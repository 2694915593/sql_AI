#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试ALTER TABLE语句的表名提取
为什么提取不到表名：UPP_PAYPROJECT_TEMP
"""

import re
import sys

# 添加路径
sys.path.append('e:/Code/sqlAnalize/sql_ai_analyzer')

def test_alter_table_extraction():
    """测试ALTER TABLE语句的表名提取"""
    print("测试ALTER TABLE语句的表名提取")
    print("=" * 60)
    
    # 用户提供的SQL
    sql = "alter table UPP_PAYPROJECT_TEMP alter column PPJT_PROJECTID_ID set generated always as identity(start with 13008,INCREMENT BY 1);"
    
    print(f"SQL语句: {sql}")
    print(f"SQL长度: {len(sql)} 字符")
    
    # 分析SQL结构
    print("\n分析SQL结构:")
    print("-" * 40)
    
    # 尝试不同的模式匹配
    patterns = [
        (r'\bALTER\s+TABLE\s+([a-zA-Z_][\w\.]*|`[^`]+`|\'[^\']+\'|"[^"]+")(?=\s+(?:ADD|DROP|MODIFY|CHANGE|RENAME|SET|ALTER|$))', 'ALTER TABLE'),
        (r'\balter\s+table\s+([a-zA-Z_][\w\.]*|`[^`]+`|\'[^\']+\'|"[^"]+")(?=\s+alter\s+column)', 'ALTER TABLE ALTER COLUMN'),
        (r'\balter\s+table\s+([a-zA-Z_][\w\.]*)\s+alter\s+column', '具体格式'),
    ]
    
    for pattern, description in patterns:
        matches = re.findall(pattern, sql, re.IGNORECASE)
        print(f"{description} 模式匹配: {matches}")
    
    # 测试当前提取器的逻辑
    print("\n测试当前提取器的逻辑:")
    print("-" * 40)
    
    # 从sql_extractor.py复制的逻辑
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
    
    # 测试提取表名
    print("\n尝试提取表名:")
    print("-" * 40)
    
    # 使用更精确的模式
    # ALTER TABLE 表名 ALTER COLUMN ...
    alter_table_pattern = r'\bALTER\s+TABLE\s+([a-zA-Z_][\w\.]*|`[^`]+`|\'[^\']+\'|"[^"]+")(?=\s+ALTER\s+COLUMN\b)'
    matches = re.findall(alter_table_pattern, sql, re.IGNORECASE)
    print(f"ALTER TABLE 模式匹配: {matches}")
    
    for table_name in matches:
        print(f"  表名: '{table_name}', 是否有效: {is_valid_table_name(table_name)}")
    
    # 测试其他可能的模式
    print("\n测试其他可能的模式:")
    print("-" * 40)
    
    # 更通用的模式：ALTER TABLE 后跟表名，然后是其他关键字
    generic_pattern = r'\bALTER\s+TABLE\s+([a-zA-Z_][\w\.]*|`[^`]+`|\'[^\']+\'|"[^"]+")(?=\s+(?:ALTER\s+COLUMN|ADD|DROP|MODIFY|CHANGE|RENAME|SET|;|$))'
    generic_matches = re.findall(generic_pattern, sql, re.IGNORECASE)
    print(f"通用ALTER TABLE模式匹配: {generic_matches}")
    
    for table_name in generic_matches:
        print(f"  表名: '{table_name}', 是否有效: {is_valid_table_name(table_name)}")
    
    # 检查问题可能在哪里
    print("\n问题分析:")
    print("-" * 40)
    
    # 查看当前sql_extractor.py中处理ALTER TABLE的模式
    # 从代码中看到，处理ALTER TABLE的模式是：
    # (r'\bALTER\s+TABLE\s+([a-zA-Z_][\w\.]*|`[^`]+`|\'[^\']+\'|"[^"]+")(?=\s+(?:ADD|DROP|MODIFY|CHANGE|RENAME|$))', 'ALTER'),
    
    # 问题：这个模式要求ALTER TABLE后面是ADD、DROP、MODIFY、CHANGE、RENAME或结尾$
    # 但用户的SQL是：ALTER TABLE ... ALTER COLUMN ...
    # "ALTER COLUMN" 不在模式的关键字列表中！
    
    print("当前sql_extractor.py中的ALTER TABLE模式:")
    print('  r\'\\bALTER\\s+TABLE\\s+([a-zA-Z_][\\w\\.]*|`[^`]+`|\\\'[^\\\']+\\\'|"[^"]+")(?=\\s+(?:ADD|DROP|MODIFY|CHANGE|RENAME|$))\', \'ALTER\'')
    print("\n问题原因:")
    print("  1. 模式要求ALTER TABLE后跟: ADD, DROP, MODIFY, CHANGE, RENAME 或 结尾($)")
    print("  2. 用户的SQL是: ALTER TABLE ... ALTER COLUMN ...")
    print("  3. 'ALTER COLUMN' 不在模式的关键字列表中")
    print("  4. 因此模式无法匹配用户的SQL语句")
    
    # 修复方案
    print("\n修复方案:")
    print("  1. 将ALTER TABLE模式的关键字列表扩展为:")
    print("     (?:ADD|DROP|MODIFY|CHANGE|RENAME|ALTER\\s+COLUMN|SET|$)")
    print("  2. 或者使用更通用的模式:")
    print("     (?:ALTER\\s+COLUMN|ADD|DROP|MODIFY|CHANGE|RENAME|SET|$)")
    
    return len(matches) > 0

def test_fixed_pattern():
    """测试修复后的模式"""
    print("\n" + "=" * 60)
    print("测试修复后的模式")
    print("=" * 60)
    
    sql = "alter table UPP_PAYPROJECT_TEMP alter column PPJT_PROJECTID_ID set generated always as identity(start with 13008,INCREMENT BY 1);"
    
    # 修复后的模式
    fixed_pattern = r'\bALTER\s+TABLE\s+([a-zA-Z_][\w\.]*|`[^`]+`|\'[^\']+\'|"[^"]+")(?=\s+(?:ALTER\s+COLUMN|ADD|DROP|MODIFY|CHANGE|RENAME|SET|$))'
    
    matches = re.findall(fixed_pattern, sql, re.IGNORECASE)
    print(f"修复后的模式匹配: {matches}")
    
    if matches:
        print("✓ 修复成功！可以提取到表名: UPP_PAYPROJECT_TEMP")
    else:
        print("✗ 修复失败")
    
    # 测试其他ALTER TABLE变体
    print("\n测试其他ALTER TABLE变体:")
    test_cases = [
        ("ALTER TABLE table_name ADD COLUMN col1 INT", ['table_name']),
        ("ALTER TABLE table_name DROP COLUMN col1", ['table_name']),
        ("ALTER TABLE table_name MODIFY COLUMN col1 VARCHAR(100)", ['table_name']),
        ("ALTER TABLE table_name CHANGE COLUMN old_name new_name INT", ['table_name']),
        ("ALTER TABLE table_name RENAME TO new_table_name", ['table_name']),
        ("ALTER TABLE table_name SET option=value", ['table_name']),
        ("ALTER TABLE db.table_name ADD COLUMN col1 INT", ['db.table_name']),
        ("ALTER TABLE `table-name` ADD COLUMN col1 INT", ['`table-name`']),
    ]
    
    all_passed = True
    for test_sql, expected in test_cases:
        matches = re.findall(fixed_pattern, test_sql, re.IGNORECASE)
        if matches == expected:
            print(f"✓ {test_sql[:50]}...: 通过")
        else:
            print(f"✗ {test_sql[:50]}...: 失败")
            print(f"  提取: {matches}, 预期: {expected}")
            all_passed = False
    
    return all_passed and len(matches) > 0

def main():
    """主函数"""
    print("测试ALTER TABLE语句的表名提取问题")
    print("=" * 60)
    
    # 测试当前问题
    extraction_works = test_alter_table_extraction()
    
    # 测试修复后的模式
    fixed_works = test_fixed_pattern()
    
    print("\n" + "=" * 60)
    print("问题总结和解决方案:")
    print("=" * 60)
    print("问题:")
    print("  1. 用户的SQL语句: ALTER TABLE UPP_PAYPROJECT_TEMP ALTER COLUMN ...")
    print("  2. 当前的sql_extractor.py中的ALTER TABLE模式只匹配:")
    print("     ADD, DROP, MODIFY, CHANGE, RENAME")
    print("  3. 'ALTER COLUMN'不在关键字列表中，所以无法提取表名")
    print("\n解决方案:")
    print("  1. 修改sql_extractor.py中的ALTER TABLE模式:")
    print("     将关键字列表扩展为: (?:ALTER\\s+COLUMN|ADD|DROP|MODIFY|CHANGE|RENAME|SET|$)")
    print("  2. 或者修改为更通用的模式:")
    print("     (?=\\s+(?:ALTER\\s+COLUMN|ADD|DROP|MODIFY|CHANGE|RENAME|SET|$))")
    print("\n具体修复:")
    print("  在sql_ai_analyzer/data_collector/sql_extractor.py中")
    print("  找到处理其他SQL语句类型的部分，修改ALTER TABLE模式")
    
    return extraction_works or fixed_works

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
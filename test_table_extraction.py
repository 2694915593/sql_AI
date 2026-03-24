#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试表名提取
"""

import re

def extract_table_names(sql_text: str):
    """测试表名提取函数"""
    # 移除注释
    sql_clean = re.sub(r'--.*?$|/\*.*?\*/', '', sql_text, flags=re.MULTILINE | re.DOTALL)
    
    tables = []
    
    # 提取FROM子句后的表名（改进版本）
    from_pattern = r'\bFROM\s+([\w\.]+)(?:\s+(?:AS\s+)?\w+)?(?:\s*,\s*([\w\.]+)(?:\s+(?:AS\s+)?\w+)?)*'
    from_matches = re.findall(from_pattern, sql_clean, re.IGNORECASE)
    print(f"FROM匹配: {from_matches}")
    
    for match in from_matches:
        # match可能是元组，需要处理多个表名
        for table in match:
            if table and table.strip():
                tables.append(table)
    
    # 提取JOIN子句后的表名
    join_pattern = r'\b(?:INNER\s+|LEFT\s+|RIGHT\s+|FULL\s+)?JOIN\s+([\w\.]+)(?:\s+(?:AS\s+)?\w+)?'
    join_matches = re.findall(join_pattern, sql_clean, re.IGNORECASE)
    print(f"JOIN匹配: {join_matches}")
    tables.extend(join_matches)
    
    # 清理表名
    cleaned = []
    for table in tables:
        if not table:
            continue
        
        # 移除数据库前缀（如db.table -> table）
        if '.' in table:
            table = table.split('.')[-1]
        
        # 移除引号
        table = table.strip('`\'"')
        
        # 移除空格
        table = table.strip()
        
        if table and table not in cleaned:
            cleaned.append(table)
    
    return cleaned

# 测试SQL语句
test_sqls = [
    'SELECT * FROM users WHERE id = 1',
    'SELECT u.name, o.amount FROM users u JOIN orders o ON u.id = o.user_id',
    'SELECT * FROM transaction_logs WHERE create_date > "2024-01-01"',
    'UPDATE products SET price = 200 WHERE id = 1',
    'DELETE FROM temp_logs WHERE created_at < "2024-01-01"'
]

for sql in test_sqls:
    print(f"\nSQL: {sql[:60]}..." if len(sql) > 60 else f"\nSQL: {sql}")
    tables = extract_table_names(sql)
    print(f"提取的表名: {tables}")
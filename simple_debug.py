#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单调试脚本，直接测试表名提取和参数替换
"""

import re
import sys
import os

# 直接添加路径
sys.path.append('e:/Code/sqlAnalize/sql_ai_analyzer')

# 测试表名提取
def test_table_extraction():
    print("测试表名提取")
    print("=" * 60)
    
    # 模拟sql_extractor中的表名提取逻辑
    def extract_tables_with_regex(sql_text):
        """使用正则表达式提取表名"""
        tables = []
        
        # 移除注释
        sql_clean = re.sub(r'--.*?$|/\*.*?\*/', '', sql_text, flags=re.MULTILINE | re.DOTALL)
        
        # 改进的正则表达式模式，更精确地匹配表名
        
        # 1. 提取FROM子句后的表名
        from_pattern = r'\bFROM\s+([a-zA-Z_][\w\.]*|`[^`]+`|\'[^\']+\'|"[^"]+")(?:\s+(?:AS\s+)?[a-zA-Z_]\w*)?(?=\s+(?:WHERE|JOIN|ORDER\s+BY|GROUP\s+BY|HAVING|LIMIT|;|$))'
        from_matches = re.findall(from_pattern, sql_clean, re.IGNORECASE)
        tables.extend(from_matches)
        
        # 2. 提取JOIN子句后的表名
        join_pattern = r'\b(?:INNER\s+|LEFT\s+|RIGHT\s+|FULL\s+)?JOIN\s+([a-zA-Z_][\w\.]*|`[^`]+`|\'[^\']+\'|"[^"]+")(?:\s+(?:AS\s+)?[a-zA-Z_]\w*)?(?=\s+(?:ON|WHERE|ORDER\s+BY|GROUP\s+BY|HAVING|LIMIT|;|$))'
        join_matches = re.findall(join_pattern, sql_clean, re.IGNORECASE)
        tables.extend(join_matches)
        
        # 3. 提取INSERT INTO表名
        insert_pattern = r'\bINSERT\s+(?:INTO\s+)?([a-zA-Z_][\w\.]*|`[^`]+`|\'[^\']+\'|"[^"]+")(?=\s*(?:\([^)]+\)\s+VALUES|VALUES|SELECT|;|$))'
        insert_matches = re.findall(insert_pattern, sql_clean, re.IGNORECASE)
        tables.extend(insert_matches)
        
        # 4. 提取UPDATE表名
        update_pattern = r'\bUPDATE\s+([a-zA-Z_][\w\.]*|`[^`]+`|\'[^\']+\'|"[^"]+")(?=\s+SET)'
        update_matches = re.findall(update_pattern, sql_clean, re.IGNORECASE)
        tables.extend(update_matches)
        
        # 5. 提取DELETE FROM表名
        delete_pattern = r'\bDELETE\s+(?:FROM\s+)?([a-zA-Z_][\w\.]*|`[^`]+`|\'[^\']+\'|"[^"]+")(?=\s+WHERE)'
        delete_matches = re.findall(delete_pattern, sql_clean, re.IGNORECASE)
        tables.extend(delete_matches)
        
        return tables
    
    def clean_table_names(table_names):
        """清理表名"""
        cleaned = []
        
        for table in table_names:
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
        "SELECT * FROM users WHERE id = #{id}",
        "SELECT * FROM db1.users WHERE id = #{id}",  # 带数据库前缀
        "SELECT a.*, b.name FROM table1 a JOIN table2 b ON a.id = b.ref_id WHERE a.status = #{status}",
        "INSERT INTO orders (user_id, amount) VALUES (#{user_id}, #{amount})",
        "UPDATE products SET price = #{price} WHERE category = #{category}",
        "DELETE FROM logs WHERE create_time > #{start_time}",
        "SELECT * FROM `special-table` WHERE id = #{id}",  # 带反引号的表名
        "SELECT * FROM 'another-table' WHERE id = #{id}",  # 带单引号的表名
        "WITH cte AS (SELECT * FROM temp) SELECT * FROM cte",  # CTE
        "SELECT * FROM (SELECT * FROM subquery) AS t",  # 子查询
    ]
    
    for i, sql in enumerate(test_sqls, 1):
        print(f"\n测试SQL {i}:")
        print(f"SQL: {sql[:80]}...")
        
        tables = extract_tables_with_regex(sql)
        print(f"原始提取: {tables}")
        
        cleaned = clean_table_names(tables)
        print(f"清理后: {cleaned}")
        
        # 检查问题
        for table in tables:
            if '.' in table:
                print(f"  注意: 表名 '{table}' 包含数据库前缀")
            if any(c in table for c in '`\'"'):
                print(f"  注意: 表名 '{table}' 包含引号")

def test_param_replacement():
    print("\n\n测试参数替换")
    print("=" * 60)
    
    def extract_params(sql_text):
        """提取参数"""
        param_pattern = r'#\{([^}]+)\}'
        return re.findall(param_pattern, sql_text)
    
    def replace_params(sql_text, params):
        """替换参数"""
        replaced = sql_text
        for param in params:
            # 根据参数名猜测类型
            param_lower = param.lower()
            if 'time' in param_lower or 'date' in param_lower:
                value = "'2025-01-01 00:00:00'"
            elif 'id' in param_lower or 'num' in param_lower or 'count' in param_lower:
                value = "123"
            elif 'status' in param_lower or 'flag' in param_lower:
                value = "1"
            else:
                value = "'test_value'"
            
            replaced = replaced.replace(f'#{{{param}}}', value)
        
        return replaced
    
    test_sqls = [
        "SELECT * FROM users WHERE id = #{id} AND name = #{name}",
        "UPDATE products SET price = #{price} WHERE category = #{category} AND status = #{status}",
        "INSERT INTO orders (user_id, amount, order_time) VALUES (#{user_id}, #{amount}, #{order_time})",
        "DELETE FROM logs WHERE batch_time = #{batch_time} AND start = #{start} AND end = #{end}",
    ]
    
    for i, sql in enumerate(test_sqls, 1):
        print(f"\n测试SQL {i}:")
        print(f"原始SQL: {sql}")
        
        params = extract_params(sql)
        print(f"提取参数: {params}")
        
        replaced = replace_params(sql, params)
        print(f"替换后SQL: {replaced}")
        
        # 检查语法问题
        if '#{' in replaced:
            print("  警告: 仍有未替换的参数")
        
        # 检查引号匹配
        single_quotes = replaced.count("'")
        if single_quotes % 2 != 0:
            print(f"  警告: 单引号不匹配 (共{single_quotes}个)")
        
        # 检查括号匹配
        open_paren = replaced.count('(')
        close_paren = replaced.count(')')
        if open_paren != close_paren:
            print(f"  警告: 括号不匹配 (开:{open_paren} vs 关:{close_paren})")

def test_sql_validation():
    print("\n\n测试SQL验证")
    print("=" * 60)
    
    # 一些可能有问题的SQL
    problem_sqls = [
        ("SELECT * FROM users WHERE id = #{id} AND name = '#{name}'", "参数在引号内"),
        ("SELECT * FROM users WHERE id IN (#{id1}, #{id2}, #{id3})", "IN子句中的多个参数"),
        ("UPDATE table SET col1 = #{val1}, col2 = #{val2} WHERE id = #{id}", "多个SET子句参数"),
        ("SELECT * FROM db.table WHERE id = #{id}", "带数据库前缀的表名"),
        ("SELECT * FROM `table-name` WHERE id = #{id}", "带连字符的表名"),
    ]
    
    for sql, desc in problem_sqls:
        print(f"\nSQL: {sql}")
        print(f"描述: {desc}")
        
        # 检查表名
        table_match = re.search(r'\bFROM\s+([\w\.`\'"]+)', sql, re.IGNORECASE)
        if table_match:
            table_name = table_match.group(1)
            print(f"提取的表名: {table_name}")
            
            # 检查是否有数据库前缀
            if '.' in table_name and not table_name.startswith('`') and not table_name.startswith("'") and not table_name.startswith('"'):
                # 如果包含点但不是引号开头，可能是数据库前缀
                print(f"  注意: 可能包含数据库前缀")
        
        # 检查参数替换问题
        if "'#{" in sql or '"#{' in sql:
            print(f"  警告: 参数在引号内，替换后可能产生语法错误")

def main():
    print("简单调试：表名提取和参数替换问题")
    print("=" * 60)
    
    test_table_extraction()
    test_param_replacement()
    test_sql_validation()
    
    print("\n" + "=" * 60)
    print("常见问题总结:")
    print("1. 表名包含数据库前缀（如db.table）")
    print("2. 表名包含特殊字符或引号")
    print("3. 参数在引号内（如 WHERE name = '#{name}'）")
    print("4. 复杂的SQL结构（CTE、子查询等）")
    print("5. 参数替换后SQL语法错误")
    print("\n建议:")
    print("1. 在获取执行计划前记录原始SQL和替换后的SQL")
    print("2. 验证替换后的SQL语法")
    print("3. 处理带数据库前缀的表名")
    print("4. 改进表名提取算法")

if __name__ == "__main__":
    main()
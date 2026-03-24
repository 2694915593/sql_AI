#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试执行计划获取失败的问题
分析常见错误原因
"""

import re
import sys
import os

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(current_dir, 'sql_ai_analyzer'))
sys.path.insert(0, current_dir)

from config.config_manager import ConfigManager
from data_collector.metadata_collector import MetadataCollector
from data_collector.sql_extractor import SQLExtractor
from utils.logger import setup_logger

def analyze_table_extraction():
    """分析表名提取问题"""
    print("=" * 60)
    print("分析表名提取问题")
    print("=" * 60)
    
    # 测试一些常见的SQL语句
    test_sqls = [
        "SELECT * FROM users WHERE id = #{id}",
        "SELECT a.name, b.address FROM users a LEFT JOIN addresses b ON a.id = b.user_id WHERE a.status = #{status}",
        "UPDATE products SET price = #{price} WHERE category = #{category}",
        "INSERT INTO orders (user_id, amount) VALUES (#{user_id}, #{amount})",
        "DELETE FROM logs WHERE create_time > #{start_time}",
        "WITH cte AS (SELECT * FROM temp_table) SELECT * FROM cte",
        "SELECT * FROM db1.table1 t1 INNER JOIN db2.table2 t2 ON t1.id = t2.ref_id",
    ]
    
    config = ConfigManager()
    logger = setup_logger('debug_table_extraction', {'log_level': 'DEBUG'})
    extractor = SQLExtractor(config, logger)
    
    for i, sql in enumerate(test_sqls, 1):
        print(f"\n测试SQL {i}:")
        print(f"原始SQL: {sql[:100]}...")
        
        # 使用extractor的方法提取表名
        tables = extractor.extract_table_names(sql, None)
        print(f"提取的表名: {tables}")
        
        # 使用正则表达式看看实际匹配情况
        print("正则匹配过程:")
        
        # 1. 移除注释
        sql_clean = re.sub(r'--.*?$|/\*.*?\*/', '', sql, flags=re.MULTILINE | re.DOTALL)
        
        # 2. 尝试不同的正则模式
        patterns = [
            (r'\bFROM\s+([a-zA-Z_][\w\.]*|`[^`]+`|\'[^\']+\'|"[^"]+")(?:\s+(?:AS\s+)?[a-zA-Z_]\w*)?(?=\s+(?:WHERE|JOIN|ORDER\s+BY|GROUP\s+BY|HAVING|LIMIT|;|$))', 'FROM子句'),
            (r'\b(?:INNER\s+|LEFT\s+|RIGHT\s+|FULL\s+)?JOIN\s+([a-zA-Z_][\w\.]*|`[^`]+`|\'[^\']+\'|"[^"]+")(?:\s+(?:AS\s+)?[a-zA-Z_]\w*)?(?=\s+(?:ON|WHERE|ORDER\s+BY|GROUP\s+BY|HAVING|LIMIT|;|$))', 'JOIN子句'),
            (r'\bUPDATE\s+([a-zA-Z_][\w\.]*|`[^`]+`|\'[^\']+\'|"[^"]+")(?=\s+SET)', 'UPDATE子句'),
            (r'\bINSERT\s+(?:INTO\s+)?([a-zA-Z_][\w\.]*|`[^`]+`|\'[^\']+\'|"[^"]+")(?=\s*(?:\([^)]+\)\s+VALUES|VALUES|SELECT|;|$))', 'INSERT子句'),
            (r'\bDELETE\s+(?:FROM\s+)?([a-zA-Z_][\w\.]*|`[^`]+`|\'[^\']+\'|"[^"]+")(?=\s+WHERE)', 'DELETE子句'),
        ]
        
        for pattern, desc in patterns:
            matches = re.findall(pattern, sql_clean, re.IGNORECASE)
            if matches:
                print(f"  {desc}匹配: {matches}")
        
        # 检查是否有数据库前缀
        for table in tables:
            if '.' in table:
                print(f"  警告: 表名 '{table}' 包含数据库前缀")

def analyze_param_extraction():
    """分析参数提取和替换问题"""
    print("\n" + "=" * 60)
    print("分析参数提取和替换问题")
    print("=" * 60)
    
    test_sqls = [
        "SELECT * FROM users WHERE id = #{id} AND name = #{name}",
        "SELECT * FROM orders WHERE user_id = #{user_id} AND status IN (#{status1}, #{status2})",
        "UPDATE products SET price = price * #{discount} WHERE category = #{category}",
    ]
    
    from sql_ai_analyzer.data_collector.param_extractor import ParamExtractor
    
    for i, sql in enumerate(test_sqls, 1):
        print(f"\n测试SQL {i}:")
        print(f"原始SQL: {sql}")
        
        # 使用参数提取器
        extractor = ParamExtractor(sql)
        replaced_sql, tables = extractor.generate_replaced_sql()
        
        print(f"替换后SQL: {replaced_sql}")
        print(f"提取的表名: {tables}")
        
        # 检查替换后的SQL语法
        print("语法检查:")
        # 检查是否有未替换的参数
        if '#{' in replaced_sql:
            print("  警告: 仍有未替换的参数")
        
        # 检查引号匹配
        single_quotes = replaced_sql.count("'")
        if single_quotes % 2 != 0:
            print("  警告: 单引号不匹配")
        
        # 检查括号匹配
        open_paren = replaced_sql.count('(')
        close_paren = replaced_sql.count(')')
        if open_paren != close_paren:
            print(f"  警告: 括号不匹配 ({open_paren} vs {close_paren})")

def analyze_sql_type_detection():
    """分析SQL类型检测问题"""
    print("\n" + "=" * 60)
    print("分析SQL类型检测问题")
    print("=" * 60)
    
    test_sqls = [
        ("SELECT * FROM users", "DML"),
        ("INSERT INTO users VALUES (1, 'test')", "DML"),
        ("UPDATE users SET name = 'test'", "DML"),
        ("DELETE FROM users", "DML"),
        ("CREATE TABLE users (id INT)", "DDL"),
        ("ALTER TABLE users ADD COLUMN age INT", "DDL"),
        ("DROP TABLE users", "DDL"),
        ("GRANT SELECT ON users TO user1", "DCL"),
        ("COMMIT", "TCL"),
        ("BEGIN TRANSACTION", "TCL"),
        ("WITH cte AS (SELECT * FROM t) SELECT * FROM cte", "DML"),  # WITH语句
        ("EXPLAIN SELECT * FROM users", "DML"),  # EXPLAIN语句
    ]
    
    config = ConfigManager()
    logger = setup_logger('debug_sql_type', {'log_level': 'DEBUG'})
    collector = MetadataCollector(config, logger)
    
    for sql, expected_type in test_sqls:
        sql_type = collector.detect_sql_type(sql)
        status = "✓" if sql_type == expected_type else "✗"
        print(f"{status} SQL: {sql[:50]}...")
        print(f"  检测类型: {sql_type}, 期望类型: {expected_type}")

def analyze_execution_plan_issues():
    """分析执行计划获取的常见问题"""
    print("\n" + "=" * 60)
    print("分析执行计划获取的常见问题")
    print("=" * 60)
    
    common_problems = [
        {
            "问题": "表名包含数据库前缀",
            "描述": "如 db.table 格式的表名，EXPLAIN时可能需要切换到对应数据库",
            "影响": "在错误的数据库上执行EXPLAIN会报表不存在",
            "解决方案": "提取表名时去除数据库前缀，或使用USE语句切换数据库"
        },
        {
            "问题": "参数替换不完整",
            "描述": "#{param}替换后可能产生语法错误",
            "影响": "替换后的SQL无法执行",
            "解决方案": "检查参数替换逻辑，确保替换后的SQL语法正确"
        },
        {
            "问题": "SQL类型检测错误",
            "描述": "非DML语句尝试获取执行计划",
            "影响": "不必要的错误",
            "解决方案": "优化SQL类型检测逻辑"
        },
        {
            "问题": "表名提取错误",
            "描述": "从复杂SQL中提取表名失败",
            "影响": "在错误的表上收集元数据",
            "解决方案": "改进表名提取算法"
        },
        {
            "问题": "多数据库实例混淆",
            "描述": "在找到表的实例上执行EXPLAIN，但可能连接了错误的实例",
            "影响": "表存在于实例A，但EXPLAIN在实例B执行",
            "解决方案": "确保实例索引正确传递"
        },
    ]
    
    for i, problem in enumerate(common_problems, 1):
        print(f"\n问题 {i}: {problem['问题']}")
        print(f"描述: {problem['描述']}")
        print(f"影响: {problem['影响']}")
        print(f"解决方案: {problem['解决方案']}")

def generate_test_cases():
    """生成测试用例"""
    print("\n" + "=" * 60)
    print("生成测试用例")
    print("=" * 60)
    
    print("建议测试以下场景:")
    print("1. 简单SELECT语句")
    print("2. 带JOIN的复杂查询")
    print("3. 带子查询的SQL")
    print("4. 带数据库前缀的表名")
    print("5. 带特殊字符的表名")
    print("6. 参数替换后的SQL语法")
    print("7. 不同类型的SQL语句（DDL/DML/DCL）")

def main():
    """主函数"""
    print("调试执行计划获取失败问题")
    print("=" * 60)
    
    analyze_table_extraction()
    analyze_param_extraction()
    analyze_sql_type_detection()
    analyze_execution_plan_issues()
    generate_test_cases()
    
    print("\n" + "=" * 60)
    print("总结建议:")
    print("1. 增加详细的日志记录，记录每个步骤的输入输出")
    print("2. 在获取执行计划前验证SQL语法")
    print("3. 改进表名提取算法，支持更多复杂情况")
    print("4. 添加参数替换后的SQL验证")
    print("5. 确保在多数据库场景下使用正确的实例")

if __name__ == "__main__":
    main()
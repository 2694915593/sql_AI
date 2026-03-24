#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试表名提取问题
"""

import re
from data_collector.sql_extractor import SQLExtractor
from config.config_manager import ConfigManager

def test_table_extraction():
    """测试表名提取问题"""
    print("测试表名提取问题")
    print("=" * 80)
    
    try:
        # 加载配置
        config = ConfigManager('config/config.ini')
        
        # 创建SQL提取器
        extractor = SQLExtractor(config)
        
        # 测试用例
        test_cases = [
            # 测试用例1：简单的SELECT语句
            {
                'sql': "SELECT id, name FROM users WHERE id = 1",
                'expected': ['users']
            },
            # 测试用例2：INSERT语句
            {
                'sql': "INSERT INTO ecdcdb.pd_errcode (PEC_ERRCODE, PEC_LANGUAGE) VALUES('20070004AC0010', 'zh_CN')",
                'expected': ['pd_errcode']
            },
            # 测试用例3：UPDATE语句
            {
                'sql': "UPDATE products SET price = price * 1.1 WHERE category = 'electronics'",
                'expected': ['products']
            },
            # 测试用例4：DELETE语句
            {
                'sql': "DELETE FROM orders WHERE status = 'cancelled'",
                'expected': ['orders']
            },
            # 测试用例5：带JOIN的SELECT
            {
                'sql': "SELECT u.name, o.amount FROM users u JOIN orders o ON u.id = o.user_id",
                'expected': ['users', 'orders']
            },
            # 测试用例6：带子查询
            {
                'sql': "SELECT * FROM (SELECT id, name FROM users) AS subquery",
                'expected': ['users']
            },
            # 测试用例7：带数据库前缀
            {
                'sql': "SELECT * FROM mydb.customers",
                'expected': ['customers']
            },
            # 测试用例8：带引号的表名
            {
                'sql': "SELECT * FROM `order-details`",
                'expected': ['order-details']
            },
            # 测试用例9：复杂的INSERT语句（用户提供的例子）
            {
                'sql': "INSERT INTO ecdcdb.pd_errcode (PEC_ERRCODE, PEC_LANGUAGE, PEC_SHOWMSG, PEC_INNERMSG, PEC_CLASS, PEC_LASTUPDATE) VALUES('20070004AC0010', 'zh_CN', '命中金融惩戒名单，终止交易', '命中金融惩戒名单，终止交易', '1', '2024-10-18 18:55:53.615353');",
                'expected': ['pd_errcode']
            },
            # 测试用例10：带注释的SQL
            {
                'sql': "SELECT /* 这是一个注释 */ id, name FROM users -- 另一个注释",
                'expected': ['users']
            }
        ]
        
        print("1. 测试正则表达式提取...")
        for i, test_case in enumerate(test_cases, 1):
            sql = test_case['sql']
            expected = test_case['expected']
            
            print(f"\n测试用例 {i}:")
            print(f"SQL: {sql[:50]}...")
            
            # 使用正则表达式提取
            tables = extractor._extract_tables_with_regex(sql)
            print(f"正则表达式提取结果: {tables}")
            print(f"期望结果: {expected}")
            
            if tables == expected:
                print("✓ 通过")
            else:
                print("✗ 失败")
        
        print("\n2. 测试完整的extract_table_names方法...")
        for i, test_case in enumerate(test_cases, 1):
            sql = test_case['sql']
            expected = test_case['expected']
            
            print(f"\n测试用例 {i}:")
            print(f"SQL: {sql[:50]}...")
            
            # 使用完整方法提取
            tables = extractor.extract_table_names(sql, None)
            print(f"完整方法提取结果: {tables}")
            print(f"期望结果: {expected}")
            
            if tables == expected:
                print("✓ 通过")
            else:
                print("✗ 失败")
        
        print("\n3. 分析正则表达式问题...")
        print("\n当前的正则表达式模式:")
        print("FROM模式:", r'\bFROM\s+([\w\.]+)(?:\s+(?:AS\s+)?\w+)?(?=\s+(?:WHERE|JOIN|ORDER\s+BY|GROUP\s+BY|HAVING|LIMIT|$))')
        print("JOIN模式:", r'\b(?:INNER\s+|LEFT\s+|RIGHT\s+|FULL\s+)?JOIN\s+([\w\.]+)(?:\s+(?:AS\s+)?\w+)?(?=\s+(?:ON|WHERE|ORDER\s+BY|GROUP\s+BY|HAVING|LIMIT|$))')
        print("INSERT模式:", r'\bINSERT\s+(?:INTO\s+)?([\w\.]+)(?=\s+(?:\(|VALUES|SELECT|$))')
        print("UPDATE模式:", r'\bUPDATE\s+([\w\.]+)(?=\s+(?:SET|WHERE|$))')
        print("DELETE模式:", r'\bDELETE\s+(?:FROM\s+)?([\w\.]+)(?=\s+(?:WHERE|$))')
        
        print("\n4. 测试改进的正则表达式...")
        
        # 改进的正则表达式
        def improved_extract_tables(sql_text):
            tables = []
            
            # 移除注释
            sql_clean = re.sub(r'--.*?$|/\*.*?\*/', '', sql_text, flags=re.MULTILINE | re.DOTALL)
            
            # 改进的FROM模式：只匹配表名，不匹配字段
            # 使用更精确的边界匹配
            from_pattern = r'\bFROM\s+([a-zA-Z_][\w\.]*)(?:\s+(?:AS\s+)?[a-zA-Z_]\w*)?(?=\s+(?:WHERE|JOIN|ORDER\s+BY|GROUP\s+BY|HAVING|LIMIT|;|$))'
            from_matches = re.findall(from_pattern, sql_clean, re.IGNORECASE)
            tables.extend(from_matches)
            
            # 改进的JOIN模式
            join_pattern = r'\b(?:INNER\s+|LEFT\s+|RIGHT\s+|FULL\s+)?JOIN\s+([a-zA-Z_][\w\.]*)(?:\s+(?:AS\s+)?[a-zA-Z_]\w*)?(?=\s+(?:ON|WHERE|ORDER\s+BY|GROUP\s+BY|HAVING|LIMIT|;|$))'
            join_matches = re.findall(join_pattern, sql_clean, re.IGNORECASE)
            tables.extend(join_matches)
            
            # 改进的INSERT模式：确保只匹配表名，不匹配字段列表
            insert_pattern = r'\bINSERT\s+(?:INTO\s+)?([a-zA-Z_][\w\.]*)(?=\s*(?:\([^)]+\)\s+VALUES|VALUES|SELECT|;|$))'
            insert_matches = re.findall(insert_pattern, sql_clean, re.IGNORECASE)
            tables.extend(insert_matches)
            
            # 改进的UPDATE模式
            update_pattern = r'\bUPDATE\s+([a-zA-Z_][\w\.]*)(?=\s+SET)'
            update_matches = re.findall(update_pattern, sql_clean, re.IGNORECASE)
            tables.extend(update_matches)
            
            # 改进的DELETE模式
            delete_pattern = r'\bDELETE\s+(?:FROM\s+)?([a-zA-Z_][\w\.]*)(?=\s+WHERE)'
            delete_matches = re.findall(delete_pattern, sql_clean, re.IGNORECASE)
            tables.extend(delete_matches)
            
            return tables
        
        print("\n使用改进的正则表达式测试:")
        for i, test_case in enumerate(test_cases, 1):
            sql = test_case['sql']
            expected = test_case['expected']
            
            tables = improved_extract_tables(sql)
            cleaned_tables = extractor._clean_table_names(tables)
            
            print(f"\n测试用例 {i}:")
            print(f"SQL: {sql[:50]}...")
            print(f"改进正则提取结果: {cleaned_tables}")
            print(f"期望结果: {expected}")
            
            if cleaned_tables == expected:
                print("✓ 通过")
            else:
                print("✗ 失败")
        
        print("\n" + "=" * 80)
        print("测试完成")
        
    except Exception as e:
        print(f"测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_table_extraction()
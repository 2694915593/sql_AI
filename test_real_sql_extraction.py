#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试真实SQL语句的表名提取
"""

from data_collector.sql_extractor import SQLExtractor
from config.config_manager import ConfigManager

def test_real_sql_extraction():
    """测试真实SQL语句的表名提取"""
    print("测试真实SQL语句的表名提取")
    print("=" * 80)
    
    try:
        # 加载配置
        config = ConfigManager('config/config.ini')
        
        # 创建SQL提取器
        extractor = SQLExtractor(config)
        
        # 从数据库获取真实的SQL语句进行测试
        print("1. 从数据库获取真实的SQL语句...")
        sql_records = extractor.get_pending_sqls(limit=5)
        
        if not sql_records:
            print("没有待分析SQL，创建测试数据...")
            # 创建测试SQL语句
            test_sqls = [
                {
                    'sql_text': "INSERT INTO ecdcdb.pd_errcode (PEC_ERRCODE, PEC_LANGUAGE, PEC_SHOWMSG, PEC_INNERMSG, PEC_CLASS, PEC_LASTUPDATE) VALUES('20070004AC0010', 'zh_CN', '命中金融惩戒名单，终止交易', '命中金融惩戒名单，终止交易', '1', '2024-10-18 18:55:53.615353');",
                    'table_name': "pd_errcode"
                },
                {
                    'sql_text': "UPDATE products SET price = price * 1.1 WHERE category = 'electronics'",
                    'table_name': "products"
                },
                {
                    'sql_text': "SELECT u.name, o.amount FROM users u JOIN orders o ON u.id = o.user_id",
                    'table_name': "users,orders"
                },
                {
                    'sql_text': "DELETE FROM orders WHERE status = 'cancelled'",
                    'table_name': "orders"
                }
            ]
            
            for i, test_sql in enumerate(test_sqls, 1):
                print(f"\n测试SQL {i}:")
                print(f"SQL: {test_sql['sql_text'][:50]}...")
                print(f"期望表名: {test_sql['table_name']}")
                
                # 提取表名
                tables = extractor.extract_table_names(test_sql['sql_text'], test_sql.get('table_name'))
                print(f"提取到的表名: {tables}")
                
                # 验证结果
                expected_tables = [t.strip() for t in test_sql['table_name'].split(',')]
                if set(tables) == set(expected_tables):
                    print("✓ 通过")
                else:
                    print("✗ 失败")
                    print(f"期望: {expected_tables}")
                    print(f"实际: {tables}")
        else:
            for i, record in enumerate(sql_records, 1):
                sql_text = record.get('sql_text', '')
                table_name_field = record.get('table_name', '')
                
                print(f"\nSQL记录 {i} (ID: {record.get('id')}):")
                print(f"SQL: {sql_text[:50]}...")
                print(f"TABLENAME字段: {table_name_field}")
                
                # 提取表名
                tables = extractor.extract_table_names(sql_text, table_name_field)
                print(f"提取到的表名: {tables}")
                
                # 分析提取结果
                if tables:
                    print("✓ 成功提取到表名")
                else:
                    print("✗ 未提取到表名")
        
        print("\n2. 测试特定问题SQL...")
        problem_sqls = [
            # 问题1：带数据库前缀的表名
            {
                'sql': "SELECT * FROM mydb.customers WHERE id = 1",
                'expected': ['customers'],
                'description': '带数据库前缀的表名'
            },
            # 问题2：带引号的表名
            {
                'sql': "SELECT * FROM `order-details` WHERE status = 'active'",
                'expected': ['order-details'],
                'description': '带反引号的表名'
            },
            # 问题3：带单引号的表名
            {
                'sql': "SELECT * FROM 'special-table' WHERE id = 1",
                'expected': ['special-table'],
                'description': '带单引号的表名'
            },
            # 问题4：带双引号的表名
            {
                'sql': 'SELECT * FROM "another-table" WHERE id = 1',
                'expected': ['another-table'],
                'description': '带双引号的表名'
            },
            # 问题5：INSERT语句带字段列表
            {
                'sql': "INSERT INTO users (id, name, email) VALUES (1, 'John', 'john@example.com')",
                'expected': ['users'],
                'description': 'INSERT语句带字段列表'
            },
            # 问题6：用户提供的实际SQL
            {
                'sql': "INSERT INTO ecdcdb.pd_errcode (PEC_ERRCODE, PEC_LANGUAGE, PEC_SHOWMSG, PEC_INNERMSG, PEC_CLASS, PEC_LASTUPDATE) VALUES('20070004AC0010', 'zh_CN', '命中金融惩戒名单，终止交易', '命中金融惩戒名单，终止交易', '1', '2024-10-18 18:55:53.615353');",
                'expected': ['pd_errcode'],
                'description': '用户提供的实际SQL'
            }
        ]
        
        for i, test_case in enumerate(problem_sqls, 1):
            print(f"\n问题测试 {i}: {test_case['description']}")
            print(f"SQL: {test_case['sql'][:50]}...")
            
            # 提取表名
            tables = extractor.extract_table_names(test_case['sql'], None)
            print(f"提取到的表名: {tables}")
            print(f"期望表名: {test_case['expected']}")
            
            if tables == test_case['expected']:
                print("✓ 通过")
            else:
                print("✗ 失败")
                
                # 调试信息
                print("\n调试信息:")
                # 测试正则表达式提取
                regex_tables = extractor._extract_tables_with_regex(test_case['sql'])
                print(f"正则表达式提取: {regex_tables}")
                
                # 测试sqlparse提取
                sqlparse_tables = extractor._extract_tables_with_sqlparse(test_case['sql'])
                print(f"sqlparse提取: {sqlparse_tables}")
                
                # 测试清理函数
                cleaned = extractor._clean_table_names(regex_tables + sqlparse_tables)
                print(f"清理后: {cleaned}")
        
        print("\n3. 分析问题原因...")
        print("\n当前的正则表达式可能的问题:")
        print("1. 对于带数据库前缀的表名（如mydb.customers），正则表达式可能匹配失败")
        print("2. 对于带引号的表名，需要特殊处理")
        print("3. 子查询中的表名提取需要特殊逻辑")
        
        print("\n" + "=" * 80)
        print("测试完成")
        
    except Exception as e:
        print(f"测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_real_sql_extraction()
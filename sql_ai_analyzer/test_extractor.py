#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试SQL提取器
"""

import logging
import sqlparse
from typing import List

def test_sql_extractor():
    """测试SQL提取器"""
    # 创建简单的日志记录器
    logger = logging.getLogger('test')
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(handler)
    
    # 模拟配置管理器
    class MockConfig:
        def get_database_config(self):
            return {
                'host': 'localhost',
                'port': 3306,
                'database': 'testdb',
                'username': 'root',
                'password': 'password',
                'db_type': 'mysql'
            }
    
    # 模拟SQL提取器，只测试表名提取功能
    class MockSQLExtractor:
        def __init__(self, config, logger):
            self.config = config
            self.logger = logger
        
        def extract_table_names(self, sql: str) -> List[str]:
            """从SQL语句中提取表名"""
            try:
                parsed = sqlparse.parse(sql)
                if not parsed:
                    return []
                
                tables = []
                for statement in parsed:
                    # 使用sqlparse提取表名
                    for token in statement.tokens:
                        if token.is_keyword and token.value.upper() in ['FROM', 'JOIN', 'INTO', 'UPDATE']:
                            # 获取下一个token，可能是表名
                            self._extract_tables_from_token(token, tables)
                
                # 清理表名
                cleaned_tables = self._clean_table_names(tables)
                self.logger.debug(f"从SQL中提取表名: {sql[:50]}... -> {cleaned_tables}")
                return cleaned_tables
                
            except Exception as e:
                self.logger.error(f"提取表名时发生错误: {str(e)}", exc_info=True)
                return []
        
        def _extract_tables_from_token(self, token, tables):
            """从token中提取表名"""
            # 简化实现：查找标识符token
            idx = token.parent.tokens.index(token)
            for i in range(idx + 1, len(token.parent.tokens)):
                next_token = token.parent.tokens[i]
                if next_token.ttype is None or next_token.ttype.is_keyword:
                    break
                if next_token.ttype and next_token.ttype.is_group:
                    # 处理括号内的内容
                    for sub_token in next_token.tokens:
                        if sub_token.ttype and sub_token.ttype.is_group:
                            continue
                        if sub_token.value and sub_token.value.strip():
                            tables.append(sub_token.value.strip())
                elif next_token.value and next_token.value.strip():
                    tables.append(next_token.value.strip())
        
        def _clean_table_names(self, tables: List[str]) -> List[str]:
            """清理表名"""
            cleaned = []
            for table in tables:
                if not table or table.upper() in ['SELECT', 'WHERE', 'SET', 'VALUES', 'ON']:
                    continue
                
                # 移除数据库前缀、引号、空格
                table = table.strip()
                if '.' in table:
                    table = table.split('.')[-1]
                table = table.strip('`\'"')
                
                if table and table not in cleaned:
                    cleaned.append(table)
            
            return cleaned
    
    config = MockConfig()
    extractor = MockSQLExtractor(config, logger)
    
    # 测试表名提取
    test_sqls = [
        'SELECT * FROM users WHERE id = 1',
        'SELECT u.name, o.amount FROM users u JOIN orders o ON u.id = o.user_id',
        'INSERT INTO products (name, price) VALUES ("test", 100)',
        'UPDATE products SET price = 200 WHERE id = 1',
        'DELETE FROM temp_logs WHERE created_at < "2024-01-01"'
    ]
    
    for sql in test_sqls:
        tables = extractor.extract_table_names(sql)
        print(f'SQL: {sql[:50]}...' if len(sql) > 50 else f'SQL: {sql}')
        print(f'  提取的表名: {tables}')
        print()

if __name__ == '__main__':
    test_sql_extractor()
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Shell脚本SQL提取器测试
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_collector.shell_sql_extractor import ShellScriptSQLExtractor, extract_sql_from_shell_content


class TestShellScriptSQLExtractor:
    """Shell脚本SQL提取器测试类"""
    
    def setup_method(self):
        """测试初始化"""
        self.extractor = ShellScriptSQLExtractor()
    
    def test_mysql_e_option(self):
        """测试mysql -e选项"""
        shell_content = """#!/bin/bash
mysql -e "SELECT * FROM users WHERE id = 1;"
mysql --execute "UPDATE users SET name='test' WHERE id=2;"
"""
        results = self.extractor.extract_sql_from_content(shell_content)
        assert len(results) == 2
        assert "SELECT * FROM users" in results[0]['sql']
        assert "UPDATE users SET name='test'" in results[1]['sql']
    
    def test_psql_c_option(self):
        """测试psql -c选项"""
        shell_content = """#!/bin/bash
psql -c "SELECT * FROM customers;"
psql --command "INSERT INTO orders VALUES (1, 'test');"
"""
        results = self.extractor.extract_sql_from_content(shell_content)
        assert len(results) == 2
        assert "SELECT * FROM customers" in results[0]['sql']
        assert "INSERT INTO orders VALUES" in results[1]['sql']
    
    def test_heredoc_mysql(self):
        """测试mysql here文档"""
        shell_content = """#!/bin/bash
mysql << EOF
SELECT * FROM products;
UPDATE products SET price = 100 WHERE id = 1;
EOF
"""
        results = self.extractor.extract_sql_from_content(shell_content)
        assert len(results) == 2
        assert "SELECT * FROM products" in results[0]['sql']
        assert "UPDATE products SET price = 100" in results[1]['sql']
    
    def test_heredoc_sqlplus(self):
        """测试sqlplus here文档"""
        shell_content = """#!/bin/bash
sqlplus user/pass@db << SQL
SELECT * FROM employees;
COMMIT;
SQL
"""
        results = self.extractor.extract_sql_from_content(shell_content)
        assert len(results) >= 1
        assert "SELECT * FROM employees" in results[0]['sql']
    
    def test_variable_assignment(self):
        """测试变量赋值中的SQL"""
        shell_content = '''#!/bin/bash
SQL_QUERY="SELECT * FROM transactions WHERE amount > 1000;"
ANOTHER_SQL='INSERT INTO logs (message) VALUES ("test");'
'''
        results = self.extractor.extract_sql_from_content(shell_content)
        assert len(results) == 2
        assert "SELECT * FROM transactions" in results[0]['sql']
        assert "INSERT INTO logs" in results[1]['sql']
    
    def test_pipe_commands(self):
        """测试管道命令"""
        shell_content = '''#!/bin/bash
echo "SELECT * FROM inventory;" | mysql
cat query.sql | psql
'''
        results = self.extractor.extract_sql_from_content(shell_content)
        assert len(results) >= 1
        assert "SELECT * FROM inventory" in results[0]['sql']
    
    def test_multiline_sql(self):
        """测试多行SQL语句"""
        shell_content = '''#!/bin/bash
mysql -e "SELECT * FROM users
WHERE status = 'active'
ORDER BY created_at DESC;"
'''
        results = self.extractor.extract_sql_from_content(shell_content)
        assert len(results) == 1
        sql = results[0]['sql']
        assert "SELECT * FROM users" in sql
        assert "WHERE status = 'active'" in sql
        assert "ORDER BY created_at DESC" in sql
    
    def test_complex_shell_script(self):
        """测试复杂的shell脚本"""
        shell_content = '''#!/bin/bash
# 这是一个复杂的shell脚本示例
DB_HOST="localhost"
DB_USER="root"
DB_PASS="password"

# 使用变量
QUERY="SELECT COUNT(*) as total FROM users WHERE status = 'active';"

# 执行查询
mysql -h $DB_HOST -u $DB_USER -p$DB_PASS -e "$QUERY"

# here文档用于批量操作
mysql -h $DB_HOST -u $DB_USER -p$DB_PASS << BATCH_SQL
UPDATE users SET last_login = NOW() WHERE status = 'active';
DELETE FROM sessions WHERE expires_at < NOW();
BATCH_SQL

# 管道示例
echo "SHOW TABLES;" | mysql -h $DB_HOST -u $DB_USER -p$DB_PASS
'''
        results = self.extractor.extract_sql_from_content(shell_content)
        assert len(results) >= 3
        sql_texts = [r['sql'] for r in results]
        
        # 检查是否提取到所有SQL
        assert any("SELECT COUNT(*) as total FROM users" in sql for sql in sql_texts)
        assert any("UPDATE users SET last_login = NOW()" in sql for sql in sql_texts)
        assert any("DELETE FROM sessions WHERE expires_at < NOW()" in sql for sql in sql_texts)
        assert any("SHOW TABLES" in sql for sql in sql_texts)
    
    def test_invalid_sql(self):
        """测试无效SQL过滤"""
        shell_content = '''#!/bin/bash
# 这不是SQL
echo "Hello World"
ls -la
# 这是SQL
mysql -e "SELECT * FROM users;"
# 这看起来像SQL但不是
FAKE="This is not a SQL statement"
'''
        results = self.extractor.extract_sql_from_content(shell_content)
        assert len(results) == 1
        assert "SELECT * FROM users" in results[0]['sql']
    
    def test_sql_with_special_chars(self):
        """测试包含特殊字符的SQL"""
        shell_content = '''#!/bin/bash
mysql -e "SELECT * FROM `user-table` WHERE name = 'O\\'Reilly';"
psql -c "SELECT * FROM "public"."users" WHERE email LIKE '%@test.com';"
'''
        results = self.extractor.extract_sql_from_content(shell_content)
        assert len(results) >= 1
    
    def test_extract_from_file(self, tmp_path):
        """测试从文件提取SQL"""
        shell_script = tmp_path / "test.sh"
        shell_content = '''#!/bin/bash
mysql -e "SELECT * FROM test_table;"
'''
        shell_script.write_text(shell_content, encoding='utf-8')
        
        results = self.extractor.extract_sql_from_file(str(shell_script))
        assert len(results) == 1
        assert "SELECT * FROM test_table" in results[0]['sql']
        assert results[0]['source'] == str(shell_script)
    
    def test_convenience_functions(self):
        """测试便捷函数"""
        shell_content = '''mysql -e "SELECT * FROM users;"'''
        results = extract_sql_from_shell_content(shell_content)
        assert len(results) == 1
        assert "SELECT * FROM users" in results[0]['sql']


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试修复后的ALTER TABLE语句表名提取
验证修复后的sql_extractor.py是否能正确提取UPP_PAYPROJECT_TEMP表名
"""

import sys
import os

# 添加路径
sys.path.append('e:/Code/sqlAnalize/sql_ai_analyzer')

def test_alter_table_fixed():
    """测试修复后的ALTER TABLE表名提取"""
    print("测试修复后的ALTER TABLE语句表名提取")
    print("=" * 60)
    
    # 用户提供的SQL
    sql = "alter table UPP_PAYPROJECT_TEMP alter column PPJT_PROJECTID_ID set generated always as identity(start with 13008,INCREMENT BY 1);"
    
    print(f"SQL语句: {sql}")
    
    # 创建模拟配置和日志
    class MockConfig:
        def get_database_config(self):
            return {
                'host': 'localhost',
                'port': 3306,
                'database': 'test_db',
                'username': 'root',
                'password': '123456',
                'db_type': 'mysql'
            }
    
    class MockLogger:
        def info(self, msg): pass
        def debug(self, msg): pass
        def error(self, msg): pass
        def warning(self, msg): pass
        def setLevel(self, level): pass
    
    try:
        from sql_ai_analyzer.data_collector.sql_extractor import SQLExtractor
        
        print("尝试导入SQLExtractor...")
        
        # 由于我们不需要真实的数据库连接，我们可以直接测试提取表名的方法
        # 先创建一个简单的测试类来避免数据库连接错误
        class TestSQLExtractor(SQLExtractor):
            def __init__(self, config_manager, logger=None):
                # 跳过父类的数据库初始化
                self.config_manager = config_manager
                if logger:
                    self.set_logger(logger)
                else:
                    self.logger = MockLogger()
        
        config = MockConfig()
        logger = MockLogger()
        
        print("创建TestSQLExtractor实例...")
        
        # 直接测试提取表名逻辑
        print("\n直接测试提取表名逻辑:")
        print("-" * 40)
        
        # 创建一个简化的提取器实例，只用于测试提取方法
        extractor = TestSQLExtractor(config, logger)
        
        # 直接调用提取表名方法
        tables = extractor.extract_table_names(sql)
        print(f"提取到的表名: {tables}")
        
        expected_tables = ['UPP_PAYPROJECT_TEMP']
        
        if tables == expected_tables:
            print("✓ 修复成功！正确提取到表名: UPP_PAYPROJECT_TEMP")
            return True
        else:
            print("✗ 提取失败")
            print(f"  提取: {tables}")
            print(f"  预期: {expected_tables}")
            return False
            
    except Exception as e:
        print(f"测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_other_alter_table_variants():
    """测试其他ALTER TABLE变体"""
    print("\n" + "=" * 60)
    print("测试其他ALTER TABLE变体")
    print("=" * 60)
    
    test_cases = [
        ("ALTER TABLE table1 ADD COLUMN col1 INT", ['table1']),
        ("ALTER TABLE table1 DROP COLUMN col1", ['table1']),
        ("ALTER TABLE table1 MODIFY COLUMN col1 VARCHAR(100)", ['table1']),
        ("ALTER TABLE table1 CHANGE COLUMN old_name new_name INT", ['table1']),
        ("ALTER TABLE table1 RENAME TO table2", ['table1']),
        ("ALTER TABLE table1 SET option=value", ['table1']),
        ("ALTER TABLE `table-name` ADD COLUMN col1 INT", ['`table-name`']),
        ("ALTER TABLE 'table-name' ADD COLUMN col1 INT", ["'table-name'"]),
        ("ALTER TABLE \"table-name\" ADD COLUMN col1 INT", ['"table-name"']),
        ("ALTER TABLE db.table_name ADD COLUMN col1 INT", ['db.table_name']),
        ("ALTER TABLE schema.table_name ALTER COLUMN col1 SET DEFAULT 0", ['schema.table_name']),
    ]
    
    # 创建一个模拟的extractor
    class MockConfig:
        def get_database_config(self):
            return {}
    
    class MockLogger:
        def info(self, msg): pass
        def debug(self, msg): pass
        def error(self, msg): pass
        def warning(self, msg): pass
        def setLevel(self, level): pass
    
    try:
        from sql_ai_analyzer.data_collector.sql_extractor import SQLExtractor
        
        class TestSQLExtractor(SQLExtractor):
            def __init__(self, config_manager, logger=None):
                self.config_manager = config_manager
                if logger:
                    self.set_logger(logger)
                else:
                    self.logger = MockLogger()
        
        config = MockConfig()
        logger = MockLogger()
        extractor = TestSQLExtractor(config, logger)
        
        all_passed = True
        
        for i, (sql, expected) in enumerate(test_cases, 1):
            tables = extractor.extract_table_names(sql)
            if tables == expected:
                print(f"✓ 测试 {i}: {sql[:40]}...: 通过")
            else:
                print(f"✗ 测试 {i}: {sql[:40]}...: 失败")
                print(f"  提取: {tables}, 预期: {expected}")
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_regular_sql_after_fix():
    """测试修复后普通SQL的提取是否仍然正常工作"""
    print("\n" + "=" * 60)
    print("测试修复后普通SQL的提取")
    print("=" * 60)
    
    test_cases = [
        ("SELECT * FROM users WHERE id = 1", ['users']),
        ("SELECT a.*, b.* FROM table1 a, table2 b", ['table1', 'table2']),
        ("INSERT INTO logs (id, message) VALUES (1, 'test')", ['logs']),
        ("UPDATE products SET price = 100 WHERE id = 1", ['products']),
        ("DELETE FROM customers WHERE id = 1", ['customers']),
        ("CREATE TABLE new_table (id INT)", ['new_table']),
        ("DROP TABLE old_table", ['old_table']),
        ("TRUNCATE TABLE temp_table", ['temp_table']),
    ]
    
    # 创建一个模拟的extractor
    class MockConfig:
        def get_database_config(self):
            return {}
    
    class MockLogger:
        def info(self, msg): pass
        def debug(self, msg): pass
        def error(self, msg): pass
        def warning(self, msg): pass
        def setLevel(self, level): pass
    
    try:
        from sql_ai_analyzer.data_collector.sql_extractor import SQLExtractor
        
        class TestSQLExtractor(SQLExtractor):
            def __init__(self, config_manager, logger=None):
                self.config_manager = config_manager
                if logger:
                    self.set_logger(logger)
                else:
                    self.logger = MockLogger()
        
        config = MockConfig()
        logger = MockLogger()
        extractor = TestSQLExtractor(config, logger)
        
        all_passed = True
        
        for i, (sql, expected) in enumerate(test_cases, 1):
            tables = extractor.extract_table_names(sql)
            # 排序后比较，因为顺序可能不同
            if sorted(tables) == sorted(expected):
                print(f"✓ 测试 {i}: {sql[:40]}...: 通过")
            else:
                print(f"✗ 测试 {i}: {sql[:40]}...: 失败")
                print(f"  提取: {tables}, 预期: {expected}")
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("测试修复后的ALTER TABLE语句表名提取")
    print("=" * 60)
    
    # 测试主要的ALTER TABLE修复
    main_fixed = test_alter_table_fixed()
    
    # 测试其他ALTER TABLE变体
    other_variants = test_other_alter_table_variants()
    
    # 测试普通SQL仍然正常工作
    regular_sql = test_regular_sql_after_fix()
    
    print("\n" + "=" * 60)
    print("测试总结:")
    print("=" * 60)
    print(f"主要ALTER TABLE修复: {'通过' if main_fixed else '失败'}")
    print(f"其他ALTER TABLE变体: {'通过' if other_variants else '失败'}")
    print(f"普通SQL提取功能: {'通过' if regular_sql else '失败'}")
    
    all_passed = main_fixed and other_variants and regular_sql
    
    if all_passed:
        print("\n✓ 所有测试通过！ALTER TABLE语句表名提取已成功修复")
        print("\n修复内容:")
        print("1. 修改了sql_extractor.py中的ALTER TABLE模式")
        print("2. 扩展了关键字列表: (?:ALTER\\s+COLUMN|ADD|DROP|MODIFY|CHANGE|RENAME|SET|$)")
        print("3. 现在支持: ALTER TABLE ... ALTER COLUMN ... 格式")
        print("4. 保持向后兼容性，其他SQL语句提取不受影响")
    else:
        print("\n✗ 部分测试失败")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
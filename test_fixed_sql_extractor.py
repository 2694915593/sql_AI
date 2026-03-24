#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试修复后的SQL表名提取器
验证修复后的正则表达式是否能正确处理复杂SQL
"""

import sys
import os

# 添加路径
sys.path.append('e:/Code/sqlAnalize/sql_ai_analyzer')

def test_fixed_extractor():
    """测试修复后的提取器"""
    print("测试修复后的SQL表名提取器")
    print("=" * 60)
    
    # 用户提供的复杂SQL
    test_sql = """SELECT * FROM( SELECT ROW_NUMBER() OVER(ORDER BY EVI_PLATENUM DESC) AS ROW_ID, EVI_PLATENUM, EVC_VIN, EVC_VEHICLETYPE, EVC_USECHARACTER, EVI_TYPE, EOI_PHONE, EOI_ADDR FROM ETC_AGREEMENTINFO JOIN ETC_VEHICLE_INFO ON EAI_VEHICLEID = EVI_VEHICLEID JOIN ETC_ORDER_INFO ON EAI_VEHICLEID = EOI_VEHICLEID LEFT JOIN ETC_VEHICLE_CERTIFY ON EAI_VEHICLEID = EVC_VEHICLEID WHERE EAI_SIGNSTT = '1' AND EAI_ISRELEVANCEFLG = 'Y' AND EAI_CARDCTFTNO = #{CERTNO} ) AS TEMP WHERE TEMP.ROW_ID BETWEEN #{FROMINDEX} AND #{TOINDEX}"""
    
    print(f"测试SQL (前200字符):")
    print(test_sql[:200] + "...")
    print()
    
    # 尝试导入并使用修复后的提取器
    try:
        from sql_ai_analyzer.data_collector.sql_extractor import SQLExtractor
        
        # 创建模拟配置和日志
        class MockConfig:
            def get_database_config(self):
                return {'host': 'localhost', 'port': 3306, 'database': 'test', 'username': 'root', 'password': '123456', 'db_type': 'mysql'}
        
        class MockLogger:
            def info(self, msg): 
                print(f"[INFO] {msg}")
            def debug(self, msg): 
                pass
            def error(self, msg): 
                print(f"[ERROR] {msg}")
            def warning(self, msg): 
                print(f"[WARNING] {msg}")
            def setLevel(self, level): 
                pass
        
        config = MockConfig()
        logger = MockLogger()
        
        print("创建SQLExtractor实例...")
        extractor = SQLExtractor(config, logger)
        
        print("提取表名...")
        tables = extractor.extract_table_names(test_sql)
        
        print(f"提取的表名: {tables}")
        
        expected_tables = ['ETC_AGREEMENTINFO', 'ETC_VEHICLE_INFO', 'ETC_ORDER_INFO', 'ETC_VEHICLE_CERTIFY']
        print(f"期望的表名: {expected_tables}")
        
        missing = [t for t in expected_tables if t not in tables]
        extra = [t for t in tables if t not in expected_tables]
        
        if missing:
            print(f"缺失的表名: {missing}")
        if extra:
            print(f"额外的表名: {extra}")
        
        if not missing and not extra:
            print("✓ 所有表名正确提取")
            return True
        else:
            print("✗ 表名提取不完整")
            return False
            
    except Exception as e:
        print(f"测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_various_sql_cases():
    """测试各种SQL案例"""
    print("\n" + "=" * 60)
    print("测试各种SQL案例")
    print("=" * 60)
    
    test_cases = [
        {
            'name': '复杂子查询SQL',
            'sql': """SELECT * FROM( SELECT ROW_NUMBER() OVER(ORDER BY EVI_PLATENUM DESC) AS ROW_ID, EVI_PLATENUM, EVC_VIN, EVC_VEHICLETYPE, EVC_USECHARACTER, EVI_TYPE, EOI_PHONE, EOI_ADDR FROM ETC_AGREEMENTINFO JOIN ETC_VEHICLE_INFO ON EAI_VEHICLEID = EVI_VEHICLEID JOIN ETC_ORDER_INFO ON EAI_VEHICLEID = EOI_VEHICLEID LEFT JOIN ETC_VEHICLE_CERTIFY ON EAI_VEHICLEID = EVC_VEHICLEID WHERE EAI_SIGNSTT = '1' AND EAI_ISRELEVANCEFLG = 'Y' AND EAI_CARDCTFTNO = #{CERTNO} ) AS TEMP WHERE TEMP.ROW_ID BETWEEN #{FROMINDEX} AND #{TOINDEX}""",
            'expected': ['ETC_AGREEMENTINFO', 'ETC_VEHICLE_INFO', 'ETC_ORDER_INFO', 'ETC_VEHICLE_CERTIFY']
        },
        {
            'name': '简单SELECT',
            'sql': "SELECT * FROM users WHERE id = #{id}",
            'expected': ['users']
        },
        {
            'name': '多表JOIN',
            'sql': "SELECT a.*, b.name FROM table1 a JOIN table2 b ON a.id = b.ref_id JOIN table3 c ON b.id = c.table2_id",
            'expected': ['table1', 'table2', 'table3']
        },
        {
            'name': 'INSERT语句',
            'sql': "INSERT INTO users (id, name, email) VALUES (#{id}, #{name}, #{email})",
            'expected': ['users']
        },
        {
            'name': 'UPDATE语句',
            'sql': "UPDATE products SET price = #{price} WHERE id = #{id}",
            'expected': ['products']
        },
        {
            'name': 'DELETE语句',
            'sql': "DELETE FROM logs WHERE batch_time = #{batch_time}",
            'expected': ['logs']
        },
        {
            'name': '带数据库前缀',
            'sql': "SELECT * FROM db1.users JOIN db2.orders ON users.id = orders.user_id",
            'expected': ['db1.users', 'db2.orders']
        }
    ]
    
    all_passed = True
    
    for test_case in test_cases:
        print(f"\n测试: {test_case['name']}")
        print(f"SQL: {test_case['sql'][:80]}...")
        
        # 使用正则表达式直接测试
        import re
        
        sql_clean = re.sub(r'--.*?$|/\*.*?\*/', '', test_case['sql'], flags=re.MULTILINE | re.DOTALL)
        
        # 修复后的正则表达式
        patterns = [
            # FROM模式（排除 FROM( 情况）
            r'\bFROM\s+(?!\()([a-zA-Z_][\w\.]*|`[^`]+`|\'[^\']+\'|"[^"]+")(?:\s+(?:AS\s+)?[a-zA-Z_]\w*)?(?=\s+(?:WHERE|JOIN|ORDER\s+BY|GROUP\s+BY|HAVING|LIMIT|;|$))',
            # 子查询中的FROM
            r'FROM\s*\(.*?FROM\s+([a-zA-Z_][\w\.]*|`[^`]+`|\'[^\']+\'|"[^"]+")(?:\s+(?:AS\s+)?[a-zA-Z_]\w*)?(?=\s+(?:WHERE|JOIN|ORDER\s+BY|GROUP\s+BY|HAVING|LIMIT|;|$))',
            # JOIN模式
            r'\b(?:INNER\s+|LEFT\s+|RIGHT\s+|FULL\s+)?JOIN\s+([a-zA-Z_][\w\.]*|`[^`]+`|\'[^\']+\'|"[^"]+")(?:\s+(?:AS\s+)?[a-zA-Z_]\w*)?(?=\s+(?:ON|WHERE|ORDER\s+BY|GROUP\s+BY|HAVING|LIMIT|;|$))',
            # INSERT模式
            r'\bINSERT\s+(?:INTO\s+)?([a-zA-Z_][\w\.]*|`[^`]+`|\'[^\']+\'|"[^"]+")(?=\s*(?:\([^)]+\)\s+VALUES|VALUES|SELECT|;|$))',
            # UPDATE模式
            r'\bUPDATE\s+([a-zA-Z_][\w\.]*|`[^`]+`|\'[^\']+\'|"[^"]+")(?=\s+SET)',
            # DELETE模式
            r'\bDELETE\s+(?:FROM\s+)?([a-zA-Z_][\w\.]*|`[^`]+`|\'[^\']+\'|"[^"]+")(?=\s+WHERE)',
        ]
        
        tables = set()
        for pattern in patterns:
            matches = re.findall(pattern, sql_clean, re.IGNORECASE)
            for match in matches:
                # 清理表名（移除引号）
                table = match.strip()
                if (table.startswith('`') and table.endswith('`')) or \
                   (table.startswith("'") and table.endswith("'")) or \
                   (table.startswith('"') and table.endswith('"')):
                    table = table[1:-1]
                tables.add(table)
        
        print(f"提取结果: {sorted(tables)}")
        print(f"期望结果: {test_case['expected']}")
        
        missing = [t for t in test_case['expected'] if t not in tables]
        extra = [t for t in tables if t not in test_case['expected']]
        
        if not missing and not extra:
            print("✓ 通过")
        else:
            print("✗ 失败")
            if missing:
                print(f"  缺失: {missing}")
            if extra:
                print(f"  多余: {extra}")
            all_passed = False
    
    return all_passed

def main():
    """主函数"""
    print("验证修复后的SQL表名提取器")
    print("=" * 60)
    
    try:
        # 测试修复后的提取器
        test1_passed = test_fixed_extractor()
        
        # 测试各种SQL案例
        test2_passed = test_various_sql_cases()
        
        print("\n" + "=" * 60)
        print("测试总结:")
        print(f"修复后提取器测试: {'通过' if test1_passed else '失败'}")
        print(f"各种SQL案例测试: {'通过' if test2_passed else '失败'}")
        
        if test1_passed and test2_passed:
            print("\n✓ 所有测试通过!")
            print("修复成功，表名提取器现在可以正确处理复杂SQL")
        else:
            print("\n✗ 部分测试失败，需要进一步调试")
        
        return test1_passed and test2_passed
        
    except Exception as e:
        print(f"\n测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
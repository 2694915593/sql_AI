#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试最终修复的表名提取器
验证修复后的方法是否能正确处理用户提供的三条SQL
"""

import sys
import os

# 添加路径
sys.path.append('e:/Code/sqlAnalize/sql_ai_analyzer')

def test_user_sqls():
    """测试用户提供的三条SQL"""
    print("测试用户提供的三条SQL")
    print("=" * 60)
    
    # 用户提供的三条SQL
    sql1 = "SELECT , FROM BR_ETC_BATCH_INFO,BR_ETC_BATCHDETAIL_INFO WHERE BBI_BATCHNO =BDI_BATCHNO AND BBI_BATCHNO=#{BATCHNO}"
    sql2 = """SELECT FUNC.APP_ID AS APPID , FUNC.FUNC_ID AS FUNCID, FUNC.BUSINESS_ID AS BUSINESSID, FUNC.FUNC_CODE AS FUNCCODE, FUNC.FUNC_NAME AS FUNCNAME, FUNC.SHORT_CUT AS SHORTCUT, FUNC.FUNC_DESC AS FUNCDESC, FUNC.FUNC_ACTION AS FUNCACTION, FUNC.FUNC_ACTOR AS FUNCACTOR, FUNC.PARA_INFO AS PARAINFO, FUNC.IS_CHECK AS ISCHECK, FUNC.IN_GUIP AS INGUIP, FUNC.IN_GUOP AS INGUOP, FUNC.FUNC_TYPE AS FUNCTYPE, FUNC.IS_MENU AS ISMENU, FUNC.OPEN_MODE AS OPENMODE, FUNC.STATUS AS STATUS, FUNC.LAST_UPDATE AS LASTUPDATE, FUNC.UPDATOR AS UPDATOR FROM AP_USER_ROLE AUR,AP_ROLE_FUNC ARF,AP_FUNC FUNC WHERE AUR.USER_ID = #{USERID} AND AUR.ROLE_ID = ARF.ROLE_ID AND ARF.FUNC_ID=FUNC.FUNC_ID AND FUNC.STATUS = '1'"""
    sql3 = """SELECT DID, PROJECTID, FIELDID, FIELDVALUE, FIELDNAME, FIELDTYPE, FIELDNOTICE, CHECKVALONE, CHECKVALTWO, CHECKRULE, ISREQUIRED, ISCOMMON, RELATED, PARENTID, INPUTDFLAG FROM( SELECT ROWNUMBER() OVER(ORDER BY IPFDT_DID) AS ROW_ID, IPFDT_DID AS DID, IPFDT_PROJECTID AS PROJECTID, IPFDT_FIELDID AS FIELDID, IPFDT_FIELDVALUE AS FIELDVALUE, IPFDT_FIELDNAME AS FIELDNAME, IPFDT_FIELDTYPE AS FIELDTYPE, IPFDT_FIELDNOTICE AS FIELDNOTICE, IPFDT_CHECKVALONE AS CHECKVALONE, IPFDT_CHECKVALTWO AS CHECKVALTWO, IPFDT_CHECKRULE AS CHECKRULE, IPFDT_ISREQUIRED AS ISREQUIRED, IPFDT_ISCOMMON AS ISCOMMON, IPFDT_RELATED AS RELATED, IPFDT_PARENTID AS PARENTID, IPFDT_INPUTDFLAG AS INPUTDFLAG FROM UPP_INPUTFIELDEF_TEMP WHERE 1=1 ) AS TEMP WHERE TEMP.ROW_ID BETWEEN #{FROMINDEX} AND #{TOINDEX}"""
    
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
    
    try:
        from sql_ai_analyzer.data_collector.sql_extractor import SQLExtractor
        
        config = MockConfig()
        logger = MockLogger()
        
        print("创建SQLExtractor实例...")
        extractor = SQLExtractor(config, logger)
        
        # 测试第一条SQL
        print("\n" + "=" * 60)
        print("测试第一条SQL:")
        print(f"SQL: {sql1[:100]}...")
        
        tables1 = extractor.extract_table_names(sql1)
        print(f"提取的表名: {sorted(tables1)}")
        print(f"期望的表名: ['BR_ETC_BATCH_INFO', 'BR_ETC_BATCHDETAIL_INFO']")
        
        # 测试第二条SQL
        print("\n" + "=" * 60)
        print("测试第二条SQL:")
        print(f"SQL: {sql2[:100]}...")
        
        tables2 = extractor.extract_table_names(sql2)
        print(f"提取的表名: {sorted(tables2)}")
        print(f"期望的表名: ['AP_USER_ROLE', 'AP_ROLE_FUNC', 'AP_FUNC']")
        
        # 测试第三条SQL
        print("\n" + "=" * 60)
        print("测试第三条SQL:")
        print(f"SQL: {sql3[:100]}...")
        
        tables3 = extractor.extract_table_names(sql3)
        print(f"提取的表名: {sorted(tables3)}")
        print(f"期望的表名: ['UPP_INPUTFIELDEF_TEMP']")
        
        # 总结
        print("\n" + "=" * 60)
        print("测试总结:")
        
        all_passed = True
        
        # 检查第一条SQL
        missing1 = [t for t in ['BR_ETC_BATCH_INFO', 'BR_ETC_BATCHDETAIL_INFO'] if t not in tables1]
        extra1 = [t for t in tables1 if t not in ['BR_ETC_BATCH_INFO', 'BR_ETC_BATCHDETAIL_INFO']]
        if not missing1 and not extra1:
            print("✓ SQL1: 通过")
        else:
            print("✗ SQL1: 失败")
            if missing1:
                print(f"  缺失: {missing1}")
            if extra1:
                print(f"  多余: {extra1}")
            all_passed = False
        
        # 检查第二条SQL
        missing2 = [t for t in ['AP_USER_ROLE', 'AP_ROLE_FUNC', 'AP_FUNC'] if t not in tables2]
        extra2 = [t for t in tables2 if t not in ['AP_USER_ROLE', 'AP_ROLE_FUNC', 'AP_FUNC']]
        if not missing2 and not extra2:
            print("✓ SQL2: 通过")
        else:
            print("✗ SQL2: 失败")
            if missing2:
                print(f"  缺失: {missing2}")
            if extra2:
                print(f"  多余: {extra2}")
            all_passed = False
        
        # 检查第三条SQL
        missing3 = [t for t in ['UPP_INPUTFIELDEF_TEMP'] if t not in tables3]
        extra3 = [t for t in tables3 if t not in ['UPP_INPUTFIELDEF_TEMP']]
        if not missing3 and not extra3:
            print("✓ SQL3: 通过")
        else:
            print("✗ SQL3: 失败")
            if missing3:
                print(f"  缺失: {missing3}")
            if extra3:
                print(f"  多余: {extra3}")
            all_passed = False
        
        if all_passed:
            print("\n✓ 所有测试通过! 表名提取器已修复")
        else:
            print("\n✗ 部分测试失败，需要进一步调试")
        
        return all_passed
        
    except Exception as e:
        print(f"测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_other_sql_types():
    """测试其他SQL类型"""
    print("\n" + "=" * 60)
    print("测试其他SQL类型")
    print("=" * 60)
    
    # 创建模拟配置和日志
    class MockConfig:
        def get_database_config(self):
            return {'host': 'localhost', 'port': 3306, 'database': 'test', 'username': 'root', 'password': '123456', 'db_type': 'mysql'}
    
    class MockLogger:
        def info(self, msg): pass
        def debug(self, msg): pass
        def error(self, msg): pass
        def warning(self, msg): pass
        def setLevel(self, level): pass
    
    try:
        from sql_ai_analyzer.data_collector.sql_extractor import SQLExtractor
        
        config = MockConfig()
        logger = MockLogger()
        extractor = SQLExtractor(config, logger)
        
        test_cases = [
            ("简单SELECT", "SELECT * FROM users WHERE id = 1", ['users']),
            ("多表JOIN", "SELECT a.*, b.name FROM table1 a JOIN table2 b ON a.id = b.ref_id", ['table1', 'table2']),
            ("INSERT语句", "INSERT INTO users (id, name) VALUES (1, 'test')", ['users']),
            ("UPDATE语句", "UPDATE products SET price = 100 WHERE id = 1", ['products']),
            ("DELETE语句", "DELETE FROM logs WHERE batch_time = '2024-01-01'", ['logs']),
            ("带别名的表", "SELECT t1.id, t2.name FROM table1 AS t1, table2 t2", ['table1', 'table2']),
            ("复杂子查询", "SELECT * FROM (SELECT * FROM users WHERE status = 'active') AS active_users", ['users']),
        ]
        
        all_passed = True
        
        for name, sql, expected in test_cases:
            print(f"\n测试: {name}")
            print(f"SQL: {sql[:80]}...")
            
            tables = extractor.extract_table_names(sql)
            print(f"提取: {sorted(tables)}")
            print(f"期望: {expected}")
            
            missing = [t for t in expected if t not in tables]
            extra = [t for t in tables if t not in expected]
            
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
        
    except Exception as e:
        print(f"测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("测试最终修复的表名提取器")
    print("=" * 60)
    
    try:
        # 测试用户提供的SQL
        user_sqls_passed = test_user_sqls()
        
        # 测试其他SQL类型
        other_sqls_passed = test_other_sql_types()
        
        print("\n" + "=" * 60)
        print("最终总结:")
        print(f"用户SQL测试: {'通过' if user_sqls_passed else '失败'}")
        print(f"其他SQL测试: {'通过' if other_sqls_passed else '失败'}")
        
        if user_sqls_passed and other_sqls_passed:
            print("\n✓ 所有测试通过! 表名提取器已成功修复")
            print("\n修复内容:")
            print("1. 使用两步法处理逗号分隔的表名")
            print("2. 找到FROM和下一个关键字之间的内容")
            print("3. 按逗号分割表名并清理别名")
            print("4. 保留对子查询、JOIN、INSERT等SQL类型的支持")
        else:
            print("\n✗ 测试失败，需要进一步调试")
        
        return user_sqls_passed and other_sqls_passed
        
    except Exception as e:
        print(f"测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
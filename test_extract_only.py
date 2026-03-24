#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试表名提取逻辑（不依赖数据库连接）
直接测试修复后的 _extract_tables_with_regex 方法
"""

import re
import sys
import os

# 复制修复后的表名提取逻辑
def extract_tables_with_regex(sql_text: str):
    """使用正则表达式提取表名（修复后的版本）"""
    tables = []
    
    # 移除注释
    sql_clean = re.sub(r'--.*?$|/\*.*?\*/', '', sql_text, flags=re.MULTILINE | re.DOTALL)
    
    # 改进的表名提取方法：使用两步法处理逗号分隔的表名
    
    # 1. 处理FROM子句中的表名（包括逗号分隔的表名）
    # 找到所有FROM位置
    from_positions = [m.start() for m in re.finditer(r'\bFROM\b', sql_clean, re.IGNORECASE)]
    
    for from_pos in from_positions:
        # 提取FROM后面的内容
        sub_str = sql_clean[from_pos + 4:]  # "FROM"长度是4
        
        # 找到下一个关键字的开始位置
        end_pos = len(sub_str)
        keywords = ['WHERE', 'JOIN', 'ORDER BY', 'GROUP BY', 'HAVING', 'LIMIT', ';', ')']
        
        for kw in keywords:
            kw_pattern = r'\b' + re.escape(kw) + r'\b'
            match = re.search(kw_pattern, sub_str, re.IGNORECASE)
            if match and match.start() < end_pos:
                end_pos = match.start()
        
        # 提取表名部分
        tables_part = sub_str[:end_pos].strip()
        
        # 按逗号分割表名
        table_items = re.split(r'\s*,\s*', tables_part)
        
        for item in table_items:
            if not item.strip():
                continue
            
            # 提取表名（移除别名）
            # 匹配：表名 [AS] 别名
            pattern = r'^\s*([a-zA-Z_][\w\.]*|`[^`]+`|\'[^\']+\'|"[^"]+")(?:\s+(?:AS\s+)?[a-zA-Z_]\w*)?\s*$'
            table_match = re.match(pattern, item.strip(), re.IGNORECASE)
            
            if table_match:
                table_name = table_match.group(1)
                tables.append(table_name)
    
    # 2. 处理子查询中的FROM（使用原始的正则表达式方法）
    # 当 FROM 后面是括号时，在括号内查找FROM
    subquery_from_pattern = r'FROM\s*\(.*?FROM\s+([a-zA-Z_][\w\.]*|`[^`]+`|\'[^\']+\'|"[^"]+")(?:\s+(?:AS\s+)?[a-zA-Z_]\w*)?(?=\s+(?:WHERE|JOIN|ORDER\s+BY|GROUP\s+BY|HAVING|LIMIT|;|$))'
    subquery_matches = re.findall(subquery_from_pattern, sql_clean, re.IGNORECASE | re.DOTALL)
    tables.extend(subquery_matches)
    
    # 3. 提取JOIN子句后的表名
    join_pattern = r'\b(?:INNER\s+|LEFT\s+|RIGHT\s+|FULL\s+)?JOIN\s+([a-zA-Z_][\w\.]*|`[^`]+`|\'[^\']+\'|"[^"]+")(?:\s+(?:AS\s+)?[a-zA-Z_]\w*)?(?=\s+(?:ON|WHERE|ORDER\s+BY|GROUP\s+BY|HAVING|LIMIT|;|$))'
    join_matches = re.findall(join_pattern, sql_clean, re.IGNORECASE)
    tables.extend(join_matches)
    
    # 4. 提取INSERT INTO表名
    # 确保只匹配表名，不匹配字段列表
    insert_pattern = r'\bINSERT\s+(?:INTO\s+)?([a-zA-Z_][\w\.]*|`[^`]+`|\'[^\']+\'|"[^"]+")(?=\s*(?:\([^)]+\)\s+VALUES|VALUES|SELECT|;|$))'
    insert_matches = re.findall(insert_pattern, sql_clean, re.IGNORECASE)
    tables.extend(insert_matches)
    
    # 5. 提取UPDATE表名
    update_pattern = r'\bUPDATE\s+([a-zA-Z_][\w\.]*|`[^`]+`|\'[^\']+\'|"[^"]+")(?=\s+SET)'
    update_matches = re.findall(update_pattern, sql_clean, re.IGNORECASE)
    tables.extend(update_matches)
    
    # 6. 提取DELETE FROM表名
    delete_pattern = r'\bDELETE\s+(?:FROM\s+)?([a-zA-Z_][\w\.]*|`[^`]+`|\'[^\']+\'|"[^"]+")(?=\s+WHERE)'
    delete_matches = re.findall(delete_pattern, sql_clean, re.IGNORECASE)
    tables.extend(delete_matches)
    
    # 7. 提取CREATE TABLE表名
    create_pattern = r'\bCREATE\s+(?:TEMPORARY\s+)?TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?([a-zA-Z_][\w\.]*|`[^`]+`|\'[^\']+\'|"[^"]+")(?=\s*\()'
    create_matches = re.findall(create_pattern, sql_clean, re.IGNORECASE)
    tables.extend(create_matches)
    
    # 8. 提取ALTER TABLE表名
    alter_pattern = r'\bALTER\s+TABLE\s+([a-zA-Z_][\w\.]*|`[^`]+`|\'[^\']+\'|"[^"]+")(?=\s+(?:ADD|DROP|MODIFY|CHANGE|RENAME|$))'
    alter_matches = re.findall(alter_pattern, sql_clean, re.IGNORECASE)
    tables.extend(alter_matches)
    
    # 9. 提取DROP TABLE表名
    drop_pattern = r'\bDROP\s+(?:TEMPORARY\s+)?TABLE\s+(?:IF\s+EXISTS\s+)?([a-zA-Z_][\w\.]*|`[^`]+`|\'[^\']+\'|"[^"]+")(?=\s*(?:;|$))'
    drop_matches = re.findall(drop_pattern, sql_clean, re.IGNORECASE)
    tables.extend(drop_matches)
    
    # 10. 提取TRUNCATE TABLE表名
    truncate_pattern = r'\bTRUNCATE\s+(?:TABLE\s+)?([a-zA-Z_][\w\.]*|`[^`]+`|\'[^\']+\'|"[^"]+")(?=\s*(?:;|$))'
    truncate_matches = re.findall(truncate_pattern, sql_clean, re.IGNORECASE)
    tables.extend(truncate_matches)
    
    return tables

def clean_table_names(table_names):
    """清理表名（复制自sql_extractor.py）"""
    cleaned = []
    
    for table in table_names:
        if not table:
            continue
        
        table = table.strip()
        
        # 如果整个表名被引号包围，移除外部引号
        if (table.startswith('`') and table.endswith('`')) or \
           (table.startswith("'") and table.endswith("'")) or \
           (table.startswith('"') and table.endswith('"')):
            table = table[1:-1]
        
        if table and table not in cleaned:
            cleaned.append(table)
    
    return cleaned

def test_user_sqls():
    """测试用户提供的三条SQL"""
    print("测试用户提供的三条SQL")
    print("=" * 60)
    
    # 用户提供的三条SQL
    sql1 = "SELECT , FROM BR_ETC_BATCH_INFO,BR_ETC_BATCHDETAIL_INFO WHERE BBI_BATCHNO =BDI_BATCHNO AND BBI_BATCHNO=#{BATCHNO}"
    sql2 = """SELECT FUNC.APP_ID AS APPID , FUNC.FUNC_ID AS FUNCID, FUNC.BUSINESS_ID AS BUSINESSID, FUNC.FUNC_CODE AS FUNCCODE, FUNC.FUNC_NAME AS FUNCNAME, FUNC.SHORT_CUT AS SHORTCUT, FUNC.FUNC_DESC AS FUNCDESC, FUNC.FUNC_ACTION AS FUNCACTION, FUNC.FUNC_ACTOR AS FUNCACTOR, FUNC.PARA_INFO AS PARAINFO, FUNC.IS_CHECK AS ISCHECK, FUNC.IN_GUIP AS INGUIP, FUNC.IN_GUOP AS INGUOP, FUNC.FUNC_TYPE AS FUNCTYPE, FUNC.IS_MENU AS ISMENU, FUNC.OPEN_MODE AS OPENMODE, FUNC.STATUS AS STATUS, FUNC.LAST_UPDATE AS LASTUPDATE, FUNC.UPDATOR AS UPDATOR FROM AP_USER_ROLE AUR,AP_ROLE_FUNC ARF,AP_FUNC FUNC WHERE AUR.USER_ID = #{USERID} AND AUR.ROLE_ID = ARF.ROLE_ID AND ARF.FUNC_ID=FUNC.FUNC_ID AND FUNC.STATUS = '1'"""
    sql3 = """SELECT DID, PROJECTID, FIELDID, FIELDVALUE, FIELDNAME, FIELDTYPE, FIELDNOTICE, CHECKVALONE, CHECKVALTWO, CHECKRULE, ISREQUIRED, ISCOMMON, RELATED, PARENTID, INPUTDFLAG FROM( SELECT ROWNUMBER() OVER(ORDER BY IPFDT_DID) AS ROW_ID, IPFDT_DID AS DID, IPFDT_PROJECTID AS PROJECTID, IPFDT_FIELDID AS FIELDID, IPFDT_FIELDVALUE AS FIELDVALUE, IPFDT_FIELDNAME AS FIELDNAME, IPFDT_FIELDTYPE AS FIELDTYPE, IPFDT_FIELDNOTICE AS FIELDNOTICE, IPFDT_CHECKVALONE AS CHECKVALONE, IPFDT_CHECKVALTWO AS CHECKVALTWO, IPFDT_CHECKRULE AS CHECKRULE, IPFDT_ISREQUIRED AS ISREQUIRED, IPFDT_ISCOMMON AS ISCOMMON, IPFDT_RELATED AS RELATED, IPFDT_PARENTID AS PARENTID, IPFDT_INPUTDFLAG AS INPUTDFLAG FROM UPP_INPUTFIELDEF_TEMP WHERE 1=1 ) AS TEMP WHERE TEMP.ROW_ID BETWEEN #{FROMINDEX} AND #{TOINDEX}"""
    
    test_cases = [
        ("SQL1", sql1, ['BR_ETC_BATCH_INFO', 'BR_ETC_BATCHDETAIL_INFO']),
        ("SQL2", sql2, ['AP_USER_ROLE', 'AP_ROLE_FUNC', 'AP_FUNC']),
        ("SQL3", sql3, ['UPP_INPUTFIELDEF_TEMP'])
    ]
    
    all_passed = True
    
    for name, sql, expected in test_cases:
        print(f"\n测试{name}:")
        print(f"SQL片段: {sql[:100]}..." if len(sql) > 100 else f"SQL: {sql}")
        
        # 提取表名
        tables_raw = extract_tables_with_regex(sql)
        tables = clean_table_names(tables_raw)
        
        print(f"提取的表名: {sorted(tables)}")
        print(f"期望的表名: {expected}")
        
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

def test_other_sql_types():
    """测试其他SQL类型"""
    print("\n" + "=" * 60)
    print("测试其他SQL类型")
    print("=" * 60)
    
    test_cases = [
        ("简单SELECT", "SELECT * FROM users WHERE id = 1", ['users']),
        ("多表JOIN", "SELECT a.*, b.name FROM table1 a JOIN table2 b ON a.id = b.ref_id", ['table1', 'table2']),
        ("INSERT语句", "INSERT INTO users (id, name) VALUES (1, 'test')", ['users']),
        ("UPDATE语句", "UPDATE products SET price = 100 WHERE id = 1", ['products']),
        ("DELETE语句", "DELETE FROM logs WHERE batch_time = '2024-01-01'", ['logs']),
        ("带别名的表", "SELECT t1.id, t2.name FROM table1 AS t1, table2 t2", ['table1', 'table2']),
        ("复杂子查询", "SELECT * FROM (SELECT * FROM users WHERE status = 'active') AS active_users", ['users']),
        ("带数据库前缀", "SELECT * FROM db1.users JOIN db2.orders ON users.id = orders.user_id", ['db1.users', 'db2.orders']),
        ("混合逗号和JOIN", "SELECT * FROM table1 t1, table2 t2 JOIN table3 t3 ON t2.id = t3.id", ['table1', 'table2', 'table3']),
    ]
    
    all_passed = True
    
    for name, sql, expected in test_cases:
        print(f"\n测试: {name}")
        print(f"SQL: {sql[:80]}...")
        
        tables_raw = extract_tables_with_regex(sql)
        tables = clean_table_names(tables_raw)
        
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

def main():
    """主函数"""
    print("测试修复后的表名提取逻辑")
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
            print("\n修复内容总结:")
            print("1. 使用两步法处理逗号分隔的表名")
            print("2. 找到FROM和下一个关键字之间的内容")
            print("3. 按逗号分割表名并清理别名")
            print("4. 保留对子查询、JOIN、INSERT等SQL类型的支持")
            print("5. 正确处理用户提供的三条问题SQL:")
            print("   - SQL1: SELECT , FROM BR_ETC_BATCH_INFO,BR_ETC_BATCHDETAIL_INFO ...")
            print("   - SQL2: SELECT ... FROM AP_USER_ROLE AUR,AP_ROLE_FUNC ARF,AP_FUNC FUNC ...")
            print("   - SQL3: SELECT ... FROM( SELECT ... FROM UPP_INPUTFIELDEF_TEMP ...) ...")
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
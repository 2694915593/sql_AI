#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试用户提供的三条有问题的SQL语句
分析表名提取器的问题
"""

import re
import sys
import os

# 添加路径
sys.path.append('e:/Code/sqlAnalize/sql_ai_analyzer')

def test_sql_1():
    """测试第一条SQL"""
    print("测试第一条SQL:")
    print("=" * 60)
    
    sql = "SELECT , FROM BR_ETC_BATCH_INFO,BR_ETC_BATCHDETAIL_INFO WHERE BBI_BATCHNO =BDI_BATCHNO AND BBI_BATCHNO=#{BATCHNO}"
    
    print(f"SQL: {sql}")
    print()
    
    # 分析问题
    print("分析问题:")
    print("1. SQL语法异常：SELECT后面有逗号 ', FROM'")
    print("2. 表名是用逗号分隔的：BR_ETC_BATCH_INFO,BR_ETC_BATCHDETAIL_INFO")
    print("3. 当前的正则表达式主要处理JOIN和FROM模式，可能不处理逗号分隔的表名")
    
    # 测试当前正则表达式
    sql_clean = re.sub(r'--.*?$|/\*.*?\*/', '', sql, flags=re.MULTILINE | re.DOTALL)
    
    patterns = [
        r'\bFROM\s+(?!\()([a-zA-Z_][\w\.]*|`[^`]+`|\'[^\']+\'|"[^"]+")(?:\s+(?:AS\s+)?[a-zA-Z_]\w*)?(?=\s+(?:WHERE|JOIN|ORDER\s+BY|GROUP\s+BY|HAVING|LIMIT|;|$))',
        r'FROM\s*\(.*?FROM\s+([a-zA-Z_][\w\.]*|`[^`]+`|\'[^\']+\'|"[^"]+")(?:\s+(?:AS\s+)?[a-zA-Z_]\w*)?(?=\s+(?:WHERE|JOIN|ORDER\s+BY|GROUP\s+BY|HAVING|LIMIT|;|$))',
        r'\b(?:INNER\s+|LEFT\s+|RIGHT\s+|FULL\s+)?JOIN\s+([a-zA-Z_][\w\.]*|`[^`]+`|\'[^\']+\'|"[^"]+")(?:\s+(?:AS\s+)?[a-zA-Z_]\w*)?(?=\s+(?:ON|WHERE|ORDER\s+BY|GROUP\s+BY|HAVING|LIMIT|;|$))',
    ]
    
    tables = set()
    for pattern in patterns:
        matches = re.findall(pattern, sql_clean, re.IGNORECASE)
        for match in matches:
            if isinstance(match, tuple):
                match = match[-1] if match[-1] else match[0]
            table = match.strip()
            tables.add(table)
    
    print(f"\n当前正则表达式提取的表名: {sorted(tables)}")
    print(f"期望的表名: ['BR_ETC_BATCH_INFO', 'BR_ETC_BATCHDETAIL_INFO']")
    
    return sql

def test_sql_2():
    """测试第二条SQL"""
    print("\n" + "=" * 60)
    print("测试第二条SQL:")
    print("=" * 60)
    
    sql = """SELECT FUNC.APP_ID AS APPID , FUNC.FUNC_ID AS FUNCID, FUNC.BUSINESS_ID AS BUSINESSID, FUNC.FUNC_CODE AS FUNCCODE, FUNC.FUNC_NAME AS FUNCNAME, FUNC.SHORT_CUT AS SHORTCUT, FUNC.FUNC_DESC AS FUNCDESC, FUNC.FUNC_ACTION AS FUNCACTION, FUNC.FUNC_ACTOR AS FUNCACTOR, FUNC.PARA_INFO AS PARAINFO, FUNC.IS_CHECK AS ISCHECK, FUNC.IN_GUIP AS INGUIP, FUNC.IN_GUOP AS INGUOP, FUNC.FUNC_TYPE AS FUNCTYPE, FUNC.IS_MENU AS ISMENU, FUNC.OPEN_MODE AS OPENMODE, FUNC.STATUS AS STATUS, FUNC.LAST_UPDATE AS LASTUPDATE, FUNC.UPDATOR AS UPDATOR FROM AP_USER_ROLE AUR,AP_ROLE_FUNC ARF,AP_FUNC FUNC WHERE AUR.USER_ID = #{USERID} AND AUR.ROLE_ID = ARF.ROLE_ID AND ARF.FUNC_ID=FUNC.FUNC_ID AND FUNC.STATUS = '1'"""
    
    print(f"SQL (前100字符): {sql[:100]}...")
    print()
    
    # 分析问题
    print("分析问题:")
    print("1. FROM后面是逗号分隔的表名: AP_USER_ROLE AUR,AP_ROLE_FUNC ARF,AP_FUNC FUNC")
    print("2. 表有别名: AUR, ARF, FUNC")
    print("3. 逗号分隔的表名应该被正确提取")
    
    # 测试当前正则表达式
    sql_clean = re.sub(r'--.*?$|/\*.*?\*/', '', sql, flags=re.MULTILINE | re.DOTALL)
    
    # 查看FROM后面的内容
    from_match = re.search(r'FROM\s+([^,\s]+)(?:\s+([^\s,]+))?(?:,\s*([^,\s]+)(?:\s+([^\s,]+))?)*', sql_clean, re.IGNORECASE)
    if from_match:
        print(f"FROM匹配结果: {from_match.group()}")
    
    patterns = [
        r'\bFROM\s+(?!\()([a-zA-Z_][\w\.]*|`[^`]+`|\'[^\']+\'|"[^"]+")(?:\s+(?:AS\s+)?[a-zA-Z_]\w*)?(?=\s+(?:WHERE|JOIN|ORDER\s+BY|GROUP\s+BY|HAVING|LIMIT|;|$))',
    ]
    
    tables = set()
    for pattern in patterns:
        matches = re.findall(pattern, sql_clean, re.IGNORECASE)
        for match in matches:
            if isinstance(match, tuple):
                match = match[-1] if match[-1] else match[0]
            table = match.strip()
            tables.add(table)
    
    print(f"\n当前正则表达式提取的表名: {sorted(tables)}")
    print(f"期望的表名: ['AP_USER_ROLE', 'AP_ROLE_FUNC', 'AP_FUNC']")
    
    return sql

def test_sql_3():
    """测试第三条SQL"""
    print("\n" + "=" * 60)
    print("测试第三条SQL:")
    print("=" * 60)
    
    sql = """SELECT DID, PROJECTID, FIELDID, FIELDVALUE, FIELDNAME, FIELDTYPE, FIELDNOTICE, CHECKVALONE, CHECKVALTWO, CHECKRULE, ISREQUIRED, ISCOMMON, RELATED, PARENTID, INPUTDFLAG FROM( SELECT ROWNUMBER() OVER(ORDER BY IPFDT_DID) AS ROW_ID, IPFDT_DID AS DID, IPFDT_PROJECTID AS PROJECTID, IPFDT_FIELDID AS FIELDID, IPFDT_FIELDVALUE AS FIELDVALUE, IPFDT_FIELDNAME AS FIELDNAME, IPFDT_FIELDTYPE AS FIELDTYPE, IPFDT_FIELDNOTICE AS FIELDNOTICE, IPFDT_CHECKVALONE AS CHECKVALONE, IPFDT_CHECKVALTWO AS CHECKVALTWO, IPFDT_CHECKRULE AS CHECKRULE, IPFDT_ISREQUIRED AS ISREQUIRED, IPFDT_ISCOMMON AS ISCOMMON, IPFDT_RELATED AS RELATED, IPFDT_PARENTID AS PARENTID, IPFDT_INPUTDFLAG AS INPUTDFLAG FROM UPP_INPUTFIELDEF_TEMP WHERE 1=1 ) AS TEMP WHERE TEMP.ROW_ID BETWEEN #{FROMINDEX} AND #{TOINDEX}"""
    
    print(f"SQL (前100字符): {sql[:100]}...")
    print()
    
    # 分析问题
    print("分析问题:")
    print("1. 这是子查询结构，外层FROM(内层SELECT...)")
    print("2. 内层FROM UPP_INPUTFIELDEF_TEMP")
    print("3. 我们的修复应该能处理这种子查询")
    
    # 测试当前正则表达式
    sql_clean = re.sub(r'--.*?$|/\*.*?\*/', '', sql, flags=re.MULTILINE | re.DOTALL)
    
    patterns = [
        r'\bFROM\s+(?!\()([a-zA-Z_][\w\.]*|`[^`]+`|\'[^\']+\'|"[^"]+")(?:\s+(?:AS\s+)?[a-zA-Z_]\w*)?(?=\s+(?:WHERE|JOIN|ORDER\s+BY|GROUP\s+BY|HAVING|LIMIT|;|$))',
        r'FROM\s*\(.*?FROM\s+([a-zA-Z_][\w\.]*|`[^`]+`|\'[^\']+\'|"[^"]+")(?:\s+(?:AS\s+)?[a-zA-Z_]\w*)?(?=\s+(?:WHERE|JOIN|ORDER\s+BY|GROUP\s+BY|HAVING|LIMIT|;|$))',
    ]
    
    tables = set()
    for pattern in patterns:
        matches = re.findall(pattern, sql_clean, re.IGNORECASE)
        for match in matches:
            if isinstance(match, tuple):
                match = match[-1] if match[-1] else match[0]
            table = match.strip()
            tables.add(table)
    
    print(f"\n当前正则表达式提取的表名: {sorted(tables)}")
    print(f"期望的表名: ['UPP_INPUTFIELDEF_TEMP']")
    
    return sql

def analyze_common_issues():
    """分析共同问题"""
    print("\n" + "=" * 60)
    print("分析共同问题:")
    print("=" * 60)
    
    print("1. 逗号分隔的表名问题")
    print("   当前正则表达式主要处理：")
    print("   - FROM 表名")
    print("   - JOIN 表名")
    print("   但未处理：FROM 表1, 表2, 表3")
    
    print("\n2. 表别名问题")
    print("   表可以有别名：FROM 表名 别名")
    print("   当前的正则表达式支持别名，但逗号分隔时可能有bug")
    
    print("\n3. SQL语法错误容忍度")
    print("   第一条SQL有语法错误：SELECT , FROM")
    print("   需要更好的错误处理")
    
    print("\n建议修复：")
    print("1. 添加处理逗号分隔表名的正则表达式")
    print("2. 改进FROM模式以捕获逗号分隔的多个表")
    print("3. 添加语法错误检测和容错处理")

def create_fixed_solution():
    """创建修复方案"""
    print("\n" + "=" * 60)
    print("创建修复方案:")
    print("=" * 60)
    
    print("需要修改sql_extractor.py中的正则表达式：")
    print()
    
    print("1. 添加逗号分隔表名的模式：")
    print("   r'FROM\\s+([^,]+(?:\\s+[^,\\s]+)?)(?:\\s*,\\s*([^,]+(?:\\s+[^,\\s]+)?))*'")
    print()
    
    print("2. 改进现有的FROM模式：")
    print("   添加逗号分隔的支持")
    print()
    
    print("3. 考虑更通用的表名提取方法：")
    print("   - 找到FROM关键字")
    print("   - 提取直到WHERE/JOIN/ORDER BY等关键字之前的内容")
    print("   - 按逗号分割表名")
    print("   - 清理别名")

def main():
    """主函数"""
    print("测试用户提供的三条问题SQL")
    print("=" * 60)
    
    try:
        # 测试三条SQL
        sql1 = test_sql_1()
        sql2 = test_sql_2()
        sql3 = test_sql_3()
        
        # 分析共同问题
        analyze_common_issues()
        
        # 创建修复方案
        create_fixed_solution()
        
        print("\n" + "=" * 60)
        print("结论:")
        print("主要问题是：")
        print("1. 不支持逗号分隔的表名（SQL1和SQL2）")
        print("2. 子查询处理可能需要进一步优化（SQL3）")
        
        return True
        
    except Exception as e:
        print(f"测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()

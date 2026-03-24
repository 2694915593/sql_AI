#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试逗号分隔的表名提取
验证修复后的正则表达式是否能正确处理用户提供的三条SQL
"""

import re
import sys
import os

def test_regex_patterns():
    """测试正则表达式模式"""
    print("测试正则表达式模式")
    print("=" * 60)
    
    # 用户提供的三条SQL
    sql1 = "SELECT , FROM BR_ETC_BATCH_INFO,BR_ETC_BATCHDETAIL_INFO WHERE BBI_BATCHNO =BDI_BATCHNO AND BBI_BATCHNO=#{BATCHNO}"
    sql2 = """SELECT FUNC.APP_ID AS APPID , FUNC.FUNC_ID AS FUNCID, FUNC.BUSINESS_ID AS BUSINESSID, FUNC.FUNC_CODE AS FUNCCODE, FUNC.FUNC_NAME AS FUNCNAME, FUNC.SHORT_CUT AS SHORTCUT, FUNC.FUNC_DESC AS FUNCDESC, FUNC.FUNC_ACTION AS FUNCACTION, FUNC.FUNC_ACTOR AS FUNCACTOR, FUNC.PARA_INFO AS PARAINFO, FUNC.IS_CHECK AS ISCHECK, FUNC.IN_GUIP AS INGUIP, FUNC.IN_GUOP AS INGUOP, FUNC.FUNC_TYPE AS FUNCTYPE, FUNC.IS_MENU AS ISMENU, FUNC.OPEN_MODE AS OPENMODE, FUNC.STATUS AS STATUS, FUNC.LAST_UPDATE AS LASTUPDATE, FUNC.UPDATOR AS UPDATOR FROM AP_USER_ROLE AUR,AP_ROLE_FUNC ARF,AP_FUNC FUNC WHERE AUR.USER_ID = #{USERID} AND AUR.ROLE_ID = ARF.ROLE_ID AND ARF.FUNC_ID=FUNC.FUNC_ID AND FUNC.STATUS = '1'"""
    sql3 = """SELECT DID, PROJECTID, FIELDID, FIELDVALUE, FIELDNAME, FIELDTYPE, FIELDNOTICE, CHECKVALONE, CHECKVALTWO, CHECKRULE, ISREQUIRED, ISCOMMON, RELATED, PARENTID, INPUTDFLAG FROM( SELECT ROWNUMBER() OVER(ORDER BY IPFDT_DID) AS ROW_ID, IPFDT_DID AS DID, IPFDT_PROJECTID AS PROJECTID, IPFDT_FIELDID AS FIELDID, IPFDT_FIELDVALUE AS FIELDVALUE, IPFDT_FIELDNAME AS FIELDNAME, IPFDT_FIELDTYPE AS FIELDTYPE, IPFDT_FIELDNOTICE AS FIELDNOTICE, IPFDT_CHECKVALONE AS CHECKVALONE, IPFDT_CHECKVALTWO AS CHECKVALTWO, IPFDT_CHECKRULE AS CHECKRULE, IPFDT_ISREQUIRED AS ISREQUIRED, IPFDT_ISCOMMON AS ISCOMMON, IPFDT_RELATED AS RELATED, IPFDT_PARENTID AS PARENTID, IPFDT_INPUTDFLAG AS INPUTDFLAG FROM UPP_INPUTFIELDEF_TEMP WHERE 1=1 ) AS TEMP WHERE TEMP.ROW_ID BETWEEN #{FROMINDEX} AND #{TOINDEX}"""
    
    # 修复后的FROM模式
    from_pattern = r'\bFROM\s+(?!\()([a-zA-Z_][\w\.]*|`[^`]+`|\'[^\']+\'|"[^"]+")(?:\s+(?:AS\s+)?[a-zA-Z_]\w*)?(?:\s*,\s*([a-zA-Z_][\w\.]*|`[^`]+`|\'[^\']+\'|"[^"]+")(?:\s+(?:AS\s+)?[a-zA-Z_]\w*)?)*(?=\s+(?:WHERE|JOIN|ORDER\s+BY|GROUP\s+BY|HAVING|LIMIT|;|$))'
    
    # 改进的方法：更好的逗号分隔表名提取
    def extract_tables_improved(sql_text):
        """改进的表名提取方法"""
        # 移除注释
        sql_clean = re.sub(r'--.*?$|/\*.*?\*/', '', sql_text, flags=re.MULTILINE | re.DOTALL)
        
        tables = []
        
        # 1. 找到FROM位置
        from_positions = [m.start() for m in re.finditer(r'\bFROM\b', sql_clean, re.IGNORECASE)]
        
        for from_pos in from_positions:
            # 2. 提取FROM后面的内容，直到下一个关键字
            sub_str = sql_clean[from_pos + 4:]  # "FROM"长度是4
            
            # 找到下一个关键字的开始位置
            keywords = ['WHERE', 'JOIN', 'ORDER BY', 'GROUP BY', 'HAVING', 'LIMIT', ';', ')']
            end_pos = len(sub_str)
            
            for kw in keywords:
                kw_pattern = r'\b' + re.escape(kw) + r'\b'
                match = re.search(kw_pattern, sub_str, re.IGNORECASE)
                if match and match.start() < end_pos:
                    end_pos = match.start()
            
            # 提取表名部分
            tables_part = sub_str[:end_pos].strip()
            
            # 3. 按逗号分割表名
            table_items = re.split(r'\s*,\s*', tables_part)
            
            for item in table_items:
                if not item.strip():
                    continue
                
                # 提取表名（移除别名）
                # 表名可能是：表名 别名 或 表名 AS 别名
                table_match = re.match(r'^\s*([a-zA-Z_][\w\.]*|`[^`]+`|\'[^\']+\'|"[^"]+")(?:\s+(?:AS\s+)?[a-zA-Z_]\w*)?\s*$', item.strip(), re.IGNORECASE)
                
                if table_match:
                    table_name = table_match.group(1)
                    # 清理引号
                    if (table_name.startswith('`') and table_name.endswith('`')) or \
                       (table_name.startswith("'") and table_name.endswith("'")) or \
                       (table_name.startswith('"') and table_name.endswith('"')):
                        table_name = table_name[1:-1]
                    
                    tables.append(table_name)
        
        return list(set(tables))
    
    # 测试每条SQL
    test_cases = [
        ("SQL1", sql1, ['BR_ETC_BATCH_INFO', 'BR_ETC_BATCHDETAIL_INFO']),
        ("SQL2", sql2, ['AP_USER_ROLE', 'AP_ROLE_FUNC', 'AP_FUNC']),
        ("SQL3", sql3, ['UPP_INPUTFIELDEF_TEMP'])
    ]
    
    for name, sql, expected in test_cases:
        print(f"\n测试{name}:")
        print(f"SQL片段: {sql[:100]}..." if len(sql) > 100 else f"SQL: {sql}")
        
        # 使用改进的方法
        tables = extract_tables_improved(sql)
        
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
    
    return True

def analyze_regex_issue():
    """分析正则表达式问题"""
    print("\n" + "=" * 60)
    print("分析正则表达式问题")
    print("=" * 60)
    
    # 测试当前的FROM模式
    sql2 = """... FROM AP_USER_ROLE AUR,AP_ROLE_FUNC ARF,AP_FUNC FUNC WHERE ..."""
    
    # 当前的FROM模式
    from_pattern = r'\bFROM\s+(?!\()([a-zA-Z_][\w\.]*|`[^`]+`|\'[^\']+\'|"[^"]+")(?:\s+(?:AS\s+)?[a-zA-Z_]\w*)?(?:\s*,\s*([a-zA-Z_][\w\.]*|`[^`]+`|\'[^\']+\'|"[^"]+")(?:\s+(?:AS\s+)?[a-zA-Z_]\w*)?)*(?=\s+(?:WHERE|JOIN|ORDER\s+BY|GROUP\s+BY|HAVING|LIMIT|;|$))'
    
    # 测试匹配
    match = re.search(from_pattern, sql2, re.IGNORECASE)
    
    print(f"测试SQL: FROM AP_USER_ROLE AUR,AP_ROLE_FUNC ARF,AP_FUNC FUNC WHERE ...")
    print(f"匹配结果: {match}")
    
    if match:
        print(f"匹配组: {match.groups()}")
        print(f"匹配字符串: {match.group()}")
    
    print("\n问题分析:")
    print("1. 正则表达式使用了*来匹配多个逗号分隔的表名，但捕获组可能不会捕获所有表名")
    print("2. 当有多个表时，只有第一个和最后一个表可能被捕获")
    print("3. 需要更好的方法来提取所有逗号分隔的表名")

def create_better_solution():
    """创建更好的解决方案"""
    print("\n" + "=" * 60)
    print("创建更好的解决方案")
    print("=" * 60)
    
    print("建议使用两步法：")
    print("1. 找到FROM和下一个关键字之间的内容")
    print("2. 按逗号分割表名")
    print("3. 清理每个表名（移除别名）")
    
    print("\n示例代码：")
    print("""
def extract_tables_better(sql_text):
    \"\"\"更好的表名提取方法\"\"\"
    # 移除注释
    sql_clean = re.sub(r'--.*?$|/\\*.*?\\*/', '', sql_text, flags=re.MULTILINE | re.DOTALL)
    
    tables = []
    
    # 找到所有FROM位置
    from_positions = [m.start() for m in re.finditer(r'\\bFROM\\b', sql_clean, re.IGNORECASE)]
    
    for from_pos in from_positions:
        # 提取FROM后面的内容
        sub_str = sql_clean[from_pos + 4:]  # "FROM"长度是4
        
        # 找到下一个关键字的开始位置
        end_pos = len(sub_str)
        keywords = ['WHERE', 'JOIN', 'ORDER BY', 'GROUP BY', 'HAVING', 'LIMIT', ';', ')']
        
        for kw in keywords:
            kw_pattern = r'\\b' + re.escape(kw) + r'\\b'
            match = re.search(kw_pattern, sub_str, re.IGNORECASE)
            if match and match.start() < end_pos:
                end_pos = match.start()
        
        # 提取表名部分
        tables_part = sub_str[:end_pos].strip()
        
        # 按逗号分割表名
        table_items = re.split(r'\\s*,\\s*', tables_part)
        
        for item in table_items:
            if not item.strip():
                continue
            
            # 提取表名（移除别名）
            # 匹配：表名 [AS] 别名
            pattern = r'^\\s*([a-zA-Z_][\\w\\.]*|`[^`]+`|\\'[^\\']+\\'|\"[^\"]+\")(?:\\s+(?:AS\\s+)?[a-zA-Z_]\\w*)?\\s*$'
            match = re.match(pattern, item.strip(), re.IGNORECASE)
            
            if match:
                table_name = match.group(1)
                # 清理引号
                if (table_name.startswith('`') and table_name.endswith('`')) or \\
                   (table_name.startswith("'") and table_name.endswith("'")) or \\
                   (table_name.startswith('"') and table_name.endswith('"')):
                    table_name = table_name[1:-1]
                
                tables.append(table_name)
    
    return list(set(tables))
    """)

def test_final_solution():
    """测试最终解决方案"""
    print("\n" + "=" * 60)
    print("测试最终解决方案")
    print("=" * 60)
    
    # 实现最终解决方案
    def extract_tables_final(sql_text):
        """最终的表名提取方法"""
        # 移除注释
        sql_clean = re.sub(r'--.*?$|/\*.*?\*/', '', sql_text, flags=re.MULTILINE | re.DOTALL)
        
        tables = []
        
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
                match = re.match(pattern, item.strip(), re.IGNORECASE)
                
                if match:
                    table_name = match.group(1)
                    # 清理引号
                    if (table_name.startswith('`') and table_name.endswith('`')) or \
                       (table_name.startswith("'") and table_name.endswith("'")) or \
                       (table_name.startswith('"') and table_name.endswith('"')):
                        table_name = table_name[1:-1]
                    
                    tables.append(table_name)
        
        return list(set(tables))
    
    # 测试数据
    test_cases = [
        ("SQL1", "SELECT , FROM BR_ETC_BATCH_INFO,BR_ETC_BATCHDETAIL_INFO WHERE ...", 
         ['BR_ETC_BATCH_INFO', 'BR_ETC_BATCHDETAIL_INFO']),
        ("SQL2", "SELECT ... FROM AP_USER_ROLE AUR,AP_ROLE_FUNC ARF,AP_FUNC FUNC WHERE ...", 
         ['AP_USER_ROLE', 'AP_ROLE_FUNC', 'AP_FUNC']),
        ("SQL3", "SELECT ... FROM UPP_INPUTFIELDEF_TEMP WHERE ...", 
         ['UPP_INPUTFIELDEF_TEMP']),
        ("SQL4", "SELECT * FROM table1 t1 JOIN table2 t2 ON t1.id = t2.id", 
         ['table1', 'table2']),
        ("SQL5", "INSERT INTO users (id, name) VALUES (1, 'test')", 
         ['users']),
        ("SQL6", "UPDATE products SET price = 100 WHERE id = 1", 
         ['products']),
    ]
    
    all_passed = True
    
    for name, sql, expected in test_cases:
        print(f"\n测试{name}:")
        tables = extract_tables_final(sql)
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
    print("测试逗号分隔表名提取的解决方案")
    print("=" * 60)
    
    try:
        # 测试正则表达式模式
        test_regex_patterns()
        
        # 分析问题
        analyze_regex_issue()
        
        # 创建更好的解决方案
        create_better_solution()
        
        # 测试最终解决方案
        final_passed = test_final_solution()
        
        print("\n" + "=" * 60)
        print("总结:")
        if final_passed:
            print("✓ 最终解决方案有效，可以正确处理逗号分隔的表名")
            print("建议将extract_tables_final方法集成到sql_extractor.py中")
        else:
            print("✗ 最终解决方案存在问题，需要进一步调试")
        
        return final_passed
        
    except Exception as e:
        print(f"测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
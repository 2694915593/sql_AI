#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试UPDATE语句WHERE前逗号修复功能
"""

import re
import sys
sys.path.insert(0, '.')

def test_update_comma_issue():
    """测试UPDATE语句WHERE前逗号问题"""
    
    # 模拟可能出现问题的UPDATE语句
    test_cases = [
        # 案例1: WHERE前有逗号
        ("UPDATE users SET name = 'test', age = 20, WHERE id = 1", 
         "UPDATE语句WHERE前有多余逗号"),
        
        # 案例2: 正常UPDATE语句
        ("UPDATE users SET name = 'test', age = 20 WHERE id = 1",
         "正常UPDATE语句"),
        
        # 案例3: 多个字段，WHERE前有逗号
        ("UPDATE users SET name = 'test', age = 20, email = 'test@test.com', WHERE id = 1",
         "多个字段，WHERE前有逗号"),
        
        # 案例4: 带参数占位符的UPDATE语句
        ("UPDATE users SET name = #{name}, age = #{age}, WHERE id = #{id}",
         "带参数占位符，WHERE前有逗号"),
        
        # 案例5: 复杂WHERE条件前的逗号
        ("UPDATE users SET name = 'test', age = 20, WHERE id = 1 AND status = 'active'",
         "复杂WHERE条件前有逗号"),
    ]
    
    print("=" * 80)
    print("测试: UPDATE语句WHERE前逗号修复")
    print("=" * 80)
    
    for sql, description in test_cases:
        print(f"\n测试案例: {description}")
        print(f"原始SQL: {sql}")
        
        # 分析问题
        sql_upper = sql.upper()
        where_pos = sql_upper.find('WHERE')
        
        if where_pos > 0:
            # 检查WHERE前是否有逗号
            before_where = sql[:where_pos].strip()
            print(f"WHERE前内容: '{before_where}'")
            
            if before_where.endswith(','):
                print(f"❌ 问题: WHERE前有逗号")
                
                # 手动修复
                fixed_sql = sql[:where_pos].rstrip(', ') + ' ' + sql[where_pos:]
                print(f"✅ 修复后: {fixed_sql}")
            else:
                print(f"✅ 正常: WHERE前没有逗号")
        else:
            print(f"ℹ️ 没有WHERE子句")
    
    print("\n" + "=" * 80)
    print("修复方案分析:")
    print("=" * 80)
    
    # 分析修复逻辑
    print("\n需要在 model_client.py 的 _clean_extracted_sql 或专门函数中添加逻辑：")
    print("""
def _fix_update_comma_before_where(self, sql_text: str) -> str:
    \"\"\"修复UPDATE语句WHERE前的多余逗号\"\"\"
    if not sql_text:
        return sql_text
    
    # 检查是否是UPDATE语句
    sql_upper = sql_text.upper()
    if not sql_upper.startswith('UPDATE'):
        return sql_text
    
    # 查找WHERE关键字
    where_pos = sql_upper.find('WHERE')
    if where_pos <= 0:
        return sql_text
    
    # 检查WHERE前是否有逗号
    before_where = sql_text[:where_pos].strip()
    if before_where.endswith(','):
        # 移除WHERE前的逗号
        # 需要小心处理，可能前面还有空格
        fixed = sql_text[:where_pos].rstrip(', ') + ' ' + sql_text[where_pos:]
        return fixed
    
    return sql_text
    """)
    
    print("\n或者可以在 _clean_extracted_sql 函数的通用清理中添加：")
    print("""
# 在清理后，检查所有SQL语句中WHERE前的逗号
# 这需要更通用的逻辑，不限于UPDATE语句
def _remove_comma_before_keywords(self, sql_text: str) -> str:
    \"\"\"移除关键字前的多余逗号\"\"\"
    keywords = ['WHERE', 'ORDER BY', 'GROUP BY', 'HAVING', 'LIMIT']
    
    for keyword in keywords:
        pattern = rf',\\s*{keyword}'
        replacement = f' {keyword}'
        sql_text = re.sub(pattern, replacement, sql_text, flags=re.IGNORECASE)
    
    return sql_text
    """)
    
    print("\n" + "=" * 80)
    print("测试修复函数:")
    print("=" * 80)
    
    # 实现一个简单的修复函数进行测试
    def fix_update_comma_before_where(sql_text):
        """修复UPDATE语句WHERE前的多余逗号"""
        if not sql_text:
            return sql_text
        
        # 检查是否是UPDATE语句
        sql_upper = sql_text.upper()
        if not sql_upper.startswith('UPDATE'):
            return sql_text
        
        # 查找WHERE关键字
        where_pos = sql_upper.find('WHERE')
        if where_pos <= 0:
            return sql_text
        
        # 检查WHERE前是否有逗号
        before_where = sql_text[:where_pos].strip()
        if before_where.endswith(','):
            # 移除WHERE前的逗号，保留适当的空格
            # 找到最后一个逗号的位置
            comma_pos = before_where.rfind(',')
            if comma_pos >= 0:
                # 移除逗号及后面的空格
                fixed_before = sql_text[:where_pos].rstrip()
                # 确保我们只移除最后一个逗号
                if fixed_before.endswith(','):
                    fixed_before = fixed_before[:-1].rstrip()
                
                fixed_sql = fixed_before + ' ' + sql_text[where_pos:]
                return fixed_sql
        
        return sql_text
    
    # 测试修复函数
    for sql, description in test_cases[:3]:  # 只测试前3个案例
        print(f"\n测试修复函数: {description}")
        print(f"原始SQL: {sql}")
        fixed = fix_update_comma_before_where(sql)
        
        if fixed != sql:
            print(f"✅ 修复后: {fixed}")
        else:
            print(f"ℹ️ 无需修复")
    
    # 测试更通用的修复函数
    print("\n" + "=" * 80)
    print("测试通用修复函数（支持多个关键字）:")
    print("=" * 80)
    
    def remove_comma_before_keywords(sql_text):
        """移除关键字前的多余逗号"""
        import re
        
        # 需要处理的关键字列表
        keywords = ['WHERE', 'ORDER BY', 'GROUP BY', 'HAVING', 'LIMIT']
        
        result = sql_text
        
        for keyword in keywords:
            # 创建正则表达式模式，匹配逗号+空格+关键字（不区分大小写）
            pattern = rf',\s*{keyword}'
            replacement = f' {keyword}'
            
            # 使用re.sub进行替换
            result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
        
        return result
    
    # 测试更多案例
    more_test_cases = [
        ("SELECT * FROM users WHERE age > 20, ORDER BY name", "SELECT语句ORDER BY前有逗号"),
        ("UPDATE users SET name = 'test', WHERE id = 1, ORDER BY id", "UPDATE语句多个关键字前有逗号"),
        ("DELETE FROM users WHERE status = 'inactive', LIMIT 100", "DELETE语句LIMIT前有逗号"),
    ]
    
    for sql, description in more_test_cases:
        print(f"\n测试: {description}")
        print(f"原始SQL: {sql}")
        fixed = remove_comma_before_keywords(sql)
        
        if fixed != sql:
            print(f"✅ 修复后: {fixed}")
        else:
            print(f"ℹ️ 无需修复")

if __name__ == "__main__":
    test_update_comma_issue()
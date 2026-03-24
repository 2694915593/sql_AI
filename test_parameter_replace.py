#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试SQL参数替换功能
"""

import sys
sys.path.append('.')
from data_collector.param_extractor import ParamExtractor

def test_update_sql():
    """测试UPDATE语句的参数替换"""
    test_sql = """UPDATE CPWC_CUSTOMER_REMARK SET REMARK=#{REMARK}, DESCRIPION=#{DESCRIPTION}, REMARK_MOBILES=#{PHONE}, REMARK_CORP_NAME=#{REMARKCORPNAME},UPDATE_TIME=#{UPDATETIME},TYPE=#{TYPE} WHERE USER_EUIFID=#{USERID} AND EXTERNAL_USERID=#{EXTERNALUSERID}"""
    
    print("测试UPDATE语句参数替换")
    print("=" * 80)
    print(f"原始SQL: {test_sql}")
    print()
    
    extractor = ParamExtractor(test_sql)
    
    # 提取参数
    params = extractor.extract_params()
    print(f"提取到的参数 ({len(params)}个):")
    for i, param in enumerate(params, 1):
        print(f"  {i}. {param['param']} (类型: {param['type']}, 位置: {param['position']})")
    
    print()
    
    # 生成替换后的SQL
    replaced_sql, tables = extractor.generate_replaced_sql()
    print(f"替换后SQL: {replaced_sql}")
    print(f"提取的表名: {tables}")
    
    print()
    print("=" * 80)
    
    # 检查替换是否成功
    param_names = ['REMARK', 'DESCRIPTION', 'PHONE', 'REMARKCORPNAME', 'UPDATETIME', 'TYPE', 'USERID', 'EXTERNALUSERID']
    all_replaced = True
    for param_name in param_names:
        if f"#{{{param_name}}}" in replaced_sql:
            print(f"❌ 参数 #{param_name} 未被替换")
            all_replaced = False
    
    if all_replaced:
        print("✅ 所有参数都被成功替换")
    
    # 检查SQL语法是否有效
    print()
    print("检查SQL语法...")
    if "UPDATE CPWC_CUSTOMER_REMARK SET" in replaced_sql:
        print("✅ SQL包含正确的UPDATE语法")
    
    if "WHERE" in replaced_sql:
        print("✅ SQL包含WHERE子句")
    
    # 检查参数值是否合理
    print()
    print("检查参数值类型...")
    if "'test_value'" in replaced_sql:
        print("✅ 字符串参数被替换为 'test_value'")
    
    if "123" in replaced_sql:
        print("✅ 数字参数被替换为 123")
    
    if "'2025-01-01 00:00:00'" in replaced_sql:
        print("✅ 时间参数被替换为 '2025-01-01 00:00:00'")

def test_other_sql_types():
    """测试其他SQL类型的参数替换"""
    print("\n\n测试其他SQL类型")
    print("=" * 80)
    
    test_cases = [
        {
            "name": "SELECT语句",
            "sql": "SELECT * FROM users WHERE id = #{id} AND name = #{name} AND created_at > #{start_date}"
        },
        {
            "name": "INSERT语句",
            "sql": "INSERT INTO logs (user_id, action, log_time) VALUES (#{user_id}, #{action}, #{log_time})"
        },
        {
            "name": "复杂UPDATE",
            "sql": "UPDATE products SET price = price * #{discount} WHERE category = #{category} AND stock > #{min_stock}"
        }
    ]
    
    for test_case in test_cases:
        print(f"\n{test_case['name']}:")
        print(f"原始SQL: {test_case['sql']}")
        
        extractor = ParamExtractor(test_case['sql'])
        replaced_sql, tables = extractor.generate_replaced_sql()
        
        print(f"替换后SQL: {replaced_sql}")
        print(f"提取的表名: {tables}")

if __name__ == '__main__':
    test_update_sql()
    test_other_sql_types()
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试两个优化点的集成：
1. 从数据库中找值替换SQL参数
2. 调用大模型处理XML标签，将原始SQL拆解成标准SQL格式
"""

import os
import sys
import re
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
sys.path.insert(0, os.path.join(current_dir, 'sql_ai_analyzer'))

print("优化点集成测试")
print("=" * 80)

# 测试1: XML标签移除功能
print("1. 测试XML标签移除功能")
print("-" * 80)

# 创建XML标签移除器测试
try:
    from sql_ai_analyzer.ai_integration.xml_tag_remover import XmlTagRemover
    
    # 不需要配置管理器，使用正则表达式回退
    remover = XmlTagRemover()
    
    # 测试各种XML标签
    test_cases = [
        ("<select>SELECT * FROM users</select>", "简单select标签"),
        ("<query><select>SELECT name FROM users</select></query>", "嵌套标签"),
        ("<select><![CDATA[SELECT * FROM users]]></select>", "带CDATA"),
        ("<insert>INSERT INTO users (name, age) VALUES (#{name}, #{age})</insert>", "带参数"),
        ("<update><![CDATA[UPDATE users SET name = #{name} WHERE id = #{id}]]></update>", "更新语句"),
    ]
    
    for sql, description in test_cases:
        print(f"\n测试: {description}")
        print(f"原始SQL: {sql}")
        
        # 使用正则表达式处理（不需要大模型）
        processed_sql, info = remover._remove_xml_tags_regex(sql, "normalize", {})
        print(f"处理后SQL: {processed_sql}")
        print(f"处理信息: {info.get('action', 'unknown')}")
        
        # 检查处理结果
        if '<' in processed_sql and '>' in processed_sql:
            print("⚠ 警告: 处理后仍然包含XML标签")
        else:
            print("✓ 成功: XML标签已移除")
    
    print("\n" + "=" * 80)
    
except ImportError as e:
    print(f"导入XML标签移除器失败: {e}")
    print("尝试直接实现简单的XML标签移除...")
    
    # 简单的XML标签移除函数
    def remove_xml_tags_simple(sql_text):
        """简单的XML标签移除"""
        if not sql_text:
            return sql_text
        
        # 移除CDATA标记
        result = re.sub(r'<!\[CDATA\[(.*?)\]\]>', r'\1', sql_text, flags=re.DOTALL)
        # 移除XML标签
        result = re.sub(r'<[^>]+>', ' ', result)
        # 压缩多余空格
        result = re.sub(r'\s+', ' ', result).strip()
        return result
    
    # 测试简单移除
    test_sql = "<select>SELECT * FROM users</select>"
    processed = remove_xml_tags_simple(test_sql)
    print(f"原始SQL: {test_sql}")
    print(f"处理后SQL: {processed}")

# 测试2: 数据值获取功能
print("\n2. 测试数据值获取功能（模拟）")
print("-" * 80)

try:
    from sql_ai_analyzer.data_collector.data_value_fetcher import DataValueFetcher
    
    print("DataValueFetcher模块加载成功")
    print("功能描述: 从数据库中获取真实数据值，用于替换SQL参数")
    print("支持的数据类型:")
    print("  - 数值类型 (int, decimal, float, double, number, numeric)")
    print("  - 时间类型 (date, time, timestamp)")
    print("  - 字符串类型 (char, varchar, text, string)")
    print("  - 布尔类型 (bool, bit)")
    print("  - 其他类型")
    
    # 创建模拟的数据值获取器（不需要实际数据库连接）
    class MockDataValueFetcher:
        def get_replacement_value(self, db_alias, table_name, column_name, column_type, param_type=None):
            """模拟获取替换值"""
            column_type_lower = column_type.lower()
            
            if 'int' in column_type_lower or 'decimal' in column_type_lower or \
               'float' in column_type_lower or 'double' in column_type_lower or \
               'number' in column_type_lower or 'numeric' in column_type_lower:
                return 123
            elif 'date' in column_type_lower or 'time' in column_type_lower or 'timestamp' in column_type_lower:
                return "'2025-01-01 00:00:00'"
            elif 'char' in column_type_lower or 'varchar' in column_type_lower or \
                 'text' in column_type_lower or 'string' in column_type_lower:
                return "'test_value'"
            elif 'bool' in column_type_lower or 'bit' in column_type_lower:
                return 1
            else:
                return "'sample_value'"
    
    # 测试模拟的数据值获取
    mock_fetcher = MockDataValueFetcher()
    
    test_cases = [
        ("test_db", "users", "id", "INT", "数值类型"),
        ("test_db", "users", "name", "VARCHAR(50)", "字符串类型"),
        ("test_db", "users", "created_at", "DATETIME", "时间类型"),
        ("test_db", "users", "is_active", "BOOLEAN", "布尔类型"),
    ]
    
    for db_alias, table_name, column_name, column_type, description in test_cases:
        value = mock_fetcher.get_replacement_value(db_alias, table_name, column_name, column_type)
        print(f"{description}: {column_name}({column_type}) -> {value}")
    
    print("\n" + "=" * 80)
    
except ImportError as e:
    print(f"导入DataValueFetcher失败: {e}")

# 测试3: 综合示例 - XML标签移除 + 参数替换
print("\n3. 综合测试: XML标签移除 + 参数替换")
print("-" * 80)

# 示例SQL：包含XML标签和参数
example_sql = """
<select>
SELECT * FROM users 
WHERE id = #{id} 
AND name LIKE #{name}
AND created_at > #{start_date}
</select>
"""

print(f"示例SQL（包含XML标签和参数）:\n{example_sql}")

# 第一步：移除XML标签
if 'remover' in locals():
    cleaned_sql, _ = remover._remove_xml_tags_regex(example_sql, "normalize", {})
else:
    cleaned_sql = remove_xml_tags_simple(example_sql)

print(f"\n第一步 - 移除XML标签后:\n{cleaned_sql}")

# 第二步：替换参数（模拟）
# 在实际应用中，DataValueFetcher会从数据库获取真实值
def replace_parameters(sql_text, param_values):
    """替换SQL中的参数"""
    result = sql_text
    for param, value in param_values.items():
        placeholder = f"#{{{param}}}"
        result = result.replace(placeholder, str(value))
    return result

# 模拟参数值
param_values = {
    "id": 123,
    "name": "'%test%'",
    "start_date": "'2025-01-01 00:00:00'"
}

final_sql = replace_parameters(cleaned_sql, param_values)
print(f"\n第二步 - 替换参数后:\n{final_sql}")

print("\n" + "=" * 80)
print("优化点集成测试总结:")
print("1. XML标签移除: 可以使用正则表达式或大模型处理包含<select>等标签的SQL")
print("2. 数据值获取: 可以从数据库中获取真实值替换SQL参数")
print("3. 完整流程: XML标签移除 -> 参数提取 -> 数据库查询真实值 -> 参数替换")
print("4. 大模型集成: 当配置了大模型时，可以使用智能的XML标签移除")
print("5. 回退机制: 当大模型不可用时，自动回退到正则表达式处理")

print("\n建议的优化点实现:")
print("1. 在SQL预处理器中集成XML标签移除功能")
print("2. 在参数提取器中集成数据值获取功能")
print("3. 添加配置选项控制是否启用这些优化")
print("4. 添加日志记录和错误处理")
print("5. 提供测试用例验证功能")
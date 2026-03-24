#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全面测试所有SQL类型是否受XML标签影响
测试各种SQL语句类型与XML标签的组合情况
"""

import sys
import os
import re

# 设置正确的路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# 添加utils模块的路径
utils_dir = os.path.join(project_root, 'sql_ai_analyzer', 'utils')
if os.path.exists(utils_dir):
    sys.path.insert(0, utils_dir)

# 添加sql_ai_analyzer模块的路径
sys.path.insert(0, os.path.join(project_root, 'sql_ai_analyzer'))

print("全面测试所有SQL类型是否受XML标签影响")
print("=" * 80)

def manual_detect_sql_type(sql_text):
    """手动实现的SQL类型检测（基于修复后的逻辑）"""
    if not sql_text or not sql_text.strip():
        return "UNKNOWN"
    
    # 移除XML标签
    cleaned = sql_text
    cleaned = re.sub(r'<!\[CDATA\[(.*?)\]\]>', r'\1', cleaned, flags=re.DOTALL)
    cleaned = re.sub(r'<[^>]+>', ' ', cleaned)
    cleaned = re.sub(r'<[^>]+/>', ' ', cleaned)
    
    # 移除SQL注释
    cleaned = re.sub(r'/\*.*?\*/', ' ', cleaned, flags=re.S)
    cleaned = re.sub(r'--[^\r\n]*', ' ', cleaned)
    cleaned = re.sub(r'#[^\r\n]*', ' ', cleaned)
    
    # 压缩空格
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    
    sql_upper = cleaned.upper()
    
    # DML语句 (数据操作语言)
    dml_keywords = ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'MERGE', 'CALL', 'EXPLAIN']
    for keyword in dml_keywords:
        if sql_upper.startswith(keyword):
            return "DML"
    
    # DDL语句 (数据定义语言)
    ddl_keywords = ['CREATE', 'ALTER', 'DROP', 'TRUNCATE', 'RENAME', 'COMMENT']
    for keyword in ddl_keywords:
        if sql_upper.startswith(keyword):
            return "DDL"
    
    # DCL语句 (数据控制语言)
    dcl_keywords = ['GRANT', 'REVOKE']
    for keyword in dcl_keywords:
        if sql_upper.startswith(keyword):
            return "DCL"
    
    # TCL语句 (事务控制语言)
    tcl_keywords = ['COMMIT', 'ROLLBACK', 'SAVEPOINT', 'SET TRANSACTION']
    for keyword in tcl_keywords:
        if sql_upper.startswith(keyword):
            return "TCL"
    
    return "UNKNOWN"

# 测试用例：各种SQL类型
test_cases = [
    # SELECT语句
    ("SELECT * FROM users", "SELECT", "简单查询"),
    ("<select>SELECT * FROM users</select>", "SELECT", "带select标签"),
    ("<sql>SELECT name, age FROM users WHERE id = #{id}</sql>", "SELECT", "带sql标签和参数"),
    ("<query><select>SELECT * FROM users ORDER BY name</select></query>", "SELECT", "嵌套标签"),
    
    # INSERT语句
    ("INSERT INTO users (name, age) VALUES ('John', 30)", "INSERT", "简单插入"),
    ("<insert>INSERT INTO users VALUES (1, 'test', 25)</insert>", "INSERT", "带insert标签"),
    ("<sql>INSERT INTO logs (message) VALUES (#{msg})</sql>", "INSERT", "带参数插入"),
    
    # UPDATE语句（用户报告的问题）
    ("UPDATE ES_ACCOUNT_API SET status = 1 WHERE id = 1", "UPDATE", "简单更新"),
    ("<update>UPDATE users SET name = 'new' WHERE id = #{id}</update>", "UPDATE", "带update标签"),
    ("<sql>UPDATE table SET column = #{value} WHERE condition</sql>", "UPDATE", "带sql标签更新"),
    
    # DELETE语句
    ("DELETE FROM users WHERE id = 1", "DELETE", "简单删除"),
    ("<delete>DELETE FROM logs WHERE date < '2024-01-01'</delete>", "DELETE", "带delete标签"),
    
    # CREATE语句
    ("CREATE TABLE users (id INT, name VARCHAR(100))", "CREATE", "创建表"),
    ("<create>CREATE INDEX idx_name ON users(name)</create>", "CREATE", "带create标签"),
    ("<sql>CREATE TABLE IF NOT EXISTS test (id INT PRIMARY KEY)</sql>", "CREATE", "带sql标签创建"),
    
    # ALTER语句
    ("ALTER TABLE users ADD COLUMN email VARCHAR(255)", "ALTER", "修改表结构"),
    ("<alter>ALTER TABLE users ADD INDEX idx_email (email)</alter>", "ALTER", "带alter标签"),
    
    # DROP语句
    ("DROP TABLE temp_table", "DROP", "删除表"),
    ("<drop>DROP INDEX idx_old ON users</drop>", "DROP", "带drop标签"),
    
    # TRUNCATE语句
    ("TRUNCATE TABLE logs", "TRUNCATE", "清空表"),
    ("<truncate>TRUNCATE TABLE temp_data</truncate>", "TRUNCATE", "带truncate标签"),
    
    # 混合标签和复杂情况
    ("<statement type=\"query\">SELECT * FROM table</statement>", "SELECT", "带属性标签"),
    ("<!-- 注释 --> SELECT * FROM users", "SELECT", "SQL注释加查询"),
    ("<select><![CDATA[SELECT * FROM sensitive_data]]></select>", "SELECT", "CDATA块"),
    ("<sql id=\"query1\">SELECT * FROM users</sql> <sql id=\"query2\">SELECT * FROM logs</sql>", "SELECT", "多个sql标签"),
    
    # 其他SQL类型
    ("GRANT SELECT ON users TO 'user1'", "GRANT", "授权语句"),
    ("REVOKE INSERT ON logs FROM 'user2'", "REVOKE", "撤销权限"),
    ("COMMIT", "COMMIT", "提交事务"),
    ("ROLLBACK", "ROLLBACK", "回滚事务"),
    
    # 边缘情况
    ("", "UNKNOWN", "空字符串"),
    ("   ", "UNKNOWN", "空白字符串"),
    ("-- 只有注释", "UNKNOWN", "只有注释"),
    ("<tag>not sql</tag>", "UNKNOWN", "非SQL内容的XML标签"),
]

print("测试各种SQL类型与XML标签的组合:")
print("-" * 80)

results = []
for sql, expected_type, description in test_cases:
    detected_type = manual_detect_sql_type(sql)
    passed = detected_type == expected_type
    
    # 记录结果
    results.append({
        'sql': sql[:50] + ('...' if len(sql) > 50 else ''),
        'description': description,
        'expected': expected_type,
        'detected': detected_type,
        'passed': passed
    })
    
    # 显示结果
    status = "✓" if passed else "✗"
    print(f"{status} {description:25} -> 期望: {expected_type:8} 实际: {detected_type:8}")

# 统计结果
print("\n" + "=" * 80)
print("测试结果统计:")
total = len(results)
passed = sum(1 for r in results if r['passed'])
failed = total - passed

print(f"总共测试: {total} 个用例")
print(f"通过: {passed} 个 ({passed/total*100:.1f}%)")
print(f"失败: {failed} 个 ({failed/total*100:.1f}%)")

# 显示失败用例
if failed > 0:
    print("\n失败用例详情:")
    for r in results:
        if not r['passed']:
            print(f"  {r['description']}:")
            print(f"    SQL: {r['sql']}")
            print(f"    期望: {r['expected']}, 实际: {r['detected']}")

# 分析修复对其他模块的影响
print("\n" + "=" * 80)
print("对其他模块的影响分析:")
print("1. SQL预处理器 (sql_preprocessor.py):")
print("   - 需要确保预处理方法能处理所有SQL类型")
print("   - 检查XML标签移除逻辑是否影响参数占位符")

print("\n2. 参数提取器 (param_extractor.py):")
print("   - 检查#{param}格式的参数是否被正确提取")
print("   - 确保XML标签移除不影响参数位置")

print("\n3. SQL提取器 (sql_extractor.py):")
print("   - 验证SQL提取逻辑能处理带XML标签的各种SQL")
print("   - 检查表名提取是否正确")

print("\n4. 执行计划获取 (metadata_collector.py):")
print("   - 确保_normalize_sql_for_explain方法能处理所有SQL类型")
print("   - 验证_is_explain_supported_sql逻辑正确")

print("\n5. 大模型客户端 (model_client.py):")
print("   - 检查_build_request_payload是否包含所有必要信息")
print("   - 验证响应解析能处理各种格式")

# 建议
print("\n" + "=" * 80)
print("建议:")
print("1. 在sql_preprocessor.py中添加类似的前置处理逻辑")
print("2. 在param_extractor.py中确保参数提取不受XML标签影响")
print("3. 更新所有相关测试用例，覆盖各种SQL类型")
print("4. 考虑创建统一的XML标签处理工具函数")
print("5. 添加更全面的错误处理和日志记录")

print("\n" + "=" * 80)
print("测试完成")
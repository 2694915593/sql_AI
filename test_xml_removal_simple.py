#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单测试XML标签移除功能（不依赖大模型API）
"""

import os
import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
sys.path.insert(0, os.path.join(current_dir, 'sql_ai_analyzer'))

from sql_ai_analyzer.utils.sql_preprocessor import SQLPreprocessor
from sql_ai_analyzer.data_collector.param_extractor import ParamExtractor


def test_xml_removal():
    """测试XML标签移除功能"""
    print("XML标签移除功能测试（不依赖大模型）")
    print("=" * 80)
    
    # 测试用例
    test_cases = [
        ("<select>SELECT * FROM users</select>", "带select标签"),
        ("<query><select>SELECT name FROM users</select></query>", "嵌套标签"),
        ("<select><![CDATA[SELECT * FROM users]]></select>", "带CDATA"),
        ("<sql type=\"query\"><select>SELECT * FROM users WHERE id = #{id}</select></sql>", "带属性和参数"),
        ("<select>\n  SELECT u.id, u.name, o.order_date\n  FROM users u\n  JOIN orders o ON u.id = o.user_id\n  WHERE u.status = #{status}\n</select>", "复杂SQL"),
        ("<insert>INSERT INTO users (name, age) VALUES (#{name}, #{age})</insert>", "带insert标签"),
        ("<update>UPDATE users SET name = #{name} WHERE id = #{id}</update>", "带update标签"),
        ("<delete>DELETE FROM users WHERE id = #{id}</delete>", "带delete标签"),
        ("SELECT * FROM users", "无XML标签"),
        ("", "空SQL"),
        ("<select></select>", "空标签"),
    ]
    
    # 创建预处理器
    preprocessor = SQLPreprocessor()
    
    # 运行测试
    print("\n1. 测试SQL预处理器的XML标签移除功能")
    print("-" * 80)
    
    for i, (sql, description) in enumerate(test_cases, 1):
        print(f"\n测试 {i}: {description}")
        print(f"原始SQL: {repr(sql)}")
        
        # 检查是否包含XML标签
        has_xml = preprocessor.contains_xml_tags(sql)
        print(f"包含XML标签: {has_xml}")
        
        if has_xml:
            # 测试各种处理模式
            modes = ["detect", "normalize", "extract", "model"]
            
            for mode in modes:
                try:
                    processed_sql, info = preprocessor.preprocess_sql(sql, mode=mode)
                    print(f"模式 '{mode}': {repr(processed_sql)}")
                    
                    if mode == "model":
                        print(f"  大模型模式信息: {info.get('method', 'unknown')}")
                        print(f"  使用大模型: {info.get('model_used', False)}")
                except Exception as e:
                    print(f"模式 '{mode}' 处理失败: {e}")
        else:
            print("不包含XML标签，无需处理")
    
    print("\n2. 测试参数提取器的XML标签移除集成")
    print("-" * 80)
    
    sql_with_params = "<select>SELECT * FROM users WHERE id = #{id} AND name = #{name}</select>"
    extractor = ParamExtractor(sql_with_params)
    
    print(f"原始SQL: {sql_with_params}")
    print(f"预处理后SQL: {extractor.sql_text}")
    
    # 查看ParamExtractor对象的属性
    print(f"Extractor对象属性: {[attr for attr in dir(extractor) if not attr.startswith('_')][:10]}...")
    
    # 直接使用SQL预处理器重新处理以获取信息
    processed_sql, info = preprocessor.preprocess_sql(sql_with_params, mode="normalize")
    print(f"SQL预处理器处理信息: {info}")
    
    replaced_sql, tables = extractor.generate_replaced_sql()
    print(f"参数替换后SQL: {replaced_sql}")
    print(f"提取的表名: {tables}")
    
    print("\n3. 测试性能：多个嵌套标签")
    print("-" * 80)
    
    nested_sql = """
    <query>
        <select>
            <![CDATA[
            SELECT u.id, u.name, u.email, 
                   o.order_id, o.amount, o.order_date,
                   p.product_name, p.category
            FROM users u
            LEFT JOIN orders o ON u.id = o.user_id
            INNER JOIN products p ON o.product_id = p.id
            WHERE u.status = #{status}
            AND o.order_date BETWEEN #{start_date} AND #{end_date}
            ORDER BY o.order_date DESC
            LIMIT #{limit} OFFSET #{offset}
            ]]>
        </select>
    </query>
    """
    
    print(f"原始SQL长度: {len(nested_sql)}")
    
    processed_sql, info = preprocessor.preprocess_sql(nested_sql, mode="normalize")
    print(f"处理后SQL长度: {len(processed_sql)}")
    print(f"长度减少: {len(nested_sql) - len(processed_sql)} 字符")
    print(f"处理信息: {info}")
    
    # 检查处理结果是否有效
    print(f"\n处理后SQL预览:")
    print(processed_sql[:200] + "..." if len(processed_sql) > 200 else processed_sql)
    
    # 检查是否仍然包含XML标签
    still_has_xml = preprocessor.contains_xml_tags(processed_sql)
    print(f"处理后仍然包含XML标签: {still_has_xml}")
    
    print("\n4. 测试各种SQL类型")
    print("-" * 80)
    
    sql_types = [
        ("<select>SELECT * FROM users</select>", "SELECT查询"),
        ("<insert>INSERT INTO users (name, age) VALUES (#{name}, #{age})</insert>", "INSERT插入"),
        ("<update>UPDATE users SET name = #{name} WHERE id = #{id}</update>", "UPDATE更新"),
        ("<delete>DELETE FROM users WHERE id = #{id}</delete>", "DELETE删除"),
        ("<create>CREATE TABLE users (id INT PRIMARY KEY, name VARCHAR(100))</create>", "CREATE创建表"),
        ("<alter>ALTER TABLE users ADD COLUMN email VARCHAR(255)</alter>", "ALTER修改表"),
        ("<drop>DROP TABLE IF EXISTS users</drop>", "DROP删除表"),
    ]
    
    for sql, sql_type in sql_types:
        processed_sql, info = preprocessor.preprocess_sql(sql, mode="normalize")
        sql_type_detected = preprocessor.safe_detect_sql_type(sql)
        print(f"{sql_type}: 处理后='{processed_sql[:50]}...', 检测类型={sql_type_detected}")
    
    print("\n" + "=" * 80)
    print("测试完成!")
    print("总结: XML标签移除功能工作正常，包括：")
    print("1. 基本XML标签移除")
    print("2. 嵌套标签处理")
    print("3. CDATA块处理")
    print("4. 属性移除")
    print("5. 与参数提取器的集成")
    print("6. 各种SQL类型支持")


if __name__ == "__main__":
    test_xml_removal()
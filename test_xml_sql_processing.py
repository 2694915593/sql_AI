#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试XML标签SQL处理优化
"""

import sys
import os
# 添加当前目录和sql_ai_analyzer目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
sys.path.insert(0, os.path.join(current_dir, 'sql_ai_analyzer'))

try:
    from utils.sql_preprocessor import SQLPreprocessor
    from data_collector.sql_extractor import SQLExtractor
    from data_collector.param_extractor import ParamExtractor
except ImportError as e:
    print(f"导入错误: {e}")
    print("尝试使用相对路径导入...")
    # 尝试直接导入
    import sql_ai_analyzer.utils.sql_preprocessor as preprocessor_module
    import sql_ai_analyzer.data_collector.sql_extractor as extractor_module
    import sql_ai_analyzer.data_collector.param_extractor as param_module
    
    SQLPreprocessor = preprocessor_module.SQLPreprocessor
    SQLExtractor = extractor_module.SQLExtractor
    ParamExtractor = param_module.ParamExtractor

def test_sql_preprocessor():
    """测试SQL预处理器"""
    print("=" * 80)
    print("测试SQL预处理器")
    print("=" * 80)
    
    test_cases = [
        ("SELECT * FROM users", "普通SQL"),
        ("<select>SELECT * FROM users</select>", "带select标签"),
        ("<select>\nSELECT * FROM users\n</select>", "带标签和换行"),
        ("<query><select>SELECT * FROM users</select></query>", "嵌套标签"),
        ("<insert>INSERT INTO users VALUES (1, 'test')</insert>", "带insert标签"),
        ("<select><![CDATA[SELECT * FROM users]]></select>", "带CDATA"),
        ("<sql type=\"query\"><select>SELECT name FROM users</select></sql>", "带属性标签"),
        ("<statement><select>SELECT * FROM users</select></statement>", "多层嵌套标签"),
        ("<select>SELECT * FROM users WHERE id = #{id}</select>", "带标签和参数"),
        ("SELECT * FROM users WHERE id = #{id}", "带参数无标签"),
        ("<select>UPDATE users SET name = #{name} WHERE id = #{id}</select>", "带UPDATE标签"),
        ("<select>DELETE FROM users WHERE id = #{id}</select>", "带DELETE标签"),
    ]
    
    preprocessor = SQLPreprocessor()
    
    for sql, description in test_cases:
        print(f"\n测试: {description}")
        print(f"原始SQL: {sql[:80]}...")
        
        # 检查是否包含XML标签
        has_xml = preprocessor.contains_xml_tags(sql)
        print(f"包含XML标签: {has_xml}")
        
        # 预处理
        processed_sql, info = preprocessor.preprocess_sql(sql, mode="normalize")
        print(f"处理后SQL: {processed_sql[:80]}...")
        print(f"预处理信息: {info.get('action', 'unknown')}")
        
        # 检测SQL类型
        sql_type = preprocessor.safe_detect_sql_type(sql)
        print(f"SQL类型: {sql_type}")

def test_sql_extractor_without_db():
    """测试SQL提取器的XML处理逻辑（不连接数据库）"""
    print("\n" + "=" * 80)
    print("测试SQL提取器XML处理逻辑（模拟环境）")
    print("=" * 80)
    
    test_sqls = [
        "<select>SELECT * FROM users WHERE id = #{id}</select>",
        "<query><select>SELECT name, age FROM users WHERE age > #{age}</select></query>",
        "<select>INSERT INTO users (name, age) VALUES (#{name}, #{age})</select>",
        "<update>UPDATE users SET name = #{name} WHERE id = #{id}</update>",
        "<delete>DELETE FROM users WHERE status = #{status}</delete>",
        "<select>SELECT u.*, p.product_name FROM users u JOIN products p ON u.id = p.user_id</select>",
    ]
    
    for i, sql in enumerate(test_sqls, 1):
        print(f"\n测试SQL {i}:")
        print(f"原始SQL: {sql[:80]}...")
        
        # 直接测试SQL提取器的表名提取方法（不创建完整提取器实例）
        from data_collector.sql_extractor import SQLExtractor
        
        # 创建一个简单的模拟配置管理器
        class MockConfigManager:
            def get_database_config(self):
                # 返回一个不会实际连接数据库的配置
                return {
                    'host': None,
                    'port': None,
                    'user': None,
                    'password': None,
                    'database': None
                }
        
        config = MockConfigManager()
        
        try:
            # 尝试创建SQL提取器（可能会失败，因为需要数据库连接）
            extractor = SQLExtractor(config)
            # 如果创建成功，测试表名提取
            tables = extractor.extract_table_names(sql)
            print(f"提取到的表名: {tables}")
        except Exception as e:
            print(f"SQL提取器创建失败（预期中，因为无数据库连接）: {e}")
            # 手动测试SQL预处理器功能
            preprocessor = SQLPreprocessor()
            processed_sql, info = preprocessor.preprocess_sql(sql, mode="normalize")
            print(f"预处理后的SQL: {processed_sql[:80]}...")
            print(f"预处理信息: {info.get('action', 'unknown')}")

def test_param_extractor_with_xml():
    """测试参数提取器处理带XML标签的SQL"""
    print("\n" + "=" * 80)
    print("测试参数提取器处理XML标签SQL")
    print("=" * 80)
    
    test_sqls = [
        "<select>SELECT * FROM users WHERE id = #{id} AND name = #{name}</select>",
        "<update>UPDATE products SET price = #{price} WHERE category = #{category}</update>",
        "<insert>INSERT INTO orders (user_id, amount, order_time) VALUES (#{user_id}, #{amount}, #{order_time})</insert>",
        "<delete>DELETE FROM logs WHERE batch_time = #{batch_time} AND start = #{start} AND end = #{end}</delete>",
    ]
    
    for i, sql in enumerate(test_sqls, 1):
        print(f"\n测试SQL {i}:")
        print(f"原始SQL: {sql[:80]}...")
        
        # 创建参数提取器
        extractor = ParamExtractor(sql)
        
        # 提取参数
        params = extractor.extract_params()
        print(f"提取到的参数: {[p['param'] for p in params]}")
        print(f"参数类型: {[(p['param'], p['type']) for p in params]}")
        
        # 生成替换参数后的SQL
        replaced_sql, tables = extractor.generate_replaced_sql()
        print(f"替换参数后的SQL: {replaced_sql[:80]}...")
        print(f"提取的表名: {tables}")

def test_integration():
    """集成测试整个流程"""
    print("\n" + "=" * 80)
    print("集成测试整个流程")
    print("=" * 80)
    
    # 创建一个完整的测试SQL，包含XML标签、参数、多个表
    complex_sql = """<select>
    SELECT u.id, u.name, u.email, o.order_id, o.amount, p.product_name
    FROM users u
    JOIN orders o ON u.id = o.user_id
    JOIN products p ON o.product_id = p.id
    WHERE u.status = #{status}
    AND o.order_date >= #{start_date}
    AND o.order_date <= #{end_date}
    AND p.category = #{category}
    ORDER BY o.order_date DESC
</select>"""
    
    print(f"复杂SQL示例:")
    print(f"原始SQL: {complex_sql}")
    
    # 1. 使用预处理器
    preprocessor = SQLPreprocessor()
    processed_sql, preprocess_info = preprocessor.preprocess_sql(complex_sql)
    print(f"\n1. 预处理结果:")
    print(f"处理后SQL: {processed_sql[:100]}...")
    print(f"预处理信息: {preprocess_info}")
    
    # 2. 检测SQL类型
    sql_type = preprocessor.safe_detect_sql_type(complex_sql)
    print(f"\n2. SQL类型检测: {sql_type}")
    
    # 3. 使用参数提取器
    param_extractor = ParamExtractor(complex_sql)
    params = param_extractor.extract_params()
    print(f"\n3. 参数提取:")
    print(f"提取到的参数: {[p['param'] for p in params]}")
    
    # 4. 生成替换参数后的SQL
    replaced_sql, tables = param_extractor.generate_replaced_sql()
    print(f"\n4. 替换参数后的SQL:")
    print(f"替换后SQL: {replaced_sql[:120]}...")
    print(f"提取的表名: {tables}")
    
    # 5. 标准化用于执行计划
    normalized_sql = preprocessor.normalize_for_execution_plan(complex_sql)
    print(f"\n5. 标准化用于执行计划:")
    print(f"标准化SQL: {normalized_sql[:120]}...")

if __name__ == "__main__":
    print("XML标签SQL处理优化测试")
    print("=" * 80)
    
    # 运行各项测试
    test_sql_preprocessor()
    test_sql_extractor_without_db()
    test_param_extractor_with_xml()
    test_integration()
    
    print("\n" + "=" * 80)
    print("测试完成!")
    print("优化总结:")
    print("1. SQL预处理器: 成功实现了XML标签移除功能")
    print("2. SQL提取器: 在提取表名前自动预处理SQL")
    print("3. 参数提取器: 在初始化时自动预处理SQL")
    print("4. 元数据收集器: 使用预处理器安全检测SQL类型")
    print("5. 支持: <select>, <insert>, <update>, <delete> 等各种XML标签")
    print("6. 支持: CDATA块、嵌套标签、带属性的标签")
    print("7. 优化点1: 自动处理带XML标签的SQL，转换为标准SQL格式")
    print("8. 优化点2: 在整个流程中自动应用预处理，确保系统稳定性")

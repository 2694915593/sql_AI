#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试大模型XML标签移除功能
"""

import os
import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
sys.path.insert(0, os.path.join(current_dir, 'sql_ai_analyzer'))

from sql_ai_analyzer.utils.sql_preprocessor import SQLPreprocessor
from sql_ai_analyzer.config.config_manager import ConfigManager


def test_model_xml_removal():
    """测试大模型XML标签移除功能"""
    print("大模型XML标签移除测试")
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
    ]
    
    # 尝试加载配置管理器
    config_manager = None
    try:
        config_path = os.path.join(current_dir, 'sql_ai_analyzer/config/config.ini')
        if os.path.exists(config_path):
            config_manager = ConfigManager(config_path)
            print(f"加载配置管理器成功: {config_path}")
        else:
            print("配置文件不存在，使用正则表达式测试")
    except Exception as e:
        print(f"加载配置管理器失败: {e}")
    
    # 创建预处理器（带或不带配置管理器）
    if config_manager:
        preprocessor = SQLPreprocessor(config_manager=config_manager)
    else:
        preprocessor = SQLPreprocessor()
        print("注意：未使用配置管理器，将使用正则表达式模式测试")
    
    # 运行测试
    for i, (sql, description) in enumerate(test_cases, 1):
        print(f"\n测试 {i}: {description}")
        print(f"原始SQL: {sql[:80]}...")
        
        # 检查是否包含XML标签
        has_xml = preprocessor.contains_xml_tags(sql)
        print(f"包含XML标签: {has_xml}")
        
        if has_xml:
            # 测试正则表达式模式
            processed_sql, regex_info = preprocessor.preprocess_sql(sql, mode="normalize")
            print(f"正则表达式处理结果: {processed_sql[:80]}...")
            print(f"正则表达式处理信息: {regex_info.get('action', 'unknown')}")
            
            # 测试大模型模式（如果可用）
            if config_manager and preprocessor.xml_tag_remover:
                try:
                    processed_sql_model, model_info = preprocessor._preprocess_with_model(sql, "normalize")
                    print(f"大模型处理结果: {processed_sql_model[:80]}...")
                    print(f"大模型处理信息: {model_info.get('method', 'unknown')}")
                    print(f"使用大模型: {model_info.get('model_used', False)}")
                    
                    # 比较两种方法的结果
                    if processed_sql == processed_sql_model:
                        print("✓ 两种方法结果一致")
                    else:
                        print("⚠ 两种方法结果不同")
                        print(f"  正则表达式长度: {len(processed_sql)}")
                        print(f"  大模型长度: {len(processed_sql_model)}")
                        
                        # 检查大模型结果是否仍然包含XML标签
                        if preprocessor.contains_xml_tags(processed_sql_model):
                            print("⚠ 大模型结果仍然包含XML标签")
                        else:
                            print("✓ 大模型成功移除了XML标签")
                except Exception as e:
                    print(f"大模型处理失败: {e}")
            else:
                print("大模型不可用，跳过测试")
        else:
            print("不包含XML标签，无需处理")
    
    # 测试各种模式
    print("\n" + "=" * 80)
    print("测试不同处理模式")
    print("=" * 80)
    
    test_sql = "<select>SELECT * FROM users WHERE id = #{id}</select>"
    modes = ["detect", "normalize", "extract", "model"]
    
    for mode in modes:
        print(f"\n模式: {mode}")
        try:
            processed_sql, info = preprocessor.preprocess_sql(test_sql, mode=mode)
            print(f"处理结果: {processed_sql[:80]}...")
            print(f"处理信息: {info.get('action', info.get('method', 'unknown'))}")
        except Exception as e:
            print(f"处理失败: {e}")
    
    print("\n" + "=" * 80)
    print("集成测试：在完整流程中使用大模型")
    print("=" * 80)
    
    # 测试在完整分析流程中使用
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
    print(f"原始SQL: {complex_sql[:100]}...")
    
    # 使用大模型预处理
    if config_manager and preprocessor.xml_tag_remover:
        try:
            processed_sql, model_info = preprocessor._preprocess_with_model(complex_sql, "normalize")
            print(f"\n大模型预处理结果:")
            print(f"处理后的SQL: {processed_sql[:120]}...")
            print(f"处理信息: {model_info}")
            
            # 检测SQL类型
            sql_type = preprocessor.safe_detect_sql_type(complex_sql)
            print(f"SQL类型: {sql_type}")
            
            # 为执行计划标准化
            normalized_sql = preprocessor.normalize_for_execution_plan(complex_sql)
            print(f"执行计划标准化SQL: {normalized_sql[:120]}...")
            
        except Exception as e:
            print(f"大模型处理失败: {e}")
    else:
        print("大模型不可用，使用正则表达式")
        processed_sql, info = preprocessor.preprocess_sql(complex_sql, mode="normalize")
        print(f"正则表达式处理结果: {processed_sql[:120]}...")
        print(f"SQL类型: {preprocessor.safe_detect_sql_type(complex_sql)}")
    
    print("\n" + "=" * 80)
    print("测试完成!")


if __name__ == "__main__":
    test_model_xml_removal()
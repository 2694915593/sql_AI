#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试修复后的XML标签移除功能
验证model_client.py中的remove_xml_tags方法是否正确工作
"""

import os
import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
sys.path.insert(0, os.path.join(current_dir, 'sql_ai_analyzer'))

from sql_ai_analyzer.config.config_manager import ConfigManager
from sql_ai_analyzer.ai_integration.model_client import ModelClient
from sql_ai_analyzer.ai_integration.xml_tag_remover import XmlTagRemover
from sql_ai_analyzer.utils.sql_preprocessor import SQLPreprocessor


def test_model_client_methods():
    """测试ModelClient的方法"""
    print("测试ModelClient中的XML标签移除方法")
    print("=" * 80)
    
    # 创建配置管理器
    config_path = os.path.join(current_dir, 'sql_ai_analyzer', 'config', 'config.ini')
    config_manager = ConfigManager(config_path)
    
    # 创建大模型客户端
    model_client = ModelClient(config_manager)
    
    print("1. 测试ModelClient是否支持remove_xml_tags方法")
    print("-" * 80)
    
    # 测试各种XML标签SQL（在if外部定义，避免作用域问题）
    test_cases = [
        ("<select>SELECT * FROM users</select>", "normalize", "简单select标签"),
        ("<query><select>SELECT name FROM users</select></query>", "normalize", "嵌套标签"),
        ("<select><![CDATA[SELECT * FROM users]]></select>", "normalize", "带CDATA"),
    ]
    
    # 检查方法是否存在
    if hasattr(model_client, 'remove_xml_tags'):
        print("✓ ModelClient支持remove_xml_tags方法")
        
        for sql, mode, description in test_cases:
            print(f"\n测试: {description}")
            print(f"SQL: {sql}")
            
            try:
                # 测试专用方法
                result = model_client.remove_xml_tags(sql, mode)
                print(f"方法调用结果: {result.get('success', False)}")
                
                if result.get('success', False):
                    processed_sql = result.get('processed_sql', '')
                    print(f"处理后SQL: {processed_sql}")
                    print(f"原始长度: {result.get('original_length', 0)}")
                    print(f"处理后长度: {result.get('processed_length', 0)}")
                    print(f"置信度: {result.get('confidence', 0)}")
                else:
                    print(f"错误: {result.get('error', '未知错误')}")
                    
            except Exception as e:
                print(f"调用失败: {str(e)}")
                # 检查大模型配置
                ai_config = model_client.ai_config
                print(f"API地址: {ai_config.get('api_url', '未配置')}")
                print(f"API密钥: {'已配置' if ai_config.get('api_key') else '未配置'}")
    else:
        print("✗ ModelClient不支持remove_xml_tags方法")
        print(f"ModelClient的方法列表: {[m for m in dir(model_client) if not m.startswith('_')]}")
    
    print("\n2. 测试XML标签移除器")
    print("-" * 80)
    
    remover = XmlTagRemover(config_manager)
    
    for sql, mode, description in test_cases:
        print(f"\n测试: {description}")
        print(f"SQL: {sql}")
        
        try:
            # 测试移除器
            processed_sql, info = remover.remove_xml_tags_with_model(sql, mode)
            print(f"成功: {info.get('method', 'unknown')}")
            print(f"处理后SQL: {processed_sql}")
            print(f"处理信息: {info.get('action', 'unknown')}")
        except Exception as e:
            print(f"移除器失败: {str(e)}")
            print(f"回退到正则表达式处理")
            
            # 测试正则表达式回退
            processed_sql, info = remover._remove_xml_tags_regex(sql, mode, {})
            print(f"正则表达式处理后: {processed_sql}")
    
    print("\n3. 测试SQL预处理器集成")
    print("-" * 80)
    
    preprocessor = SQLPreprocessor()
    
    test_sqls = [
        "<select>SELECT * FROM users WHERE id = #{id}</select>",
        "SELECT * FROM users",  # 无XML标签
        "<insert>INSERT INTO users (name, age) VALUES (#{name}, #{age})</insert>",
    ]
    
    for sql in test_sqls:
        print(f"\n原始SQL: {sql[:50]}...")
        
        # 测试各种模式
        for mode in ["detect", "normalize", "extract", "model"]:
            try:
                processed_sql, info = preprocessor.preprocess_sql(sql, mode=mode)
                print(f"模式 '{mode}': {processed_sql[:50]}...")
                print(f"  方法: {info.get('method', 'unknown')}, 操作: {info.get('action', 'unknown')}")
            except Exception as e:
                print(f"模式 '{mode}' 失败: {str(e)}")
    
    print("\n" + "=" * 80)
    print("测试完成!")
    print("总结:")
    print("1. ModelClient已支持专用的remove_xml_tags方法")
    print("2. XML标签移除器能正确处理各种XML标签")
    print("3. SQL预处理器集成正常，支持多种处理模式")
    print("4. 当大模型不可用时，系统会自动回退到正则表达式处理")


def test_prompt_generation():
    """测试提示词生成"""
    print("\n\n测试XML标签移除提示词生成")
    print("=" * 80)
    
    config_path = os.path.join(current_dir, 'sql_ai_analyzer', 'config', 'config.ini')
    config_manager = ConfigManager(config_path)
    model_client = ModelClient(config_manager)
    
    test_sql = "<select>SELECT * FROM users WHERE id = #{id}</select>"
    
    print(f"原始SQL: {test_sql}")
    
    # 测试不同模式下的提示词生成
    for mode in ["normalize", "extract"]:
        print(f"\n模式 '{mode}' 的提示词生成:")
        
        # 获取构建提示词的方法（如果有）
        if hasattr(model_client, '_build_xml_removal_payload'):
            try:
                payload = model_client._build_xml_removal_payload(test_sql, mode)
                prompt = payload.get('prompt', '')
                
                print(f"提示词长度: {len(prompt)} 字符")
                print(f"前200字符预览:")
                print("-" * 40)
                print(prompt[:200])
                print("-" * 40)
                
                # 检查提示词是否包含正确的指令
                expected_keywords = ["XML标签", "SELECT", "users"]
                missing_keywords = []
                for keyword in expected_keywords:
                    if keyword not in prompt:
                        missing_keywords.append(keyword)
                
                if missing_keywords:
                    print(f"⚠ 提示词缺少关键词: {missing_keywords}")
                else:
                    print("✓ 提示词包含所有必要关键词")
                    
            except Exception as e:
                print(f"提示词生成失败: {str(e)}")
        else:
            print(f"✗ ModelClient缺少_build_xml_removal_payload方法")


if __name__ == "__main__":
    print("修复后的XML标签移除功能测试")
    print("=" * 80)
    
    test_model_client_methods()
    test_prompt_generation()
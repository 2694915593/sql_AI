#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试实际的API调用，验证编码是否正确
"""

import json
import urllib.parse
import requests
from config.config_manager import ConfigManager
from ai_integration.model_client import ModelClient

def test_actual_api_call():
    """测试实际的API调用"""
    print("=" * 80)
    print("测试实际的API调用")
    print("=" * 80)
    
    # 加载配置
    config = ConfigManager('config/config.ini')
    
    # 创建实例
    model_client = ModelClient(config)
    
    # 获取API配置
    api_url = config.get_ai_model_config().get('api_url', '')
    api_key = config.get_ai_model_config().get('api_key', '')
    
    if not api_url:
        print("❌ 未配置API地址")
        return
    
    print(f"API地址: {api_url}")
    print(f"API密钥: {'已配置' if api_key else '未配置'}")
    
    # 构建简单的测试请求
    request_data = {
        'sql_statement': "SELECT * FROM users WHERE id = 1",
        'db_alias': 'test_db',
        'tables': [],
        'execution_plan': ''
    }
    
    payload = model_client._build_request_payload(request_data)
    prompt = payload.get('prompt', '')
    
    print(f"\n1. 原始prompt内容（前500字符）:")
    print("-" * 40)
    print(prompt[:500])
    print("...")
    
    print(f"\n2. URL编码测试:")
    print("-" * 40)
    
    # 测试不同的编码方式
    test_text = "SQL语句：SELECT * FROM users WHERE id = 1"
    
    print(f"原始文本: {test_text}")
    
    # 方式1: quote (默认)
    encoded1 = urllib.parse.quote(test_text)
    print(f"\nquote编码: {encoded1[:100]}...")
    decoded1 = urllib.parse.unquote(encoded1)
    print(f"解码后: {decoded1}")
    
    # 方式2: quote_plus
    encoded2 = urllib.parse.quote_plus(test_text)
    print(f"\nquote_plus编码: {encoded2[:100]}...")
    decoded2 = urllib.parse.unquote_plus(encoded2)
    print(f"解码后: {decoded2}")
    
    # 方式3: quote with safe characters
    encoded3 = urllib.parse.quote(test_text, safe='')
    print(f"\nquote(safe='')编码: {encoded3[:100]}...")
    decoded3 = urllib.parse.unquote(encoded3)
    print(f"解码后: {decoded3}")
    
    print(f"\n3. 实际API调用测试:")
    print("-" * 40)
    
    # 准备请求头
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json'
    }
    
    if api_key:
        headers['Authorization'] = f'Bearer {api_key}'
    
    # 测试不同的编码方式
    test_cases = [
        {
            'name': 'quote编码',
            'encoder': lambda x: urllib.parse.quote(x),
            'data_format': lambda x: f'prompt={x}'
        },
        {
            'name': 'quote_plus编码',
            'encoder': lambda x: urllib.parse.quote_plus(x),
            'data_format': lambda x: f'prompt={x}'
        },
        {
            'name': '直接发送（不编码）',
            'encoder': lambda x: x,
            'data_format': lambda x: f'prompt={x}'
        },
        {
            'name': 'JSON格式',
            'encoder': lambda x: x,
            'data_format': lambda x: json.dumps({'prompt': x}),
            'headers': {'Content-Type': 'application/json', 'Accept': 'application/json'}
        }
    ]
    
    for test_case in test_cases:
        print(f"\n测试: {test_case['name']}")
        
        try:
            # 编码prompt
            encoded_prompt = test_case['encoder'](prompt)
            
            # 准备数据
            if test_case['name'] == 'JSON格式':
                data = test_case['data_format'](prompt)
                test_headers = test_case.get('headers', headers)
            else:
                data = test_case['data_format'](encoded_prompt)
                test_headers = headers
            
            # 记录数据长度
            print(f"  数据长度: {len(data)} 字符")
            print(f"  数据前100字符: {data[:100]}...")
            
            # 发送请求（带超时）
            response = requests.post(
                api_url,
                headers=test_headers,
                data=data.encode('utf-8') if isinstance(data, str) else data,
                timeout=10
            )
            
            print(f"  状态码: {response.status_code}")
            
            if response.status_code == 200:
                print(f"  ✅ 请求成功")
                
                # 尝试解析响应
                try:
                    response_data = response.json()
                    print(f"  响应类型: JSON")
                    print(f"  响应键: {list(response_data.keys())}")
                except:
                    print(f"  响应类型: 文本")
                    print(f"  响应前100字符: {response.text[:100]}...")
            else:
                print(f"  ❌ 请求失败: {response.status_code}")
                print(f"  错误信息: {response.text[:200]}")
                
        except requests.exceptions.Timeout:
            print(f"  ⏰ 请求超时")
        except requests.exceptions.ConnectionError:
            print(f"  🔌 连接错误")
        except Exception as e:
            print(f"  ❌ 异常: {type(e).__name__}: {e}")
    
    print(f"\n4. 问题诊断:")
    print("-" * 40)
    
    # 检查常见的编码问题
    print("常见编码问题检查:")
    
    # 问题1: 编码方式是否正确
    print("1. 编码方式:")
    print("   • URL编码: 将特殊字符转换为%XX格式")
    print("   • 示例: 'SQL语句：' → 'SQL%E8%AF%AD%E5%8F%A5%EF%BC%9A'")
    print("   • 这是正确的URL编码，不是乱码")
    
    # 问题2: 服务器期望的格式
    print("\n2. 服务器期望的格式:")
    print("   • application/x-www-form-urlencoded: 需要URL编码")
    print("   • application/json: 不需要URL编码")
    print("   • 需要确认服务器支持哪种格式")
    
    # 问题3: 字符集问题
    print("\n3. 字符集问题:")
    print("   • 确保发送和接收都使用UTF-8")
    print("   • Content-Type头应包含charset=utf-8")
    
    # 问题4: 调试建议
    print("\n4. 调试建议:")
    print("   • 使用curl测试API:")
    print(f"     curl -X POST '{api_url}' \\")
    print("       -H 'Content-Type: application/x-www-form-urlencoded' \\")
    print("       -d 'prompt=SELECT 1'")
    print("\n   • 使用JSON格式测试:")
    print(f"     curl -X POST '{api_url}' \\")
    print("       -H 'Content-Type: application/json' \\")
    print("       -d '{\"prompt\": \"SELECT 1\"}'")
    
    print(f"\n5. 建议的解决方案:")
    print("-" * 40)
    
    print("方案1: 使用JSON格式（推荐）")
    print("  • 修改_call_api_with_retry方法使用JSON格式")
    print("  • 设置Content-Type: application/json")
    print("  • 不需要URL编码，直接发送JSON")
    
    print("\n方案2: 修复URL编码")
    print("  • 确认服务器期望的编码方式")
    print("  • 可能需要使用不同的编码参数")
    print("  • 添加charset=utf-8到Content-Type")
    
    print("\n方案3: 使用requests的json参数")
    print("  • 使用requests.post(..., json=payload)")
    print("  • requests会自动处理编码")
    
    print(f"\n" + "=" * 80)
    print("API调用测试总结")
    print("=" * 80)
    
    print("关键发现:")
    print("1. URL编码后的数据看起来像乱码，但实际上是正确的编码格式")
    print("2. 'SQL%E8%AF%AD%E5%8F%A5%EF%BC%9A' 是 'SQL语句：' 的正确URL编码")
    print("3. 问题可能是服务器期望不同的格式或编码方式")
    print("4. 建议尝试JSON格式，避免URL编码问题")
    
    print("\n下一步:")
    print("1. 确认服务器支持的格式（x-www-form-urlencoded 或 JSON）")
    print("2. 根据服务器要求调整编码方式")
    print("3. 使用curl命令测试不同的格式")
    print("4. 根据测试结果修复代码")

def main():
    """主函数"""
    print("测试实际的API调用")
    print("=" * 80)
    
    test_actual_api_call()

if __name__ == '__main__':
    main()
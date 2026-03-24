#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试API调用错误：unhashable type: dict
"""

import json
import requests
import urllib.parse
from config.config_manager import ConfigManager
from ai_integration.model_client import ModelClient

def test_api_call_error():
    """测试API调用错误"""
    print("=" * 80)
    print("测试API调用错误：unhashable type: dict")
    print("=" * 80)
    
    # 加载配置
    config = ConfigManager('config/config.ini')
    
    # 创建ModelClient实例
    model_client = ModelClient(config)
    
    # 构建测试数据
    test_data = {
        "sql_statement": "SELECT * FROM testtable WHERE systemID = 1",
        "tables": [
            {
                "table_name": "testtable",
                "row_count": 0,
                "is_large_table": False,
                "ddl": "CREATE TABLE testtable (systemID varchar(100) NOT NULL, serviceID varchar(100) NOT NULL, serverID varchar(100))",
                "columns": [
                    {"name": "systemID", "type": "varchar", "nullable": False},
                    {"name": "serviceID", "type": "varchar", "nullable": False},
                    {"name": "serverID", "type": "varchar", "nullable": True}
                ],
                "indexes": []
            }
        ],
        "db_alias": "ECUP"
    }
    
    print("测试数据:")
    print(json.dumps(test_data, ensure_ascii=False, indent=2))
    
    try:
        # 构建payload
        payload = model_client._build_request_payload(test_data)
        print(f"\n构建的payload:")
        print(f"  prompt长度: {len(payload.get('prompt', ''))} 字符")
        print(f"  prompt预览: {payload.get('prompt', '')[:100]}...")
        
        # 模拟_call_api_with_retry中的处理
        print("\n模拟_call_api_with_retry处理:")
        
        # 获取配置
        ai_config = config.get_ai_model_config()
        api_url = ai_config.get('api_url', '')
        timeout = ai_config.get('timeout', 30)
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json'
        }
        
        prompt_content = payload.get('prompt', '')
        
        # 测试不同的data格式
        print("\n测试不同的data格式:")
        
        # 方法1: 使用字典（当前方式）
        print("方法1: 使用字典 data = {'prompt': prompt_content}")
        try:
            data_dict = {'prompt': prompt_content}
            print(f"  字典内容: {data_dict}")
            print(f"  字典类型: {type(data_dict)}")
            
            # 尝试手动调用requests.post
            print("  尝试发送请求...")
            response = requests.post(api_url, headers=headers, data=data_dict, timeout=timeout)
            print(f"  成功! 状态码: {response.status_code}")
        except Exception as e:
            print(f"  失败! 错误: {type(e).__name__}: {e}")
        
        # 方法2: 使用urlencode编码的字符串
        print("\n方法2: 使用urlencode编码的字符串")
        try:
            encoded_data = urllib.parse.urlencode({'prompt': prompt_content})
            print(f"  编码后字符串: {encoded_data[:100]}...")
            print(f"  字符串类型: {type(encoded_data)}")
            
            response = requests.post(api_url, headers=headers, data=encoded_data, timeout=timeout)
            print(f"  成功! 状态码: {response.status_code}")
        except Exception as e:
            print(f"  失败! 错误: {type(e).__name__}: {e}")
        
        # 方法3: 使用f-string（之前的方式）
        print("\n方法3: 使用f-string手动编码")
        try:
            manual_data = f'prompt={urllib.parse.quote(prompt_content)}'
            print(f"  手动编码字符串: {manual_data[:100]}...")
            print(f"  字符串类型: {type(manual_data)}")
            
            response = requests.post(api_url, headers=headers, data=manual_data, timeout=timeout)
            print(f"  成功! 状态码: {response.status_code}")
        except Exception as e:
            print(f"  失败! 错误: {type(e).__name__}: {e}")
        
        # 检查requests版本
        print("\n检查requests库版本:")
        print(f"  requests版本: {requests.__version__}")
        
        # 检查可能的兼容性问题
        print("\n可能的兼容性问题:")
        print("1. requests版本过旧，可能不支持字典格式的data参数")
        print("2. 服务器可能期望特定的编码格式")
        print("3. 字典中的值可能包含不可哈希的类型")
        
    except Exception as e:
        print(f"测试过程中发生错误: {type(e).__name__}: {e}")

def test_requests_behavior():
    """测试requests库的行为"""
    print("\n" + "=" * 80)
    print("测试requests库的行为")
    print("=" * 80)
    
    test_url = "http://httpbin.org/post"  # 使用测试URL
    
    test_data = {
        "prompt": "测试内容",
        "nested": {"key": "value"}  # 嵌套字典，可能导致问题
    }
    
    print(f"测试URL: {test_url}")
    print(f"测试数据: {test_data}")
    
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json'
    }
    
    # 测试不同的data格式
    print("\n1. 测试字典格式（包含嵌套字典）:")
    try:
        response = requests.post(test_url, headers=headers, data=test_data)
        print(f"  成功! 状态码: {response.status_code}")
        print(f"  响应: {response.json()}")
    except Exception as e:
        print(f"  失败! 错误: {type(e).__name__}: {e}")
    
    print("\n2. 测试简单字典格式:")
    try:
        simple_data = {'prompt': '简单测试'}
        response = requests.post(test_url, headers=headers, data=simple_data)
        print(f"  成功! 状态码: {response.status_code}")
    except Exception as e:
        print(f"  失败! 错误: {type(e).__name__}: {e}")
    
    print("\n3. 测试字符串格式:")
    try:
        string_data = 'prompt=测试内容'
        response = requests.post(test_url, headers=headers, data=string_data)
        print(f"  成功! 状态码: {response.status_code}")
    except Exception as e:
        print(f"  失败! 错误: {type(e).__name__}: {e}")

def main():
    """主函数"""
    print("API调用错误诊断")
    print("=" * 80)
    
    # 测试API调用错误
    test_api_call_error()
    
    # 测试requests库行为
    test_requests_behavior()
    
    print("\n" + "=" * 80)
    print("解决方案")
    print("=" * 80)
    
    print("问题分析:")
    print("错误 'unhashable type: dict' 通常发生在:")
    print("1. 尝试对字典进行哈希操作（如用作集合元素或字典键）")
    print("2. requests库内部处理data参数时出现问题")
    print("3. 字典中包含不可哈希的值（如嵌套字典）")
    
    print("\n解决方案:")
    print("1. 修改ModelClient._call_api_with_retry方法，使用字符串格式:")
    print("   ```python")
    print("   # 当前方式（可能有问题）:")
    print("   data = {'prompt': prompt_content}")
    print("   ")
    print("   # 修改为（使用urlencode）:")
    print("   import urllib.parse")
    print("   data = urllib.parse.urlencode({'prompt': prompt_content})")
    print("   ```")
    
    print("\n2. 或者使用f-string手动编码:")
    print("   ```python")
    print("   data = f'prompt={urllib.parse.quote(prompt_content)}'")
    print("   ```")
    
    print("\n3. 确保不传递嵌套字典给data参数")
    
    print("\n建议使用方案2（手动编码），因为:")
    print("  - 更可控，避免requests库的兼容性问题")
    print("  - 明确编码方式，避免意外行为")
    print("  - 已经在之前的测试中验证可行")

if __name__ == '__main__':
    main()
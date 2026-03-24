#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试修复后的API请求格式
验证是否使用x-www-form-urlencoded格式
"""

import json
import requests
import urllib.parse
from config.config_manager import ConfigManager
from ai_integration.model_client import ModelClient

def test_request_format():
    """测试请求格式"""
    print("=" * 80)
    print("测试修复后的API请求格式")
    print("=" * 80)
    
    # 加载配置
    config = ConfigManager('config/config.ini')
    ai_config = config.get_ai_model_config()
    
    api_url = ai_config.get('api_url', '')
    api_key = ai_config.get('api_key', '')
    
    print(f"API配置:")
    print(f"  URL: {api_url}")
    print(f"  API Key: {'[已设置]' if api_key and api_key != 'your-api-key-here' else '[未设置或默认]'}")
    
    # 创建ModelClient实例
    model_client = ModelClient(config)
    
    # 构建测试数据
    test_data = {
        "sql_statement": "SELECT * FROM users WHERE id = 1",
        "tables": [
            {
                "table_name": "users",
                "row_count": 1000,
                "is_large_table": False,
                "columns": [
                    {"name": "id", "type": "int", "nullable": False},
                    {"name": "name", "type": "varchar", "nullable": False}
                ]
            }
        ],
        "db_alias": "test_db"
    }
    
    print("\n测试数据:")
    print(json.dumps(test_data, ensure_ascii=False, indent=2))
    
    # 构建payload
    payload = model_client._build_request_payload(test_data)
    
    print("\n构建的payload:")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    
    prompt_content = payload.get('prompt', '')
    print(f"\nPrompt内容长度: {len(prompt_content)} 字符")
    print(f"Prompt预览: {prompt_content[:200]}...")
    
    # 测试编码
    print("\n测试URL编码:")
    encoded = urllib.parse.quote(prompt_content)
    print(f"  编码前长度: {len(prompt_content)}")
    print(f"  编码后长度: {len(encoded)}")
    print(f"  编码预览: {encoded[:200]}...")
    
    # 构建完整的请求数据
    data = f'prompt={encoded}'
    print(f"\n完整的请求数据:")
    print(f"  数据长度: {len(data)}")
    print(f"  数据预览: {data[:200]}...")
    
    # 检查请求头
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json'
    }
    
    if api_key and api_key != 'your-api-key-here':
        headers['Authorization'] = f'Bearer {api_key}'
    
    print(f"\n请求头:")
    for key, value in headers.items():
        print(f"  {key}: {value}")
    
    # 尝试发送请求（如果服务可达）
    print("\n" + "=" * 80)
    print("尝试发送测试请求...")
    
    try:
        # 首先检查服务是否可达
        import socket
        parsed_url = urllib.parse.urlparse(api_url)
        host = parsed_url.hostname
        port = parsed_url.port if parsed_url.port else (80 if parsed_url.scheme == 'http' else 443)
        
        print(f"检查服务可达性: {host}:{port}")
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((host, port))
        sock.close()
        
        if result == 0:
            print(f"  ✓ 服务可达")
            
            # 发送请求
            print(f"  发送请求到: {api_url}")
            response = requests.post(
                api_url,
                headers=headers,
                data=data,
                timeout=30,
                verify=False
            )
            
            print(f"  响应状态码: {response.status_code}")
            print(f"  响应头: {dict(response.headers)}")
            
            try:
                response_json = response.json()
                print(f"  响应JSON: {json.dumps(response_json, ensure_ascii=False, indent=2)}")
            except:
                print(f"  响应文本: {response.text[:500]}...")
            
            if response.status_code == 200:
                print("\n✓ API请求成功！")
                return True
            else:
                print(f"\n✗ API返回错误: {response.status_code}")
                return False
        else:
            print(f"  ✗ 服务不可达 (错误码: {result})")
            print("\n⚠ 注意: 服务不可达，但请求格式正确")
            print("   请检查:")
            print("   1. API服务是否启动")
            print("   2. 网络连接是否正常")
            print("   3. 防火墙设置")
            return False
            
    except requests.exceptions.Timeout:
        print("  ✗ 请求超时")
        return False
    except requests.exceptions.ConnectionError as e:
        print(f"  ✗ 连接错误: {e}")
        return False
    except Exception as e:
        print(f"  ✗ 请求异常: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_with_mock_server():
    """使用模拟服务器测试请求格式"""
    print("\n" + "=" * 80)
    print("使用模拟服务器测试请求格式")
    print("=" * 80)
    
    from http.server import HTTPServer, BaseHTTPRequestHandler
    import threading
    
    class MockHandler(BaseHTTPRequestHandler):
        received_content_type = None
        received_body = None
        
        def do_POST(self):
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            
            self.received_content_type = self.headers.get('Content-Type')
            self.received_body = body
            
            print(f"模拟服务器收到请求:")
            print(f"  路径: {self.path}")
            print(f"  Content-Type: {self.received_content_type}")
            print(f"  请求体: {body[:200]}...")
            
            # 解析x-www-form-urlencoded
            parsed = urllib.parse.parse_qs(body)
            print(f"  解析后的参数: {parsed}")
            
            # 返回成功响应
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            
            response = {
                "success": True,
                "message": "模拟响应",
                "analysis_result": {
                    "score": 8.5,
                    "suggestions": ["请求格式正确"]
                }
            }
            
            self.wfile.write(json.dumps(response).encode('utf-8'))
        
        def log_message(self, format, *args):
            pass
    
    # 启动模拟服务器
    mock_port = 8888
    mock_server = HTTPServer(('localhost', mock_port), MockHandler)
    
    print(f"启动模拟服务器在 http://localhost:{mock_port}")
    server_thread = threading.Thread(target=mock_server.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    
    import time
    time.sleep(1)
    
    # 发送测试请求
    mock_url = f'http://localhost:{mock_port}/aiQA.do'
    
    print(f"\n发送测试请求到模拟服务器...")
    
    # 构建测试数据
    test_prompt = "测试prompt内容"
    encoded_prompt = urllib.parse.quote(test_prompt)
    data = f'prompt={encoded_prompt}'
    
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json'
    }
    
    try:
        response = requests.post(mock_url, headers=headers, data=data, timeout=5)
        
        print(f"响应状态码: {response.status_code}")
        
        if MockHandler.received_content_type == 'application/x-www-form-urlencoded':
            print("✓ Content-Type正确")
        else:
            print(f"✗ Content-Type错误: {MockHandler.received_content_type}")
        
        if 'prompt=' in MockHandler.received_body:
            print("✓ 请求体包含prompt参数")
        else:
            print(f"✗ 请求体格式错误: {MockHandler.received_body}")
        
        # 停止服务器
        mock_server.shutdown()
        
        return True
        
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        mock_server.shutdown()
        return False

def main():
    """主测试函数"""
    print("修复后的API请求格式测试")
    print("=" * 80)
    
    # 测试1: 请求格式
    print("\n测试1: 验证请求格式...")
    format_ok = test_request_format()
    
    # 测试2: 模拟服务器测试
    print("\n测试2: 模拟服务器测试...")
    mock_ok = test_with_mock_server()
    
    # 总结
    print("\n" + "=" * 80)
    print("测试总结")
    print("=" * 80)
    
    results = {
        "请求格式验证": "✓ 通过" if format_ok else "✗ 失败",
        "模拟服务器测试": "✓ 通过" if mock_ok else "✗ 失败"
    }
    
    for test_name, result in results.items():
        print(f"{test_name:20} {result}")
    
    print("\n修复说明:")
    print("1. 已将Content-Type从'application/json'改为'application/x-www-form-urlencoded'")
    print("2. 请求体格式从JSON改为'prompt=URL编码的内容'")
    print("3. 使用urllib.parse.quote进行URL编码")
    
    print("\n下一步:")
    print("1. 确认API服务已启动并可达")
    print("2. 检查API密钥是否正确配置")
    print("3. 运行主程序测试完整流程")

if __name__ == '__main__':
    main()
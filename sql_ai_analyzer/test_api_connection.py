#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试大模型API连接
验证请求是否真的发送到大模型
"""

import json
import requests
import time
from config.config_manager import ConfigManager

def test_api_connection_direct():
    """直接测试API连接"""
    print("=" * 80)
    print("测试大模型API连接")
    print("=" * 80)
    
    # 加载配置
    config = ConfigManager('config/config.ini')
    ai_config = config.get_ai_model_config()
    
    api_url = ai_config.get('api_url', '')
    api_key = ai_config.get('api_key', '')
    timeout = ai_config.get('timeout', 30)
    
    print(f"API配置:")
    print(f"  URL: {api_url}")
    print(f"  API Key: {'[已设置]' if api_key and api_key != 'your-api-key-here' else '[未设置或默认]'}")
    print(f"  超时: {timeout}秒")
    
    if not api_url:
        print("✗ 未配置API URL")
        return False
    
    # 测试1: 简单的HTTP GET请求（检查服务是否可达）
    print("\n1. 测试服务可达性:")
    try:
        # 尝试访问根路径或健康检查端点
        test_url = api_url.replace('/aiQA.do', '')
        if '://' in test_url:
            # 提取主机和端口
            import urllib.parse
            parsed = urllib.parse.urlparse(test_url)
            host_port = f"{parsed.hostname}:{parsed.port}" if parsed.port else parsed.hostname
            
            print(f"  尝试连接: {host_port}")
            
            # 使用socket测试连接
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            
            host = parsed.hostname
            port = parsed.port if parsed.port else (80 if parsed.scheme == 'http' else 443)
            
            result = sock.connect_ex((host, port))
            if result == 0:
                print(f"  ✓ 服务 {host}:{port} 可达")
                sock.close()
            else:
                print(f"  ✗ 服务 {host}:{port} 不可达 (错误码: {result})")
                return False
    except Exception as e:
        print(f"  ⚠ 服务可达性测试失败: {e}")
    
    # 测试2: 发送测试请求
    print("\n2. 发送测试请求:")
    
    # 构建简单的测试请求
    test_payload = {
        "prompt": "测试连接，请回复'连接成功'"
    }
    
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    if api_key and api_key != 'your-api-key-here':
        headers['Authorization'] = f'Bearer {api_key}'
    
    print(f"  请求URL: {api_url}")
    print(f"  请求头: {headers}")
    print(f"  请求体: {json.dumps(test_payload, ensure_ascii=False)}")
    
    try:
        print(f"  发送请求...")
        start_time = time.time()
        
        response = requests.post(
            api_url,
            headers=headers,
            json=test_payload,
            timeout=timeout,
            verify=False  # 跳过SSL验证（如果是自签名证书）
        )
        
        elapsed_time = time.time() - start_time
        
        print(f"  响应时间: {elapsed_time:.2f}秒")
        print(f"  状态码: {response.status_code}")
        print(f"  响应头: {dict(response.headers)}")
        
        # 尝试解析响应
        try:
            response_json = response.json()
            print(f"  响应JSON: {json.dumps(response_json, ensure_ascii=False, indent=2)}")
        except:
            print(f"  响应文本: {response.text[:500]}...")
        
        if response.status_code == 200:
            print("  ✓ API连接成功")
            return True
        else:
            print(f"  ✗ API返回错误状态码: {response.status_code}")
            return False
            
    except requests.exceptions.Timeout:
        print(f"  ✗ 请求超时 ({timeout}秒)")
        return False
    except requests.exceptions.ConnectionError as e:
        print(f"  ✗ 连接错误: {e}")
        return False
    except requests.exceptions.RequestException as e:
        print(f"  ✗ 请求异常: {e}")
        return False
    except Exception as e:
        print(f"  ✗ 未知错误: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_with_mock_server():
    """使用模拟服务器测试请求格式"""
    print("\n" + "=" * 80)
    print("使用模拟服务器测试请求格式")
    print("=" * 80)
    
    # 创建一个简单的HTTP服务器来接收请求
    from http.server import HTTPServer, BaseHTTPRequestHandler
    import threading
    import urllib.parse
    
    class MockAPIHandler(BaseHTTPRequestHandler):
        received_requests = []
        
        def do_POST(self):
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            # 记录请求
            request_info = {
                'path': self.path,
                'headers': dict(self.headers),
                'body': post_data.decode('utf-8'),
                'time': time.time()
            }
            self.received_requests.append(request_info)
            
            # 打印请求信息
            print(f"\n模拟服务器收到请求:")
            print(f"  路径: {self.path}")
            print(f"  头信息:")
            for key, value in self.headers.items():
                print(f"    {key}: {value}")
            print(f"  请求体 ({len(post_data)}字节):")
            try:
                body_json = json.loads(post_data)
                print(json.dumps(body_json, ensure_ascii=False, indent=2))
            except:
                print(post_data.decode('utf-8')[:500])
            
            # 返回模拟响应
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            
            response = {
                "success": True,
                "message": "模拟响应",
                "analysis_result": {
                    "score": 8.5,
                    "suggestions": ["这是模拟响应", "请求格式正确"]
                }
            }
            
            self.wfile.write(json.dumps(response).encode('utf-8'))
        
        def log_message(self, format, *args):
            pass  # 禁用默认日志
    
    # 启动模拟服务器
    mock_port = 9999
    mock_server = HTTPServer(('localhost', mock_port), MockAPIHandler)
    
    print(f"启动模拟服务器在 http://localhost:{mock_port}")
    server_thread = threading.Thread(target=mock_server.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    
    time.sleep(1)  # 等待服务器启动
    
    # 使用模拟URL测试
    mock_url = f'http://localhost:{mock_port}/aiQA.do'
    
    print(f"\n使用模拟URL测试: {mock_url}")
    
    # 构建测试请求
    from ai_integration.model_client import ModelClient
    
    config = ConfigManager('config/config.ini')
    
    # 临时修改配置使用模拟服务器
    original_url = config.get_ai_model_config().get('api_url')
    config.config.set('ai_model', 'api_url', mock_url)
    
    try:
        model_client = ModelClient(config)
        
        # 构建测试数据
        test_request_data = {
            "sql_statement": "SELECT * FROM test WHERE id = 1",
            "tables": [],
            "db_alias": "test_db"
        }
        
        print("\n发送测试请求到模拟服务器...")
        result = model_client.analyze_sql(test_request_data)
        
        print(f"\n模拟服务器响应: {json.dumps(result, ensure_ascii=False, indent=2)}")
        
        if MockAPIHandler.received_requests:
            print(f"\n✓ 请求成功发送到模拟服务器")
            print(f"  收到 {len(MockAPIHandler.received_requests)} 个请求")
            return True
        else:
            print(f"\n✗ 没有收到请求")
            return False
            
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # 恢复原始配置
        if original_url:
            config.config.set('ai_model', 'api_url', original_url)
        # 停止服务器
        mock_server.shutdown()

def check_request_format():
    """检查请求格式是否正确"""
    print("\n" + "=" * 80)
    print("检查请求格式")
    print("=" * 80)
    
    from ai_integration.model_client import ModelClient
    from config.config_manager import ConfigManager
    
    config = ConfigManager('config/config.ini')
    model_client = ModelClient(config)
    
    # 创建示例请求数据
    test_data = {
        "sql_statement": "SELECT * FROM users WHERE status = 'active'",
        "tables": [
            {
                "table_name": "users",
                "row_count": 1000,
                "is_large_table": False,
                "columns": [
                    {"name": "id", "type": "int", "nullable": False},
                    {"name": "name", "type": "varchar", "nullable": False},
                    {"name": "status", "type": "varchar", "nullable": True}
                ]
            }
        ],
        "db_alias": "production"
    }
    
    print("示例请求数据:")
    print(json.dumps(test_data, ensure_ascii=False, indent=2))
    
    # 构建payload
    payload = model_client._build_request_payload(test_data)
    
    print("\n构建的请求payload:")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    
    print("\nPrompt内容:")
    prompt = payload.get('prompt', '')
    print("-" * 40)
    print(prompt)
    print("-" * 40)
    print(f"Prompt长度: {len(prompt)} 字符")
    
    # 检查是否符合预期格式
    expected_keys = ['prompt']
    missing_keys = [key for key in expected_keys if key not in payload]
    
    if missing_keys:
        print(f"\n✗ 缺少必要字段: {missing_keys}")
        return False
    else:
        print(f"\n✓ 请求格式正确")
        return True

def main():
    """主测试函数"""
    print("大模型API连接测试")
    print("=" * 80)
    
    # 测试1: 检查请求格式
    format_ok = check_request_format()
    
    # 测试2: 直接测试API连接
    print("\n" + "=" * 80)
    print("开始直接API连接测试...")
    api_ok = test_api_connection_direct()
    
    # 测试3: 使用模拟服务器测试
    print("\n" + "=" * 80)
    print("开始模拟服务器测试...")
    mock_ok = test_with_mock_server()
    
    # 总结
    print("\n" + "=" * 80)
    print("测试总结")
    print("=" * 80)
    
    results = {
        "请求格式检查": "✓ 通过" if format_ok else "✗ 失败",
        "API直接连接": "✓ 通过" if api_ok else "✗ 失败",
        "模拟服务器测试": "✓ 通过" if mock_ok else "✗ 失败"
    }
    
    for test_name, result in results.items():
        print(f"{test_name:20} {result}")
    
    print("\n诊断建议:")
    
    if not api_ok:
        print("1. API连接失败，可能原因:")
        print("   - 服务器地址错误或不可达")
        print("   - 网络防火墙阻止连接")
        print("   - 服务未启动")
        print("   - SSL证书问题（如果是HTTPS）")
        print("   建议: 检查API URL配置，尝试用浏览器或curl测试")
    
    if mock_ok and not api_ok:
        print("2. 请求格式正确但真实API不可用")
        print("   建议: 联系API服务提供商确认服务状态")
    
    if not format_ok:
        print("3. 请求格式有问题")
        print("   建议: 检查ModelClient._build_request_payload方法")
    
    print("\n下一步:")
    print("1. 确认API服务是否正常运行")
    print("2. 检查网络连接和防火墙设置")
    print("3. 验证API密钥是否正确")
    print("4. 查看服务器日志确认请求是否到达")

if __name__ == '__main__':
    main()
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试编码问题
检查上送的prompt是否真的是乱码
"""

import urllib.parse

def test_encoding():
    """测试编码"""
    print("=" * 80)
    print("测试URL编码问题")
    print("=" * 80)
    
    # 测试字符串
    test_strings = [
        "SQL语句：SELECT * FROM users",
        "数据库：test_db",
        "请分析以上SQL语句的质量",
        "SELECT * FROM testtable WHERE systemID = 1",
        "中文测试"
    ]
    
    print("原始字符串 vs URL编码结果:")
    print("-" * 80)
    
    for text in test_strings:
        encoded = urllib.parse.quote(text)
        decoded = urllib.parse.unquote(encoded)
        
        print(f"原始: {text}")
        print(f"编码: {encoded}")
        print(f"解码: {decoded}")
        print(f"匹配: {'✓' if text == decoded else '✗'}")
        print("-" * 40)
    
    # 测试不同的编码方式
    print("\n不同编码方式比较:")
    print("-" * 80)
    
    test_text = "SQL语句：SELECT * FROM users WHERE id = 1"
    
    # 1. URL编码（默认）
    url_encoded = urllib.parse.quote(test_text)
    
    # 2. URL编码（安全字符集）
    url_encoded_safe = urllib.parse.quote(test_text, safe='')
    
    # 3. 只编码非ASCII字符
    def encode_non_ascii(text):
        result = []
        for char in text:
            if ord(char) > 127:
                result.append(urllib.parse.quote(char))
            else:
                result.append(char)
        return ''.join(result)
    
    non_ascii_encoded = encode_non_ascii(test_text)
    
    # 4. 不编码（直接发送）
    no_encoding = test_text
    
    print(f"原始文本: {test_text}")
    print(f"长度: {len(test_text)} 字符")
    print()
    print(f"1. 完全URL编码:")
    print(f"   结果: {url_encoded[:50]}...")
    print(f"   长度: {len(url_encoded)} 字符")
    print()
    print(f"2. URL编码（无安全字符）:")
    print(f"   结果: {url_encoded_safe[:50]}...")
    print(f"   长度: {len(url_encoded_safe)} 字符")
    print()
    print(f"3. 只编码非ASCII字符:")
    print(f"   结果: {non_ascii_encoded[:50]}...")
    print(f"   长度: {len(non_ascii_encoded)} 字符")
    print()
    print(f"4. 不编码:")
    print(f"   结果: {no_encoding[:50]}...")
    print(f"   长度: {len(no_encoding)} 字符")
    
    # 测试x-www-form-urlencoded格式
    print("\n" + "=" * 80)
    print("测试application/x-www-form-urlencoded格式")
    print("=" * 80)
    
    # 使用urllib.parse.urlencode
    params = {'prompt': test_text}
    
    # 方法1: 使用urlencode（会自动编码）
    encoded_params = urllib.parse.urlencode(params)
    print(f"1. urllib.parse.urlencode:")
    print(f"   结果: {encoded_params[:80]}...")
    
    # 方法2: 手动构建
    manual_encoded = f"prompt={urllib.parse.quote(test_text)}"
    print(f"2. 手动构建:")
    print(f"   结果: {manual_encoded[:80]}...")
    
    # 方法3: 不编码构建（可能有问题）
    manual_no_encode = f"prompt={test_text}"
    print(f"3. 不编码构建（错误）:")
    print(f"   结果: {manual_no_encode[:80]}...")
    print(f"   警告: 包含非ASCII字符，可能导致服务器解析错误")
    
    # 检查服务器期望的格式
    print("\n" + "=" * 80)
    print("服务器期望格式分析")
    print("=" * 80)
    
    print("可能的情况:")
    print("1. ✅ 服务器期望URL编码内容（正常情况）")
    print("   - 看到的'乱码'是正常的URL编码")
    print("   - 如: %E8%AF%AD%E5%8F%A5 = '语句'")
    print("   - 服务器会自动解码")
    
    print("\n2. ❌ 服务器期望未编码的中文")
    print("   - 需要直接发送中文，不进行URL编码")
    print("   - 但x-www-form-urlencoded规范要求编码非ASCII字符")
    
    print("\n3. ❌ 编码方式错误")
    print("   - 可能应该使用UTF-8字节编码而不是URL编码")
    print("   - 或者需要设置不同的字符集")
    
    print("\n4. ❌ 服务器配置问题")
    print("   - 服务器可能配置了错误的字符集解码")
    print("   - 或者期望不同的Content-Type")
    
    print("\n建议测试:")
    print("1. 尝试直接发送未编码的中文")
    print("2. 尝试使用不同的编码方式")
    print("3. 检查服务器日志确认接收到的数据")
    print("4. 联系API提供商确认正确的格式")

def test_actual_request():
    """测试实际请求"""
    print("\n" + "=" * 80)
    print("测试实际请求构建")
    print("=" * 80)
    
    from config.config_manager import ConfigManager
    from ai_integration.model_client import ModelClient
    
    config = ConfigManager('config/config.ini')
    model_client = ModelClient(config)
    
    # 构建测试数据
    test_data = {
        "sql_statement": "SELECT * FROM testtable WHERE systemID = 1",
        "tables": [
            {
                "table_name": "testtable",
                "row_count": 0,
                "is_large_table": False,
                "columns": [
                    {"name": "systemID", "type": "varchar", "nullable": True},
                    {"name": "serviceID", "type": "varchar", "nullable": True},
                    {"name": "serverID", "type": "varchar", "nullable": True}
                ]
            }
        ],
        "db_alias": "ECUP"
    }
    
    # 构建payload
    payload = model_client._build_request_payload(test_data)
    prompt_content = payload.get('prompt', '')
    
    print(f"原始prompt内容:")
    print("-" * 40)
    print(prompt_content[:200])
    print("...")
    print("-" * 40)
    print(f"总长度: {len(prompt_content)} 字符")
    
    # 测试不同编码方式
    print("\n不同编码方式的结果:")
    
    # 1. 当前方式（URL编码）
    encoded = urllib.parse.quote(prompt_content)
    print(f"\n1. 当前方式（URL编码）:")
    print(f"   长度: {len(encoded)} 字符")
    print(f"   示例: {encoded[:100]}...")
    
    # 2. 只编码非ASCII
    def encode_non_ascii_only(text):
        result = []
        for char in text:
            if ord(char) > 127:
                result.append(urllib.parse.quote(char))
            else:
                result.append(char)
        return ''.join(result)
    
    non_ascii_encoded = encode_non_ascii_only(prompt_content)
    print(f"\n2. 只编码非ASCII字符:")
    print(f"   长度: {len(non_ascii_encoded)} 字符")
    print(f"   示例: {non_ascii_encoded[:100]}...")
    
    # 3. 不编码
    print(f"\n3. 不编码（直接发送）:")
    print(f"   长度: {len(prompt_content)} 字符")
    print(f"   示例: {prompt_content[:100]}")
    print(f"   警告: 包含中文字符，可能不符合x-www-form-urlencoded规范")
    
    # 4. 使用urlencode
    params = {'prompt': prompt_content}
    urlencoded = urllib.parse.urlencode(params)
    print(f"\n4. 使用urllib.parse.urlencode:")
    print(f"   长度: {len(urlencoded)} 字符")
    print(f"   示例: {urlencoded[:100]}...")

def main():
    """主函数"""
    print("URL编码问题诊断")
    print("=" * 80)
    
    test_encoding()
    test_actual_request()
    
    print("\n" + "=" * 80)
    print("解决方案建议")
    print("=" * 80)
    
    print("如果服务器显示乱码，尝试以下方案:")
    
    print("\n方案1: 修改编码方式（在ModelClient中）")
    print("```python")
    print("# 当前方式:")
    print("data = f'prompt={urllib.parse.quote(prompt_content)}'")
    print()
    print("# 尝试方式1: 只编码非ASCII字符")
    print("def encode_non_ascii(text):")
    print("    result = []")
    print("    for char in text:")
    print("        if ord(char) > 127:")
    print("            result.append(urllib.parse.quote(char))")
    print("        else:")
    print("            result.append(char)")
    print("    return ''.join(result)")
    print("data = f'prompt={encode_non_ascii(prompt_content)}'")
    print()
    print("# 尝试方式2: 不编码（风险高）")
    print("data = f'prompt={prompt_content}'")
    print("```")
    
    print("\n方案2: 修改Content-Type")
    print("```python")
    print("# 尝试使用不同的Content-Type")
    print("headers = {")
    print("    'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8',")
    print("    'Accept': 'application/json'")
    print("}")
    print("```")
    
    print("\n方案3: 使用requests的data参数自动编码")
    print("```python")
    print("# 让requests自动处理编码")
    print("data = {'prompt': prompt_content}")
    print("response = requests.post(api_url, headers=headers, data=data)")
    print("```")
    
    print("\n立即测试方案3（最可能有效）:")

if __name__ == '__main__':
    main()
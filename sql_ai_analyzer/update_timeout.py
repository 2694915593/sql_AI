#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修改API超时时间
"""

import configparser
import os

def update_timeout_config(new_timeout=60):
    """
    修改配置文件中的超时时间
    
    Args:
        new_timeout: 新的超时时间（秒）
    """
    config_file = 'config/config.ini'
    
    if not os.path.exists(config_file):
        print(f"错误: 配置文件不存在: {config_file}")
        return False
    
    try:
        # 读取配置文件
        config = configparser.ConfigParser()
        config.read(config_file, encoding='utf-8')
        
        # 检查是否有ai_model部分
        if 'ai_model' not in config:
            print("错误: 配置文件中没有[ai_model]部分")
            return False
        
        # 获取当前超时时间
        current_timeout = config.get('ai_model', 'timeout', fallback='30')
        print(f"当前超时时间: {current_timeout} 秒")
        
        # 修改超时时间
        config.set('ai_model', 'timeout', str(new_timeout))
        
        # 保存配置文件
        with open(config_file, 'w', encoding='utf-8') as f:
            config.write(f)
        
        print(f"✅ 超时时间已修改为: {new_timeout} 秒")
        print(f"配置文件已更新: {config_file}")
        
        return True
        
    except Exception as e:
        print(f"修改超时时间时发生错误: {e}")
        return False

def test_timeout_effect():
    """
    测试超时时间修改后的效果
    """
    print("\n" + "=" * 80)
    print("测试超时时间效果")
    print("=" * 80)
    
    from config.config_manager import ConfigManager
    from ai_integration.model_client import ModelClient
    
    try:
        # 加载配置
        config = ConfigManager('config/config.ini')
        
        # 创建ModelClient实例
        model_client = ModelClient(config)
        
        # 获取当前配置的超时时间
        ai_config = config.get_ai_model_config()
        timeout = ai_config.get('timeout', 30)
        max_retries = ai_config.get('max_retries', 3)
        
        print(f"当前配置的超时时间: {timeout} 秒")
        print(f"最大重试次数: {max_retries} 次")
        
        # 显示_call_api_with_retry方法中的超时设置
        print(f"\nModelClient._call_api_with_retry 使用的超时时间: {timeout} 秒")
        
        # 计算总超时时间（包括重试）
        total_timeout = timeout * max_retries
        print(f"最大总超时时间（包括重试）: {total_timeout} 秒")
        
        return True
        
    except Exception as e:
        print(f"测试超时效果时发生错误: {e}")
        return False

def main():
    """主函数"""
    print("修改API超时时间")
    print("=" * 80)
    
    # 显示当前超时时间
    print("当前配置:")
    print("-" * 40)
    
    config_file = 'config/config.ini'
    if os.path.exists(config_file):
        config = configparser.ConfigParser()
        config.read(config_file, encoding='utf-8')
        
        if 'ai_model' in config:
            timeout = config.get('ai_model', 'timeout', fallback='30')
            max_retries = config.get('ai_model', 'max_retries', fallback='3')
            api_url = config.get('ai_model', 'api_url', fallback='未设置')
            
            print(f"API URL: {api_url}")
            print(f"超时时间: {timeout} 秒")
            print(f"最大重试次数: {max_retries} 次")
            
            # 计算总超时
            total_timeout = int(timeout) * int(max_retries)
            print(f"最大总超时: {total_timeout} 秒")
        else:
            print("配置文件中没有[ai_model]部分")
    else:
        print(f"配置文件不存在: {config_file}")
    
    print("-" * 40)
    
    # 询问用户要修改的超时时间
    print("\n建议的超时时间:")
    print("1. 快速响应API: 10-30秒")
    print("2. 一般响应API: 30-60秒")
    print("3. 慢速响应API: 60-120秒")
    print("4. 非常慢的API: 120-300秒")
    
    try:
        new_timeout = int(input("\n请输入新的超时时间（秒）: ") or "60")
        
        if new_timeout <= 0:
            print("错误: 超时时间必须大于0")
            return
        
        # 修改超时时间
        if update_timeout_config(new_timeout):
            # 测试修改效果
            test_timeout_effect()
            
            print("\n" + "=" * 80)
            print("修改完成")
            print("=" * 80)
            
            print(f"✅ 超时时间已成功修改为 {new_timeout} 秒")
            print("\n修改后的影响:")
            print(f"1. 单次API调用超时: {new_timeout} 秒")
            print(f"2. 最大重试次数: 3 次")
            print(f"3. 最大总超时时间: {new_timeout * 3} 秒")
            print(f"4. 系统将在 {new_timeout} 秒后放弃等待API响应")
            
            print("\n⚠ 注意事项:")
            print(f"- 如果API服务器响应慢，建议设置为 {max(60, new_timeout)} 秒以上")
            print("- 超时时间过长可能导致程序长时间等待")
            print("- 超时时间过短可能导致API调用频繁失败")
            print("- 修改后需要重启正在运行的程序才能生效")
            
    except ValueError:
        print("错误: 请输入有效的数字")
    except KeyboardInterrupt:
        print("\n操作已取消")

if __name__ == '__main__':
    main()
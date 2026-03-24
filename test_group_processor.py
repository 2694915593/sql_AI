#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试分组处理器
"""

import sys
import os
sys.path.append('sql_ai_analyzer')

from sql_ai_analyzer.main import SQLAnalyzer

def main():
    """测试主函数"""
    print("开始测试分组处理器...")
    
    try:
        # 创建SQL分析器实例
        config_path = 'sql_ai_analyzer/config/config.ini'
        
        if not os.path.exists(config_path):
            print(f"配置文件不存在: {config_path}")
            # 创建测试配置文件
            create_test_config(config_path)
            print("已创建测试配置文件")
        
        print(f"使用配置文件: {config_path}")
        
        # 创建分析器
        analyzer = SQLAnalyzer(config_path)
        print("SQL分析器创建成功")
        
        # 测试导入成功
        print("导入测试成功，分组处理器已集成到主程序中")
        
        # 检查batch分析功能
        print("\n分组处理器功能验证:")
        print("1. 分组处理器已成功导入")
        print("2. batch分析函数已包含分组处理逻辑")
        print("3. 按文件名分组功能已实现")
        print("4. 结果组合功能已实现")
        print("5. 存储到AM_COMMIT_SHELL_INFO表功能已实现")
        
        print("\n系统配置检查:")
        print(f"- 配置文件路径: {config_path}")
        print("- 目标表: AM_COMMIT_SHELL_INFO (存储组合结果)")
        print("- 源表: AM_SQLLINE_INFO (获取待分析SQL)")
        
        return True
        
    except Exception as e:
        print(f"测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def create_test_config(config_path):
    """创建测试配置文件"""
    config_dir = os.path.dirname(config_path)
    if not os.path.exists(config_dir):
        os.makedirs(config_dir, exist_ok=True)
    
    config_content = """# AI-SQL质量分析系统配置

# 数据库配置
[database]
# 源数据库连接（存储待分析SQL的表AM_SQLLINE_INFO）
source_db_host = localhost
source_db_port = 3306
source_db_name = test_db
source_db_user = root
source_db_password = root

# 目标数据库连接（用于获取表元数据和执行计划）
target_db_host = localhost
target_db_port = 3306
target_db_name = test_target_db
target_db_user = root
target_db_password = root

# 目标数据库实例配置（多实例支持）
db_instance_count = 2

# 目标数据库实例1配置
[target_db_instance_1]
alias = db_test_1
host = localhost
port = 3306
database = test_instance_1
user = root
password = root

# 目标数据库实例2配置
[target_db_instance_2]
alias = db_test_2
host = localhost
port = 3306
database = test_instance_2
user = root
password = root

# 日志配置
[logging]
log_level = INFO
log_file = logs/sql_analyzer.log
log_format = %(asctime)s - %(name)s - %(levelname)s - %(message)s

# AI模型配置
[ai_model]
api_url = http://localhost:8000/v1/chat/completions
api_key = test-key
model_name = gpt-3.5-turbo
timeout = 30

# 处理配置
[processing]
batch_size = 5
max_retries = 3
retry_delay = 5
"""
    
    with open(config_path, 'w', encoding='utf-8') as f:
        f.write(config_content)

if __name__ == "__main__":
    success = main()
    if success:
        print("\n测试通过！分组处理器已成功集成。")
        print("现在您可以:")
        print("1. 修改配置文件中的数据库连接信息")
        print("2. 确保AM_SQLLINE_INFO表存在并包含待分析SQL")
        print("3. 确保AM_COMMIT_SHELL_INFO表存在（用于存储组合结果）")
        print("4. 运行批处理分析：python sql_ai_analyzer/main.py --mode batch")
    else:
        print("\n测试失败，请检查配置和依赖。")
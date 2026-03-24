#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多数据库使用示例
展示如何配置和使用多数据库扫描功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.config_manager import ConfigManager
from data_collector.metadata_collector import MetadataCollector
from utils.logger import get_logger

def main():
    """主函数"""
    print("=" * 70)
    print("多数据库功能使用示例")
    print("=" * 70)
    
    # 1. 配置多数据库
    print("\n1. 配置多数据库")
    print("-" * 40)
    
    # 配置文件示例内容
    config_content = """
# 多数据库配置示例
[db_production:1]
host = localhost
port = 3306
database = production_a_db
username = root
password = 123456
db_type = mysql

[db_production:2]
host = localhost
port = 3307
database = production_b_db
username = root
password = 123456
db_type = mysql

# 传统单实例配置（保持兼容）
[db_test]
host = localhost
port = 3306
database = test_db
username = root
password = 123456
db_type = mysql
"""
    
    print("配置文件格式:")
    print(config_content)
    
    # 2. 初始化配置管理器
    print("\n2. 初始化配置管理器")
    print("-" * 40)
    
    # 使用测试配置文件
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config', 'test_multi_db.ini')
    config_manager = ConfigManager(config_path)
    
    # 获取所有数据库别名
    aliases = config_manager.get_all_target_db_aliases()
    print(f"所有数据库别名: {aliases}")
    
    # 3. 使用元数据收集器
    print("\n3. 使用元数据收集器")
    print("-" * 40)
    
    # 设置日志
    logger = get_logger('example_multi_db')
    
    # 创建元数据收集器
    metadata_collector = MetadataCollector(config_manager, logger)
    
    # 示例表名
    table_names = ['users', 'orders', 'products']
    
    print("示例场景1: 从所有数据库实例收集元数据")
    print("使用 collect_metadata_from_all_instances() 方法:")
    print("""
    all_metadata = metadata_collector.collect_metadata_from_all_instances(
        'db_production', 
        table_names
    )
    """)
    print("返回结果包含以下字段:")
    print("""
    - table_name: 表名
    - ddl: 表结构定义
    - row_count: 行数
    - is_large_table: 是否为大表
    - columns: 列信息列表
    - indexes: 索引信息列表
    - primary_keys: 主键列列表
    - table_exists: 表是否存在
    - db_alias: 数据库别名
    - instance_alias: 实例别名 (如 'db_production:1')
    - instance_index: 实例索引
    - database: 数据库名
    """)
    
    print("\n示例场景2: 依次尝试所有实例直到找到表")
    print("使用 collect_metadata_until_found() 方法:")
    print("""
    metadata = metadata_collector.collect_metadata_until_found(
        'db_production',
        table_names
    )
    """)
    print("这个方法会按顺序尝试每个实例，直到找到包含所有表的实例")
    
    print("\n示例场景3: 从特定实例收集元数据")
    print("使用 collect_metadata() 方法并指定实例索引:")
    print("""
    # 从第一个实例 (索引0) 收集
    metadata1 = metadata_collector.collect_metadata(
        'db_production', 
        table_names, 
        instance_index=0
    )
    
    # 从第二个实例 (索引1) 收集
    metadata2 = metadata_collector.collect_metadata(
        'db_production', 
        table_names, 
        instance_index=1
    )
    """)
    
    # 4. 执行计划获取
    print("\n4. 获取SQL执行计划")
    print("-" * 40)
    
    # 示例SQL
    example_sql = "SELECT * FROM users WHERE id = 1"
    
    print(f"示例SQL: {example_sql}")
    print("\n从特定实例获取执行计划:")
    print("""
    plan_result = metadata_collector.get_execution_plan(
        'db_production',
        example_sql,
        instance_index=0  # 从第一个实例获取
    )
    """)
    
    print("执行计划结果包含以下字段:")
    print("""
    - sql_type: SQL类型 (DML, DDL等)
    - has_execution_plan: 是否有执行计划
    - execution_plan: 原始执行计划数据
    - formatted_plan: 格式化后的执行计划文本
    - plan_summary: 执行计划摘要 (包含优化建议关键信息)
    - db_type: 数据库类型
    - explain_sql: 执行的EXPLAIN语句
    - row_count: 执行计划行数
    - db_alias: 数据库别名
    - instance_index: 实例索引
    - instance_alias: 实例别名
    """)
    
    print("\nplan_summary字段包含优化建议的关键信息:")
    print("""
    - has_full_scan: 是否有全表扫描
    - estimated_rows: 估计行数
    - key_used: 是否使用索引
    - access_types: 访问类型列表
    - warnings: 警告列表 (包含优化建议)
    """)
    
    # 5. 集成AI分析的建议
    print("\n5. 集成AI分析的建议")
    print("-" * 40)
    
    print("在实际使用中，AI分析的结果应该包含以下字段:")
    print("""
    analysis_result = {
        'sql_text': '原始SQL语句',
        'optimized_sql': '优化后的SQL语句',
        'suggestions': [
            '建议1: 添加索引...',
            '建议2: 优化JOIN条件...',
            '建议3: 避免全表扫描...'
        ],
        'performance_improvement': '预计性能提升',
        'risk_level': '风险等级',
        'execution_plan_comparison': '执行计划对比',
        'db_alias': '数据库别名',
        'instance_info': '实例信息'
    }
    """)
    
    print("\n对于多数据库场景，建议字段应该包含:")
    print("""
    - 每个数据库实例的分析结果
    - 不同实例之间的差异分析
    - 针对不同实例的优化建议
    - 统一的优化方案建议
    """)
    
    # 6. 配置建议
    print("\n6. 配置和使用建议")
    print("-" * 40)
    
    print("建议1: 在配置文件中使用一致的命名约定")
    print("""
    # 推荐格式
    [application_name:1]
    [application_name:2]
    [application_name:3]
    """)
    
    print("\n建议2: 根据业务需求选择合适的扫描策略")
    print("""
    - 如果表只在某个实例中存在: 使用 collect_metadata_until_found()
    - 如果需要对比不同实例的结构: 使用 collect_metadata_from_all_instances()
    - 如果明确知道表所在的实例: 使用 collect_metadata() 指定实例索引
    """)
    
    print("\n建议3: 在执行计划分析时考虑实例差异")
    print("""
    - 同一SQL在不同实例中可能有不同的执行计划
    - 建议对比多个实例的执行计划
    - 根据数据量和索引差异给出不同的优化建议
    """)
    
    print("\n建议4: 在AI分析结果中标记实例来源")
    print("""
    - 明确标注分析结果来自哪个数据库实例
    - 如果多个实例有差异，提供合并或差异化的建议
    - 对于生产环境，优先使用生产实例的分析结果
    """)
    
    print("\n7. 完整工作流程示例")
    print("-" * 40)
    
    workflow_example = """
# 1. 配置多数据库
config_manager = ConfigManager("config.ini")

# 2. 初始化收集器
metadata_collector = MetadataCollector(config_manager, logger)

# 3. 收集元数据（从所有实例）
all_metadata = metadata_collector.collect_metadata_from_all_instances(
    "db_production", 
    ["table1", "table2"]
)

# 4. 获取执行计划（从特定实例）
execution_plan = metadata_collector.get_execution_plan(
    "db_production",
    "SELECT * FROM table1",
    instance_index=0
)

# 5. 准备AI分析数据
analysis_data = {
    "sql": "SELECT * FROM table1",
    "metadata": all_metadata,
    "execution_plan": execution_plan,
    "instance_count": len(config_manager.get_all_target_db_configs("db_production"))
}

# 6. 调用AI分析（实际项目中会调用model_client）
# suggestions = model_client.analyze_sql(analysis_data)
"""
    
    print(workflow_example)
    
    print("\n" + "=" * 70)
    print("多数据库功能使用示例完成")
    print("=" * 70)
    
    print("\n关键点总结:")
    print("1. ✅ 支持配置多个相同别名的数据库实例")
    print("2. ✅ 提供三种扫描策略：全部实例、依次尝试、指定实例")
    print("3. ✅ 执行计划分析支持实例索引")
    print("4. ✅ 元数据结果包含实例信息")
    print("5. ✅ 保持向后兼容性")
    print("6. ✅ 完整的错误处理和日志记录")
    print("7. ✅ 便于集成AI分析的多实例支持")

if __name__ == "__main__":
    main()
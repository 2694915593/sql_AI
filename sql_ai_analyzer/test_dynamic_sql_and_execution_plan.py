#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试动态SQL生成和SQL执行计划生成功能
"""

import json
from config.config_manager import ConfigManager
from ai_integration.model_client import ModelClient

def test_dynamic_sql_generation():
    """测试动态SQL生成功能"""
    print("=" * 80)
    print("测试动态SQL生成功能")
    print("=" * 80)
    
    # 加载配置
    config = ConfigManager('config/config.ini')
    
    # 创建实例
    model_client = ModelClient(config)
    
    # 测试不同的SQL类型
    test_cases = [
        {
            'name': 'SELECT语句',
            'sql': "SELECT * FROM users WHERE id = 1",
            'expected_examples': ['动态查询示例', '参数化查询示例', '存储过程调用示例']
        },
        {
            'name': 'INSERT语句',
            'sql': "INSERT INTO users (name, age) VALUES ('张三', 25)",
            'expected_examples': ['动态插入示例', '参数化插入示例', '批量插入注入示例']
        },
        {
            'name': 'UPDATE语句',
            'sql': "UPDATE users SET age = 30 WHERE name = '张三'",
            'expected_examples': ['动态更新示例', '参数化更新示例', '多条件更新注入示例']
        },
        {
            'name': 'DELETE语句',
            'sql': "DELETE FROM users WHERE id = 1",
            'expected_examples': ['动态删除示例', '参数化删除示例', '条件删除注入示例']
        }
    ]
    
    all_passed = True
    
    for test_case in test_cases:
        print(f"\n测试: {test_case['name']}")
        print(f"SQL: {test_case['sql']}")
        
        # 生成动态SQL示例
        examples = model_client._generate_dynamic_sql_examples(test_case['sql'])
        
        print(f"生成的示例数量: {len(examples)}")
        
        # 检查是否包含预期的示例
        for expected in test_case['expected_examples']:
            found = any(expected in example for example in examples)
            if found:
                print(f"  ✅ 包含: {expected}")
            else:
                print(f"  ❌ 缺少: {expected}")
                all_passed = False
        
        # 显示前3个示例
        print(f"  示例预览:")
        for i, example in enumerate(examples[:3], 1):
            print(f"    {i}. {example[:80]}...")
    
    # 测试表名提取
    print(f"\n测试表名提取功能:")
    test_sqls = [
        "SELECT * FROM users WHERE id = 1",
        "INSERT INTO orders (user_id, amount) VALUES (1, 100)",
        "UPDATE products SET price = 50 WHERE id = 1",
        "DELETE FROM logs WHERE date < '2024-01-01'"
    ]
    
    for sql in test_sqls:
        table_name = model_client._extract_table_name(sql)
        print(f"  SQL: {sql[:50]}...")
        print(f"    提取的表名: {table_name}")
    
    return all_passed

def test_execution_plan_generation():
    """测试SQL执行计划生成功能"""
    print("\n" + "=" * 80)
    print("测试SQL执行计划生成功能")
    print("=" * 80)
    
    # 加载配置
    config = ConfigManager('config/config.ini')
    
    # 创建实例
    model_client = ModelClient(config)
    
    # 测试数据
    test_tables = [
        {
            'table_name': 'users',
            'row_count': 10000,
            'is_large_table': False,
            'columns': [
                {'name': 'id', 'type': 'INT', 'nullable': False},
                {'name': 'name', 'type': 'VARCHAR', 'nullable': True},
                {'name': 'age', 'type': 'INT', 'nullable': True}
            ],
            'indexes': [
                {'name': 'idx_id', 'columns': ['id'], 'type': 'BTREE', 'unique': True},
                {'name': 'idx_name', 'columns': ['name'], 'type': 'BTREE', 'unique': False}
            ]
        },
        {
            'table_name': 'orders',
            'row_count': 500000,
            'is_large_table': True,
            'columns': [
                {'name': 'order_id', 'type': 'INT', 'nullable': False},
                {'name': 'user_id', 'type': 'INT', 'nullable': False},
                {'name': 'amount', 'type': 'DECIMAL', 'nullable': False}
            ],
            'indexes': [
                {'name': 'idx_order_id', 'columns': ['order_id'], 'type': 'BTREE', 'unique': True},
                {'name': 'idx_user_id', 'columns': ['user_id'], 'type': 'BTREE', 'unique': False}
            ]
        }
    ]
    
    # 测试不同的SQL类型
    test_cases = [
        {
            'name': 'SELECT语句',
            'sql': "SELECT * FROM users WHERE id = 1",
            'tables': [test_tables[0]]
        },
        {
            'name': '多表JOIN查询',
            'sql': "SELECT u.name, o.amount FROM users u JOIN orders o ON u.id = o.user_id",
            'tables': test_tables
        },
        {
            'name': 'INSERT语句',
            'sql': "INSERT INTO users (name, age) VALUES ('张三', 25)",
            'tables': [test_tables[0]]
        },
        {
            'name': 'UPDATE语句',
            'sql': "UPDATE users SET age = 30 WHERE name = '张三'",
            'tables': [test_tables[0]]
        },
        {
            'name': 'DELETE语句',
            'sql': "DELETE FROM users WHERE id = 1",
            'tables': [test_tables[0]]
        },
        {
            'name': '无WHERE条件的DELETE（高风险）',
            'sql': "DELETE FROM users",
            'tables': [test_tables[0]]
        }
    ]
    
    all_passed = True
    
    for test_case in test_cases:
        print(f"\n测试: {test_case['name']}")
        print(f"SQL: {test_case['sql']}")
        
        # 生成执行计划
        execution_plan = model_client._generate_execution_plan(
            test_case['sql'], 
            test_case['tables']
        )
        
        # 检查执行计划内容
        plan_lines = execution_plan.split('\n')
        print(f"执行计划行数: {len(plan_lines)}")
        
        # 检查关键部分
        required_sections = [
            'SQL执行计划分析',
            'SQL类型分析',
            '涉及表分析',
            '执行计划预测',
            '性能优化建议',
            '执行风险评估'
        ]
        
        for section in required_sections:
            found = any(section in line for line in plan_lines)
            if found:
                print(f"  ✅ 包含: {section}")
            else:
                print(f"  ❌ 缺少: {section}")
                all_passed = False
        
        # 显示执行计划预览
        print(f"  执行计划预览 (前10行):")
        for i, line in enumerate(plan_lines[:10], 1):
            print(f"    {i}. {line}")
        
        # 检查风险评估
        if '无WHERE条件的DELETE' in test_case['name']:
            if '⚠️ 风险' in execution_plan:
                print(f"  ✅ 正确识别高风险操作")
            else:
                print(f"  ❌ 未识别高风险操作")
                all_passed = False
    
    return all_passed

def test_prompt_integration():
    """测试prompt集成功能"""
    print("\n" + "=" * 80)
    print("测试prompt集成功能")
    print("=" * 80)
    
    # 加载配置
    config = ConfigManager('config/config.ini')
    
    # 创建实例
    model_client = ModelClient(config)
    
    # 构建测试请求数据
    request_data = {
        'sql_statement': "SELECT * FROM users WHERE id = 1",
        'db_alias': '生产数据库',
        'tables': [
            {
                'table_name': 'users',
                'row_count': 10000,
                'is_large_table': False,
                'ddl': 'CREATE TABLE users (id INT PRIMARY KEY, name VARCHAR(50), age INT)',
                'columns': [
                    {'name': 'id', 'type': 'INT', 'nullable': False},
                    {'name': 'name', 'type': 'VARCHAR', 'nullable': True},
                    {'name': 'age', 'type': 'INT', 'nullable': True}
                ],
                'indexes': [
                    {'name': 'idx_id', 'columns': ['id'], 'type': 'BTREE', 'unique': True}
                ]
            }
        ],
        'execution_plan': ''  # 不提供执行计划，让系统生成
    }
    
    print("构建请求数据:")
    print(json.dumps(request_data, ensure_ascii=False, indent=2))
    
    # 构建prompt
    payload = model_client._build_request_payload(request_data)
    prompt = payload.get('prompt', '')
    
    print(f"\n生成的prompt长度: {len(prompt)} 字符")
    
    # 检查prompt内容
    required_sections = [
        'SQL语句：',
        '数据库：生产数据库',
        '涉及的表信息：',
        '动态SQL示例（用于判断SQL注入漏洞）：',
        'SQL执行计划分析：',
        '请根据以下SQL评审规则进行分析：',
        '建表规则：',
        '表结构变更规则：',
        '新建/修改索引规则：',
        '数据量规则：',
        '请严格按照以下JSON格式回复：'
    ]
    
    all_passed = True
    
    print("\n检查prompt内容:")
    for section in required_sections:
        if section in prompt:
            print(f"  ✅ 包含: {section}")
        else:
            print(f"  ❌ 缺少: {section}")
            all_passed = False
    
    # 检查动态SQL示例
    if '动态查询示例' in prompt:
        print(f"  ✅ 包含动态SQL示例")
    else:
        print(f"  ❌ 缺少动态SQL示例")
        all_passed = False
    
    # 检查执行计划分析
    if 'SQL执行计划分析：' in prompt and '执行计划预测：' in prompt:
        print(f"  ✅ 包含执行计划分析")
    else:
        print(f"  ❌ 缺少执行计划分析")
        all_passed = False
    
    # 检查SQL评审规则
    if '建表规则：' in prompt and '索引无冗余' in prompt:
        print(f"  ✅ 包含SQL评审规则")
    else:
        print(f"  ❌ 缺少SQL评审规则")
        all_passed = False
    
    # 显示prompt预览
    print(f"\nprompt预览 (前500字符):")
    print(prompt[:500])
    print("...")
    
    return all_passed

def main():
    """主测试函数"""
    print("动态SQL生成和SQL执行计划生成功能测试")
    print("=" * 80)
    
    # 测试1: 动态SQL生成
    print("\n1. 测试动态SQL生成功能...")
    dynamic_sql_passed = test_dynamic_sql_generation()
    
    # 测试2: 执行计划生成
    print("\n2. 测试SQL执行计划生成功能...")
    execution_plan_passed = test_execution_plan_generation()
    
    # 测试3: prompt集成
    print("\n3. 测试prompt集成功能...")
    prompt_integration_passed = test_prompt_integration()
    
    # 总结
    print("\n" + "=" * 80)
    print("测试总结")
    print("=" * 80)
    
    results = {
        "动态SQL生成": "✅ 通过" if dynamic_sql_passed else "❌ 失败",
        "执行计划生成": "✅ 通过" if execution_plan_passed else "❌ 失败",
        "prompt集成": "✅ 通过" if prompt_integration_passed else "❌ 失败"
    }
    
    for test_name, result in results.items():
        print(f"{test_name:20} {result}")
    
    all_passed = dynamic_sql_passed and execution_plan_passed and prompt_integration_passed
    
    print("\n" + "=" * 80)
    print("功能实现总结")
    print("=" * 80)
    
    if all_passed:
        print("🎉 所有测试通过!")
        print("\n✅ 已成功实现以下功能:")
        print("1. 动态SQL生成功能")
        print("   • 根据SQL类型生成相应的动态SQL示例")
        print("   • 包含多种SQL注入示例")
        print("   • 提供防护建议")
        
        print("\n2. SQL执行计划生成功能")
        print("   • 基于SQL类型和表元数据生成执行计划分析")
        print("   • 包含SQL类型分析、表信息分析、执行计划预测")
        print("   • 提供性能优化建议和风险评估")
        
        print("\n3. prompt集成功能")
        print("   • 将动态SQL示例集成到prompt中")
        print("   • 将执行计划分析集成到prompt中")
        print("   • 完整的SQL评审规则集成")
        print("   • 结构化输出格式要求")
        
        print("\n🚀 系统现在具备:")
        print("• 智能SQL注入风险分析能力")
        print("• 基于元数据的执行计划分析能力")
        print("• 完整的SQL评审规则检查能力")
        print("• 结构化的大模型响应格式")
        
        print("\n📋 发送给大模型的prompt现在包含:")
        print("1. SQL语句和数据库信息")
        print("2. 表结构和索引信息")
        print("3. 动态SQL示例（用于SQL注入分析）")
        print("4. SQL执行计划分析")
        print("5. 完整的SQL评审规则")
        print("6. 结构化输出格式要求")
        
        print("\n🎯 大模型现在可以:")
        print("• 基于动态SQL示例分析SQL注入风险")
        print("• 基于执行计划分析SQL性能")
        print("• 基于完整规则进行SQL质量评审")
        print("• 返回结构化的分析结果")
    else:
        print("⚠ 部分测试未通过，请检查代码实现")
    
    print("\n" + "=" * 80)
    print("下一步:")
    print("1. 运行完整的API测试验证功能")
    print("2. 如果API服务正常，应该能收到更全面的分析结果")
    print("3. 监控日志确认所有功能正常工作")

if __name__ == '__main__':
    main()
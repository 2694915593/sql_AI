#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
大模型API完整请求报文示例
展示发送给大模型的完整请求数据
"""

import json
from ai_integration.model_client import ModelClient
from config.config_manager import ConfigManager

def create_example_request():
    """创建示例请求数据"""
    
    # 示例SQL语句
    sql_statement = "SELECT * FROM users u JOIN orders o ON u.id = o.user_id WHERE u.status = 'active' AND o.amount > 1000 ORDER BY o.create_date DESC"
    
    # 示例表元数据
    tables = [
        {
            "table_name": "users",
            "ddl": "CREATE TABLE users (\n  id INT PRIMARY KEY AUTO_INCREMENT,\n  username VARCHAR(50) NOT NULL,\n  email VARCHAR(100) UNIQUE NOT NULL,\n  status VARCHAR(20) DEFAULT 'active',\n  create_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,\n  update_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP\n)",
            "row_count": 150000,
            "is_large_table": True,
            "columns": [
                {"name": "id", "type": "int", "full_type": "int(11)", "nullable": False, "default": None, "comment": "用户ID"},
                {"name": "username", "type": "varchar", "full_type": "varchar(50)", "nullable": False, "default": None, "comment": "用户名"},
                {"name": "email", "type": "varchar", "full_type": "varchar(100)", "nullable": False, "default": None, "comment": "邮箱"},
                {"name": "status", "type": "varchar", "full_type": "varchar(20)", "nullable": True, "default": "'active'", "comment": "状态"},
                {"name": "create_date", "type": "timestamp", "full_type": "timestamp", "nullable": True, "default": "CURRENT_TIMESTAMP", "comment": "创建时间"},
                {"name": "update_date", "type": "timestamp", "full_type": "timestamp", "nullable": True, "default": "CURRENT_TIMESTAMP", "comment": "更新时间"}
            ],
            "indexes": [
                {"name": "idx_username", "columns": ["username"], "unique": False, "type": "BTREE"},
                {"name": "idx_status", "columns": ["status"], "unique": False, "type": "BTREE"},
                {"name": "idx_email", "columns": ["email"], "unique": True, "type": "BTREE"}
            ],
            "primary_keys": ["id"],
            "table_exists": True
        },
        {
            "table_name": "orders",
            "ddl": "CREATE TABLE orders (\n  id INT PRIMARY KEY AUTO_INCREMENT,\n  user_id INT NOT NULL,\n  order_no VARCHAR(50) UNIQUE NOT NULL,\n  amount DECIMAL(10,2) NOT NULL,\n  status VARCHAR(20) DEFAULT 'pending',\n  create_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,\n  FOREIGN KEY (user_id) REFERENCES users(id)\n)",
            "row_count": 500000,
            "is_large_table": True,
            "columns": [
                {"name": "id", "type": "int", "full_type": "int(11)", "nullable": False, "default": None, "comment": "订单ID"},
                {"name": "user_id", "type": "int", "full_type": "int(11)", "nullable": False, "default": None, "comment": "用户ID"},
                {"name": "order_no", "type": "varchar", "full_type": "varchar(50)", "nullable": False, "default": None, "comment": "订单号"},
                {"name": "amount", "type": "decimal", "full_type": "decimal(10,2)", "nullable": False, "default": None, "comment": "金额"},
                {"name": "status", "type": "varchar", "full_type": "varchar(20)", "nullable": True, "default": "'pending'", "comment": "状态"},
                {"name": "create_date", "type": "timestamp", "full_type": "timestamp", "nullable": True, "default": "CURRENT_TIMESTAMP", "comment": "创建时间"}
            ],
            "indexes": [
                {"name": "idx_user_id", "columns": ["user_id"], "unique": False, "type": "BTREE"},
                {"name": "idx_order_no", "columns": ["order_no"], "unique": True, "type": "BTREE"},
                {"name": "idx_status", "columns": ["status"], "unique": False, "type": "BTREE"},
                {"name": "idx_create_date", "columns": ["create_date"], "unique": False, "type": "BTREE"}
            ],
            "primary_keys": ["id"],
            "table_exists": True
        }
    ]
    
    # 构建请求数据
    request_data = {
        "sql_statement": sql_statement,
        "tables": tables,
        "db_alias": "production_db"
    }
    
    return request_data

def show_complete_request():
    """显示完整的请求报文"""
    print("=" * 80)
    print("大模型API完整请求报文示例")
    print("=" * 80)
    
    # 创建配置管理器（使用测试配置）
    config = ConfigManager('config/test_config.ini')
    
    # 创建模型客户端
    model_client = ModelClient(config)
    
    # 创建示例请求数据
    request_data = create_example_request()
    
    print("\n1. 原始请求数据 (request_data):")
    print("-" * 40)
    print(json.dumps(request_data, ensure_ascii=False, indent=2))
    
    print("\n2. 构建的请求负载 (payload):")
    print("-" * 40)
    
    # 使用模型客户端的方法构建payload
    payload = model_client._build_request_payload(request_data)
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    
    print("\n3. 完整的HTTP请求:")
    print("-" * 40)
    
    # 获取API配置
    ai_config = config.get_ai_model_config()
    api_url = ai_config.get('api_url', 'http://182.207.164.154:4004/aiQA.do')
    api_key = ai_config.get('api_key', 'your-api-key-here')
    
    # 构建请求头
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    if api_key:
        headers['Authorization'] = f'Bearer {api_key}'
    
    print(f"URL: POST {api_url}")
    print("Headers:")
    for key, value in headers.items():
        if key == 'Authorization':
            print(f"  {key}: Bearer [REDACTED]")
        else:
            print(f"  {key}: {value}")
    
    print("\nBody:")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    
    print("\n4. 请求的prompt内容:")
    print("-" * 40)
    prompt = payload.get('prompt', '')
    print(prompt)
    
    print("\n5. 预期的API响应格式:")
    print("-" * 40)
    
    expected_response = {
        "success": True,
        "analysis_result": {
            "sql_analysis": {
                "complexity": "中等",
                "performance_issues": [
                    "缺少复合索引: (users.status, orders.amount)",
                    "JOIN条件缺少索引覆盖"
                ],
                "potential_risks": [
                    "可能返回大量数据，建议添加LIMIT",
                    "status字段没有索引，可能导致全表扫描"
                ],
                "optimization_suggestions": [
                    "为users表添加复合索引: (status, id)",
                    "为orders表添加复合索引: (user_id, amount, create_date)",
                    "考虑分页查询，添加LIMIT子句"
                ]
            },
            "table_analysis": {
                "users": {
                    "row_count": 150000,
                    "index_coverage": "良好",
                    "suggestions": ["定期清理inactive用户"]
                },
                "orders": {
                    "row_count": 500000,
                    "index_coverage": "良好",
                    "suggestions": ["考虑按时间分区"]
                }
            },
            "overall_score": 7.5,
            "severity_level": "中等",
            "recommendations": [
                "立即优化: 添加复合索引",
                "建议优化: 添加分页限制",
                "长期优化: 考虑表分区"
            ]
        },
        "suggestions": [
            "添加复合索引提高查询性能",
            "使用分页限制返回数据量",
            "定期维护索引统计信息"
        ],
        "score": 7.5
    }
    
    print(json.dumps(expected_response, ensure_ascii=False, indent=2))
    
    print("\n" + "=" * 80)
    print("请求报文说明:")
    print("=" * 80)
    print("""
1. 请求流程:
   - 系统收集SQL语句和表元数据
   - 构建包含详细信息的prompt
   - 发送HTTP POST请求到AI API
   - 解析AI返回的JSON响应

2. 请求特点:
   - 使用简单的prompt格式，而非复杂的结构化数据
   - prompt包含SQL语句、表结构、数据量等信息
   - AI模型需要理解自然语言prompt并返回结构化分析

3. 当前API格式:
   - 只需要一个"prompt"参数
   - 所有信息都组织在prompt文本中
   - 简化了API调用，但依赖AI的文本理解能力

4. 响应处理:
   - 期望返回JSON格式的响应
   - 包含分析结果、建议和评分
   - 系统会解析并存储到数据库
    """)

if __name__ == '__main__':
    show_complete_request()
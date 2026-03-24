#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建测试表
"""

import pymysql

def create_test_tables():
    """创建测试表"""
    try:
        conn = pymysql.connect(
            host='localhost',
            port=3306,
            database='testdb',
            user='root',
            password='123456'
        )
        
        cursor = conn.cursor()
        
        print("开始创建测试表...")
        
        # 创建users表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT PRIMARY KEY,
                name VARCHAR(100),
                email VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_email (email)
            )
        """)
        print("✓ 创建users表")
        
        # 插入一些测试数据
        cursor.execute("INSERT INTO users (id, name, email) VALUES (1, '张三', 'zhangsan@example.com')")
        cursor.execute("INSERT INTO users (id, name, email) VALUES (2, '李四', 'lisi@example.com')")
        cursor.execute("INSERT INTO users (id, name, email) VALUES (3, '王五', 'wangwu@example.com')")
        print("✓ 插入users表测试数据")
        
        # 创建orders表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INT PRIMARY KEY,
                user_id INT,
                amount DECIMAL(10,2),
                status VARCHAR(20),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id),
                INDEX idx_user_id (user_id),
                INDEX idx_status (status)
            )
        """)
        print("✓ 创建orders表")
        
        # 插入一些测试数据
        cursor.execute("INSERT INTO orders (id, user_id, amount, status) VALUES (1, 1, 100.50, 'completed')")
        cursor.execute("INSERT INTO orders (id, user_id, amount, status) VALUES (2, 2, 200.75, 'pending')")
        print("✓ 插入orders表测试数据")
        
        # 创建products表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INT PRIMARY KEY,
                name VARCHAR(200),
                category VARCHAR(50),
                price DECIMAL(10,2),
                stock INT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_category (category),
                INDEX idx_price (price)
            )
        """)
        print("✓ 创建products表")
        
        # 插入一些测试数据
        cursor.execute("INSERT INTO products (id, name, category, price, stock) VALUES (1, '手机', 'electronics', 2999.00, 100)")
        cursor.execute("INSERT INTO products (id, name, category, price, stock) VALUES (2, '笔记本电脑', 'electronics', 5999.00, 50)")
        print("✓ 插入products表测试数据")
        
        # 创建transaction_logs表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transaction_logs (
                id BIGINT PRIMARY KEY AUTO_INCREMENT,
                user_id INT,
                action VARCHAR(50),
                amount DECIMAL(15,2),
                create_date DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_create_date (create_date),
                INDEX idx_user_id (user_id)
            )
        """)
        print("✓ 创建transaction_logs表")
        
        # 插入一些测试数据
        cursor.execute("INSERT INTO transaction_logs (user_id, action, amount, create_date) VALUES (1, 'purchase', 100.50, '2024-01-15')")
        cursor.execute("INSERT INTO transaction_logs (user_id, action, amount, create_date) VALUES (2, 'purchase', 200.75, '2024-02-20')")
        print("✓ 插入transaction_logs表测试数据")
        
        # 创建temp_logs表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS temp_logs (
                id INT PRIMARY KEY AUTO_INCREMENT,
                message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_created_at (created_at)
            )
        """)
        print("✓ 创建temp_logs表")
        
        # 插入一些测试数据
        cursor.execute("INSERT INTO temp_logs (message) VALUES ('测试日志1')")
        cursor.execute("INSERT INTO temp_logs (message) VALUES ('测试日志2')")
        print("✓ 插入temp_logs表测试数据")
        
        conn.commit()
        print("\n所有测试表创建完成！")
        
        # 显示表信息
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print(f"\n数据库中有 {len(tables)} 个表:")
        for table in tables:
            print(f"  - {table[0]}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f'数据库错误: {e}')
    except Exception as e:
        print(f'错误: {e}')

if __name__ == '__main__':
    create_test_tables()
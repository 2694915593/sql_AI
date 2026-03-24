#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库连接工具模块
提供统一的数据库连接管理
"""

import pymysql
# from mysql.connector import  # 已迁移到pymysql pooling
# import psycopg2  # 暂时注释掉，因为我们只使用MySQL
from typing import Dict, Any, Optional
import threading


class DBConnector:
    """数据库连接管理器"""
    
    _instances = {}
    _lock = threading.Lock()
    
    def __new__(cls, config: Dict[str, Any], pool_size: int = 5):
        """单例模式，确保相同的配置只有一个连接池"""
        key = tuple(sorted(config.items()))
        
        with cls._lock:
            if key not in cls._instances:
                instance = super().__new__(cls)
                instance._init_pool(config, pool_size)
                cls._instances[key] = instance
            
            return cls._instances[key]
    
    def _init_pool(self, config: Dict[str, Any], pool_size: int):
        """初始化连接池"""
        self.config = config
        self.db_type = config.get('db_type', 'mysql').lower()
        self.pool_size = pool_size
        
        if self.db_type == 'mysql':
            self._init_mysql_pool()
        elif self.db_type == 'postgresql':
            self._init_postgresql_pool()
        else:
            raise ValueError(f"不支持的数据库类型: {self.db_type}")
    
    def _init_mysql_pool(self):
        """初始化MySQL连接池"""
        pool_config = {
            'host': self.config.get('host', 'localhost'),
            'port': self.config.get('port', 3306),
            'database': self.config.get('database', ''),
            'user': self.config.get('username', ''),
            'password': self.config.get('password', ''),
            'pool_name': f"mysql_pool_{id(self)}",
            'pool_size': self.pool_size,
            'pool_reset_session': True,
            'charset': 'utf8mb4',
            'use_unicode': True,
            'autocommit': True
        }
        
        # 移除空值配置
        pool_config = {k: v for k, v in pool_config.items() if v is not None}
        
        try:
            self.pool = # mysql.connector.pooling.MySQLConnectionPool  # 已迁移到pymysql(**pool_config)
        except Exception as e:
            raise ConnectionError(f"MySQL连接池初始化失败: {str(e)}")
    
    def _init_postgresql_pool(self):
        """初始化PostgreSQL连接池（简单实现）"""
        # PostgreSQL没有内置连接池，这里使用简单的连接管理
        raise NotImplementedError("PostgreSQL支持暂未实现，请使用MySQL")
        # self.pool_config = {
        #     'host': self.config.get('host', 'localhost'),
        #     'port': self.config.get('port', 5432),
        #     'database': self.config.get('database', ''),
        #     'user': self.config.get('username', ''),
        #     'password': self.config.get('password', ''),
        # }
        # self.connections = []
    
    def get_connection(self):
        """获取数据库连接"""
        if self.db_type == 'mysql':
            return self.pool.get_connection()
        elif self.db_type == 'postgresql':
            # PostgreSQL简单连接管理
            raise NotImplementedError("PostgreSQL支持暂未实现，请使用MySQL")
            # conn = psycopg2.connect(**self.pool_config)
            # self.connections.append(conn)
            # return conn
        else:
            raise ValueError(f"不支持的数据库类型: {self.db_type}")
    
    def execute_query(self, query: str, params: tuple = None, fetch_one: bool = False):
        """
        执行查询
        
        Args:
            query: SQL查询语句
            params: 查询参数
            fetch_one: 是否只获取一条记录
            
        Returns:
            查询结果
        """
        conn = None
        cursor = None
        
        try:
            conn = self.get_connection()
            cursor = conn.cursor(dictionary=True)
            
            cursor.execute(query, params or ())
            
            if query.strip().upper().startswith('SELECT'):
                if fetch_one:
                    result = cursor.fetchone()
                else:
                    result = cursor.fetchall()
            else:
                conn.commit()
                result = cursor.rowcount
            
            return result
            
        except Exception as e:
            if conn:
                conn.rollback()
            raise e
        finally:
            if cursor:
                cursor.close()
            if conn:
                # 重要：将连接返回到连接池
                conn.close()
                # 对于PostgreSQL，还需要从连接列表中移除
                if self.db_type == 'postgresql' and hasattr(self, 'connections'):
                    if conn in self.connections:
                        self.connections.remove(conn)
    
    def close_all(self):
        """关闭所有连接"""
        if self.db_type == 'mysql':
            # MySQL连接池会自动管理
            pass
        elif self.db_type == 'postgresql':
            for conn in self.connections:
                try:
                    conn.close()
                except:
                    pass
            self.connections.clear()


def create_db_connection(config: Dict[str, Any]) -> Any:
    """
    创建数据库连接（简化版，不使用连接池）
    
    Args:
        config: 数据库配置
        
    Returns:
        数据库连接对象
    """
    db_type = config.get('db_type', 'mysql').lower()
    
    if db_type == 'mysql':
        conn = pymysql.connect(
            host=config.get('host', 'localhost'),
            port=config.get('port', 3306),
            database=config.get('database', ''),
            user=config.get('username', ''),
            password=config.get('password', ''),
            charset='utf8mb4',
            use_unicode=True,
            autocommit=True
        )
        return conn
    
    elif db_type == 'postgresql':
        conn = psycopg2.connect(
            host=config.get('host', 'localhost'),
            port=config.get('port', 5432),
            database=config.get('database', ''),
            user=config.get('username', ''),
            password=config.get('password', ''),
        )
        return conn
    
    else:
        raise ValueError(f"不支持的数据库类型: {db_type}")


class DatabaseManager:
    """数据库管理器，封装常用操作"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化数据库管理器
        
        Args:
            config: 数据库配置
        """
        self.config = config
        self.connector = DBConnector(config)
    
    def fetch_all(self, query: str, params: tuple = None) -> list:
        """
        获取所有记录
        
        Args:
            query: SQL查询语句
            params: 查询参数
            
        Returns:
            记录列表
        """
        return self.connector.execute_query(query, params, fetch_one=False)
    
    def fetch_one(self, query: str, params: tuple = None) -> Optional[dict]:
        """
        获取一条记录
        
        Args:
            query: SQL查询语句
            params: 查询参数
            
        Returns:
            单条记录或None
        """
        return self.connector.execute_query(query, params, fetch_one=True)
    
    def execute(self, query: str, params: tuple = None) -> int:
        """
        执行更新操作
        
        Args:
            query: SQL语句
            params: 参数
            
        Returns:
            影响的行数
        """
        return self.connector.execute_query(query, params)
    
    def insert(self, table: str, data: Dict[str, Any]) -> int:
        """
        插入数据
        
        Args:
            table: 表名
            data: 数据字典
            
        Returns:
            插入的行ID（如果支持）
        """
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['%s'] * len(data))
        values = tuple(data.values())
        
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        
        if self.config.get('db_type') == 'mysql':
            query += "; SELECT LAST_INSERT_ID();"
            result = self.connector.execute_query(query, values)
            return result
        else:
            self.connector.execute_query(query, values)
            # PostgreSQL需要不同的方式获取ID
            return 0
    
    def update(self, table: str, data: Dict[str, Any], where: str, where_params: tuple = None) -> int:
        """
        更新数据
        
        Args:
            table: 表名
            data: 要更新的数据
            where: WHERE条件
            where_params: WHERE条件参数
            
        Returns:
            影响的行数
        """
        set_clause = ', '.join([f"{k} = %s" for k in data.keys()])
        values = tuple(data.values())
        
        if where_params:
            values += where_params
        
        query = f"UPDATE {table} SET {set_clause} WHERE {where}"
        return self.connector.execute_query(query, values)
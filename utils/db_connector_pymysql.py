#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库连接工具模块 - 使用pymysql
提供统一的数据库连接管理
"""

import pymysql
from pymysql import cursors
from typing import Dict, Any, Optional, List
import threading
import queue
import time


class PyMySQLConnectionPool:
    """简单的pymysql连接池"""
    
    def __init__(self, config: Dict[str, Any], pool_size: int = 5):
        """
        初始化连接池
        
        Args:
            config: 数据库配置
            pool_size: 连接池大小
        """
        self.config = config
        self.pool_size = pool_size
        self._pool = queue.Queue(maxsize=pool_size)
        self._lock = threading.Lock()
        
        # 初始化连接
        for _ in range(pool_size):
            conn = self._create_connection()
            self._pool.put(conn)
    
    def _create_connection(self):
        """创建新连接"""
        try:
            conn = pymysql.connect(
                host=self.config.get('host', 'localhost'),
                port=int(self.config.get('port', 3306)),
                database=self.config.get('database', ''),
                user=self.config.get('username', ''),
                password=self.config.get('password', ''),
                charset='utf8mb4',
                cursorclass=cursors.DictCursor,
                autocommit=True
            )
            return conn
        except Exception as e:
            raise ConnectionError(f"创建数据库连接失败: {str(e)}")
    
    def get_connection(self, timeout: float = 5.0):
        """
        从连接池获取连接
        
        Args:
            timeout: 获取连接的超时时间（秒）
            
        Returns:
            数据库连接
        """
        try:
            # 尝试从队列获取连接
            conn = self._pool.get(timeout=timeout)
            
            # 检查连接是否有效
            try:
                conn.ping(reconnect=True)
            except:
                # 连接无效，创建新连接
                conn = self._create_connection()
            
            return conn
        except queue.Empty:
            raise ConnectionError("连接池已耗尽，请稍后重试")
    
    def return_connection(self, conn):
        """将连接返回到连接池"""
        if conn:
            try:
                # 检查连接是否仍然有效
                conn.ping(reconnect=True)
                self._pool.put(conn, timeout=1.0)
            except:
                # 连接无效，创建新连接
                try:
                    new_conn = self._create_connection()
                    self._pool.put(new_conn, timeout=1.0)
                except:
                    pass  # 忽略创建新连接失败
    
    def close_all(self):
        """关闭所有连接"""
        while not self._pool.empty():
            try:
                conn = self._pool.get_nowait()
                conn.close()
            except:
                pass


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
        """初始化MySQL连接池（使用pymysql）"""
        try:
            self.pool = PyMySQLConnectionPool(self.config, self.pool_size)
        except Exception as e:
            raise ConnectionError(f"MySQL连接池初始化失败: {str(e)}")
    
    def _init_postgresql_pool(self):
        """初始化PostgreSQL连接池（简单实现）"""
        # PostgreSQL支持暂未实现
        raise NotImplementedError("PostgreSQL支持暂未实现，请使用MySQL")
    
    def get_connection(self):
        """获取数据库连接"""
        if self.db_type == 'mysql':
            return self.pool.get_connection()
        elif self.db_type == 'postgresql':
            raise NotImplementedError("PostgreSQL支持暂未实现，请使用MySQL")
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
        
        try:
            conn = self.get_connection()
            
            with conn.cursor() as cursor:
                cursor.execute(query, params or ())
                
                # 检查是否是SELECT查询或SHOW查询
                query_upper = query.strip().upper()
                is_select_query = query_upper.startswith('SELECT') or query_upper.startswith('SHOW')
                
                if is_select_query:
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
            if conn:
                # 将连接返回到连接池
                if self.db_type == 'mysql':
                    self.pool.return_connection(conn)
    
    def close_all(self):
        """关闭所有连接"""
        if self.db_type == 'mysql':
            self.pool.close_all()


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
            port=int(config.get('port', 3306)),
            database=config.get('database', ''),
            user=config.get('username', ''),
            password=config.get('password', ''),
            charset='utf8mb4',
            cursorclass=cursors.DictCursor,
            autocommit=True
        )
        return conn
    
    elif db_type == 'postgresql':
        # PostgreSQL支持暂未实现
        raise NotImplementedError("PostgreSQL支持暂未实现，请使用MySQL")
    
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
    
    def fetch_all(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """
        获取所有记录
        
        Args:
            query: SQL查询语句
            params: 查询参数
            
        Returns:
            记录列表
        """
        return self.connector.execute_query(query, params, fetch_one=False) or []
    
    def fetch_one(self, query: str, params: tuple = None) -> Optional[Dict[str, Any]]:
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
            conn = None
            try:
                conn = create_db_connection(self.config)
                with conn.cursor() as cursor:
                    cursor.execute(query, values)
                    conn.commit()
                    return cursor.lastrowid
            finally:
                if conn:
                    conn.close()
        else:
            self.connector.execute_query(query, values)
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
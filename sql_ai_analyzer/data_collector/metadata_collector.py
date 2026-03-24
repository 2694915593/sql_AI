#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
元数据收集器模块
负责收集表的元数据信息
"""

from typing import List, Dict, Any, Optional
import re
from utils.logger import LogMixin
from utils.db_connector_pymysql import DatabaseManager


class MetadataCollector(LogMixin):
    """元数据收集器"""
    
    def __init__(self, config_manager, logger=None):
        """
        初始化元数据收集器
        
        Args:
            config_manager: 配置管理器
            logger: 日志记录器
        """
        self.config_manager = config_manager
        
        if logger:
            self.set_logger(logger)
        
        self.logger.info("元数据收集器初始化完成")
    
    def collect_metadata(self, db_alias: str, table_names: List[str]) -> List[Dict[str, Any]]:
        """
        收集表的元数据
        
        Args:
            db_alias: 数据库别名
            table_names: 表名列表
            
        Returns:
            元数据列表
        """
        if not table_names:
            self.logger.warning("没有表名需要收集元数据")
            return []
        
        try:
            # 获取目标数据库配置
            target_config = self.config_manager.get_target_db_config(db_alias)
            target_db = DatabaseManager(target_config)
            
            metadata_list = []
            
            for table_name in table_names:
                try:
                    metadata = self._collect_table_metadata(target_db, table_name, target_config['db_type'])
                    if metadata:
                        metadata_list.append(metadata)
                    else:
                        self.logger.warning(f"表 {table_name} 元数据收集失败")
                except Exception as e:
                    self.logger.error(f"收集表 {table_name} 元数据时发生错误: {str(e)}")
                    # 继续收集其他表
        
            self.logger.info(f"成功收集 {len(metadata_list)}/{len(table_names)} 个表的元数据")
            return metadata_list
            
        except Exception as e:
            self.logger.error(f"收集元数据时发生错误: {str(e)}", exc_info=True)
            return []
    
    def _check_table_exists(self, db_manager: DatabaseManager, table_name: str, db_type: str) -> bool:
        """
        检查表是否存在
        
        Args:
            db_manager: 数据库管理器
            table_name: 表名
            db_type: 数据库类型
            
        Returns:
            表是否存在
        """
        try:
            if db_type == 'mysql':
                query = "SELECT COUNT(*) as count FROM information_schema.TABLES WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = %s"
                result = db_manager.fetch_one(query, (table_name,))
                return result and result.get('count', 0) > 0
            elif db_type == 'postgresql':
                query = "SELECT COUNT(*) as count FROM information_schema.tables WHERE table_name = %s"
                result = db_manager.fetch_one(query, (table_name,))
                return result and result.get('count', 0) > 0
            else:
                # 默认尝试查询表，如果失败则认为表不存在
                try:
                    db_manager.fetch_one(f"SELECT 1 FROM {table_name} LIMIT 1")
                    return True
                except:
                    return False
        except Exception as e:
            self.logger.warning(f"检查表 {table_name} 是否存在时发生错误: {str(e)}")
            return False
    
    def _collect_table_metadata(self, db_manager: DatabaseManager, table_name: str, db_type: str) -> Optional[Dict[str, Any]]:
        """
        收集单个表的元数据
        
        Args:
            db_manager: 数据库管理器
            table_name: 表名
            db_type: 数据库类型
            
        Returns:
            表元数据字典
        """
        metadata = {
            'table_name': table_name,
            'ddl': '',
            'row_count': 0,
            'is_large_table': False,
            'columns': [],
            'indexes': [],
            'primary_keys': [],
            'table_exists': True
        }
        
        try:
            # 首先检查表是否存在
            if not self._check_table_exists(db_manager, table_name, db_type):
                self.logger.warning(f"表 {table_name} 不存在，跳过元数据收集")
                metadata['table_exists'] = False
                metadata['error'] = f"表 {table_name} 不存在"
                return metadata
            
            # 获取DDL
            metadata['ddl'] = self._get_table_ddl(db_manager, table_name, db_type)
            
            # 获取行数
            metadata['row_count'] = self._get_table_row_count(db_manager, table_name, db_type)
            
            # 判断是否为大表
            large_table_threshold = self.config_manager.get_processing_config().get('large_table_threshold', 100000)
            metadata['is_large_table'] = metadata['row_count'] > large_table_threshold
            
            # 获取列信息
            metadata['columns'] = self._get_table_columns(db_manager, table_name, db_type)
            
            # 获取索引信息
            metadata['indexes'] = self._get_table_indexes(db_manager, table_name, db_type)
            
            # 获取主键信息
            metadata['primary_keys'] = self._get_primary_keys(db_manager, table_name, db_type)
            
            self.logger.debug(f"收集到表 {table_name} 的元数据: {len(metadata['columns'])} 列, {metadata['row_count']} 行")
            return metadata
            
        except Exception as e:
            self.logger.error(f"收集表 {table_name} 元数据时发生错误: {str(e)}")
            metadata['table_exists'] = False
            metadata['error'] = str(e)
            return metadata
    
    def _get_table_ddl(self, db_manager: DatabaseManager, table_name: str, db_type: str) -> str:
        """获取表DDL"""
        try:
            if db_type == 'mysql':
                # 使用更简单的方法获取表结构，避免SHOW CREATE TABLE的问题
                query = """
                    SELECT 
                        CONCAT(
                            'CREATE TABLE ', table_name, ' (',
                            GROUP_CONCAT(
                                CONCAT(
                                    column_name, ' ', column_type,
                                    IF(is_nullable = 'NO', ' NOT NULL', ''),
                                    IF(column_default IS NOT NULL, CONCAT(' DEFAULT ', QUOTE(column_default)), ''),
                                    IF(extra != '', CONCAT(' ', extra), ''),
                                    IF(column_comment != '', CONCAT(' COMMENT ', QUOTE(column_comment)), '')
                                )
                                ORDER BY ordinal_position
                                SEPARATOR ', '
                            ),
                            ')'
                        ) as ddl
                    FROM information_schema.columns
                    WHERE table_schema = DATABASE() 
                    AND table_name = %s
                    GROUP BY table_name
                """
                result = db_manager.fetch_one(query, (table_name,))
                if result and 'ddl' in result:
                    return result['ddl']
            elif db_type == 'postgresql':
                query = """
                    SELECT 
                        'CREATE TABLE ' || table_name || ' (' || 
                        string_agg(column_definition, ', ') || 
                        COALESCE(', ' || constraint_definitions, '') || 
                        ');' as ddl
                    FROM (
                        SELECT 
                            c.table_name,
                            c.column_name || ' ' || c.data_type || 
                            CASE WHEN c.is_nullable = 'NO' THEN ' NOT NULL' ELSE '' END as column_definition
                        FROM information_schema.columns c
                        WHERE c.table_name = %s
                        ORDER BY c.ordinal_position
                    ) cols
                    LEFT JOIN (
                        SELECT 
                            tc.table_name,
                            string_agg(
                                'CONSTRAINT ' || tc.constraint_name || ' ' || 
                                CASE WHEN tc.constraint_type = 'PRIMARY KEY' THEN 'PRIMARY KEY (' || 
                                    string_agg(kcu.column_name, ', ') || ')'
                                WHEN tc.constraint_type = 'FOREIGN KEY' THEN 'FOREIGN KEY (' || 
                                    string_agg(kcu.column_name, ', ') || ') REFERENCES ' || 
                                    ccu.table_name || '(' || string_agg(ccu.column_name, ', ') || ')'
                                ELSE tc.constraint_type
                                END, ', '
                            ) as constraint_definitions
                        FROM information_schema.table_constraints tc
                        JOIN information_schema.key_column_usage kcu 
                            ON tc.constraint_name = kcu.constraint_name
                        JOIN information_schema.constraint_column_usage ccu 
                            ON tc.constraint_name = ccu.constraint_name
                        WHERE tc.table_name = %s
                        GROUP BY tc.table_name, tc.constraint_type
                    ) cons ON cols.table_name = cons.table_name
                    GROUP BY cols.table_name, constraint_definitions
                """
                result = db_manager.fetch_one(query, (table_name, table_name))
                if result and 'ddl' in result:
                    return result['ddl']
        
        except Exception as e:
            self.logger.warning(f"获取表 {table_name} DDL失败: {str(e)}")
        
        return f"CREATE TABLE {table_name} (/* 无法获取完整DDL */)"
    
    def _get_table_row_count(self, db_manager: DatabaseManager, table_name: str, db_type: str) -> int:
        """获取表行数"""
        try:
            # 使用近似行数查询，避免全表扫描
            if db_type == 'mysql':
                query = f"SELECT TABLE_ROWS as row_count FROM information_schema.TABLES WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = %s"
                result = db_manager.fetch_one(query, (table_name,))
                if result and 'row_count' in result:
                    return int(result['row_count'] or 0)
            
            # 如果近似行数不可用，使用COUNT(*)
            query = f"SELECT COUNT(*) as row_count FROM {table_name}"
            result = db_manager.fetch_one(query)
            if result and 'row_count' in result:
                return int(result['row_count'])
        
        except Exception as e:
            self.logger.warning(f"获取表 {table_name} 行数失败: {str(e)}")
        
        return 0
    
    def _get_table_columns(self, db_manager: DatabaseManager, table_name: str, db_type: str) -> List[Dict[str, Any]]:
        """获取表列信息"""
        columns = []
        
        try:
            if db_type == 'mysql':
                query = """
                    SELECT 
                        COLUMN_NAME as column_name,
                        DATA_TYPE as data_type,
                        COLUMN_TYPE as full_type,
                        IS_NULLABLE as is_nullable,
                        COLUMN_DEFAULT as column_default,
                        COLUMN_COMMENT as column_comment,
                        CHARACTER_MAXIMUM_LENGTH as max_length,
                        NUMERIC_PRECISION as numeric_precision,
                        NUMERIC_SCALE as numeric_scale
                    FROM information_schema.COLUMNS
                    WHERE TABLE_SCHEMA = DATABASE() 
                    AND TABLE_NAME = %s
                    ORDER BY ORDINAL_POSITION
                """
                results = db_manager.fetch_all(query, (table_name,))
                
                for row in results:
                    column_info = {
                        'name': row['column_name'],
                        'type': row['data_type'],
                        'full_type': row['full_type'],
                        'nullable': row['is_nullable'] == 'YES',
                        'default': row['column_default'],
                        'comment': row['column_comment'],
                        'max_length': row['max_length'],
                        'numeric_precision': row['numeric_precision'],
                        'numeric_scale': row['numeric_scale']
                    }
                    columns.append(column_info)
            
            elif db_type == 'postgresql':
                query = """
                    SELECT 
                        column_name,
                        data_type,
                        is_nullable,
                        column_default,
                        character_maximum_length,
                        numeric_precision,
                        numeric_scale
                    FROM information_schema.columns
                    WHERE table_name = %s
                    ORDER BY ordinal_position
                """
                results = db_manager.fetch_all(query, (table_name,))
                
                for row in results:
                    column_info = {
                        'name': row['column_name'],
                        'type': row['data_type'],
                        'full_type': row['data_type'],
                        'nullable': row['is_nullable'] == 'YES',
                        'default': row['column_default'],
                        'comment': '',
                        'max_length': row['character_maximum_length'],
                        'numeric_precision': row['numeric_precision'],
                        'numeric_scale': row['numeric_scale']
                    }
                    columns.append(column_info)
        
        except Exception as e:
            self.logger.warning(f"获取表 {table_name} 列信息失败: {str(e)}")
        
        return columns
    
    def _get_table_indexes(self, db_manager: DatabaseManager, table_name: str, db_type: str) -> List[Dict[str, Any]]:
        """获取表索引信息"""
        indexes = []
        
        try:
            if db_type == 'mysql':
                # 使用information_schema查询索引信息，避免SHOW INDEX的问题
                query = """
                    SELECT 
                        INDEX_NAME as index_name,
                        COLUMN_NAME as column_name,
                        NON_UNIQUE as non_unique,
                        INDEX_TYPE as index_type,
                        SEQ_IN_INDEX as seq_in_index
                    FROM information_schema.STATISTICS
                    WHERE TABLE_SCHEMA = DATABASE()
                    AND TABLE_NAME = %s
                    AND INDEX_NAME != 'PRIMARY'
                    ORDER BY INDEX_NAME, SEQ_IN_INDEX
                """
                results = db_manager.fetch_all(query, (table_name,))
                
                # 按索引名分组
                index_dict = {}
                for row in results:
                    index_name = row['index_name']
                    
                    if index_name not in index_dict:
                        index_dict[index_name] = {
                            'name': index_name,
                            'columns': [],
                            'unique': row['non_unique'] == 0,
                            'type': row['index_type']
                        }
                    
                    index_dict[index_name]['columns'].append(row['column_name'])
                
                indexes = list(index_dict.values())
            
            elif db_type == 'postgresql':
                query = """
                    SELECT
                        i.relname as index_name,
                        a.attname as column_name,
                        ix.indisunique as is_unique,
                        am.amname as index_type
                    FROM pg_index ix
                    JOIN pg_class t ON t.oid = ix.indrelid
                    JOIN pg_class i ON i.oid = ix.indexrelid
                    JOIN pg_am am ON i.relam = am.oid
                    JOIN pg_attribute a ON a.attrelid = t.oid AND a.attnum = ANY(ix.indkey)
                    WHERE t.relname = %s
                    AND ix.indisprimary = false
                    ORDER BY i.relname, array_position(ix.indkey, a.attnum)
                """
                results = db_manager.fetch_all(query, (table_name,))
                
                # 按索引名分组
                index_dict = {}
                for row in results:
                    index_name = row['index_name']
                    
                    if index_name not in index_dict:
                        index_dict[index_name] = {
                            'name': index_name,
                            'columns': [],
                            'unique': row['is_unique'],
                            'type': row['index_type']
                        }
                    
                    index_dict[index_name]['columns'].append(row['column_name'])
                
                indexes = list(index_dict.values())
        
        except Exception as e:
            self.logger.warning(f"获取表 {table_name} 索引信息失败: {str(e)}")
        
        return indexes
    
    def _get_primary_keys(self, db_manager: DatabaseManager, table_name: str, db_type: str) -> List[str]:
        """获取主键列"""
        primary_keys = []
        
        try:
            if db_type == 'mysql':
                query = """
                    SELECT COLUMN_NAME
                    FROM information_schema.KEY_COLUMN_USAGE
                    WHERE TABLE_SCHEMA = DATABASE()
                    AND TABLE_NAME = %s
                    AND CONSTRAINT_NAME = 'PRIMARY'
                    ORDER BY ORDINAL_POSITION
                """
                results = db_manager.fetch_all(query, (table_name,))
                primary_keys = [row['COLUMN_NAME'] for row in results]
            
            elif db_type == 'postgresql':
                query = """
                    SELECT a.attname as column_name
                    FROM pg_index ix
                    JOIN pg_class t ON t.oid = ix.indrelid
                    JOIN pg_attribute a ON a.attrelid = t.oid AND a.attnum = ANY(ix.indkey)
                    WHERE t.relname = %s
                    AND ix.indisprimary = true
                    ORDER BY array_position(ix.indkey, a.attnum)
                """
                results = db_manager.fetch_all(query, (table_name,))
                primary_keys = [row['column_name'] for row in results]
        
        except Exception as e:
            self.logger.warning(f"获取表 {table_name} 主键信息失败: {str(e)}")
        
        return primary_keys
    
    def detect_sql_type(self, sql_text: str) -> str:
        """
        检测SQL语句类型
        
        Args:
            sql_text: SQL语句文本
            
        Returns:
            SQL类型: DML, DDL, DCL, TCL 或 UNKNOWN
        """
        if not sql_text or not sql_text.strip():
            return "UNKNOWN"
        
        sql_upper = sql_text.strip().upper()
        
        # DML语句 (数据操作语言)
        dml_keywords = ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'MERGE', 'CALL', 'EXPLAIN']
        for keyword in dml_keywords:
            if sql_upper.startswith(keyword):
                return "DML"
        
        # DDL语句 (数据定义语言)
        ddl_keywords = ['CREATE', 'ALTER', 'DROP', 'TRUNCATE', 'RENAME', 'COMMENT']
        for keyword in ddl_keywords:
            if sql_upper.startswith(keyword):
                return "DDL"
        
        # DCL语句 (数据控制语言)
        dcl_keywords = ['GRANT', 'REVOKE']
        for keyword in dcl_keywords:
            if sql_upper.startswith(keyword):
                return "DCL"
        
        # TCL语句 (事务控制语言)
        tcl_keywords = ['COMMIT', 'ROLLBACK', 'SAVEPOINT', 'SET TRANSACTION']
        for keyword in tcl_keywords:
            if sql_upper.startswith(keyword):
                return "TCL"
        
        return "UNKNOWN"
    
    def get_execution_plan(self, db_alias: str, dynamic_sql: str) -> Dict[str, Any]:
        """
        获取SQL执行计划
        
        Args:
            db_alias: 数据库别名
            dynamic_sql: 动态SQL语句（参数已替换）
            
        Returns:
            执行计划信息
        """
        try:
            # 检测SQL类型，只有DML语句才有执行计划
            sql_type = self.detect_sql_type(dynamic_sql)
            
            if sql_type != 'DML':
                self.logger.info(f"SQL类型为 {sql_type}，无需获取执行计划")
                return {
                    'sql_type': sql_type,
                    'has_execution_plan': False,
                    'message': f'SQL类型为 {sql_type}，无需获取执行计划'
                }
            
            # 获取目标数据库配置
            target_config = self.config_manager.get_target_db_config(db_alias)
            
            # 根据数据库类型执行不同的EXPLAIN命令
            db_type = target_config.get('db_type', 'mysql')
            
            # 创建数据库连接
            conn = None
            try:
                # 导入create_db_connection函数
                from utils.db_connector_pymysql import create_db_connection
                conn = create_db_connection(target_config)
                
                with conn.cursor() as cursor:
                    if db_type == 'mysql':
                        # MySQL使用EXPLAIN（EXTENDED在某些版本中已弃用）
                        explain_sql = f"EXPLAIN {dynamic_sql}"
                    elif db_type == 'postgresql':
                        # PostgreSQL使用EXPLAIN (FORMAT JSON)
                        explain_sql = f"EXPLAIN (FORMAT JSON) {dynamic_sql}"
                    else:
                        # 其他数据库使用普通EXPLAIN
                        explain_sql = f"EXPLAIN {dynamic_sql}"
                    
                    self.logger.info(f"执行EXPLAIN语句: {explain_sql[:100]}...")
                    cursor.execute(explain_sql)
                    
                    # 获取执行计划结果
                    if db_type == 'postgresql':
                        # PostgreSQL返回JSON格式
                        result = cursor.fetchone()
                        if result:
                            execution_plan = result[0] if isinstance(result, tuple) else result
                        else:
                            execution_plan = {}
                    else:
                        # 其他数据库返回表格格式
                        columns = [desc[0] for desc in cursor.description]
                        rows = cursor.fetchall()
                        
                        # 将结果转换为字典列表
                        execution_plan = []
                        for row in rows:
                            # 如果row已经是字典（如使用DictCursor），直接使用
                            if isinstance(row, dict):
                                execution_plan.append(row)
                            else:
                                # 否则转换为字典
                                row_dict = {}
                                for i, col in enumerate(columns):
                                    row_dict[col] = row[i]
                                execution_plan.append(row_dict)
                    
                    self.logger.info(f"成功获取执行计划，结果类型: {type(execution_plan)}")
                    
                    return {
                        'sql_type': sql_type,
                        'has_execution_plan': True,
                        'execution_plan': execution_plan,
                        'db_type': db_type,
                        'explain_sql': explain_sql
                    }
                    
            finally:
                if conn:
                    conn.close()
        
        except Exception as e:
            self.logger.error(f"获取执行计划时发生错误: {str(e)}", exc_info=True)
            return {
                'sql_type': self.detect_sql_type(dynamic_sql) if dynamic_sql else 'UNKNOWN',
                'has_execution_plan': False,
                'error': str(e),
                'message': f'获取执行计划失败: {str(e)}'
            }

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SQL提取与解析模块
负责从数据库读取待分析SQL并解析表名
"""

import re
import sqlparse
from typing import List, Dict, Any, Optional
from utils.logger import LogMixin
from utils.db_connector_pymysql import DatabaseManager
from .param_extractor import ParamExtractor


class SQLExtractor(LogMixin):
    """SQL提取器"""
    
    def __init__(self, config_manager, logger=None):
        """
        初始化SQL提取器
        
        Args:
            config_manager: 配置管理器
            logger: 日志记录器
        """
        self.config_manager = config_manager
        
        if logger:
            self.set_logger(logger)
        
        # 初始化源数据库连接
        source_config = config_manager.get_database_config()
        self.source_db = DatabaseManager(source_config)
        
        self.logger.info("SQL提取器初始化完成")
    
    def get_pending_sqls(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        获取待分析的SQL语句
        
        Args:
            limit: 获取数量限制
            
        Returns:
            SQL记录列表
        """
        try:
            # 根据实际表结构查询
            query = """
                SELECT 
                    ID as id,
                    SQLLINE as sql_text,
                    TABLENAME as table_name,
                    OPERATETYPE as operate_type,
                    PROJECTID as project_id,
                    SYSTEMID as system_id,
                    AUTHOR as author,
                    FILENAME as file_name
                FROM am_solline_info 
                WHERE (analysis_status IS NULL OR analysis_status = 'pending')
                AND SQLLINE IS NOT NULL 
                AND SQLLINE != ''
                ORDER BY ID ASC
                LIMIT %s
            """
            
            results = self.source_db.fetch_all(query, (limit,))
            
            self.logger.info(f"获取到 {len(results)} 条待分析SQL")
            return results
            
        except Exception as e:
            self.logger.error(f"获取待分析SQL时发生错误: {str(e)}", exc_info=True)
            return []
    
    def extract_sql_by_id(self, sql_id: int) -> Optional[Dict[str, Any]]:
        """
        根据ID提取SQL信息
        
        Args:
            sql_id: SQL记录ID
            
        Returns:
            SQL信息字典
        """
        try:
            query = """
                SELECT 
                    ID as id,
                    SQLLINE as sql_text,
                    TABLENAME as table_name,
                    OPERATETYPE as operate_type,
                    PROJECTID as project_id,
                    SYSTEMID as system_id,
                    AUTHOR as author,
                    FILENAME as file_name
                FROM am_solline_info 
                WHERE ID = %s
            """
            
            result = self.source_db.fetch_one(query, (sql_id,))
            
            if result:
                self.logger.info(f"提取到SQL ID {sql_id}: {result.get('sql_text', '')[:50]}...")
            else:
                self.logger.warning(f"未找到SQL ID {sql_id}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"提取SQL ID {sql_id} 时发生错误: {str(e)}", exc_info=True)
            return None
    
    def extract_table_names(self, sql_text: str, table_name_field: Optional[str] = None) -> List[str]:
        """
        提取表名
        
        Args:
            sql_text: SQL语句文本
            table_name_field: TABLENAME字段内容
            
        Returns:
            表名列表
        """
        # 优先使用TABLENAME字段
        if table_name_field and table_name_field.strip():
            tables = self.get_table_names_from_field(table_name_field)
            if tables:
                self.logger.debug(f"从TABLENAME字段提取到表名: {tables}")
                return tables
        
        # 如果TABLENAME字段为空，则从SQL语句中提取
        if not sql_text or not sql_text.strip():
            return []
        
        try:
            # 首先尝试使用sqlparse库解析
            tables = self._extract_tables_with_sqlparse(sql_text)
            
            # 如果sqlparse没有提取到表名，尝试使用正则表达式
            if not tables:
                tables = self._extract_tables_with_regex(sql_text)
            
            # 去重并清理表名
            tables = self._clean_table_names(tables)
            
            self.logger.debug(f"从SQL中提取到表名: {tables}")
            return tables
            
        except Exception as e:
            self.logger.error(f"提取表名时发生错误: {str(e)}", exc_info=True)
            # 出错时返回空列表
            return []
    
    def _extract_tables_with_sqlparse(self, sql_text: str) -> List[str]:
        """使用sqlparse库提取表名"""
        tables = []
        
        try:
            parsed = sqlparse.parse(sql_text)
            
            for statement in parsed:
                # 使用sqlparse的get_identifiers方法获取标识符
                # 但我们需要更精确地提取表名，而不是所有标识符
                from_clause_found = False
                
                for token in statement.tokens:
                    # 检查是否是FROM关键字
                    if token.is_keyword and token.value.upper() == 'FROM':
                        from_clause_found = True
                        continue
                    
                    # 如果是FROM子句后的标识符，可能是表名
                    if from_clause_found and isinstance(token, sqlparse.sql.Identifier):
                        # 提取表名（可能包含别名）
                        table_name = str(token).split()[0]  # 取第一个词作为表名
                        tables.append(table_name)
                        from_clause_found = False
                    
                    # 检查JOIN子句
                    elif token.is_keyword and token.value.upper() in ['JOIN', 'INNER JOIN', 'LEFT JOIN', 'RIGHT JOIN', 'FULL JOIN']:
                        # 查找JOIN后的标识符
                        join_found = True
                        continue
                    
                    # 如果是JOIN后的标识符
                    elif 'join_found' in locals() and join_found and isinstance(token, sqlparse.sql.Identifier):
                        table_name = str(token).split()[0]
                        tables.append(table_name)
                        join_found = False
            
        except Exception as e:
            self.logger.debug(f"sqlparse解析失败: {str(e)}")
        
        return tables
    
    def _extract_tables_with_regex(self, sql_text: str) -> List[str]:
        """使用正则表达式提取表名"""
        tables = []
        
        # 移除注释
        sql_clean = re.sub(r'--.*?$|/\*.*?\*/', '', sql_text, flags=re.MULTILINE | re.DOTALL)
        
        # 改进的正则表达式模式，更精确地匹配表名
        
        # 1. 提取FROM子句后的表名
        # 匹配模式：FROM 表名 [别名] [WHERE/JOIN/ORDER/GROUP等]
        # 支持带引号的表名和带数据库前缀的表名
        from_pattern = r'\bFROM\s+([a-zA-Z_][\w\.]*|`[^`]+`|\'[^\']+\'|"[^"]+")(?:\s+(?:AS\s+)?[a-zA-Z_]\w*)?(?=\s+(?:WHERE|JOIN|ORDER\s+BY|GROUP\s+BY|HAVING|LIMIT|;|$))'
        from_matches = re.findall(from_pattern, sql_clean, re.IGNORECASE)
        tables.extend(from_matches)
        
        # 2. 提取JOIN子句后的表名
        join_pattern = r'\b(?:INNER\s+|LEFT\s+|RIGHT\s+|FULL\s+)?JOIN\s+([a-zA-Z_][\w\.]*|`[^`]+`|\'[^\']+\'|"[^"]+")(?:\s+(?:AS\s+)?[a-zA-Z_]\w*)?(?=\s+(?:ON|WHERE|ORDER\s+BY|GROUP\s+BY|HAVING|LIMIT|;|$))'
        join_matches = re.findall(join_pattern, sql_clean, re.IGNORECASE)
        tables.extend(join_matches)
        
        # 3. 提取INSERT INTO表名
        # 确保只匹配表名，不匹配字段列表
        insert_pattern = r'\bINSERT\s+(?:INTO\s+)?([a-zA-Z_][\w\.]*|`[^`]+`|\'[^\']+\'|"[^"]+")(?=\s*(?:\([^)]+\)\s+VALUES|VALUES|SELECT|;|$))'
        insert_matches = re.findall(insert_pattern, sql_clean, re.IGNORECASE)
        tables.extend(insert_matches)
        
        # 4. 提取UPDATE表名
        update_pattern = r'\bUPDATE\s+([a-zA-Z_][\w\.]*|`[^`]+`|\'[^\']+\'|"[^"]+")(?=\s+SET)'
        update_matches = re.findall(update_pattern, sql_clean, re.IGNORECASE)
        tables.extend(update_matches)
        
        # 5. 提取DELETE FROM表名
        delete_pattern = r'\bDELETE\s+(?:FROM\s+)?([a-zA-Z_][\w\.]*|`[^`]+`|\'[^\']+\'|"[^"]+")(?=\s+WHERE)'
        delete_matches = re.findall(delete_pattern, sql_clean, re.IGNORECASE)
        tables.extend(delete_matches)
        
        # 6. 提取CREATE TABLE表名
        create_pattern = r'\bCREATE\s+(?:TEMPORARY\s+)?TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?([a-zA-Z_][\w\.]*|`[^`]+`|\'[^\']+\'|"[^"]+")(?=\s*\()'
        create_matches = re.findall(create_pattern, sql_clean, re.IGNORECASE)
        tables.extend(create_matches)
        
        # 7. 提取ALTER TABLE表名
        alter_pattern = r'\bALTER\s+TABLE\s+([a-zA-Z_][\w\.]*|`[^`]+`|\'[^\']+\'|"[^"]+")(?=\s+(?:ADD|DROP|MODIFY|CHANGE|RENAME|$))'
        alter_matches = re.findall(alter_pattern, sql_clean, re.IGNORECASE)
        tables.extend(alter_matches)
        
        # 8. 提取DROP TABLE表名
        drop_pattern = r'\bDROP\s+(?:TEMPORARY\s+)?TABLE\s+(?:IF\s+EXISTS\s+)?([a-zA-Z_][\w\.]*|`[^`]+`|\'[^\']+\'|"[^"]+")(?=\s*(?:;|$))'
        drop_matches = re.findall(drop_pattern, sql_clean, re.IGNORECASE)
        tables.extend(drop_matches)
        
        # 9. 提取TRUNCATE TABLE表名
        truncate_pattern = r'\bTRUNCATE\s+(?:TABLE\s+)?([a-zA-Z_][\w\.]*|`[^`]+`|\'[^\']+\'|"[^"]+")(?=\s*(?:;|$))'
        truncate_matches = re.findall(truncate_pattern, sql_clean, re.IGNORECASE)
        tables.extend(truncate_matches)
        
        return tables
    
    def _clean_table_names(self, table_names: List[str]) -> List[str]:
        """清理表名"""
        cleaned = []
        
        for table in table_names:
            if not table:
                continue
            
            # 移除数据库前缀（如db.table -> table）
            if '.' in table:
                table = table.split('.')[-1]
            
            # 移除引号
            table = table.strip('`\'"')
            
            # 移除空格
            table = table.strip()
            
            if table and table not in cleaned:
                cleaned.append(table)
        
        return cleaned
    
    def get_table_names_from_field(self, table_name_field: str) -> List[str]:
        """
        从表名字段中提取表名列表
        
        Args:
            table_name_field: 表名字段内容（可能包含多个表名）
            
        Returns:
            表名列表
        """
        if not table_name_field:
            return []
        
        # 表名可能用逗号、分号或空格分隔
        separators = [',', ';', ' ', '，', '；']
        
        for sep in separators:
            if sep in table_name_field:
                tables = [t.strip() for t in table_name_field.split(sep) if t.strip()]
                if tables:
                    return tables
        
        # 如果没有分隔符，直接返回
        return [table_name_field.strip()]
    
    def update_analysis_status(self, sql_id: int, status: str, error_message: str = None) -> bool:
        """
        更新分析状态
        
        Args:
            sql_id: SQL记录ID
            status: 状态（pending/analyzed/failed）
            error_message: 错误信息
            
        Returns:
            是否成功
        """
        try:
            data = {
                'analysis_status': status
            }
            
            if error_message:
                data['error_message'] = error_message
            
            # 构建更新语句
            # 对于analysis_time，如果状态是analyzed，使用NOW()函数
            set_clause = ', '.join([f"{k} = %s" for k in data.keys()])
            if status == 'analyzed':
                set_clause += ', analysis_time = NOW()'
            
            values = [data[k] for k in data.keys()]
            values.append(sql_id)
            
            query = f"UPDATE am_solline_info SET {set_clause} WHERE ID = %s"
            
            affected = self.source_db.execute(query, tuple(values))
            
            if affected > 0:
                self.logger.info(f"更新SQL ID {sql_id} 状态为 {status}")
                return True
            else:
                self.logger.warning(f"更新SQL ID {sql_id} 状态失败，未找到记录")
                return False
                
        except Exception as e:
            self.logger.error(f"更新分析状态时发生错误: {str(e)}", exc_info=True)
            return False
    
    def generate_replaced_sql(self, sql_text: str) -> tuple:
        """
        生成替换参数后的SQL
        
        Args:
            sql_text: 原始SQL语句
            
        Returns:
            (替换后的SQL, 表名列表)
        """
        try:
            # 使用参数提取器生成替换后的SQL
            param_extractor = ParamExtractor(sql_text, self.logger)
            replaced_sql, tables = param_extractor.generate_replaced_sql()
            
            self.logger.info(f"生成替换参数后的SQL，原始SQL长度: {len(sql_text)}，替换后长度: {len(replaced_sql)}")
            
            # 如果参数提取器没有提取到表名，使用现有的提取表名方法
            if not tables:
                tables = self.extract_table_names(sql_text)
            
            return replaced_sql, tables
            
        except Exception as e:
            self.logger.error(f"生成替换参数后的SQL时发生错误: {str(e)}", exc_info=True)
            return sql_text, []

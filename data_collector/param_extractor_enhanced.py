#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
参数提取器模块
负责从SQL语句中提取参数并生成替换参数后的SQL
增强版：支持所有SQL类型（INSERT、SELECT、UPDATE、DELETE）的列名映射
"""

import re
from typing import List, Dict, Any, Optional
from ..utils.logger import LogMixin
from ..utils.sql_preprocessor import SQLPreprocessor


class ParamExtractor(LogMixin):
    """参数提取器"""
    
    def __init__(self, sql_text: str, logger=None, metadata_list=None, config_manager=None):
        """
        初始化参数提取器
        
        Args:
            sql_text: SQL语句文本
            logger: 日志记录器
            metadata_list: 表元数据列表
            config_manager: 配置管理器（用于数据值获取）
        """
        self.original_sql = sql_text
        self.metadata_list = metadata_list or []
        self.config_manager = config_manager
        
        # 调用父类的初始化方法
        super().__init__()
        
        if logger:
            self.set_logger(logger)
        
        # 初始化SQL预处理器
        self.preprocessor = SQLPreprocessor(logger)
        
        # 预处理SQL，移除XML标签
        self.sql_text, self.preprocess_info = self.preprocessor.preprocess_sql(
            sql_text, mode="normalize"
        )
        
        if self.preprocess_info['has_xml_tags']:
            self.logger.info(f"SQL包含XML标签，预处理后长度: {self.preprocess_info['processed_length']} (原始: {self.preprocess_info['original_length']})")
        
        # 初始化数据值获取器（如果需要）
        self.data_value_fetcher = None
        if config_manager:
            try:
                from .data_value_fetcher import DataValueFetcher
                self.data_value_fetcher = DataValueFetcher(config_manager, logger)
            except Exception as e:
                self.logger.warning(f"初始化数据值获取器失败: {str(e)}，将使用默认值替换")
        
        self.logger.debug(f"参数提取器初始化，原始SQL长度: {len(self.original_sql)}, 处理后SQL长度: {len(self.sql_text)}, 表元数据数量: {len(self.metadata_list)}")
    
    def extract_params(self) -> List[Dict[str, Any]]:
        """
        从SQL语句中提取参数
        
        Returns:
            参数信息列表
        """
        params = []
        
        try:
            # 查找参数模式：#{参数名}
            param_pattern = r'#\{([^}]+)\}'
            param_matches = re.findall(param_pattern, self.sql_text)
            
            for param_name in param_matches:
                param_info = {
                    'param': param_name,
                    'position': self.sql_text.find(f'#{{{param_name}}}')
                }
                params.append(param_info)
            
            # 改为debug级别，避免重复日志
            self.logger.debug(f"从SQL中提取到 {len(params)} 个参数: {[p['param'] for p in params]}")
            return params
            
        except Exception as e:
            self.logger.error(f"提取参数时发生错误: {str(e)}", exc_info=True)
            return []
    
    
    def _get_param_type_from_metadata(self, param_name: str) -> str:
        """
        从表元数据中获取参数类型
        
        Args:
            param_name: 参数名
            
        Returns:
            参数类型字符串，如果没有找到匹配则返回空字符串
        """
        if not self.metadata_list:
            return ""
        
        # 尝试在表元数据中查找匹配的字段
        for metadata in self.metadata_list:
            if not metadata.get('columns'):
                continue
                
            for column in metadata['columns']:
                column_name = column.get('name', '')
                if not column_name:
                    continue
                
                # 匹配参数名与字段名
                if self._param_matches_column(param_name, column_name):
                    return self._map_db_type_to_param_type(column.get('type', ''))
        
        return ""
    
    def _param_matches_column(self, param_name: str, column_name: str) -> bool:
        """
        检查参数名是否匹配字段名
        
        Args:
            param_name: 参数名
            column_name: 字段名
            
        Returns:
            是否匹配
        """
        # 1. 精确匹配
        if column_name == param_name:
            return True
        
        # 2. 忽略大小写匹配
        if column_name.lower() == param_name.lower():
            return True
        
        # 3. 忽略下划线匹配
        if column_name.replace('_', '').lower() == param_name.replace('_', '').lower():
            return True
        
        # 4. 包含关系
        param_lower = param_name.lower()
        column_lower = column_name.lower()
        if param_lower in column_lower or column_lower in param_lower:
            return True
        
        # 5. 更智能的模糊匹配：标准化后比较
        column_norm = self._normalize_name_for_matching(column_name)
        param_norm = self._normalize_name_for_matching(param_name)
        
        if column_norm == param_norm:
            return True
        
        # 6. 标准化后的包含关系
        if param_norm in column_norm or column_norm in param_norm:
            return True
        
        return False
    
    def _normalize_name_for_matching(self, name: str) -> str:
        """
        标准化名称以进行匹配
        
        Args:
            name: 要标准化的名称（参数名或列名）
            
        Returns:
            标准化后的名称
        """
        if not name:
            return ""
        
        # 转换为小写
        normalized = name.lower()
        
        # 移除常见的前缀（数据库列常见前缀）
        db_prefixes = [
            'eaf_', 'f_', 'fld_', 'col_', 'field_', 'column_', 
            't_', 'tb_', 'tab_', 'table_', 'v_', 'view_',
            'epi_', 'eci_', 'et_', 'prod_', 'order_', 'log_', 'user_'
        ]
        for prefix in db_prefixes:
            if normalized.startswith(prefix):
                normalized = normalized[len(prefix):]
        
        # 移除常见的后缀
        db_suffixes = [
            '_id', '_no', '_num', '_number', '_code', '_name', 
            '_value', '_type', '_status', '_flag', '_time',
            '_date', '_datetime', '_ts', '_key'
        ]
        for suffix in db_suffixes:
            if normalized.endswith(suffix):
                normalized = normalized[:-len(suffix)]
        
        # 移除下划线
        normalized = normalized.replace('_', '')
        
        return normalized
    
    def _map_db_type_to_param_type(self, db_type: str) -> str:
        """
        将数据库字段类型映射到参数类型
        
        Args:
            db_type: 数据库字段类型
            
        Returns:
            参数类型
        """
        if not db_type:
            return "string"
        
        db_type_lower = db_type.lower()
        
        # 时间类型
        time_types = ['date', 'time', 'datetime', 'timestamp']
        if any(time_type in db_type_lower for time_type in time_types):
            return 'datetime'
        
        # 数字类型
        number_types = ['int', 'integer', 'smallint', 'bigint', 'tinyint',
                        'decimal', 'numeric', 'float', 'double', 'real',
                        'money', 'currency']
        if any(number_type in db_type_lower for number_type in number_types):
            return 'number'
        
        # 布尔类型
        bool_types = ['bool', 'boolean', 'bit']
        if any(bool_type in db_type_lower for bool_type in bool_types):
            return 'boolean'
        
        # 默认字符串类型
        return 'string'
    
    def _parse_insert_column_mapping(self) -> Dict[str, str]:
        """
        解析INSERT语句中的列名和参数映射关系
        
        Returns:
            参数名到列名的映射字典
        """
        mapping = {}
        
        # 检查是否是INSERT语句
        if not self.sql_text.strip().upper().startswith('INSERT'):
            return mapping
        
        try:
            # 提取INSERT语句中的列名列表
            # 模式：INSERT INTO table_name (col1, col2, ...) VALUES (...)
            column_pattern = r'INSERT\s+INTO\s+\w+\s*\(([^)]+)\)'
            column_match = re.search(column_pattern, self.sql_text, re.IGNORECASE)
            
            if column_match:
                columns_str = column_match.group(1)
                columns = [col.strip() for col in columns_str.split(',')]
                
                # 提取参数位置信息
                params = self.extract_params()
                
                # 建立参数名到列名的映射（按位置对应）
                for i, param in enumerate(params):
                    if i < len(columns):
                        mapping[param['param']] = columns[i]
                    else:
                        # 如果没有足够的列，尝试使用模糊匹配
                        mapping[param['param']] = None
        
        except Exception as e:
            self.logger.debug(f"解析INSERT列名映射失败: {str(e)}")
        
        return mapping
    
    def _extract_column_from_context(self, param_name: str) -> Optional[str]:
        """
        从SQL上下文中提取参数对应的列名
        
        Args:
            param_name: 参数名
            
        Returns:
            列名，如果找不到则返回None
        """
        try:
            # 查找参数在SQL中的位置
            param_pattern = f'#{{{param_name}}}'
            param_pos = self.sql_text.find(param_pattern)
            if param_pos == -1:
                return None
            
            # 获取参数前的文本（最多向前500个字符）
            context_start = max(0, param_pos - 500)
            context_text = self.sql_text[context_start:param_pos]
            
            # 尝试匹配常见的列名模式
            # 模式1: column_name = #{param}
            # 模式2: column_name > #{param}
            # 模式3: column_name < #{param}
            # 模式4: column_name >= #{param}
            # 模式5: column_name <= #{param}
            # 模式6: column_name LIKE #{param}
            # 模式7: column_name IN (#{param})
            # 模式8: column_name IS #{param}
            
            # 反向查找最近的列名
            # 列名通常由字母、数字、下划线组成，可能包含点（数据库前缀）
            column_patterns = [
                r'([\w\.]+)\s*=\s*#\{' + re.escape(param_name) + r'\}',
                r'([\w\.]+)\s*>\s*#\{' + re.escape(param_name) + r'\}',
                r'([\w\.]+)\s*<\s*#\{' + re.escape(param_name) + r'\}',
                r'([\w\.]+)\s*>=\s*#\{' + re.escape(param_name) + r'\}',
                r'([\w\.]+)\s*<=\s*#\{' + re.escape(param_name) + r'\}',
                r'([\w\.]+)\s+LIKE\s*#\{' + re.escape(param_name) + r'\}',
                r'([\w\.]+)\s+IN\s*\(\s*#\{' + re.escape(param_name) + r'\}',
                r'([\w\.]+)\s+IS\s*#\{' + re.escape(param_name) + r'\}',
                r'([\w\.]+)\s+NOT\s+IN\s*\(\s*#\{' + re.escape(param_name) + r'\}',
                r'([\w\.]+)\s+NOT\s+LIKE\s*#\{' + re.escape(param_name) + r'\}',
            ]
            
            for pattern in column_patterns:
                match = re.search(pattern, self.sql_text, re.IGNORECASE)
                if match:
                    column_name = match.group(1)
                    # 如果包含数据库前缀，只取列名部分
                    if '.' in column_name:
                        column_name = column_name.split('.')[-1]
                    return column_name
            
            # 尝试从SET子句中提取（UPDATE语句）
            # 模式: SET column_name = #{param}
            set_pattern = r'SET\s+([^=]+)\s*=\s*#\{' + re.escape(param_name) + r'\}'
            set_match = re.search(set_pattern, self.sql_text, re.IGNORECASE)
            if set_match:
                column_name = set_match.group(1).strip()
                # 移除可能的表别名前缀
                if '.' in column_name:
                    column_name = column_name.split('.')[-1]
                return column_name
            
            # 尝试从WHERE子句中更复杂的模式
            # 查找参数前的列名（反向扫描）
            # 从参数位置向前查找，找到最近的标识符
            before_text = self.sql_text[:param_pos]
            
            # 反向查找列名（字母数字下划线组成的标识符）
            # 使用正则表达式查找参数前的列名
            column_candidate_pattern = r'([a-zA-Z_][a-zA-Z0-9_\.]*)\s*[=<>!~]+\s*#\{' + re.escape(param_name) + r'\}'
            candidate_match = re.search(column_candidate_pattern, before_text, re.IGNORECASE)
            if candidate_match:
                column_name = candidate_match.group(1)
                if '.' in column_name:
                    column_name = column_name.split('.')[-1]
                return column_name
            
            return None
            
        except Exception as e:
            self.logger.debug(f"从上下文提取列名失败 {param_name}: {str(e)}")
            return None
    
    def _camel_to_snake(self, name: str) -> str:
        """
        将驼峰命名转换为蛇形命名
        
        Args:
            name: 驼峰命名的字符串
            
        Returns:
            蛇形命名的字符串
        """
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
    
    def _get_column_name_for_param(self, param_name: str) -> Optional[str]:
        """
        根据参数名获取对应的列名
        
        Args:
            param_name: 参数名
            
        Returns:
            列名，如果找不到则返回None
        """
        # 1. 首先尝试从INSERT语句映射中获取
        mapping = self._parse_insert_column_mapping()
        if param_name in mapping and mapping[param_name]:
            return mapping[param_name]
        
        # 2. 尝试从SQL上下文中提取列名
        column_from_context = self._extract_column_from_context(param_name)
        if column_from_context:
            return column_from_context
        
        # 3. 如果没有找到，尝试根据常见的命名规则推断
        # 例如：flowNo -> FLOWNO, EAF_FLOWNO 等
        param_upper = param_name.upper()
        
        # 常见的命名转换模式
        patterns = []
        
        # 如果有元数据，尝试根据表名前缀生成模式
        if self.metadata_list:
            for metadata in self.metadata_list:
                table_name = metadata.get('table_name', '').upper()
                # 提取表名前缀（如果表名有特定模式）
                if table_name.startswith('ES_'):
                    # ES_ACCOUNTCANCEL_FLOW -> EAF_
                    parts = table_name.split('_')
                    if len(parts) >= 2:
                        # 取每个部分的首字母
                        prefix = ''.join([p[0] for p in parts if p]) + '_'
                        patterns.append(f'{prefix}{param_upper}')
                elif table_name.endswith('_INFO'):
                    # PARTY_INFO -> PI_
                    base_name = table_name.replace('_INFO', '')
                    if '_' in base_name:
                        parts = base_name.split('_')
                        prefix = ''.join([p[0] for p in parts if p]) + '_'
                        patterns.append(f'{prefix}{param_upper}')
                    else:
                        patterns.append(f'{base_name[0:2]}_{param_upper}')
        
        # 添加通用模式
        patterns.extend([
            param_upper,  # flowNo -> FLOWNO
            f'EAF_{param_upper}',  # flowNo -> EAF_FLOWNO
            f'EPI_{param_upper}',  # partyNo -> EPI_PARTYNO
            f'ECI_{param_upper}',  # cardNo -> ECI_CARDNO
            param_name,  # 原样
            param_name.replace('No', 'NO').replace('No', 'NO'),  # 转换No为NO
            self._camel_to_snake(param_name).upper(),  # flowNo -> FLOW_NO
        ])
        
        # 去重
        patterns = list(dict.fromkeys(patterns))
        
        # 如果有元数据，检查这些模式是否匹配任何列
        if self.metadata_list:
            for metadata in self.metadata_list:
                columns = metadata.get('columns', [])
                for column in columns:
                    column_name = column.get('name', '')
                    column_name_upper = column_name.upper()
                    
                    for pattern in patterns:
                        pattern_upper = pattern.upper() if isinstance(pattern, str) else pattern
                        if pattern_upper == column_name_upper:
                            return column_name
        
        # 4. 如果还没有找到，尝试模糊匹配
        if self.metadata_list:
            for metadata in self.metadata_list:
                columns = metadata.get('columns', [])
                for column in columns:
                    column_name = column.get('name', '')
                    if self._param_matches_column(param_name, column_name):
                        return column_name
        
        return None
    
    def _get_replacement_value_from_db(self, param_name: str, tables: List[str], 
                                       db_alias: Optional[str] = None) -> Optional[str]:
        """
        从数据表中获取随机实际值来替换参数
        
        Args:
            param_name: 参数名
            tables: 表名列表
            db_alias: 数据库别名
            
        Returns:
            替换的值字符串，如果无法获取则返回None
        """
        # 如果没有数据值获取器，直接返回None
        if not self.data_value_fetcher:
            self.logger.debug(f"数据值获取器未启用，无法从数据库获取值: {param_name}")
            return None
        
        # 如果没有表信息，无法从数据库获取值
        if not tables:
            self.logger.debug(f"没有表信息，无法从数据库获取值: {param_name}")
            return None
        
        # 如果没有数据库别名，尝试获取一个默认的
        if not db_alias and self.config_manager:
            # 尝试获取默认数据库别名
            try:
                target_dbs = self.config_manager.get_all_target_db_aliases()
                if target_dbs:
                    db_alias = target_dbs[0]
            except:
                pass
        
        if not db_alias:
            self.logger.debug(f"没有数据库别名，无法从数据库获取值: {param_name}")
            return None
        
        try:
            # 首先尝试根据参数名获取对应的列名
            column_name = self._get_column_name_for_param(param_name)
            
            # 如果有找到对应的列名，优先使用列名
            if column_name:
                self.logger.debug(f"为参数 {param_name} 找到列名: {column_name}")
                # 使用列名查找匹配的列信息
                for table_name in tables:
                    if not self.metadata_list:
                        continue
                    
                    # 在元数据中查找匹配的列
                    for metadata in self.metadata_list:
                        if metadata.get('table_name') == table_name:
                            columns = metadata.get('columns', [])
                            for column in columns:
                                if column.get('name', '').lower() == column_name.lower():
                                    column_type = column.get('type', '')
                                    # 从数据库获取替换值
                                    replacement_value = self.data_value_fetcher.get_replacement_value(
                                        db_alias, table_name, column_name, column_type
                                    )
                                    
                                    if replacement_value is not None:
                                        # 根据列类型判断是否需要加引号
                                        if isinstance(replacement_value, str):
                                            # 检查是否已经加了引号
                                            if not (replacement_value.startswith("'") and replacement_value.endswith("'")):
                                                # 对于字符串和时间类型，需要加引号
                                                column_type_lower = column_type.lower()
                                                if ('char' in column_type_lower or 'text' in column_type_lower or 
                                                    'varchar' in column_type_lower or 'string' in column_type_lower or
                                                    'date' in column_type_lower or 'time' in column_type_lower or
                                                    'datetime' in column_type_lower or 'timestamp' in column_type_lower):
                                                    return f"'{replacement_value}'"
                                                else:
                                                    return str(replacement_value)
                                            else:
                                                return replacement_value
                                        else:
                                            # 非字符串类型直接转换为字符串
                                            return str(replacement_value)
            
            # 如果没有通过列名映射找到，则尝试原有的模糊匹配逻辑
            for table_name in tables:
                if not self.metadata_list:
                    continue
                
                # 查找匹配的列
                result = self.data_value_fetcher.find_matching_column(
                    db_alias, table_name, param_name, self.metadata_list
                )
                
                if result:
                    matched_table_name, matched_column_name, column_info = result
                    column_type = column_info.get('type', '')
                    
                    # 从数据库获取替换值（不再传递param_type参数）
                    replacement_value = self.data_value_fetcher.get_replacement_value(
                        db_alias, matched_table_name, matched_column_name, column_type
                    )
                    
                    if replacement_value is not None:
                        # 根据列类型判断是否需要加引号
                        if isinstance(replacement_value, str):
                            # 检查是否已经加了引号
                            if not (replacement_value.startswith("'") and replacement_value.endswith("'")):
                                # 对于字符串和时间类型，需要加引号
                                column_type_lower = column_type.lower()
                                if ('char' in column_type_lower or 'text' in column_type_lower or 
                                    'varchar' in column_type_lower or 'string' in column_type_lower or
                                    'date' in column_type_lower or 'time' in column_type_lower or
                                    'datetime' in column_type_lower or 'timestamp' in column_type_lower):
                                    return f"'{replacement_value}'"
                                else:
                                    return str(replacement_value)
                            else:
                                return replacement_value
                        else:
                            # 非字符串类型直接转换为字符串
                            return str(replacement_value)
            
            # 如果没有找到匹配的列，尝试使用第一个表
            if tables and self.metadata_list:
                first_table = tables[0]
                # 查找第一个表的元数据
                for metadata in self.metadata_list:
                    if metadata.get('table_name') == first_table:
                        columns = metadata.get('columns', [])
                        if columns:
                            # 使用第一个列作为参考
                            first_column = columns[0]
                            column_name = first_column.get('name', '')
                            column_type = first_column.get('type', '')
                            
                            # 尝试获取该列的值
                            replacement_value = self.data_value_fetcher.get_replacement_value(
                                db_alias, first_table, column_name, column_type
                            )
                            
                            if replacement_value is not None:
                                if isinstance(replacement_value, str):
                                    if not (replacement_value.startswith("'") and replacement_value.endswith("'")):
                                        column_type_lower = column_type.lower()
                                        if ('char' in column_type_lower or 'text' in column_type_lower or 
                                            'varchar' in column_type_lower or 'string' in column_type_lower or
                                            'date' in column_type_lower or 'time' in column_type_lower or
                                            'datetime' in column_type_lower or 'timestamp' in column_type_lower):
                                            return f"'{replacement_value}'"
                                        else:
                                            return str(replacement_value)
                                    else:
                                        return replacement_value
                                else:
                                    return str(replacement_value)
                            break
            
            self.logger.debug(f"无法从数据库获取参数 {param_name} 的值")
            return None
            
        except Exception as e:
            self.logger.warning(f"从数据库获取参数值 {param_name} 失败: {str(e)}")
            return None
    
    def _get_preset_value(self, param_type: str) -> str:
        """
        获取预设的值（当无法从数据库获取时）
        
        Args:
            param_type: 参数类型
            
        Returns:
            预设值字符串
        """
        raise ValueError("不允许使用预设值，必须使用实际的表字段值进行参数替换")
    
    def generate_replaced_sql(self) -> tuple:
        """
        生成替换参数后的SQL
        
        Returns:
            (替换后的SQL, 表名列表)
        """
        try:
            # 提取参数
            params = self.extract_params()
            
            # 如果没有参数需要替换，直接返回原始SQL
            if not params:
                self.logger.info("SQL中没有需要替换的参数")
                return self.sql_text, []
            
            # 有参数需要替换时，必须检查配置管理器和数据值获取器
            if not self.config_manager:
                raise ValueError("必须提供config_manager才能进行参数替换，因为需要使用实际的表字段值")
            
            # 检查数据值获取器是否初始化成功
            if not self.data_value_fetcher:
                raise ValueError("数据值获取器初始化失败，无法从数据库获取实际值")
            
            # 替换参数为随机值
            replaced_sql = self.sql_text
            tables = set()
            
            # 提取表名 - 改进版本，支持带数据库前缀的表名
            table_patterns = [
                r'\bFROM\s+([\w\.]+)',  # FROM 表名
                r'\bJOIN\s+([\w\.]+)',   # JOIN 表名
                r'\bINSERT\s+INTO\s+([\w\.]+)',  # INSERT INTO 表名
                r'\bUPDATE\s+([\w\.]+)',  # UPDATE 表名
                r'\bDELETE\s+FROM\s+([\w\.]+)',  # DELETE FROM 表名
            ]
            
            for pattern in table_patterns:
                matches = re.findall(pattern, self.sql_text, re.IGNORECASE)
                for table_name in matches:
                    if table_name:
                        # 如果表名包含数据库前缀，只取表名部分
                        if '.' in table_name:
                            table_name = table_name.split('.')[-1]
                        tables.add(table_name)
            
            # 尝试获取数据库别名（用于数据值获取）
            db_alias = None
            if self.config_manager:
                # 尝试获取默认数据库别名
                try:
                    target_dbs = self.config_manager.get_all_target_db_aliases()
                    if target_dbs:
                        db_alias = target_dbs[0]
                        self.logger.debug(f"使用数据库别名: {db_alias}")
                except Exception as e:
                    self.logger.warning(f"获取数据库别名失败: {str(e)}")
            
            # 记录无法获取值的参数
            failed_params = []
            
            # 替换参数 - 只使用数据表中获取的实际值
            for param_info in params:
                param_name = param_info['param']
                
                # 从数据表获取随机实际值（不再使用参数类型）
                replaced_value = self._get_replacement_value_from_db(param_name, list(tables), db_alias)
                
                # 如果无法从数据库获取值，记录失败
                if replaced_value is None:
                    failed_params.append(param_name)
                    raise ValueError(f"无法从数据库获取参数 '{param_name}' 的实际值，请确保数据库中有对应的表字段数据")
                
                # 更精确的替换，避免错误匹配
                param_pattern = f"#{{{param_name}}}"
                replaced_sql = re.sub(re.escape(param_pattern), replaced_value, replaced_sql)
            
            # 检查是否所有参数都已成功替换
            param_pattern = r'#\{([^}]+)\}'
            remaining_params = re.findall(param_pattern, replaced_sql)
            if remaining_params:
                raise ValueError(f"仍有未替换的参数: {remaining_params}")
            
            self.logger.info(f"生成替换参数后的SQL，成功替换了 {len(params)} 个参数")
            self.logger.debug(f"替换后的SQL（前200字符）: {replaced_sql[:200]}...")
            
            return replaced_sql, list(tables)
            
        except Exception as e:
            self.logger.error(f"生成替换参数后的SQL时发生错误: {str(e)}")
            raise  # 重新抛出异常，让调用者处理


def test_param_extractor():
    """测试参数提取器"""
    test_sqls = [
        "SELECT * FROM users WHERE id = #{id} AND name = #{name}",
        "UPDATE products SET price = #{price} WHERE category = #{category}",
        "INSERT INTO orders (user_id, amount, order_time) VALUES (#{user_id}, #{amount}, #{order_time})",
        "DELETE FROM logs WHERE batch_time = #{batch_time} AND start = #{start} AND end = #{end}"
    ]
    
    for i, sql in enumerate(test_sqls, 1):
        print(f"\n测试SQL {i}:")
        print(f"原始SQL: {sql}")
        
        extractor = ParamExtractor(sql)
        replaced_sql, tables = extractor.generate_replaced_sql()
        
        print(f"替换后SQL: {replaced_sql}")
        print(f"提取的表名: {tables}")


if __name__ == '__main__':
    test_param_extractor()
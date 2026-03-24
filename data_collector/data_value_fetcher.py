#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据值获取器模块
负责从数据库中获取真实数据值，用于替换SQL参数
"""

import re
import random
import logging
from typing import Dict, Any, List, Optional, Tuple, Set
from utils.logger import LogMixin
from utils.db_connector_pymysql import DatabaseManager


class DataValueFetcher(LogMixin):
    """数据值获取器，从数据库中获取真实数据替换参数"""
    
    def __init__(self, config_manager, logger=None):
        """
        初始化数据值获取器
        
        Args:
            config_manager: 配置管理器
            logger: 日志记录器
        """
        self.config_manager = config_manager
        
        if logger:
            self.set_logger(logger)
        
        # 初始化数据库连接管理器（但不立即连接）
        self.db_managers = {}  # db_alias -> DatabaseManager
        self.value_cache = {}  # 缓存已获取的数据值
        self.sample_cache = {}  # 缓存表的数据采样
        
        # 获取配置
        self.optimization_config = config_manager.get_optimization_config()
        self.enable_data_fetching = self.optimization_config.get('enable_data_fetching', True)
        self.max_sample_size = int(self.optimization_config.get('max_sample_size', 100))
        self.use_cache = self.optimization_config.get('use_cache', True)
        
        self.logger.info("数据值获取器初始化完成")
    
    def get_db_manager(self, db_alias: str) -> Optional[DatabaseManager]:
        """
        获取数据库连接管理器
        
        Args:
            db_alias: 数据库别名
            
        Returns:
            数据库连接管理器，如果失败则返回None
        """
        if db_alias in self.db_managers:
            return self.db_managers[db_alias]
        
        try:
            # 从配置中获取数据库连接信息
            db_config = self.config_manager.get_target_database_config(db_alias)
            if not db_config:
                self.logger.warning(f"未找到数据库 {db_alias} 的配置")
                return None
            
            db_manager = DatabaseManager(db_config)
            self.db_managers[db_alias] = db_manager
            return db_manager
            
        except Exception as e:
            self.logger.error(f"创建数据库连接管理器失败: {str(e)}")
            return None
    
    def fetch_column_values(self, db_alias: str, table_name: str, column_name: str, 
                           column_type: str) -> Dict[str, Any]:
        """
        获取表中某列的数据值
        
        Args:
            db_alias: 数据库别名
            table_name: 表名
            column_name: 列名
            column_type: 列类型
            
        Returns:
            包含各种数据值信息的字典
        """
        cache_key = f"{db_alias}.{table_name}.{column_name}"
        
        # 检查缓存
        if self.use_cache and cache_key in self.value_cache:
            self.logger.debug(f"从缓存获取列值: {cache_key}")
            return self.value_cache[cache_key]
        
        if not self.enable_data_fetching:
            self.logger.debug(f"数据获取已禁用，返回空值: {cache_key}")
            return {}
        
        db_manager = self.get_db_manager(db_alias)
        if not db_manager:
            self.logger.warning(f"无法获取数据库连接: {db_alias}")
            return {}
        
        try:
            result = {}
            column_type_lower = column_type.lower()
            
            # 根据列类型获取不同的数据值
            if 'int' in column_type_lower or 'decimal' in column_type_lower or \
               'float' in column_type_lower or 'double' in column_type_lower or \
               'number' in column_type_lower or 'numeric' in column_type_lower:
                # 数值类型：获取最小值、最大值、常见值
                result.update(self._fetch_numeric_values(db_manager, table_name, column_name))
                
            elif 'date' in column_type_lower or 'time' in column_type_lower or 'timestamp' in column_type_lower:
                # 时间类型：获取最早、最晚时间
                result.update(self._fetch_datetime_values(db_manager, table_name, column_name))
                
            elif 'char' in column_type_lower or 'varchar' in column_type_lower or \
                 'text' in column_type_lower or 'string' in column_type_lower:
                # 字符串类型：获取枚举值或常见值
                result.update(self._fetch_string_values(db_manager, table_name, column_name))
                
            elif 'bool' in column_type_lower or 'bit' in column_type_lower:
                # 布尔类型：获取可能的布尔值
                result.update(self._fetch_boolean_values(db_manager, table_name, column_name))
                
            else:
                # 其他类型：尝试获取样本值
                result.update(self._fetch_sample_values(db_manager, table_name, column_name))
            
            # 缓存结果
            if self.use_cache:
                self.value_cache[cache_key] = result
                
            self.logger.debug(f"获取列值成功: {cache_key}, 结果: {len(result)} 项")
            return result
            
        except Exception as e:
            self.logger.error(f"获取列值失败 {cache_key}: {str(e)}")
            return {}
    
    def _fetch_numeric_values(self, db_manager: DatabaseManager, table_name: str, 
                             column_name: str) -> Dict[str, Any]:
        """获取数值类型的数据值"""
        result = {}
        
        try:
            # 获取最小值
            min_query = f"SELECT MIN({column_name}) as min_val FROM {table_name}"
            min_result = db_manager.fetch_one(min_query)
            if min_result and min_result.get('min_val') is not None:
                result['min'] = min_result['min_val']
            
            # 获取最大值
            max_query = f"SELECT MAX({column_name}) as max_val FROM {table_name}"
            max_result = db_manager.fetch_one(max_query)
            if max_result and max_result.get('max_val') is not None:
                result['max'] = max_result['max_val']
            
            # 获取常见值（出现频率最高的值）
            common_query = f"""
                SELECT {column_name}, COUNT(*) as freq 
                FROM {table_name} 
                WHERE {column_name} IS NOT NULL 
                GROUP BY {column_name} 
                ORDER BY freq DESC 
                LIMIT 5
            """
            common_results = db_manager.fetch_all(common_query)
            if common_results:
                result['common_values'] = [row[column_name] for row in common_results[:3]]
            
            # 获取平均值（如果适用）
            avg_query = f"SELECT AVG({column_name}) as avg_val FROM {table_name}"
            avg_result = db_manager.fetch_one(avg_query)
            if avg_result and avg_result.get('avg_val') is not None:
                result['avg'] = avg_result['avg_val']
            
            # 获取中位数近似值
            median_query = f"""
                SELECT {column_name} 
                FROM {table_name} 
                WHERE {column_name} IS NOT NULL 
                ORDER BY {column_name} 
                LIMIT 1 OFFSET (
                    SELECT COUNT(*) FROM {table_name} WHERE {column_name} IS NOT NULL
                ) / 2
            """
            median_result = db_manager.fetch_one(median_query)
            if median_result and median_result.get(column_name) is not None:
                result['median'] = median_result[column_name]
                
        except Exception as e:
            self.logger.warning(f"获取数值类型数据失败 {table_name}.{column_name}: {str(e)}")
        
        return result
    
    def _fetch_datetime_values(self, db_manager: DatabaseManager, table_name: str, 
                              column_name: str) -> Dict[str, Any]:
        """获取时间类型的数据值"""
        result = {}
        
        try:
            # 获取最早时间
            min_query = f"SELECT MIN({column_name}) as min_val FROM {table_name}"
            min_result = db_manager.fetch_one(min_query)
            if min_result and min_result.get('min_val') is not None:
                result['min'] = min_result['min_val']
            
            # 获取最晚时间
            max_query = f"SELECT MAX({column_name}) as max_val FROM {table_name}"
            max_result = db_manager.fetch_one(max_query)
            if max_result and max_result.get('max_val') is not None:
                result['max'] = max_result['max_val']
            
            # 获取常见日期值
            common_query = f"""
                SELECT DATE({column_name}) as date_val, COUNT(*) as freq 
                FROM {table_name} 
                WHERE {column_name} IS NOT NULL 
                GROUP BY DATE({column_name}) 
                ORDER BY freq DESC 
                LIMIT 5
            """
            common_results = db_manager.fetch_all(common_query)
            if common_results:
                result['common_dates'] = [row['date_val'] for row in common_results[:3]]
            
            # 获取最近的时间值
            recent_query = f"""
                SELECT {column_name} 
                FROM {table_name} 
                WHERE {column_name} IS NOT NULL 
                ORDER BY {column_name} DESC 
                LIMIT 3
            """
            recent_results = db_manager.fetch_all(recent_query)
            if recent_results:
                result['recent_values'] = [row[column_name] for row in recent_results]
                
        except Exception as e:
            self.logger.warning(f"获取时间类型数据失败 {table_name}.{column_name}: {str(e)}")
        
        return result
    
    def _fetch_string_values(self, db_manager: DatabaseManager, table_name: str, 
                            column_name: str) -> Dict[str, Any]:
        """获取字符串类型的数据值"""
        result = {}
        
        try:
            # 获取不同的值（枚举值）
            distinct_query = f"""
                SELECT DISTINCT {column_name} 
                FROM {table_name} 
                WHERE {column_name} IS NOT NULL AND LENGTH({column_name}) > 0 
                ORDER BY {column_name} 
                LIMIT {self.max_sample_size}
            """
            distinct_results = db_manager.fetch_all(distinct_query)
            if distinct_results:
                values = [row[column_name] for row in distinct_results]
                result['distinct_values'] = values
                
                # 如果值数量较少，认为是枚举类型
                if len(values) <= 10:
                    result['is_enum'] = True
                    result['enum_values'] = values
                else:
                    result['is_enum'] = False
            
            # 获取常见值（出现频率最高的值）
            common_query = f"""
                SELECT {column_name}, COUNT(*) as freq 
                FROM {table_name} 
                WHERE {column_name} IS NOT NULL 
                GROUP BY {column_name} 
                ORDER BY freq DESC 
                LIMIT 10
            """
            common_results = db_manager.fetch_all(common_query)
            if common_results:
                result['common_values'] = [row[column_name] for row in common_results[:5]]
            
            # 获取平均长度
            length_query = f"""
                SELECT AVG(LENGTH({column_name})) as avg_len, 
                       MIN(LENGTH({column_name})) as min_len,
                       MAX(LENGTH({column_name})) as max_len
                FROM {table_name} 
                WHERE {column_name} IS NOT NULL
            """
            length_result = db_manager.fetch_one(length_query)
            if length_result:
                if length_result.get('avg_len') is not None:
                    result['avg_length'] = int(length_result['avg_len'])
                if length_result.get('min_len') is not None:
                    result['min_length'] = length_result['min_len']
                if length_result.get('max_len') is not None:
                    result['max_length'] = length_result['max_len']
                    
        except Exception as e:
            self.logger.warning(f"获取字符串类型数据失败 {table_name}.{column_name}: {str(e)}")
        
        return result
    
    def _fetch_boolean_values(self, db_manager: DatabaseManager, table_name: str, 
                             column_name: str) -> Dict[str, Any]:
        """获取布尔类型的数据值"""
        result = {}
        
        try:
            # 获取分布情况
            distribution_query = f"""
                SELECT {column_name}, COUNT(*) as count 
                FROM {table_name} 
                WHERE {column_name} IS NOT NULL 
                GROUP BY {column_name} 
                ORDER BY {column_name}
            """
            distribution_results = db_manager.fetch_all(distribution_query)
            
            if distribution_results:
                values = {}
                total = 0
                for row in distribution_results:
                    value = row[column_name]
                    count = row['count']
                    values[value] = count
                    total += count
                
                result['distribution'] = values
                
                # 计算比例
                if total > 0:
                    for value, count in values.items():
                        result[f'ratio_{value}'] = count / total
                        
                # 获取最常见的值
                most_common = max(values.items(), key=lambda x: x[1])[0] if values else None
                if most_common is not None:
                    result['most_common'] = most_common
                    
        except Exception as e:
            self.logger.warning(f"获取布尔类型数据失败 {table_name}.{column_name}: {str(e)}")
        
        return result
    
    def _fetch_sample_values(self, db_manager: DatabaseManager, table_name: str, 
                            column_name: str) -> Dict[str, Any]:
        """获取其他类型的数据样本"""
        result = {}
        
        try:
            # 获取样本值 - 获取20个随机样本
            sample_size = 20
            sample_query = f"""
                SELECT {column_name} 
                FROM {table_name} 
                WHERE {column_name} IS NOT NULL 
                ORDER BY RAND() 
                LIMIT {sample_size}
            """
            sample_results = db_manager.fetch_all(sample_query)
            if sample_results:
                values = [row[column_name] for row in sample_results]
                result['sample_values'] = values
                
                # 分析值的类型
                if values:
                    # 检查是否是数值
                    try:
                        numeric_values = [float(v) for v in values if v is not None]
                        if len(numeric_values) == len(values):
                            result['is_numeric'] = True
                            result['min'] = min(numeric_values)
                            result['max'] = max(numeric_values)
                    except:
                        pass
                        
        except Exception as e:
            self.logger.warning(f"获取样本数据失败 {table_name}.{column_name}: {str(e)}")
        
        return result
    
    def get_replacement_value(self, db_alias: str, table_name: str, column_name: str, 
                             column_type: str) -> Any:
        """
        获取用于替换参数的合适值
        
        Args:
            db_alias: 数据库别名
            table_name: 表名
            column_name: 列名
            column_type: 列类型
            
        Returns:
            用于替换的值
        """
        # 如果没有启用数据获取，返回默认值
        if not self.enable_data_fetching:
            return self._get_default_value(column_type)
        
        # 获取列的值信息
        column_values = self.fetch_column_values(db_alias, table_name, column_name, column_type)
        
        # 根据列类型选择合适的值
        column_type_lower = column_type.lower()
        
        if 'int' in column_type_lower or 'decimal' in column_type_lower or \
           'float' in column_type_lower or 'double' in column_type_lower or \
           'number' in column_type_lower or 'numeric' in column_type_lower:
            # 数值类型
            if 'common_values' in column_values and column_values['common_values']:
                return random.choice(column_values['common_values'])
            elif 'min' in column_values and 'max' in column_values:
                # 在最小值和最大值之间选择一个值
                min_val = column_values['min']
                max_val = column_values['max']
                if isinstance(min_val, (int, float)) and isinstance(max_val, (int, float)):
                    if min_val == max_val:
                        return min_val
                    # 选择偏向常见值的点（偏向较低的值，因为通常小值更常见）
                    return int(min_val + (max_val - min_val) * 0.3)
            elif 'avg' in column_values:
                return int(column_values['avg']) if isinstance(column_values['avg'], float) else column_values['avg']
            else:
                return 123  # 默认值
        
        elif 'date' in column_type_lower or 'time' in column_type_lower or 'timestamp' in column_type_lower:
            # 时间类型
            if 'common_dates' in column_values and column_values['common_dates']:
                date_str = str(random.choice(column_values['common_dates']))
                # 确保返回的是字符串格式
                return f"'{date_str}'"
            elif 'recent_values' in column_values and column_values['recent_values']:
                date_str = str(random.choice(column_values['recent_values']))
                return f"'{date_str}'"
            elif 'min' in column_values:
                date_str = str(column_values['min'])
                return f"'{date_str}'"
            else:
                return "'2025-01-01 00:00:00'"  # 默认值
        
        elif 'char' in column_type_lower or 'varchar' in column_type_lower or \
             'text' in column_type_lower or 'string' in column_type_lower:
            # 字符串类型
            if 'common_values' in column_values and column_values['common_values']:
                value = random.choice(column_values['common_values'])
                return f"'{value}'"
            elif 'distinct_values' in column_values and column_values['distinct_values']:
                value = random.choice(column_values['distinct_values'])
                return f"'{value}'"
            else:
                return "'test_value'"  # 默认值
        
        elif 'bool' in column_type_lower or 'bit' in column_type_lower:
            # 布尔类型
            if 'most_common' in column_values:
                return 1 if column_values['most_common'] else 0
            else:
                return 1  # 默认值
        
        else:
            # 其他类型
            if 'sample_values' in column_values and column_values['sample_values']:
                value = random.choice(column_values['sample_values'])
                # 如果是数值，直接返回；否则加引号
                if isinstance(value, (int, float)):
                    return value
                else:
                    return f"'{value}'"
            else:
                return self._get_default_value(column_type)
    
    def _get_default_value(self, column_type: str) -> Any:
        """
        获取默认值（当无法从数据库获取时）
        
        Args:
            column_type: 列类型
            
        Returns:
            默认值
        """
        # 根据列类型判断
        column_type_lower = column_type.lower()
        
        if 'int' in column_type_lower or 'decimal' in column_type_lower or \
           'float' in column_type_lower or 'double' in column_type_lower or \
           'number' in column_type_lower or 'numeric' in column_type_lower:
            return 123
        elif 'date' in column_type_lower or 'time' in column_type_lower or 'timestamp' in column_type_lower:
            return "'2025-01-01 00:00:00'"
        elif 'bool' in column_type_lower or 'bit' in column_type_lower:
            return 1
        else:
            return "'test_value'"
    
    def find_matching_column(self, db_alias: str, table_name: str, param_name: str, 
                            metadata_list: List[Dict[str, Any]]) -> Optional[Tuple[str, str, Dict[str, Any]]]:
        """
        在表元数据中查找匹配参数的列
        
        Args:
            db_alias: 数据库别名
            table_name: 表名
            param_name: 参数名
            metadata_list: 表元数据列表
            
        Returns:
            (表名, 列名, 列信息) 或 None
        """
        # 首先查找指定表名的表
        target_table = None
        for metadata in metadata_list:
            if metadata.get('table_name') == table_name:
                target_table = metadata
                break
        
        if not target_table:
            # 如果没有找到指定表名的表，使用第一个表
            if metadata_list:
                target_table = metadata_list[0]
                table_name = target_table.get('table_name', '')
            else:
                return None
        
        # 在表的列中查找匹配的列
        columns = target_table.get('columns', [])
        param_lower = param_name.lower()
        
        # 尝试精确匹配
        for column in columns:
            column_name = column.get('name', '')
            if column_name.lower() == param_lower:
                return table_name, column_name, column
        
        # 尝试包含匹配
        for column in columns:
            column_name = column.get('name', '')
            column_lower = column_name.lower()
            
            # 检查参数名是否包含列名或列名是否包含参数名
            if param_lower in column_lower or column_lower in param_lower:
                return table_name, column_name, column
            
            # 移除常见后缀后再匹配
            param_without_suffix = self._remove_common_suffixes(param_lower)
            column_without_suffix = self._remove_common_suffixes(column_lower)
            
            if param_without_suffix and column_without_suffix:
                if param_without_suffix == column_without_suffix:
                    return table_name, column_name, column
                elif param_without_suffix in column_without_suffix or column_without_suffix in param_without_suffix:
                    return table_name, column_name, column
        
        # 尝试模糊匹配
        for column in columns:
            column_name = column.get('name', '')
            # 如果参数名看起来像是列名的缩写或变体
            if self._is_likely_match(param_lower, column_name.lower()):
                return table_name, column_name, column
        
        return None
    
    def _remove_common_suffixes(self, text: str) -> str:
        """移除常见的后缀"""
        if not text:
            return ""
        suffixes = ['_id', '_no', '_num', '_code', '_name', '_value', '_type', '_status']
        for suffix in suffixes:
            if text.endswith(suffix):
                return text[:-len(suffix)]
        return text
    
    def _is_likely_match(self, param_name: str, column_name: str) -> bool:
        """检查参数名和列名是否可能匹配"""
        # 简单的启发式匹配
        if not param_name or not column_name:
            return False
        
        # 检查共享的单词
        param_words = set(re.findall(r'[a-z]+', param_name))
        column_words = set(re.findall(r'[a-z]+', column_name))
        
        if param_words.intersection(column_words):
            return True
        
        # 检查缩写匹配
        param_initials = ''.join([w[0] for w in param_name.split('_') if w])
        column_initials = ''.join([w[0] for w in column_name.split('_') if w])
        
        if param_initials and column_initials and param_initials in column_initials:
            return True
        
        return False
    
    def clear_cache(self):
        """清空缓存"""
        self.value_cache.clear()
        self.sample_cache.clear()
        self.logger.info("数据值缓存已清空")


# 测试函数
def test_data_value_fetcher():
    """测试数据值获取器"""
    # 注意：这个测试需要实际的数据库连接，所以这里只展示结构
    print("DataValueFetcher 模块加载成功")
    print("功能：")
    print("1. 从数据库中获取真实数据值")
    print("2. 支持数值、字符串、时间、布尔等类型")
    print("3. 支持缓存机制")
    print("4. 智能选择替换值")


if __name__ == '__main__':
    test_data_value_fetcher()
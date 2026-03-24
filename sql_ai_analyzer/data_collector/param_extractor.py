#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
参数提取器模块
负责从SQL语句中提取参数并生成替换参数后的SQL
"""

import re
from typing import List, Dict, Any
from utils.logger import LogMixin


class ParamExtractor(LogMixin):
    """参数提取器"""
    
    def __init__(self, sql_text: str, logger=None):
        """
        初始化参数提取器
        
        Args:
            sql_text: SQL语句文本
            logger: 日志记录器
        """
        self.sql_text = sql_text
        
        # 调用父类的初始化方法
        super().__init__()
        
        if logger:
            self.set_logger(logger)
        
        self.logger.debug(f"参数提取器初始化，SQL长度: {len(sql_text)}")
    
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
                    'type': self._guess_param_type(param_name),
                    'position': self.sql_text.find(f'#{{{param_name}}}')
                }
                params.append(param_info)
            
            self.logger.info(f"从SQL中提取到 {len(params)} 个参数: {[p['param'] for p in params]}")
            return params
            
        except Exception as e:
            self.logger.error(f"提取参数时发生错误: {str(e)}", exc_info=True)
            return []
    
    def _guess_param_type(self, param_name: str) -> str:
        """
        根据参数名猜测参数类型
        
        Args:
            param_name: 参数名
            
        Returns:
            参数类型
        """
        param_lower = param_name.lower()
        
        # 时间相关参数
        time_keywords = ['time', 'date', 'datetime', 'timestamp', 'batch_time', 'start_time', 'end_time']
        if any(keyword in param_lower for keyword in time_keywords):
            return 'datetime'
        
        # 数字相关参数
        num_keywords = ['id', 'num', 'count', 'amount', 'quantity', 'size', 'start', 'end', 'page', 'limit', 'offset']
        if any(keyword in param_lower for keyword in num_keywords):
            return 'number'
        
        # 字符串相关参数
        str_keywords = ['name', 'title', 'desc', 'description', 'content', 'text', 'value', 'code', 'status']
        if any(keyword in param_lower for keyword in str_keywords):
            return 'string'
        
        # 默认返回字符串类型
        return 'string'
    
    def generate_replaced_sql(self) -> tuple:
        """
        生成替换参数后的SQL
        
        Returns:
            (替换后的SQL, 表名列表)
        """
        try:
            # 提取参数
            params = self.extract_params()
            
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
            
            # 替换参数
            for param_info in params:
                param_name = param_info['param']
                # 根据参数类型生成合适的随机值
                if param_name in ['batch_time', 'start', 'end']:
                    if param_name == 'batch_time':
                        replaced_value = "'2025-04-17 14:45:02'"
                    elif param_name == 'start':
                        replaced_value = "1"
                    elif param_name == 'end':
                        replaced_value = "39"
                else:
                    # 根据参数类型生成合适的值
                    param_type = param_info['type']
                    if param_type == 'datetime':
                        replaced_value = "'2025-01-01 00:00:00'"
                    elif param_type == 'number':
                        replaced_value = "123"
                    else:  # string
                        replaced_value = "'test_value'"
                
                replaced_sql = replaced_sql.replace(f"#{{{param_name}}}", replaced_value)
            
            self.logger.info(f"生成替换参数后的SQL，替换了 {len(params)} 个参数")
            self.logger.debug(f"替换后的SQL（前200字符）: {replaced_sql[:200]}...")
            
            return replaced_sql, list(tables)
            
        except Exception as e:
            self.logger.error(f"生成替换参数后的SQL时发生错误: {str(e)}", exc_info=True)
            return self.sql_text, []


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
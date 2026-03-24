#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置管理模块
负责读取和管理配置文件
"""

import os
import configparser
from typing import Dict, Any, Optional


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        初始化配置管理器
        
        Args:
            config_path: 配置文件路径，如果为None则使用默认路径
        """
        if config_path is None:
            # 默认配置文件路径
            config_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                'config',
                'config.ini'
            )
        
        self.config_path = config_path
        self.config = configparser.ConfigParser()
        
        # 读取配置文件
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"配置文件不存在: {config_path}")
        
        self.config.read(config_path, encoding='utf-8')
        
        # 验证必要配置
        self._validate_config()
    
    def _validate_config(self) -> None:
        """验证配置文件"""
        required_sections = ['database', 'ai_model']
        
        for section in required_sections:
            if not self.config.has_section(section):
                raise ValueError(f"配置文件中缺少必要的段: [{section}]")
    
    def get_database_config(self) -> Dict[str, Any]:
        """
        获取源数据库配置
        
        Returns:
            数据库配置字典
        """
        if not self.config.has_section('database'):
            return {}
        
        return {
            'host': self.config.get('database', 'source_host', fallback='localhost'),
            'port': self.config.getint('database', 'source_port', fallback=3306),
            'database': self.config.get('database', 'source_database', fallback='sql_analysis_db'),
            'username': self.config.get('database', 'source_username', fallback=''),
            'password': self.config.get('database', 'source_password', fallback=''),
            'db_type': self.config.get('database', 'source_db_type', fallback='mysql')
        }
    
    def get_target_db_config(self, db_alias: str) -> Dict[str, Any]:
        """
        获取目标数据库配置
        
        Args:
            db_alias: 数据库别名
            
        Returns:
            目标数据库配置字典
        """
        section_name = db_alias
        
        if not self.config.has_section(section_name):
            # 尝试使用默认的生产数据库配置
            if self.config.has_section('db_production'):
                section_name = 'db_production'
            else:
                raise ValueError(f"找不到数据库配置: {db_alias}")
        
        return {
            'host': self.config.get(section_name, 'host', fallback='localhost'),
            'port': self.config.getint(section_name, 'port', fallback=3306),
            'database': self.config.get(section_name, 'database', fallback=''),
            'username': self.config.get(section_name, 'username', fallback=''),
            'password': self.config.get(section_name, 'password', fallback=''),
            'db_type': self.config.get(section_name, 'db_type', fallback='mysql')
        }
    
    def get_ai_model_config(self) -> Dict[str, Any]:
        """
        获取AI模型配置
        
        Returns:
            AI模型配置字典
        """
        if not self.config.has_section('ai_model'):
            return {}
        
        return {
            'api_url': self.config.get('ai_model', 'api_url', fallback=''),
            'api_key': self.config.get('ai_model', 'api_key', fallback=''),
            'timeout': self.config.getint('ai_model', 'timeout', fallback=30),
            'max_retries': self.config.getint('ai_model', 'max_retries', fallback=3)
        }
    
    def get_log_config(self) -> Dict[str, Any]:
        """
        获取日志配置
        
        Returns:
            日志配置字典
        """
        if not self.config.has_section('logging'):
            return {
                'log_level': 'INFO',
                'log_file': 'logs/sql_analyzer.log',
                'log_format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            }
        
        return {
            'log_level': self.config.get('logging', 'log_level', fallback='INFO'),
            'log_file': self.config.get('logging', 'log_file', fallback='logs/sql_analyzer.log'),
            'log_format': self.config.get('logging', 'log_format', 
                                         fallback='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        }
    
    def get_processing_config(self) -> Dict[str, Any]:
        """
        获取处理配置
        
        Returns:
            处理配置字典
        """
        if not self.config.has_section('processing'):
            return {
                'batch_size': 10,
                'max_workers': 4,
                'large_table_threshold': 100000
            }
        
        return {
            'batch_size': self.config.getint('processing', 'batch_size', fallback=10),
            'max_workers': self.config.getint('processing', 'max_workers', fallback=4),
            'large_table_threshold': self.config.getint('processing', 'large_table_threshold', fallback=100000)
        }
    
    def get_app_config(self) -> Dict[str, Any]:
        """
        获取应用配置
        
        Returns:
            应用配置字典
        """
        if not self.config.has_section('app'):
            return {
                'debug': False,
                'max_sql_length': 10000
            }
        
        return {
            'debug': self.config.getboolean('app', 'debug', fallback=False),
            'max_sql_length': self.config.getint('app', 'max_sql_length', fallback=10000)
        }
    
    def get_all_target_db_aliases(self) -> list:
        """
        获取所有目标数据库别名
        
        Returns:
            数据库别名列表
        """
        aliases = []
        for section in self.config.sections():
            if section.startswith('db_'):
                aliases.append(section)
        
        return aliases
    
    def reload(self) -> None:
        """重新加载配置文件"""
        self.config.read(self.config_path, encoding='utf-8')
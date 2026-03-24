#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日志工具模块
提供统一的日志配置和管理
"""

import os
import sys
import logging
from logging.handlers import RotatingFileHandler
from typing import Dict, Any


def setup_logger(name: str, log_config: Dict[str, Any]) -> logging.Logger:
    """
    设置日志记录器
    
    Args:
        name: 日志记录器名称
        log_config: 日志配置字典
        
    Returns:
        配置好的日志记录器
    """
    logger = logging.getLogger(name)
    
    # 避免重复添加handler
    if logger.handlers:
        return logger
    
    # 设置日志级别
    log_level = getattr(logging, log_config.get('log_level', 'INFO').upper())
    logger.setLevel(log_level)
    
    # 创建格式化器
    formatter = logging.Formatter(
        log_config.get('log_format', 
                      '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    )
    
    # 控制台handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 文件handler
    log_file = log_config.get('log_file', 'logs/sql_analyzer.log')
    if log_file:
        # 创建日志目录
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
        
        # 使用RotatingFileHandler，每个文件最大10MB，保留5个备份
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    获取日志记录器（简化版，使用默认配置）
    
    Args:
        name: 日志记录器名称
        
    Returns:
        日志记录器
    """
    # 默认配置
    default_config = {
        'log_level': 'INFO',
        'log_file': 'logs/sql_analyzer.log',
        'log_format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    }
    
    return setup_logger(name, default_config)


class LogMixin:
    """日志混入类，方便其他类使用日志"""
    
    @property
    def logger(self) -> logging.Logger:
        """获取日志记录器"""
        if not hasattr(self, '_logger'):
            self._logger = get_logger(self.__class__.__name__)
        return self._logger
    
    def set_logger(self, logger: logging.Logger) -> None:
        """设置日志记录器"""
        self._logger = logger
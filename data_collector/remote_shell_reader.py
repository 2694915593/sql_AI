#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
远程Shell文件读取器
负责从远程服务器读取shell脚本文件内容
"""

import os
import paramiko
from typing import Optional, Dict, Any
from utils.logger import LogMixin
import socket
import time


class RemoteShellReader(LogMixin):
    """远程Shell文件读取器"""
    
    def __init__(self, config_manager=None, logger=None):
        """
        初始化远程Shell文件读取器
        
        Args:
            config_manager: 配置管理器（可选）
            logger: 日志记录器（可选）
        """
        if logger:
            self.set_logger(logger)
        # 如果logger为None，使用LogMixin的默认logger
        
        self.config_manager = config_manager
        self.ssh_client = None
        self.sftp_client = None
        
        # 默认服务器配置（可以从配置管理器读取）
        self.server_config = {
            'host': '182.118.38.115',
            'username': 'wasadmin',
            'password': 'sjyh1234',
            'base_path': '~/jump-management/TAG'
        }
        
        # 如果提供了配置管理器，尝试从配置读取
        if config_manager:
            self._load_config_from_manager()
            
        self.logger.info("远程Shell文件读取器初始化完成")
    
    def _load_config_from_manager(self):
        """从配置管理器加载服务器配置"""
        try:
            # 尝试从配置读取服务器配置
            # 可以在config.ini中添加[remote_server]节
            remote_config = self.config_manager.get_section('remote_server')
            if remote_config:
                self.server_config.update({
                    'host': remote_config.get('host', self.server_config['host']),
                    'username': remote_config.get('username', self.server_config['username']),
                    'password': remote_config.get('password', self.server_config['password']),
                    'base_path': remote_config.get('base_path', self.server_config['base_path']),
                    'port': int(remote_config.get('port', 22)),
                    'timeout': int(remote_config.get('timeout', 30))
                })
        except Exception as e:
            self.logger.warning(f"从配置管理器加载远程服务器配置失败: {str(e)}，使用默认配置")
    
    def connect(self) -> bool:
        """
        连接到远程服务器
        
        Returns:
            连接是否成功
        """
        try:
            if self.ssh_client and self.ssh_client.get_transport() and self.ssh_client.get_transport().is_active():
                self.logger.debug("SSH连接已存在且活跃")
                return True
            
            self.logger.info(f"正在连接到远程服务器 {self.server_config['host']}:{self.server_config.get('port', 22)}")
            
            # 创建SSH客户端
            self.ssh_client = paramiko.SSHClient()
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            # 连接参数
            connect_params = {
                'hostname': self.server_config['host'],
                'port': self.server_config.get('port', 22),
                'username': self.server_config['username'],
                'password': self.server_config['password'],
                'timeout': self.server_config.get('timeout', 30),
                'allow_agent': False,
                'look_for_keys': False
            }
            
            # 尝试连接
            self.ssh_client.connect(**connect_params)
            
            self.logger.info("SSH连接成功")
            return True
            
        except paramiko.AuthenticationException as e:
            self.logger.error(f"SSH认证失败: {str(e)}")
            return False
        except paramiko.SSHException as e:
            self.logger.error(f"SSH连接异常: {str(e)}")
            return False
        except socket.timeout as e:
            self.logger.error(f"连接超时: {str(e)}")
            return False
        except Exception as e:
            self.logger.error(f"连接远程服务器失败: {str(e)}")
            return False
    
    def disconnect(self):
        """断开连接"""
        try:
            if self.sftp_client:
                self.sftp_client.close()
                self.sftp_client = None
            
            if self.ssh_client:
                self.ssh_client.close()
                self.ssh_client = None
            
            self.logger.info("已断开远程连接")
        except Exception as e:
            self.logger.warning(f"断开连接时发生错误: {str(e)}")
    
    def get_sftp_client(self):
        """获取SFTP客户端（如果不存在则创建）"""
        try:
            if not self.ssh_client or not self.ssh_client.get_transport() or not self.ssh_client.get_transport().is_active():
                if not self.connect():
                    return None
            
            if not self.sftp_client:
                self.sftp_client = self.ssh_client.open_sftp()
            
            return self.sftp_client
        except Exception as e:
            self.logger.error(f"创建SFTP客户端失败: {str(e)}")
            return None
    
    def read_shell_file(self, system: str, classpath: str, filename: Optional[str] = None) -> Optional[str]:
        """
        从远程服务器读取shell文件内容
        
        Args:
            system: SYSTEM字段（如CBNK）
            classpath: CLASSPATH字段（如CbnkShell/release/26.1.06/a.sh）
            filename: 文件名（可选，如果classpath已包含文件名则不需要）
            
        Returns:
            文件内容字符串，如果失败则返回None
        """
        # 构建远程文件路径
        remote_path = self.build_remote_path(system, classpath, filename)
        if not remote_path:
            return None
        
        self.logger.info(f"正在读取远程文件: {remote_path}")
        
        try:
            sftp = self.get_sftp_client()
            if not sftp:
                self.logger.error("无法获取SFTP客户端")
                return None
            
            # 检查文件是否存在
            try:
                file_stat = sftp.stat(remote_path)
                self.logger.debug(f"文件大小: {file_stat.st_size} 字节")
            except FileNotFoundError:
                self.logger.error(f"远程文件不存在: {remote_path}")
                return None
            except Exception as e:
                self.logger.error(f"检查远程文件状态失败: {str(e)}")
                return None
            
            # 读取文件内容
            with sftp.open(remote_path, 'r') as f:
                content = f.read()
            
            # 尝试解码为UTF-8，如果失败则使用其他编码
            try:
                content_str = content.decode('utf-8')
            except UnicodeDecodeError:
                self.logger.warning("UTF-8解码失败，尝试GBK编码")
                try:
                    content_str = content.decode('gbk')
                except UnicodeDecodeError:
                    self.logger.warning("GBK解码失败，尝试latin-1编码")
                    content_str = content.decode('latin-1', errors='replace')
            
            self.logger.info(f"成功读取远程文件，大小: {len(content_str)} 字符")
            return content_str
            
        except Exception as e:
            self.logger.error(f"读取远程文件失败: {str(e)}")
            return None
    
    def build_remote_path(self, system: str, classpath: str, filename: Optional[str] = None) -> Optional[str]:
        """
        构建远程文件路径
        
        Args:
            system: SYSTEM字段
            classpath: CLASSPATH字段
            filename: 文件名（可选）
            
        Returns:
            完整的远程文件路径
        """
        if not system or not classpath:
            self.logger.error("SYSTEM和CLASSPATH字段不能为空")
            return None
        
        # 清理路径组件
        system = system.strip()
        classpath = classpath.strip()
        
        # 如果classpath已经包含文件名，则直接使用
        # 否则，如果提供了filename，则添加到classpath末尾
        if filename and not self._has_filename(classpath):
            # 确保classpath以斜杠结尾
            if not classpath.endswith('/'):
                classpath += '/'
            classpath += filename.strip()
        
        # 构建完整路径：base_path/SYSTEM/CLASSPATH
        base_path = self.server_config['base_path'].rstrip('/')
        remote_path = f"{base_path}/{system}/{classpath}"
        
        # 规范化路径（移除多余的斜杠等）
        remote_path = remote_path.replace('//', '/').replace('//', '/')
        
        self.logger.debug(f"构建的远程路径: {remote_path}")
        return remote_path
    
    def _has_filename(self, path: str) -> bool:
        """检查路径是否包含文件名（有扩展名）"""
        if not path:
            return False
        
        # 获取路径的最后一部分
        basename = os.path.basename(path)
        if not basename:
            return False
        
        # 检查是否有扩展名（如.sh、.shell、.sql等）
        # 简单的检查：包含点号且点号后至少有一个字符
        if '.' in basename:
            parts = basename.split('.')
            if len(parts) > 1 and parts[-1]:
                return True
        
        return False
    
    def test_connection(self) -> Dict[str, Any]:
        """
        测试远程连接
        
        Returns:
            测试结果字典
        """
        result = {
            'success': False,
            'message': '',
            'details': {}
        }
        
        try:
            start_time = time.time()
            connected = self.connect()
            end_time = time.time()
            
            if connected:
                result['success'] = True
                result['message'] = f"成功连接到 {self.server_config['host']}"
                result['details'] = {
                    'host': self.server_config['host'],
                    'connection_time': round(end_time - start_time, 3),
                    'transport_active': self.ssh_client.get_transport().is_active() if self.ssh_client else False
                }
                
                # 尝试执行一个简单命令来验证连接
                try:
                    stdin, stdout, stderr = self.ssh_client.exec_command('pwd', timeout=5)
                    pwd_output = stdout.read().decode('utf-8', errors='ignore').strip()
                    result['details']['pwd'] = pwd_output
                except Exception as e:
                    result['details']['command_test_error'] = str(e)
                
                self.disconnect()
            else:
                result['message'] = f"无法连接到 {self.server_config['host']}"
                
        except Exception as e:
            result['message'] = f"连接测试异常: {str(e)}"
        
        return result
    
    def list_files(self, system: str, path: str = "") -> Optional[list]:
        """
        列出远程目录中的文件
        
        Args:
            system: SYSTEM字段
            path: 相对路径（相对于base_path/SYSTEM）
            
        Returns:
            文件列表，每个元素为字典包含文件名和属性
        """
        try:
            remote_path = self.build_remote_path(system, path)
            if not remote_path:
                return None
            
            sftp = self.get_sftp_client()
            if not sftp:
                return None
            
            files = []
            for item in sftp.listdir_attr(remote_path):
                file_info = {
                    'filename': item.filename,
                    'size': item.st_size,
                    'mode': item.st_mode,
                    'is_directory': not self._is_file(item)
                }
                files.append(file_info)
            
            return files
            
        except Exception as e:
            self.logger.error(f"列出远程目录失败: {str(e)}")
            return None
    
    def _is_file(self, attrs) -> bool:
        """检查SFTP属性是否为文件"""
        import stat
        return stat.S_ISREG(attrs.st_mode)


# 提供便捷函数
def read_remote_shell_file(system: str, classpath: str, filename: Optional[str] = None, 
                          config_manager=None, logger=None) -> Optional[str]:
    """从远程服务器读取shell文件内容（便捷函数）"""
    reader = RemoteShellReader(config_manager, logger)
    try:
        content = reader.read_shell_file(system, classpath, filename)
        return content
    finally:
        reader.disconnect()


def test_remote_connection(config_manager=None, logger=None) -> Dict[str, Any]:
    """测试远程连接（便捷函数）"""
    reader = RemoteShellReader(config_manager, logger)
    try:
        return reader.test_connection()
    finally:
        reader.disconnect()
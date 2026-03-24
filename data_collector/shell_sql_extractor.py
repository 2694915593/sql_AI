#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Shell脚本SQL提取器
负责从shell脚本中提取SQL语句，支持多种shell语法和数据库客户端命令
"""

import re
import os
from typing import List, Dict, Any, Optional, Tuple
from utils.logger import LogMixin


class ShellScriptSQLExtractor(LogMixin):
    """Shell脚本SQL提取器"""
    
    # 支持的数据库客户端命令
    DB_CLIENTS = {
        'mysql': ['-e', '--execute'],
        'psql': ['-c', '--command'],
        'sqlplus': [],  # sqlplus通常使用here文档或直接参数
        'sqlcmd': ['-Q', '--query'],
        'clickhouse-client': ['--query'],
        'mariadb': ['-e', '--execute'],
        'sqlite3': [],  # sqlite3通常使用管道或文件
    }
    
    # SQL语句开始关键字（用于验证提取的文本是否是SQL）
    SQL_KEYWORDS = [
        'SELECT', 'INSERT', 'UPDATE', 'DELETE', 'CREATE', 'ALTER', 'DROP',
        'TRUNCATE', 'MERGE', 'WITH', 'EXPLAIN', 'DESCRIBE', 'SHOW',
        'BEGIN', 'COMMIT', 'ROLLBACK', 'SAVEPOINT', 'RELEASE',
        'GRANT', 'REVOKE', 'DENY', 'USE', 'SET'
    ]
    
    def __init__(self, logger=None):
        """
        初始化Shell脚本SQL提取器
        
        Args:
            logger: 日志记录器
        """
        if logger:
            self.set_logger(logger)
        # 如果logger为None，使用LogMixin的默认logger
            
        self.logger.info("Shell脚本SQL提取器初始化完成")
    
    def extract_sql_from_file(self, file_path: str) -> List[Dict[str, Any]]:
        """
        从shell脚本文件提取SQL语句
        
        Args:
            file_path: shell脚本文件路径
            
        Returns:
            SQL语句列表，每个元素包含:
            - sql: SQL语句文本
            - line_start: 起始行号
            - line_end: 结束行号
            - context: 提取上下文（命令、变量名等）
            - source: 源文件路径
        """
        if not os.path.exists(file_path):
            self.logger.error(f"文件不存在: {file_path}")
            return []
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            return self.extract_sql_from_content(content, file_path)
            
        except Exception as e:
            self.logger.error(f"读取文件 {file_path} 失败: {str(e)}")
            return []
    
    def extract_sql_from_content(self, content: str, source: str = None) -> List[Dict[str, Any]]:
        """
        从shell脚本内容提取SQL语句
        
        Args:
            content: shell脚本内容
            source: 源标识（文件路径或描述）
            
        Returns:
            SQL语句列表
        """
        if not content:
            return []
            
        sql_statements = []
        
        # 按行分割，保留行号信息
        lines = content.split('\n')
        
        # 方法1: 提取数据库客户端命令中的SQL
        sql_statements.extend(self._extract_from_db_commands(lines, source))
        
        # 方法2: 提取here文档中的SQL
        sql_statements.extend(self._extract_from_heredocs(lines, source))
        
        # 方法3: 提取变量赋值中的SQL
        sql_statements.extend(self._extract_from_variables(lines, source))
        
        # 方法4: 提取管道和重定向中的SQL
        sql_statements.extend(self._extract_from_pipes(lines, source))
        
        # 方法5: 提取直接SQL字符串（作为最后的备选方案）
        sql_statements.extend(self._extract_direct_sql_strings(lines, source))
        
        # 去重并清理
        sql_statements = self._deduplicate_sql_statements(sql_statements)
        
        self.logger.info(f"从内容中提取到 {len(sql_statements)} 条SQL语句")
        return sql_statements
    
    def _extract_from_db_commands(self, lines: List[str], source: str) -> List[Dict[str, Any]]:
        """从数据库客户端命令中提取SQL"""
        sql_statements = []
        i = 0
        
        while i < len(lines):
            result = self._find_command_and_string(lines, i)
            if result:
                command, sql_content, start_line, end_line, context = result
                
                # 清理SQL内容
                sql_text = self._clean_sql_text(sql_content)
                
                if self._is_valid_sql(sql_text):
                    sql_statements.append({
                        'sql': sql_text,
                        'line_start': start_line + 1,  # 转换为1-based
                        'line_end': end_line + 1,
                        'context': context,
                        'source': source
                    })
                
                # 跳到结束引号之后的行
                i = end_line + 1
            else:
                i += 1
        
        return sql_statements
    
    def _extract_from_heredocs(self, lines: List[str], source: str) -> List[Dict[str, Any]]:
        """从here文档中提取SQL"""
        sql_statements = []
        
        # 匹配here文档开始标记：<<或<<- 后跟标记符，允许命令后跟参数
        heredoc_start_pattern = r'^\s*(\w+)\b[^\n]*<<\s*-?\s*[\'"`]?(\w+)[\'"`]?\s*$'
        
        i = 0
        while i < len(lines):
            line = lines[i]
            start_match = re.match(heredoc_start_pattern, line)
            
            if start_match:
                # 找到here文档开始
                command = start_match.group(1)  # 命令（如mysql）
                marker = start_match.group(2)   # 结束标记
                
                # 查找结束标记
                heredoc_lines = []
                j = i + 1
                while j < len(lines):
                    if lines[j].strip() == marker:
                        # 找到结束标记
                        break
                    heredoc_lines.append(lines[j])
                    j += 1
                
                if j < len(lines):
                    # 成功找到结束标记
                    heredoc_content = '\n'.join(heredoc_lines)
                    
                    # 提取命令基本名称（去掉路径）
                    cmd_name = command.split('/')[-1].split('\\')[-1]
                    # 检查命令是否是数据库客户端
                    is_db_client = any(client in cmd_name.lower() for client in self.DB_CLIENTS.keys())
                    
                    if is_db_client or self._contains_sql_keywords(heredoc_content):
                        # 清理内容并分割SQL语句
                        sql_texts = self._split_sql_statements(heredoc_content)
                        
                        for sql_text in sql_texts:
                            if self._is_valid_sql(sql_text):
                                sql_statements.append({
                                    'sql': sql_text,
                                    'line_start': i + 2,  # here文档内容开始行
                                    'line_end': j,
                                    'context': f"{command} heredoc",
                                    'source': source
                                })
                
                i = j + 1  # 跳到结束标记之后
            else:
                i += 1
        
        return sql_statements
    
    def _extract_from_variables(self, lines: List[str], source: str) -> List[Dict[str, Any]]:
        """从变量赋值中提取SQL"""
        sql_statements = []
        
        # 匹配变量赋值：VAR="SQL语句" 或 VAR='SQL语句'（只匹配到开始引号）
        var_pattern = r'^\s*(\w+)\s*=\s*([\'"`])'
        
        i = 0
        while i < len(lines):
            line = lines[i]
            match = re.search(var_pattern, line)
            
            if match:
                var_name = match.group(1)
                quote_char = match.group(2)
                start_col = match.start(2)  # 引号开始位置
                
                # 提取跨行字符串
                var_value, end_line, end_col = self._extract_multiline_string(
                    lines, i, start_col, quote_char
                )
                
                # 检查变量值是否包含SQL
                if var_value and self._contains_sql_keywords(var_value):
                    sql_texts = self._split_sql_statements(var_value)
                    
                    for sql_text in sql_texts:
                        if self._is_valid_sql(sql_text):
                            sql_statements.append({
                                'sql': sql_text,
                                'line_start': i + 1,  # 转换为1-based
                                'line_end': end_line + 1,
                                'context': f"variable ${var_name}",
                                'source': source
                            })
                
                # 跳到结束引号之后的行
                i = end_line + 1
            else:
                i += 1
        
        return sql_statements
    
    def _extract_from_pipes(self, lines: List[str], source: str) -> List[Dict[str, Any]]:
        """从管道命令中提取SQL"""
        sql_statements = []
        
        # 匹配管道：echo "SQL" | mysql 或 cat file.sql | mysql
        pipe_pattern = r'^\s*(?:echo|cat|printf)\s+([\'"`])(.*?)\1\s*\|\s*(\w+)\s*$'
        
        for line_num, line in enumerate(lines, 1):
            match = re.match(pipe_pattern, line, re.IGNORECASE)
            if match:
                quote_char = match.group(1)
                pipe_content = match.group(2)
                command = match.group(3)
                
                # 检查命令是否是数据库客户端
                is_db_client = any(client in command.lower() for client in self.DB_CLIENTS.keys())
                
                if is_db_client and self._contains_sql_keywords(pipe_content):
                    sql_text = self._clean_sql_text(pipe_content)
                    
                    if self._is_valid_sql(sql_text):
                        sql_statements.append({
                            'sql': sql_text,
                            'line_start': line_num,
                            'line_end': line_num,
                            'context': f"pipe to {command}",
                            'source': source
                        })
        
        return sql_statements
    
    def _extract_direct_sql_strings(self, lines: List[str], source: str) -> List[Dict[str, Any]]:
        """提取直接的SQL字符串（作为备选方案）"""
        sql_statements = []
        
        # 匹配被引号包围的文本，且包含SQL关键字
        quote_pattern = r'([\'"`])(.*?)\1'
        
        for line_num, line in enumerate(lines, 1):
            # 查找所有引号包围的文本
            matches = re.finditer(quote_pattern, line)
            for match in matches:
                text = match.group(2)
                
                # 检查是否包含SQL关键字
                if self._contains_sql_keywords(text):
                    sql_texts = self._split_sql_statements(text)
                    
                    for sql_text in sql_texts:
                        if self._is_valid_sql(sql_text):
                            sql_statements.append({
                                'sql': sql_text,
                                'line_start': line_num,
                                'line_end': line_num,
                                'context': "quoted string",
                                'source': source
                            })
        
        return sql_statements
    
    def _clean_sql_text(self, sql_text: str) -> str:
        """清理SQL文本"""
        if not sql_text:
            return ""
        
        # 移除首尾空白
        sql_text = sql_text.strip()
        
        # 移除行续行符（反斜杠后跟换行符）
        sql_text = re.sub(r'\\\s*\n\s*', ' ', sql_text)
        
        # 移除多余的空白字符
        sql_text = re.sub(r'\s+', ' ', sql_text)
        
        return sql_text
    
    def _extract_multiline_string(self, lines: List[str], start_line: int, start_col: int, quote_char: str) -> Tuple[str, int, int]:
        """
        提取跨行引号字符串
        
        Args:
            lines: 行列表
            start_line: 起始行索引（0-based）
            start_col: 起始列索引（引号开始位置）
            quote_char: 引号字符（'、"、`）
            
        Returns:
            (字符串内容, 结束行索引, 结束列索引)
        """
        content_lines = []
        current_line = start_line
        current_col = start_col + 1  # 跳过开始引号
        
        # 处理转义引号：\" \' \`
        escape_char = '\\'
        in_escape = False
        
        while current_line < len(lines):
            line = lines[current_line]
            
            while current_col < len(line):
                char = line[current_col]
                
                if in_escape:
                    # 转义字符，下一个字符直接加入
                    content_lines.append(char)
                    in_escape = False
                elif char == escape_char:
                    # 遇到转义字符
                    in_escape = True
                elif char == quote_char:
                    # 找到结束引号
                    # 返回内容（不包括结束引号）和结束位置
                    end_line = current_line
                    end_col = current_col
                    # 合并内容
                    content = ''.join(content_lines)
                    return content, end_line, end_col
                else:
                    content_lines.append(char)
                
                current_col += 1
            
            # 当前行结束，换行
            if current_line < len(lines) - 1:
                content_lines.append('\n')
                current_line += 1
                current_col = 0
            else:
                # 文件结束，没有找到结束引号
                break
        
        # 没有找到结束引号，返回已收集的内容
        content = ''.join(content_lines)
        return content, current_line, current_col
    
    def _find_command_and_string(self, lines: List[str], start_line: int) -> Optional[Tuple[str, str, int, int, str]]:
        """
        从指定行开始查找数据库命令和SQL字符串
        
        Args:
            lines: 行列表
            start_line: 起始行索引
            
        Returns:
            (命令, SQL字符串, 开始行, 结束行, 上下文) 或 None
        """
        clients_pattern = '|'.join(re.escape(client) for client in self.DB_CLIENTS.keys())
        
        # 匹配命令和可能的参数，直到遇到引号
        command_pattern = rf'\b({clients_pattern})\s+(?:[^\'"\n]*(?:(?:-e|-c|--execute|--command|-Q|--query)\s+)?)([\'"`])'
        
        for line_idx in range(start_line, len(lines)):
            line = lines[line_idx]
            match = re.search(command_pattern, line, re.IGNORECASE)
            if match:
                command = match.group(1)
                quote_char = match.group(2)
                start_col = match.start(2)  # 引号开始位置
                
                # 提取跨行字符串
                sql_content, end_line, end_col = self._extract_multiline_string(
                    lines, line_idx, start_col, quote_char
                )
                
                if sql_content:
                    context = f"{command} command"
                    return command, sql_content, line_idx, end_line, context
        
        return None
    
    def _contains_sql_keywords(self, text: str) -> bool:
        """检查文本是否包含SQL关键字"""
        text_upper = text.upper()
        for keyword in self.SQL_KEYWORDS:
            # 使用单词边界匹配，避免匹配到子字符串
            pattern = r'\b' + re.escape(keyword) + r'\b'
            if re.search(pattern, text_upper):
                return True
        return False
    
    def _is_valid_sql(self, sql_text: str) -> bool:
        """检查是否是有效的SQL语句"""
        if not sql_text or len(sql_text) < 10:  # 最小长度阈值
            return False
        
        # 必须包含SQL关键字
        if not self._contains_sql_keywords(sql_text):
            return False
        
        # 检查常见的SQL语法问题
        # 这里可以添加更多验证逻辑
        
        return True
    
    def _split_sql_statements(self, text: str) -> List[str]:
        """将文本分割成独立的SQL语句"""
        if not text:
            return []
        
        # 使用分号分割SQL语句
        statements = []
        current = ""
        in_quote = None  # 跟踪当前是否在引号内
        
        for char in text:
            if char in ['"', "'", '`']:
                if in_quote == char:
                    in_quote = None
                elif in_quote is None:
                    in_quote = char
                current += char
            elif char == ';' and in_quote is None:
                statements.append(current.strip() + ';')
                current = ""
            else:
                current += char
        
        # 添加最后一个语句（如果没有以分号结尾）
        if current.strip():
            statements.append(current.strip())
        
        return [stmt for stmt in statements if stmt]
    
    def _deduplicate_sql_statements(self, sql_statements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """去重SQL语句"""
        seen = set()
        deduplicated = []
        
        for stmt in sql_statements:
            # 创建标识符：SQL文本 + 行号范围
            identifier = (stmt['sql'], stmt.get('line_start'), stmt.get('line_end'))
            
            if identifier not in seen:
                seen.add(identifier)
                deduplicated.append(stmt)
        
        return deduplicated


# 提供便捷函数
def extract_sql_from_shell_file(file_path: str, logger=None) -> List[Dict[str, Any]]:
    """从shell脚本文件提取SQL语句（便捷函数）"""
    extractor = ShellScriptSQLExtractor(logger)
    return extractor.extract_sql_from_file(file_path)


def extract_sql_from_shell_content(content: str, source: str = None, logger=None) -> List[Dict[str, Any]]:
    """从shell脚本内容提取SQL语句（便捷函数）"""
    extractor = ShellScriptSQLExtractor(logger)
    return extractor.extract_sql_from_content(content, source)
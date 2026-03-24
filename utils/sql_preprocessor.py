#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SQL预处理器模块
负责处理带XML标签的SQL，将其转换为标准SQL格式
"""

import re
from typing import Tuple, List, Dict, Any
from .logger import LogMixin
try:
    from ..ai_integration.xml_tag_remover import XmlTagRemover
    HAS_AI_MODULE = True
except ImportError:
    HAS_AI_MODULE = False
    XmlTagRemover = None


class SQLPreprocessor(LogMixin):
    """SQL预处理器"""
    
    def __init__(self, logger=None, config_manager=None):
        """
        初始化SQL预处理器
        
        Args:
            logger: 日志记录器
            config_manager: 配置管理器（用于大模型处理）
        """
        super().__init__()
        if logger:
            self.set_logger(logger)
        
        self.config_manager = config_manager
        self.xml_tag_remover = None
        
        # 如果启用了大模型且可用，初始化大模型移除器
        if HAS_AI_MODULE and config_manager:
            try:
                self.xml_tag_remover = XmlTagRemover(config_manager, logger)
                # 改为debug级别，避免重复日志
                self.logger.debug("SQL预处理器初始化完成，大模型XML标签移除器已启用")
            except Exception as e:
                self.logger.debug(f"初始化大模型XML标签移除器失败，将使用正则表达式: {str(e)}")
                self.xml_tag_remover = None
        else:
            self.logger.debug("SQL预处理器初始化完成，使用正则表达式处理XML标签")
    
    def contains_xml_tags(self, sql_text: str) -> bool:
        """
        检查SQL是否包含XML标签
        
        Args:
            sql_text: SQL语句文本
            
        Returns:
            是否包含XML标签
        """
        if not sql_text or not sql_text.strip():
            return False
        
        # 检查是否包含XML标签模式
        xml_patterns = [
            r'<[^>]+>',  # 基本XML标签
            r'<!\[CDATA\[',  # CDATA标记
        ]
        
        for pattern in xml_patterns:
            if re.search(pattern, sql_text):
                return True
        
        return False
    
    def remove_xml_tags(self, sql_text: str, keep_content: bool = True) -> str:
        """
        移除SQL中的XML标签
        
        Args:
            sql_text: 原始SQL语句
            keep_content: 是否保留标签内容（True：保留，False：移除标签及内容）
            
        Returns:
            清理后的SQL语句
        """
        if not sql_text or not sql_text.strip():
            return sql_text
        
        result = sql_text
        
        # 先处理CDATA部分
        if keep_content:
            # 保留CDATA内容
            result = re.sub(r'<!\[CDATA\[(.*?)\]\]>', r'\1', result, flags=re.DOTALL)
        else:
            # 移除整个CDATA部分
            result = re.sub(r'<!\[CDATA\[.*?\]\]>', '', result, flags=re.DOTALL)
        
        if keep_content:
            # 保留标签内容，只移除标签本身
            # 先移除自闭合标签
            result = re.sub(r'<[^>]+/>', ' ', result)
            # 再移除普通标签
            result = re.sub(r'<[^>]+>', ' ', result)
        else:
            # 移除整个标签及其内容
            # 先移除CDATA标签（已处理）
            # 移除其他标签及其内容
            result = re.sub(r'<[^>]+>.*?</[^>]+>', '', result, flags=re.DOTALL)
            result = re.sub(r'<[^>]+/>', '', result)
        
        # 压缩多余空格
        result = re.sub(r'\s+', ' ', result).strip()
        
        return result
    
    def _preprocess_with_model(self, sql_text: str, mode: str = "normalize") -> Tuple[str, Dict[str, Any]]:
        """
        使用大模型预处理SQL
        
        Args:
            sql_text: 原始SQL语句
            mode: 处理模式
            
        Returns:
            (处理后的SQL, 处理信息)
        """
        if not self.xml_tag_remover:
            self.logger.warning("大模型移除器未初始化，使用正则表达式回退")
            return self.remove_xml_tags(sql_text, keep_content=True), {
                'method': 'regex_fallback',
                'model_used': False
            }
        
        try:
            # 调用大模型移除XML标签
            processed_sql, model_info = self.xml_tag_remover.remove_xml_tags_with_model(sql_text, mode)
            model_info['model_used'] = True
            return processed_sql, model_info
        except Exception as e:
            self.logger.error(f"大模型处理失败: {str(e)}")
            # 回退到正则表达式
            return self.remove_xml_tags(sql_text, keep_content=True), {
                'method': 'regex_fallback',
                'model_used': False,
                'error': str(e)
            }
    
    def preprocess_sql(self, sql_text: str, mode: str = "normalize") -> Tuple[str, Dict[str, Any]]:
        """
        预处理SQL语句，处理XML标签等特殊格式
        
        Args:
            sql_text: 原始SQL语句
            mode: 预处理模式
                - "normalize": 标准化处理，移除标签但保留内容（正则表达式）
                - "extract": 提取SQL内容，移除整个标签
                - "detect": 仅检测，不修改
                - "model": 使用大模型智能处理XML标签
                
        Returns:
            (处理后的SQL, 预处理信息)
        """
        if not sql_text or not sql_text.strip():
            return sql_text, {
                'has_xml_tags': False,
                'original_length': 0,
                'processed_length': 0,
                'mode': mode
            }
        
        info = {
            'has_xml_tags': self.contains_xml_tags(sql_text),
            'original_length': len(sql_text),
            'mode': mode,
            'original_preview': sql_text[:100] + ('...' if len(sql_text) > 100 else '')
        }
        
        if mode == "detect":
            # 只检测，不修改
            processed_sql = sql_text
        elif info['has_xml_tags']:
            if mode == "model":
                # 大模型处理模式
                processed_sql, model_info = self._preprocess_with_model(sql_text, "normalize")
                info.update(model_info)
                info['action'] = 'model_normalized'
            elif mode == "extract":
                # 提取模式：移除整个标签
                processed_sql = self.remove_xml_tags(sql_text, keep_content=True)
                info['action'] = 'extracted_xml_tags'
            else:  # normalize or default
                # 标准化模式：移除标签但保留内容
                processed_sql = self.remove_xml_tags(sql_text, keep_content=True)
                info['action'] = 'normalized_xml_tags'
            
            # 记录处理详情
            info['processed_preview'] = processed_sql[:100] + ('...' if len(processed_sql) > 100 else '')
            
            # 如果处理后的SQL为空，可能需要特殊处理
            if not processed_sql.strip():
                self.logger.warning(f"预处理后SQL为空，原始SQL: {sql_text[:50]}...")
                # 尝试使用提取模式再处理一次
                processed_sql = self.remove_xml_tags(sql_text, keep_content=False)
                if processed_sql.strip():
                    info['action'] = 'extracted_xml_tags_fallback'
                    info['processed_preview'] = processed_sql[:100] + ('...' if len(processed_sql) > 100 else '')
        else:
            # 没有XML标签，直接返回
            processed_sql = sql_text
            info['action'] = 'no_action_needed'
        
        info['processed_length'] = len(processed_sql)
        
        if info['has_xml_tags']:
            self.logger.info(f"SQL预处理: 原始长度={info['original_length']}, 处理后长度={info['processed_length']}, 模式={mode}")
            if info.get('original_preview') and info.get('processed_preview'):
                self.logger.debug(f"预处理前后对比: '{info['original_preview']}' -> '{info['processed_preview']}'")
        
        return processed_sql, info
    
    def safe_detect_sql_type(self, sql_text: str) -> str:
        """
        安全检测SQL类型，先预处理再检测
        
        Args:
            sql_text: SQL语句文本
            
        Returns:
            SQL类型: DML, DDL, DCL, TCL 或 UNKNOWN
        """
        if not sql_text:
            return "UNKNOWN"
        
        # 先预处理SQL
        processed_sql, info = self.preprocess_sql(sql_text, mode="normalize")
        
        if not processed_sql.strip():
            return "UNKNOWN"
        
        # 使用现有的detect_sql_type逻辑（这里简化实现）
        sql_upper = processed_sql.strip().upper()
        
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
    
    def normalize_for_execution_plan(self, sql_text: str) -> str:
        """
        为执行计划标准化SQL（去注释、去标签、去末尾分号、压缩空白）
        
        Args:
            sql_text: SQL语句文本
            
        Returns:
            标准化后的SQL
        """
        if not sql_text:
            return ""
        
        # 先预处理移除XML标签
        processed_sql, _ = self.preprocess_sql(sql_text, mode="normalize")
        
        if not processed_sql:
            return ""
        
        # 移除SQL注释
        text = re.sub(r'/\*.*?\*/', ' ', processed_sql, flags=re.S)
        text = re.sub(r'--[^\r\n]*', ' ', text)
        text = re.sub(r'#[^\r\n]*', ' ', text)
        
        # 去末尾分号
        text = text.strip().rstrip(';').strip()
        
        # 压缩连续空白
        text = re.sub(r'\s+', ' ', text)
        
        return text


def preprocess_sql_wrapper(sql_text: str, logger=None) -> Tuple[str, Dict[str, Any]]:
    """
    SQL预处理的便捷函数
    
    Args:
        sql_text: SQL语句文本
        logger: 日志记录器
        
    Returns:
        (处理后的SQL, 预处理信息)
    """
    preprocessor = SQLPreprocessor(logger)
    return preprocessor.preprocess_sql(sql_text)


def contains_xml_tags_wrapper(sql_text: str) -> bool:
    """
    检查是否包含XML标签的便捷函数
    
    Args:
        sql_text: SQL语句文本
        
    Returns:
        是否包含XML标签
    """
    preprocessor = SQLPreprocessor()
    return preprocessor.contains_xml_tags(sql_text)


if __name__ == "__main__":
    """测试SQL预处理器"""
    
    test_cases = [
        ("SELECT * FROM users", "普通SQL"),
        ("<select>SELECT * FROM users</select>", "带select标签"),
        ("<select>\nSELECT * FROM users\n</select>", "带标签和换行"),
        ("<query><select>SELECT * FROM users</select></query>", "嵌套标签"),
        ("<insert>INSERT INTO users VALUES (1, 'test')</insert>", "带insert标签"),
        ("<select><![CDATA[SELECT * FROM users]]></select>", "带CDATA"),
        ("<sql type=\"query\"><select>SELECT name FROM users</select></sql>", "带属性标签"),
        ("<statement><select>SELECT * FROM users</select></statement>", "多层嵌套标签"),
    ]
    
    preprocessor = SQLPreprocessor()
    
    print("SQL预处理器测试")
    print("=" * 80)
    
    for sql, description in test_cases:
        print(f"\n测试: {description}")
        print(f"原始SQL: {sql[:60]}...")
        
        # 检查是否包含XML标签
        has_xml = preprocessor.contains_xml_tags(sql)
        print(f"包含XML标签: {has_xml}")
        
        if has_xml:
            # 预处理
            processed_sql, info = preprocessor.preprocess_sql(sql)
            print(f"处理后SQL: {processed_sql[:60]}...")
            print(f"预处理信息: {info}")
            
            # 检测SQL类型
            sql_type = preprocessor.safe_detect_sql_type(sql)
            print(f"SQL类型: {sql_type}")
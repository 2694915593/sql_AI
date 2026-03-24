#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
大模型驱动的XML标签移除器
使用大模型智能移除SQL语句中的XML标签，转换为标准SQL格式
"""

import re
from typing import Tuple, Dict, Any, Optional
from utils.logger import LogMixin
from ai_integration.model_client import ModelClient


class XmlTagRemover(LogMixin):
    """使用大模型移除XML标签的处理器"""
    
    def __init__(self, config_manager=None, logger=None):
        """
        初始化XML标签移除器
        
        Args:
            config_manager: 配置管理器（用于获取大模型配置）
            logger: 日志记录器
        """
        super().__init__()
        if logger:
            self.set_logger(logger)
        
        self.config_manager = config_manager
        self.model_client = None
        
        # 如果提供了配置管理器，尝试初始化大模型客户端
        if config_manager:
            try:
                self.model_client = ModelClient(config_manager, logger)
                self.logger.info("大模型XML标签移除器初始化完成")
            except Exception as e:
                self.logger.warning(f"初始化大模型客户端失败，将使用正则表达式回退: {str(e)}")
                self.model_client = None
        else:
            self.logger.warning("未提供配置管理器，将使用正则表达式方法")
            self.model_client = None
    
    def remove_xml_tags_with_model(self, sql_text: str, mode: str = "normalize") -> Tuple[str, Dict[str, Any]]:
        """
        使用大模型移除XML标签
        
        Args:
            sql_text: 原始SQL语句
            mode: 处理模式
                - "normalize": 标准化处理，移除标签但保留内容
                - "extract": 提取SQL内容，移除整个标签
                
        Returns:
            (处理后的SQL, 处理信息)
        """
        if not sql_text or not sql_text.strip():
            return sql_text, {
                'method': 'none',
                'has_xml_tags': False,
                'original_length': 0,
                'processed_length': 0,
                'mode': mode
            }
        
        info = {
            'method': 'regex_fallback',
            'has_xml_tags': self._contains_xml_tags_regex(sql_text),
            'original_length': len(sql_text),
            'mode': mode,
            'original_preview': sql_text[:100] + ('...' if len(sql_text) > 100 else '')
        }
        
        # 如果没有大模型客户端，直接使用正则表达式
        if not self.model_client:
            self.logger.info("未使用大模型，使用正则表达式处理XML标签")
            return self._remove_xml_tags_regex(sql_text, mode, info)
        
        # 检查是否包含XML标签
        if not info['has_xml_tags']:
            info['method'] = 'none_needed'
            info['action'] = 'no_action_needed'
            return sql_text, info
        
        try:
            # 使用大模型处理
            processed_sql, model_info = self._call_model_for_xml_removal(sql_text, mode)
            
            # 验证大模型返回的结果
            if self._validate_model_result(processed_sql, sql_text):
                info.update(model_info)
                info['method'] = 'model'
                info['processed_preview'] = processed_sql[:100] + ('...' if len(processed_sql) > 100 else '')
                info['processed_length'] = len(processed_sql)
                self.logger.info(f"大模型处理成功: 原始长度={info['original_length']}, 处理后长度={info['processed_length']}")
                return processed_sql, info
            else:
                self.logger.warning("大模型返回结果验证失败，使用正则表达式回退")
        except Exception as e:
            self.logger.warning(f"大模型处理失败，使用正则表达式回退: {str(e)}")
        
        # 大模型失败，使用正则表达式回退
        return self._remove_xml_tags_regex(sql_text, mode, info)
    
    def _call_model_for_xml_removal(self, sql_text: str, mode: str) -> Tuple[str, Dict[str, Any]]:
        """
        调用大模型API移除XML标签
        
        Args:
            sql_text: 原始SQL语句
            mode: 处理模式
            
        Returns:
            (处理后的SQL, 模型处理信息)
        """
        # 检查大模型客户端是否可用
        if not self.model_client:
            raise Exception("大模型客户端未初始化")
        
        try:
            # 使用专用的XML标签移除API
            response = self.model_client.remove_xml_tags(sql_text, mode)
            
            # 解析响应
            if response.get('success', False):
                processed_sql = response.get('processed_sql', sql_text)
                
                model_info = {
                    'action': 'model_normalized',
                    'model_used': True,
                    'model_response_summary': 'XML标签移除完成',
                    'confidence': response.get('confidence', 0.0),
                    'original_length': response.get('original_length', len(sql_text)),
                    'processed_length': response.get('processed_length', len(processed_sql))
                }
                
                self.logger.info(f"大模型XML标签移除成功: 原始长度={model_info['original_length']}, 处理后长度={model_info['processed_length']}")
                return processed_sql, model_info
            else:
                error_msg = response.get('error', '未知错误')
                self.logger.warning(f"大模型XML标签移除失败: {error_msg}")
                raise Exception(f"大模型处理失败: {error_msg}")
                
        except Exception as e:
            self.logger.warning(f"调用大模型XML标签移除API时发生错误: {str(e)}")
            raise
    
    def _build_model_prompt(self, sql_text: str, mode: str) -> str:
        """
        构建大模型提示
        
        Args:
            sql_text: 原始SQL语句
            mode: 处理模式
            
        Returns:
            大模型提示文本
        """
        # 构建清晰的指令
        instructions = []
        instructions.append("请将以下包含XML标签的SQL语句转换为标准SQL格式。")
        
        if mode == "normalize":
            instructions.append("要求：移除所有的XML标签（如<select>, <insert>, <update>, <delete>, <query>等），但保留标签内的SQL内容。")
            instructions.append("注意：保留SQL注释、参数占位符（如#{id}）和SQL语句的原始格式。")
        elif mode == "extract":
            instructions.append("要求：提取SQL内容，移除整个XML标签及其内容中不相关的部分。")
            instructions.append("注意：只保留有效的SQL语句部分。")
        
        instructions.append("")
        instructions.append("处理规则：")
        instructions.append("1. 移除所有XML标签，包括开标签、闭标签和自闭合标签")
        instructions.append("2. 处理CDATA块：移除<![CDATA[ 和 ]]>标记，保留其中的内容")
        instructions.append("3. 移除XML标签属性（如<sql type='query'>中的type='query'）")
        instructions.append("4. 处理嵌套标签（如<query><select>...</select></query>）")
        instructions.append("5. 保留SQL语句的完整性，不要修改SQL语法")
        instructions.append("6. 输出中只包含处理后的SQL语句，不要包含解释或额外文本")
        instructions.append("")
        instructions.append("需要处理的SQL语句：")
        instructions.append(f"```sql")
        instructions.append(sql_text)
        instructions.append(f"```")
        instructions.append("")
        instructions.append("请直接输出处理后的SQL语句，不要包含任何其他内容。")
        
        return "\n".join(instructions)
    
    def _parse_model_response(self, response: Dict[str, Any], original_sql: str) -> Dict[str, Any]:
        """
        解析大模型响应
        
        Args:
            response: 大模型响应
            original_sql: 原始SQL语句
            
        Returns:
            解析后的结果
        """
        result = {
            'processed_sql': original_sql,  # 默认使用原始SQL
            'summary': '模型处理失败',
            'confidence': 0.0
        }
        
        try:
            # 从响应中提取文本
            response_text = self._extract_response_text(response)
            
            if response_text:
                # 清理响应文本
                cleaned_sql = self._clean_model_response(response_text)
                
                # 检查处理后的SQL是否有效
                if self._is_valid_sql_result(cleaned_sql, original_sql):
                    result['processed_sql'] = cleaned_sql
                    result['summary'] = '模型处理成功'
                    result['confidence'] = self._calculate_confidence(cleaned_sql, original_sql)
                else:
                    self.logger.warning(f"模型返回的SQL无效: {cleaned_sql[:100]}...")
        
        except Exception as e:
            self.logger.error(f"解析模型响应失败: {str(e)}")
        
        return result
    
    def _extract_response_text(self, response: Dict[str, Any]) -> str:
        """从大模型响应中提取文本"""
        # 尝试从多个可能的位置提取文本
        text_candidates = []
        
        # 1. 从raw_response.RSP_BODY.answer提取
        if 'raw_response' in response:
            raw_response = response.get('raw_response', {})
            if isinstance(raw_response, dict) and 'RSP_BODY' in raw_response:
                rsp_body = raw_response.get('RSP_BODY', {})
                if isinstance(rsp_body, dict) and 'answer' in rsp_body:
                    answer = rsp_body.get('answer', '')
                    text_candidates.append(str(answer))
        
        # 2. 从analysis_result提取
        if 'analysis_result' in response:
            analysis_result = response.get('analysis_result', {})
            if isinstance(analysis_result, dict):
                # 尝试提取文本字段
                for field in ['processed_sql', 'result', 'answer', 'text']:
                    if field in analysis_result:
                        text_candidates.append(str(analysis_result[field]))
        
        # 3. 从suggestions提取（如果其他方式都失败）
        if 'suggestions' in response:
            suggestions = response.get('suggestions', [])
            if isinstance(suggestions, list) and suggestions:
                text_candidates.append(' '.join([str(s) for s in suggestions]))
        
        # 选择最有可能的文本
        for text in text_candidates:
            if text and len(text.strip()) > 0:
                return text.strip()
        
        return ""
    
    def _clean_model_response(self, text: str) -> str:
        """清理大模型返回的文本"""
        if not text:
            return ""
        
        # 移除代码块标记
        text = re.sub(r'```[\w]*\s*', '', text)
        text = re.sub(r'```', '', text)
        
        # 移除可能的XML标签（如果模型没有完全移除）
        text = self._remove_xml_tags_simple(text)
        
        # 移除首尾空白
        text = text.strip()
        
        return text
    
    def _is_valid_sql_result(self, processed_sql: str, original_sql: str) -> bool:
        """检查处理后的SQL是否有效"""
        if not processed_sql or not processed_sql.strip():
            return False
        
        # 检查长度是否合理（处理后不应比原始长度大很多）
        if len(processed_sql) > len(original_sql) * 2:
            self.logger.warning(f"处理后的SQL过长: {len(processed_sql)} > {len(original_sql) * 2}")
            return False
        
        # 检查是否仍然包含明显的XML标签
        if self._contains_xml_tags_regex(processed_sql):
            self.logger.warning("处理后的SQL仍然包含XML标签")
            return False
        
        # 检查是否包含有效的SQL关键字
        sql_keywords = ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'CREATE', 'ALTER', 'DROP', 'FROM', 'WHERE', 'SET']
        sql_upper = processed_sql.upper()
        has_sql_keyword = any(keyword in sql_upper for keyword in sql_keywords)
        
        if not has_sql_keyword:
            self.logger.warning("处理后的SQL不包含有效的SQL关键字")
            return False
        
        return True
    
    def _calculate_confidence(self, processed_sql: str, original_sql: str) -> float:
        """计算处理结果的置信度"""
        # 基于多个因素计算置信度
        confidence = 1.0
        
        # 1. 检查是否移除了XML标签
        if self._contains_xml_tags_regex(processed_sql):
            confidence *= 0.3
        
        # 2. 检查长度变化是否合理
        original_len = len(original_sql)
        processed_len = len(processed_sql)
        
        if original_len > 0:
            length_ratio = processed_len / original_len
            if length_ratio < 0.3 or length_ratio > 1.5:
                confidence *= 0.5
            elif 0.7 <= length_ratio <= 1.2:
                confidence *= 1.2  # 奖励合理的长度比例
        
        # 3. 检查是否包含SQL关键字
        sql_keywords = ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'CREATE', 'ALTER', 'DROP']
        sql_upper = processed_sql.upper()
        keyword_count = sum(1 for keyword in sql_keywords if keyword in sql_upper)
        if keyword_count > 0:
            confidence *= (1.0 + 0.1 * keyword_count)
        
        # 确保置信度在0-1之间
        return max(0.0, min(1.0, confidence))
    
    def _validate_model_result(self, processed_sql: str, original_sql: str) -> bool:
        """验证大模型处理结果"""
        return self._is_valid_sql_result(processed_sql, original_sql)
    
    def _contains_xml_tags_regex(self, sql_text: str) -> bool:
        """使用正则表达式检查是否包含XML标签"""
        if not sql_text or not sql_text.strip():
            return False
        
        xml_patterns = [
            r'<[^>]+>',  # 基本XML标签
            r'<!\[CDATA\[',  # CDATA标记
        ]
        
        for pattern in xml_patterns:
            if re.search(pattern, sql_text):
                return True
        
        return False
    
    def _remove_xml_tags_regex(self, sql_text: str, mode: str, info: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        """使用正则表达式移除XML标签（回退方法）"""
        keep_content = (mode != "extract")
        
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
            result = re.sub(r'<[^>]+>.*?</[^>]+>', '', result, flags=re.DOTALL)
            result = re.sub(r'<[^>]+/>', '', result)
        
        # 压缩多余空格
        result = re.sub(r'\s+', ' ', result).strip()
        
        # 更新信息
        info['action'] = 'regex_normalized' if keep_content else 'regex_extracted'
        info['processed_preview'] = result[:100] + ('...' if len(result) > 100 else '')
        info['processed_length'] = len(result)
        
        return result, info
    
    def _remove_xml_tags_simple(self, text: str) -> str:
        """简单的XML标签移除（用于清理大模型响应）"""
        if not text:
            return text
        
        result = text
        # 移除XML标签
        result = re.sub(r'<[^>]+>', ' ', result)
        # 移除CDATA标记
        result = re.sub(r'<!\[CDATA\[', '', result)
        result = re.sub(r'\]\]>', '', result)
        # 压缩空白
        result = re.sub(r'\s+', ' ', result).strip()
        
        return result


# 便捷函数
def remove_xml_tags_with_model(sql_text: str, config_manager=None, logger=None, mode: str = "normalize") -> Tuple[str, Dict[str, Any]]:
    """
    使用大模型移除XML标签的便捷函数
    
    Args:
        sql_text: SQL语句文本
        config_manager: 配置管理器
        logger: 日志记录器
        mode: 处理模式
        
    Returns:
        (处理后的SQL, 处理信息)
    """
    remover = XmlTagRemover(config_manager, logger)
    return remover.remove_xml_tags_with_model(sql_text, mode)


if __name__ == "__main__":
    """测试XML标签移除器"""
    
    test_cases = [
        ("<select>SELECT * FROM users</select>", "带select标签"),
        ("<query><select>SELECT name FROM users</select></query>", "嵌套标签"),
        ("<select><![CDATA[SELECT * FROM users]]></select>", "带CDATA"),
        ("<sql type=\"query\"><select>SELECT * FROM users WHERE id = #{id}</select></sql>", "带属性和参数"),
    ]
    
    print("大模型XML标签移除器测试")
    print("=" * 80)
    
    # 由于没有实际配置管理器，只能测试正则表达式回退
    remover = XmlTagRemover()
    
    for sql, description in test_cases:
        print(f"\n测试: {description}")
        print(f"原始SQL: {sql[:60]}...")
        
        # 检查是否包含XML标签
        has_xml = remover._contains_xml_tags_regex(sql)
        print(f"包含XML标签: {has_xml}")
        
        if has_xml:
            # 使用正则表达式处理
            processed_sql, info = remover._remove_xml_tags_regex(sql, "normalize", {})
            print(f"处理后SQL: {processed_sql[:60]}...")
            print(f"处理信息: {info.get('action', 'unknown')}")
        else:
            print("无需处理")
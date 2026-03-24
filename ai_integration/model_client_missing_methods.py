#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ModelClient缺失方法补全
"""

import re
import json
from typing import Dict, Any, List


def _extract_all_suggestions(self, response_data: Dict[str, Any], answer_data: Dict[str, Any] = None) -> List[str]:
    """
    从多个可能的位置提取建议
    
    Args:
        response_data: 响应数据
        answer_data: answer字段数据
        
    Returns:
        提取的建议列表
    """
    suggestions = []
    
    try:
        # 从response_data中提取
        if response_data:
            # 检查是否有suggestions字段
            if 'suggestions' in response_data and isinstance(response_data['suggestions'], list):
                suggestions.extend(response_data['suggestions'])
            
            # 检查是否有建议字段
            suggestion_fields = ['建议', 'recommendations', 'advice', '优化建议']
            for field in suggestion_fields:
                if field in response_data:
                    value = response_data[field]
                    if isinstance(value, list):
                        suggestions.extend(value)
                    elif isinstance(value, str):
                        # 如果是字符串，尝试解析为列表
                        try:
                            parsed = json.loads(value)
                            if isinstance(parsed, list):
                                suggestions.extend(parsed)
                        except:
                            # 如果不是JSON，作为单个建议
                            suggestions.append(value)
        
        # 从answer_data中提取
        if answer_data:
            # 检查是否有建议字段
            if 'suggestions' in answer_data and isinstance(answer_data['suggestions'], list):
                suggestions.extend(answer_data['suggestions'])
            
            # 检查规范违反详情中的建议
            if '规范检查结果' in answer_data:
                check_result = answer_data['规范检查结果']
                if isinstance(check_result, dict) and 'violations' in check_result:
                    for violation in check_result['violations']:
                        if isinstance(violation, dict) and 'suggestion' in violation:
                            suggestions.append(violation['suggestion'])
        
        # 去重和清理
        unique_suggestions = []
        seen = set()
        for suggestion in suggestions:
            if isinstance(suggestion, str):
                suggestion_text = suggestion.strip()
                if suggestion_text and suggestion_text not in seen:
                    seen.add(suggestion_text)
                    unique_suggestions.append(suggestion_text)
        
        return unique_suggestions
        
    except Exception as e:
        self.logger.warning(f"提取所有建议时发生错误: {str(e)}")
        return []


def _extract_all_fields(self, response_data: Dict[str, Any], answer_data: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    提取其他字段
    
    Args:
        response_data: 响应数据
        answer_data: answer字段数据
        
    Returns:
        提取的字段字典
    """
    extracted_fields = {}
    
    try:
        # 从response_data中提取
        if response_data:
            # 提取可能的字段
            fields_to_extract = ['sql_type', 'score', 'summary', 'detailed_analysis']
            for field in fields_to_extract:
                if field in response_data:
                    extracted_fields[field] = response_data[field]
        
        # 从answer_data中提取
        if answer_data:
            # 提取SQL类型
            if 'SQL类型' in answer_data:
                extracted_fields['sql_type'] = answer_data['SQL类型']
            
            # 提取规范检查结果
            if '规范检查结果' in answer_data:
                check_result = answer_data['规范检查结果']
                extracted_fields['规范检查结果'] = check_result
                
                # 提取合规评分
                if 'compliance_score' in check_result:
                    extracted_fields['score'] = check_result['compliance_score']
                
                # 提取总结
                if 'summary' in check_result:
                    extracted_fields['summary'] = check_result['summary']
            
            # 提取其他字段
            other_fields = ['summary', 'score', 'detailed_analysis']
            for field in other_fields:
                if field in answer_data:
                    extracted_fields[field] = answer_data[field]
        
        # 确保有SQL类型
        if 'sql_type' not in extracted_fields:
            extracted_fields['sql_type'] = '未知'
        
        # 确保有评分
        if 'score' not in extracted_fields:
            extracted_fields['score'] = 0.0
        
        # 确保有总结
        if 'summary' not in extracted_fields:
            extracted_fields['summary'] = '未提供总结'
        
        return extracted_fields
        
    except Exception as e:
        self.logger.warning(f"提取所有字段时发生错误: {str(e)}")
        return {
            'sql_type': '未知',
            'score': 0.0,
            'summary': '字段提取失败',
            'detailed_analysis': '字段提取失败'
        }


def _deep_clean_response_text(self, response_text: str) -> str:
    """
    多层清理响应文本
    
    Args:
        response_text: 响应文本
        
    Returns:
        清理后的文本
    """
    if not response_text:
        return ""
    
    cleaned = response_text
    
    # 1. 移除多余的空白字符
    cleaned = re.sub(r'\s+', ' ', cleaned)
    
    # 2. 移除多余的引号
    cleaned = cleaned.replace('\"\"', '"')
    cleaned = cleaned.replace("\'\'", "'")
    
    # 3. 修复常见的JSON格式问题
    # 修复缺少逗号的情况
    cleaned = re.sub(r'([}\]"])\s*"', r'\1, "', cleaned)
    
    # 修复多余的逗号
    cleaned = re.sub(r',\s*([}\]])', r'\1', cleaned)
    
    # 4. 移除XML标签残留
    cleaned = re.sub(r'<[^>]+>', '', cleaned)
    
    # 5. 移除控制字符
    cleaned = ''.join(ch for ch in cleaned if ord(ch) >= 32 or ch in '\n\r\t')
    
    return cleaned.strip()


def _fix_common_format_issues(self, response_text: str) -> str:
    """
    修复常见格式问题
    
    Args:
        response_text: 响应文本
        
    Returns:
        修复后的文本
    """
    if not response_text:
        return ""
    
    fixed = response_text
    
    # 1. 修复RSP_BODY格式问题
    # 常见的格式：{"RSP_BODY": {"answer": "..."}} 但有时会缺少引号
    if 'RSP_BODY' in fixed and 'answer' in fixed:
        # 确保RSP_BODY是有效的JSON格式
        pattern = r'{\s*"RSP_BODY"\s*:\s*([^}]+)}'
        match = re.search(pattern, fixed)
        if match:
            body_content = match.group(1)
            # 尝试修复缺少引号的情况
            if '"answer":' in body_content:
                # 确保answer值有引号
                answer_pattern = r'"answer"\s*:\s*([^,}]+)'
                answer_match = re.search(answer_pattern, body_content)
                if answer_match and not (answer_match.group(1).startswith('"') and answer_match.group(1).endswith('"')):
                    # 添加引号
                    body_content = re.sub(answer_pattern, r'"answer": "' + answer_match.group(1) + '"', body_content)
                    fixed = re.sub(pattern, r'{"RSP_BODY": ' + body_content + '}', fixed)
    
    # 2. 修复转义字符
    fixed = fixed.replace('\\"', '"')
    fixed = fixed.replace('\\n', '\n')
    fixed = fixed.replace('\\r', '\r')
    fixed = fixed.replace('\\t', '\t')
    
    # 3. 修复双重引号
    fixed = fixed.replace('""', '"')
    
    return fixed


def _validate_processed_sql(self, processed_sql: str, original_sql: str) -> bool:
    """
    验证处理后的SQL
    
    Args:
        processed_sql: 处理后的SQL
        original_sql: 原始SQL
        
    Returns:
        是否有效
    """
    if not processed_sql:
        self.logger.warning("处理后的SQL为空")
        return False
    
    # 1. 检查长度
    if len(processed_sql) < 5:
        self.logger.warning(f"处理后的SQL太短: {processed_sql}")
        return False
    
    # 2. 检查是否包含SQL关键字
    sql_keywords = ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'CREATE', 'ALTER', 'DROP']
    if not any(keyword in processed_sql.upper() for keyword in sql_keywords):
        self.logger.warning(f"处理后的SQL不包含SQL关键字: {processed_sql}")
        return False
    
    # 3. 检查括号平衡
    open_paren = processed_sql.count('(')
    close_paren = processed_sql.count(')')
    if open_paren != close_paren:
        self.logger.warning(f"括号不平衡: 开括号={open_paren}, 闭括号={close_paren}")
        # 如果相差不大，可以接受
        if abs(open_paren - close_paren) > 2:
            return False
    
    # 4. 检查XML标签是否被移除
    if '<' in processed_sql and '>' in processed_sql:
        # 可能还有XML标签残留
        xml_tags = re.findall(r'<[^>]+>', processed_sql)
        if xml_tags:
            self.logger.warning(f"仍有XML标签残留: {xml_tags}")
            return False
    
    return True


def _calculate_xml_removal_confidence(self, processed_sql: str, original_sql: str) -> float:
    """
    计算XML移除置信度
    
    Args:
        processed_sql: 处理后的SQL
        original_sql: 原始SQL
        
    Returns:
        置信度 (0-100)
    """
    if not processed_sql or not original_sql:
        return 0.0
    
    confidence = 100.0
    
    # 1. 长度比 - 处理后的SQL不应该太短
    processed_len = len(processed_sql)
    original_len = len(original_sql)
    length_ratio = processed_len / original_len if original_len > 0 else 0
    
    if length_ratio < 0.3:
        confidence -= 40  # 太短，扣分
    elif length_ratio < 0.5:
        confidence -= 20  # 有点短
    elif length_ratio > 2.0:
        confidence -= 30  # 太长，可能有问题
    
    # 2. XML标签移除
    original_xml_tags = len(re.findall(r'<[^>]+>', original_sql))
    processed_xml_tags = len(re.findall(r'<[^>]+>', processed_sql))
    
    if processed_xml_tags > 0:
        # 仍有XML标签残留
        confidence -= processed_xml_tags * 10
    
    # 3. SQL关键字保留
    sql_keywords = ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'CREATE', 'ALTER', 'DROP', 'FROM', 'WHERE', 'SET', 'VALUES']
    original_keywords = sum(1 for keyword in sql_keywords if keyword in original_sql.upper())
    processed_keywords = sum(1 for keyword in sql_keywords if keyword in processed_sql.upper())
    
    if processed_keywords < original_keywords * 0.5:
        confidence -= 20  # 丢失太多SQL关键字
    
    # 4. 括号平衡
    open_paren = processed_sql.count('(')
    close_paren = processed_sql.count(')')
    if open_paren != close_paren:
        confidence -= abs(open_paren - close_paren) * 5
    
    # 确保置信度在0-100之间
    confidence = max(0.0, min(100.0, confidence))
    
    return round(confidence, 1)
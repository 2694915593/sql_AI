#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
结果处理器模块
负责处理分析结果并存储到数据库
"""

import json
from typing import Dict, Any, List, Optional
from utils.logger import LogMixin
from data_collector.sql_extractor import SQLExtractor


class ResultProcessor(LogMixin):
    """结果处理器"""
    
    def __init__(self, config_manager, logger=None):
        """
        初始化结果处理器
        
        Args:
            config_manager: 配置管理器
            logger: 日志记录器
        """
        self.config_manager = config_manager
        
        if logger:
            self.set_logger(logger)
        
        # 初始化SQL提取器用于更新状态
        self.sql_extractor = SQLExtractor(config_manager, logger)
        
        self.logger.info("结果处理器初始化完成")
    
    def process_result(self, sql_id: int, analysis_result: Dict[str, Any], 
                      metadata: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        处理分析结果
        
        Args:
            sql_id: SQL记录ID
            analysis_result: 分析结果
            metadata: 表元数据
            
        Returns:
            处理后的结果
        """
        try:
            self.logger.info(f"开始处理SQL ID {sql_id} 的分析结果")
            
            # 检查分析结果是否成功
            if not analysis_result.get('success', False):
                error_message = analysis_result.get('error', '分析失败')
                self.update_error_status(sql_id, error_message)
                return {
                    'success': False,
                    'sql_id': sql_id,
                    'error': error_message
                }
            
            # 准备存储数据
            storage_data = self._prepare_storage_data(analysis_result, metadata)
            
            # 存储分析结果
            success = self._store_analysis_result(sql_id, storage_data)
            
            if success:
                # 更新状态为已分析
                self.sql_extractor.update_analysis_status(sql_id, 'analyzed')
                
                result = {
                    'success': True,
                    'sql_id': sql_id,
                    'score': analysis_result.get('score', 0),
                    'suggestion_count': len(analysis_result.get('suggestions', [])),
                    'storage_success': True
                }
                
                self.logger.info(f"SQL ID {sql_id} 分析结果处理完成，评分: {result['score']}")
                return result
            else:
                error_message = "存储分析结果失败"
                self.update_error_status(sql_id, error_message)
                return {
                    'success': False,
                    'sql_id': sql_id,
                    'error': error_message
                }
                
        except Exception as e:
            error_message = f"处理分析结果时发生错误: {str(e)}"
            self.logger.error(error_message, exc_info=True)
            self.update_error_status(sql_id, error_message)
            return {
                'success': False,
                'sql_id': sql_id,
                'error': error_message
            }
    
    def _prepare_storage_data(self, analysis_result: Dict[str, Any], 
                             metadata: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        准备存储数据
        
        Args:
            analysis_result: 分析结果
            metadata: 表元数据
            
        Returns:
            准备存储的数据
        """
        # 提取关键信息
        raw_result = analysis_result.get('analysis_result', {})
        suggestions = analysis_result.get('suggestions', [])
        score = analysis_result.get('score', 0)
        
        # 获取SQL类型
        sql_type = analysis_result.get('sql_type', '未知')
        if sql_type == 'UNKNOWN':
            sql_type = '未知'
        
        # 处理建议
        cleaned_suggestions = self._clean_suggestions(suggestions)
        
        # 从raw_result（即AI模型的analysis_result）中提取风险评估和修改建议
        # 注意：AI模型返回的数据结构在raw_result中
        if isinstance(raw_result, dict):
            # 从raw_result中直接提取风险评估
            risk_assessment = raw_result.get('风险评估', {})
            # 从raw_result中直接提取修改建议
            modification_suggestions = raw_result.get('修改建议', {})
            # 从raw_result中提取分析摘要
            analysis_summary = raw_result.get('分析摘要', '')
        else:
            # 如果raw_result不是字典，使用默认值
            risk_assessment = {}
            modification_suggestions = {}
            analysis_summary = ''
        
        # 如果从raw_result中提取到了分析摘要，使用它作为详细分析
        if analysis_summary:
            detailed_analysis = analysis_summary
        else:
            # 否则使用旧的提取方法
            summary = analysis_result.get('summary', '')
            if summary:
                detailed_analysis = summary
            else:
                detailed_analysis = self._extract_detailed_analysis(raw_result)
        
        # 构建新的JSON格式
        storage_data = self._build_new_json_format(
            suggestions=cleaned_suggestions,
            sql_type=sql_type,
            detailed_analysis=detailed_analysis,
            score=score,
            analysis_result=analysis_result,
            metadata=metadata,
            risk_assessment=risk_assessment,
            modification_suggestions=modification_suggestions
        )
        
        return storage_data
    
    def _extract_detailed_analysis(self, raw_result: Dict[str, Any]) -> str:
        """
        从原始结果中提取详细分析文本
        
        Args:
            raw_result: 原始分析结果
            
        Returns:
            提取的详细分析文本
        """
        try:
            # 如果包含detailed_analysis.RSP_BODY.answer，提取它
            if 'detailed_analysis' in raw_result:
                detailed = raw_result['detailed_analysis']
                if 'RSP_BODY' in detailed and 'answer' in detailed['RSP_BODY']:
                    answer_text = detailed['RSP_BODY']['answer']
                    # 清理文本：移除多余的引号和转义字符
                    if answer_text.startswith('"') and answer_text.endswith('"'):
                        answer_text = answer_text[1:-1]
                    answer_text = answer_text.replace('\\n', '\n').replace('\\"', '"')
                    return answer_text
            
            # 如果没有找到，尝试其他字段
            if 'analysis_text' in raw_result:
                return str(raw_result['analysis_text'])
            elif 'result' in raw_result:
                return str(raw_result['result'])
            elif 'data' in raw_result:
                return str(raw_result['data'])
            else:
                # 如果没有详细分析，返回空字符串
                return ""
                
        except Exception as e:
            self.logger.warning(f"提取详细分析时发生错误: {str(e)}")
            return ""
    
    def _clean_suggestions(self, suggestions: List[Any]) -> List[str]:
        """
        清理建议列表
        
        Args:
            suggestions: 原始建议列表
            
        Returns:
            清理后的建议列表
        """
        cleaned = []
        
        for suggestion in suggestions:
            if isinstance(suggestion, dict):
                # 如果是字典，尝试提取文本
                if 'text' in suggestion:
                    cleaned.append(str(suggestion['text']))
                elif 'suggestion' in suggestion:
                    cleaned.append(str(suggestion['suggestion']))
                elif 'recommendation' in suggestion:
                    cleaned.append(str(suggestion['recommendation']))
                else:
                    # 否则转换为字符串
                    cleaned.append(str(suggestion))
            elif isinstance(suggestion, str):
                # 清理字符串建议
                clean_suggestion = suggestion.strip()
                if clean_suggestion:
                    # 移除Markdown格式
                    clean_suggestion = clean_suggestion.replace('**', '').replace('`', '')
                    cleaned.append(clean_suggestion)
            else:
                # 其他类型转换为字符串
                cleaned.append(str(suggestion))
        
        # 去重
        unique_suggestions = []
        seen = set()
        for suggestion in cleaned:
            if suggestion and suggestion not in seen:
                seen.add(suggestion)
                unique_suggestions.append(suggestion)
        
        return unique_suggestions
    
    def _has_critical_issues(self, suggestions: List[Any]) -> bool:
        """检查是否有严重问题"""
        critical_keywords = ['严重', 'critical', 'error', 'bug', '错误', '致命', 'fatal']
        return self._check_suggestions_for_keywords(suggestions, critical_keywords)
    
    def _has_warnings(self, suggestions: List[Any]) -> bool:
        """检查是否有警告"""
        warning_keywords = ['警告', 'warning', '注意', 'caution', 'alert']
        return self._check_suggestions_for_keywords(suggestions, warning_keywords)
    
    def _has_optimization_suggestions(self, suggestions: List[Any]) -> bool:
        """检查是否有优化建议"""
        optimization_keywords = ['优化', 'optimization', 'improve', 'enhance', '建议', 'suggestion']
        return self._check_suggestions_for_keywords(suggestions, optimization_keywords)
    
    def _check_suggestions_for_keywords(self, suggestions: List[Any], keywords: List[str]) -> bool:
        """检查建议中是否包含关键词"""
        for suggestion in suggestions:
            if isinstance(suggestion, dict):
                suggestion_text = json.dumps(suggestion).lower()
            else:
                suggestion_text = str(suggestion).lower()
            
            for keyword in keywords:
                if keyword.lower() in suggestion_text:
                    return True
        return False
    
    def _create_metadata_summary(self, metadata: List[Dict[str, Any]]) -> Dict[str, Any]:
        """创建元数据摘要"""
        if not metadata:
            return {}
        
        summary = {
            'table_count': len(metadata),
            'total_rows': 0,
            'large_tables': 0,
            'total_columns': 0,
            'total_indexes': 0,
            'tables': []
        }
        
        for table_meta in metadata:
            summary['total_rows'] += table_meta.get('row_count', 0)
            if table_meta.get('is_large_table', False):
                summary['large_tables'] += 1
            summary['total_columns'] += len(table_meta.get('columns', []))
            summary['total_indexes'] += len(table_meta.get('indexes', []))
            
            table_summary = {
                'table_name': table_meta.get('table_name', ''),
                'row_count': table_meta.get('row_count', 0),
                'is_large_table': table_meta.get('is_large_table', False),
                'column_count': len(table_meta.get('columns', [])),
                'index_count': len(table_meta.get('indexes', [])),
                'has_primary_key': len(table_meta.get('primary_keys', [])) > 0
            }
            summary['tables'].append(table_summary)
        
        return summary
    
    def _categorize_suggestions(self, suggestions: List[Any]) -> Dict[str, List[Any]]:
        """分类建议"""
        categorized = {
            'performance': [],
            'security': [],
            'maintainability': [],
            'correctness': [],
            'other': []
        }
        
        for suggestion in suggestions:
            category = self._determine_suggestion_category(suggestion)
            categorized[category].append(suggestion)
        
        # 移除空类别
        return {k: v for k, v in categorized.items() if v}
    
    def _determine_suggestion_category(self, suggestion: Any) -> str:
        """确定建议类别"""
        if isinstance(suggestion, dict):
            suggestion_text = json.dumps(suggestion).lower()
        else:
            suggestion_text = str(suggestion).lower()
        
        # 性能相关关键词
        performance_keywords = ['性能', 'performance', '慢', 'slow', '索引', 'index', '查询', 'query', 
                               '优化', 'optimize', '执行计划', 'explain']
        # 安全相关关键词
        security_keywords = ['安全', 'security', '注入', 'injection', '权限', 'permission', '密码', 'password',
                            '加密', 'encrypt', '敏感', 'sensitive']
        # 可维护性相关关键词
        maintainability_keywords = ['维护', 'maintain', '可读', 'readable', '注释', 'comment', '命名', 'naming',
                                   '结构', 'structure', '规范', 'standard']
        # 正确性相关关键词
        correctness_keywords = ['错误', 'error', 'bug', '正确', 'correct', '逻辑', 'logic', '数据', 'data',
                               '一致', 'consistent', '完整', 'integrity']
        
        if any(keyword in suggestion_text for keyword in performance_keywords):
            return 'performance'
        elif any(keyword in suggestion_text for keyword in security_keywords):
            return 'security'
        elif any(keyword in suggestion_text for keyword in maintainability_keywords):
            return 'maintainability'
        elif any(keyword in suggestion_text for keyword in correctness_keywords):
            return 'correctness'
        else:
            return 'other'
    
    def _simplify_storage_data(self, sql_id: int, storage_data: Dict[str, Any]) -> str:
        """
        简化存储数据为四行文本格式 - 适配优化后的数据结构
        
        格式要求（按照用户反馈）：
        第一行：SQL原文（直接显示SQL文本，不加序号）
        第二行：违反内容（如：全表扫描、in索引失效）
        第三行：违反规范（如：索引列顺序不一致）
        第四行：修改建议（如：建议优化索引结构，优化内容如下）
        
        Args:
            sql_id: SQL记录ID
            storage_data: 优化后的存储数据
            
        Returns:
            简化后的四行文本
        """
        try:
            # 获取原始SQL文本 - 优先从storage_data中获取，如果不存在则查询数据库
            original_sql = self._get_original_sql(sql_id)
            if not original_sql:
                original_sql = f"SQL ID: {sql_id} (未获取到SQL原文)"
            
            # 第一行：SQL原文（直接显示SQL文本，不加序号）
            # 简化SQL文本：如果太长则截断
            max_sql_length = 300
            if len(original_sql) > max_sql_length:
                first_line = original_sql[:max_sql_length] + "..."
            else:
                first_line = original_sql
            
            # 第二行：违反内容（从关键问题中提取）
            # 格式要求：全表扫描、in索引失效
            key_issues = storage_data.get('key_issues', [])
            violation_contents = []
            
            for issue in key_issues[:5]:  # 最多取5个关键问题
                if isinstance(issue, dict):
                    category = issue.get('category', '')
                    severity = issue.get('severity', '')
                    # 只添加高风险和中风险的问题
                    if severity in ['高风险', '中风险'] and category:
                        violation_contents.append(category)
            
            # 如果没有关键问题，检查是否有规范违反
            if not violation_contents:
                normative_summary = storage_data.get('normative_summary', {})
                failed_angles = normative_summary.get('failed', [])
                violation_contents = failed_angles[:5]
            
            second_line = "违反内容："
            if violation_contents:
                # 使用中文顿号分隔，最多显示5个
                unique_violations = list(dict.fromkeys(violation_contents))[:5]
                second_line += "、".join(unique_violations)
                if len(violation_contents) > 5:
                    second_line += f" 等{len(violation_contents)}项"
            else:
                second_line += "无"
            
            # 第三行：违反规范（从规范性摘要中提取）
            # 格式要求：索引列顺序不一致
            normative_summary = storage_data.get('normative_summary', {})
            violation_rules = []
            
            # 从规范性摘要中提取未通过的角度
            failed_angles = normative_summary.get('failed', [])
            for angle in failed_angles[:3]:  # 最多取3个
                violation_rules.append(angle)
            
            # 如果没有规范性违反，从关键问题中提取
            if not violation_rules:
                for issue in key_issues[:3]:
                    if isinstance(issue, dict):
                        issue_type = issue.get('type', '')
                        if issue_type == '规范违反':
                            description = issue.get('description', '')
                            if description:
                                violation_rules.append(description)
            
            third_line = "违反规范："
            if violation_rules:
                unique_rules = list(dict.fromkeys(violation_rules))[:3]
                third_line += "、".join(unique_rules)
                if len(violation_rules) > 3:
                    third_line += f" 等{len(violation_rules)}条规范"
            else:
                third_line += "无"
            
            # 第四行：修改建议
            # 格式要求：建议优化索引结构，优化内容如下
            suggestions = storage_data.get('suggestions', [])
            optimized_sql = storage_data.get('optimized_sql', '')
            
            fourth_line = "修改建议："
            
            # 首先尝试从优化SQL中获取具体的优化内容
            if optimized_sql:
                # 清理优化SQL：移除注释和多余空格
                clean_optimized_sql = optimized_sql.strip()
                # 如果包含注释，提取注释后的部分
                if clean_optimized_sql.startswith("--"):
                    # 提取注释行后的SQL
                    lines = clean_optimized_sql.split('\n')
                    if len(lines) > 1:
                        sql_part = lines[1].strip()
                    else:
                        sql_part = clean_optimized_sql
                else:
                    sql_part = clean_optimized_sql
                
                if len(sql_part) > 80:
                    fourth_line += f"优化SQL：{sql_part[:80]}..."
                else:
                    fourth_line += f"优化SQL：{sql_part}"
            
            # 如果没有优化SQL，使用通用建议
            if fourth_line == "修改建议：":
                if suggestions:
                    # 取第一条建议作为主要修改建议
                    main_suggestion = suggestions[0]
                    # 清理建议文本
                    clean_suggestion = main_suggestion.strip()
                    if len(clean_suggestion) > 80:
                        fourth_line += f"{clean_suggestion[:80]}..."
                    else:
                        fourth_line += clean_suggestion
                    
                    # 如果有多个建议，添加数量提示
                    if len(suggestions) > 1:
                        fourth_line += f"（共{len(suggestions)}条建议）"
                else:
                    fourth_line += "无"
            
            # 组合四行文本，每行最大长度限制
            max_line_length = 500
            lines = [first_line, second_line, third_line, fourth_line]
            simplified_text = "\n".join([line[:max_line_length] for line in lines])
            
            return simplified_text
            
        except Exception as e:
            self.logger.warning(f"简化存储数据时发生错误: {str(e)}")
            # 返回默认简化格式
            return f"SQL ID: {sql_id}\n违反内容：数据处理失败\n违反规范：请查看详细分析\n修改建议：检查代码逻辑"
    
    def _get_original_sql(self, sql_id: int) -> str:
        """
        获取原始SQL文本
        
        Args:
            sql_id: SQL记录ID
            
        Returns:
            原始SQL文本
        """
        try:
            # 查询数据库获取原始SQL
            query = """
                SELECT SQL_TEXT 
                FROM AM_SQLLINE_INFO 
                WHERE ID = %s
            """
            result = self.sql_extractor.source_db.fetch_one(query, (sql_id,))
            
            if result and result.get('SQL_TEXT'):
                return result['SQL_TEXT']
            else:
                return f"SQL ID: {sql_id}"
                
        except Exception as e:
            self.logger.warning(f"获取原始SQL时发生错误: {str(e)}")
            return f"SQL ID: {sql_id}"

    def _store_analysis_result(self, sql_id: int, storage_data: Dict[str, Any]) -> bool:
        """
        存储分析结果到数据库
        
        Args:
            sql_id: SQL记录ID
            storage_data: 存储数据
            
        Returns:
            是否成功
        """
        try:
            # 生成简化文本内容
            simplified_text = self._simplify_storage_data(sql_id, storage_data)
            
            # 同时保留完整的JSON数据和简化文本
            json_data = json.dumps(storage_data, ensure_ascii=False, indent=2)
            
            # 更新数据库记录 - 同时存储简化和完整数据
            data = {
                'analysis_result': json_data,
                'simplified_result': simplified_text,  # 新增简化结果字段
                'analysis_status': 'analyzed',
                'analysis_time': 'NOW()'  # 使用MySQL的NOW()函数
            }
            
            # 构建更新语句 - 注意：实际表字段名是ID（大写）
            set_items = []
            values = []
            
            for key, value in data.items():
                if value == 'NOW()':
                    # 对于NOW()函数，直接使用函数调用而不是参数
                    set_items.append(f"{key} = NOW()")
                else:
                    set_items.append(f"{key} = %s")
                    values.append(value)
            
            values.append(sql_id)
            set_clause = ', '.join(set_items)
            query = f"UPDATE AM_SQLLINE_INFO SET {set_clause} WHERE ID = %s"
            
            affected = self.sql_extractor.source_db.execute(query, tuple(values))
            
            if affected > 0:
                self.logger.info(f"SQL ID {sql_id} 分析结果存储成功")
                self.logger.debug(f"简化存储内容: {simplified_text}")
                
                # 可选：存储详细分析结果到详情表
                self._store_detailed_analysis(sql_id, storage_data)
                
                return True
            else:
                self.logger.warning(f"SQL ID {sql_id} 分析结果存储失败，未找到记录")
                return False
                
        except Exception as e:
            self.logger.error(f"存储分析结果时发生错误: {str(e)}", exc_info=True)
            return False
    
    def _store_detailed_analysis(self, sql_id: int, storage_data: Dict[str, Any]) -> None:
        """存储详细分析结果到详情表（可选）"""
        try:
            # 检查是否存在analysis_details表
            # 这里只是示例，实际实现可能需要检查表是否存在
            pass
            
        except Exception as e:
            self.logger.warning(f"存储详细分析结果时发生错误: {str(e)}")
            # 不影响主流程
    
    def update_error_status(self, sql_id: int, error_message: str) -> bool:
        """
        更新错误状态
        
        Args:
            sql_id: SQL记录ID
            error_message: 错误信息
            
        Returns:
            是否成功
        """
        try:
            success = self.sql_extractor.update_analysis_status(sql_id, 'failed', error_message)
            
            if success:
                self.logger.info(f"SQL ID {sql_id} 错误状态更新成功")
            else:
                self.logger.warning(f"SQL ID {sql_id} 错误状态更新失败")
            
            return success
            
        except Exception as e:
            self.logger.error(f"更新错误状态时发生错误: {str(e)}", exc_info=True)
            return False
    
    def get_analysis_result(self, sql_id: int) -> Optional[Dict[str, Any]]:
        """
        获取分析结果
        
        Args:
            sql_id: SQL记录ID
            
        Returns:
            分析结果
        """
        try:
            query = """
                SELECT 
                    ID as id,
                    SQLLINE as sql_text,
                    analysis_result,
                    analysis_status,
                    analysis_time,
                    error_message
                FROM am_solline_info 
                WHERE ID = %s
            """
            
            result = self.sql_extractor.source_db.fetch_one(query, (sql_id,))
            
            if result and result.get('analysis_result'):
                try:
                    analysis_data = json.loads(result['analysis_result'])
                    result['analysis_result'] = analysis_data
                except json.JSONDecodeError:
                    self.logger.warning(f"SQL ID {sql_id} 的分析结果JSON解析失败")
            
            return result
            
        except Exception as e:
            self.logger.error(f"获取分析结果时发生错误: {str(e)}", exc_info=True)
            return None
    
    def _extract_compliance_data(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        从分析结果中提取规范符合性数据
        
        Args:
            analysis_result: 分析结果
            
        Returns:
            规范符合性数据
        """
        compliance_data = {
            "规范符合度": 100.0,  # 默认值
            "规范违反详情": []
        }
        
        try:
            # 首先尝试从analysis_result中直接获取规范符合性数据
            if '规范符合性' in analysis_result:
                compliance_data = analysis_result['规范符合性']
                return compliance_data
            
            # 尝试从analysis_result的嵌套结构中获取
            if 'analysis_result' in analysis_result:
                deep_result = analysis_result['analysis_result']
                if isinstance(deep_result, dict) and '规范符合性' in deep_result:
                    compliance_data = deep_result['规范符合性']
                    return compliance_data
            
            # 尝试从原始响应中提取规范符合度
            if 'raw_response' in analysis_result:
                raw_response = analysis_result['raw_response']
                if isinstance(raw_response, dict):
                    # 检查是否有规范符合度字段
                    if '规范符合度' in raw_response:
                        compliance_data['规范符合度'] = float(raw_response['规范符合度'])
                    
                    # 检查是否有规范违反详情
                    if '规范违反详情' in raw_response:
                        compliance_data['规范违反详情'] = raw_response['规范违反详情']
            
            # 尝试从建议中提取规范违反信息
            suggestions = analysis_result.get('suggestions', [])
            for suggestion in suggestions:
                if isinstance(suggestion, str):
                    # 检查是否包含规范违反相关关键词
                    if any(keyword in suggestion.lower() for keyword in ['规范', '不符合', '违反', '违规']):
                        compliance_data['规范违反详情'].append({
                            "description": "通用规范检查",
                            "violation": suggestion,
                            "suggestion": "遵循相关SQL规范"
                        })
            
            # 如果没有规范违反详情，添加默认值
            if not compliance_data['规范违反详情']:
                compliance_data['规范违反详情'] = [
                    {
                        "description": "规范符合性检查",
                        "violation": "未发现明显的规范违反",
                        "suggestion": "继续保持良好的SQL编写习惯"
                    }
                ]
            
            # 根据规范违反数量调整规范符合度
            violation_count = len(compliance_data['规范违反详情'])
            if violation_count > 0:
                # 有违反则降低符合度
                compliance_data['规范符合度'] = max(60.0, 100.0 - (violation_count * 5.0))
            
        except Exception as e:
            self.logger.warning(f"提取规范符合性数据时发生错误: {str(e)}")
            # 使用默认值
        
        return compliance_data
    
    def _build_new_json_format(self, suggestions: List[str], sql_type: str,
                              detailed_analysis: str, score: int,
                              analysis_result: Dict[str, Any],
                              metadata: List[Dict[str, Any]],
                              risk_assessment: Optional[Dict[str, List[str]]] = None,
                              modification_suggestions: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        构建新的JSON存储格式 - 优化版本
        
        格式要求:
        {
            "summary": {
                "sql_type": "查询",
                "score": 8.5,
                "compliance_score": 85.5,
                "has_critical_issues": false,
                "suggestion_count": 3
            },
            "key_issues": [
                {
                    "type": "规范性评审",
                    "category": "全表扫描",
                    "severity": "中风险",
                    "description": "查询条件未使用索引",
                    "suggestion": "添加索引或优化查询条件"
                }
            ],
            "suggestions": ["建议1: 添加索引", "建议2: 使用参数化查询"],
            "normative_summary": {
                "total_angles": 15,
                "passed": 13,
                "failed": ["全表扫描", "索引设计"],
                "compliance_rate": 86.7
            },
            "optimized_sql": "SELECT id, name FROM users WHERE status = ?"
        }
        
        Args:
            suggestions: 建议列表
            sql_type: SQL类型
            detailed_analysis: 详细分析文本
            score: 综合评分
            analysis_result: 分析结果
            metadata: 表元数据
            risk_assessment: 从AI模型响应中提取的风险评估数据（可选）
            modification_suggestions: 从AI模型响应中提取的修改建议（可选）
            
        Returns:
            优化后的JSON格式数据
        """
        # 从详细分析中提取分析摘要
        analysis_summary = self._extract_analysis_summary(detailed_analysis)
        
        # 提取规范符合性数据
        compliance_data = self._extract_compliance_data(analysis_result)
        
        # 提取关键问题
        key_issues = self._extract_key_issues(suggestions, analysis_result)
        
        # 生成规范性摘要
        normative_summary = self._generate_normative_summary(suggestions, detailed_analysis)
        
        # 提取优化SQL
        optimized_sql = self._extract_optimized_sql(analysis_result)
        
        # 如果optimized_sql为空，尝试从modification_suggestions中获取
        if not optimized_sql and modification_suggestions:
            # 优先使用性能优化SQL，其次使用高风险问题SQL
            optimized_sql = modification_suggestions.get('性能优化SQL', '') or \
                           modification_suggestions.get('高风险问题SQL', '')
        
        # 构建优化后的JSON
        result_json = {
            "summary": {
                "sql_type": sql_type,
                "score": score,
                "compliance_score": compliance_data.get("规范符合度", 100.0),
                "has_critical_issues": len(key_issues) > 0,
                "suggestion_count": len(suggestions)
            },
            "key_issues": key_issues[:3],  # 最多3个关键问题
            "suggestions": suggestions[:5],  # 最多5条建议
            "normative_summary": normative_summary,
            "optimized_sql": optimized_sql
        }
        
        return result_json
    
    def _extract_analysis_summary(self, detailed_analysis: str) -> str:
        """
        从详细分析中提取分析摘要
        
        Args:
            detailed_analysis: 详细分析文本
            
        Returns:
            分析摘要
        """
        if not detailed_analysis:
            return "无详细分析内容"
        
        # 如果详细分析太长，截取前200字
        if len(detailed_analysis) > 200:
            # 找到最近的句子结束位置
            sentences = detailed_analysis.split('。')
            summary = sentences[0] + '。' if len(sentences) > 1 else detailed_analysis[:200]
            if len(summary) > 200:
                summary = summary[:197] + '...'
            return summary
        
        return detailed_analysis
    
    def _categorize_risk_issues(self, suggestions: List[str], 
                               metadata: List[Dict[str, Any]],
                               analysis_result: Dict[str, Any]) -> Dict[str, List[str]]:
        """
        分类风险问题
        
        Args:
            suggestions: 建议列表
            metadata: 表元数据
            analysis_result: 分析结果
            
        Returns:
            分类后的风险问题
        """
        risk_categories = {
            "高风险问题": [],
            "中风险问题": [],
            "低风险问题": []
        }
        
        # 高风险关键词
        high_risk_keywords = [
            'sql注入', '注入', 'injection', '安全漏洞', '安全风险',
            '无主键', '无索引', '大数据量', '性能瓶颈', '死锁',
            '事务隔离', '数据丢失', '数据不一致', '权限过大'
        ]
        
        # 中风险关键词
        medium_risk_keywords = [
            '性能问题', '查询慢', '索引缺失', '缺少索引',
            '表扫描', '全表扫描', '参数未转义', '未参数化',
            '缺少验证', '输入验证', '数据类型', '类型转换'
        ]
        
        # 低风险关键词
        low_risk_keywords = [
            '代码规范', '命名规范', '注释缺失', '可读性',
            '维护性', '最佳实践', '建议优化', '小优化'
        ]
        
        # 检查表元数据中的高风险问题
        for table_meta in metadata:
            # 检查是否无主键
            if not table_meta.get('primary_keys'):
                risk_categories["高风险问题"].append(f"表 {table_meta.get('table_name', '未知')} 无主键，可能导致数据完整性问题")
            
            # 检查是否为大表
            if table_meta.get('is_large_table', False):
                risk_categories["高风险问题"].append(f"表 {table_meta.get('table_name', '未知')} 数据量较大，可能导致性能瓶颈")
        
        # 分析建议并分类
        for suggestion in suggestions:
            suggestion_lower = suggestion.lower()
            
            # 检查高风险关键词
            if any(keyword in suggestion_lower for keyword in high_risk_keywords):
                if suggestion not in risk_categories["高风险问题"]:
                    risk_categories["高风险问题"].append(suggestion)
            
            # 检查中风险关键词
            elif any(keyword in suggestion_lower for keyword in medium_risk_keywords):
                if suggestion not in risk_categories["中风险问题"]:
                    risk_categories["中风险问题"].append(suggestion)
            
            # 检查低风险关键词
            elif any(keyword in suggestion_lower for keyword in low_risk_keywords):
                if suggestion not in risk_categories["低风险问题"]:
                    risk_categories["低风险问题"].append(suggestion)
            else:
                # 默认归类为低风险
                if suggestion not in risk_categories["低风险问题"]:
                    risk_categories["低风险问题"].append(suggestion)
        
        # 去除重复项
        for category in risk_categories:
            risk_categories[category] = list(set(risk_categories[category]))
        
        return risk_categories
    
    def _generate_high_risk_fixed_sql(self, original_sql: str, 
                                     high_risk_issues: List[str]) -> str:
        """
        生成高风险问题的修改SQL
        
        Args:
            original_sql: 原始SQL
            high_risk_issues: 高风险问题列表
            
        Returns:
            修改后的SQL建议
        """
        if not original_sql:
            return "无原始SQL，无法生成修改建议"
        
        if not high_risk_issues:
            return "无高风险问题，无需修改SQL"
        
        fixed_sql = original_sql
        
        # 根据高风险问题应用修改
        for issue in high_risk_issues:
            issue_lower = issue.lower()
            
            # 处理SQL注入问题
            if any(keyword in issue_lower for keyword in ['注入', 'injection', '参数未转义']):
                # 将#{参数}替换为?作为参数化查询示例
                import re
                fixed_sql = re.sub(r'#\{([^}]+)\}', '?', fixed_sql)
            
            # 处理性能问题
            if any(keyword in issue_lower for keyword in ['性能', '慢', '索引缺失']):
                # 添加查询优化提示
                fixed_sql = f"-- 建议：添加适当的索引以提高查询性能\n{fixed_sql}"
        
        # 如果SQL被修改，返回修改后的版本
        if fixed_sql != original_sql:
            return fixed_sql
        else:
            return "原始SQL已符合最佳实践，无需重大修改"

    def _extract_modification_suggestions_from_analysis(self, analysis_result: Dict[str, Any]) -> Dict[str, str]:
        """
        从AI分析结果中提取修改建议SQL
        
        Args:
            analysis_result: 分析结果
            
        Returns:
            修改建议字典，包含不同风险级别的SQL修改建议
        """
        modification_suggestions = {
            "高风险问题SQL": "",
            "中风险问题SQL": "",
            "低风险问题SQL": "",
            "性能优化SQL": ""
        }
        
        try:
            # 首先检查analysis_result中是否有直接字段
            if '高风险问题SQL' in analysis_result:
                modification_suggestions['高风险问题SQL'] = analysis_result['高风险问题SQL']
            if '中风险问题SQL' in analysis_result:
                modification_suggestions['中风险问题SQL'] = analysis_result['中风险问题SQL']
            if '低风险问题SQL' in analysis_result:
                modification_suggestions['低风险问题SQL'] = analysis_result['低风险问题SQL']
            if '性能优化SQL' in analysis_result:
                modification_suggestions['性能优化SQL'] = analysis_result['性能优化SQL']
            
            # 检查是否有modification_suggestions字段
            if 'modification_suggestions' in analysis_result:
                mod_suggestions = analysis_result['modification_suggestions']
                if isinstance(mod_suggestions, dict):
                    if '高风险问题SQL' in mod_suggestions and mod_suggestions['高风险问题SQL']:
                        modification_suggestions['高风险问题SQL'] = mod_suggestions['高风险问题SQL']
                    if '中风险问题SQL' in mod_suggestions and mod_suggestions['中风险问题SQL']:
                        modification_suggestions['中风险问题SQL'] = mod_suggestions['中风险问题SQL']
                    if '低风险问题SQL' in mod_suggestions and mod_suggestions['低风险问题SQL']:
                        modification_suggestions['低风险问题SQL'] = mod_suggestions['低风险问题SQL']
                    if '性能优化SQL' in mod_suggestions and mod_suggestions['性能优化SQL']:
                        modification_suggestions['性能优化SQL'] = mod_suggestions['性能优化SQL']
            
            # 检查是否有sql_modifications字段
            if 'sql_modifications' in analysis_result:
                sql_mods = analysis_result['sql_modifications']
                if isinstance(sql_mods, dict):
                    if 'high_risk_sql' in sql_mods and sql_mods['high_risk_sql']:
                        modification_suggestions['高风险问题SQL'] = sql_mods['high_risk_sql']
                    if 'medium_risk_sql' in sql_mods and sql_mods['medium_risk_sql']:
                        modification_suggestions['中风险问题SQL'] = sql_mods['medium_risk_sql']
                    if 'low_risk_sql' in sql_mods and sql_mods['low_risk_sql']:
                        modification_suggestions['低风险问题SQL'] = sql_mods['low_risk_sql']
                    if 'performance_sql' in sql_mods and sql_mods['performance_sql']:
                        modification_suggestions['性能优化SQL'] = sql_mods['performance_sql']
            
            # 检查analysis_result['analysis_result']中是否有修改建议（深层嵌套）
            if 'analysis_result' in analysis_result:
                deep_result = analysis_result['analysis_result']
                if isinstance(deep_result, dict):
                    # 检查深层分析结果中的修改建议
                    if '修改建议' in deep_result:
                        deep_suggestions = deep_result['修改建议']
                        if isinstance(deep_suggestions, dict):
                            if '高风险问题SQL' in deep_suggestions and deep_suggestions['高风险问题SQL']:
                                modification_suggestions['高风险问题SQL'] = deep_suggestions['高风险问题SQL']
                            if '中风险问题SQL' in deep_suggestions and deep_suggestions['中风险问题SQL']:
                                modification_suggestions['中风险问题SQL'] = deep_suggestions['中风险问题SQL']
                            if '低风险问题SQL' in deep_suggestions and deep_suggestions['低风险问题SQL']:
                                modification_suggestions['低风险问题SQL'] = deep_suggestions['低风险问题SQL']
                            if '性能优化SQL' in deep_suggestions and deep_suggestions['性能优化SQL']:
                                modification_suggestions['性能优化SQL'] = deep_suggestions['性能优化SQL']
                    
                    # 检查深层分析结果中的sql_modifications
                    if 'sql_modifications' in deep_result:
                        deep_sql_mods = deep_result['sql_modifications']
                        if isinstance(deep_sql_mods, dict):
                            if 'high_risk_sql' in deep_sql_mods and deep_sql_mods['high_risk_sql']:
                                modification_suggestions['高风险问题SQL'] = deep_sql_mods['high_risk_sql']
                            if 'medium_risk_sql' in deep_sql_mods and deep_sql_mods['medium_risk_sql']:
                                modification_suggestions['中风险问题SQL'] = deep_sql_mods['medium_risk_sql']
                            if 'low_risk_sql' in deep_sql_mods and deep_sql_mods['low_risk_sql']:
                                modification_suggestions['低风险问题SQL'] = deep_sql_mods['low_risk_sql']
                            if 'performance_sql' in deep_sql_mods and deep_sql_mods['performance_sql']:
                                modification_suggestions['性能优化SQL'] = deep_sql_mods['performance_sql']
                    
                    # 检查深层分析结果中的直接字段
                    if '高风险问题SQL' in deep_result:
                        modification_suggestions['高风险问题SQL'] = deep_result['高风险问题SQL']
                    if '中风险问题SQL' in deep_result:
                        modification_suggestions['中风险问题SQL'] = deep_result['中风险问题SQL']
                    if '低风险问题SQL' in deep_result:
                        modification_suggestions['低风险问题SQL'] = deep_result['低风险问题SQL']
                    if '性能优化SQL' in deep_result:
                        modification_suggestions['性能优化SQL'] = deep_result['性能优化SQL']
            
            # 清理结果：去除空值
            for key in list(modification_suggestions.keys()):
                if not modification_suggestions[key] or modification_suggestions[key].strip() == "":
                    modification_suggestions[key] = ""
            
            self.logger.info(f"从分析结果中提取修改建议：高风险SQL长度={len(modification_suggestions['高风险问题SQL'])}, "
                           f"中风险SQL长度={len(modification_suggestions['中风险问题SQL'])}, "
                           f"低风险SQL长度={len(modification_suggestions['低风险问题SQL'])}, "
                           f"性能优化SQL长度={len(modification_suggestions['性能优化SQL'])}")
            
        except Exception as e:
            self.logger.warning(f"提取修改建议时发生错误: {str(e)}")
        
        return modification_suggestions
    
    def _generate_normative_review(self, suggestions: List[str], detailed_analysis: str, 
                                  analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成规范性评审数据
        
        生成15个关键规范性角度的评审结果
        
        Args:
            suggestions: 建议列表
            detailed_analysis: 详细分析文本
            analysis_result: 分析结果
            
        Returns:
            规范性评审数据
        """
        normative_review = {}
        
        # 定义15个关键规范性角度及其描述
        normative_angles = {
            "修改列时加属性": {
                "description": "检查ALTER TABLE语句修改列时是否保留了原列的属性（如NOT NULL、DEFAULT、COMMENT等）",
                "keywords": ["修改列", "alter column", "列属性", "not null", "default", "comment"]
            },
            "in操作索引失效": {
                "description": "检查IN操作是否导致索引失效（特别是IN列表值过多时）",
                "keywords": ["in操作", "in索引", "索引失效", "in条件", "索引使用"]
            },
            "字符集问题": {
                "description": "检查字符集是否一致（表、字段、连接字符集），避免乱码和性能问题",
                "keywords": ["字符集", "charset", "编码", "utf8", "gbk", "乱码"]
            },
            "注释--问题": {
                "description": "检查SQL注释是否正确使用--格式（--后面必须有空格），避免注释错误解析",
                "keywords": ["注释", "--", "comment", "注释格式"]
            },
            "comment问题": {
                "description": "检查表和字段是否有合适的COMMENT注释，注释内容是否清晰明确",
                "keywords": ["comment", "注释", "表注释", "字段注释", "备注"]
            },
            "表参数问题": {
                "description": "检查表参数设置是否合理（如ENGINE、CHARSET、COLLATE、ROW_FORMAT等）",
                "keywords": ["表参数", "engine", "row_format", "参数设置", "表定义"]
            },
            "akm接入": {
                "description": "检查AKM（访问密钥管理）相关配置和接入问题，确保敏感信息安全",
                "keywords": ["akm", "接入", "密钥", "安全", "敏感信息"]
            },
            "analyze问题": {
                "description": "检查ANALYZE统计信息是否准确，是否需要手动更新统计信息",
                "keywords": ["analyze", "统计信息", "分析表", "统计更新"]
            },
            "dml与ddl之间休眠3秒": {
                "description": "检查DDL操作后是否等待足够时间（建议3秒）再执行DML，避免锁冲突",
                "keywords": ["dml", "ddl", "休眠", "sleep", "锁冲突", "等待"]
            },
            "隐式转换": {
                "description": "检查SQL语句中是否存在隐式类型转换，可能导致性能问题或数据错误",
                "keywords": ["隐式转换", "类型转换", "数据类型", "转换问题"]
            },
            "主键问题": {
                "description": "检查表是否有主键，主键设计是否合理（自增、业务主键等）",
                "keywords": ["主键", "primary key", "无主键", "主键设计"]
            },
            "索引设计": {
                "description": "检查索引设计是否合理（联合索引字段顺序、索引冗余、索引数量等）",
                "keywords": ["索引", "index", "索引设计", "联合索引", "索引冗余"]
            },
            "全表扫描": {
                "description": "检查SQL是否可能导致全表扫描，特别是大表的查询",
                "keywords": ["全表扫描", "全表查询", "性能问题", "扫描", "性能瓶颈"]
            },
            "表结构一致性": {
                "description": "检查涉及的表结构是否一致（如字段类型、长度、默认值等）",
                "keywords": ["表结构", "结构一致", "字段类型", "字段长度", "默认值"]
            },
            "唯一约束字段须添加not null": {
                "description": "检查唯一索引字段是否都有NOT NULL约束，确保数据完整性",
                "keywords": ["唯一约束", "unique", "not null", "约束", "数据完整性"]
            }
        }
        
        # 检查每个角度
        for angle_name, angle_info in normative_angles.items():
            status = "通过"
            details = "未发现相关问题"
            suggestion = "继续保持良好的SQL编写习惯"
            
            # 检查建议中是否有相关关键词
            has_issue = False
            issue_details = []
            
            for suggestion_text in suggestions:
                suggestion_lower = suggestion_text.lower()
                for keyword in angle_info["keywords"]:
                    if keyword.lower() in suggestion_lower:
                        has_issue = True
                        issue_details.append(f"建议中提到: {suggestion_text}")
                        break
            
            # 检查详细分析中是否有相关关键词
            if detailed_analysis:
                detailed_lower = detailed_analysis.lower()
                for keyword in angle_info["keywords"]:
                    if keyword.lower() in detailed_lower:
                        has_issue = True
                        issue_details.append(f"分析中提到: {keyword}")
            
            # 如果有问题，更新状态和详情
            if has_issue:
                status = "未通过"
                details = f"发现{angle_name}相关的问题: " + "; ".join(issue_details[:3])
                suggestion = f"请检查并修复{angle_name}相关的问题，确保符合SQL规范要求"
            
            # 构建角度评审结果
            normative_review[angle_name] = {
                "status": status,
                "description": angle_info["description"],
                "details": details,
                "suggestion": suggestion
            }
        
        # 过滤掉status为"通过"或"未涉及"的角度，只保留"未通过"的角度
        filtered_review = {}
        for angle_name, review_data in normative_review.items():
            if review_data.get("status") == "未通过":
                filtered_review[angle_name] = review_data
        
        return filtered_review
    def _generate_modification_suggestions(self, original_sql: str,
                                          risk_assessment: Dict[str, List[str]],
                                          suggestions: List[str]) -> Dict[str, str]:
        """
        生成修改建议SQL（备用方法）
        
        Args:
            original_sql: 原始SQL
            risk_assessment: 风险评估结果
            suggestions: 建议列表
            
        Returns:
            修改建议字典
        """
        modification_suggestions = {
            "高风险问题SQL": "",
            "中风险问题SQL": "",
            "低风险问题SQL": "",
            "性能优化SQL": ""
        }
        
        if not original_sql:
            return modification_suggestions
        
        # 生成高风险问题SQL
        high_risk_issues = risk_assessment.get('高风险问题', [])
        if high_risk_issues:
            modification_suggestions['高风险问题SQL'] = self._generate_high_risk_fixed_sql(original_sql, high_risk_issues)
        
        # 生成中风险问题SQL
        medium_risk_issues = risk_assessment.get('中风险问题', [])
        if medium_risk_issues:
            # 针对中风险问题，提供参数化查询示例
            import re
            medium_fixed_sql = original_sql
            # 将 #{param} 替换为 ? 作为参数化示例
            medium_fixed_sql = re.sub(r'#\{([^}]+)\}', '?', medium_fixed_sql)
            modification_suggestions['中风险问题SQL'] = f"-- 参数化查询示例（防止SQL注入）\n{medium_fixed_sql}"
        
        # 生成低风险问题SQL
        low_risk_issues = risk_assessment.get('低风险问题', [])
        if low_risk_issues:
            # 针对低风险问题，提供优化建议
            low_fixed_sql = original_sql
            # 添加索引建议
            modification_suggestions['低风险问题SQL'] = f"-- 优化建议：考虑添加适当的索引以提高查询性能\n{low_fixed_sql}"
        
        # 生成性能优化SQL
        # 检查是否有性能相关建议
        performance_keywords = ['性能', '慢', '索引', '优化', '查询计划', '执行计划']
        has_performance_issues = False
        for suggestion in suggestions:
            if any(keyword in suggestion.lower() for keyword in performance_keywords):
                has_performance_issues = True
                break
        
        if has_performance_issues:
            # 生成性能优化SQL（添加索引提示）
            perf_fixed_sql = original_sql
            # 如果是SELECT语句，添加索引提示
            if perf_fixed_sql.lower().strip().startswith('select'):
                table_match = re.search(r'from\s+(\w+)', perf_fixed_sql.lower())
                if table_match:
                    table_name = table_match.group(1)
                    modification_suggestions['性能优化SQL'] = f"-- 性能优化建议：为表 {table_name} 添加适当的索引\n{perf_fixed_sql}"
                else:
                    modification_suggestions['性能优化SQL'] = f"-- 性能优化建议：检查查询条件是否使用索引\n{perf_fixed_sql}"
            else:
                modification_suggestions['性能优化SQL'] = f"-- 性能优化建议：优化SQL语句结构\n{perf_fixed_sql}"
        
        return modification_suggestions
    
    def _extract_key_issues(self, suggestions: List[str], analysis_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        提取关键问题
        
        Args:
            suggestions: 建议列表
            analysis_result: 分析结果
            
        Returns:
            关键问题列表
        """
        key_issues = []
        
        # 从规范性评审中提取未通过的角度
        normative_review = analysis_result.get('规范性评审', {})
        for angle_name, review_data in normative_review.items():
            if review_data.get('status') == '未通过':
                key_issues.append({
                    "type": "规范性评审",
                    "category": angle_name,
                    "severity": self._determine_severity(angle_name),
                    "description": review_data.get('details', ''),
                    "suggestion": review_data.get('suggestion', '')
                })
        
        # 从规范违反详情中提取
        compliance_data = analysis_result.get('规范符合性', {})
        violations = compliance_data.get('规范违反详情', [])
        for violation in violations:
            if isinstance(violation, dict):
                key_issues.append({
                    "type": "规范违反",
                    "category": violation.get('description', ''),
                    "severity": "中风险",
                    "description": violation.get('violation', ''),
                    "suggestion": violation.get('suggestion', '')
                })
        
        return key_issues[:3]  # 最多返回3个关键问题
    
    def _determine_severity(self, angle_name: str) -> str:
        """
        确定问题的严重程度
        
        Args:
            angle_name: 角度名称
            
        Returns:
            严重程度（高风险/中风险/低风险）
        """
        high_risk_angles = ["全表扫描", "sql注入", "安全漏洞", "无主键", "无索引"]
        medium_risk_angles = ["索引设计", "字符集问题", "隐式转换", "索引失效", "性能问题"]
        
        if angle_name in high_risk_angles:
            return "高风险"
        elif angle_name in medium_risk_angles:
            return "中风险"
        else:
            return "低风险"
    
    def _generate_normative_summary(self, suggestions: List[str], detailed_analysis: str) -> Dict[str, Any]:
        """
        生成规范性摘要
        
        Args:
            suggestions: 建议列表
            detailed_analysis: 详细分析文本
            
        Returns:
            规范性摘要
        """
        # 分析规范性角度（简化版本）
        # 在实际实现中，应该调用更详细的分析方法
        normative_angles = {
            "修改列时加属性": "通过",
            "in操作索引失效": "通过", 
            "字符集问题": "通过",
            "注释--问题": "通过",
            "comment问题": "通过",
            "表参数问题": "通过",
            "akm接入": "通过",
            "analyze问题": "通过",
            "dml与ddl之间休眠3秒": "通过",
            "隐式转换": "通过",
            "主键问题": "通过",
            "索引设计": "通过",
            "全表扫描": "通过",
            "表结构一致性": "通过",
            "唯一约束字段须添加not null": "通过"
        }
        
        # 基于建议和详细分析更新状态
        for suggestion in suggestions:
            suggestion_lower = suggestion.lower()
            
            # 检查全表扫描
            if "全表扫描" in suggestion_lower or "全表查询" in suggestion_lower:
                normative_angles["全表扫描"] = "未通过"
            
            # 检查索引设计
            if "索引" in suggestion_lower and ("问题" in suggestion_lower or "失效" in suggestion_lower):
                normative_angles["索引设计"] = "未通过"
                normative_angles["in操作索引失效"] = "未通过"
            
            # 检查字符集
            if "字符集" in suggestion_lower or "编码" in suggestion_lower or "乱码" in suggestion_lower:
                normative_angles["字符集问题"] = "未通过"
        
        # 统计结果
        total_angles = len(normative_angles)
        failed_angles = [angle for angle, status in normative_angles.items() if status == "未通过"]
        passed_count = total_angles - len(failed_angles)
        
        return {
            "total_angles": total_angles,
            "passed": passed_count,
            "failed": failed_angles,
            "compliance_rate": (passed_count / total_angles * 100) if total_angles > 0 else 100.0
        }
    
    def _extract_optimized_sql(self, analysis_result: Dict[str, Any]) -> str:
        """
        提取优化SQL
        
        Args:
            analysis_result: 分析结果
            
        Returns:
            优化后的SQL语句
        """
        # 首先尝试从分析结果中直接提取
        if 'optimized_sql' in analysis_result:
            return analysis_result['optimized_sql']
        
        if '性能优化SQL' in analysis_result:
            return analysis_result['性能优化SQL']
        
        if '修改建议' in analysis_result:
            modification_suggestions = analysis_result['修改建议']
            if isinstance(modification_suggestions, dict):
                if modification_suggestions.get('性能优化SQL'):
                    return modification_suggestions['性能优化SQL']
                elif modification_suggestions.get('高风险问题SQL'):
                    return modification_suggestions['高风险问题SQL']
        
        # 如果没有找到，返回空字符串
        return ""
    
    def _analyze_normative_angles(self, suggestions: List[str], detailed_analysis: str) -> Dict[str, str]:
        """
        分析规范性角度状态（辅助方法）
        
        Args:
            suggestions: 建议列表
            detailed_analysis: 详细分析文本
            
        Returns:
            角度状态字典
        """
        # 简化的分析逻辑
        # 在实际应用中，应该实现更详细的分析
        return self._generate_normative_summary(suggestions, detailed_analysis)

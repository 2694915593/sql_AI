#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SQL分析结果分组处理器 - 修复版
负责将同一文件名的SQL分析结果组合成一个结果，并存储到AM_COMMIT_SHELL_INFO表
修复空值问题
"""

import json
import re
from typing import Dict, Any, List, Optional
from utils.logger import LogMixin
from data_collector.sql_extractor import SQLExtractor


class GroupProcessor(LogMixin):
    """SQL分析结果分组处理器"""
    
    def __init__(self, config_manager, logger=None):
        """
        初始化分组处理器
        
        Args:
            config_manager: 配置管理器
            logger: 日志记录器
        """
        self.config_manager = config_manager
        
        if logger:
            self.set_logger(logger)
        
        # 初始化SQL提取器用于数据库操作
        self.sql_extractor = SQLExtractor(config_manager, logger)
        
        self.logger.info("SQL分析结果分组处理器初始化完成")
    
    def get_files_by_branch(self, branch_name: str) -> List[Dict[str, Any]]:
        """
        从AM_COMMIT_SHELL_INFO表获取指定分支的所有文件
        
        Args:
            branch_name: 分支名称（DEFAULT_VERSION字段值）
            
        Returns:
            文件列表，每个文件包含FILENAME、PROJECT_ID等信息
        """
        try:
            query = """
                SELECT DISTINCT FILENAME, PROJECT_ID, CLASSPATH, DEFAULT_VERSION
                FROM AM_COMMIT_SHELL_INFO 
                WHERE DEFAULT_VERSION = %s
                ORDER BY FILENAME
            """
            
            results = self.sql_extractor.source_db.fetch_all(query, (branch_name,))
            
            files = []
            for row in results:
                files.append({
                    'file_name': row.get('FILENAME'),
                    'project_id': row.get('PROJECT_ID'),
                    'file_path': row.get('CLASSPATH', ''),
                    'default_version': row.get('DEFAULT_VERSION')
                })
            
            self.logger.info(f"从AM_COMMIT_SHELL_INFO表获取到分支 '{branch_name}' 的 {len(files)} 个文件")
            return files
            
        except Exception as e:
            self.logger.error(f"获取分支文件列表失败: {str(e)}", exc_info=True)
            return []
    
    def get_pending_sqls_by_file_and_branch(self, file_name: str, branch_name: str, 
                                           project_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        从AM_SQLLINE_INFO表获取指定文件和分支的待分析SQL
        
        Args:
            file_name: 文件名
            branch_name: 分支名称（DEFAULT_VERSION字段值）
            project_id: 项目ID（可选，如果提供则精确匹配）
            
        Returns:
            SQL记录列表
        """
        try:
            if project_id:
                query = """
                    SELECT ID, SQL_TEXT, FILENAME as file_name, PROJECT_ID as project_id,
                           DEFAULT_VERSION as default_version, FILE_PATH as file_path,
                           SYSTEM_ID as system_id, AUTHOR as author, OPERATE_TYPE as operate_type
                    FROM AM_SQLLINE_INFO 
                    WHERE FILENAME = %s 
                    AND DEFAULT_VERSION = %s
                    AND PROJECT_ID = %s
                    AND (STATUS IS NULL OR STATUS = 'pending' OR STATUS = 'new')
                    ORDER BY ID
                """
                params = (file_name, branch_name, project_id)
            else:
                query = """
                    SELECT ID, SQL_TEXT, FILENAME as file_name, PROJECT_ID as project_id,
                           DEFAULT_VERSION as default_version, FILE_PATH as file_path,
                           SYSTEM_ID as system_id, AUTHOR as author, OPERATE_TYPE as operate_type
                    FROM AM_SQLLINE_INFO 
                    WHERE FILENAME = %s 
                    AND DEFAULT_VERSION = %s
                    AND (STATUS IS NULL OR STATUS = 'pending' OR STATUS = 'new')
                    ORDER BY ID
                """
                params = (file_name, branch_name)
            
            results = self.sql_extractor.source_db.fetch_all(query, params)
            
            sqls = []
            for row in results:
                sqls.append({
                    'id': row.get('ID'),
                    'sql_text': row.get('SQL_TEXT', ''),
                    'file_name': row.get('file_name'),
                    'project_id': row.get('project_id'),
                    'default_version': row.get('default_version'),
                    'file_path': row.get('file_path', ''),
                    'system_id': row.get('system_id'),
                    'author': row.get('author'),
                    'operate_type': row.get('operate_type')
                })
            
            self.logger.info(f"从AM_SQLLINE_INFO表获取到文件 '{file_name}' (分支: {branch_name}) 的 {len(sqls)} 条待分析SQL")
            return sqls
            
        except Exception as e:
            self.logger.error(f"获取SQL记录失败: {str(e)}", exc_info=True)
            return []
    
    def group_by_branch_and_file(self, branch_name: str) -> Dict[str, Dict[str, Any]]:
        """
        根据分支和文件名进行分组
        
        Args:
            branch_name: 分支名称
            
        Returns:
            按分支和文件名分组的字典
        """
        try:
            self.logger.info(f"开始按分支 '{branch_name}' 进行分组")
            
            # 1. 获取该分支的所有文件
            files = self.get_files_by_branch(branch_name)
            if not files:
                self.logger.warning(f"分支 '{branch_name}' 没有找到文件")
                return {}
            
            grouped_results = {}
            
            # 2. 对每个文件，获取待分析的SQL
            for file_info in files:
                file_name = file_info['file_name']
                project_id = file_info['project_id']
                default_version = file_info['default_version']
                file_path = file_info['file_path']
                
                # 获取该文件的待分析SQL
                sqls = self.get_pending_sqls_by_file_and_branch(file_name, branch_name, project_id)
                if not sqls:
                    self.logger.debug(f"文件 '{file_name}' 没有待分析的SQL")
                    continue
                
                # 构建分组键
                group_key = f"{file_name}_{project_id}_{default_version}"
                
                # 准备SQL数据
                sqls_data = []
                for sql_info in sqls:
                    sql_data = {
                        'sql_id': sql_info['id'],
                        'sql_text': sql_info['sql_text'],
                        'sql_info': {
                            'project_id': sql_info['project_id'],
                            'default_version': sql_info['default_version'],
                            'file_path': sql_info['file_path'],
                            'file_name': sql_info['file_name'],
                            'system_id': sql_info.get('system_id'),
                            'author': sql_info.get('author'),
                            'operate_type': sql_info.get('operate_type')
                        }
                    }
                    sqls_data.append(sql_data)
                
                grouped_results[group_key] = {
                    'file_name': file_name,
                    'project_id': project_id,
                    'default_version': default_version,
                    'file_path': file_path,
                    'sqls': sqls_data
                }
            
            self.logger.info(f"分组完成：分支 '{branch_name}' 共 {len(files)} 个文件，分为 {len(grouped_results)} 组（有待分析SQL的组）")
            return grouped_results
            
        except Exception as e:
            self.logger.error(f"按分支分组失败: {str(e)}", exc_info=True)
            return {}
    
    def group_by_filename(self, results: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """
        根据文件名对分析结果进行分组（旧版本，保留兼容性）
        
        Args:
            results: 分析结果列表，每个结果包含sql_id和analysis_result
            
        Returns:
            按文件名分组的字典
        """
        grouped_results = {}
        
        for result in results:
            if not result.get('success', False):
                continue
                
            sql_id = result.get('sql_id')
            analysis_data = result.get('analysis_result', {})
            
            # 确保sql_id是整数类型
            if sql_id is None:
                self.logger.warning("跳过sql_id为None的结果")
                continue
                
            try:
                sql_id_int = int(sql_id)
            except (ValueError, TypeError):
                self.logger.warning(f"sql_id {sql_id} 无法转换为整数")
                continue
            
            # 获取SQL记录信息
            sql_info = self.sql_extractor.extract_sql_by_id(sql_id_int)
            if not sql_info:
                self.logger.warning(f"无法获取SQL ID {sql_id_int} 的信息")
                continue
            
            file_name = sql_info.get('file_name')
            if not file_name:
                # 如果没有文件名，使用其他标识符
                file_name = f"unknown_{sql_id}"
            
            # 提取关键字段用于关联AM_COMMIT_SHELL_INFO表
            project_id = sql_info.get('project_id')
            default_version = sql_info.get('default_version')
            file_path = sql_info.get('file_path', '')
            
            # 构建分组键
            group_key = f"{file_name}_{project_id}_{default_version}"
            
            # 添加附加信息
            sql_data = {
                'sql_id': sql_id,
                'sql_text': sql_info.get('sql_text', ''),
                'analysis_data': analysis_data,
                'sql_info': {
                    'project_id': project_id,
                    'default_version': default_version,
                    'file_path': file_path,
                    'file_name': file_name,
                    'system_id': sql_info.get('system_id'),
                    'author': sql_info.get('author'),
                    'operate_type': sql_info.get('operate_type')
                }
            }
            
            if group_key not in grouped_results:
                grouped_results[group_key] = {
                    'file_name': file_name,
                    'project_id': project_id,
                    'default_version': default_version,
                    'file_path': file_path,
                    'sqls': []
                }
            
            grouped_results[group_key]['sqls'].append(sql_data)
        
        self.logger.info(f"分组完成：共 {len(results)} 条结果，分为 {len(grouped_results)} 组")
        return grouped_results
    
    def combine_analysis_results(self, sqls_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        组合同一文件名的SQL分析结果
        
        Args:
            sqls_data: 同一文件名的SQL数据列表
            
        Returns:
            组合后的分析结果
        """
        if not sqls_data:
            return {"success": False, "error": "没有可组合的SQL数据"}
        
        combined_result = {
            "summary": {
                "total_sqls": len(sqls_data),
                "unique_files": len(set([d['sql_info']['file_name'] for d in sqls_data])),
                "unique_projects": len(set([d['sql_info']['project_id'] for d in sqls_data])),
                "analysis_time": "NOW()"
            },
            "sql_list": [],
            "combined_analysis": {
                "all_suggestions": [],
                "risk_summary": {},
                "performance_summary": {},
                "security_summary": {}
            }
        }
        
        # 收集所有SQL的分析结果
        all_suggestions = []
        risk_categories = {
            "高风险问题": [],
            "中风险问题": [],
            "低风险问题": []
        }
        
        # 收集分析摘要
        analysis_summaries = []
        
        for sql_data in sqls_data:
            sql_id = sql_data['sql_id']
            sql_text = sql_data['sql_text']
            analysis_data = sql_data['analysis_data']
            sql_info = sql_data['sql_info']
            
            # 添加到SQL列表
            sql_entry = {
                "sql_id": sql_id,
                "sql_preview": self._truncate_sql(sql_text, 100),
                "sql_type": analysis_data.get('SQL类型', analysis_data.get('sql_type', '未知')),
                "score": analysis_data.get('综合评分', analysis_data.get('score', 0)),
                "suggestion_count": len(analysis_data.get('建议', analysis_data.get('suggestions', [])))
            }
            combined_result["sql_list"].append(sql_entry)
            
            # 提取建议（兼容新旧格式）
            suggestions = analysis_data.get('建议', analysis_data.get('suggestions', []))
            if isinstance(suggestions, list):
                for suggestion in suggestions:
                    if isinstance(suggestion, str):
                        # 精简建议：只保留关键角度的建议
                        if self._is_critical_suggestion(suggestion):
                            if suggestion not in all_suggestions:
                                all_suggestions.append(suggestion)
                    elif isinstance(suggestion, dict):
                        # 如果是字典，尝试提取文本
                        suggestion_text = suggestion.get('text', str(suggestion))
                        if self._is_critical_suggestion(suggestion_text):
                            if suggestion_text not in all_suggestions:
                                all_suggestions.append(suggestion_text)
            
            # 提取风险评估（兼容新旧格式）
            risk_assessment = analysis_data.get('风险评估', analysis_data.get('risk_assessment', {}))
            for category, issues in risk_assessment.items():
                if isinstance(issues, list):
                    for issue in issues:
                        if issue and isinstance(issue, str):
                            # 规范化类别名称
                            norm_category = category
                            if category == '高风险问题' or category == 'high_risk' or '高风险' in category:
                                norm_category = '高风险问题'
                            elif category == '中风险问题' or category == 'medium_risk' or '中风险' in category:
                                norm_category = '中风险问题'
                            elif category == '低风险问题' or category == 'low_risk' or '低风险' in category:
                                norm_category = '低风险问题'
                            
                            # 精简问题：只保留关键角度的问题
                            if self._is_critical_risk_issue(issue):
                                if norm_category in risk_categories and issue not in risk_categories[norm_category]:
                                    risk_categories[norm_category].append(issue)
            
            # 提取分析摘要
            analysis_summary = analysis_data.get('分析摘要', analysis_data.get('summary', ''))
            if analysis_summary and isinstance(analysis_summary, str) and analysis_summary.strip():
                # 精简分析摘要：只保留关键信息
                simplified_summary = self._simplify_analysis_summary(analysis_summary)
                if simplified_summary and simplified_summary not in analysis_summaries:
                    analysis_summaries.append(simplified_summary)
        
        # 组合建议：按照SQL原文分点统一展示
        formatted_suggestions = self._format_suggestions_by_sql(sqls_data, all_suggestions)
        
        # 构建组合后的分析结果
        combined_result["combined_analysis"]["all_suggestions"] = formatted_suggestions
        combined_result["combined_analysis"]["risk_summary"] = {
            "高风险问题数量": len(risk_categories["高风险问题"]),
            "中风险问题数量": len(risk_categories["中风险问题"]), 
            "低风险问题数量": len(risk_categories["低风险问题"]),
            "详细问题": risk_categories
        }
        
        # 计算综合评分（平均分）
        total_score = 0
        count = 0
        for sql_data in sqls_data:
            score = sql_data['analysis_data'].get('score', 0)
            if score > 0:
                total_score += score
                count += 1
        
        combined_result["summary"]["average_score"] = total_score / count if count > 0 else 0
        combined_result["summary"]["success_rate"] = len(sqls_data) / len(sqls_data) * 100 if sqls_data else 0
        
        return combined_result
    
    def _truncate_sql(self, sql_text: str, max_length: int = 100) -> str:
        """截断SQL文本"""
        if not sql_text:
            return ""
        
        if len(sql_text) <= max_length:
            return sql_text
        
        return sql_text[:max_length] + "..."
    
    def _format_suggestions_by_sql(self, sqls_data: List[Dict[str, Any]], all_suggestions: List[str]) -> List[Dict[str, Any]]:
        """
        按照SQL原文分点统一展示建议
        
        Args:
            sqls_data: SQL数据列表
            all_suggestions: 所有建议列表
            
        Returns:
            格式化后的建议列表
        """
        formatted_suggestions = []
        
        # 去重建议
        unique_suggestions = []
        seen_suggestions = set()
        
        for suggestion in all_suggestions:
            # 简单的文本去重
            suggestion_key = suggestion.strip().lower()
            if suggestion_key and suggestion_key not in seen_suggestions:
                seen_suggestions.add(suggestion_key)
                unique_suggestions.append(suggestion)
        
        # 按SQL分组建议
        for sql_data in sqls_data:
            sql_id = sql_data['sql_id']
            sql_text = sql_data['sql_text']
            
            # 获取该SQL的特定建议
            sql_suggestions = sql_data['analysis_data'].get('suggestions', [])
            if not sql_suggestions:
                continue
            
            # 创建该SQL的建议条目
            sql_suggestion_entry = {
                "sql_id": sql_id,
                "sql_preview": self._truncate_sql(sql_text, 80),
                "suggestions": []
            }
            
            for suggestion in sql_suggestions:
                if isinstance(suggestion, str):
                    sql_suggestion_entry["suggestions"].append({
                        "text": suggestion,
                        "type": "general"
                    })
                elif isinstance(suggestion, dict):
                    sql_suggestion_entry["suggestions"].append({
                        "text": json.dumps(suggestion, ensure_ascii=False),
                        "type": "detailed"
                    })
            
            if sql_suggestion_entry["suggestions"]:
                formatted_suggestions.append(sql_suggestion_entry)
        
        # 如果没有按SQL分组，则使用通用的建议列表
        if not formatted_suggestions and unique_suggestions:
            formatted_suggestions = [{
                "summary": "通用建议",
                "suggestions": [{"text": s, "type": "general"} for s in unique_suggestions[:10]]
            }]
        
        return formatted_suggestions
    
    def store_to_commit_shell_info(self, group_key: str, group_data: Dict[str, Any], 
                                   combined_result: Dict[str, Any]) -> bool:
        """
        将组合结果存储到AM_COMMIT_SHELL_INFO表
        
        Args:
            group_key: 分组键
            group_data: 分组数据
            combined_result: 组合后的分析结果
            
        Returns:
            是否成功
        """
        try:
            # 准备存储数据
            storage_data = self._prepare_storage_data(group_data, combined_result)
            
            # 将数据转换为JSON字符串
            json_data = json.dumps(storage_data, ensure_ascii=False, indent=2)
            
            # 查找或创建AM_COMMIT_SHELL_INFO记录
            file_name = group_data['file_name']
            project_id = group_data['project_id']
            default_version = group_data['default_version']
            file_path = group_data.get('file_path', '')
            
            # 首先检查记录是否存在
            check_query = """
                SELECT ID 
                FROM AM_COMMIT_SHELL_INFO 
                WHERE PROJECT_ID = %s 
                AND DEFAULT_VERSION = %s 
                AND FILENAME = %s
            """
            
            result = self.sql_extractor.source_db.fetch_one(
                check_query, (project_id, default_version, file_name)
            )
            
            if result:
                # 更新现有记录
                update_query = """
                    UPDATE AM_COMMIT_SHELL_INFO 
                    SET AI_ANALYSE_RESULT = %s, 
                        UPDATE_TIME = NOW()
                    WHERE ID = %s
                """
                affected = self.sql_extractor.source_db.execute(
                    update_query, (json_data, result['ID'])
                )
                
                if affected > 0:
                    self.logger.info(f"更新AM_COMMIT_SHELL_INFO记录成功，ID: {result['ID']}")
                    return True
                else:
                    self.logger.warning(f"更新AM_COMMIT_SHELL_INFO记录失败，ID: {result['ID']}")
                    return False
            else:
                # 插入新记录
                insert_query = """
                    INSERT INTO AM_COMMIT_SHELL_INFO 
                    (PROJECT_ID, DEFAULT_VERSION, CLASSPATH, FILENAME, AI_ANALYSE_RESULT, CREATE_TIME, UPDATE_TIME)
                    VALUES (%s, %s, %s, %s, %s, NOW(), NOW())
                """
                affected = self.sql_extractor.source_db.execute(
                    insert_query, (project_id, default_version, file_path, file_name, json_data)
                )
                
                if affected > 0:
                    self.logger.info(f"插入AM_COMMIT_SHELL_INFO记录成功")
                    return True
                else:
                    self.logger.warning(f"插入AM_COMMIT_SHELL_INFO记录失败")
                    return False
                
        except Exception as e:
            self.logger.error(f"存储到AM_COMMIT_SHELL_INFO表时发生错误: {str(e)}", exc_info=True)
            return False
    
    def _prepare_storage_data(self, group_data: Dict[str, Any], 
                            combined_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        准备存储到AM_COMMIT_SHELL_INFO表的数据
        修复空值问题
        
        Args:
            group_data: 分组数据
            combined_result: 组合后的分析结果
            
        Returns:
            存储数据
        """
        storage_data = {
            "file_info": {
                "file_name": group_data['file_name'],
                "project_id": group_data['project_id'],
                "default_version": group_data['default_version'],
                "file_path": group_data.get('file_path', ''),
                "sql_count": len(group_data['sqls'])
            },
            "analysis_summary": combined_result.get('summary', {}),
            "combined_analysis": combined_result.get('combined_analysis', {}),
            "sql_details": []
        }
        
        # 确保analysis_summary有完整的结构
        if not storage_data["analysis_summary"]:
            storage_data["analysis_summary"] = {
                "total_sqls": len(group_data['sqls']),
                "unique_files": 1,
                "unique_projects": 1,
                "analysis_time": "NOW()",
                "average_score": 0,
                "success_rate": 100.0 if group_data['sqls'] else 0
            }
        
        # 确保combined_analysis有完整的结构
        if not storage_data["combined_analysis"]:
            storage_data["combined_analysis"] = {
                "all_suggestions": [],
                "risk_summary": {
                    "高风险问题数量": 0,
                    "中风险问题数量": 0,
                    "低风险问题数量": 0,
                    "详细问题": {
                        "高风险问题": [],
                        "中风险问题": [],
                        "低风险问题": []
                    }
                },
                "performance_summary": {},
                "security_summary": {}
            }
        else:
            # 确保risk_summary有完整结构
            if "risk_summary" not in storage_data["combined_analysis"]:
                storage_data["combined_analysis"]["risk_summary"] = {
                    "高风险问题数量": 0,
                    "中风险问题数量": 0,
                    "低风险问题数量": 0,
                    "详细问题": {
                        "高风险问题": [],
                        "中风险问题": [],
                        "低风险问题": []
                    }
                }
            elif "详细问题" not in storage_data["combined_analysis"]["risk_summary"]:
                storage_data["combined_analysis"]["risk_summary"]["详细问题"] = {
                    "高风险问题": [],
                    "中风险问题": [],
                    "低风险问题": []
                }
            
            # 确保performance_summary和security_summary存在
            if "performance_summary" not in storage_data["combined_analysis"]:
                storage_data["combined_analysis"]["performance_summary"] = {}
            if "security_summary" not in storage_data["combined_analysis"]:
                storage_data["combined_analysis"]["security_summary"] = {}
            
            # 确保all_suggestions存在
            if "all_suggestions" not in storage_data["combined_analysis"]:
                storage_data["combined_analysis"]["all_suggestions"] = []
        
        # 添加每个SQL的详细信息
        for sql_data in group_data['sqls']:
            sql_detail = {
                "sql_id": sql_data['sql_id'],
                "sql_preview": self._truncate_sql(sql_data['sql_text'], 150),
                "analysis_data": sql_data['analysis_data']
            }
            
            # 如果analysis_data为空，提供默认结构
            if not sql_detail["analysis_data"]:
                sql_detail["analysis_data"] = {
                    "建议": [],
                    "SQL类型": "未知",
                    "分析摘要": "未提供详细分析",
                    "综合评分": 0,
                    "规范符合性": {
                        "规范符合度": 0.0,
                        "规范违反详情": []
                    },
                    "风险评估": {
                        "高风险问题": [],
                        "中风险问题": [],
                        "低风险问题": []
                    },
                    "修改建议": {
                        "高风险问题SQL": "",
                        "中风险问题SQL": "",
                        "低风险问题SQL": "",
                        "性能优化SQL": ""
                    }
                }
            
            storage_data["sql_details"].append(sql_detail)
        
        return storage_data
    
    def process_grouped_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        处理分组结果（主入口函数）
        
        Args:
            results: 分析结果列表
            
        Returns:
            处理结果
        """
        try:
            self.logger.info(f"开始处理分组结果，共 {len(results)} 条分析结果")
            
            # 1. 按文件名分组
            grouped_results = self.group_by_filename(results)
            
            if not grouped_results:
                self.logger.warning("没有可分组的结果")
                return {"success": False, "error": "没有可分组的结果"}
            
            # 2. 处理每个分组
            processed_groups = []
            success_count = 0
            fail_count = 0
            
            for group_key, group_data in grouped_results.items():
                try:
                    self.logger.info(f"处理分组: {group_key}，包含 {len(group_data['sqls'])} 条SQL")
                    
                    # 组合分析结果
                    combined_result = self.combine_analysis_results(group_data['sqls'])
                    
                    # 存储到AM_COMMIT_SHELL_INFO表
                    success = self.store_to_commit_shell_info(group_key, group_data, combined_result)
                    
                    if success:
                        processed_groups.append({
                            "group_key": group_key,
                            "file_name": group_data['file_name'],
                            "sql_count": len(group_data['sqls']),
                            "status": "success"
                        })
                        success_count += 1
                        self.logger.info(f"分组 {group_key} 处理成功")
                    else:
                        processed_groups.append({
                            "group_key": group_key,
                            "file_name": group_data['file_name'],
                            "sql_count": len(group_data['sqls']),
                            "status": "failed"
                        })
                        fail_count += 1
                        self.logger.warning(f"分组 {group_key} 处理失败")
                        
                except Exception as e:
                    self.logger.error(f"处理分组 {group_key} 时发生错误: {str(e)}", exc_info=True)
                    fail_count += 1
                    processed_groups.append({
                        "group_key": group_key,
                        "status": "error",
                        "error": str(e)
                    })
            
            summary = {
                "success": True,
                "total_groups": len(grouped_results),
                "success_count": success_count,
                "fail_count": fail_count,
                "processed_groups": processed_groups
            }
            
            self.logger.info(f"分组处理完成：共 {len(grouped_results)} 组，成功 {success_count} 组，失败 {fail_count} 组")
            return summary
            
        except Exception as e:
            self.logger.error(f"处理分组结果时发生错误: {str(e)}", exc_info=True)
            return {"success": False, "error": str(e)}
    
    def _is_critical_suggestion(self, suggestion: str) -> bool:
        """
        检查建议是否属于关键角度
        
        关键角度列表：
        1. 隐式转换
        2. 主键
        3. 全表扫描
        4. 修改列时加属性
        5. 表结构不一致
        6. 测试数据不合格
        7. in操作索引失效
        8. 字符集问题
        9. 注释--问题
        10. comment
        11. 表参数问题
        12. 唯一约束字段须添加not null
        13. akm接入
        14. analyze问题
        15. dml与ddl之间休眠3秒
        
        Args:
            suggestion: 建议文本
            
        Returns:
            是否属于关键角度
        """
        if not suggestion or not isinstance(suggestion, str):
            return False
        
        suggestion_lower = suggestion.lower()
        
        # 关键角度关键词
        critical_keywords = [
            '隐式转换', 'implicit conversion', '类型转换',
            '主键', 'primary key', 'primary_key',
            '全表扫描', 'full table scan', '全表查询',
            '修改列', 'alter column', '列属性',
            '表结构', '表不一致', '结构不一致',
            '测试数据', 'test data', '测试不合格',
            'in操作', 'in索引', '索引失效',
            '字符集', 'charset', '编码',
            '注释', 'comment', '--',
            '表参数', 'table parameter', '参数问题',
            '唯一约束', 'unique constraint', 'not null',
            'akm', '接入', 'akm接入',
            'analyze', '分析表', '统计信息',
            'dml', 'ddl', '休眠', 'sleep'
        ]
        
        # 检查是否包含任何关键角度关键词
        for keyword in critical_keywords:
            if keyword in suggestion_lower:
                return True
        
        # 如果建议太短或太长，可能不是关键建议
        if len(suggestion) < 10 or len(suggestion) > 500:
            return False
        
        return False
    
    def _is_critical_risk_issue(self, issue: str) -> bool:
        """
        检查风险问题是否属于关键角度
        
        Args:
            issue: 风险问题文本
            
        Returns:
            是否属于关键角度
        """
        if not issue or not isinstance(issue, str):
            return False
        
        issue_lower = issue.lower()
        
        # 关键风险问题关键词（更严格的关键角度）
        critical_risk_keywords = [
            'sql注入', 'sql injection', '安全漏洞',
            '无主键', '缺少主键', '无索引',
            '全表扫描', '性能瓶颈', '死锁',
            '数据丢失', '数据不一致', '权限过大'
        ]
        
        # 检查是否包含关键风险关键词
        for keyword in critical_risk_keywords:
            if keyword in issue_lower:
                return True
        
        # 同时检查是否属于关键角度
        return self._is_critical_suggestion(issue)
    
    def _simplify_analysis_summary(self, summary: str) -> str:
        """
        简化分析摘要，只保留关键信息
        
        Args:
            summary: 原始分析摘要
            
        Returns:
            简化后的分析摘要
        """
        if not summary or not isinstance(summary, str):
            return ""
        
        # 去除多余的空格和换行
        summary = summary.strip()
        
        # 如果摘要太短，直接返回
        if len(summary) <= 100:
            return summary
        
        # 关键信息标记
        critical_markers = [
            '存在', '问题', '风险', '建议', '优化', 
            '性能', '安全', '索引', '主键', '全表扫描',
            '隐式转换', '字符集', '注释', 'analyze'
        ]
        
        # 查找包含关键信息的句子
        sentences = re.split(r'[。！？；]', summary)
        critical_sentences = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            # 检查句子是否包含关键信息
            sentence_lower = sentence.lower()
            for marker in critical_markers:
                if marker in sentence_lower:
                    critical_sentences.append(sentence)
                    break
        
        # 如果有关键句子，组合它们
        if critical_sentences:
            simplified = '。'.join(critical_sentences[:3]) + '。'
            if len(simplified) <= 200:
                return simplified
        
        # 如果没有关键句子或组合后太长，截取前150字
        if len(summary) > 150:
            return summary[:147] + '...'
        
        return summary
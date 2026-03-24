#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SQL分析结果分组处理器 - 修复版本
负责将同一文件名的SQL分析结果组合成一个结果，并存储到AM_COMMIT_SHELL_INFO表
修复数据丢失问题：确保combined_analysis.risk_summary.详细问题字段正确填充
"""

import json
import re
from typing import Dict, Any, List, Optional
from utils.logger import LogMixin
from data_collector.sql_extractor import SQLExtractor
from data_collector.remote_shell_reader import RemoteShellReader
from data_collector.shell_sql_extractor import ShellScriptSQLExtractor
import pymysql.err


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
            # 首先尝试查询包含SYSTEM字段
            query_with_system = """
                SELECT DISTINCT FILENAME, PROJECT_ID, CLASSPATH, DEFAULT_VERSION, SYSTEM
                FROM AM_COMMIT_SHELL_INFO 
                WHERE DEFAULT_VERSION = %s
                ORDER BY FILENAME
            """
            
            try:
                results = self.sql_extractor.source_db.fetch_all(query_with_system, (branch_name,))
                has_system_field = True
            except pymysql.err.ProgrammingError as e:
                # 如果SYSTEM字段不存在，回退到原始查询
                self.logger.warning(f"SYSTEM字段不存在，使用原始查询: {str(e)}")
                query_without_system = """
                    SELECT DISTINCT FILENAME, PROJECT_ID, CLASSPATH, DEFAULT_VERSION
                    FROM AM_COMMIT_SHELL_INFO 
                    WHERE DEFAULT_VERSION = %s
                    ORDER BY FILENAME
                """
                results = self.sql_extractor.source_db.fetch_all(query_without_system, (branch_name,))
                has_system_field = False
            except Exception as e:
                self.logger.error(f"查询AM_COMMIT_SHELL_INFO表失败: {str(e)}", exc_info=True)
                return []
            
            files = []
            for row in results:
                file_info = {
                    'file_name': row.get('FILENAME'),
                    'project_id': row.get('PROJECT_ID'),
                    'file_path': row.get('CLASSPATH', ''),
                    'default_version': row.get('DEFAULT_VERSION')
                }
                if has_system_field:
                    file_info['system'] = row.get('SYSTEM', '')
                else:
                    file_info['system'] = ''
                files.append(file_info)
            
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
            
            # 检查远程服务器配置是否启用
            remote_enabled = False
            try:
                remote_config = self.config_manager.get_section('remote_server')
                if remote_config:
                    remote_enabled = remote_config.get('enabled', 'true').lower() == 'true'
            except Exception as e:
                self.logger.warning(f"读取远程服务器配置失败: {str(e)}，默认禁用")
            
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
                system = file_info.get('system', '')
                
                # 获取该文件的待分析SQL
                sqls = self.get_pending_sqls_by_file_and_branch(file_name, branch_name, project_id)
                if not sqls:
                    self.logger.debug(f"文件 '{file_name}' 没有待分析的SQL")
                    continue
                
                # 如果远程读取启用，从远程文件提取SQL
                extracted_sqls = []
                if remote_enabled and system and file_path:
                    extracted_sqls = self.extract_sql_from_remote_file(system, file_path, file_name)
                    if extracted_sqls:
                        self.logger.info(f"从远程文件提取到 {len(extracted_sqls)} 条SQL语句")
                
                # 构建分组键
                group_key = f"{file_name}_{project_id}_{default_version}"
                
                # 准备SQL数据
                sqls_data = []
                
                # 确定要处理的SQL数量
                if extracted_sqls:
                    # 如果提取到SQL，只处理提取的SQL（数量不超过数据库记录）
                    process_count = min(len(extracted_sqls), len(sqls))
                    self.logger.info(f"提取到 {len(extracted_sqls)} 条SQL，数据库有 {len(sqls)} 条记录，处理 {process_count} 条SQL")
                else:
                    # 如果没有提取到SQL，处理所有数据库记录
                    process_count = len(sqls)
                
                for i in range(process_count):
                    if i < len(sqls):
                        sql_info = sqls[i]
                        # 如果有提取的SQL，使用提取的SQL；否则使用数据库中的SQL
                        if i < len(extracted_sqls):
                            sql_text = extracted_sqls[i]['sql']
                            self.logger.debug(f"使用从远程文件提取的SQL替换索引 {i} 的SQL文本")
                        else:
                            sql_text = sql_info['sql_text']
                        
                        sql_data = {
                            'sql_id': sql_info['id'],
                            'sql_text': sql_text,
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
                    else:
                        # 理论上不会发生，因为process_count <= len(sqls)
                        break
                
                grouped_results[group_key] = {
                    'file_name': file_name,
                    'project_id': project_id,
                    'default_version': default_version,
                    'file_path': file_path,
                    'system': system,
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
        
        # 构建组合后的分析结果 - 确保risk_summary有完整结构
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
        修复空值问题，并添加简化版本
        
        Args:
            group_data: 分组数据
            combined_result: 组合后的分析结果
            
        Returns:
            存储数据（包含完整和简化版本）
        """
        # 生成完整存储数据
        full_storage_data = self._prepare_full_storage_data(group_data, combined_result)
        
        # 生成简化存储数据
        simplified_storage_data = self._prepare_simplified_storage_data(group_data, combined_result)
        
        # 返回包含完整和简化版本的数据
        storage_data = {
            "full_data": full_storage_data,
            "simplified_data": simplified_storage_data
        }
        
        return storage_data
    
    def _prepare_full_storage_data(self, group_data: Dict[str, Any], 
                                 combined_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        准备完整的存储数据
        
        Args:
            group_data: 分组数据
            combined_result: 组合后的分析结果
            
        Returns:
            完整存储数据
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
        if not storage_data["combined_analysis"] or not isinstance(storage_data["combined_analysis"], dict):
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
            if "risk_summary" not in storage_data["combined_analysis"] or not isinstance(storage_data["combined_analysis"]["risk_summary"], dict):
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
            else:
                # 确保risk_summary包含必要的字段
                risk_summary = storage_data["combined_analysis"]["risk_summary"]
                
                # 确保数量字段存在
                for count_field in ["高风险问题数量", "中风险问题数量", "低风险问题数量"]:
                    if count_field not in risk_summary or not isinstance(risk_summary[count_field], (int, float)):
                        risk_summary[count_field] = 0
                
                # 确保详细问题字段存在且有完整结构
                if "详细问题" not in risk_summary or not isinstance(risk_summary["详细问题"], dict):
                    risk_summary["详细问题"] = {
                        "高风险问题": [],
                        "中风险问题": [],
                        "低风险问题": []
                    }
                else:
                    # 确保详细问题的子字段存在
                    detail_problems = risk_summary["详细问题"]
                    for problem_type in ["高风险问题", "中风险问题", "低风险问题"]:
                        if problem_type not in detail_problems or not isinstance(detail_problems[problem_type], list):
                            detail_problems[problem_type] = []
            
            # 确保performance_summary和security_summary存在
            if "performance_summary" not in storage_data["combined_analysis"]:
                storage_data["combined_analysis"]["performance_summary"] = {}
            if "security_summary" not in storage_data["combined_analysis"]:
                storage_data["combined_analysis"]["security_summary"] = {}
            
            # 确保all_suggestions存在
            if "all_suggestions" not in storage_data["combined_analysis"]:
                storage_data["combined_analysis"]["all_suggestions"] = []
            elif not isinstance(storage_data["combined_analysis"]["all_suggestions"], list):
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
                    "规范性评审": {},
                    "修改建议": {
                        "高风险问题SQL": "",
                        "中风险问题SQL": "",
                        "低风险问题SQL": "",
                        "性能优化SQL": ""
                    }
                }
            
            storage_data["sql_details"].append(sql_detail)
        
        return storage_data
    
    def _prepare_simplified_storage_data(self, group_data: Dict[str, Any], 
                                       combined_result: Dict[str, Any]) -> str:
        """
        准备简化存储数据为四行文本格式 - 新格式要求
        
        格式要求（按照用户反馈）：
        第一行：文件信息（文件名和SQL数量）
        第二行：违反内容（如：全表扫描、in索引失效）
        第三行：违反规范（如：索引列顺序不一致）
        第四行：修改建议（如：建议优化索引结构，优化内容如下）
        
        Args:
            group_data: 分组数据
            combined_result: 组合后的分析结果
            
        Returns:
            简化后的四行文本
        """
        try:
            # 第一行：文件信息（文件名和SQL数量）
            file_name = group_data['file_name']
            sql_count = len(group_data['sqls'])
            
            # 如果是单条SQL，显示SQL预览
            if sql_count == 1 and group_data['sqls']:
                sql_text = group_data['sqls'][0].get('sql_text', '')
                if sql_text:
                    # 简化SQL文本：如果太长则截断
                    max_sql_length = 200
                    if len(sql_text) > max_sql_length:
                        first_line = sql_text[:max_sql_length] + "..."
                    else:
                        first_line = sql_text
                else:
                    first_line = f"文件: {file_name} (包含{sql_count}条SQL)"
            else:
                first_line = f"文件: {file_name} (包含{sql_count}条SQL)"
            
            # 第二行：违反内容（从规范性评审中提取）
            # 收集所有SQL的违反内容（角度名称）
            all_violation_contents = []
            for sql_data in group_data['sqls']:
                analysis_data = sql_data.get('analysis_data', {})
                normative_review = analysis_data.get('规范性评审', {})
                
                for angle_name, review_data in normative_review.items():
                    status = review_data.get('status', '')
                    if status == '未通过':
                        # 只添加角度名称作为违反内容
                        if angle_name not in all_violation_contents:
                            all_violation_contents.append(angle_name)
            
            second_line = "违反内容："
            if all_violation_contents:
                # 使用中文顿号分隔，最多显示5个
                unique_violations = list(dict.fromkeys(all_violation_contents))[:5]
                second_line += "、".join(unique_violations)
                if len(all_violation_contents) > 5:
                    second_line += f" 等{len(all_violation_contents)}项"
            else:
                second_line += "无"
            
            # 第三行：违反规范（从规范违反详情中提取）
            # 收集所有SQL的规范违反详情
            all_violation_rules = []
            for sql_data in group_data['sqls']:
                analysis_data = sql_data.get('analysis_data', {})
                compliance_data = analysis_data.get('规范符合性', {})
                compliance_violations = compliance_data.get('规范违反详情', [])
                
                for violation in compliance_violations[:3]:  # 每个SQL最多取3个
                    if isinstance(violation, dict):
                        description = violation.get('description', '')
                        violation_text = violation.get('violation', '')
                        if description:
                            # 提取关键规范描述
                            if "规范" in description or "要求" in description or "标准" in description:
                                all_violation_rules.append(description)
                            else:
                                all_violation_rules.append(f"{description}: {violation_text[:30]}...")
            
            third_line = "违反规范："
            if all_violation_rules:
                unique_rules = list(dict.fromkeys(all_violation_rules))[:3]
                third_line += "、".join(unique_rules)
                if len(all_violation_rules) > 3:
                    third_line += f" 等{len(all_violation_rules)}条规范"
            else:
                third_line += "无"
            
            # 第四行：修改建议
            # 收集所有SQL的修改建议
            all_modification_suggestions = []
            for sql_data in group_data['sqls']:
                analysis_data = sql_data.get('analysis_data', {})
                modification_suggestions = analysis_data.get('修改建议', {})
                
                # 优先从修改建议中获取具体的优化内容
                if modification_suggestions and isinstance(modification_suggestions, dict):
                    # 尝试性能优化SQL
                    if modification_suggestions.get('性能优化SQL'):
                        perf_sql = modification_suggestions.get('性能优化SQL', '')
                        if len(perf_sql) > 80:
                            all_modification_suggestions.append(f"性能优化：{perf_sql[:80]}...")
                        else:
                            all_modification_suggestions.append(f"性能优化：{perf_sql}")
                    # 尝试高风险问题SQL
                    elif modification_suggestions.get('高风险问题SQL'):
                        high_risk_sql = modification_suggestions.get('高风险问题SQL', '')
                        if len(high_risk_sql) > 80:
                            all_modification_suggestions.append(f"高风险修复：{high_risk_sql[:80]}...")
                        else:
                            all_modification_suggestions.append(f"高风险修复：{high_risk_sql}")
                    # 尝试通用建议
                    elif modification_suggestions.get('低风险问题SQL'):
                        low_risk_sql = modification_suggestions.get('低风险问题SQL', '')
                        if low_risk_sql:
                            all_modification_suggestions.append(f"优化建议：{low_risk_sql[:80]}...")
                
                # 如果没有修改建议，从通用建议中获取
                if not all_modification_suggestions:
                    suggestions = analysis_data.get('建议', [])
                    if suggestions:
                        # 取第一条建议作为主要修改建议
                        main_suggestion = suggestions[0]
                        if len(main_suggestion) > 80:
                            all_modification_suggestions.append(f"{main_suggestion[:80]}...")
                        else:
                            all_modification_suggestions.append(main_suggestion)
            
            fourth_line = "修改建议："
            if all_modification_suggestions:
                # 去重，取前2条
                unique_suggestions = list(dict.fromkeys(all_modification_suggestions))[:2]
                for i, suggestion in enumerate(unique_suggestions):
                    if i == 0:
                        fourth_line += suggestion
                    else:
                        fourth_line += f"；{suggestion}"
                
                # 如果有更多建议，添加数量提示
                if len(all_modification_suggestions) > 2:
                    fourth_line += f" 等{len(all_modification_suggestions)}条建议"
            else:
                fourth_line += "无"
            
            # 组合四行文本，每行最大长度限制
            max_line_length = 500
            lines = [first_line, second_line, third_line, fourth_line]
            simplified_text = "\n".join([line[:max_line_length] for line in lines])
            
            return simplified_text
            
        except Exception as e:
            self.logger.warning(f"准备简化存储数据时发生错误: {str(e)}")
            # 返回默认简化格式
            return f"文件: {group_data.get('file_name', '未知')}\n违反内容：数据处理失败\n违反规范：请查看完整分析\n修改建议：检查代码逻辑"
    
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
    
    def extract_sql_from_remote_file(self, system: str, classpath: str, file_name: str) -> List[Dict[str, Any]]:
        """
        从远程服务器读取shell文件并提取SQL语句（不存储到数据库）
        
        Args:
            system: SYSTEM字段
            classpath: CLASSPATH字段
            file_name: 文件名
            
        Returns:
            提取的SQL语句列表，每个元素包含:
            - sql: SQL语句文本
            - line_start: 起始行号
            - line_end: 结束行号
            - context: 提取上下文
            - source: 源标识
        """
        try:
            self.logger.info(f"从远程服务器读取shell文件并提取SQL: system={system}, classpath={classpath}")
            
            # 1. 读取远程文件内容
            remote_reader = RemoteShellReader(self.config_manager, self.logger)
            shell_content = remote_reader.read_shell_file(system, classpath, file_name)
            if shell_content is None:
                self.logger.error(f"读取远程shell文件失败: {system}/{classpath}")
                return []
                
            # 2. 提取SQL语句
            extractor = ShellScriptSQLExtractor(self.logger)
            sql_statements = extractor.extract_sql_from_content(shell_content, source=f"{system}/{classpath}")
            if not sql_statements:
                self.logger.warning(f"从shell文件中未提取到SQL语句: {file_name}")
                return []
                
            self.logger.info(f"从远程文件提取到 {len(sql_statements)} 条SQL语句")
            return sql_statements
            
        except Exception as e:
            self.logger.error(f"从远程文件提取SQL时发生错误: {str(e)}", exc_info=True)
            return []
    
    def update_sql_from_remote_file(self, system: str, classpath: str, file_name: str, branch_name: str, project_id: str) -> bool:
        """
        从远程服务器读取shell文件并更新AM_SQLLINE_INFO中的SQL语句
        （已弃用 - 提取的SQL不应存储到AM_SQLLINE_INFO表中）
        
        Args:
            system: SYSTEM字段
            classpath: CLASSPATH字段
            file_name: 文件名
            branch_name: 分支名称
            project_id: 项目ID
            
        Returns:
            是否成功（始终返回False，因为不应更新数据库）
        """
        self.logger.warning(f"update_sql_from_remote_file已弃用，提取的SQL不应存储到AM_SQLLINE_INFO表中")
        return False
    
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
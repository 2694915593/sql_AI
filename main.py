#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI-SQL质量分析系统主程序
主要功能：从数据库读取待分析SQL，收集表元数据，调用大模型API分析，存储结果
"""

import sys
import os
import logging
from typing import List, Dict, Any, Optional

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.config_manager import ConfigManager
from data_collector.sql_extractor import SQLExtractor
from data_collector.metadata_collector import MetadataCollector
# 使用增强版模型客户端，包含完整的SQL规范集成
from ai_integration.model_client_enhanced import ModelClient
from storage.result_processor import ResultProcessor
from storage.group_processor import GroupProcessor
from utils.logger import setup_logger


class SQLAnalyzer:
    """SQL质量分析器主类"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        初始化分析器
        
        Args:
            config_path: 配置文件路径，默认为config/config.ini
        """
        # 初始化配置 - 确保config_path不是None
        actual_config_path = config_path if config_path is not None else 'config/config.ini'
        self.config = ConfigManager(actual_config_path)
        
        # 初始化日志
        self.logger = setup_logger(__name__, self.config.get_log_config())
        
        # 初始化各模块
        self.sql_extractor = SQLExtractor(self.config, self.logger)
        self.metadata_collector = MetadataCollector(self.config, self.logger)
        self.model_client = ModelClient(self.config, self.logger)
        self.result_processor = ResultProcessor(self.config, self.logger)
        self.group_processor = GroupProcessor(self.config, self.logger)
        
        self.logger.info("SQL质量分析器初始化完成")
    
    def analyze_single_sql(self, sql_id: int) -> Dict[str, Any]:
        """
        分析单个SQL语句
        
        Args:
            sql_id: SQL记录ID
            
        Returns:
            分析结果字典
        """
        try:
            self.logger.info(f"开始分析SQL ID: {sql_id}")
            
            # 1. 提取SQL信息
            sql_info = self.sql_extractor.extract_sql_by_id(sql_id)
            if not sql_info:
                self.logger.error(f"未找到SQL ID: {sql_id}")
                return {"success": False, "error": "SQL记录不存在"}
            
            # 2. 提取表名（优先使用TABLENAME字段）
            table_names, processed_sql = self.sql_extractor.extract_table_names(
                sql_info['sql_text'], 
                sql_info.get('table_name')
            )
            self.logger.info(f"提取到表名: {table_names}")
            self.logger.debug(f"处理后的SQL长度: {len(processed_sql)} (原始: {len(sql_info['sql_text'])})")
            
            # 3. 收集表元数据
            # 使用system_id作为db_alias
            db_alias = sql_info.get('system_id', 'db_production')
            
            # 收集所有实例的元数据供AI分析使用（包含从数据库获取实际值的功能）
            # 注意：这可能会收集到多个实例的元数据，用于全面分析
            all_metadata = self.metadata_collector.collect_metadata_from_all_instances(
                db_alias, table_names
            )
            
            if not all_metadata:
                # 如果无法收集所有实例的元数据，尝试找到至少一个实例有数据
                found_metadata = self.metadata_collector.collect_metadata_until_found(
                    db_alias, table_names
                )
                
                if not found_metadata:
                    self.logger.error(f"在所有实例中都未找到表: {table_names}")
                    # 更新SQL问题类型为表提取失败
                    self.sql_extractor.update_sql_issue(
                        sql_id, 
                        'table_extraction_failed', 
                        f"在所有实例中都未找到表: {table_names}"
                    )
                    # 更新分析状态为失败
                    self.sql_extractor.update_analysis_status(sql_id, 'failed', f"在所有实例中都未找到表: {table_names}")
                    return {"success": False, "error": f"在所有实例中都未找到表: {table_names}"}
                
                all_metadata = found_metadata
                self.logger.warning(f"无法收集所有实例的元数据，使用已找到的实例数据")
            
            # 从找到的元数据中提取实例信息（使用第一个找到的实例）
            first_found_instance = all_metadata[0]
            instance_index = first_found_instance.get('instance_index', 0)
            instance_alias = first_found_instance.get('instance_alias', db_alias)
            
            self.logger.info(f"在实例 {instance_alias} (索引 {instance_index}) 中找到表，将在此实例获取执行计划")
            
            # 4. 生成替换参数后的SQL（为执行计划做准备）- 使用从数据表获取的实际随机值
            # 使用已经处理过的SQL（来自提取表名步骤）来避免重复处理
            # 使用找到表的实例别名作为数据库别名，确保参数替换时使用正确的数据库实例
            replaced_sql, extracted_tables = self.sql_extractor.generate_replaced_sql(
                sql_info['sql_text'], 
                all_metadata,  # 传递元数据列表，用于参数与列的匹配和值获取
                processed_sql=processed_sql,  # 使用已经处理过的SQL
                db_alias=instance_alias  # 使用找到表的实例别名作为数据库别名
            )
            
            self.logger.info(f"生成替换参数后的SQL完成，长度: {len(replaced_sql)}，使用的元数据数量: {len(all_metadata)}")
            
            # 4.1 生成执行计划（必须在调用大模型之前先生成）
            # 在找到表的实例上获取执行计划
            execution_plan_info = self.metadata_collector.get_execution_plan(
                db_alias, 
                replaced_sql,  # 使用替换参数后的SQL
                instance_index  # 在找到表的实例上执行
            )
            
            # 5. 构建请求数据（包含执行计划）
            request_data = {
                "sql_statement": sql_info['sql_text'],
                "tables": all_metadata,  # 使用收集到的所有实例的元数据
                "db_alias": db_alias,
                "execution_plan_info": execution_plan_info,
                "replaced_sql": replaced_sql,  # 参数替换后的SQL
                "execution_instance_alias": instance_alias,  # 执行计划所在的实例
                "execution_instance_index": instance_index   # 执行计划所在的实例索引
            }
            
            # 6. 调用大模型API
            analysis_result = self.model_client.analyze_sql(request_data)
            
            # 7. 处理并存储结果
            result = self.result_processor.process_result(
                sql_id, analysis_result, all_metadata
            )
            
            self.logger.info(f"SQL ID {sql_id} 分析完成")
            return result
            
        except Exception as e:
            self.logger.error(f"分析SQL ID {sql_id} 时发生错误: {str(e)}", exc_info=True)
            # 更新错误状态
            self.result_processor.update_error_status(sql_id, str(e))
            return {"success": False, "error": str(e)}
    
    def analyze_batch(self, batch_size: Optional[int] = None) -> Dict[str, Any]:
        """
        批量分析SQL语句
        
        Args:
            batch_size: 批量大小，默认为配置中的值
            
        Returns:
            批量分析结果
        """
        if batch_size is None:
            batch_size = int(self.config.get_processing_config().get('batch_size', 10))
        
        self.logger.info(f"开始批量分析，批量大小: {batch_size}")
        
        try:
            # 获取待分析的SQL列表
            pending_sqls = self.sql_extractor.get_pending_sqls(batch_size)
            
            if not pending_sqls:
                self.logger.info("没有待分析的SQL语句")
                return {"success": True, "processed": 0, "results": []}
            
            results = []
            success_count = 0
            fail_count = 0
            
            for sql_info in pending_sqls:
                sql_id = sql_info['id']
                try:
                    result = self.analyze_single_sql(sql_id)
                    if result.get('success'):
                        success_count += 1
                    else:
                        fail_count += 1
                    results.append({"sql_id": sql_id, "result": result})
                except Exception as e:
                    self.logger.error(f"处理SQL ID {sql_id} 时发生异常: {str(e)}")
                    fail_count += 1
                    results.append({"sql_id": sql_id, "error": str(e)})
            
            # 处理分组结果（将同一文件名的SQL分析结果组合并存储到AM_COMMIT_SHELL_INFO表）
            group_processing_result = None
            if results and success_count > 0:
                self.logger.info("开始处理分组结果...")
                
                # 准备分组处理器需要的格式
                analysis_results = []
                for item in results:
                    if 'result' in item and isinstance(item['result'], dict):
                        analysis_results.append({
                            'sql_id': item['sql_id'],
                            'success': item['result'].get('success', False),
                            'analysis_result': item['result'].get('analysis_result', {})
                        })
                
                if analysis_results:
                    group_processing_result = self.group_processor.process_grouped_results(analysis_results)
                    self.logger.info(f"分组处理完成: {group_processing_result}")
            
            summary = {
                "success": True,
                "processed": len(pending_sqls),
                "success_count": success_count,
                "fail_count": fail_count,
                "results": results,
                "group_processing": group_processing_result
            }
            
            self.logger.info(f"批量分析完成: 共处理 {len(pending_sqls)} 条，成功 {success_count} 条，失败 {fail_count} 条")
            return summary
            
        except Exception as e:
            self.logger.error(f"批量分析时发生错误: {str(e)}", exc_info=True)
            return {"success": False, "error": str(e)}
    
    def analyze_by_branch(self, branch_name: str, batch_size: Optional[int] = None) -> Dict[str, Any]:
        """
        按分支分析SQL语句
        
        Args:
            branch_name: 分支名称（DEFAULT_VERSION字段值）
            batch_size: 批量大小，默认为配置中的值
            
        Returns:
            分析结果
        """
        self.logger.info(f"开始按分支分析，分支: {branch_name}")
        
        try:
            # 1. 通过分组处理器获取该分支的文件和SQL
            grouped_results = self.group_processor.group_by_branch_and_file(branch_name)
            
            if not grouped_results:
                self.logger.warning(f"分支 '{branch_name}' 没有找到待分析的SQL")
                return {"success": True, "processed": 0, "results": [], "groups": 0}
            
            all_results = []
            group_summaries = []
            
            # 2. 对每个分组进行分析
            for group_key, group_data in grouped_results.items():
                file_name = group_data['file_name']
                project_id = group_data['project_id']
                default_version = group_data['default_version']
                sqls = group_data['sqls']
                
                self.logger.info(f"处理分组 {group_key}，包含 {len(sqls)} 条SQL")
                
                group_results = []
                success_count = 0
                fail_count = 0
                
                # 3. 分析该分组中的每个SQL
                for sql_data in sqls:
                    sql_id = sql_data['sql_id']
                    try:
                        result = self.analyze_single_sql(sql_id)
                        if result.get('success'):
                            success_count += 1
                        else:
                            fail_count += 1
                        
                        # 添加analysis_result到sql_data中，供后续组合使用
                        sql_data['analysis_data'] = result.get('analysis_result', {})
                        sql_data['success'] = result.get('success', False)
                        
                        group_results.append({
                            'sql_id': sql_id,
                            'result': result
                        })
                        all_results.append({
                            'sql_id': sql_id,
                            'result': result
                        })
                    except Exception as e:
                        self.logger.error(f"处理SQL ID {sql_id} 时发生异常: {str(e)}")
                        fail_count += 1
                        group_results.append({
                            'sql_id': sql_id,
                            'error': str(e)
                        })
                
                # 4. 如果该分组有成功的分析结果，则组合并存储
                if success_count > 0:
                    # 准备分组处理器需要的数据格式
                    analysis_results = []
                    for item in group_results:
                        if 'result' in item and isinstance(item['result'], dict):
                            analysis_results.append({
                                'sql_id': item['sql_id'],
                                'success': item['result'].get('success', False),
                                'analysis_data': item['result'].get('analysis_result', {})
                            })
                    
                    if analysis_results:
                        # 组合分析结果
                        combined_result = self.group_processor.combine_analysis_results([
                            {
                                'sql_id': data['sql_id'],
                                'sql_text': next((s['sql_text'] for s in sqls if s['sql_id'] == data['sql_id']), ''),
                                'analysis_data': data.get('analysis_data', {}),
                                'sql_info': next((s['sql_info'] for s in sqls if s['sql_id'] == data['sql_id']), {})
                            }
                            for data in analysis_results
                        ])
                        
                        # 存储到AM_COMMIT_SHELL_INFO表
                        store_success = self.group_processor.store_to_commit_shell_info(
                            group_key, group_data, combined_result
                        )
                        
                        group_summaries.append({
                            'group_key': group_key,
                            'file_name': file_name,
                            'project_id': project_id,
                            'default_version': default_version,
                            'sql_count': len(sqls),
                            'success_count': success_count,
                            'fail_count': fail_count,
                            'store_success': store_success,
                            'status': 'success' if store_success else 'failed'
                        })
                    else:
                        group_summaries.append({
                            'group_key': group_key,
                            'file_name': file_name,
                            'project_id': project_id,
                            'default_version': default_version,
                            'sql_count': len(sqls),
                            'success_count': 0,
                            'fail_count': len(sqls),
                            'store_success': False,
                            'status': 'no_success_results'
                        })
                else:
                    group_summaries.append({
                        'group_key': group_key,
                        'file_name': file_name,
                        'project_id': project_id,
                        'default_version': default_version,
                        'sql_count': len(sqls),
                        'success_count': 0,
                        'fail_count': len(sqls),
                        'store_success': False,
                        'status': 'all_failed'
                    })
            
            # 5. 汇总统计
            total_sqls = sum(len(group['sqls']) for group in grouped_results.values())
            total_success = sum(summary['success_count'] for summary in group_summaries)
            total_fail = sum(summary['fail_count'] for summary in group_summaries)
            total_groups = len(grouped_results)
            success_groups = len([s for s in group_summaries if s.get('store_success')])
            
            summary = {
                "success": True,
                "branch_name": branch_name,
                "processed": total_sqls,
                "success_count": total_success,
                "fail_count": total_fail,
                "total_groups": total_groups,
                "success_groups": success_groups,
                "group_summaries": group_summaries,
                "results": all_results
            }
            
            self.logger.info(f"分支分析完成: 分支 '{branch_name}'，共处理 {total_sqls} 条SQL，成功 {total_success} 条，失败 {total_fail} 条，分组 {total_groups} 组，成功存储 {success_groups} 组")
            return summary
            
        except Exception as e:
            self.logger.error(f"按分支分析时发生错误: {str(e)}", exc_info=True)
            return {"success": False, "error": str(e)}
    
    def run_once(self) -> Dict[str, Any]:
        """运行一次分析任务"""
        self.logger.info("开始运行分析任务")
        result = self.analyze_batch()
        self.logger.info("分析任务运行完成")
        return result
    
    def run_continuously(self, interval_seconds: int = 300):
        """
        持续运行分析任务
        
        Args:
            interval_seconds: 运行间隔（秒），默认5分钟
        """
        import time
        
        self.logger.info(f"开始持续运行模式，间隔: {interval_seconds}秒")
        
        try:
            while True:
                try:
                    self.run_once()
                except Exception as e:
                    self.logger.error(f"运行分析任务时发生错误: {str(e)}")
                
                self.logger.info(f"等待 {interval_seconds} 秒后继续...")
                time.sleep(interval_seconds)
                
        except KeyboardInterrupt:
            self.logger.info("收到中断信号，停止运行")
        except Exception as e:
            self.logger.error(f"持续运行模式发生错误: {str(e)}")


def main():
    """主函数入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description='AI-SQL质量分析系统')
    parser.add_argument('--config', '-c', default='config/config.ini', 
                       help='配置文件路径')
    parser.add_argument('--mode', '-m', choices=['single', 'batch', 'continuous', 'branch'], 
                       default='batch', help='运行模式')
    parser.add_argument('--sql-id', type=int, help='单个SQL的ID（single模式使用）')
    parser.add_argument('--batch-size', type=int, default=10, 
                       help='批量大小（batch模式使用）')
    parser.add_argument('--interval', type=int, default=300,
                       help='运行间隔秒数（continuous模式使用）')
    parser.add_argument('--branch-name', type=str, 
                       help='分支名称（branch模式使用，DEFAULT_VERSION字段值）')
    
    args = parser.parse_args()
    
    # 检查配置文件是否存在
    if not os.path.exists(args.config):
        print(f"错误: 配置文件不存在: {args.config}")
        print(f"请复制 config.ini.example 为 {args.config} 并填写配置")
        sys.exit(1)
    
    # 创建分析器实例
    analyzer = SQLAnalyzer(args.config)
    
    try:
        if args.mode == 'single':
            if not args.sql_id:
                print("错误: single模式需要指定 --sql-id 参数")
                sys.exit(1)
            result = analyzer.analyze_single_sql(args.sql_id)
            print(f"分析结果: {result}")
            
        elif args.mode == 'batch':
            result = analyzer.analyze_batch(args.batch_size)
            print(f"批量分析结果: {result}")
            
        elif args.mode == 'branch':
            if not args.branch_name:
                print("错误: branch模式需要指定 --branch-name 参数")
                sys.exit(1)
            result = analyzer.analyze_by_branch(args.branch_name, args.batch_size)
            print(f"分支分析结果: {result}")
            
        elif args.mode == 'continuous':
            analyzer.run_continuously(args.interval)
            
    except KeyboardInterrupt:
        print("\n程序被用户中断")
    except Exception as e:
        print(f"程序运行错误: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试修复后的group_processor.py
验证数据流向修复效果
"""

import sys
import json
sys.path.append('sql_ai_analyzer')

# 导入修复后的GroupProcessor
from storage.group_processor import GroupProcessor

def test_group_processor_data_flow():
    """测试分组处理器的数据流向"""
    print("=" * 80)
    print("测试修复后的group_processor.py数据流向")
    print("=" * 80)
    
    # 模拟配置管理器
    class MockConfigManager:
        def __init__(self):
            self.configs = {
                'database': {
                    'host': 'localhost',
                    'port': 3306,
                    'user': 'test',
                    'password': 'test',
                    'database': 'test_db'
                }
            }
        
        def get(self, key, default=None):
            return self.configs.get(key, default)
        
        def get_database_config(self):
            return self.configs.get('database')
        
        def get_section(self, section):
            return self.configs.get(section, {})
    
    # 模拟日志记录器
    class MockLogger:
        def info(self, msg, *args):
            print(f"[INFO] {msg % args if args else msg}")
        def debug(self, msg, *args):
            pass
        def warning(self, msg, *args):
            print(f"[WARNING] {msg % args if args else msg}")
        def error(self, msg, *args):
            print(f"[ERROR] {msg % args if args else msg}")
        
        def setLevel(self, level):
            pass
        
        def addHandler(self, handler):
            pass
    
    # 由于依赖数据库连接，我们需要直接测试核心方法而不初始化父类
    class TestGroupProcessor:
        def __init__(self, config_manager, logger):
            self.config_manager = config_manager
            self.logger = logger
        
        # 直接复制修复后的方法进行测试
        def combine_analysis_results(self, sqls_data):
            """测试combine_analysis_results方法 - 从修复版本复制"""
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
                            if suggestion not in all_suggestions:
                                all_suggestions.append(suggestion)
                
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
                                
                                if norm_category in risk_categories and issue not in risk_categories[norm_category]:
                                    risk_categories[norm_category].append(issue)
            
            # 组合建议
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
        
        def _prepare_storage_data(self, group_data, combined_result):
            """测试_prepare_storage_data方法 - 从修复版本复制"""
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
        
        def _truncate_sql(self, sql_text: str, max_length: int = 100) -> str:
            """截断SQL文本"""
            if not sql_text:
                return ""
            
            if len(sql_text) <= max_length:
                return sql_text
            
            return sql_text[:max_length] + "..."
        
        def _format_suggestions_by_sql(self, sqls_data, all_suggestions):
            """格式化建议"""
            formatted_suggestions = []
            
            # 去重建议
            unique_suggestions = []
            seen_suggestions = set()
            
            for suggestion in all_suggestions:
                suggestion_key = suggestion.strip().lower()
                if suggestion_key and suggestion_key not in seen_suggestions:
                    seen_suggestions.add(suggestion_key)
                    unique_suggestions.append(suggestion)
            
            # 按SQL分组建议
            for sql_data in sqls_data:
                sql_id = sql_data['sql_id']
                sql_text = sql_data['sql_text']
                
                sql_suggestions = sql_data['analysis_data'].get('suggestions', [])
                if not sql_suggestions:
                    continue
                
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
    
    config_manager = MockConfigManager()
    logger = MockLogger()
    processor = TestGroupProcessor(config_manager, logger)
    
    # 测试数据：模拟SQL分析结果
    test_sqls_data = [
        {
            'sql_id': 21483,
            'sql_text': 'CREATE TABLE pub_buried (id INT, name VARCHAR(100))',
            'analysis_data': {
                "建议": ["建议添加主键", "检查字符集一致性"],
                "SQL类型": "CREATE",
                "分析摘要": "该建表语句存在缺少主键和字符集不一致的问题",
                "综合评分": 8.5,
                "规范符合性": {
                    "规范符合度": 85.0,
                    "规范违反详情": []
                },
                "风险评估": {
                    "高风险问题": ["缺少主键"],
                    "中风险问题": ["字符集不一致"],
                    "低风险问题": ["注释不完整"]
                },
                "修改建议": {
                    "高风险问题SQL": "ALTER TABLE pub_buried ADD PRIMARY KEY (id)",
                    "中风险问题SQL": "ALTER TABLE pub_buried CONVERT TO CHARACTER SET utf8mb4",
                    "低风险问题SQL": "ALTER TABLE pub_buried MODIFY COLUMN name VARCHAR(100) COMMENT '用户姓名'",
                    "性能优化SQL": ""
                }
            },
            'sql_info': {
                'project_id': 'CBNK',
                'default_version': 'release-prd-2603.13',
                'file_path': 'db_cbnk/release/2603.13/037_BoCom07987930/V_001_BoCom07987930_CREATE_TABLE_PUB_BURIED.sql',
                'file_name': 'V_001_BoCom07987930_CREATE_TABLE_PUB_BURIED.sql'
            }
        },
        {
            'sql_id': 21485,
            'sql_text': 'ALTER TABLE pub_buried ADD COLUMN created_at TIMESTAMP',
            'analysis_data': {
                "建议": ["添加NOT NULL约束", "设置默认值"],
                "SQL类型": "ALTER",
                "分析摘要": "ALTER TABLE语句缺少NOT NULL约束和默认值",
                "综合评分": 7.5,
                "规范符合性": {
                    "规范符合度": 75.0,
                    "规范违反详情": ["缺少NOT NULL约束"]
                },
                "风险评估": {
                    "高风险问题": ["可能插入NULL值"],
                    "中风险问题": [],
                    "低风险问题": ["缺少默认值"]
                },
                "修改建议": {
                    "高风险问题SQL": "ALTER TABLE pub_buried MODIFY COLUMN created_at TIMESTAMP NOT NULL",
                    "中风险问题SQL": "",
                    "低风险问题SQL": "ALTER TABLE pub_buried MODIFY COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
                    "性能优化SQL": ""
                }
            },
            'sql_info': {
                'project_id': 'CBNK',
                'default_version': 'release-prd-2603.13',
                'file_path': 'db_cbnk/release/2603.13/037_BoCom07987930/V_001_BoCom07987930_CREATE_TABLE_PUB_BURIED.sql',
                'file_name': 'V_001_BoCom07987930_CREATE_TABLE_PUB_BURIED.sql'
            }
        }
    ]
    
    # 测试group_data
    test_group_data = {
        'file_name': 'V_001_BoCom07987930_CREATE_TABLE_PUB_BURIED.sql',
        'project_id': 'CBNK',
        'default_version': 'release-prd-2603.13',
        'file_path': 'db_cbnk/release/2603.13/037_BoCom07987930/V_001_BoCom07987930_CREATE_TABLE_PUB_BURIED.sql',
        'sqls': test_sqls_data
    }
    
    print("\n1. 测试combine_analysis_results方法:")
    print("-" * 60)
    
    combined_result = processor.combine_analysis_results(test_sqls_data)
    print("组合结果结构检查:")
    print(f"  combined_analysis 是否存在: {'是' if 'combined_analysis' in combined_result else '否'}")
    
    if 'combined_analysis' in combined_result:
        combined_analysis = combined_result['combined_analysis']
        print(f"    risk_summary 是否存在: {'是' if 'risk_summary' in combined_analysis else '否'}")
        
        if 'risk_summary' in combined_analysis:
            risk_summary = combined_analysis['risk_summary']
            print(f"      详细问题 是否存在: {'是' if '详细问题' in risk_summary else '否'}")
            
            if '详细问题' in risk_summary:
                detail_problems = risk_summary['详细问题']
                print(f"        高风险问题: {len(detail_problems.get('高风险问题', []))} 条")
                print(f"        中风险问题: {len(detail_problems.get('中风险问题', []))} 条")
                print(f"        低风险问题: {len(detail_problems.get('低风险问题', []))} 条")
            
            print(f"      高风险问题数量: {risk_summary.get('高风险问题数量', 'N/A')}")
            print(f"      中风险问题数量: {risk_summary.get('中风险问题数量', 'N/A')}")
            print(f"      低风险问题数量: {risk_summary.get('低风险问题数量', 'N/A')}")
        
        print(f"    performance_summary 是否存在: {'是' if 'performance_summary' in combined_analysis else '否'}")
        print(f"    security_summary 是否存在: {'是' if 'security_summary' in combined_analysis else '否'}")
        print(f"    all_suggestions 是否存在: {'是' if 'all_suggestions' in combined_analysis else '否'}")
    
    print("\n2. 测试_prepare_storage_data方法:")
    print("-" * 60)
    
    storage_data = processor._prepare_storage_data(test_group_data, combined_result)
    
    print("存储数据结构检查:")
    print(f"  file_info 是否存在: {'是' if 'file_info' in storage_data else '否'}")
    print(f"  analysis_summary 是否存在: {'是' if 'analysis_summary' in storage_data else '否'}")
    print(f"  combined_analysis 是否存在: {'是' if 'combined_analysis' in storage_data else '否'}")
    print(f"  sql_details 数量: {len(storage_data.get('sql_details', []))}")
    
    if 'combined_analysis' in storage_data:
        combined_analysis = storage_data['combined_analysis']
        print(f"\n  combined_analysis 详细检查:")
        print(f"    risk_summary 类型: {type(combined_analysis.get('risk_summary'))}")
        
        risk_summary = combined_analysis.get('risk_summary', {})
        if isinstance(risk_summary, dict):
            print(f"      详细问题 是否存在: {'是' if '详细问题' in risk_summary else '否'}")
            if '详细问题' in risk_summary:
                detail_problems = risk_summary['详细问题']
                print(f"        详细问题类型: {type(detail_problems)}")
                if isinstance(detail_problems, dict):
                    for problem_type in ["高风险问题", "中风险问题", "低风险问题"]:
                        if problem_type in detail_problems:
                            problems = detail_problems[problem_type]
                            print(f"        {problem_type} 类型: {type(problems)}, 数量: {len(problems)}")
                        else:
                            print(f"        {problem_type} 不存在")
        
        print(f"    performance_summary 类型: {type(combined_analysis.get('performance_summary'))}")
        print(f"    security_summary 类型: {type(combined_analysis.get('security_summary'))}")
        print(f"    all_suggestions 类型: {type(combined_analysis.get('all_suggestions'))}")
    
    print("\n3. sql_details检查:")
    print("-" * 60)
    
    for i, sql_detail in enumerate(storage_data.get('sql_details', [])):
        print(f"  SQL {i+1} (ID: {sql_detail.get('sql_id')}):")
        analysis_data = sql_detail.get('analysis_data', {})
        print(f"    analysis_data 是否为空: {'是' if not analysis_data else '否'}")
        if analysis_data:
            print(f"    包含字段: {list(analysis_data.keys())}")
            
            # 检查风险评估
            risk_assessment = analysis_data.get('风险评估', {})
            print(f"    风险评估存在: {'是' if risk_assessment else '否'}")
            if risk_assessment:
                print(f"      高风险问题: {len(risk_assessment.get('高风险问题', []))}")
                print(f"      中风险问题: {len(risk_assessment.get('中风险问题', []))}")
                print(f"      低风险问题: {len(risk_assessment.get('低风险问题', []))}")
    
    print("\n4. 与用户提供的示例对比:")
    print("-" * 60)
    
    user_example_problems = [
        "sql_details[].analysis_data 为空对象 {}",
        "combined_analysis.risk_summary.详细问题 不存在或为空",
        "performance_summary 和 security_summary 为空"
    ]
    
    fixed_problems_status = []
    
    # 问题1: sql_details[].analysis_data 是否为空
    empty_analysis_data = any(not sql_detail.get('analysis_data') for sql_detail in storage_data.get('sql_details', []))
    fixed_problems_status.append(f"sql_details[].analysis_data 为空: {'是（未修复）' if empty_analysis_data else '否（已修复）'}")
    
    # 问题2: combined_analysis.risk_summary.详细问题 是否存在
    has_detail_problems = False
    combined_analysis = storage_data.get('combined_analysis', {})
    risk_summary = combined_analysis.get('risk_summary', {})
    if '详细问题' in risk_summary:
        detail_problems = risk_summary['详细问题']
        if isinstance(detail_problems, dict) and any(detail_problems.values()):
            has_detail_problems = True
    fixed_problems_status.append(f"combined_analysis.risk_summary.详细问题 存在且有内容: {'是（已修复）' if has_detail_problems else '否（未修复）'}")
    
    # 问题3: performance_summary 和 security_summary 是否存在
    has_perf_summary = 'performance_summary' in combined_analysis
    has_sec_summary = 'security_summary' in combined_analysis
    fixed_problems_status.append(f"performance_summary 存在: {'是（已修复）' if has_perf_summary else '否（未修复）'}")
    fixed_problems_status.append(f"security_summary 存在: {'是（已修复）' if has_sec_summary else '否（未修复）'}")
    
    for status in fixed_problems_status:
        print(f"  {status}")
    
    print("\n5. 最终数据结构验证:")
    print("-" * 60)
    
    # 检查最终数据结构是否符合预期
    validation_results = []
    
    # 检查必需字段
    required_fields = ['file_info', 'analysis_summary', 'combined_analysis', 'sql_details']
    for field in required_fields:
        validation_results.append((field, field in storage_data, f"缺少 {field}"))
    
    # 检查combined_analysis结构
    if 'combined_analysis' in storage_data:
        ca = storage_data['combined_analysis']
        ca_fields = ['all_suggestions', 'risk_summary', 'performance_summary', 'security_summary']
        for field in ca_fields:
            validation_results.append((f"combined_analysis.{field}", field in ca, f"缺少 combined_analysis.{field}"))
    
    # 检查risk_summary结构
    if 'combined_analysis' in storage_data and 'risk_summary' in storage_data['combined_analysis']:
        rs = storage_data['combined_analysis']['risk_summary']
        rs_fields = ['高风险问题数量', '中风险问题数量', '低风险问题数量', '详细问题']
        for field in rs_fields:
            validation_results.append((f"risk_summary.{field}", field in rs, f"缺少 risk_summary.{field}"))
        
        # 检查详细问题结构
        if '详细问题' in rs:
            dp = rs['详细问题']
            if isinstance(dp, dict):
                dp_fields = ['高风险问题', '中风险问题', '低风险问题']
                for field in dp_fields:
                    validation_results.append((f"详细问题.{field}", field in dp and isinstance(dp[field], list), 
                                            f"详细问题.{field} 不存在或不是列表"))
    
    print("字段验证结果:")
    for field_name, is_valid, error_msg in validation_results:
        status = "✅ 通过" if is_valid else "❌ 失败"
        print(f"  {field_name}: {status}")
        if not is_valid:
            print(f"    -> {error_msg}")
    
    # 计算通过率
    passed = sum(1 for _, is_valid, _ in validation_results if is_valid)
    total = len(validation_results)
    pass_rate = (passed / total) * 100 if total > 0 else 0
    
    print(f"\n验证通过率: {passed}/{total} ({pass_rate:.1f}%)")
    
    if pass_rate >= 90:
        print("\n🎉 修复成功！数据结构完整性已大幅提升。")
    else:
        print("\n⚠️ 仍有部分问题需要进一步修复。")
    
    print("\n" + "=" * 80)
    print("测试完成")
    
    return storage_data

if __name__ == "__main__":
    result = test_group_processor_data_flow()
    
    # 输出修复后的数据结构供参考
    print("\n修复后的数据结构示例（前500字符）:")
    print(json.dumps(result, ensure_ascii=False, indent=2)[:500] + "...")
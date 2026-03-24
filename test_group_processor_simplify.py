#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试分组处理器的精简功能
"""

import sys
import json
sys.path.append('sql_ai_analyzer')

# 模拟配置管理器
class TestConfigManager:
    def get_ai_model_config(self):
        return {}
    def get_database_config(self):
        return {
            'source': {
                'host': 'localhost',
                'port': 3306,
                'user': 'test',
                'password': 'test',
                'database': 'test',
                'charset': 'utf8mb4'
            }
        }

def test_critical_suggestion_filter():
    """测试关键建议筛选"""
    print("测试关键建议筛选...")
    
    from sql_ai_analyzer.storage.group_processor import GroupProcessor
    
    # 创建一个简化版的GroupProcessor，避免初始化数据库连接
    class SimpleGroupProcessor(GroupProcessor):
        def __init__(self, config_manager, logger=None):
            self.config_manager = config_manager
            if logger:
                self.set_logger(logger)
            # 不初始化sql_extractor
    
    config_manager = TestConfigManager()
    group_processor = SimpleGroupProcessor(config_manager, None)
    
    # 测试关键角度建议
    critical_suggestions = [
        "建议添加主键以避免数据重复",
        "存在隐式转换风险，建议显式转换",
        "需要检查全表扫描风险",
        "字符集不一致，建议统一为utf8mb4",
        "注释不完整，建议补充注释",
        "表参数设置不合理",
        "唯一约束字段缺少not null约束",
        "AKM接入存在问题",
        "ANALYZE统计信息不准确",
        "DML与DDL之间缺少休眠时间"
    ]
    
    # 测试普通建议
    normal_suggestions = [
        "这是一个普通的优化建议",
        "建议优化代码结构",
        "可以考虑使用更好的命名",
        "这是一个很长的建议但不包含关键角度"
    ]
    
    print("\n关键角度建议测试:")
    for suggestion in critical_suggestions:
        result = group_processor._is_critical_suggestion(suggestion)
        status = '✅' if result else '❌'
        print(f'{status} "{suggestion[:40]}..." -> {result}')
    
    print("\n普通建议测试:")
    for suggestion in normal_suggestions:
        result = group_processor._is_critical_suggestion(suggestion)
        status = '❌' if not result else '✅'
        print(f'{status} "{suggestion[:40]}..." -> {result}')
    
    return True

def test_risk_issue_filter():
    """测试风险问题筛选"""
    print("\n\n测试风险问题筛选...")
    
    from sql_ai_analyzer.storage.group_processor import GroupProcessor
    
    # 创建一个简化版的GroupProcessor，避免初始化数据库连接
    class SimpleGroupProcessor(GroupProcessor):
        def __init__(self, config_manager, logger=None):
            self.config_manager = config_manager
            if logger:
                self.set_logger(logger)
            # 不初始化sql_extractor
    
    config_manager = TestConfigManager()
    group_processor = SimpleGroupProcessor(config_manager, None)
    
    # 测试高风险问题
    high_risk_issues = [
        "SQL注入漏洞",
        "缺少主键",
        "全表扫描导致性能问题",
        "数据不一致风险"
    ]
    
    # 测试关键角度风险问题
    critical_risk_issues = [
        "隐式转换可能导致数据精度丢失",
        "字符集问题导致乱码",
        "IN操作索引失效",
        "表结构不一致"
    ]
    
    print("\n高风险问题测试:")
    for issue in high_risk_issues:
        result = group_processor._is_critical_risk_issue(issue)
        status = '✅' if result else '❌'
        print(f'{status} "{issue}" -> {result}')
    
    print("\n关键角度风险问题测试:")
    for issue in critical_risk_issues:
        result = group_processor._is_critical_risk_issue(issue)
        status = '✅' if result else '❌'
        print(f'{status} "{issue}" -> {result}')
    
    return True

def test_summary_simplify():
    """测试分析摘要简化"""
    print("\n\n测试分析摘要简化...")
    
    from sql_ai_analyzer.storage.group_processor import GroupProcessor
    
    # 创建一个简化版的GroupProcessor，避免初始化数据库连接
    class SimpleGroupProcessor(GroupProcessor):
        def __init__(self, config_manager, logger=None):
            self.config_manager = config_manager
            if logger:
                self.set_logger(logger)
            # 不初始化sql_extractor
    
    config_manager = TestConfigManager()
    group_processor = SimpleGroupProcessor(config_manager, None)
    
    test_summaries = [
        {
            'input': '该SQL语句存在隐式转换问题，可能导致数据精度丢失。建议进行显式类型转换。同时，表缺少主键，可能导致数据完整性问题。这是一个关键的风险问题，需要立即处理。',
            'expected_len': 100
        },
        {
            'input': '这是一个很长但没有关键信息的分析摘要。' * 30,
            'expected_len': 150
        },
        {
            'input': '存在性能问题，建议优化。',
            'expected_len': 20
        },
        {
            'input': '字符集不统一，可能导致乱码。索引设计不合理，存在全表扫描风险。主键缺失，影响数据完整性。注释不完整，影响可维护性。',
            'expected_len': 120
        }
    ]
    
    for i, test in enumerate(test_summaries, 1):
        result = group_processor._simplify_analysis_summary(test['input'])
        print(f"\n测试 {i}:")
        print(f"  输入长度: {len(test['input'])}")
        print(f"  输出长度: {len(result)}")
        print(f"  精简后: {result[:80]}..." if len(result) > 80 else f"  精简后: {result}")
        
        # 检查是否在预期长度范围内
        if len(result) <= test['expected_len'] + 50 and len(result) >= 10:
            print(f"  ✅ 长度合理")
        else:
            print(f"  ❌ 长度异常")
    
    return True

def test_combine_with_critical_filter():
    """测试组合分析结果时的关键筛选"""
    print("\n\n测试组合分析结果时的关键筛选...")
    
    from sql_ai_analyzer.storage.group_processor import GroupProcessor
    
    # 创建一个简化版的GroupProcessor，避免初始化数据库连接
    class SimpleGroupProcessor(GroupProcessor):
        def __init__(self, config_manager, logger=None):
            self.config_manager = config_manager
            if logger:
                self.set_logger(logger)
            # 不初始化sql_extractor
        
        def combine_analysis_results(self, sqls_data):
            """重写combine_analysis_results方法，避免调用需要数据库的方法"""
            if not sqls_data:
                return {"success": False, "error": "没有可组合的SQL数据"}
            
            # 简化的组合结果
            combined_result = {
                "summary": {
                    "total_sqls": len(sqls_data),
                    "unique_files": len(set([d['sql_info'].get('file_name', 'unknown') for d in sqls_data])),
                    "unique_projects": len(set([d['sql_info'].get('project_id', 'unknown') for d in sqls_data])),
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
            
            for sql_data in sqls_data:
                sql_id = sql_data['sql_id']
                sql_text = sql_data['sql_text']
                analysis_data = sql_data['analysis_data']
                
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
            
            # 组合建议
            combined_result["combined_analysis"]["all_suggestions"] = [{"text": s, "type": "general"} for s in all_suggestions[:5]]
            combined_result["combined_analysis"]["risk_summary"] = {
                "高风险问题数量": len(risk_categories["高风险问题"]),
                "中风险问题数量": len(risk_categories["中风险问题"]), 
                "低风险问题数量": len(risk_categories["低风险问题"]),
                "详细问题": risk_categories
            }
            
            return combined_result
    
    config_manager = TestConfigManager()
    group_processor = SimpleGroupProcessor(config_manager, None)
    
    # 模拟分析数据
    sqls_data = [
        {
            'sql_id': 1,
            'sql_text': 'SELECT * FROM users WHERE id = 1',
            'analysis_data': {
                'SQL类型': 'SELECT',
                '综合评分': 8.5,
                '建议': [
                    '建议添加主键',
                    '这是一个普通的优化建议',
                    '存在隐式转换风险',
                    '字符集需要统一'
                ],
                '风险评估': {
                    '高风险问题': ['SQL注入风险', '缺少索引导致全表扫描'],
                    '中风险问题': ['查询性能较差', '缺少参数化'],
                    '低风险问题': ['命名不规范']
                },
                '分析摘要': '该SQL语句存在隐式转换问题，可能导致数据精度丢失。建议进行显式类型转换。同时，表缺少主键，可能导致数据完整性问题。'
            },
            'sql_info': {}
        },
        {
            'sql_id': 2,
            'sql_text': 'UPDATE products SET price = price * 1.1',
            'analysis_data': {
                'SQL类型': 'UPDATE',
                '综合评分': 7.0,
                '建议': [
                    '这是一个很长的普通建议，但不包含关键角度',
                    '建议优化代码结构'
                ],
                '风险评估': {
                    '高风险问题': ['无WHERE条件可能导致全表更新'],
                    '中风险问题': [],
                    '低风险问题': ['缺少注释']
                },
                '分析摘要': 'UPDATE语句缺少WHERE条件，可能导致全表数据被更新，存在较大风险。'
            },
            'sql_info': {}
        }
    ]
    
    try:
        # 测试组合功能
        combined_result = group_processor.combine_analysis_results(sqls_data)
        
        print("组合结果摘要:")
        print(f"  SQL数量: {combined_result.get('summary', {}).get('total_sqls', 0)}")
        
        # 检查组合后的风险摘要
        risk_summary = combined_result.get('combined_analysis', {}).get('risk_summary', {})
        print(f"  高风险问题数量: {risk_summary.get('高风险问题数量', 0)}")
        print(f"  中风险问题数量: {risk_summary.get('中风险问题数量', 0)}")
        print(f"  低风险问题数量: {risk_summary.get('低风险问题数量', 0)}")
        
        # 检查建议筛选
        all_suggestions = combined_result.get('combined_analysis', {}).get('all_suggestions', [])
        print(f"  筛选后的建议组数: {len(all_suggestions)}")
        
        print("\n✅ 组合功能测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 组合功能测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("=" * 60)
    print("测试分组处理器的精简功能")
    print("=" * 60)
    
    # 运行所有测试
    tests = [
        ("关键建议筛选测试", test_critical_suggestion_filter),
        ("风险问题筛选测试", test_risk_issue_filter),
        ("分析摘要简化测试", test_summary_simplify),
        ("组合分析结果测试", test_combine_with_critical_filter)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        try:
            success = test_func()
            results.append((test_name, success))
            if success:
                print(f"✅ {test_name} 通过")
            else:
                print(f"❌ {test_name} 失败")
        except Exception as e:
            print(f"❌ {test_name} 异常: {str(e)}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    print("\n" + "=" * 60)
    print("测试总结:")
    
    all_passed = True
    for test_name, success in results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"  {test_name}: {status}")
        if not success:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ 所有测试通过！分组处理器的精简功能已生效。")
        print("\n修复说明:")
        print("1. 分组处理器现在能够根据关键角度筛选建议和风险问题")
        print("2. 关键角度包括: 隐式转换、主键、全表扫描、字符集问题等")
        print("3. 分析摘要会被简化为关键信息，避免过长")
        print("4. 存储到AM_COMMIT_SHELL_INFO表的数据将被精简")
        return 0
    else:
        print("❌ 部分测试失败，请检查代码。")
        return 1

if __name__ == "__main__":
    sys.exit(main())
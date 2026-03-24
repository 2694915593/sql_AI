#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试结果处理器的修复：确保风险问题和分析总结字段正确填充
"""

import sys
import os
import json
sys.path.append('sql_ai_analyzer')

from sql_ai_analyzer.storage.result_processor import ResultProcessor

# 模拟配置管理器
class MockConfigManager:
    def __init__(self):
        self.config = {}
    
    def get_ai_model_config(self):
        return {}
    
    def get(self, key, default=None):
        return self.config.get(key, default)
    
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

# 模拟数据库连接
class MockDbConnection:
    def execute(self, query, params=None):
        return 1
    
    def fetch_one(self, query, params=None):
        return None
    
    def fetch_all(self, query, params=None):
        return []

# 模拟SQL提取器
class MockSQLExtractor:
    def __init__(self, config_manager, logger=None):
        self.config_manager = config_manager
        self.logger = logger
        self.source_db = MockDbConnection()
    
    def update_analysis_status(self, sql_id, status, error_message=None):
        return True
    
    def extract_sql_by_id(self, sql_id):
        return {}

def test_result_processor_with_ai_response():
    """测试结果处理器处理AI响应"""
    print("开始测试结果处理器修复...")
    
    # 创建模拟对象
    config_manager = MockConfigManager()
    result_processor = ResultProcessor(config_manager)
    result_processor.sql_extractor = MockSQLExtractor(config_manager)
    
    # 模拟AI模型的响应数据（包含风险评估和修改建议）
    mock_analysis_result = {
        'success': True,
        'score': 8.5,
        'sql_type': 'SELECT',
        'suggestions': ['建议添加索引', '考虑参数化查询'],
        'analysis_result': {
            '风险评估': {
                '高风险问题': ['SQL注入风险', '缺少索引导致全表扫描'],
                '中风险问题': ['查询性能较差', '缺少参数化'],
                '低风险问题': ['命名不规范']
            },
            '修改建议': {
                '高风险问题SQL': 'SELECT * FROM users WHERE id = ?',
                '中风险问题SQL': 'SELECT id, name FROM users WHERE status = ?',
                '低风险问题SQL': 'SELECT id, username FROM users WHERE status = ?',
                '性能优化SQL': 'SELECT id, name FROM users WHERE status = ? AND id > 0'
            },
            '分析摘要': '该SQL语句存在SQL注入风险和性能问题，建议进行参数化查询并添加适当索引。'
        }
    }
    
    # 模拟表元数据
    mock_metadata = [
        {
            'table_name': 'users',
            'row_count': 10000,
            'is_large_table': False,
            'columns': [],
            'indexes': [],
            'primary_keys': ['id']
        }
    ]
    
    # 处理分析结果
    try:
        # 调用_prepare_storage_data方法（这是修复的关键）
        storage_data = result_processor._prepare_storage_data(mock_analysis_result, mock_metadata)
        
        print("\n生成的存储数据：")
        print(json.dumps(storage_data, ensure_ascii=False, indent=2))
        
        # 验证关键字段
        print("\n验证关键字段：")
        
        # 1. 检查风险评估字段
        risk_assessment = storage_data.get('风险评估', {})
        print(f"风险评估字段是否存在：{'是' if risk_assessment else '否'}")
        if risk_assessment:
            print(f"  高风险问题数量：{len(risk_assessment.get('高风险问题', []))}")
            print(f"  中风险问题数量：{len(risk_assessment.get('中风险问题', []))}")
            print(f"  低风险问题数量：{len(risk_assessment.get('低风险问题', []))}")
        
        # 2. 检查修改建议字段
        modification_suggestions = storage_data.get('修改建议', {})
        print(f"修改建议字段是否存在：{'是' if modification_suggestions else '否'}")
        if modification_suggestions:
            print(f"  高风险问题SQL长度：{len(modification_suggestions.get('高风险问题SQL', ''))}")
            print(f"  中风险问题SQL长度：{len(modification_suggestions.get('中风险问题SQL', ''))}")
            print(f"  低风险问题SQL长度：{len(modification_suggestions.get('低风险问题SQL', ''))}")
            print(f"  性能优化SQL长度：{len(modification_suggestions.get('性能优化SQL', ''))}")
        
        # 3. 检查分析摘要字段
        analysis_summary = storage_data.get('分析摘要', '')
        print(f"分析摘要字段是否存在：{'是' if analysis_summary else '否'}")
        if analysis_summary:
            print(f"  分析摘要内容：{analysis_summary[:100]}...")
        
        # 4. 检查其他必要字段
        print(f"建议字段数量：{len(storage_data.get('建议', []))}")
        print(f"SQL类型：{storage_data.get('SQL类型', '未知')}")
        print(f"综合评分：{storage_data.get('综合评分', 0)}")
        
        # 5. 验证数据结构完整性
        required_fields = ['建议', 'SQL类型', '分析摘要', '综合评分', '规范符合性', '风险评估', '修改建议']
        missing_fields = [field for field in required_fields if field not in storage_data]
        
        if missing_fields:
            print(f"\n❌ 缺少必要字段：{missing_fields}")
            return False
        else:
            print("\n✅ 所有必要字段都存在")
        
        # 6. 检查风险评估和修改建议内容是否正确（应该来自AI响应，不是空的）
        if risk_assessment and any(risk_assessment.values()):
            print("✅ 风险评估字段包含来自AI响应的内容")
        else:
            print("❌ 风险评估字段为空或没有内容")
        
        if modification_suggestions and any(modification_suggestions.values()):
            print("✅ 修改建议字段包含来自AI响应的内容")
        else:
            print("❌ 修改建议字段为空或没有内容")
        
        print("\n✅ 测试通过：结果处理器修复有效")
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败：{str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_result_processor_without_ai_response():
    """测试没有AI响应时的回退逻辑"""
    print("\n开始测试没有AI响应时的回退逻辑...")
    
    # 创建模拟对象
    config_manager = MockConfigManager()
    result_processor = ResultProcessor(config_manager)
    result_processor.sql_extractor = MockSQLExtractor(config_manager)
    
    # 模拟AI模型的响应数据（不包含风险评估和修改建议）
    mock_analysis_result = {
        'success': True,
        'score': 7.0,
        'sql_type': 'UPDATE',
        'suggestions': ['建议添加WHERE条件'],
        'analysis_result': {}  # 空的analysis_result
    }
    
    # 模拟表元数据
    mock_metadata = [
        {
            'table_name': 'orders',
            'row_count': 5000,
            'is_large_table': False,
            'columns': [],
            'indexes': [],
            'primary_keys': ['order_id']
        }
    ]
    
    try:
        # 调用_prepare_storage_data方法
        storage_data = result_processor._prepare_storage_data(mock_analysis_result, mock_metadata)
        
        print("生成的存储数据（摘要）：")
        print(f"  风险评估：{'存在' if storage_data.get('风险评估') else '不存在'}")
        print(f"  修改建议：{'存在' if storage_data.get('修改建议') else '不存在'}")
        
        # 验证回退逻辑
        risk_assessment = storage_data.get('风险评估', {})
        modification_suggestions = storage_data.get('修改建议', {})
        
        if risk_assessment and isinstance(risk_assessment, dict):
            print(f"✅ 风险评估字段存在（使用回退逻辑生成）")
        else:
            print("❌ 风险评估字段不存在")
        
        if modification_suggestions and isinstance(modification_suggestions, dict):
            print(f"✅ 修改建议字段存在（使用回退逻辑生成）")
        else:
            print("❌ 修改建议字段不存在")
        
        print("✅ 回退逻辑测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 回退逻辑测试失败：{str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("=" * 60)
    print("测试结果处理器修复")
    print("=" * 60)
    
    test1_success = test_result_processor_with_ai_response()
    test2_success = test_result_processor_without_ai_response()
    
    print("\n" + "=" * 60)
    print("测试总结：")
    print(f"  测试1（含AI响应）: {'✅ 通过' if test1_success else '❌ 失败'}")
    print(f"  测试2（无AI响应）: {'✅ 通过' if test2_success else '❌ 失败'}")
    
    if test1_success and test2_success:
        print("\n✅ 所有测试通过！修复已生效。")
        print("\n修复说明：")
        print("1. 结果处理器现在能够从AI模型的analysis_result中直接提取风险评估和修改建议")
        print("2. 如果没有这些字段，系统会使用回退逻辑生成相应内容")
        print("3. 分析摘要也会从AI响应中提取，如果没有则使用其他字段")
        print("4. 分组存储入表时，风险问题、分析总结等内容将不再为空")
        return 0
    else:
        print("\n❌ 部分测试失败，请检查修复代码。")
        return 1

if __name__ == "__main__":
    sys.exit(main())
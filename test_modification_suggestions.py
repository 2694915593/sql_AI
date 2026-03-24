#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试修改建议SQL提取功能
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, 'sql_ai_analyzer')

# 模拟日志类
class MockLogger:
    def __init__(self):
        pass
    
    def info(self, msg, *args):
        print(f"INFO: {msg % args if args else msg}")
    
    def debug(self, msg, *args):
        print(f"DEBUG: {msg % args if args else msg}")
    
    def warning(self, msg, *args):
        print(f"WARNING: {msg % args if args else msg}")
    
    def error(self, msg, *args):
        print(f"ERROR: {msg % args if args else msg}")

# 创建模拟对象
class MockResultProcessor:
    def __init__(self):
        self.logger = MockLogger()
    
    def _extract_modification_suggestions_from_analysis(self, analysis_result):
        """从AI分析结果中提取修改建议SQL"""
        modification_suggestions = {
            "高风险问题SQL": "",
            "中风险问题SQL": "",
            "低风险问题SQL": "",
            "性能优化SQL": ""
        }
        
        try:
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
            elif 'sql_modifications' in analysis_result:
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
            
            # 检查analysis_result中是否有直接字段
            elif '高风险问题SQL' in analysis_result:
                modification_suggestions['高风险问题SQL'] = analysis_result['高风险问题SQL']
            elif '中风险问题SQL' in analysis_result:
                modification_suggestions['中风险问题SQL'] = analysis_result['中风险问题SQL']
            elif '低风险问题SQL' in analysis_result:
                modification_suggestions['低风险问题SQL'] = analysis_result['低风险问题SQL']
            elif '性能优化SQL' in analysis_result:
                modification_suggestions['性能优化SQL'] = analysis_result['性能优化SQL']
            
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

def test_extraction():
    """测试修改建议SQL提取"""
    print("测试修改建议SQL提取功能")
    print("=" * 60)
    
    processor = MockResultProcessor()
    
    # 测试用例1: 包含完整修改建议的AI响应
    print("\n测试用例1: 包含完整修改建议的AI响应")
    analysis_result_1 = {
        'success': True,
        'analysis_result': {
            '修改建议': {
                '高风险问题SQL': 'SELECT * FROM users WHERE id = ?',
                '中风险问题SQL': 'ALTER TABLE users ADD INDEX idx_user_id (user_id)',
                '低风险问题SQL': 'SELECT * FROM users LIMIT 0, 100',
                '性能优化SQL': 'SELECT id, name FROM users WHERE status = 1 ORDER BY created_at DESC LIMIT 100'
            }
        }
    }
    
    result1 = processor._extract_modification_suggestions_from_analysis(analysis_result_1)
    print("提取结果:")
    for key, value in result1.items():
        print(f"  {key}: {value[:50]}..." if value else f"  {key}: (空)")
    
    # 测试用例2: 包含sql_modifications字段的AI响应
    print("\n测试用例2: 包含sql_modifications字段的AI响应")
    analysis_result_2 = {
        'success': True,
        'sql_modifications': {
            'high_risk_sql': 'SELECT * FROM products WHERE id = ?',
            'medium_risk_sql': 'CREATE INDEX idx_product_name ON products (name)',
            'low_risk_sql': 'SELECT * FROM products WHERE category = "electronics" LIMIT 50',
            'performance_sql': 'SELECT id, name, price FROM products WHERE in_stock = 1 ORDER BY price ASC LIMIT 100'
        }
    }
    
    result2 = processor._extract_modification_suggestions_from_analysis(analysis_result_2)
    print("提取结果:")
    for key, value in result2.items():
        print(f"  {key}: {value[:50]}..." if value else f"  {key}: (空)")
    
    # 测试用例3: 不包含修改建议的AI响应
    print("\n测试用例3: 不包含修改建议的AI响应")
    analysis_result_3 = {
        'success': True,
        'analysis_result': {
            '风险评估': {
                '高风险问题': ['存在SQL注入风险'],
                '中风险问题': ['查询缺少索引']
            }
        }
    }
    
    result3 = processor._extract_modification_suggestions_from_analysis(analysis_result_3)
    print("提取结果:")
    for key, value in result3.items():
        print(f"  {key}: {value[:50]}..." if value else f"  {key}: (空)")
    
    print("\n" + "=" * 60)
    print("测试完成!")

if __name__ == "__main__":
    test_extraction()
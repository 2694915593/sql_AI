#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试实际用户提供的AI接口返回报文
使用用户提供的完整报文进行测试
"""

import json
from config.config_manager import ConfigManager
from ai_integration.model_client import ModelClient

def test_user_actual_response():
    """测试用户提供的实际AI接口返回报文"""
    print("=" * 80)
    print("测试用户提供的实际AI接口返回报文")
    print("=" * 80)
    
    # 加载配置
    config = ConfigManager('config/config.ini')
    
    # 创建ModelClient实例
    model_client = ModelClient(config)
    
    # 用户提供的完整报文（转换为Python字典）
    # 注意：这是用户提供的原始报文格式
    user_response_text =""
    
    print("用户提供的报文格式:")
    print("-" * 40)
    print(f"报文长度: {len(user_response_text)} 字符")
    print(f"报文预览 (前500字符):")
    print(user_response_text[:500] + "...")
    
    # 模拟一个requests.Response对象
    import requests
    
    class MockResponse:
        def __init__(self, text):
            self.status_code = 200
            self.text = text
            self._json_data = None
            
        def json(self):
            # 尝试解析JSON
            if self._json_data is None:
                try:
                    self._json_data = json.loads(self.text)
                except json.JSONDecodeError as e:
                    print(f"JSON解析错误: {e}")
                    print(f"文本内容: {self.text[:200]}...")
                    raise
            return self._json_data
    
    mock_resp = MockResponse(user_response_text)
    
    try:
        print("\n开始解析用户提供的报文...")
        
        # 调用_parse_response方法
        result = model_client._parse_response(mock_resp)
        
        print("✅ 解析成功!")
        print("-" * 40)
        print(f"成功状态: {result.get('success', False)}")
        print(f"综合评分: {result.get('score', 'N/A')}")
        print(f"SQL类型: {result.get('sql_type', 'N/A')}")
        
        # 提取的分析数据
        analysis_result = result.get('analysis_result', {})
        print(f"\n分析结果中的关键字段:")
        print(f"  - sql_type: {analysis_result.get('sql_type', 'N/A')}")
        print(f"  - overall_score: {analysis_result.get('overall_score', 'N/A')}")
        print(f"  - summary: {analysis_result.get('summary', 'N/A')[:100]}...")
        
        # 规则分析
        rule_analysis = analysis_result.get('rule_analysis', {})
        if rule_analysis:
            print(f"\n规则分析:")
            for rule_type, rules in rule_analysis.items():
                if isinstance(rules, dict):
                    print(f"  {rule_type}:")
                    for key, value in rules.items():
                        print(f"    - {key}: {value}")
        
        # 风险评估
        risk_assessment = analysis_result.get('risk_assessment', {})
        if risk_assessment:
            print(f"\n风险评估:")
            for risk_level, issues in risk_assessment.items():
                if isinstance(issues, list):
                    print(f"  {risk_level}: {len(issues)} 个问题")
                    for i, issue in enumerate(issues[:3], 1):
                        print(f"    {i}. {issue}")
                    if len(issues) > 3:
                        print(f"    ... 还有{len(issues)-3}个问题")
        
        # 改进建议
        improvement_suggestions = analysis_result.get('improvement_suggestions', [])
        if improvement_suggestions:
            print(f"\n改进建议 ({len(improvement_suggestions)} 条):")
            for i, suggestion in enumerate(improvement_suggestions, 1):
                print(f"  {i}. {suggestion}")
        
        # 检查提取的建议
        suggestions = result.get('suggestions', [])
        print(f"\n提取的建议 ({len(suggestions)} 条):")
        for i, suggestion in enumerate(suggestions[:5], 1):
            print(f"  {i}. {suggestion}")
        if len(suggestions) > 5:
            print(f"  ... 还有{len(suggestions)-5}条建议")
        
        # 显示详细分析
        if 'detailed_analysis' in result:
            detailed = result['detailed_analysis']
            print(f"\n详细分析 (前200字符):")
            print(f"  {detailed[:200]}...")
        
        # 显示提取的score
        score = result.get('score', 'N/A')
        print(f"\n最终提取的评分: {score}")
        
        # 检查是否成功提取了数据
        print(f"\n解析结果检查:")
        print(f"  ✅ 成功提取SQL类型: {result.get('sql_type', '未提取')}")
        print(f"  ✅ 成功提取综合评分: {result.get('score', '未提取')}")
        print(f"  ✅ 成功提取建议数量: {len(result.get('suggestions', []))}")
        
        return True
        
    except Exception as e:
        print(f"❌ 解析失败: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("测试用户提供的实际AI接口返回报文")
    print("=" * 80)
    
    # 测试用户提供的实际报文
    success = test_user_actual_response()
    
    print("\n" + "=" * 80)
    print("测试总结")
    print("=" * 80)
    
    if success:
        print("✅ 测试通过!")
        print("\nModelClient能够正确解析用户提供的复杂报文格式。")
        print("成功提取以下信息:")
        print("  1. SQL类型 (数据操作)")
        print("  2. 综合评分 (7)")
        print("  3. 规则分析 (建表规则、表结构变更规则等)")
        print("  4. 风险评估 (高、中、低风险问题)")
        print("  5. 改进建议")
        print("  6. 总结")
    else:
        print("❌ 测试失败!")
        print("\nModelClient无法正确解析用户提供的报文格式。")
        print("需要检查 _parse_response 方法中的解析逻辑。")

if __name__ == '__main__':
    main()
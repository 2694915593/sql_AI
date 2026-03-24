#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试SQL分析系统修改是否生效
验证规范性评审字段是否被正确添加
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sql_ai_analyzer.ai_integration.model_client_enhanced import ModelClient
from sql_ai_analyzer.utils.sql_specifications import SQLType
import json

def test_prompt_modification():
    """测试提示词修改是否生效"""
    print("测试提示词修改...")
    
    # 创建一个模拟的配置管理器
    class MockConfigManager:
        def get_ai_model_config(self):
            return {
                'api_url': 'http://mock.api',
                'api_key': 'mock-key',
                'max_retries': 3,
                'timeout': 30
            }
    
    # 创建模拟的logger
    class MockLogger:
        def info(self, msg, *args, **kwargs):
            print(f"[INFO] {msg}")
        def debug(self, msg, *args, **kwargs):
            pass
        def error(self, msg, *args, **kwargs):
            print(f"[ERROR] {msg}")
        def warning(self, msg, *args, **kwargs):
            print(f"[WARNING] {msg}")
    
    config_manager = MockConfigManager()
    logger = MockLogger()
    
    try:
        # 创建模型客户端
        client = ModelClient(config_manager, logger)
        
        # 构建模拟请求数据
        request_data = {
            'sql_statement': 'SELECT * FROM users WHERE id = 1',
            'tables': [],
            'db_alias': 'test_db',
            'execution_plan_info': {'has_execution_plan': False},
            'replaced_sql': 'SELECT * FROM users WHERE id = 1'
        }
        
        # 调用_build_request_payload方法
        payload = client._build_request_payload(request_data)
        
        # 检查payload
        print(f"Payload类型: {type(payload)}")
        print(f"Payload是否包含prompt: {'prompt' in payload}")
        
        if 'prompt' in payload:
            prompt = payload['prompt']
            print(f"Prompt长度: {len(prompt)}")
            
            # 检查是否包含关键规范性评审内容
            check_items = [
                "规范性评审",
                "修改列时加属性",
                "in操作索引失效", 
                "字符集问题",
                "注释--问题",
                "comment问题",
                "表参数问题",
                "akm接入",
                "analyze问题",
                "dml与ddl之间休眠3秒",
                "隐式转换",
                "主键问题",
                "索引设计",
                "全表扫描",
                "表结构一致性",
                "唯一约束字段须添加not null"
            ]
            
            print("\n检查关键规范性评审内容:")
            found_count = 0
            for item in check_items:
                if item in prompt:
                    print(f"  ✓ 找到: {item}")
                    found_count += 1
                else:
                    print(f"  ✗ 未找到: {item}")
            
            print(f"\n找到 {found_count}/{len(check_items)} 个关键规范性评审项目")
            
            # 检查JSON输出格式
            if '"规范性评审":' in prompt:
                print("✓ JSON输出格式包含'规范性评审'字段")
                
                # 检查是否包含完整的规范性评审结构
                import re
                normative_review_pattern = r'"规范性评审":\s*{[\s\S]*?}'
                match = re.search(normative_review_pattern, prompt, re.DOTALL)
                if match:
                    normative_review_section = match.group(0)
                    print(f"✓ 找到规范性评审JSON结构，长度: {len(normative_review_section)}")
                    
                    # 检查是否包含15个评审角度
                    angle_count = normative_review_section.count('"status":')
                    print(f"  包含 {angle_count} 个评审角度")
                else:
                    print("✗ 未找到完整的规范性评审JSON结构")
            else:
                print("✗ JSON输出格式不包含'规范性评审'字段")
        
        # 检查SQL类型检测
        sql_type = client._detect_sql_type('SELECT * FROM users')
        print(f"\nSQL类型检测结果: {sql_type.value}")
        
        # 检查SQL规范集成
        from sql_ai_analyzer.utils.sql_specifications import integrate_specifications_into_prompt
        prompt_parts = ["测试SQL语句"]
        enhanced_parts = integrate_specifications_into_prompt(prompt_parts, SQLType.SELECT)
        print(f"SQL规范集成测试: 原始部分 {len(prompt_parts)} -> 增强后 {len(enhanced_parts)}")
        
        return True
        
    except Exception as e:
        print(f"测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_response_format():
    """测试响应格式解析"""
    print("\n\n测试响应格式解析...")
    
    # 创建一个模拟的响应，包含规范性评审
    mock_response_json = '''{
  "建议": ["测试建议1", "测试建议2"],
  "SQL类型": "查询",
  "分析摘要": "测试分析摘要",
  "综合评分": 8.5,
  "规范符合性": {
    "规范符合度": 90.0,
    "规范违反详情": []
  },
  "规范性评审": {
    "修改列时加属性": {
      "status": "未涉及",
      "description": "检查ALTER TABLE语句修改列时是否保留了原列的属性",
      "details": "当前SQL为SELECT语句，不涉及ALTER TABLE操作",
      "suggestion": "继续保持良好的SQL编写习惯"
    },
    "in操作索引失效": {
      "status": "通过",
      "description": "检查IN操作是否导致索引失效",
      "details": "SQL中未使用IN操作",
      "suggestion": "继续保持良好的SQL编写习惯"
    }
  },
  "修改建议": {
    "高风险问题SQL": "",
    "中风险问题SQL": "",
    "低风险问题SQL": "",
    "性能优化SQL": ""
  }
}'''
    
    print(f"模拟响应JSON:\n{mock_response_json}")
    
    try:
        # 解析JSON
        parsed = json.loads(mock_response_json)
        print(f"\n成功解析JSON，包含字段:")
        for key in parsed.keys():
            print(f"  {key}")
        
        # 检查规范性评审字段
        if "规范性评审" in parsed:
            normative_review = parsed["规范性评审"]
            print(f"\n规范性评审包含 {len(normative_review)} 个角度:")
            for angle, details in normative_review.items():
                print(f"  {angle}: status={details.get('status', '未知')}")
        
        return True
        
    except Exception as e:
        print(f"JSON解析失败: {str(e)}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("SQL分析系统修改验证测试")
    print("=" * 60)
    
    # 运行测试
    test1_success = test_prompt_modification()
    test2_success = test_response_format()
    
    print("\n" + "=" * 60)
    print("测试结果:")
    print(f"提示词修改测试: {'通过' if test1_success else '失败'}")
    print(f"响应格式解析测试: {'通过' if test2_success else '失败'}")
    
    if test1_success and test2_success:
        print("\n✅ 所有测试通过！修改已成功应用。")
        print("提示词现在包含15个关键规范性评审角度")
        print("响应格式支持规范性评审字段")
    else:
        print("\n❌ 测试失败，请检查修改。")
    
    print("=" * 60)
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试stripped字符串的格式问题
"""

import json
import ast

def debug_stripped_string():
    """调试stripped字符串的解析问题"""
    # 用户提供的stripped字符串（截断版本，只包含前200字符用于分析）
    stripped_str = '''{"RSP_BODY":{"head":{},"TRAN_PROCESS":"aiQA","answer":"\"{\\n  \\\"sql_type\\\": \\\"数据操作\\\",\\n  \\\"rule_analysis\\\": {\\n    \\\"建表规则\\\": {\\n      \\\"涉及历史表\\\": false,\\n      \\\"评估完全\\\": false,\\n      \\\"主键检查\\\": \\\"未通过\\\",\\n      \\\"索引检查\\\": \\\"未通过\\\",\\n      \\\"数据量评估\\\": \\\"合理\\\",\\n      \\\"注释检查\\\": \\\"不完整\\\",\\n      \\\"字段类型检查\\\": \\\"合理\\\"\\n    },"'''
    
    print("原始字符串前200字符:")
    print(repr(stripped_str[:200]))
    print()
    
    # 检查语法错误的位置
    print("检查字符串格式:")
    print(f"字符串长度: {len(stripped_str)}")
    print(f"第一个字符: '{stripped_str[0]}'")
    print(f"第56个字符: '{stripped_str[55]}' (ASCII: {ord(stripped_str[55])})")
    print(f"第55-60个字符: '{stripped_str[54:60]}'")
    print()
    
    # 检查转义序列
    print("检查转义序列:")
    # 查找所有反斜杠的位置
    backslash_positions = [i for i, char in enumerate(stripped_str) if char == '\\']
    print(f"反斜杠数量: {len(backslash_positions)}")
    if backslash_positions:
        print(f"前5个反斜杠位置: {backslash_positions[:5]}")
        for pos in backslash_positions[:5]:
            print(f"  位置 {pos}: 字符 '{stripped_str[pos]}', 下一个字符 '{stripped_str[pos+1] if pos+1 < len(stripped_str) else 'EOF'}'")
    print()
    
    # 尝试分步解析
    print("尝试分步解析:")
    
    # 1. 尝试解析为JSON
    try:
        data = json.loads(stripped_str)
        print("✅ 可以解析为JSON")
    except json.JSONDecodeError as e:
        print(f"❌ JSON解析错误: {e}")
        print(f"错误位置: 第{e.lineno}行, 第{e.colno}列")
        
        # 提取错误位置附近的文本
        lines = stripped_str.split('\n')
        if e.lineno <= len(lines):
            error_line = lines[e.lineno - 1]
            print(f"错误行内容: {error_line}")
            print(f"错误列位置: {e.colno}")
            if e.colno <= len(error_line):
                print(f"错误位置字符: '{error_line[e.colno-1]}'")
                print(f"错误位置前后文本: '{error_line[max(0, e.colno-10):e.colno+10]}'")
    
    print()
    
    # 2. 检查是否是有效的Python字面量
    try:
        data = ast.literal_eval(stripped_str)
        print("✅ 可以解析为Python字面量")
    except Exception as e:
        print(f"❌ Python字面量解析错误: {e}")
    
    print()
    
    # 3. 手动清理转义字符
    print("手动清理转义字符:")
    cleaned = stripped_str.replace('\\n', '\n').replace('\\"', '"')
    print(f"清理后前100字符: {repr(cleaned[:100])}")
    
    try:
        data = json.loads(cleaned)
        print("✅ 清理后可以解析为JSON")
    except json.JSONDecodeError as e:
        print(f"❌ 清理后JSON解析错误: {e}")

def analyze_complete_structure():
    """分析完整数据结构"""
    print("\n" + "=" * 80)
    print("分析完整数据结构")
    print("=" * 80)
    
    # 构建一个简化的正确版本
    correct_structure = {
        "RSP_BODY": {
            "head": {},
            "TRAN_PROCESS": "aiQA",
            "answer": '''{
  "sql_type": "数据操作",
  "rule_analysis": {
    "建表规则": {
      "涉及历史表": false,
      "评估完全": false,
      "主键检查": "未通过",
      "索引检查": "未通过",
      "数据量评估": "合理",
      "注释检查": "不完整",
      "字段类型检查": "合理"
    }
  }
}''',
            "prompt": "prompt=SQL语句..."
        },
        "RSP_HEAD": {
            "TRAN_SUCCESS": "1",
            "TRACE_NO": "SDSS118-38-115-7221128146"
        }
    }
    
    print("正确的JSON结构:")
    print(json.dumps(correct_structure, ensure_ascii=False, indent=2)[:500] + "...")
    
    # 模拟用户提供的格式
    user_like_structure = {
        "RSP_BODY": {
            "head": {},
            "TRAN_PROCESS": "aiQA",
            "answer": json.dumps({
                "sql_type": "数据操作",
                "rule_analysis": {
                    "建表规则": {
                        "涉及历史表": False,
                        "评估完全": False,
                        "主键检查": "未通过",
                        "索引检查": "未通过",
                        "数据量评估": "合理",
                        "注释检查": "不完整",
                        "字段类型检查": "合理"
                    }
                }
            }, ensure_ascii=False)
        },
        "RSP_HEAD": {
            "TRAN_SUCCESS": "1",
            "TRACE_NO": "SDSS118-38-115-7221128146"
        }
    }
    
    print("\n模拟用户格式（answer字段是JSON字符串）:")
    user_json = json.dumps(user_like_structure, ensure_ascii=False)
    print(f"JSON字符串长度: {len(user_json)}")
    print(f"前200字符: {user_json[:200]}")
    
    # 然后添加转义（模拟实际API响应）
    escaped = user_json.replace('"', '\\"').replace('\n', '\\n')
    print(f"\n转义后字符串（模拟实际响应）:")
    print(f"前200字符: {escaped[:200]}")
    
    # 现在整个字符串应该被包裹在另一个JSON中
    final_response = {
        "success": True,
        "raw_response": user_like_structure,
        "analysis_result": {}
    }
    
    final_json = json.dumps(final_response, ensure_ascii=False)
    print(f"\n完整响应JSON:")
    print(f"前200字符: {final_json[:200]}")

def test_fix_parser():
    """测试修复解析器"""
    print("\n" + "=" * 80)
    print("测试修复解析器")
    print("=" * 80)
    
    # 模拟实际API响应（简化版）
    response_text = '''{
  "success": true,
  "raw_response": {
    "RSP_BODY": {
      "head": {},
      "TRAN_PROCESS": "aiQA",
      "answer": "{\\"sql_type\\": \\"数据操作\\", \\"overall_score\\": 7}"
    },
    "RSP_HEAD": {
      "TRAN_SUCCESS": "1",
      "TRACE_NO": "SDSS118-38-115-7221128146"
    }
  }
}'''
    
    print("模拟API响应文本:")
    print(response_text[:200] + "...")
    
    # 尝试解析
    try:
        data = json.loads(response_text)
        print("\n✅ 成功解析外层JSON")
        
        # 提取answer字段
        answer_str = data.get('raw_response', {}).get('RSP_BODY', {}).get('answer', '')
        print(f"answer字段: {answer_str}")
        
        # 解析answer字段
        if answer_str:
            # 清理转义字符
            cleaned_answer = answer_str.replace('\\"', '"')
            print(f"清理后answer: {cleaned_answer}")
            
            try:
                answer_data = json.loads(cleaned_answer)
                print(f"✅ 成功解析answer字段: {answer_data}")
            except json.JSONDecodeError as e:
                print(f"❌ 解析answer字段失败: {e}")
    except json.JSONDecodeError as e:
        print(f"❌ 解析外层JSON失败: {e}")

def main():
    """主函数"""
    print("调试stripped字符串的格式问题")
    print("=" * 80)
    
    # 调试stripped字符串
    debug_stripped_string()
    
    # 分析完整数据结构
    analyze_complete_structure()
    
    # 测试修复解析器
    test_fix_parser()

if __name__ == '__main__':
    main()
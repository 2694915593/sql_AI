#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试JSON字符串的具体字符问题
"""

import json

def debug_json_char_position():
    """调试JSON字符串的字符位置问题"""
    # 用户提供的原始字符串
    stripped_str = '''{"RSP_BODY":{"head":{},"TRAN_PROCESS":"aiQA","answer":"\"{\\n  \\\"sql_type\\\": \\\"数据操作\\\",\\n  \\\"rule_analysis\\\": {\\n    \\\"建表规则\\\": {\\n      \\\"涉及历史表\\\": false,\\n      \\\"评估完全\\\": false,\\n      \\\"主键检查\\\": \\\"未通过\\\",\\n      \\\"索引检查\\\": \\\"未通过\\\",\\n      \\\"数据量评估\\\": \\\"合理\\\",\\n      \\\"注释检查\\\": \\\"不完整\\\",\\n      \\\"字段类型检查\\\": \\\"合理\\\"\\n    },\\n    \\\"表结构变更规则\\\": {\\n      \\\"涉及历史表\\\": false,\\n      \\\"评估完全\\\": false,\\n      \\\"影响范围评估\\\": \\\"不完整\\\",\\n      \\\"联机影响评估\\\": \\\"合理\\\",\\n      \\\"注释检查\\\": \\\"不完整\\\"\\n    },\\n    \\\"索引规则\\\": {\\n      \\\"索引冗余检查\\\": \\\"无冗余\\\",\\n      \\\"索引总数\\\": 0,\\n      \\\"索引设计合理性\\\": \\\"不合理\\\",\\n      \\\"执行计划分析\\\": \\\"无\\\"\\n    },\\n    \\\"数据量规则\\\": {\\n      \\\"数据量级别\\\": \\\"十万以下\\\",\\n      \\\"SQL耗时评估\\\": \\\"毫秒级\\\",\\n      \\\"备份策略\\\": \\\"无\\\",\\n      \\\"数据核对\\\": \\\"未核对\\\"\\n    }\\n  },\\n  \\\"risk_assessment\\\": {\\n    \\\"高风险问题\\\": [],\\n    \\\"中风险问题\\\": [\\\"表无主键和索引，可能影响查询性能\\\", \\\"未进行数据核对，可能导致数据不一致\\\"],\\n    \\\"低风险问题\\\": [\\\"表和字段注释不完整\\\", \\\"未提供备份策略\\\"]\\n  },\\n  \\\"improvement_suggestions\\\": [\\\"为表添加主键和必要的索引\\\", \\\"完善表和字段的注释\\\", \\\"制定数据核对流程\\\", \\\"考虑数据备份策略\\\"],\\n  \\\"overall_score\\\": 7,\\n  \\\"summary\\\": \\\"该SQL语句为数据插入操作，当前表无主键和索引，这可能会影响未来的查询性能。此外，表和字段的注释不完整，缺少数据核对和备份策略。建议改进上述方面以提高系统的稳定性和可维护性。\\\"\\n}\"","prompt":"prompt=SQL语句..."},"RSP_HEAD":{"TRAN_SUCCESS":"1","TRACE_NO":"SDSS118-38-115-7221128146"}}'''
    
    print("调试JSON字符位置问题")
    print("=" * 80)
    
    # 显示前100个字符的详细分析
    print("原始字符串前100字符:")
    print(repr(stripped_str[:100]))
    print()
    
    # 显示第50-70个字符的详细分析
    print("第50-70字符分析:")
    for i in range(50, 71):
        char = stripped_str[i] if i < len(stripped_str) else 'EOF'
        ascii_val = ord(char) if char != 'EOF' else -1
        print(f"  位置 {i}: 字符 '{char}' (ASCII: {ascii_val})")
    print()
    
    # 检查问题位置
    print("检查问题位置（第56个字符）:")
    print(f"  第55个字符: '{stripped_str[54] if 54 < len(stripped_str) else 'EOF'}'")
    print(f"  第56个字符: '{stripped_str[55] if 55 < len(stripped_str) else 'EOF'}'")
    print(f"  第57个字符: '{stripped_str[56] if 56 < len(stripped_str) else 'EOF'}'")
    print(f"  第55-60个字符: {repr(stripped_str[54:60])}")
    print()
    
    # 尝试手动修复双重引号问题
    print("尝试修复双重引号问题:")
    fixed_str = stripped_str.replace('""{', '"{')
    print(f"  修复后前100字符: {repr(fixed_str[:100])}")
    print(f"  修复后第55-60字符: {repr(fixed_str[54:60])}")
    
    # 尝试解析修复后的字符串
    print("\n尝试解析修复后的字符串:")
    try:
        data = json.loads(fixed_str)
        print("  ✅ 修复后JSON解析成功")
        print(f"  解析结果键: {list(data.keys())}")
        
        # 检查RSP_BODY
        if 'RSP_BODY' in data:
            rsp_body = data['RSP_BODY']
            print(f"  RSP_BODY字段: {list(rsp_body.keys())}")
            
            # 检查answer字段
            if 'answer' in rsp_body:
                answer = rsp_body['answer']
                print(f"  answer字段类型: {type(answer)}")
                print(f"  answer字段长度: {len(answer)}")
                print(f"  answer前100字符: {repr(answer[:100])}")
                
                # 尝试解析answer字段
                try:
                    answer_data = json.loads(answer)
                    print("  ✅ 成功解析answer字段")
                    print(f"    SQL类型: {answer_data.get('sql_type')}")
                    print(f"    综合评分: {answer_data.get('overall_score')}")
                except json.JSONDecodeError as e:
                    print(f"  ❌ 解析answer字段失败: {e}")
                    
                    # 清理answer字段中的转义字符
                    cleaned_answer = answer.replace('\\n', '\n').replace('\\"', '"')
                    print(f"  清理后answer前100字符: {repr(cleaned_answer[:100])}")
                    
                    # 如果以引号开头和结尾，移除它们
                    cleaned_answer_stripped = cleaned_answer.strip()
                    if cleaned_answer_stripped.startswith('"') and cleaned_answer_stripped.endswith('"'):
                        cleaned_answer_stripped = cleaned_answer_stripped[1:-1]
                        print(f"  移除最外层引号后前100字符: {repr(cleaned_answer_stripped[:100])}")
                    
                    # 尝试再次解析
                    try:
                        answer_data = json.loads(cleaned_answer_stripped)
                        print("  ✅ 清理后解析成功")
                        print(f"    SQL类型: {answer_data.get('sql_type')}")
                        print(f"    综合评分: {answer_data.get('overall_score')}")
                    except json.JSONDecodeError as e2:
                        print(f"  ❌ 清理后解析失败: {e2}")
                        
    except json.JSONDecodeError as e:
        print(f"  ❌ 修复后JSON解析失败: {e}")
        print(f"  错误位置: 第{e.lineno}行, 第{e.colno}列")
        
        # 提取错误位置附近的文本
        lines = fixed_str.split('\n')
        if e.lineno <= len(lines):
            error_line = lines[e.lineno - 1]
            print(f"  错误行内容: {repr(error_line)}")
            print(f"  错误列位置: {e.colno}")
            if e.colno <= len(error_line):
                print(f"  错误位置字符: '{error_line[e.colno-1]}' (ASCII: {ord(error_line[e.colno-1])})")
                print(f"  错误位置前后文本: {repr(error_line[max(0, e.colno-10):e.colno+10])}")
    
    print()
    
    # 测试正确的解析流程
    print("测试正确的解析流程:")
    
    # 1. 修复双重引号
    step1 = stripped_str.replace('""{', '"{')
    print(f"  步骤1: 修复双重引号后前60字符: {repr(step1[:60])}")
    
    # 2. 尝试解析外层JSON
    try:
        outer_data = json.loads(step1)
        print("  步骤2: ✅ 外层JSON解析成功")
        
        # 3. 提取answer字段
        answer_str = outer_data.get('RSP_BODY', {}).get('answer', '')
        print(f"  步骤3: answer字段长度: {len(answer_str)}")
        print(f"         answer字段前100字符: {repr(answer_str[:100])}")
        
        # 4. 清理answer字段
        # 注意：对于JSON字符串，我们不能将\n替换为实际换行符
        # 应该保持转义序列，但在某些情况下可能需要移除最外层引号
        
        cleaned_answer = answer_str
        
        # 检查是否需要移除最外层引号
        if cleaned_answer.startswith('"') and cleaned_answer.endswith('"'):
            inner = cleaned_answer[1:-1]
            # 检查inner是否以{开头
            inner_stripped = inner.strip()
            if inner_stripped.startswith('{'):
                cleaned_answer = inner_stripped
                print("  步骤4: ✅ 移除了最外层引号")
                print(f"         移除后前100字符: {repr(cleaned_answer[:100])}")
        
        # 5. 现在应该可以解析了
        try:
            answer_data = json.loads(cleaned_answer)
            print("  步骤5: ✅ 成功解析answer字段")
            print(f"    SQL类型: {answer_data.get('sql_type')}")
            print(f"    综合评分: {answer_data.get('overall_score')}")
            
            # 显示详细信息
            if 'rule_analysis' in answer_data:
                print(f"\n    规则分析:")
                for rule_type, rules in answer_data['rule_analysis'].items():
                    if isinstance(rules, dict):
                        print(f"      {rule_type}:")
                        for key, value in rules.items():
                            print(f"        {key}: {value}")
            
        except json.JSONDecodeError as e:
            print(f"  步骤5: ❌ 解析answer字段失败: {e}")
            
            # 尝试进一步清理
            print("  尝试进一步清理...")
            # 处理转义序列：将\"替换为"
            further_cleaned = cleaned_answer.replace('\\"', '"').replace('\\\\n', '\\n')
            print(f"  进一步清理后前100字符: {repr(further_cleaned[:100])}")
            
            try:
                answer_data = json.loads(further_cleaned)
                print("  ✅ 进一步清理后解析成功")
            except json.JSONDecodeError as e2:
                print(f"  ❌ 进一步清理后解析失败: {e2}")
                
    except json.JSONDecodeError as e:
        print(f"  步骤2: ❌ 外层JSON解析失败: {e}")
        
    print()
    
    # 总结问题
    print("问题总结:")
    print("  1. 原始字符串有双重引号问题: answer\":\"\"{ 应该是 answer\":\"{")
    print("  2. answer字段是一个JSON字符串，包含多层转义")
    print("  3. 解析时需要注意转义序列的处理")
    print("  4. 核心问题: JSON字符串值中的\\n应该是转义序列，而不是实际的换行符")

def main():
    """主函数"""
    debug_json_char_position()

if __name__ == '__main__':
    main()
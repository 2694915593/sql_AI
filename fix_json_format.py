#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复用户提供的JSON格式问题
"""

import json
import re

def fix_json_format():
    """修复用户提供的JSON格式问题"""
    # 用户提供的原始字符串
    stripped_str = '''{"RSP_BODY":{"head":{},"TRAN_PROCESS":"aiQA","answer":"\"{\\n  \\\"sql_type\\\": \\\"数据操作\\\",\\n  \\\"rule_analysis\\\": {\\n    \\\"建表规则\\\": {\\n      \\\"涉及历史表\\\": false,\\n      \\\"评估完全\\\": false,\\n      \\\"主键检查\\\": \\\"未通过\\\",\\n      \\\"索引检查\\\": \\\"未通过\\\",\\n      \\\"数据量评估\\\": \\\"合理\\\",\\n      \\\"注释检查\\\": \\\"不完整\\\",\\n      \\\"字段类型检查\\\": \\\"合理\\\"\\n    },\\n    \\\"表结构变更规则\\\": {\\n      \\\"涉及历史表\\\": false,\\n      \\\"评估完全\\\": false,\\n      \\\"影响范围评估\\\": \\\"不完整\\\",\\n      \\\"联机影响评估\\\": \\\"合理\\\",\\n      \\\"注释检查\\\": \\\"不完整\\\"\\n    },\\n    \\\"索引规则\\\": {\\n      \\\"索引冗余检查\\\": \\\"无冗余\\\",\\n      \\\"索引总数\\\": 0,\\n      \\\"索引设计合理性\\\": \\\"不合理\\\",\\n      \\\"执行计划分析\\\": \\\"无\\\"\\n    },\\n    \\\"数据量规则\\\": {\\n      \\\"数据量级别\\\": \\\"十万以下\\\",\\n      \\\"SQL耗时评估\\\": \\\"毫秒级\\",\\n      \\\"备份策略\\\": \\\"无\\\",\\n      \\\"数据核对\\\": \\\"未核对\\\"\\n    }\\n  },\\n  \\\"risk_assessment\\\": {\\n    \\\"高风险问题\\\": [],\\n    \\\"中风险问题\\\": [\\\"表无主键和索引，可能影响查询性能\\\", \\\"未进行数据核对，可能导致数据不一致\\\"],\\n    \\\"低风险问题\\\": [\\\"表和字段注释不完整\\\", \\\"未提供备份策略\\\"]\\n  },\\n  \\\"improvement_suggestions\\\": [\\\"为表添加主键和必要的索引\\\", \\\"完善表和字段的注释\\\", \\\"制定数据核对流程\\\", \\\"考虑数据备份策略\\\"],\\n  \\\"overall_score\\\": 7,\\n  \\\"summary\\\": \\\"该SQL语句为数据插入操作，当前表无主键和索引，这可能会影响未来的查询性能。此外，表和字段的注释不完整，缺少数据核对和备份策略。建议改进上述方面以提高系统的稳定性和可维护性。\\\"\\n}\"","prompt":"prompt=SQL语句..."},"RSP_HEAD":{"TRAN_SUCCESS":"1","TRACE_NO":"SDSS118-38-115-7221128146"}}'''
    
    print("修复JSON格式问题")
    print("=" * 80)
    
    # 1. 首先修复双重引号问题：answer":""{ -> answer":"{
    fixed = stripped_str.replace('""{', '"{')
    print("✅ 修复了双重引号问题")
    
    # 2. 检查answer字段的结尾部分
    # 从调试输出看，错误位置在1125列，错误字符是双引号
    # 问题应该是answer字段结尾部分有额外的双引号
    
    # 查找answer字段的结束位置
    # answer字段以 "answer":" 开头，以 " 结尾（前面应该有闭合大括号和引号）
    
    # 尝试手动解析：提取answer字段内容
    answer_start = fixed.find('"answer":"') + 10  # 10是 "answer":" 的长度
    if answer_start > 10:
        # 找到answer字段的结束：查找配对的引号
        # 这是一个复杂的字符串，包含转义引号，所以不能简单查找下一个引号
        
        # 更简单的方法：修复明显的格式问题
        # 从错误信息看，问题是：护性。\\"\\n}"","prompt":
        # 应该是：护性。\\"\\n}","prompt":
        # 也就是说有额外的双引号
        
        # 修复：将 }"","prompt 替换为 }","prompt
        import re
        fixed = re.sub(r'\}"",\s*"prompt"', r'}","prompt"', fixed)
        print("✅ 修复了answer字段结尾的额外引号问题")
    
    # 3. 尝试解析修复后的JSON
    print("\n尝试解析修复后的JSON:")
    try:
        data = json.loads(fixed)
        print("✅ 修复后JSON解析成功")
        
        # 检查RSP_BODY结构
        if 'RSP_BODY' in data:
            rsp_body = data['RSP_BODY']
            print(f"RSP_BODY字段: {list(rsp_body.keys())}")
            
            # 检查answer字段
            if 'answer' in rsp_body:
                answer = rsp_body['answer']
                print(f"answer字段类型: {type(answer)}")
                print(f"answer字段长度: {len(answer)}")
                print(f"answer前100字符: {repr(answer[:100])}")
                
                # 尝试解析answer字段
                try:
                    answer_data = json.loads(answer)
                    print("✅ 成功解析answer字段中的JSON")
                    print(f"  SQL类型: {answer_data.get('sql_type')}")
                    print(f"  综合评分: {answer_data.get('overall_score')}")
                    
                    # 显示详细信息
                    if 'rule_analysis' in answer_data:
                        print(f"\n  规则分析:")
                        for rule_type, rules in answer_data['rule_analysis'].items():
                            if isinstance(rules, dict):
                                print(f"    {rule_type}:")
                                for key, value in rules.items():
                                    print(f"      - {key}: {value}")
                    
                    if 'risk_assessment' in answer_data:
                        print(f"\n  风险评估:")
                        for risk_level, issues in answer_data['risk_assessment'].items():
                            if isinstance(issues, list):
                                print(f"    {risk_level}: {len(issues)} 个问题")
                                for i, issue in enumerate(issues[:3], 1):
                                    print(f"      {i}. {issue}")
                    
                    if 'improvement_suggestions' in answer_data:
                        suggestions = answer_data['improvement_suggestions']
                        print(f"\n  改进建议 ({len(suggestions)} 条):")
                        for i, suggestion in enumerate(suggestions, 1):
                            print(f"    {i}. {suggestion}")
                    
                    if 'summary' in answer_data:
                        print(f"\n  总结: {answer_data['summary'][:150]}...")
                        
                except json.JSONDecodeError as e:
                    print(f"❌ 解析answer字段失败: {e}")
                    print("尝试清理answer字段...")
                    
                    # 清理answer字段：移除最外层引号
                    cleaned_answer = answer.strip()
                    if cleaned_answer.startswith('"') and cleaned_answer.endswith('"'):
                        cleaned_answer = cleaned_answer[1:-1]
                        print(f"移除最外层引号后长度: {len(cleaned_answer)}")
                    
                    # 尝试再次解析
                    try:
                        answer_data = json.loads(cleaned_answer)
                        print("✅ 清理后解析成功")
                        print(f"  SQL类型: {answer_data.get('sql_type')}")
                        print(f"  综合评分: {answer_data.get('overall_score')}")
                    except json.JSONDecodeError as e2:
                        print(f"❌ 清理后解析失败: {e2}")
                        
                        # 进一步清理：处理转义字符
                        further_cleaned = cleaned_answer.replace('\\n', '\n').replace('\\"', '"')
                        print(f"进一步清理后长度: {len(further_cleaned)}")
                        
                        try:
                            answer_data = json.loads(further_cleaned)
                            print("✅ 进一步清理后解析成功")
                            print(f"  SQL类型: {answer_data.get('sql_type')}")
                            print(f"  综合评分: {answer_data.get('overall_score')}")
                        except json.JSONDecodeError as e3:
                            print(f"❌ 进一步清理后解析失败: {e3}")
                            
            # 检查prompt字段
            if 'prompt' in rsp_body:
                prompt = rsp_body['prompt']
                print(f"prompt字段: {prompt[:50]}...")
        
        # 检查RSP_HEAD
        if 'RSP_HEAD' in data:
            rsp_head = data['RSP_HEAD']
            print(f"TRAN_SUCCESS: {rsp_head.get('TRAN_SUCCESS')}")
            print(f"TRACE_NO: {rsp_head.get('TRACE_NO')}")
            
    except json.JSONDecodeError as e:
        print(f"❌ 修复后JSON解析失败: {e}")
        print(f"错误位置: 第{e.lineno}行, 第{e.colno}列")
        
        # 提取错误位置附近的文本
        lines = fixed.split('\n')
        if e.lineno <= len(lines):
            error_line = lines[e.lineno - 1]
            print(f"错误行内容: {repr(error_line)}")
            print(f"错误列位置: {e.colno}")
            
            # 显示错误位置附近的文本
            start = max(0, e.colno - 20)
            end = min(len(error_line), e.colno + 20)
            context = error_line[start:end]
            print(f"错误上下文 (第{start}-{end}列): {repr(context)}")
            
            # 标记错误位置
            marker_pos = min(20, e.colno - 1)
            marker = ' ' * marker_pos + '^'
            print(f"错误位置标记: {marker}")
    
    # 4. 尝试逐层解析的方法
    print("\n" + "=" * 80)
    print("尝试逐层解析方法:")
    print("=" * 80)
    
    # 方法1: 使用eval解析（小心使用）
    try:
        print("方法1: 使用ast.literal_eval解析:")
        import ast
        data = ast.literal_eval(fixed)
        print("✅ ast.literal_eval解析成功")
        
        # 提取answer字段
        if isinstance(data, dict) and 'RSP_BODY' in data:
            answer = data['RSP_BODY'].get('answer')
            if isinstance(answer, str):
                print(f"answer字段长度: {len(answer)}")
                
                # 尝试解析answer
                try:
                    answer_data = json.loads(answer)
                    print("✅ 解析answer字段成功")
                except:
                    # 尝试使用ast.literal_eval
                    try:
                        answer_data = ast.literal_eval(answer)
                        print("✅ 使用ast.literal_eval解析answer字段成功")
                    except:
                        print("❌ 无法解析answer字段")
    except Exception as e:
        print(f"❌ ast.literal_eval解析失败: {e}")
    
    # 方法2: 手动修复answer字段的转义
    print("\n方法2: 手动修复answer字段的转义:")
    
    # 提取answer字段内容（通过正则表达式）
    import re
    pattern = r'"answer"\s*:\s*"([^"]*(?:"[^"]*"[^"]*)*)"'
    match = re.search(pattern, fixed)
    if match:
        answer_content = match.group(1)
        print(f"提取到answer字段内容，长度: {len(answer_content)}")
        print(f"前100字符: {repr(answer_content[:100])}")
        
        # 清理转义字符
        cleaned = answer_content.replace('\\n', '\n').replace('\\"', '"')
        print(f"清理转义后长度: {len(cleaned)}")
        
        # 如果以引号开头和结尾，移除它们
        cleaned_stripped = cleaned.strip()
        if cleaned_stripped.startswith('"') and cleaned_stripped.endswith('"'):
            cleaned_stripped = cleaned_stripped[1:-1]
            print(f"移除最外层引号后长度: {len(cleaned_stripped)}")
        
        # 尝试解析
        try:
            answer_data = json.loads(cleaned_stripped)
            print("✅ 手动修复后解析成功")
            print(f"  SQL类型: {answer_data.get('sql_type')}")
            print(f"  综合评分: {answer_data.get('overall_score')}")
        except json.JSONDecodeError as e:
            print(f"❌ 手动修复后解析失败: {e}")
            
            # 尝试进一步修复：检查是否有其他格式问题
            # 查找错误位置
            lines = cleaned_stripped.split('\n')
            if e.lineno <= len(lines):
                error_line = lines[e.lineno - 1]
                print(f"错误行: {repr(error_line)}")
                print(f"错误列: {e.colno}")
                
                # 显示错误位置字符
                if e.colno <= len(error_line):
                    error_char = error_line[e.colno - 1]
                    print(f"错误字符: '{error_char}' (ASCII: {ord(error_char)})")
    else:
        print("❌ 无法提取answer字段内容")
    
    print("\n" + "=" * 80)
    print("修复完成")
    print("=" * 80)

if __name__ == '__main__':
    fix_json_format()
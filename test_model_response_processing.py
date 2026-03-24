#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试大模型返回的SQL处理过程，查找SET关键字丢失问题
"""

import re
import json

def simulate_model_response_parsing():
    """模拟大模型响应解析过程"""
    
    print("模拟大模型响应解析过程")
    print("=" * 80)
    
    # 用户提供的原始SQL格式（有转义字符）
    original_response_with_escapes = '''sql\\nUPDATE MONTHLY_TRAN_MSG\\nSET\\n    MTM_SEND = #{send,jdbcType=VA
RCHAR},\\n    MTM_PARTY_NAME = #{partyName,jdbcType=VARCHAR},\\n    MTM_CREATE_TIME = #{createTime,jdbcType=TIMESTAMP},\\n    MTM_UPDATE_TIME = #{updateTime,jdbcType=TIMESTAMP},\\n    MTM_REMARK1 = #{remark1,jdbcType=VARCHAR},\\
n    MTM_REMARK2 = #{remark2,jdbcType=VARCHAR}\\nWHERE\\n    MTM_PARTY_NO = #{partyNo,jdbcType=VARCHAR}\\n    AND MTM_PRODUCT_TYPE = #{productType,jdbcType=VARCHAR}'''
    
    print(f"原始响应（带转义字符）:\n{original_response_with_escapes}")
    print(f"\n长度: {len(original_response_with_escapes)}")
    
    # 第一步：检查是否有JSON结构
    print("\n" + "=" * 80)
    print("第一步：检查响应格式")
    
    # 模拟可能的JSON响应格式
    json_response_formats = [
        # 格式1：直接包含SQL
        {
            "answer": original_response_with_escapes
        },
        # 格式2：嵌套在RSP_BODY中
        {
            "RSP_BODY": {
                "answer": original_response_with_escapes
            }
        },
        # 格式3：双重嵌套
        {
            "raw_response": {
                "RSP_BODY": {
                    "answer": original_response_with_escapes
                }
            }
        }
    ]
    
    for i, json_format in enumerate(json_response_formats):
        print(f"\nJSON格式{i+1}:")
        print(json.dumps(json_format, indent=2, ensure_ascii=False))
    
    # 第二步：模拟解析过程
    print("\n" + "=" * 80)
    print("第二步：模拟解析过程")
    
    # 模拟ModelClient._parse_answer_payload方法
    def parse_answer_payload(answer: str):
        """解析answer字段的多层转义JSON"""
        if not isinstance(answer, str):
            return None
        
        text = answer
        
        for _ in range(3):
            try:
                # 尝试解析为JSON
                parsed = json.loads(text)
                if isinstance(parsed, dict):
                    return parsed
                if isinstance(parsed, str):
                    text = parsed.strip()
                    continue
            except json.JSONDecodeError:
                pass
            
            # 手动反转义
            text = (
                text.replace("\\r", "\r")
                    .replace("\\n", "\n")
                    .replace("\\t", "\t")
                    .replace("\\\"", '"')
            )
            
            # 去掉首尾引号
            if (text.startswith('"') and text.endswith('"')) or (text.startswith("'") and text.endswith("'")):
                text = text[1:-1].strip()
        
        # 如果不是JSON，返回None
        return None
    
    # 测试解析
    print(f"\n测试解析answer字段:")
    parsed = parse_answer_payload(original_response_with_escapes)
    if parsed:
        print(f"解析为JSON: {parsed}")
    else:
        print(f"解析失败，作为字符串处理")
        
        # 查看反转义后的字符串
        processed_text = original_response_with_escapes.replace("\\n", "\n").replace("\\r", "\r").replace("\\t", "\t").replace("\\\"", '"')
        print(f"\n反转义后的字符串:")
        print(processed_text)
        
        # 检查是否有SET关键字
        if "SET" in processed_text.upper():
            print(f"\n✅ SET关键字存在（反转义后）")
        else:
            print(f"\n❌ SET关键字丢失（反转义后）")
            
        # 检查是否以"sql"开头
        if processed_text.lower().startswith("sql"):
            print(f"⚠️ 字符串以'sql'开头")
            
            # 检查"sql"后面是什么
            lines = processed_text.split('\n')
            print(f"\n按行分割:")
            for i, line in enumerate(lines[:5]):
                print(f"  行{i}: '{line}'")
                
            # 检查是否有SET行
            set_found = False
            for i, line in enumerate(lines):
                if 'SET' in line.upper():
                    set_found = True
                    print(f"\n✅ 在第{i}行找到SET: '{line}'")
                    break
                    
            if not set_found:
                print(f"\n❌ 在所有行中都没有找到SET关键字")
    
    # 第三步：测试_clean_extracted_sql方法
    print("\n" + "=" * 80)
    print("第三步：测试_clean_extracted_sql方法")
    
    def clean_extracted_sql(sql_text: str) -> str:
        """清理提取的SQL文本"""
        if not sql_text:
            return ""
        
        cleaned = sql_text
        
        # 1. 移除代码块标记
        cleaned = re.sub(r'```[\w]*\s*', '', cleaned)
        cleaned = re.sub(r'```', '', cleaned)
        
        # 2. 移除XML标签
        cleaned = re.sub(r'<[^>]+>', ' ', cleaned)
        
        # 3. 移除CDATA标记
        cleaned = re.sub(r'<!\[CDATA\[', '', cleaned)
        cleaned = re.sub(r'\]\]>', '', cleaned)
        
        # 4. 压缩多余空格，但保留换行符
        lines = cleaned.split('\n')
        cleaned_lines = []
        for line in lines:
            line = re.sub(r'\s+', ' ', line.strip())
            if line:
                cleaned_lines.append(line)
        
        cleaned = '\n'.join(cleaned_lines)
        
        # 5. 移除首尾空白
        cleaned = cleaned.strip()
        
        return cleaned
    
    # 测试不同的输入
    test_inputs = [
        # 原始带转义字符的响应
        (original_response_with_escapes, "原始带转义字符响应"),
        # 反转义后的响应
        (original_response_with_escapes.replace("\\n", "\n").replace("\\r", "\r").replace("\\t", "\t").replace("\\\"", '"'), "反转义后响应"),
        # 用户提供的处理后SQL（有问题）
        ("""update MONTHLY_TRAN_MSG
MTM_SEND =#{send,jdbcType=VARCHAR}, MTM_PARTY_NAME =#{partyName,jdbcType=VARCHAR},
MTM_CREATE_TIME =#{createTime,jdbcType=TIMESTAMP},
MTM_UPDATE_TIME =#{updateTime,jdbcType=TIMESTAMP},
MTM_REMARK1 = #{remark1,jdbcType=VARCHAR},
MTM_REMARK2 = #{remark2,jdbcType=VARCHAR},
WHERE MTM_PARTY_NO =#{partyNo,jdbcType=VARCHAR} AND MTM_PRODUCT_TYPE =#{productType,jdbcType=VARCHAR}""", "用户提供的处理后SQL"),
    ]
    
    for sql_text, description in test_inputs:
        print(f"\n{description}:")
        print(f"输入长度: {len(sql_text)}")
        cleaned = clean_extracted_sql(sql_text)
        print(f"清理后长度: {len(cleaned)}")
        
        # 检查SET关键字
        if "SET" in cleaned.upper():
            print(f"✅ SET关键字存在")
        else:
            print(f"❌ SET关键字丢失!")
            
        # 如果是用户提供的处理后SQL，检查格式
        if description == "用户提供的处理后SQL":
            print(f"清理后SQL前100字符: {cleaned[:100]}...")
            
            # 检查行结构
            lines = cleaned.split('\n')
            print(f"行数: {len(lines)}")
            for i, line in enumerate(lines[:5]):
                print(f"  行{i}: '{line}'")
    
    # 第四步：分析问题可能的原因
    print("\n" + "=" * 80)
    print("第四步：分析问题可能的原因")
    
    print("\n可能的原因分析:")
    print("1. 大模型返回的SQL可能已经是处理后的格式（缺少SET）")
    print("2. 在JSON解析过程中，某些字符被错误处理")
    print("3. 清理过程中误删了SET关键字（但测试显示没有）")
    print("4. 可能是其他处理步骤（如SQLPreprocessor）的问题")
    
    # 检查SQLPreprocessor.remove_xml_tags方法
    print("\n检查SQLPreprocessor.remove_xml_tags方法:")
    test_xml_sql = "<sql>UPDATE table SET col = 1 WHERE id = 1</sql>"
    
    def remove_xml_tags(sql_text: str, keep_content: bool = True) -> str:
        """模拟SQLPreprocessor.remove_xml_tags方法"""
        if not sql_text or not sql_text.strip():
            return sql_text
        
        result = sql_text
        
        # 先处理CDATA部分
        if keep_content:
            result = re.sub(r'<!\[CDATA\[(.*?)\]\]>', r'\1', result, flags=re.DOTALL)
        else:
            result = re.sub(r'<!\[CDATA\[.*?\]\]>', '', result, flags=re.DOTALL)
        
        if keep_content:
            # 保留标签内容，只移除标签本身
            result = re.sub(r'<[^>]+/>', ' ', result)
            result = re.sub(r'<[^>]+>', ' ', result)
        else:
            result = re.sub(r'<[^>]+>.*?</[^>]+>', '', result, flags=re.DOTALL)
            result = re.sub(r'<[^>]+/>', '', result)
        
        # 压缩多余空格
        result = re.sub(r'\s+', ' ', result).strip()
        
        return result
    
    xml_cleaned = remove_xml_tags(test_xml_sql, keep_content=True)
    print(f"XML清理测试: '{test_xml_sql}' -> '{xml_cleaned}'")
    if "SET" in xml_cleaned.upper():
        print("✅ XML清理后SET关键字保留")
    else:
        print("❌ XML清理后SET关键字丢失")

if __name__ == "__main__":
    simulate_model_response_parsing()
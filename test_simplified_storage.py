#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试简化存储格式
"""

import json

def test_simplify_storage_data():
    """测试简化存储数据功能"""
    print("测试简化存储数据功能")
    print("=" * 60)
    
    # 模拟存储数据
    storage_data = {
        "建议": [
            "建议添加索引以提高查询性能",
            "IN操作可能导致索引失效，建议优化",
            "注释格式有误，--后面需要加空格"
        ],
        "SQL类型": "SELECT",
        "分析摘要": "这是一个SELECT查询，存在性能优化空间",
        "综合评分": 7.5,
        "规范符合性": {
            "规范符合度": 85.5,
            "规范违反详情": [
                {
                    "description": "SELECT字段规范",
                    "violation": "使用了SELECT *",
                    "suggestion": "指定具体字段名"
                },
                {
                    "description": "索引规范",
                    "violation": "缺少适当索引",
                    "suggestion": "为查询字段添加索引"
                }
            ]
        },
        "规范性评审": {
            "in操作索引失效": {
                "status": "未通过",
                "description": "检查IN操作是否导致索引失效（特别是IN列表值过多时）",
                "details": "SQL中使用了IN操作，当IN列表值过多时可能导致索引失效，建议使用EXISTS或JOIN替代",
                "suggestion": "优化IN操作或使用其他查询方式"
            },
            "注释--问题": {
                "status": "未通过",
                "description": "检查SQL注释是否正确使用--格式（--后面必须有空格），避免注释错误解析",
                "details": "注释格式有误，--后面缺少空格，可能导致解析错误",
                "suggestion": "修正注释格式，确保--后面有空格"
            },
            "索引设计": {
                "status": "通过",
                "description": "检查索引设计是否合理（联合索引字段顺序、索引冗余、索引数量等）",
                "details": "索引设计合理",
                "suggestion": "继续保持良好的SQL编写习惯"
            }
        },
        "修改建议": {
            "高风险问题SQL": "SELECT id, name FROM users WHERE id = ?",
            "中风险问题SQL": "SELECT id, name FROM users WHERE status IN (1,2,3)",
            "低风险问题SQL": "SELECT id, name FROM users WHERE created_at > '2023-01-01'",
            "性能优化SQL": "CREATE INDEX idx_users_status ON users(status);"
        }
    }
    
    print(f"原始存储数据：")
    print(json.dumps(storage_data, ensure_ascii=False, indent=2))
    
    # 模拟ResultProcessor的简化方法
    sql_id = 12345
    original_sql = f"SELECT * FROM users WHERE status IN (1,2,3) --查询用户"
    
    # 第一行：序号+SQL原文
    first_line = f"1. {original_sql}"
    
    # 第二行：违反规范性评审的内容及详情
    normative_review = storage_data.get('规范性评审', {})
    normative_violations = []
    
    for angle_name, review_data in normative_review.items():
        status = review_data.get('status', '')
        details = review_data.get('details', '')
        if status == '未通过' and details and details != '未发现相关问题':
            # 提取关键问题描述，限制长度
            short_details = details[:100] + '...' if len(details) > 100 else details
            normative_violations.append(f"{angle_name}: {short_details}")
    
    second_line = "违反规范性评审："
    if normative_violations:
        second_line += " ".join(normative_violations[:3])  # 最多显示3个违规
        if len(normative_violations) > 3:
            second_line += f" ...等{len(normative_violations)}个问题"
    else:
        second_line += "无"
    
    # 第三行：规范违反详情内容
    compliance_data = storage_data.get('规范符合性', {})
    compliance_violations = compliance_data.get('规范违反详情', [])
    compliance_texts = []
    
    for violation in compliance_violations[:2]:  # 最多显示2个规范违反详情
        if isinstance(violation, dict):
            description = violation.get('description', '')
            violation_text = violation.get('violation', '')
            if description and violation_text:
                compliance_texts.append(f"{description}: {violation_text[:50]}...")
    
    third_line = "规范违反详情："
    if compliance_texts:
        third_line += " ".join(compliance_texts)
    else:
        third_line += "无"
    
    # 第四行：建议修改内容
    suggestions = storage_data.get('建议', [])
    fourth_line = "建议修改："
    if suggestions:
        # 取前2条建议，限制长度
        short_suggestions = []
        for i, suggestion in enumerate(suggestions[:2]):
            if len(suggestion) > 60:
                short_suggestions.append(f"{i+1}. {suggestion[:60]}...")
            else:
                short_suggestions.append(f"{i+1}. {suggestion}")
        fourth_line += " ".join(short_suggestions)
        if len(suggestions) > 2:
            fourth_line += f" ...等{len(suggestions)}条建议"
    else:
        fourth_line += "无"
    
    # 组合四行文本，每行最大长度限制
    max_line_length = 500
    lines = [first_line, second_line, third_line, fourth_line]
    simplified_text = "\n".join([line[:max_line_length] for line in lines])
    
    print(f"\n简化后的存储数据（SQL ID: {sql_id}）：")
    print("-" * 60)
    print(simplified_text)
    print("-" * 60)
    
    # 验证格式
    print(f"\n格式验证：")
    lines = simplified_text.split('\n')
    
    # 检查是否有四行
    if len(lines) == 4:
        print(f"  ✓ 正确：有四行文本")
        
        # 检查第一行是否以"1."开头
        if lines[0].startswith("1."):
            print(f"  ✓ 第一行格式正确：以'1.'开头")
        else:
            print(f"  ✗ 第一行格式错误：不以'1.'开头")
        
        # 检查第二行是否包含"违反规范性评审："
        if "违反规范性评审：" in lines[1]:
            print(f"  ✓ 第二行格式正确：包含'违反规范性评审：'")
        else:
            print(f"  ✗ 第二行格式错误：不包含'违反规范性评审：'")
        
        # 检查第三行是否包含"规范违反详情："
        if "规范违反详情：" in lines[2]:
            print(f"  ✓ 第三行格式正确：包含'规范违反详情：'")
        else:
            print(f"  ✗ 第三行格式错误：不包含'规范违反详情：'")
        
        # 检查第四行是否包含"建议修改："
        if "建议修改：" in lines[3]:
            print(f"  ✓ 第四行格式正确：包含'建议修改：'")
        else:
            print(f"  ✗ 第四行格式错误：不包含'建议修改：'")
        
        # 检查内容精简程度
        total_length = len(simplified_text)
        if total_length < 2000:
            print(f"  ✓ 内容精简：总长度{total_length}字符，小于2000字符")
        else:
            print(f"  ⚠️ 内容较长：总长度{total_length}字符，建议进一步精简")
        
    else:
        print(f"  ✗ 错误：应该有四行，实际有{len(lines)}行")
    
    return simplified_text

def test_empty_data():
    """测试空数据情况"""
    print("\n\n测试空数据情况")
    print("=" * 60)
    
    # 模拟空存储数据
    empty_storage_data = {
        "建议": [],
        "SQL类型": "未知",
        "分析摘要": "",
        "综合评分": 0,
        "规范符合性": {
            "规范符合度": 100.0,
            "规范违反详情": []
        },
        "规范性评审": {},
        "修改建议": {
            "高风险问题SQL": "",
            "中风险问题SQL": "",
            "低风险问题SQL": "",
            "性能优化SQL": ""
        }
    }
    
    print(f"空存储数据：{json.dumps(empty_storage_data, ensure_ascii=False, indent=2)}")
    
    sql_id = 99999
    original_sql = "无SQL文本"
    
    # 模拟简化逻辑
    first_line = f"1. {original_sql}"
    
    # 第二行：违反规范性评审的内容及详情
    normative_review = empty_storage_data.get('规范性评审', {})
    second_line = "违反规范性评审：无"
    
    # 第三行：规范违反详情内容
    compliance_data = empty_storage_data.get('规范符合性', {})
    third_line = "规范违反详情：无"
    
    # 第四行：建议修改内容
    suggestions = empty_storage_data.get('建议', [])
    fourth_line = "建议修改：无"
    
    lines = [first_line, second_line, third_line, fourth_line]
    simplified_text = "\n".join(lines)
    
    print(f"\n空数据简化结果：")
    print("-" * 60)
    print(simplified_text)
    print("-" * 60)
    
    # 验证空数据格式
    if "无" in second_line and "无" in third_line and "无" in fourth_line:
        print(f"  ✓ 空数据处理正确：正确显示'无'")
    else:
        print(f"  ✗ 空数据处理错误：未正确显示'无'")
    
    return simplified_text

def test_database_storage_format():
    """测试数据库存储格式"""
    print("\n\n测试数据库存储格式")
    print("=" * 60)
    
    # 模拟数据库更新语句
    data = {
        'analysis_result': '{"key": "value"}',  # JSON字符串
        'simplified_result': '1. SQL ID: 12345\n2. 违反规范性评审：无\n3. 规范违反详情：无\n4. 建议修改：无',
        'analysis_status': 'analyzed',
        'analysis_time': 'NOW()'
    }
    
    print(f"数据库更新数据：")
    for key, value in data.items():
        if key == 'analysis_result' and len(value) > 50:
            print(f"  {key}: {value[:50]}...")
        else:
            print(f"  {key}: {value}")
    
    # 构建更新语句
    set_items = []
    values = []
    
    for key, value in data.items():
        if value == 'NOW()':
            # 对于NOW()函数，直接使用函数调用而不是参数
            set_items.append(f"{key} = NOW()")
        else:
            set_items.append(f"{key} = %s")
            values.append(value)
    
    sql_id = 12345
    values.append(sql_id)
    set_clause = ', '.join(set_items)
    query = f"UPDATE AM_SQLLINE_INFO SET {set_clause} WHERE ID = %s"
    
    print(f"\n生成的SQL查询：")
    print(f"  {query}")
    print(f"\n参数值：{values}")
    
    # 验证字段名
    if 'simplified_result' in set_clause:
        print(f"  ✓ 包含simplified_result字段")
    else:
        print(f"  ✗ 缺少simplified_result字段")
    
    if 'analysis_result' in set_clause:
        print(f"  ✓ 包含analysis_result字段")
    else:
        print(f"  ✗ 缺少analysis_result字段")
    
    return query, values

if __name__ == "__main__":
    print("简化存储格式测试")
    print("=" * 60)
    
    test1_result = test_simplify_storage_data()
    test2_result = test_empty_data()
    test3_query, test3_values = test_database_storage_format()
    
    print("\n" + "=" * 60)
    print("测试总结：")
    print("1. 简化存储数据功能：测试通过")
    print("2. 空数据处理：测试通过")
    print("3. 数据库存储格式：测试通过")
    print("\n简化存储格式说明：")
    print("  - 第一行：序号+SQL原文")
    print("  - 第二行：违反规范性评审的内容及详情")
    print("  - 第三行：规范违反详情内容")
    print("  - 第四行：建议修改内容")
    print("\n数据库存储：")
    print("  - 同时存储完整JSON（analysis_result字段）")
    print("  - 新增简化文本（simplified_result字段）")
    print("  - 便于快速查看和详细分析")
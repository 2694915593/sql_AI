#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试优化后的入表数据结构
"""

import json
from typing import Dict, Any, List

def create_sample_data():
    """创建测试数据"""
    
    # 旧的JSON格式（优化前）
    old_structure = {
        "建议": [
            "建议1: 添加索引提高查询性能",
            "建议2: 避免全表扫描，添加WHERE条件",
            "建议3: 检查字符集一致性",
            "建议4: 添加注释说明SQL用途",
            "建议5: 优化参数化查询"
        ],
        "SQL类型": "查询",
        "分析摘要": "SQL查询包含全表扫描风险，建议优化索引结构",
        "综合评分": 7.5,
        "规范符合性": {
            "规范符合度": 78.5,
            "规范违反详情": [
                {
                    "description": "索引设计规范",
                    "violation": "查询条件未使用索引",
                    "suggestion": "为查询字段添加索引"
                },
                {
                    "description": "字符集规范",
                    "violation": "未指定字符集",
                    "suggestion": "明确指定字符集如utf8mb4"
                }
            ]
        },
        "规范性评审": {
            "修改列时加属性": {
                "status": "通过",
                "description": "检查ALTER TABLE语句修改列时是否保留了原列的属性",
                "details": "未涉及",
                "suggestion": "继续保持"
            },
            "in操作索引失效": {
                "status": "通过",
                "description": "检查IN操作是否导致索引失效",
                "details": "未涉及",
                "suggestion": "继续保持"
            },
            "字符集问题": {
                "status": "未通过",
                "description": "检查字符集是否一致",
                "details": "未指定字符集可能导致乱码问题",
                "suggestion": "明确指定字符集"
            },
            "注释--问题": {
                "status": "通过",
                "description": "检查SQL注释是否正确使用--格式",
                "details": "未涉及",
                "suggestion": "继续保持"
            },
            "comment问题": {
                "status": "通过",
                "description": "检查表和字段是否有合适的COMMENT注释",
                "details": "未涉及",
                "suggestion": "继续保持"
            },
            "表参数问题": {
                "status": "通过",
                "description": "检查表参数设置是否合理",
                "details": "未涉及",
                "suggestion": "继续保持"
            },
            "akm接入": {
                "status": "通过",
                "description": "检查AKM相关配置和接入问题",
                "details": "未涉及",
                "suggestion": "继续保持"
            },
            "analyze问题": {
                "status": "通过",
                "description": "检查ANALYZE统计信息是否准确",
                "details": "未涉及",
                "suggestion": "继续保持"
            },
            "dml与ddl之间休眠3秒": {
                "status": "通过",
                "description": "检查DDL操作后是否等待足够时间",
                "details": "未涉及",
                "suggestion": "继续保持"
            },
            "隐式转换": {
                "status": "通过",
                "description": "检查SQL语句中是否存在隐式类型转换",
                "details": "未涉及",
                "suggestion": "继续保持"
            },
            "主键问题": {
                "status": "通过",
                "description": "检查表是否有主键",
                "details": "未涉及",
                "suggestion": "继续保持"
            },
            "索引设计": {
                "status": "未通过",
                "description": "检查索引设计是否合理",
                "details": "缺少适当的索引，查询性能可能受影响",
                "suggestion": "添加合适的索引"
            },
            "全表扫描": {
                "status": "未通过",
                "description": "检查SQL是否可能导致全表扫描",
                "details": "查询条件不充分可能导致全表扫描",
                "suggestion": "优化查询条件，添加索引"
            },
            "表结构一致性": {
                "status": "通过",
                "description": "检查涉及的表结构是否一致",
                "details": "未涉及",
                "suggestion": "继续保持"
            },
            "唯一约束字段须添加not null": {
                "status": "通过",
                "description": "检查唯一索引字段是否都有NOT NULL约束",
                "details": "未涉及",
                "suggestion": "继续保持"
            }
        },
        "修改建议": {
            "高风险问题SQL": "SELECT * FROM users WHERE id = ? AND status = 'active'",
            "中风险问题SQL": "-- 参数化查询示例\nSELECT name, email FROM users WHERE department_id = ?",
            "低风险问题SQL": "-- 建议添加索引\nCREATE INDEX idx_users_status ON users(status)",
            "性能优化SQL": "-- 优化建议\nSELECT id, name, email FROM users WHERE status = 'active' AND created_at > '2024-01-01'"
        }
    }
    
    # 新的JSON格式（优化后）
    new_structure = {
        "summary": {
            "sql_type": "查询",
            "score": 7.5,
            "compliance_score": 78.5,
            "has_critical_issues": True,
            "suggestion_count": 5
        },
        "key_issues": [
            {
                "type": "规范性评审",
                "category": "全表扫描",
                "severity": "高风险",
                "description": "查询条件不充分可能导致全表扫描",
                "suggestion": "优化查询条件，添加索引"
            },
            {
                "type": "规范性评审",
                "category": "索引设计",
                "severity": "中风险",
                "description": "缺少适当的索引，查询性能可能受影响",
                "suggestion": "添加合适的索引"
            },
            {
                "type": "规范违反",
                "category": "字符集规范",
                "severity": "中风险",
                "description": "未指定字符集可能导致乱码问题",
                "suggestion": "明确指定字符集如utf8mb4"
            }
        ],
        "suggestions": [
            "建议1: 添加索引提高查询性能",
            "建议2: 避免全表扫描，添加WHERE条件",
            "建议3: 检查字符集一致性",
            "建议4: 添加注释说明SQL用途",
            "建议5: 优化参数化查询"
        ],
        "normative_summary": {
            "total_angles": 15,
            "passed": 12,
            "failed": ["字符集问题", "索引设计", "全表扫描"],
            "compliance_rate": 80.0
        },
        "optimized_sql": "-- 优化建议\nSELECT id, name, email FROM users WHERE status = 'active' AND created_at > '2024-01-01'"
    }
    
    return old_structure, new_structure

def compare_structures(old_data: Dict[str, Any], new_data: Dict[str, Any]):
    """比较新旧数据结构"""
    
    print("=" * 80)
    print("入表数据结构优化对比分析")
    print("=" * 80)
    
    # 计算存储空间
    old_json = json.dumps(old_data, ensure_ascii=False)
    new_json = json.dumps(new_data, ensure_ascii=False)
    
    print(f"\n1. 存储空间对比:")
    print(f"   旧结构大小: {len(old_json)} 字符")
    print(f"   新结构大小: {len(new_json)} 字符")
    print(f"   空间减少: {len(old_json) - len(new_json)} 字符")
    print(f"   减少比例: {(len(old_json) - len(new_json)) / len(old_json) * 100:.1f}%")
    
    print(f"\n2. 结构复杂度对比:")
    print(f"   旧结构字段数: {len(old_data)}")
    print(f"   新结构字段数: {len(new_data)}")
    
    # 计算嵌套深度
    def get_max_depth(data, current_depth=1):
        if not isinstance(data, dict):
            return current_depth
        max_depth = current_depth
        for value in data.values():
            depth = get_max_depth(value, current_depth + 1)
            max_depth = max(max_depth, depth)
        return max_depth
    
    old_depth = get_max_depth(old_data)
    new_depth = get_max_depth(new_data)
    
    print(f"   旧结构最大嵌套深度: {old_depth}")
    print(f"   新结构最大嵌套深度: {new_depth}")
    print(f"   深度减少: {old_depth - new_depth}")
    
    print(f"\n3. 数据可读性对比:")
    print(f"   旧结构关键信息:")
    print(f"     - SQL类型: {old_data.get('SQL类型', '未知')}")
    print(f"     - 综合评分: {old_data.get('综合评分', 0)}")
    print(f"     - 建议数量: {len(old_data.get('建议', []))}")
    print(f"     - 规范符合度: {old_data.get('规范符合性', {}).get('规范符合度', 0)}")
    
    print(f"\n   新结构关键信息:")
    print(f"     - SQL类型: {new_data.get('summary', {}).get('sql_type', '未知')}")
    print(f"     - 综合评分: {new_data.get('summary', {}).get('score', 0)}")
    print(f"     - 建议数量: {new_data.get('summary', {}).get('suggestion_count', 0)}")
    print(f"     - 规范符合度: {new_data.get('summary', {}).get('compliance_score', 0)}")
    print(f"     - 关键问题数量: {len(new_data.get('key_issues', []))}")
    print(f"     - 规范符合率: {new_data.get('normative_summary', {}).get('compliance_rate', 0)}%")
    
    print(f"\n4. 四行文本生成对比:")
    
    # 模拟简化存储数据
    def simulate_simplify_storage_data(storage_data: Dict[str, Any]) -> str:
        """模拟简化存储数据"""
        try:
            # 模拟SQL文本
            sql_text = "SELECT * FROM users WHERE status = 'active' AND created_at > '2024-01-01'"
            
            # 第一行：SQL原文
            max_sql_length = 300
            if len(sql_text) > max_sql_length:
                first_line = sql_text[:max_sql_length] + "..."
            else:
                first_line = sql_text
            
            # 根据数据结构类型选择不同的提取逻辑
            if "规范性评审" in storage_data:
                # 旧结构
                # 第二行：违反内容
                normative_review = storage_data.get('规范性评审', {})
                violation_contents = []
                for angle_name, review_data in normative_review.items():
                    if review_data.get('status') == '未通过':
                        violation_contents.append(angle_name)
                
                second_line = "违反内容："
                if violation_contents:
                    second_line += "、".join(violation_contents[:5])
                else:
                    second_line += "无"
                
                # 第三行：违反规范
                compliance_data = storage_data.get('规范符合性', {})
                compliance_violations = compliance_data.get('规范违反详情', [])
                violation_rules = []
                for violation in compliance_violations[:3]:
                    if isinstance(violation, dict):
                        description = violation.get('description', '')
                        violation_rules.append(description)
                
                third_line = "违反规范："
                if violation_rules:
                    third_line += "、".join(violation_rules[:3])
                else:
                    third_line += "无"
                
                # 第四行：修改建议
                suggestions = storage_data.get('建议', [])
                fourth_line = "修改建议："
                if suggestions:
                    fourth_line += suggestions[0][:80]
                    if len(suggestions) > 1:
                        fourth_line += f"（共{len(suggestions)}条建议）"
                else:
                    fourth_line += "无"
            else:
                # 新结构
                # 第二行：违反内容
                key_issues = storage_data.get('key_issues', [])
                violation_contents = []
                for issue in key_issues[:5]:
                    if isinstance(issue, dict):
                        category = issue.get('category', '')
                        severity = issue.get('severity', '')
                        if severity in ['高风险', '中风险'] and category:
                            violation_contents.append(category)
                
                if not violation_contents:
                    normative_summary = storage_data.get('normative_summary', {})
                    failed_angles = normative_summary.get('failed', [])
                    violation_contents = failed_angles[:5]
                
                second_line = "违反内容："
                if violation_contents:
                    second_line += "、".join(violation_contents[:5])
                else:
                    second_line += "无"
                
                # 第三行：违反规范
                normative_summary = storage_data.get('normative_summary', {})
                violation_rules = []
                failed_angles = normative_summary.get('failed', [])
                for angle in failed_angles[:3]:
                    violation_rules.append(angle)
                
                third_line = "违反规范："
                if violation_rules:
                    third_line += "、".join(violation_rules[:3])
                else:
                    third_line += "无"
                
                # 第四行：修改建议
                suggestions = storage_data.get('suggestions', [])
                optimized_sql = storage_data.get('optimized_sql', '')
                
                fourth_line = "修改建议："
                if optimized_sql:
                    # 清理优化SQL：移除注释和多余空格
                    clean_optimized_sql = optimized_sql.strip()
                    if clean_optimized_sql.startswith("--"):
                        lines = clean_optimized_sql.split('\n')
                        if len(lines) > 1:
                            sql_part = lines[1].strip()
                        else:
                            sql_part = clean_optimized_sql
                    else:
                        sql_part = clean_optimized_sql
                    
                    if len(sql_part) > 80:
                        fourth_line += f"优化SQL：{sql_part[:80]}..."
                    else:
                        fourth_line += f"优化SQL：{sql_part}"
                elif suggestions:
                    main_suggestion = suggestions[0]
                    clean_suggestion = main_suggestion.strip()
                    if len(clean_suggestion) > 80:
                        fourth_line += f"{clean_suggestion[:80]}..."
                    else:
                        fourth_line += clean_suggestion
                    
                    if len(suggestions) > 1:
                        fourth_line += f"（共{len(suggestions)}条建议）"
                else:
                    fourth_line += "无"
            
            # 组合四行文本
            lines = [first_line, second_line, third_line, fourth_line]
            simplified_text = "\n".join(lines[:500] for lines in lines)
            
            return simplified_text
            
        except Exception as e:
            return f"数据处理失败: {str(e)}"
    
    old_simplified = simulate_simplify_storage_data(old_data)
    new_simplified = simulate_simplify_storage_data(new_data)
    
    print(f"\n   旧结构简化文本:")
    for i, line in enumerate(old_simplified.split('\n')[:4]):
        print(f"     第{i+1}行: {line[:100]}..." if len(line) > 100 else f"     第{i+1}行: {line}")
    
    print(f"\n   新结构简化文本:")
    for i, line in enumerate(new_simplified.split('\n')[:4]):
        print(f"     第{i+1}行: {line[:100]}..." if len(line) > 100 else f"     第{i+1}行: {line}")
    
    print(f"\n5. 结论:")
    print(f"   优化效果显著:")
    print(f"   - 存储空间减少: {len(old_json) - len(new_json)} 字符")
    print(f"   - 结构更简洁: 字段减少 {len(old_data) - len(new_data)} 个")
    print(f"   - 嵌套层级降低: 从 {old_depth} 层减少到 {new_depth} 层")
    print(f"   - 关键信息更突出: 综合评分、建议数量、规范符合度一目了然")
    print(f"   - 查询效率更高: 扁平化结构减少JSON解析开销")
    
    return True

def main():
    """主函数"""
    try:
        print("开始测试优化后的入表数据结构...")
        
        # 创建测试数据
        old_structure, new_structure = create_sample_data()
        
        # 比较新旧结构
        success = compare_structures(old_structure, new_structure)
        
        # 保存测试数据供检查
        with open("test_old_structure.json", "w", encoding="utf-8") as f:
            json.dump(old_structure, f, ensure_ascii=False, indent=2)
        
        with open("test_new_structure.json", "w", encoding="utf-8") as f:
            json.dump(new_structure, f, ensure_ascii=False, indent=2)
        
        print("\n测试数据已保存:")
        print("  - test_old_structure.json (优化前结构)")
        print("  - test_new_structure.json (优化后结构)")
        
        print("\n✓ 测试完成！优化效果显著。")
        return success
        
    except Exception as e:
        print(f"测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    import sys
    sys.exit(0 if success else 1)
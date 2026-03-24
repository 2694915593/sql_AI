#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SQL规范提示词生成器模块
负责生成包含SQL规范的提示词
"""

import re
from typing import Dict, List, Any, Optional, Tuple
from .sql_specifications import SQLType, SQLSpecificationsManager, integrate_specifications_into_prompt


class SpecificationsPromptGenerator:
    """
    SQL规范提示词生成器
    生成包含SQL规范的提示词
    """
    
    def __init__(self):
        """初始化提示词生成器"""
        self.specifications_manager = SQLSpecificationsManager()
    
    def generate_sql_specifications_prompt(self, sql_type: SQLType) -> str:
        """
        生成SQL规范提示词
        
        Args:
            sql_type: SQL类型
            
        Returns:
            规范提示词
        """
        relevant_rules = self.specifications_manager.get_specifications_by_sql_type(sql_type)
        
        prompt_parts = []
        prompt_parts.append("SQL规范要求：")
        prompt_parts.append("请根据以下SQL规范对SQL语句进行分析和优化：")
        prompt_parts.append("")
        
        # 按分类组织规则
        rules_by_category = {}
        for rule in relevant_rules:
            category = self._get_rule_category(rule)
            if category not in rules_by_category:
                rules_by_category[category] = []
            rules_by_category[category].append(rule)
        
        # 生成分类化的规范提示
        for category, rules in rules_by_category.items():
            prompt_parts.append(f"【{category}】")
            for rule in rules[:10]:  # 每个分类最多10条规则，避免过长
                level_str = rule["level"].value if hasattr(rule["level"], "value") else rule["level"]
                # 简化内容，保留关键信息
                simplified_content = self._simplify_rule_content(rule["content"])
                prompt_parts.append(f"  {rule['id']} 【{level_str}】: {simplified_content}")
            prompt_parts.append("")
        
        # 添加分析要求
        prompt_parts.append("基于以上SQL规范的分析要求：")
        prompt_parts.append("1. 首先检查SQL语句是否符合相关规范")
        prompt_parts.append("2. 识别违反规范的语句和潜在风险")
        prompt_parts.append("3. 提供具体的、可执行的修改建议SQL")
        prompt_parts.append("4. 确保修改建议SQL完全符合所有相关规范")
        prompt_parts.append("5. 在风险评估中明确标注违反规范的问题")
        prompt_parts.append("6. 给出基于规范符合性的综合评分")
        prompt_parts.append("")
        prompt_parts.append("重要提示：")
        prompt_parts.append("- 修改建议SQL必须是可执行的、语法正确的SQL语句")
        prompt_parts.append("- 对于违反强制规范的SQL，必须提供修复建议")
        prompt_parts.append("- 确保建议的优化不违反任何SQL规范")
        prompt_parts.append("- 优先解决高风险问题，确保SQL质量和安全性")
        
        return "\n".join(prompt_parts)
    
    def _get_rule_category(self, rule: Dict[str, Any]) -> str:
        """获取规则所属分类"""
        # 根据规则ID判断分类
        rule_id = rule["id"]
        if rule_id.startswith("2.1"):
            return "字符集规范"
        elif rule_id.startswith("2.2"):
            return "命名规范"
        elif rule_id.startswith("2.3"):
            return "业务表规范"
        elif rule_id.startswith("2.4"):
            return "字段规范"
        elif rule_id.startswith("2.5"):
            return "自增列和序列规范"
        elif rule_id.startswith("2.6"):
            return "索引规范"
        elif rule_id.startswith("2.7"):
            return "其他禁用类规范"
        elif rule_id.startswith("3.1"):
            return "查询语句规范"
        elif rule_id.startswith("3.2"):
            return "多表关联查询语句规范"
        elif rule_id.startswith("3.3"):
            return "增删改语句规范"
        elif rule_id.startswith("3.4"):
            return "事务规范"
        elif rule_id.startswith("3.5"):
            return "其他规范"
        else:
            return "其他规范"
    
    def _simplify_rule_content(self, content: str) -> str:
        """简化规则内容，保留关键信息"""
        # 移除过长的示例和详细说明
        lines = content.split('\n')
        simplified_lines = []
        
        for line in lines:
            # 保留关键信息，移除过于详细的说明
            if len(line) > 200:
                line = line[:200] + "..."
            
            # 移除版本信息标记（如【v3.2.3】）
            line = re.sub(r'【v\d+\.\d+\.\d+[^】]*】', '', line)
            
            # 保留核心内容
            if line.strip() and not line.strip().startswith("反例："):
                simplified_lines.append(line.strip())
        
        # 合并为单个字符串，限制长度
        simplified = " ".join(simplified_lines[:3])  # 最多3行
        if len(simplified) > 300:
            simplified = simplified[:300] + "..."
        
        return simplified
    
    def generate_enhanced_prompt(self, base_prompt_parts: List[str], sql_type: SQLType) -> str:
        """
        生成增强版提示词（包含SQL规范）
        
        Args:
            base_prompt_parts: 基础提示词部分
            sql_type: SQL类型
            
        Returns:
            增强版提示词
        """
        # 集成规范到提示词
        enhanced_parts = integrate_specifications_into_prompt(base_prompt_parts, sql_type)
        
        # 确保有清晰的输出格式要求
        enhanced_parts.append("\n输出格式要求：")
        enhanced_parts.append("请严格按照以下JSON格式回复，不要包含任何其他内容：")
        enhanced_parts.append('''{
  "建议": ["具体建议1", "具体建议2", "具体建议3"],
  "SQL类型": "查询/更新/插入/删除/建表/其他",
  "分析摘要": "简明的分析摘要，包括SQL的主要问题和优化建议",
  "综合评分": 0-10,
  "规范符合性": {
    "合规规则": ["2.3.1", "3.1.1"],
    "违规规则": ["2.3.4", "3.1.10"],
    "规范符合度": 85.5,
    "规范违反详情": [
      {
        "rule_id": "3.1.1",
        "description": "SELECT字段规范",
        "violation": "使用了SELECT *",
        "suggestion": "指定具体字段名"
      }
    ]
  },
  "风险评估": {
    "高风险问题": ["高风险问题1", "高风险问题2"],
    "中风险问题": ["中风险问题1", "中风险问题2"],
    "低风险问题": ["低风险问题1", "低风险问题2"]
  },
  "修改建议": {
    "高风险问题SQL": "针对高风险问题修改后的具体SQL语句示例",
    "中风险问题SQL": "针对中风险问题修改后的具体SQL语句示例",
    "低风险问题SQL": "针对低风险问题修改后的具体SQL语句示例",
    "性能优化SQL": "针对性能问题优化后的具体SQL语句示例"
  }
}''')
        
        enhanced_parts.append("\n重要提示：")
        enhanced_parts.append("1. 综合评分范围是0-10分，分数越高表示SQL质量越好")
        enhanced_parts.append("2. 规范符合度是百分比，表示SQL符合相关规范的程度")
        enhanced_parts.append("3. 规范违反详情必须具体明确，包含规则ID和违反内容")
        enhanced_parts.append("4. 修改建议字段必须提供具体的、可执行的SQL语句")
        enhanced_parts.append("5. 所有修改建议SQL必须是可执行的、语法正确的SQL语句")
        enhanced_parts.append("6. 建议字段提供3-5条具体的改进建议")
        enhanced_parts.append("7. 分析摘要要简洁明了，包含SQL的主要问题和优化建议")
        enhanced_parts.append("8. 特别关注规范符合性，确保SQL符合所有相关规范")
        enhanced_parts.append("\n注意：请只回复JSON格式的内容，不要包含任何解释性文字。")
        
        return "\n".join(enhanced_parts)
    
    def generate_sql_type_specific_prompt(self, sql: str, sql_type: Optional[SQLType] = None) -> str:
        """
        生成针对特定SQL类型的提示词
        
        Args:
            sql: SQL语句
            sql_type: SQL类型，如果为None则自动检测
            
        Returns:
            针对性的提示词
        """
        if sql_type is None:
            sql_type = self.specifications_manager.detect_sql_type(sql)
        
        # 基础提示部分
        base_parts = [
            f"SQL语句：\n{sql}\n",
            f"SQL类型：{sql_type.value}\n",
            "请分析以上SQL语句的质量、性能和安全性。"
        ]
        
        # 根据SQL类型添加特定要求
        if sql_type == SQLType.SELECT:
            base_parts.append("\n对于SELECT语句，请特别关注：")
            base_parts.append("1. 是否指定具体字段（禁止SELECT *）")
            base_parts.append("2. 是否使用合适的索引")
            base_parts.append("3. 是否有全表扫描风险")
            base_parts.append("4. 是否使用物理分页（LIMIT）")
            base_parts.append("5. 排序结果是否稳定（ORDER BY）")
        elif sql_type == SQLType.INSERT:
            base_parts.append("\n对于INSERT语句，请特别关注：")
            base_parts.append("1. 是否指定列名（禁止INSERT ... VALUES）")
            base_parts.append("2. 是否有SQL注入风险")
            base_parts.append("3. 批量插入性能")
            base_parts.append("4. ON DUPLICATE KEY UPDATE使用规范")
        elif sql_type == SQLType.UPDATE or sql_type == SQLType.DELETE:
            base_parts.append("\n对于UPDATE/DELETE语句，请特别关注：")
            base_parts.append("1. 是否有WHERE条件")
            base_parts.append("2. 是否使用LIMIT避免大事务")
            base_parts.append("3. 是否使用合适的索引")
            base_parts.append("4. 对性能的影响评估")
        elif sql_type == SQLType.CREATE:
            base_parts.append("\n对于CREATE语句，请特别关注：")
            base_parts.append("1. 字符集和字符序设置")
            base_parts.append("2. 表和字段命名规范")
            base_parts.append("3. 字段类型选择（特别是小数类型）")
            base_parts.append("4. 索引设计合理性")
            base_parts.append("5. 表和字段注释")
        elif sql_type == SQLType.ALTER:
            base_parts.append("\n对于ALTER语句，请特别关注：")
            base_parts.append("1. 对现有业务的影响")
            base_parts.append("2. 列属性修改规范")
            base_parts.append("3. 索引变更影响")
            base_parts.append("4. DDL执行时间")
        
        # 生成增强版提示词
        enhanced_prompt = self.generate_enhanced_prompt(base_parts, sql_type)
        return enhanced_prompt
    
    def generate_compact_specifications_prompt(self, sql_type: SQLType) -> str:
        """
        生成紧凑版SQL规范提示词（用于提示词长度限制）
        
        Args:
            sql_type: SQL类型
            
        Returns:
            紧凑版规范提示词
        """
        relevant_rules = self.specifications_manager.get_specifications_by_sql_type(sql_type)
        
        # 只选择关键规则（强制规范）
        key_rules = [rule for rule in relevant_rules 
                    if (hasattr(rule["level"], "value") and rule["level"].value == "强制") 
                    or rule["level"] == "强制"]
        
        # 如果关键规则太多，只取前5条
        if len(key_rules) > 5:
            key_rules = key_rules[:5]
        
        prompt_parts = []
        prompt_parts.append("关键SQL规范要求：")
        
        for rule in key_rules:
            rule_id = rule["id"]
            description = rule["description"]
            
            # 生成简化的提示
            if rule_id == "3.1.1":
                prompt_parts.append(f"- {rule_id}: SELECT必须指定字段，禁止SELECT *")
            elif rule_id == "3.3.1":
                prompt_parts.append(f"- {rule_id}: UPDATE/DELETE必须有WHERE条件或LIMIT")
            elif rule_id == "3.3.4":
                prompt_parts.append(f"- {rule_id}: INSERT必须指定列名")
            elif rule_id == "2.3.1":
                prompt_parts.append(f"- {rule_id}: 表名列名禁止大小写混用和反引号")
            elif rule_id == "2.4.1":
                prompt_parts.append(f"- {rule_id}: 小数类型使用DECIMAL，禁止DOUBLE/FLOAT")
            else:
                # 通用的简化提示
                simplified_desc = description[:50] + "..." if len(description) > 50 else description
                prompt_parts.append(f"- {rule_id}: {simplified_desc}")
        
        prompt_parts.append("")
        prompt_parts.append("请确保SQL符合以上关键规范，并在分析中检查规范符合性。")
        
        return "\n".join(prompt_parts)


def generate_sql_specifications_prompt(sql_type_str: str) -> str:
    """
    生成SQL规范提示词（便捷函数）
    
    Args:
        sql_type_str: SQL类型字符串
        
    Returns:
        规范提示词
    """
    try:
        sql_type = SQLType(sql_type_str.lower())
        generator = SpecificationsPromptGenerator()
        return generator.generate_sql_specifications_prompt(sql_type)
    except ValueError:
        # 如果类型不合法，使用默认的SELECT类型
        generator = SpecificationsPromptGenerator()
        return generator.generate_sql_specifications_prompt(SQLType.SELECT)


# 测试函数
def test_prompt_generator():
    """测试提示词生成器"""
    generator = SpecificationsPromptGenerator()
    
    print("=" * 60)
    print("测试SQL规范提示词生成器")
    print("=" * 60)
    
    # 测试生成SELECT规范提示词
    print("\n1. 生成SELECT规范提示词（前500字符）：")
    select_prompt = generator.generate_sql_specifications_prompt(SQLType.SELECT)
    print(select_prompt[:500] + "..." if len(select_prompt) > 500 else select_prompt)
    
    # 测试生成紧凑版提示词
    print("\n2. 生成SELECT紧凑版提示词：")
    compact_prompt = generator.generate_compact_specifications_prompt(SQLType.SELECT)
    print(compact_prompt)
    
    # 测试生成SQL类型特定提示词
    print("\n3. 生成SELECT语句特定提示词（前500字符）：")
    sql = "SELECT * FROM users WHERE age > 18"
    specific_prompt = generator.generate_sql_type_specific_prompt(sql, SQLType.SELECT)
    print(specific_prompt[:500] + "..." if len(specific_prompt) > 500 else specific_prompt)
    
    # 测试便捷函数
    print("\n4. 测试便捷函数：")
    prompt = generate_sql_specifications_prompt("select")
    print(f"生成的提示词长度: {len(prompt)} 字符")
    
    return True


if __name__ == "__main__":
    test_prompt_generator()
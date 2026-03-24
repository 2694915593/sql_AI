#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强SQL规范管理器模块
基于用户提供的完整规范列表进行补充
"""

import re
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
from .sql_specifications import SQLType, RuleLevel, SQLSpecificationsManager as BaseManager


class EnhancedSQLSpecificationsManager(BaseManager):
    """
    增强SQL规范管理器
    基于用户提供的完整规范列表进行补充
    """
    
    def _initialize_specifications(self) -> Dict[str, Any]:
        """
        初始化增强版SQL规范数据结构
        基于用户提供的完整规范文档
        """
        # 先调用父类的初始化
        base_specs = super()._initialize_specifications()
        
        # 补充缺失的规范
        self._supplement_specifications(base_specs)
        
        return base_specs
    
    def _supplement_specifications(self, base_specs: Dict[str, Any]) -> None:
        """补充缺失的规范"""
        
        # 1. 补充SELECT规范
        if "查询语句规范" in base_specs:
            select_rules = base_specs["查询语句规范"]["rules"]
            
            # 补充SELECT *规范（如果不存在）
            if not any(rule["id"] == "3.1.1" for rule in select_rules):
                select_rules.insert(0, {
                    "id": "3.1.1",
                    "level": RuleLevel.MANDATORY,
                    "content": "应用程序中，SELECT语句必须指定具体字段名称，禁止写成 'select *'。",
                    "description": "SELECT字段规范",
                    "sql_types": [SQLType.SELECT],
                    "applicable_scenarios": ["查询"]
                })
            
            # 补充物理分页规范
            if not any(rule["id"] == "3.1.10" for rule in select_rules):
                select_rules.append({
                    "id": "3.1.10",
                    "level": RuleLevel.MANDATORY,
                    "content": "在不确定结果集大小如非主键、非唯一键查询或关联查询，应使用物理分页(即SQL中使用limit)，避免出现大结果集造成程序 JVM OOM。",
                    "description": "物理分页规范",
                    "sql_types": [SQLType.SELECT],
                    "applicable_scenarios": ["查询"]
                })
            
            # 补充排序稳定性规范
            if not any(rule["id"] == "3.1.13" for rule in select_rules):
                select_rules.append({
                    "id": "3.1.13",
                    "level": RuleLevel.MANDATORY,
                    "content": "业务逻辑要求查询结果有序或稳定时，需添加order by排序，且排序字段必须唯一或者组合唯一（非空），否则会造成结果不稳定（即每次查询结果集顺序不一致）。分页查询或join表关联后row_number() over() 获取序号场景，尤为注意。",
                    "description": "排序稳定性规范",
                    "sql_types": [SQLType.SELECT],
                    "applicable_scenarios": ["查询"]
                })
        
        # 2. 补充禁用功能规范
        if "其他禁用类规范" in base_specs:
            disable_rules = base_specs["其他禁用类规范"]["rules"]
            
            # 补充外键、临时表、存储过程、触发器禁用规范
            if not any(rule["id"] == "2.7.1" for rule in disable_rules):
                disable_rules.insert(0, {
                    "id": "2.7.1",
                    "level": RuleLevel.MANDATORY,
                    "content": "禁止在应用程序设计阶段使用外键、临时表（CREATE TEMPORARY TABLE）、存储过程以及触发器。",
                    "description": "禁用功能规范",
                    "sql_types": [SQLType.CREATE],
                    "applicable_scenarios": ["所有创建操作"]
                })
        
        # 3. 补充增删改语句规范
        if "增删改语句规范" in base_specs:
            dml_rules = base_specs["增删改语句规范"]["rules"]
            
            # 补充INSERT指定列规范
            if not any(rule["id"] == "3.3.4" for rule in dml_rules):
                dml_rules.append({
                    "id": "3.3.4",
                    "level": RuleLevel.MANDATORY,
                    "content": "INSERT时必须指定列，以避免数据表出现结构上变化时造成程序错误，如在表中增加了一个字段；",
                    "description": "INSERT列指定规范",
                    "sql_types": [SQLType.INSERT],
                    "applicable_scenarios": ["插入"]
                })
            
            # 补充ON DUPLICATE KEY UPDATE规范
            if not any(rule["id"] == "3.3.6" for rule in dml_rules):
                dml_rules.append({
                    "id": "3.3.6",
                    "level": RuleLevel.MANDATORY,
                    "content": "执行INSERT INTO table_name(list_of_columns) VALUES (list_of_values) ON DUPLICATE KEY UPDATE语句时，对于非空字段无论是否需要更新，禁止传入null值；",
                    "description": "ON DUPLICATE KEY UPDATE规范",
                    "sql_types": [SQLType.INSERT],
                    "applicable_scenarios": ["插入"]
                })
            
            # 补充分区表操作索引失效规范
            if not any(rule["id"] == "3.3.7" for rule in dml_rules):
                dml_rules.append({
                    "id": "3.3.7",
                    "level": RuleLevel.MANDATORY,
                    "content": "在对分区表执行DROP或TRUNCATE分区操作时，需注意执行期间全局索引会失效。",
                    "description": "分区表操作索引失效规范",
                    "sql_types": [SQLType.DROP, SQLType.TRUNCATE],
                    "applicable_scenarios": ["删除分区", "清空分区"]
                })
        
        # 4. 补充序列规范（新增分类）
        if "序列规范" not in base_specs:
            base_specs["序列规范"] = {
                "category": "序列规范",
                "description": "序列使用和配置规范",
                "rules": [
                    {
                        "id": "2.5.5",
                        "level": RuleLevel.MANDATORY,
                        "content": "noorder选项的序列不保证全局单调递增，发生切主时等特定情况下值会跳变，应用要避免跳变带来的值变大或变小的影响。",
                        "description": "序列noorder选项规范",
                        "sql_types": [SQLType.CREATE],
                        "applicable_scenarios": ["创建序列"]
                    },
                    {
                        "id": "2.5.6",
                        "level": RuleLevel.MANDATORY,
                        "content": "序列字段使用bigint类型存储，禁止使用int类型，防止存储溢出。",
                        "description": "序列字段类型规范",
                        "sql_types": [SQLType.CREATE, SQLType.ALTER],
                        "applicable_scenarios": ["创建序列", "修改序列"]
                    }
                ]
            }
        
        # 5. 补充其他规范
        if "其他规范" in base_specs:
            other_rules = base_specs["其他规范"]["rules"]
            
            # 补充OPTIMIZE TABLE规范
            if not any(rule["id"] == "3.5.3" for rule in other_rules):
                other_rules.append({
                    "id": "3.5.3",
                    "level": RuleLevel.MANDATORY,
                    "content": "禁止使用optimize table语法，因在OceanBase中该指令无法重整表结构，且可能引发schema同步延迟风险。",
                    "description": "OPTIMIZE TABLE使用规范",
                    "sql_types": [SQLType.OTHER],
                    "applicable_scenarios": ["表维护"]
                })
            
            # 补充IF函数规范
            if not any(rule["id"] == "3.5.4" for rule in other_rules):
                other_rules.append({
                    "id": "3.5.4",
                    "level": RuleLevel.MANDATORY,
                    "content": "在使用if(expr1, expr2, expr3)函数时，expr1不能为字符类型，否则SQL语句的执行结果可能会不符合预期。反例：if(c5, 'cc', '123')，其中c5为字符类型，if函数会尝试将c5的值转成数值类型，转换可能会失败，若为select语句，SQL语句执行成功但结果为'123'，同时报warning，若为update语句会直接报错",
                    "description": "IF函数参数类型规范",
                    "sql_types": [SQLType.SELECT, SQLType.UPDATE],
                    "applicable_scenarios": ["查询", "更新"]
                })
            
            # 补充SQL Hint规范
            if not any(rule["id"] == "3.5.5" for rule in other_rules):
                other_rules.append({
                    "id": "3.5.5",
                    "level": RuleLevel.MANDATORY,
                    "content": "SQL Hint必须经过验证确保其有效性，避免因语法错误或位置不当等原因导致HINT被忽略。",
                    "description": "SQL Hint使用规范",
                    "sql_types": [SQLType.SELECT, SQLType.INSERT, SQLType.UPDATE, SQLType.DELETE],
                    "applicable_scenarios": ["所有数据操作"]
                })
        
        # 6. 补充CASE WHEN规范（新增分类）
        if "表达式规范" not in base_specs:
            base_specs["表达式规范"] = {
                "category": "表达式规范",
                "description": "SQL表达式使用规范",
                "rules": [
                    {
                        "id": "3.6.1",
                        "level": RuleLevel.MANDATORY,
                        "content": "case when表达式应控制在150个以内，case when表达式过多可能会导致性能下降或租户内存被打爆；",
                        "description": "CASE WHEN表达式数量规范",
                        "sql_types": [SQLType.SELECT, SQLType.UPDATE],
                        "applicable_scenarios": ["查询", "更新"]
                    },
                    {
                        "id": "3.6.2",
                        "level": RuleLevel.MANDATORY,
                        "content": "CASE WHEN 语句必须显式定义ELSE分支并明确返回值，避免因隐式返回NULL 值而出现非预期的结果。",
                        "description": "CASE WHEN ELSE分支规范",
                        "sql_types": [SQLType.SELECT, SQLType.UPDATE],
                        "applicable_scenarios": ["查询", "更新"]
                    }
                ]
            }
    
    def generate_simplified_specifications_prompt(self, sql_type: SQLType) -> str:
        """
        生成简化版规范提示词
        只包含关键规范，用于大模型分析
        
        Args:
            sql_type: SQL类型
            
        Returns:
            简化版规范提示词
        """
        relevant_rules = self.get_specifications_by_sql_type(sql_type)
        
        if not relevant_rules:
            return "无相关SQL规范要求。"
        
        prompt_parts = []
        prompt_parts.append("SQL规范检查要求：")
        prompt_parts.append("请检查以下SQL语句是否符合相关规范。如果违反规范，请详细说明违反内容和改进建议；如果没有违反，请返回'不涉及'。")
        prompt_parts.append("")
        prompt_parts.append("相关规范如下：")
        
        # 按分类组织，每个分类最多显示5条关键规范
        rules_by_category = {}
        for rule in relevant_rules:
            # 确定分类
            category = self._determine_rule_category(rule)
            if category not in rules_by_category:
                rules_by_category[category] = []
            
            # 只添加强制规范
            if rule["level"] == RuleLevel.MANDATORY:
                rules_by_category[category].append(rule)
        
        # 生成分类化的规范提示
        for category, rules in rules_by_category.items():
            if rules:
                prompt_parts.append(f"【{category}】")
                for rule in rules[:5]:  # 每个分类最多5条规则
                    simplified_content = self._simplify_for_prompt(rule["content"])
                    prompt_parts.append(f"- {simplified_content}")
                prompt_parts.append("")
        
        prompt_parts.append("输出要求：")
        prompt_parts.append("1. 如果SQL违反上述任何规范，请详细说明：")
        prompt_parts.append("   - 违反的规范内容")
        prompt_parts.append("   - 具体的违反位置和原因")
        prompt_parts.append("   - 改进建议和修复后的SQL示例")
        prompt_parts.append("2. 如果SQL没有违反上述规范，请返回：'不涉及'")
        prompt_parts.append("3. 请使用简洁明了的语言，避免冗长解释")
        
        return "\n".join(prompt_parts)
    
    def _determine_rule_category(self, rule: Dict[str, Any]) -> str:
        """根据规则ID确定分类"""
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
            return "序列规范"
        elif rule_id.startswith("2.6"):
            return "索引规范"
        elif rule_id.startswith("2.7"):
            return "禁用功能规范"
        elif rule_id.startswith("3.1"):
            return "查询语句规范"
        elif rule_id.startswith("3.2"):
            return "关联查询规范"
        elif rule_id.startswith("3.3"):
            return "增删改语句规范"
        elif rule_id.startswith("3.4"):
            return "事务规范"
        elif rule_id.startswith("3.5"):
            return "其他规范"
        elif rule_id.startswith("3.6"):
            return "表达式规范"
        else:
            return "通用规范"
    
    def _simplify_for_prompt(self, content: str) -> str:
        """简化规范内容用于提示词"""
        # 移除版本标记和过长的说明
        simplified = re.sub(r'【v\d+\.\d+\.\d+[^】]*】', '', content)
        simplified = re.sub(r'反例：.*', '', simplified)
        simplified = re.sub(r'例如：.*', '', simplified)
        
        # 限制长度
        if len(simplified) > 120:
            simplified = simplified[:120] + "..."
        
        return simplified.strip()
    
    def check_sql_compliance(self, sql: str, sql_type: Optional[SQLType] = None) -> Dict[str, Any]:
        """
        检查SQL规范符合性
        简化版检查，只返回违反详情
        
        Args:
            sql: SQL语句
            sql_type: SQL类型，如果为None则自动检测
            
        Returns:
            检查结果，格式：{"has_violations": bool, "violations": List, "compliance_score": float}
        """
        if sql_type is None:
            sql_type = self.detect_sql_type(sql)
        
        relevant_rules = self.get_specifications_by_sql_type(sql_type)
        violations = []
        
        # 这里可以实现具体的检查逻辑
        # 目前先返回空结果，实际的检查由大模型完成
        for rule in relevant_rules:
            rule_id = rule["id"]
            rule_content = rule["content"]
            
            # 简单检查示例
            if sql_type == SQLType.SELECT and rule_id == "3.1.1":
                if re.search(r'SELECT\s+\*\s+FROM', sql, re.IGNORECASE):
                    violations.append({
                        "rule_id": rule_id,
                        "description": rule["description"],
                        "violation": "使用了SELECT *",
                        "suggestion": "指定具体字段名，如SELECT id, name FROM table_name"
                    })
        
        has_violations = len(violations) > 0
        
        # 计算合规评分（简化版）
        total_rules = len(relevant_rules)
        compliant_rules = total_rules - len(violations)
        compliance_score = (compliant_rules / total_rules * 100) if total_rules > 0 else 100
        
        return {
            "has_violations": has_violations,
            "violations": violations,
            "compliance_score": round(compliance_score, 1),
            "total_rules_checked": total_rules,
            "compliant_rules": compliant_rules
        }


def get_enhanced_specifications_prompt(sql_type: SQLType) -> str:
    """
    获取增强版规范提示词
    
    Args:
        sql_type: SQL类型
        
    Returns:
        增强版规范提示词
    """
    manager = EnhancedSQLSpecificationsManager()
    return manager.generate_simplified_specifications_prompt(sql_type)


def check_sql_with_enhanced_specifications(sql: str) -> Dict[str, Any]:
    """
    使用增强规范检查SQL
    
    Args:
        sql: SQL语句
        
    Returns:
        检查结果
    """
    manager = EnhancedSQLSpecificationsManager()
    sql_type = manager.detect_sql_type(sql)
    return manager.check_sql_compliance(sql, sql_type)


# 测试函数
def test_enhanced_specifications():
    """测试增强规范管理器"""
    manager = EnhancedSQLSpecificationsManager()
    
    print("=" * 60)
    print("测试增强SQL规范管理器")
    print("=" * 60)
    
    # 测试规范摘要
    summary = manager.get_specifications_summary()
    print(f"规范分类数: {summary['total_categories']}")
    print(f"规范总条款数: {summary['total_rules']}")
    
    # 测试简化提示词生成
    print(f"\nSELECT语句简化规范提示词（前300字符）:")
    select_prompt = manager.generate_simplified_specifications_prompt(SQLType.SELECT)
    print(select_prompt[:300] + "..." if len(select_prompt) > 300 else select_prompt)
    
    # 测试SQL检查
    print(f"\nSQL规范检查测试:")
    test_sql = "SELECT * FROM users WHERE age > 18"
    check_result = manager.check_sql_compliance(test_sql)
    print(f"  SQL: {test_sql}")
    print(f"  是否违规: {check_result['has_violations']}")
    print(f"  违规数量: {len(check_result['violations'])}")
    print(f"  合规评分: {check_result['compliance_score']}%")
    
    if check_result['violations']:
        for violation in check_result['violations']:
            print(f"    - {violation['violation']}: {violation['suggestion']}")
    
    return True


if __name__ == "__main__":
    test_enhanced_specifications()
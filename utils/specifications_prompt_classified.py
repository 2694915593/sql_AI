#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分类版SQL规范提示词生成器
按照用户提供的分类表格重新组织53条SQL规范
"""

from typing import List, Dict, Any
from .sql_specifications import SQLType


class ClassifiedSpecificationsPromptGenerator:
    """分类版SQL规范提示词生成器"""
    
    def __init__(self):
        """初始化生成器"""
        self.classified_rules = self._get_classified_rules()
    
    def _get_classified_rules(self) -> Dict[str, List[str]]:
        """
        获取按类别组织的规范规则
        
        返回:
            类别到规则列表的字典
        """
        rules = {
            "建表语句": [
                "表名和列名禁止大小写混用，禁止反闭包（backquote）表名和列名",
                "表名和列名只能使用字母、数字和下划线，必须以字母开头，不得使用系统保留字和特殊字符",
                "表名禁止两个下划线中间只出现数字",
                "定义表结构时，表或列须用comment属性加上注释",
                "禁止使用生成列作为分区键",
                "小数类型使用decimal存储，禁止使用double、float、varchar",
                "表上强制添加创建时间（CREATE_TIME）和变更时间（UPDATE_TIME）字段，类型DATETIME(6)，并设置默认值及ON UPDATE属性",
                "禁止使用枚举数据类型",
                "禁止使用定义为STORED类型且依赖其他列值计算的生成列",
                "自增列字段使用bigint类型存储，禁止使用int类型",
                "禁止使用自增列作为分区键",
                "修改列名、列长度等属性时，须带上列的原属性值，以避免定义被覆盖",
                "对分区表执行DROP或TRUNCATE分区操作时，注意执行期间全局索引会失效"
            ],
            "查询语句": [
                "当字段类型为字符串时，禁止直接对该字段数据进行数值函数计算",
                "联机TP交易SQL语句运行时必须使用对应的索引",
                "通用表达式CTE recursive递归行数禁止超过1000",
                "禁用get_format函数",
                "SELECT语句必须指定具体字段名称，禁止写成'select *'",
                "禁止大表查询使用全表扫描",
                "非主键/非唯一键查询或关联查询，应使用物理分页（limit），避免大结果集",
                "查询结果需要有序时，须添加order by，且排序字段必须唯一或组合唯一（非空）",
                "多表关联必须有关联条件，禁止出现笛卡尔积",
                "子查询内SELECT列表字段禁止引用外表"
            ],
            "增删改语句": [
                "删改语句必须带where条件或使用limit物理分页，避免大事务",
                "INSERT时必须指定列",
                "INSERT ... ON DUPLICATE KEY UPDATE时，非空字段禁止传入null值",
                "INSERT INTO ... SELECT须确保SELECT结果集不超过大事务标准限制"
            ],
            "事务控制语句": [
                "禁止设置timezone、SQL_mode和isolation_level变量",
                "事务隔离级别应使用默认的RC读已提交",
                "禁止事务内第一条查询为特定写法（如select '1'；select * from t1;等）",
                "禁止创建全文索引",
                "唯一索引的所有字段须添加not null约束"
            ],
            "序列语句": [
                "创建序列必须指定cache大小，cache值=租户TPS*60*60*24/100",
                "序列禁止添加order属性",
                "序列字段使用bigint类型存储，禁止使用int类型",
                "noorder选项的序列不保证全局单调递增，值可能跳变"
            ],
            "其他DDL语句": [
                "数据库名：子系统标识(4位)+应用模块名(最多4位，可选)+db，例如gabsdb",
                "禁止使用optimize table语法"
            ],
            "通用规范": [
                "字符集应设置为utf8mb4，根据业务场景选择字符序：推荐utf8mb4_bin（大小写敏感）或utf8mb4_general_ci（不区分大小写）",
                "字符集/字符序逐级继承，若显式指定必须保证表、列与数据库一致，设置后不可修改",
                "普通租户名：小写32字符，t+应用标识(4位)+环境标识(3位)+租户编号(XX)，如tecifsit00",
                "单元化租户名：小写32字符，t+应用标识(4位)+环境标识(3位)+ZONE类型(G/C/R)+租户编号(XX)",
                "单分区数据量安全水位线2TB，超过1TB需及时清理",
                "分区表的查询或修改必须带上分区键",
                "禁止使用外键、临时表、存储过程以及触发器",
                "SQL单行注释以--开头，符号后必须加空格再写注释内容",
                "SQL语句中禁止使用数据库保留字",
                "使用SOFA-ODP组件时，SQL谓词中禁用反单引号修饰分区键",
                "case when表达式应控制在150个以内",
                "CASE WHEN语句必须显式定义ELSE分支并明确返回值",
                "DDL操作后需等待至少3秒并检查确认后再执行DML，重试三次若失败需人工处置",
                "使用if(expr1, expr2, expr3)函数时，expr1不能为字符类型",
                "SQL Hint必须经过验证确保其有效性"
            ]
        }
        
        # 验证所有规则总数为53条
        total_rules = sum(len(rules[category]) for category in rules)
        print(f"总规范条数: {total_rules}条")
        
        # 打印每个类别的规则数量
        for category in rules:
            print(f"{category}: {len(rules[category])}条")
        
        if total_rules != 53:
            print(f"警告: 规范总数为{total_rules}条，但应有53条")
        
        return rules
    
    def _get_relevant_categories_by_type(self, sql_type: SQLType) -> List[str]:
        """
        根据SQL类型获取相关类别
        
        Args:
            sql_type: SQL类型
            
        Returns:
            相关类别列表
        """
        if sql_type == SQLType.CREATE or sql_type == SQLType.ALTER:
            return ["建表语句", "通用规范", "其他DDL语句"]
        elif sql_type == SQLType.SELECT:
            return ["查询语句", "通用规范"]
        elif sql_type == SQLType.INSERT:
            return ["增删改语句", "通用规范", "建表语句"]
        elif sql_type == SQLType.UPDATE or sql_type == SQLType.DELETE:
            return ["增删改语句", "通用规范"]
        else:
            # 对于其他类型，返回所有类别
            return list(self.classified_rules.keys())
    
    def _format_rules_for_category(self, category: str) -> str:
        """
        格式化某个类别的规则
        
        Args:
            category: 类别名称
            
        Returns:
            格式化后的规则字符串
        """
        if category not in self.classified_rules:
            return ""
        
        rules = self.classified_rules[category]
        formatted = f"\n{category}：\n"
        for i, rule in enumerate(rules, 1):
            formatted += f"{i}. {rule}\n"
        return formatted
    
    def generate_prompt(self, sql_type: SQLType) -> str:
        """
        生成分类版规范提示词
        
        Args:
            sql_type: SQL类型
            
        Returns:
            分类版规范提示词
        """
        # 获取相关类别
        relevant_categories = self._get_relevant_categories_by_type(sql_type)
        
        # 构建基础规则部分（所有类别）
        base_rules = ""
        for category in self.classified_rules.keys():
            base_rules += self._format_rules_for_category(category)
        
        # 构建相关规则部分
        relevant_rules = ""
        if relevant_categories:
            relevant_rules = "\n请重点关注以下相关规范：\n"
            for category in relevant_categories:
                relevant_rules += f"\n{category}：\n"
                rules = self.classified_rules.get(category, [])
                for i, rule in enumerate(rules, 1):
                    relevant_rules += f"- {rule}\n"
        
        prompt = f"""
SQL规范检查要求：

请检查SQL语句是否符合相关规范。如果违反规范，请详细说明违反内容和改进建议；如果没有违反，请返回'不涉及'。

所有规范分类摘要：
{base_rules}

{relevant_rules}

输出要求：
1. 如果SQL违反上述任何规范，请详细说明：
   - 违反的规范内容
   - 具体的违反位置和原因
   - 改进建议和修复后的SQL示例
2. 如果SQL没有违反上述规范，请返回：'不涉及'
3. 请使用简洁明了的语言，避免冗长解释

请严格按照以下JSON格式回复，不要包含任何其他内容：
{{
  "规范检查结果": {{
    "has_violations": true/false,
    "summary": "简要总结",
    "violations": [
      {{
        "category": "规范分类",
        "description": "规范描述",
        "violation": "具体违反内容",
        "position": "违反位置",
        "suggestion": "改进建议",
        "fixed_sql_example": "修复后的SQL示例"
      }}
    ],
    "compliance_score": 85.5
  }}
}}

重要提示：
1. 如果SQL没有违反任何规范，请设置has_violations为false，violations为空数组，summary为'不涉及'
2. 如果SQL违反规范，请设置has_violations为true，并在violations中详细说明
3. compliance_score是合规评分（0-100%），表示SQL符合规范的程度
4. 请使用简洁明了的语言，避免冗长解释
5. 请只关注规范违反详情，不需要返回其他分析内容

注意：请只回复JSON格式的内容，不要包含任何解释性文字。大模型仅需返回SQL的规范违反详情，若无违反则返回'不涉及'。
"""
        
        return prompt
    
    def get_rule_count(self) -> Dict[str, int]:
        """
        获取每个类别的规则数量
        
        Returns:
            类别到规则数量的字典
        """
        counts = {}
        for category in self.classified_rules:
            counts[category] = len(self.classified_rules[category])
        return counts


def get_classified_specifications_prompt(sql_type: SQLType) -> str:
    """
    获取分类版SQL规范提示词
    
    Args:
        sql_type: SQL类型
        
    Returns:
        分类版规范提示词
    """
    generator = ClassifiedSpecificationsPromptGenerator()
    return generator.generate_prompt(sql_type)


# 测试函数
def test_classified_generator():
    """测试分类版提示词生成器"""
    generator = ClassifiedSpecificationsPromptGenerator()
    
    print("=" * 60)
    print("测试分类版SQL规范提示词生成器")
    print("=" * 60)
    
    # 检查规则数量
    counts = generator.get_rule_count()
    total_rules = sum(counts.values())
    print(f"\n总规范条数: {total_rules}条")
    for category, count in counts.items():
        print(f"  {category}: {count}条")
    
    # 测试SELECT语句提示词
    print("\n" + "=" * 60)
    print("SELECT语句提示词")
    print("=" * 60)
    select_prompt = generator.generate_prompt(SQLType.SELECT)
    print(f"提示词长度: {len(select_prompt)}字符")
    print(f"前300字符:\n{select_prompt[:300]}...")
    
    # 测试CREATE语句提示词
    print("\n" + "=" * 60)
    print("CREATE语句提示词")
    print("=" * 60)
    create_prompt = generator.generate_prompt(SQLType.CREATE)
    print(f"提示词长度: {len(create_prompt)}字符")
    print(f"前300字符:\n{create_prompt[:300]}...")
    
    # 测试INSERT语句提示词
    print("\n" + "=" * 60)
    print("INSERT语句提示词")
    print("=" * 60)
    insert_prompt = generator.generate_prompt(SQLType.INSERT)
    print(f"提示词长度: {len(insert_prompt)}字符")
    print(f"前300字符:\n{insert_prompt[:300]}...")
    
    return True


if __name__ == "__main__":
    test_classified_generator()
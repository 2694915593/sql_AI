#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强SQL规范提示词生成器
专门为model_client_enhanced.py优化，用于生成大模型分析用的规范提示词
"""

import re
from typing import List, Dict, Any
from .sql_specifications import SQLType


class SpecificationsPromptGenerator:
    """SQL规范提示词生成器"""
    
    def __init__(self):
        """初始化生成器"""
        self.base_rules = self._get_base_rules()
    
    def _get_base_rules(self) -> str:
        """获取基础规范列表"""
        return """
表名和列名规范：
1. 表名和列名禁止大小写混用，禁止反闭包（backquote）表名和列名
2. 表名和列名只能使用字母、数字和下划线，必须以字母开头，不得使用系统保留字和特殊字符
3. 表名禁止两个下划线中间只出现数字

表结构规范：
4. 定义表结构时，表或列须用comment属性加上注释
5. 禁止使用生成列作为分区键
6. 小数类型使用decimal存储，禁止使用double、float、varchar
7. 表上强制添加创建时间（CREATE_TIME）和变更时间（UPDATE_TIME）字段，类型DATETIME(6)，并设置默认值及ON UPDATE属性
8. 禁止使用枚举数据类型
9. 禁止使用定义为STORED类型且依赖其他列值计算的生成列
10. 自增列字段使用bigint类型存储，禁止使用int类型
11. 禁止使用自增列作为分区键
12. 修改列名、列长度等属性时，须带上列的原属性值，以避免定义被覆盖
13. 对分区表执行DROP或TRUNCATE分区操作时，注意执行期间全局索引会失效

字符串操作规范：
14. 当字段类型为字符串时，禁止直接对该字段数据进行数值函数计算

查询规范：
15. 联机TP交易SQL语句运行时必须使用对应的索引
16. 通用表达式CTE recursive递归行数禁止超过1000
17. 禁用get_format函数
18. SELECT语句必须指定具体字段名称，禁止写成"select *"
19. 禁止大表查询使用全表扫描
20. 非主键/非唯一键查询或关联查询，应使用物理分页（limit），避免大结果集
21. 查询结果需要有序时，须添加order by，且排序字段必须唯一或组合唯一（非空）
22. 多表关联必须有关联条件，禁止出现笛卡尔积
23. 子查询内SELECT列表字段禁止引用外表

增删改规范：
24. 删改语句必须带where条件或使用limit物理分页，避免大事务
25. INSERT时必须指定列
26. INSERT ... ON DUPLICATE KEY UPDATE时，非空字段禁止传入null值
27. INSERT INTO ... SELECT须确保SELECT结果集不超过大事务标准限制

数据库变量规范：
28. 禁止设置timezone、SQL_mode和isolation_level变量
29. 事务隔离级别应使用默认的RC读已提交
30. 禁止事务内第一条查询为特定写法（如select '1'；select * from t1;等）

索引规范：
31. 禁止创建全文索引
32. 唯一索引的所有字段须添加not null约束

序列规范：
33. 创建序列必须指定cache大小，cache值=租户TPS*60*60*24/100
34. 序列禁止添加order属性
35. 序列字段使用bigint类型存储，禁止使用int类型
36. noorder选项的序列不保证全局单调递增，值可能跳变

数据库命名规范：
37. 数据库名：子系统标识(4位)+应用模块名(最多4位，可选)+db，例如gabsdb
38. 禁止使用optimize table语法
39. 字符集应设置为utf8mb4，根据业务场景选择字符序：推荐utf8mb4_bin（大小写敏感）或utf8mb4_general_ci（不区分大小写）
40. 字符集/字符序逐级继承，若显式指定必须保证表、列与数据库一致，设置后不可修改

租户命名规范：
41. 普通租户名：小写32字符，t+应用标识(4位)+环境标识(3位)+租户编号(XX)，如tecifsit00
42. 单元化租户名：小写32字符，t+应用标识(4位)+环境标识(3位)+ZONE类型(G/C/R)+租户编号(XX)

分区规范：
43. 单分区数据量安全水位线2TB，超过1TB需及时清理
44. 分区表的查询或修改必须带上分区键

其他禁用规范：
45. 禁止使用外键、临时表、存储过程以及触发器

注释规范：
46. SQL单行注释以--开头，符号后必须加空格再写注释内容
47. SQL语句中禁止使用数据库保留字

SOFA-ODP组件规范：
48. 使用SOFA-ODP组件时，SQL谓词中禁用反单引号修饰分区键

CASE WHEN规范：
49. case when表达式应控制在150个以内
50. CASE WHEN语句必须显式定义ELSE分支并明确返回值

DDL操作规范：
51. DDL操作后需等待至少3秒并检查确认后再执行DML，重试三次若失败需人工处置

函数使用规范：
52. 使用if(expr1, expr2, expr3)函数时，expr1不能为字符类型

SQL Hint规范：
53. SQL Hint必须经过验证确保其有效性
"""
    
    def _get_relevant_rules_by_type(self, sql_type: SQLType) -> str:
        """根据SQL类型获取相关规则"""
        if sql_type == SQLType.SELECT:
            return """
请重点关注以下SELECT相关规范：
- SELECT语句必须指定具体字段名称，禁止写成"select *"
- 禁止大表查询使用全表扫描
- 非主键/非唯一键查询或关联查询，应使用物理分页（limit）
- 查询结果需要有序时，须添加order by，且排序字段必须唯一或组合唯一
- 多表关联必须有关联条件，禁止出现笛卡尔积
- 子查询内SELECT列表字段禁止引用外表
- 联机TP交易SQL语句运行时必须使用对应的索引
- 通用表达式CTE recursive递归行数禁止超过1000
- 禁止使用get_format函数
- 当字段类型为字符串时，禁止直接对该字段数据进行数值函数计算
"""
        elif sql_type == SQLType.INSERT:
            return """
请重点关注以下INSERT相关规范：
- INSERT时必须指定列
- INSERT ... ON DUPLICATE KEY UPDATE时，非空字段禁止传入null值
- INSERT INTO ... SELECT须确保SELECT结果集不超过大事务标准限制
- 禁止使用自增列作为分区键
- 自增列字段使用bigint类型存储，禁止使用int类型
"""
        elif sql_type == SQLType.UPDATE or sql_type == SQLType.DELETE:
            return """
请重点关注以下UPDATE/DELETE相关规范：
- 删改语句必须带where条件或使用limit物理分页，避免大事务
- 分区表的查询或修改必须带上分区键
- 对分区表执行DROP或TRUNCATE分区操作时，注意执行期间全局索引会失效
"""
        elif sql_type == SQLType.CREATE or sql_type == SQLType.ALTER:
            return """
请重点关注以下CREATE/ALTER相关规范：
- 表名和列名禁止大小写混用，禁止反闭包（backquote）
- 表名和列名只能使用字母、数字和下划线，必须以字母开头
- 表名禁止两个下划线中间只出现数字
- 定义表结构时，表或列须用comment属性加上注释
- 禁止使用生成列作为分区键
- 小数类型使用decimal存储，禁止使用double、float、varchar
- 表上强制添加创建时间和变更时间字段
- 禁止使用枚举数据类型
- 禁止使用定义为STORED类型且依赖其他列值计算的生成列
- 修改列名、列长度等属性时，须带上列的原属性值
- 禁止使用外键、临时表、存储过程以及触发器
- 禁止创建全文索引
- 唯一索引的所有字段须添加not null约束
- 字符集应设置为utf8mb4
"""
        else:
            return "请检查SQL语句是否符合所有相关规范。"
    
    def generate_prompt(self, sql_type: SQLType) -> str:
        """
        生成增强版规范提示词
        
        Args:
            sql_type: SQL类型
            
        Returns:
            增强版规范提示词
        """
        base_rules = self.base_rules
        relevant_rules = self._get_relevant_rules_by_type(sql_type)
        
        prompt = f"""
SQL规范检查要求：

请检查SQL语句是否符合相关规范。如果违反规范，请详细说明违反内容和改进建议；如果没有违反，请返回'不涉及'。

相关规范摘要：
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


def get_specifications_prompt(sql_type: SQLType) -> str:
    """
    获取SQL规范提示词
    
    Args:
        sql_type: SQL类型
        
    Returns:
        规范提示词
    """
    generator = SpecificationsPromptGenerator()
    return generator.generate_prompt(sql_type)


# 测试函数
def test_prompt_generator():
    """测试提示词生成器"""
    generator = SpecificationsPromptGenerator()
    
    print("=" * 60)
    print("测试SQL规范提示词生成器")
    print("=" * 60)
    
    # 测试SELECT语句提示词
    select_prompt = generator.generate_prompt(SQLType.SELECT)
    print(f"\nSELECT语句提示词长度: {len(select_prompt)}")
    print(f"前500字符: {select_prompt[:500]}...")
    
    # 测试INSERT语句提示词
    insert_prompt = generator.generate_prompt(SQLType.INSERT)
    print(f"\nINSERT语句提示词长度: {len(insert_prompt)}")
    print(f"前500字符: {insert_prompt[:500]}...")
    
    # 测试CREATE语句提示词
    create_prompt = generator.generate_prompt(SQLType.CREATE)
    print(f"\nCREATE语句提示词长度: {len(create_prompt)}")
    print(f"前500字符: {create_prompt[:500]}...")
    
    return True


if __name__ == "__main__":
    test_prompt_generator()
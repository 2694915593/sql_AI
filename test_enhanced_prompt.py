#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试增强版SQL规范提示词
"""

import json
import re
from typing import Dict, Any, Optional, List

class SQLType:
    """SQL类型枚举"""
    SELECT = "SELECT"
    INSERT = "INSERT"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    CREATE = "CREATE"
    ALTER = "ALTER"
    DROP = "DROP"
    TRUNCATE = "TRUNCATE"
    OTHER = "OTHER"

class RuleLevel:
    """规则级别"""
    MANDATORY = "mandatory"
    WARNING = "warning"
    SUGGESTION = "suggestion"

def get_enhanced_specifications_prompt(sql_type: SQLType) -> str:
    """
    获取增强版规范提示词
    
    Args:
        sql_type: SQL类型
        
    Returns:
        增强版规范提示词
    """
    # 基于用户提供的规范创建提示词
    base_rules = """
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
    
    # 根据SQL类型选择相关规则
    if sql_type == SQLType.SELECT:
        relevant_rules = """
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
        relevant_rules = """
请重点关注以下INSERT相关规范：
- INSERT时必须指定列
- INSERT ... ON DUPLICATE KEY UPDATE时，非空字段禁止传入null值
- INSERT INTO ... SELECT须确保SELECT结果集不超过大事务标准限制
- 禁止使用自增列作为分区键
- 自增列字段使用bigint类型存储，禁止使用int类型
"""
    elif sql_type == SQLType.UPDATE or sql_type == SQLType.DELETE:
        relevant_rules = """
请重点关注以下UPDATE/DELETE相关规范：
- 删改语句必须带where条件或使用limit物理分页，避免大事务
- 分区表的查询或修改必须带上分区键
- 对分区表执行DROP或TRUNCATE分区操作时，注意执行期间全局索引会失效
"""
    elif sql_type == SQLType.CREATE or sql_type == SQLType.ALTER:
        relevant_rules = """
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
        relevant_rules = "请检查SQL语句是否符合所有相关规范。"
    
    # 构建最终提示词
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

注意：请只回复JSON格式的内容，不要包含任何解释性文字。
"""
    
    return prompt

def test_prompt():
    """测试提示词生成"""
    print("测试SELECT语句提示词:")
    select_prompt = get_enhanced_specifications_prompt(SQLType.SELECT)
    print(select_prompt[:500] + "...")
    print("\n" + "="*80 + "\n")
    
    print("测试INSERT语句提示词:")
    insert_prompt = get_enhanced_specifications_prompt(SQLType.INSERT)
    print(insert_prompt[:500] + "...")
    print("\n" + "="*80 + "\n")
    
    print("测试CREATE语句提示词:")
    create_prompt = get_enhanced_specifications_prompt(SQLType.CREATE)
    print(create_prompt[:500] + "...")
    
    # 测试示例SQL
    test_sqls = [
        "SELECT * FROM users WHERE age > 18",
        "INSERT INTO users VALUES (1, 'John', 25)",
        "CREATE TABLE users (id INT, name VARCHAR(50))"
    ]
    
    for sql in test_sqls:
        print(f"\nSQL: {sql}")
        if sql.upper().startswith("SELECT"):
            prompt = get_enhanced_specifications_prompt(SQLType.SELECT)
        elif sql.upper().startswith("INSERT"):
            prompt = get_enhanced_specifications_prompt(SQLType.INSERT)
        elif sql.upper().startswith("CREATE"):
            prompt = get_enhanced_specifications_prompt(SQLType.CREATE)
        else:
            prompt = get_enhanced_specifications_prompt(SQLType.OTHER)
        
        print(f"提示词长度: {len(prompt)}")
        print(f"提示词前200字符: {prompt[:200]}...")

if __name__ == "__main__":
    test_prompt()
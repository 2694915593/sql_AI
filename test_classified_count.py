#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试分类版SQL规范数量验证
"""

from sql_ai_analyzer.utils.specifications_prompt_classified import ClassifiedSpecificationsPromptGenerator

def count_user_table_rules():
    """根据用户提供的表格手动统计"""
    # 用户表格中的规则，逐条统计
    categories = {
        "建表语句": 12,
        "查询语句": 10,
        "增删改语句": 4,
        "事务控制语句": 5,
        "序列语句": 4,
        "其他DDL语句": 2,
        "通用规范": 15
    }
    
    total = sum(categories.values())
    print("根据用户表格统计：")
    for category, count in categories.items():
        print(f"  {category}: {count}条")
    print(f"总规范条数: {total}条")
    print(f"缺少 {53-total} 条规范")
    
    return total

def check_missing_rules():
    """检查可能缺少的规则"""
    print("\n检查可能缺少的规范：")
    print("1. 检查用户提供的表格：")
    print("   SQL类别有：建表语句、查询语句、增删改语句、事务控制语句、序列语句、其他DDL语句、通用规范")
    print("2. 可能缺少的规范：")
    print("   - INSERT INTO ... SELECT 可能已在增删改语句中包含")
    print("   - 检查是否有重复或遗漏")
    
    # 实际统计
    from collections import Counter
    
    all_rules = [
        # 建表语句 (12条)
        ("建表语句", "表名和列名禁止大小写混用，禁止反闭包（backquote）表名和列名"),
        ("建表语句", "表名和列名只能使用字母、数字和下划线，必须以字母开头，不得使用系统保留字和特殊字符；表名禁止两个下划线中间只出现数字"),
        ("建表语句", "定义表结构时，表或列须用comment属性加上注释"),
        ("建表语句", "禁止使用生成列作为分区键"),
        ("建表语句", "小数类型使用decimal存储，禁止使用double、float、varchar"),
        ("建表语句", "表上强制添加创建时间（CREATE_TIME）和变更时间（UPDATE_TIME）字段，类型DATETIME(6)，并设置默认值及ON UPDATE属性"),
        ("建表语句", "禁止使用枚举数据类型"),
        ("建表语句", "禁止使用定义为STORED类型且依赖其他列值计算的生成列"),
        ("建表语句", "自增列字段使用bigint类型存储，禁止使用int类型"),
        ("建表语句", "禁止使用自增列作为分区键"),
        ("建表语句", "修改列名、列长度等属性时，须带上列的原属性值，以避免定义被覆盖"),
        ("建表语句", "对分区表执行DROP或TRUNCATE分区操作时，注意执行期间全局索引会失效"),
        
        # 查询语句 (10条)
        ("查询语句", "当字段类型为字符串时，禁止直接对该字段数据进行数值函数计算"),
        ("查询语句", "联机TP交易SQL语句运行时必须使用对应的索引"),
        ("查询语句", "通用表达式CTE recursive递归行数禁止超过1000"),
        ("查询语句", "禁用get_format函数"),
        ("查询语句", "SELECT语句必须指定具体字段名称，禁止写成'select *'"),
        ("查询语句", "禁止大表查询使用全表扫描"),
        ("查询语句", "非主键/非唯一键查询或关联查询，应使用物理分页（limit），避免大结果集"),
        ("查询语句", "查询结果需要有序时，须添加order by，且排序字段必须唯一或组合唯一（非空）"),
        ("查询语句", "多表关联必须有关联条件，禁止出现笛卡尔积"),
        ("查询语句", "子查询内SELECT列表字段禁止引用外表"),
        
        # 增删改语句 (4条)
        ("增删改语句", "删改语句必须带where条件或使用limit物理分页，避免大事务"),
        ("增删改语句", "INSERT时必须指定列"),
        ("增删改语句", "INSERT ... ON DUPLICATE KEY UPDATE时，非空字段禁止传入null值"),
        ("增删改语句", "INSERT INTO ... SELECT须确保SELECT结果集不超过大事务标准限制"),
        
        # 事务控制语句 (5条)
        ("事务控制语句", "禁止设置timezone、SQL_mode和isolation_level变量"),
        ("事务控制语句", "事务隔离级别应使用默认的RC读已提交"),
        ("事务控制语句", "禁止事务内第一条查询为特定写法（如select '1'；select * from t1;等）"),
        ("事务控制语句", "禁止创建全文索引"),
        ("事务控制语句", "唯一索引的所有字段须添加not null约束"),
        
        # 序列语句 (4条)
        ("序列语句", "创建序列必须指定cache大小，cache值=租户TPS*60*60*24/100"),
        ("序列语句", "序列禁止添加order属性"),
        ("序列语句", "序列字段使用bigint类型存储，禁止使用int类型"),
        ("序列语句", "noorder选项的序列不保证全局单调递增，值可能跳变"),
        
        # 其他DDL语句 (2条)
        ("其他DDL语句", "数据库名：子系统标识(4位)+应用模块名(最多4位，可选)+db，例如gabsdb"),
        ("其他DDL语句", "禁止使用optimize table语法"),
        
        # 通用规范 (15条)
        ("通用规范", "字符集应设置为utf8mb4，根据业务场景选择字符序：推荐utf8mb4_bin（大小写敏感）或utf8mb4_general_ci（不区分大小写）"),
        ("通用规范", "字符集/字符序逐级继承，若显式指定必须保证表、列与数据库一致，设置后不可修改"),
        ("通用规范", "普通租户名：小写32字符，t+应用标识(4位)+环境标识(3位)+租户编号(XX)，如tecifsit00"),
        ("通用规范", "单元化租户名：小写32字符，t+应用标识(4位)+环境标识(3位)+ZONE类型(G/C/R)+租户编号(XX)"),
        ("通用规范", "单分区数据量安全水位线2TB，超过1TB需及时清理"),
        ("通用规范", "分区表的查询或修改必须带上分区键"),
        ("通用规范", "禁止使用外键、临时表、存储过程以及触发器"),
        ("通用规范", "SQL单行注释以--开头，符号后必须加空格再写注释内容"),
        ("通用规范", "SQL语句中禁止使用数据库保留字"),
        ("通用规范", "使用SOFA-ODP组件时，SQL谓词中禁用反单引号修饰分区键"),
        ("通用规范", "case when表达式应控制在150个以内"),
        ("通用规范", "CASE WHEN语句必须显式定义ELSE分支并明确返回值"),
        ("通用规范", "DDL操作后需等待至少3秒并检查确认后再执行DML，重试三次若失败需人工处置"),
        ("通用规范", "使用if(expr1, expr2, expr3)函数时，expr1不能为字符类型"),
        ("通用规范", "SQL Hint必须经过验证确保其有效性")
    ]
    
    # 统计每个类别的规则数量
    category_counts = Counter()
    for category, rule in all_rules:
        category_counts[category] += 1
    
    print("\n实际统计结果：")
    for category, count in category_counts.most_common():
        print(f"  {category}: {count}条")
    
    total = sum(category_counts.values())
    print(f"\n总规范条数: {total}条")
    
    return total

def main():
    print("=" * 60)
    print("分类版SQL规范数量验证")
    print("=" * 60)
    
    # 方法1: 使用分类生成器
    print("\n1. 使用ClassifiedSpecificationsPromptGenerator统计：")
    generator = ClassifiedSpecificationsPromptGenerator()
    counts = generator.get_rule_count()
    total1 = sum(counts.values())
    for category, count in counts.items():
        print(f"  {category}: {count}条")
    print(f"总规范条数: {total1}条")
    
    # 方法2: 手动统计
    total2 = check_missing_rules()
    
    print("\n" + "=" * 60)
    print("验证结果：")
    print(f"当前实现: {total1}条规范")
    print(f"预期目标: 53条规范")
    print(f"缺少: {53 - total1}条规范")
    
    if total1 == total2:
        print("✓ 两种统计方法结果一致")
    else:
        print(f"⚠ 统计不一致: 生成器{total1}条 vs 手动{total2}条")
    
    # 检查是否有规范遗漏
    if total1 < 53:
        print(f"\n需要找到缺少的 {53-total1} 条规范")
        print("可能遗漏的规范：")
        print("1. 检查用户表格中的'其他DDL语句'，可能还有更多条目")
        print("2. 检查是否有规范被拆分成了多条")
        print("3. 检查是否有规范被遗漏")

if __name__ == "__main__":
    main()
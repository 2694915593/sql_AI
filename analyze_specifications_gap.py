#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析规范差距：比较用户提供的规范列表与现有规范
"""

from sql_ai_analyzer.utils.sql_specifications import SQLSpecificationsManager, SQLType

def get_user_specifications_list():
    """从用户任务描述中提取的规范列表"""
    return [
        # 命名规范
        "表名和列名禁止大小写混用，禁止反闭包（backquote）表名和列名。",
        "表名和列名只能使用字母、数字和下划线，必须以字母开头，不得使用系统保留字和特殊字符；表名禁止两个下划线中间只出现数字。",
        
        # 注释规范
        "定义表结构时，表或列须用comment属性加上注释。",
        
        # 分区规范
        "禁止使用生成列作为分区键。",
        
        # 数据类型规范
        "小数类型使用decimal存储，禁止使用double、float、varchar。",
        "表上强制添加创建时间（CREATE_TIME）和变更时间（UPDATE_TIME）字段，类型DATETIME(6)，并设置默认值及ON UPDATE属性。",
        "禁止使用枚举数据类型。",
        "禁止使用定义为STORED类型且依赖其他列值计算的生成列。",
        "自增列字段使用bigint类型存储，禁止使用int类型。",
        "禁止使用自增列作为分区键。",
        
        # 修改规范
        "修改列名、列长度等属性时，须带上列的原属性值，以避免定义被覆盖。",
        
        # 分区操作规范
        "对分区表执行DROP或TRUNCATE分区操作时，注意执行期间全局索引会失效。",
        
        # 字符串操作规范
        "当字段类型为字符串时，禁止直接对该字段数据进行数值函数计算。",
        
        # 索引规范
        "联机TP交易SQL语句运行时必须使用对应的索引。",
        
        # CTE规范
        "通用表达式CTE recursive递归行数禁止超过1000。",
        
        # 函数规范
        "禁用get_format函数。",
        
        # SELECT规范
        "SELECT语句必须指定具体字段名称，禁止写成'select *'。",
        "禁止大表查询使用全表扫描。",
        "非主键/非唯一键查询或关联查询，应使用物理分页（limit），避免大结果集。",
        "查询结果需要有序时，须添加order by，且排序字段必须唯一或组合唯一（非空）。",
        
        # 关联查询规范
        "多表关联必须有关联条件，禁止出现笛卡尔积。",
        "子查询内SELECT列表字段禁止引用外表。",
        
        # DML规范
        "删改语句必须带where条件或使用limit物理分页，避免大事务。",
        "INSERT时必须指定列。",
        "INSERT ... ON DUPLICATE KEY UPDATE时，非空字段禁止传入null值。",
        "INSERT INTO ... SELECT须确保SELECT结果集不超过大事务标准限制。",
        
        # 变量规范
        "禁止设置timezone、SQL_mode和isolation_level变量。",
        "事务隔离级别应使用默认的RC读已提交。",
        "禁止事务内第一条查询为特定写法（如select '1'；select * from t1;等）。",
        
        # 索引规范
        "禁止创建全文索引。",
        "唯一索引的所有字段须添加not null约束。",
        
        # 序列规范
        "创建序列必须指定cache大小，cache值=租户TPS*60*60*24/100。",
        "序列禁止添加order属性。",
        "序列字段使用bigint类型存储，禁止使用int类型。",
        "noorder选项的序列不保证全局单调递增，值可能跳变。",
        
        # 数据库命名规范
        "数据库名：子系统标识(4位)+应用模块名(最多4位，可选)+db，例如gabsdb。",
        
        # 表优化规范
        "禁止使用optimize table语法。",
        
        # 字符集规范
        "字符集应设置为utf8mb4，根据业务场景选择字符序：推荐utf8mb4_bin（大小写敏感）或utf8mb4_general_ci（不区分大小写）。",
        "字符集/字符序逐级继承，若显式指定必须保证表、列与数据库一致，设置后不可修改。",
        
        # 租户命名规范
        "普通租户名：小写32字符，t+应用标识(4位)+环境标识(3位)+租户编号(XX)，如tecifsit00。",
        "单元化租户名：小写32字符，t+应用标识(4位)+环境标识(3位)+ZONE类型(G/C/R)+租户编号(XX)。",
        
        # 分区数据量规范
        "单分区数据量安全水位线2TB，超过1TB需及时清理。",
        
        # 分区表规范
        "分区表的查询或修改必须带上分区键。",
        
        # 禁用功能规范
        "禁止使用外键、临时表、存储过程以及触发器。",
        
        # 注释规范
        "SQL单行注释以--开头，符号后必须加空格再写注释内容。",
        
        # 保留字规范
        "SQL语句中禁止使用数据库保留字。",
        
        # SOFA-ODP规范
        "使用SOFA-ODP组件时，SQL谓词中禁用反单引号修饰分区键。",
        
        # CASE WHEN规范
        "case when表达式应控制在150个以内。",
        "CASE WHEN语句必须显式定义ELSE分支并明确返回值。",
        
        # DDL操作规范
        "DDL操作后需等待至少3秒并检查确认后再执行DML，重试三次若失败需人工处置。",
        
        # IF函数规范
        "使用if(expr1, expr2, expr3)函数时，expr1不能为字符类型。",
        
        # SQL Hint规范
        "SQL Hint必须经过验证确保其有效性。",
    ]

def analyze_specifications_gap():
    """分析规范差距"""
    manager = SQLSpecificationsManager()
    
    # 获取现有规范
    existing_categories = manager.get_all_categories()
    existing_rules = []
    
    for category in existing_categories:
        cat_data = manager.get_specifications_by_category(category)
        for rule in cat_data.get('rules', []):
            existing_rules.append({
                'id': rule['id'],
                'description': rule['description'],
                'content': rule['content'][:100] + '...' if len(rule['content']) > 100 else rule['content']
            })
    
    # 用户规范列表
    user_specs = get_user_specifications_list()
    
    print("=" * 80)
    print("规范差距分析报告")
    print("=" * 80)
    
    print(f"\n1. 现有规范统计:")
    print(f"   - 分类数: {len(existing_categories)}")
    print(f"   - 规则数: {len(existing_rules)}")
    
    print(f"\n2. 用户规范统计:")
    print(f"   - 规范条目数: {len(user_specs)}")
    
    print(f"\n3. 现有规范详情:")
    for i, cat in enumerate(existing_categories, 1):
        cat_data = manager.get_specifications_by_category(cat)
        rule_count = len(cat_data.get('rules', []))
        print(f"   {i}. {cat}: {rule_count}条规则")
    
    print(f"\n4. 关键规范覆盖情况检查:")
    
    # 检查关键规范是否已覆盖
    key_specs_to_check = [
        "SELECT语句必须指定具体字段名称，禁止写成'select *'",
        "表名和列名禁止大小写混用",
        "禁止使用外键、临时表、存储过程以及触发器",
        "小数类型使用decimal存储，禁止使用double、float、varchar",
        "禁止大表查询使用全表扫描",
        "多表关联必须有关联条件，禁止出现笛卡尔积",
        "删改语句必须带where条件或使用limit物理分页",
    ]
    
    for spec in key_specs_to_check:
        covered = False
        for rule in existing_rules:
            if spec[:30] in rule['content']:
                covered = True
                break
        status = "✅ 已覆盖" if covered else "❌ 未覆盖"
        print(f"   - {spec[:40]}... {status}")
    
    print(f"\n5. 建议:")
    print(f"   - 需要补充的规范条目数: 约{max(0, len(user_specs) - len(existing_rules))}条")
    print(f"   - 建议按用户提供的完整规范列表进行补充")
    print(f"   - 特别关注DML操作规范、分区表规范、序列规范等")
    
    return existing_rules, user_specs

if __name__ == "__main__":
    existing_rules, user_specs = analyze_specifications_gap()
    
    # 输出详细对比
    print(f"\n" + "=" * 80)
    print("详细规范对比")
    print("=" * 80)
    
    print(f"\n用户规范列表 (前20条):")
    for i, spec in enumerate(user_specs[:20], 1):
        print(f"{i:2d}. {spec[:60]}...")
    
    print(f"\n现有规范列表 (前20条):")
    for i, rule in enumerate(existing_rules[:20], 1):
        print(f"{i:2d}. [{rule['id']}] {rule['description']}: {rule['content'][:40]}...")
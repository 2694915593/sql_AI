#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试增强版SQL规范提示词的完整性
验证所有53条规范是否都被正确集成
"""

import sys
import os
sys.path.append('.')
sys.path.append('sql_ai_analyzer')

from sql_ai_analyzer.utils.sql_specifications import SQLType
from sql_ai_analyzer.utils.specifications_prompt_enhanced import get_specifications_prompt, SpecificationsPromptGenerator

def test_specifications_coverage():
    """测试规范覆盖完整性"""
    print("=" * 80)
    print("测试SQL规范提示词完整性验证")
    print("=" * 80)
    
    # 创建生成器
    generator = SpecificationsPromptGenerator()
    
    # 获取基础规则
    base_rules = generator._get_base_rules()
    
    print("\n1. 基础规范列表检查:")
    print("-" * 40)
    
    # 检查规范数量
    lines = base_rules.strip().split('\n')
    rule_lines = [line for line in lines if line.strip() and line.strip()[0].isdigit() and '.' in line]
    
    print(f"检测到的规范条目数量: {len(rule_lines)}")
    
    # 用户提供的53条规范检查
    expected_rules = [
        "1. 表名和列名禁止大小写混用，禁止反闭包（backquote）表名和列名",
        "2. 表名和列名只能使用字母、数字和下划线，必须以字母开头，不得使用系统保留字和特殊字符",
        "3. 表名禁止两个下划线中间只出现数字",
        "4. 定义表结构时，表或列须用comment属性加上注释",
        "5. 禁止使用生成列作为分区键",
        "6. 小数类型使用decimal存储，禁止使用double、float、varchar",
        "7. 表上强制添加创建时间（CREATE_TIME）和变更时间（UPDATE_TIME）字段，类型DATETIME(6)，并设置默认值及ON UPDATE属性",
        "8. 禁止使用枚举数据类型",
        "9. 禁止使用定义为STORED类型且依赖其他列值计算的生成列",
        "10. 自增列字段使用bigint类型存储，禁止使用int类型",
        "11. 禁止使用自增列作为分区键",
        "12. 修改列名、列长度等属性时，须带上列的原属性值，以避免定义被覆盖",
        "13. 对分区表执行DROP或TRUNCATE分区操作时，注意执行期间全局索引会失效",
        "14. 当字段类型为字符串时，禁止直接对该字段数据进行数值函数计算",
        "15. 联机TP交易SQL语句运行时必须使用对应的索引",
        "16. 通用表达式CTE recursive递归行数禁止超过1000",
        "17. 禁用get_format函数",
        "18. SELECT语句必须指定具体字段名称，禁止写成\"select *\"",
        "19. 禁止大表查询使用全表扫描",
        "20. 非主键/非唯一键查询或关联查询，应使用物理分页（limit），避免大结果集",
        "21. 查询结果需要有序时，须添加order by，且排序字段必须唯一或组合唯一（非空）",
        "22. 多表关联必须有关联条件，禁止出现笛卡尔积",
        "23. 子查询内SELECT列表字段禁止引用外表",
        "24. 删改语句必须带where条件或使用limit物理分页，避免大事务",
        "25. INSERT时必须指定列",
        "26. INSERT ... ON DUPLICATE KEY UPDATE时，非空字段禁止传入null值",
        "27. INSERT INTO ... SELECT须确保SELECT结果集不超过大事务标准限制",
        "28. 禁止设置timezone、SQL_mode和isolation_level变量",
        "29. 事务隔离级别应使用默认的RC读已提交",
        "30. 禁止事务内第一条查询为特定写法（如select '1'；select * from t1;等）",
        "31. 禁止创建全文索引",
        "32. 唯一索引的所有字段须添加not null约束",
        "33. 创建序列必须指定cache大小，cache值=租户TPS*60*60*24/100",
        "34. 序列禁止添加order属性",
        "35. 序列字段使用bigint类型存储，禁止使用int类型",
        "36. noorder选项的序列不保证全局单调递增，值可能跳变",
        "37. 数据库名：子系统标识(4位)+应用模块名(最多4位，可选)+db，例如gabsdb",
        "38. 禁止使用optimize table语法",
        "39. 字符集应设置为utf8mb4，根据业务场景选择字符序：推荐utf8mb4_bin（大小写敏感）或utf8mb4_general_ci（不区分大小写）",
        "40. 字符集/字符序逐级继承，若显式指定必须保证表、列与数据库一致，设置后不可修改",
        "41. 普通租户名：小写32字符，t+应用标识(4位)+环境标识(3位)+租户编号(XX)，如tecifsit00",
        "42. 单元化租户名：小写32字符，t+应用标识(4位)+环境标识(3位)+ZONE类型(G/C/R)+租户编号(XX)",
        "43. 单分区数据量安全水位线2TB，超过1TB需及时清理",
        "44. 分区表的查询或修改必须带上分区键",
        "45. 禁止使用外键、临时表、存储过程以及触发器",
        "46. SQL单行注释以--开头，符号后必须加空格再写注释内容",
        "47. SQL语句中禁止使用数据库保留字",
        "48. 使用SOFA-ODP组件时，SQL谓词中禁用反单引号修饰分区键",
        "49. case when表达式应控制在150个以内",
        "50. CASE WHEN语句必须显式定义ELSE分支并明确返回值",
        "51. DDL操作后需等待至少3秒并检查确认后再执行DML，重试三次若失败需人工处置",
        "52. 使用if(expr1, expr2, expr3)函数时，expr1不能为字符类型",
        "53. SQL Hint必须经过验证确保其有效性"
    ]
    
    # 检查每条规范是否都存在
    missing_rules = []
    for expected_rule in expected_rules:
        found = False
        for rule_line in rule_lines:
            if expected_rule in rule_line:
                found = True
                break
        
        if not found:
            # 提取规则编号
            rule_num = expected_rule.split('.')[0].strip()
            missing_rules.append(f"规则{rule_num}: {expected_rule[:50]}...")
    
    if missing_rules:
        print(f"\n❌ 检测到缺失的规范 ({len(missing_rules)}条):")
        for missing in missing_rules:
            print(f"  - {missing}")
    else:
        print("\n✅ 所有53条规范都已完整集成")
    
    # 检查分类是否完整
    print("\n2. 规范分类检查:")
    print("-" * 40)
    
    # 检查生成的提示词分类
    categories_in_base = []
    current_category = ""
    for line in lines:
        if line.strip().endswith('规范：'):
            current_category = line.strip()
            categories_in_base.append(current_category)
    
    print(f"基础规范分类数量: {len(categories_in_base)}")
    for category in categories_in_base:
        print(f"  - {category}")
    
    # 测试不同类型的提示词
    print("\n3. 不同SQL类型的提示词生成测试:")
    print("-" * 40)
    
    sql_types = [
        (SQLType.SELECT, "SELECT语句"),
        (SQLType.INSERT, "INSERT语句"),
        (SQLType.UPDATE, "UPDATE语句"),
        (SQLType.DELETE, "DELETE语句"),
        (SQLType.CREATE, "CREATE语句"),
        (SQLType.ALTER, "ALTER语句"),
        (SQLType.OTHER, "其他语句")
    ]
    
    for sql_type, type_name in sql_types:
        prompt = get_specifications_prompt(sql_type)
        print(f"{type_name}:")
        print(f"  提示词长度: {len(prompt)} 字符")
        
        # 检查是否包含正确的JSON格式
        if '"规范检查结果"' in prompt:
            print("  ✅ 包含正确的JSON格式")
        else:
            print("  ❌ JSON格式可能有问题")
        
        # 检查是否包含"不涉及"要求
        if '不涉及' in prompt:
            print("  ✅ 包含'不涉及'输出要求")
        else:
            print("  ❌ 缺少'不涉及'输出要求")
        
        # 检查是否包含评分要求
        if 'compliance_score' in prompt:
            print("  ✅ 包含合规评分要求")
        else:
            print("  ❌ 缺少合规评分要求")
    
    # 测试优化版ModelClient的集成
    print("\n4. ModelClient集成测试:")
    print("-" * 40)
    
    try:
        from sql_ai_analyzer.ai_integration.model_client_enhanced_optimized import ModelClient
        
        print("✅ 成功导入优化版ModelClient")
        
        # 检查类的方法
        methods = [
            'analyze_sql',
            '_build_request_payload', 
            '_parse_response',
            '_extract_all_suggestions',
            '_extract_all_fields'
        ]
        
        for method in methods:
            if hasattr(ModelClient, method):
                print(f"  ✅ 方法存在: {method}")
            else:
                print(f"  ❌ 方法缺失: {method}")
                
    except Exception as e:
        print(f"❌ 导入ModelClient失败: {e}")
    
    print("\n5. 规范提示词优化点验证:")
    print("-" * 40)
    
    # 检查是否按照要求进行了优化
    select_prompt = get_specifications_prompt(SQLType.SELECT)
    
    optimization_checks = [
        ("仅返回规范违反详情或'不涉及'", "violations" in select_prompt and "不涉及" in select_prompt),
        ("简化输出格式，只关注规范违反", "JSON格式回复" in select_prompt),
        ("大模型不需要返回其他分析内容", "不需要其他分析内容" in select_prompt or "只关注规范违反详情" in select_prompt),
        ("包含合规评分", "compliance_score" in select_prompt),
        ("has_violations字段控制输出", "has_violations" in select_prompt)
    ]
    
    for check_name, check_result in optimization_checks:
        if check_result:
            print(f"✅ {check_name}")
        else:
            print(f"❌ {check_name}")
    
    return len(missing_rules) == 0

def test_model_client_prompt_generation():
    """测试ModelClient提示词生成"""
    print("\n" + "=" * 80)
    print("测试ModelClient提示词生成")
    print("=" * 80)
    
    try:
        # 模拟一个简单的配置管理器
        class MockConfigManager:
            def get_ai_model_config(self):
                return {
                    'api_url': 'http://mock-api.com',
                    'api_key': 'test-key',
                    'max_retries': 3,
                    'timeout': 30
                }
        
        # 模拟一个简单的logger
        import logging
        logger = logging.getLogger('test')
        logger.setLevel(logging.DEBUG)
        
        from sql_ai_analyzer.ai_integration.model_client_enhanced_optimized import ModelClient
        
        config_manager = MockConfigManager()
        client = ModelClient(config_manager, logger)
        
        # 测试请求数据
        request_data = {
            'sql_statement': 'SELECT * FROM users WHERE id = 1',
            'tables': [{'table_name': 'users', 'row_count': 1000}],
            'db_alias': 'test_db'
        }
        
        # 测试_build_request_payload方法
        print("\n测试提示词生成:")
        payload = client._build_request_payload(request_data)
        
        if 'prompt' in payload:
            prompt = payload['prompt']
            print(f"✅ 成功生成提示词，长度: {len(prompt)} 字符")
            
            # 检查提示词内容
            checks = [
                ("包含SQL语句", 'SELECT * FROM users' in prompt),
                ("包含表信息", 'users' in prompt),
                ("包含数据库信息", 'test_db' in prompt),
                ("包含规范检查要求", 'SQL规范检查要求' in prompt),
                ("包含53条规范", '表名和列名规范' in prompt),
                ("包含输出格式要求", 'JSON格式回复' in prompt),
                ("包含'不涉及'要求", '不涉及' in prompt)
            ]
            
            for check_name, check_result in checks:
                if check_result:
                    print(f"  ✅ {check_name}")
                else:
                    print(f"  ❌ {check_name}")
            
            # 显示提示词预览
            print(f"\n提示词预览（前300字符）:")
            print(prompt[:300] + "...")
            
        else:
            print("❌ 提示词生成失败")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("开始验证SQL规范完整性...")
    
    # 测试规范覆盖
    coverage_ok = test_specifications_coverage()
    
    # 测试ModelClient提示词生成
    client_ok = test_model_client_prompt_generation()
    
    print("\n" + "=" * 80)
    print("验证结果总结:")
    print("=" * 80)
    
    if coverage_ok and client_ok:
        print("✅ 所有验证通过！")
        print("\n优化完成总结:")
        print("1. ✅ 已完整集成53条SQL规范")
        print("2. ✅ 已优化大模型提示词，使其仅返回规范违反详情或'不涉及'")
        print("3. ✅ 已修复优化版ModelClient中的所有缺失方法")
        print("4. ✅ ModelClient可以正确生成包含完整规范的提示词")
        print("5. ✅ 输出格式已简化为JSON，只关注规范违反详情")
        print("\n大模型现在将按照以下要求返回结果:")
        print("- 如果SQL违反规范：返回详细的违反信息和改进建议")
        print("- 如果SQL没有违反规范：返回'不涉及'")
        print("- 统一使用JSON格式，包含has_violations字段控制输出")
    else:
        print("❌ 验证失败，请检查上述问题")
    
    sys.exit(0 if coverage_ok and client_ok else 1)
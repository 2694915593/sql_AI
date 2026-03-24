#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
解释动态SQL生成和SQL执行计划生成的实现原理
"""

def explain_dynamic_sql_generation():
    """解释动态SQL生成原理"""
    print("动态SQL生成实现原理")
    print("=" * 80)
    
    print("\n1. 动态SQL的概念：")
    print("   动态SQL是指在运行时根据用户输入或程序逻辑动态构建的SQL语句。")
    print("   在SQL注入分析中，我们需要生成各种可能的动态SQL示例，用于判断是否存在注入风险。")
    
    print("\n2. 实现目标：")
    print("   • 使用用户真实上传的数据（表名、字段名）")
    print("   • 生成多种类型的动态SQL示例")
    print("   • 展示SQL注入的常见模式")
    print("   • 提供防护建议")
    
    print("\n3. 实现步骤：")
    print("   步骤1: 提取真实表名和字段名")
    print("     - 从用户上传的SQL语句中提取表名")
    print("     - 从收集的元数据中获取表的真实字段名")
    print("     - 如果没有真实字段，使用通用字段名")
    
    print("\n   步骤2: 根据SQL类型生成动态SQL示例")
    print("     - SELECT语句: 生成查询相关的动态SQL")
    print("     - INSERT语句: 生成插入相关的动态SQL")
    print("     - UPDATE语句: 生成更新相关的动态SQL")
    print("     - DELETE语句: 生成删除相关的动态SQL")
    
    print("\n   步骤3: 生成通用SQL注入示例")
    print("     - 字符串拼接注入")
    print("     - 数字类型注入")
    print("     - 时间类型注入")
    print("     - 布尔盲注")
    print("     - 时间盲注")
    print("     - 报错注入")
    
    print("\n4. 代码实现（model_client.py中的_generate_dynamic_sql_examples方法）：")
    print("""
    def _generate_dynamic_sql_examples(self, sql_statement: str, tables: List[Dict[str, Any]] = None) -> List[str]:
        \"\"\"生成动态SQL示例用于判断SQL注入漏洞，使用用户真实数据\"\"\"\"
        
        # 1. 提取真实表名和字段名
        if tables and len(tables) > 0:
            first_table = tables[0]
            real_table_name = first_table.get('table_name', '')
            
            # 提取真实字段名
            columns = first_table.get('columns', [])
            for col in columns:
                col_name = col.get('name', '')
                if col_name and col_name not in real_columns:
                    real_columns.append(col_name)
        
        # 2. 根据SQL类型生成示例
        if sql_lower.startswith('select'):
            # SELECT语句的动态SQL示例
            examples.append(f"动态查询示例：SELECT * FROM {table_name} WHERE {column2} = '" + "${user_input}" + "'")
            examples.append(f"参数化查询示例：SELECT * FROM {table_name} WHERE {column2} = ?")
        
        elif sql_lower.startswith('insert'):
            # INSERT语句的动态SQL示例
            examples.append(f"动态插入示例：INSERT INTO {table_name} ({column1}, {column2}) VALUES ('" + "${value1}" + "', '" + "${value2}" + "')")
        
        # 3. 生成通用注入示例
        examples.append(f"字符串拼接示例：SELECT * FROM {table_name} WHERE {column2} LIKE '%" + "${search_term}" + "%'")
        examples.append(f"数字类型注入示例：SELECT * FROM {table_name} WHERE {column1} = " + "${id}")
        
        # 4. 添加防护建议
        examples.append("\\n防护建议：")
        examples.append("1. 使用参数化查询（Prepared Statements）")
        examples.append("2. 使用存储过程")
        examples.append("3. 输入验证和过滤")
        examples.append("4. 最小权限原则")
        examples.append("5. 使用ORM框架")
    """)
    
    print("\n5. 示例输出：")
    print("   对于表 pd_errcode，字段 PEC_ERRCODE, PEC_LANGUAGE，生成的动态SQL示例：")
    print("   - 动态查询示例：SELECT * FROM pd_errcode WHERE PEC_LANGUAGE = '${user_input}'")
    print("   - 参数化查询示例：SELECT * FROM pd_errcode WHERE PEC_LANGUAGE = ?")
    print("   - 字符串拼接示例：SELECT * FROM pd_errcode WHERE PEC_LANGUAGE LIKE '%${search_term}%'")
    print("   - 数字类型注入示例：SELECT * FROM pd_errcode WHERE PEC_ERRCODE = ${id}")
    
    print("\n6. 优势：")
    print("   • 使用真实数据：基于用户实际使用的表名和字段名")
    print("   • 针对性强：根据SQL类型生成相关示例")
    print("   • 全面覆盖：包含各种SQL注入类型")
    print("   • 实用性强：提供具体的防护建议")

def explain_execution_plan_generation():
    """解释SQL执行计划生成原理"""
    print("\n\nSQL执行计划生成实现原理")
    print("=" * 80)
    
    print("\n1. SQL执行计划的概念：")
    print("   SQL执行计划是数据库优化器为执行SQL语句选择的执行路径。")
    print("   它描述了数据库如何访问数据、使用索引、连接表等。")
    
    print("\n2. 实现目标：")
    print("   • 基于元数据生成执行计划分析")
    print("   • 预测SQL执行性能")
    print("   • 识别潜在的性能问题")
    print("   • 提供优化建议")
    
    print("\n3. 实现步骤：")
    print("   步骤1: 分析SQL类型")
    print("     - 识别是SELECT、INSERT、UPDATE还是DELETE")
    print("     - 分析SQL的操作类型（查询、插入、更新、删除）")
    
    print("\n   步骤2: 分析表信息")
    print("     - 表的数据量（行数）")
    print("     - 是否为大表（>10万行）")
    print("     - 表的列数")
    print("     - 表的索引信息")
    
    print("\n   步骤3: 生成执行计划预测")
    print("     - 基于SQL类型预测执行方式")
    print("     - 基于表大小预测扫描方式")
    print("     - 基于索引预测访问路径")
    
    print("\n   步骤4: 生成性能优化建议")
    print("     - 索引优化建议")
    print("     - 查询优化建议")
    print("     - 结构优化建议")
    
    print("\n   步骤5: 风险评估")
    print("     - 识别高风险操作")
    print("     - 评估执行风险")
    
    print("\n4. 代码实现（model_client.py中的_generate_execution_plan方法）：")
    print("""
    def _generate_execution_plan(self, sql_statement: str, tables: List[Dict[str, Any]]) -> str:
        \"\"\"生成SQL执行计划分析\"\"\"
        
        # 1. SQL类型分析
        if sql_lower.startswith('select'):
            plan_parts.append("   • 类型：查询语句 (SELECT)")
            plan_parts.append("   • 操作：数据读取")
            plan_parts.append("   • 性能关注点：查询优化、索引使用")
        
        # 2. 表信息分析
        for table in tables:
            table_name = table.get('table_name', '未知表')
            row_count = table.get('row_count', 0)
            is_large_table = table.get('is_large_table', False)
            
            plan_parts.append(f"   表{i}：{table_name}")
            plan_parts.append(f"     • 数据量：{row_count} 行")
            plan_parts.append(f"     • 是否大表：{'是' if is_large_table else '否'}")
            
            # 索引分析
            indexes = table.get('indexes', [])
            if indexes:
                plan_parts.append(f"     • 索引详情：")
            else:
                plan_parts.append(f"     • 索引：无索引（全表扫描风险）")
        
        # 3. 执行计划预测
        if sql_lower.startswith('select'):
            if tables and any(table.get('indexes') for table in tables):
                plan_parts.append("   • 预测：可能使用索引扫描")
                plan_parts.append("   • 建议：检查WHERE条件是否匹配索引")
            else:
                plan_parts.append("   • 预测：可能进行全表扫描")
                plan_parts.append("   • 建议：考虑添加合适的索引")
        
        # 4. 性能优化建议
        plan_parts.append("   • 确保WHERE条件使用索引")
        plan_parts.append("   • 避免SELECT *，只选择需要的列")
        plan_parts.append("   • 考虑查询结果集大小")
        
        # 5. 风险评估
        if sql_lower.startswith('delete') and 'where' not in sql_lower:
            plan_parts.append("   • ⚠️ 风险：无WHERE条件的DELETE语句（可能删除全表数据）")
    """)
    
    print("\n5. 示例输出：")
    print("   对于SQL: SELECT * FROM pd_errcode WHERE PEC_LANGUAGE = 'zh_CN'")
    print("   表信息: pd_errcode (212行，无索引)")
    print("   生成的执行计划分析：")
    print("   SQL执行计划分析：")
    print("   ==================================================")
    print("   1. SQL类型分析：")
    print("      • 类型：查询语句 (SELECT)")
    print("      • 操作：数据读取")
    print("      • 性能关注点：查询优化、索引使用")
    print("   2. 涉及表分析：")
    print("      表1：pd_errcode")
    print("        • 数据量：212 行")
    print("        • 是否大表：否")
    print("        • 列数：6")
    print("        • 索引数：0")
    print("        • 索引：无索引（全表扫描风险）")
    print("   3. 执行计划预测：")
    print("      • 预测：可能进行全表扫描")
    print("      • 建议：考虑添加合适的索引")
    print("   4. 性能优化建议：")
    print("      • 确保WHERE条件使用索引")
    print("      • 避免SELECT *，只选择需要的列")
    print("      • 考虑查询结果集大小")
    print("   5. 执行风险评估：")
    print("      • ✅ 风险较低")
    
    print("\n6. 优势：")
    print("   • 基于元数据：使用实际的表大小、索引信息")
    print("   • 预测准确：基于SQL类型和表特征进行合理预测")
    print("   • 实用性强：提供具体的优化建议")
    print("   • 风险识别：提前识别潜在的执行风险")

def explain_complete_workflow():
    """解释完整的工作流程"""
    print("\n\n完整的工作流程")
    print("=" * 80)
    
    print("\n1. 数据收集阶段：")
    print("   • 从am_solline_info表读取待分析SQL")
    print("   • 提取SQL中的表名")
    print("   • 连接目标数据库收集表元数据")
    print("   • 收集DDL、行数、索引、列信息")
    
    print("\n2. 分析准备阶段：")
    print("   • 构建请求数据：SQL语句、表信息、数据库别名")
    print("   • 生成动态SQL示例（使用真实表名和字段名）")
    print("   • 生成执行计划分析（基于元数据）")
    
    print("\n3. 大模型分析阶段：")
    print("   • 构建完整的prompt，包含：")
    print("     1. SQL语句")
    print("     2. 数据库信息")
    print("     3. 表信息（包括DDL）")
    print("     4. 动态SQL示例")
    print("     5. SQL执行计划分析")
    print("     6. SQL评审规则")
    print("     7. 分析要求")
    print("     8. 输出格式要求")
    print("   • 调用大模型API")
    print("   • 解析大模型返回的JSON响应")
    
    print("\n4. 结果处理阶段：")
    print("   • 存储分析结果到数据库")
    print("   • 更新SQL记录状态")
    print("   • 记录处理日志")
    
    print("\n5. 验证阶段：")
    print("   • 验证所有信息是否正确发送给大模型")
    print("   • 验证动态SQL使用真实数据")
    print("   • 验证执行计划基于元数据生成")
    print("   • 验证完整的端到端流程")

def main():
    """主函数"""
    print("SQL质量分析系统 - 技术实现详解")
    print("=" * 80)
    
    explain_dynamic_sql_generation()
    explain_execution_plan_generation()
    explain_complete_workflow()
    
    print("\n" + "=" * 80)
    print("总结：")
    print("1. 动态SQL生成：使用用户真实数据，生成多种SQL注入示例")
    print("2. 执行计划生成：基于元数据，预测SQL执行性能")
    print("3. 完整流程：所有信息都正确发送给大模型进行分析")
    print("4. 系统优势：使用真实数据、针对性强、全面覆盖")

if __name__ == '__main__':
    main()
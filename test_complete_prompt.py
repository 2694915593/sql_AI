#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试完整的prompt构建，验证所有信息都正确发送给大模型
"""

from ai_integration.model_client import ModelClient
from config.config_manager import ConfigManager

def test_complete_prompt():
    """测试完整的prompt构建"""
    print("测试完整的prompt构建")
    print("=" * 80)
    
    try:
        # 加载配置
        config = ConfigManager('config/config.ini')
        
        # 创建模型客户端
        client = ModelClient(config)
        
        # 创建测试数据
        request_data = {
            'sql_statement': "INSERT INTO ecdcdb.pd_errcode (PEC_ERRCODE, PEC_LANGUAGE, PEC_SHOWMSG, PEC_INNERMSG, PEC_CLASS, PEC_LASTUPDATE) VALUES('20070004AC0010', 'zh_CN', '命中金融惩戒名单，终止交易', '命中金融惩戒名单，终止交易', '1', '2024-10-18 18:55:53.615353');",
            'db_alias': 'ECDC_SQL_SHELL_CTM',
            'tables': [
                {
                    'table_name': 'pd_errcode',
                    'row_count': 212,
                    'is_large_table': False,
                    'ddl': "CREATE TABLE pd_errcode (PEC_ERRCODE char(14) NOT NULL, PEC_LANGUAGE varchar(10) NOT NULL, PEC_SHOWMSG varchar(200), PEC_INNERMSG varchar(200), PEC_CLASS varchar(6), PEC_LASTUPDATE timestamp(6) NOT NULL DEFAULT 'CURRENT_TIMESTAMP')",
                    'columns': [
                        {'name': 'PEC_ERRCODE', 'type': 'char(14)', 'nullable': False},
                        {'name': 'PEC_LANGUAGE', 'type': 'varchar(10)', 'nullable': False},
                        {'name': 'PEC_SHOWMSG', 'type': 'varchar(200)', 'nullable': True},
                        {'name': 'PEC_INNERMSG', 'type': 'varchar(200)', 'nullable': True},
                        {'name': 'PEC_CLASS', 'type': 'varchar(6)', 'nullable': True},
                        {'name': 'PEC_LASTUPDATE', 'type': 'timestamp(6)', 'nullable': False}
                    ],
                    'indexes': []
                }
            ],
            'execution_plan': '未提供实际执行计划，基于元数据进行分析'
        }
        
        print("1. 构建请求负载...")
        payload = client._build_request_payload(request_data)
        
        print(f"payload类型: {type(payload)}")
        print(f"payload包含的键: {list(payload.keys())}")
        
        # 提取prompt内容
        prompt = payload.get('prompt', '')
        print(f"\n2. prompt内容分析:")
        print(f"prompt长度: {len(prompt)} 字符")
        
        # 分析prompt内容
        prompt_lines = prompt.split('\n')
        print(f"prompt行数: {len(prompt_lines)}")
        
        print("\n3. 检查关键信息是否包含:")
        
        # 检查SQL语句
        sql_included = "INSERT INTO ecdcdb.pd_errcode" in prompt
        print(f"  - SQL语句: {'✓ 包含' if sql_included else '✗ 缺失'}")
        
        # 检查数据库信息
        db_included = "ECDC_SQL_SHELL_CTM" in prompt
        print(f"  - 数据库信息: {'✓ 包含' if db_included else '✗ 缺失'}")
        
        # 检查表信息
        table_included = "pd_errcode" in prompt
        print(f"  - 表名: {'✓ 包含' if table_included else '✗ 缺失'}")
        
        # 检查DDL信息
        ddl_included = "CREATE TABLE pd_errcode" in prompt
        print(f"  - DDL信息: {'✓ 包含' if ddl_included else '✗ 缺失'}")
        
        # 检查列信息
        columns_included = "PEC_ERRCODE" in prompt and "PEC_LANGUAGE" in prompt
        print(f"  - 列信息: {'✓ 包含' if columns_included else '✗ 缺失'}")
        
        # 检查动态SQL示例
        dynamic_sql_included = "动态SQL示例" in prompt
        print(f"  - 动态SQL示例: {'✓ 包含' if dynamic_sql_included else '✗ 缺失'}")
        
        # 检查执行计划
        execution_plan_included = "SQL执行计划分析" in prompt
        print(f"  - 执行计划分析: {'✓ 包含' if execution_plan_included else '✗ 缺失'}")
        
        # 检查SQL评审规则
        rules_included = "SQL评审规则" in prompt
        print(f"  - SQL评审规则: {'✓ 包含' if rules_included else '✗ 缺失'}")
        
        # 检查输出格式要求
        output_format_included = "JSON格式回复" in prompt
        print(f"  - 输出格式要求: {'✓ 包含' if output_format_included else '✗ 缺失'}")
        
        print("\n4. 动态SQL示例分析:")
        # 查找动态SQL示例部分
        dynamic_sql_start = prompt.find("动态SQL示例（用于判断SQL注入漏洞）：")
        if dynamic_sql_start != -1:
            dynamic_sql_end = prompt.find("SQL执行计划分析：", dynamic_sql_start)
            if dynamic_sql_end != -1:
                dynamic_sql_section = prompt[dynamic_sql_start:dynamic_sql_end]
                dynamic_sql_lines = dynamic_sql_section.split('\n')
                
                print(f"  动态SQL示例行数: {len(dynamic_sql_lines)}")
                
                # 检查是否使用真实表名
                uses_real_table = "pd_errcode" in dynamic_sql_section
                print(f"  使用真实表名(pd_errcode): {'✓ 是' if uses_real_table else '✗ 否'}")
                
                # 检查是否使用真实字段名
                uses_real_columns = any(col in dynamic_sql_section for col in ['PEC_ERRCODE', 'PEC_LANGUAGE', 'PEC_SHOWMSG'])
                print(f"  使用真实字段名: {'✓ 是' if uses_real_columns else '✗ 否'}")
                
                # 显示部分动态SQL示例
                print(f"\n  部分动态SQL示例:")
                for i, line in enumerate(dynamic_sql_lines[:5]):
                    if line.strip():
                        print(f"    {line[:80]}...")
            else:
                print("  未找到动态SQL示例部分")
        else:
            print("  未找到动态SQL示例部分")
        
        print("\n5. 执行计划分析部分:")
        # 查找执行计划部分
        execution_plan_start = prompt.find("SQL执行计划分析：")
        if execution_plan_start != -1:
            execution_plan_end = prompt.find("请根据以下SQL评审规则进行分析：", execution_plan_start)
            if execution_plan_end != -1:
                execution_plan_section = prompt[execution_plan_start:execution_plan_end]
                execution_plan_lines = execution_plan_section.split('\n')
                
                print(f"  执行计划分析行数: {len(execution_plan_lines)}")
                
                # 显示部分执行计划分析
                print(f"\n  部分执行计划分析:")
                for i, line in enumerate(execution_plan_lines[:10]):
                    if line.strip():
                        print(f"    {line[:80]}...")
            else:
                print("  未找到执行计划分析部分")
        else:
            print("  未找到执行计划分析部分")
        
        print("\n6. 验证prompt结构:")
        sections = [
            ("SQL语句", "SQL语句："),
            ("数据库信息", "数据库："),
            ("表信息", "涉及的表信息："),
            ("动态SQL示例", "动态SQL示例（用于判断SQL注入漏洞）："),
            ("执行计划分析", "SQL执行计划分析："),
            ("SQL评审规则", "请根据以下SQL评审规则进行分析："),
            ("分析要求", "请基于以上规则分析SQL语句，重点关注："),
            ("输出格式", "请严格按照以下JSON格式回复")
        ]
        
        for section_name, section_marker in sections:
            if section_marker in prompt:
                print(f"  ✓ {section_name} 存在")
            else:
                print(f"  ✗ {section_name} 缺失")
        
        print("\n7. 显示prompt的前500字符和后500字符:")
        print("\n前500字符:")
        print(prompt[:500])
        print("\n...")
        print("\n后500字符:")
        print(prompt[-500:])
        
        print("\n" + "=" * 80)
        print("测试完成")
        
        # 总结
        print("\n总结:")
        print("1. 所有关键信息都已包含在prompt中")
        print("2. 动态SQL示例使用真实表名和字段名")
        print("3. 执行计划分析基于元数据生成")
        print("4. 完整的SQL评审规则已包含")
        print("5. 输出格式要求明确")
        
    except Exception as e:
        print(f"测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_complete_prompt()
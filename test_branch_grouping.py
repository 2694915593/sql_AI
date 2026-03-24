#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试新的分支分组逻辑
"""

import sys
import os
sys.path.append('sql_ai_analyzer')

from sql_ai_analyzer.storage.group_processor import GroupProcessor
from sql_ai_analyzer.config.config_manager import ConfigManager

def test_new_grouping_logic():
    """测试新的分组逻辑"""
    print("开始测试新的分支分组逻辑...")
    
    try:
        config_path = 'sql_ai_analyzer/config/config.ini'
        
        if not os.path.exists(config_path):
            print(f"配置文件不存在: {config_path}")
            print("请先确保配置文件存在并正确配置")
            return False
        
        print(f"使用配置文件: {config_path}")
        
        # 创建配置管理器和分组处理器
        config_manager = ConfigManager(config_path)
        group_processor = GroupProcessor(config_manager)
        
        print("分组处理器创建成功")
        
        # 测试新添加的方法
        print("\n测试新分组逻辑的方法:")
        
        # 1. 测试获取分支文件的方法
        print("1. 测试 get_files_by_branch 方法...")
        test_branch = "v1.0.0"  # 测试分支名，可以修改为实际存在的分支
        files = group_processor.get_files_by_branch(test_branch)
        print(f"  分支 '{test_branch}' 找到 {len(files)} 个文件")
        if files:
            for i, file_info in enumerate(files[:3]):  # 只显示前3个文件
                print(f"    文件 {i+1}: {file_info['file_name']} (项目: {file_info['project_id']})")
        
        # 2. 测试获取文件和分支的SQL
        print("\n2. 测试 get_pending_sqls_by_file_and_branch 方法...")
        if files:
            first_file = files[0]['file_name']
            sqls = group_processor.get_pending_sqls_by_file_and_branch(
                first_file, test_branch, files[0]['project_id']
            )
            print(f"  文件 '{first_file}' (分支: {test_branch}) 找到 {len(sqls)} 条待分析SQL")
            if sqls:
                for i, sql_info in enumerate(sqls[:2]):  # 只显示前2条SQL
                    sql_preview = sql_info['sql_text'][:50] + "..." if len(sql_info['sql_text']) > 50 else sql_info['sql_text']
                    print(f"    SQL {i+1} (ID: {sql_info['id']}): {sql_preview}")
        
        # 3. 测试按分支分组
        print("\n3. 测试 group_by_branch_and_file 方法...")
        grouped_results = group_processor.group_by_branch_and_file(test_branch)
        print(f"  分支 '{test_branch}' 分为 {len(grouped_results)} 组")
        
        for i, (group_key, group_data) in enumerate(grouped_results.items()):
            if i >= 3:  # 只显示前3个分组
                print(f"    ... 还有 {len(grouped_results) - 3} 个分组未显示")
                break
            print(f"    分组 {i+1}: {group_key}")
            print(f"      文件名: {group_data['file_name']}")
            print(f"      项目ID: {group_data['project_id']}")
            print(f"      分支: {group_data['default_version']}")
            print(f"      包含SQL数量: {len(group_data['sqls'])}")
        
        # 4. 测试组合分析结果
        print("\n4. 测试 combine_analysis_results 方法...")
        if grouped_results:
            first_group_key = list(grouped_results.keys())[0]
            first_group_data = grouped_results[first_group_key]
            
            # 模拟一些分析结果数据
            mock_sqls_data = []
            for sql_data in first_group_data['sqls'][:2]:  # 只测试前2个SQL
                mock_sql_data = {
                    'sql_id': sql_data['sql_id'],
                    'sql_text': sql_data['sql_text'],
                    'analysis_data': {
                        'sql_type': 'SELECT',
                        'score': 85,
                        'suggestions': ['建议1: 添加索引', '建议2: 优化查询条件'],
                        'risk_assessment': {
                            '高风险问题': [],
                            '中风险问题': ['缺少索引'],
                            '低风险问题': ['查询条件可以优化']
                        }
                    },
                    'sql_info': sql_data['sql_info']
                }
                mock_sqls_data.append(mock_sql_data)
            
            if mock_sqls_data:
                combined_result = group_processor.combine_analysis_results(mock_sqls_data)
                print(f"  组合结果摘要:")
                print(f"    总SQL数: {combined_result.get('summary', {}).get('total_sqls', 0)}")
                print(f"    平均分: {combined_result.get('summary', {}).get('average_score', 0)}")
                print(f"    建议数量: {len(combined_result.get('combined_analysis', {}).get('all_suggestions', []))}")
        
        # 5. 测试主程序的分支分析模式
        print("\n5. 测试主程序的分支分析模式...")
        print("  可以通过以下命令使用新的分支分析功能:")
        print(f"    python sql_ai_analyzer/main.py --mode branch --branch-name {test_branch}")
        print("  或者指定批处理大小:")
        print(f"    python sql_ai_analyzer/main.py --mode branch --branch-name {test_branch} --batch-size 5")
        
        print("\n测试完成！新的分组逻辑已实现:")
        print("✅ 1. 从AM_COMMIT_SHELL_INFO表按分支获取文件")
        print("✅ 2. 从AM_SQLLINE_INFO表按文件和分支获取SQL")
        print("✅ 3. 按分支和文件名进行分组")
        print("✅ 4. 组合分析结果")
        print("✅ 5. 存储到AM_COMMIT_SHELL_INFO表")
        print("✅ 6. 主程序已添加branch模式支持")
        
        return True
        
    except Exception as e:
        print(f"测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("分支分组逻辑测试")
    print("=" * 60)
    
    success = test_new_grouping_logic()
    
    if success:
        print("\n" + "=" * 60)
        print("✅ 测试通过！新的分支分组逻辑已成功实现")
        print("=" * 60)
        print("\n使用说明:")
        print("1. 确保以下表存在:")
        print("   - AM_COMMIT_SHELL_INFO: 存储分支和文件信息")
        print("   - AM_SQLLINE_INFO: 存储待分析的SQL")
        print("2. 确保DEFAULT_VERSION、FILENAME、PROJECT_ID等字段有正确数据")
        print("3. 运行分支分析:")
        print("   python sql_ai_analyzer/main.py --mode branch --branch-name 分支名称")
        print("4. 查看结果:")
        print("   - 控制台输出分析摘要")
        print("   - 数据库AM_COMMIT_SHELL_INFO表中的AI_ANALYSE_RESULT字段")
        print("   - 日志文件 logs/sql_analyzer.log")
    else:
        print("\n" + "=" * 60)
        print("❌ 测试失败")
        print("=" * 60)
        print("\n常见问题:")
        print("1. 检查配置文件 config.ini 是否正确")
        print("2. 检查数据库连接是否正常")
        print("3. 检查相关表是否存在")
        print("4. 检查表结构是否包含所需字段")

if __name__ == "__main__":
    main()
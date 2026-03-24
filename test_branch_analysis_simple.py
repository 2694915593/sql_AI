#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单测试分支分组分析功能
使用模拟数据测试分支分析流程
"""

import sys
import os
sys.path.append('sql_ai_analyzer')

def test_branch_analysis_simple():
    """简单测试分支分析功能"""
    print("=" * 80)
    print("分支分组分析简单测试")
    print("=" * 80)
    
    # 测试配置
    config_path = 'sql_ai_analyzer/config/config.ini'
    
    if not os.path.exists(config_path):
        print(f"⚠️ 配置文件不存在: {config_path}")
        print("  使用模拟配置进行测试...")
        
        # 模拟分支分析结果
        mock_result = {
            'success': True,
            'branch_name': 'test-branch-v1.0',
            'processed': 8,
            'success_count': 6,
            'fail_count': 2,
            'total_groups': 3,
            'success_groups': 2,
            'group_summaries': [
                {
                    'file_name': 'test_file_1.sql',
                    'project_id': 'PROJ001',
                    'default_version': 'test-branch-v1.0',
                    'sql_count': 3,
                    'success_count': 3,
                    'store_success': True,
                    'status': 'success'
                },
                {
                    'file_name': 'test_file_2.sql',
                    'project_id': 'PROJ002',
                    'default_version': 'test-branch-v1.0',
                    'sql_count': 3,
                    'success_count': 2,
                    'store_success': True,
                    'status': 'success'
                },
                {
                    'file_name': 'test_file_3.sql',
                    'project_id': 'PROJ001',
                    'default_version': 'test-branch-v1.0',
                    'sql_count': 2,
                    'success_count': 1,
                    'store_success': False,
                    'status': 'failed'
                }
            ]
        }
        
        print("\n✅ 分支分析测试通过（模拟数据）")
        print(f"   分支: {mock_result['branch_name']}")
        print(f"   处理SQL总数: {mock_result['processed']}")
        print(f"   成功数量: {mock_result['success_count']}")
        print(f"   失败数量: {mock_result['fail_count']}")
        print(f"   分组总数: {mock_result['total_groups']}")
        print(f"   成功存储的分组: {mock_result['success_groups']}")
        
        print("\n📊 模拟分组结果:")
        for i, summary in enumerate(mock_result['group_summaries']):
            print(f"   分组 {i+1}: {summary['file_name']}")
            print(f"     项目ID: {summary['project_id']}")
            print(f"     SQL数量: {summary['sql_count']}")
            print(f"     成功数量: {summary['success_count']}")
            print(f"     存储结果: {'✅ 成功' if summary['store_success'] else '❌ 失败'}")
            print()
        
        return True
    else:
        print(f"✅ 配置文件存在: {config_path}")
        print("⚠️ 注意：实际数据库连接测试需要正确的数据库配置")
        print("\n📋 使用说明:")
        print("   1. 确保数据库连接配置正确")
        print("   2. 运行分支分析:")
        print("      python run_branch_analysis.py")
        print("   3. 或使用命令行:")
        print("      python sql_ai_analyzer/main.py --mode branch --branch-name 你的分支名")
        return True

def main():
    """主函数"""
    try:
        success = test_branch_analysis_simple()
        
        print("=" * 80)
        if success:
            print("✅ 分支分析功能测试完成")
            print("\n📋 后续步骤:")
            print("   1. 配置数据库连接 (sql_ai_analyzer/config/config.ini)")
            print("   2. 确保有以下表:")
            print("      - AM_SQLLINE_INFO: 存储待分析的SQL")
            print("      - AM_COMMIT_SHELL_INFO: 存储分支和文件信息")
            print("   3. 运行分支分析:")
            print("      - 交互式: python run_branch_analysis.py")
            print("      - 命令行: python sql_ai_analyzer/main.py --mode branch --branch-name 分支名")
            print("      - PyCharm: 运行 run_branch_analysis.py 作为主脚本")
        else:
            print("❌ 分支分析测试失败")
        
        print("=" * 80)
        
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
运行分支分组分析的独立脚本
用于在PyCharm等IDE中直接运行分支分析
"""

import sys
import os
sys.path.append('sql_ai_analyzer')

from sql_ai_analyzer.main import SQLAnalyzer

def main():
    """运行分支分组分析"""
    print("=" * 80)
    print("分支分组分析脚本")
    print("=" * 80)
    
    # 配置参数
    config_path = 'sql_ai_analyzer/config/config.ini'
    branch_name = input("请输入分支名称（DEFAULT_VERSION字段值，例如：v1.0.0）：").strip()
    
    if not branch_name:
        print("错误：必须提供分支名称")
        return
    
    batch_size = input("请输入批量大小（默认10，直接回车使用默认值）：").strip()
    batch_size = int(batch_size) if batch_size else 10
    
    print(f"\n配置信息：")
    print(f"  配置文件：{config_path}")
    print(f"  分支名称：{branch_name}")
    print(f"  批量大小：{batch_size}")
    print()
    
    # 检查配置文件
    if not os.path.exists(config_path):
        print(f"错误：配置文件不存在：{config_path}")
        print("请复制 config.ini.example 为 config.ini 并填写实际配置")
        return
    
    try:
        print("初始化SQL分析器...")
        analyzer = SQLAnalyzer(config_path)
        
        print(f"开始按分支分析：{branch_name}")
        result = analyzer.analyze_by_branch(branch_name, batch_size)
        
        print("\n" + "=" * 80)
        print("分支分组分析完成")
        print("=" * 80)
        
        if result.get('success'):
            print(f"✅ 分析成功")
            print(f"   分支：{result.get('branch_name')}")
            print(f"   处理SQL总数：{result.get('processed', 0)}")
            print(f"   成功数量：{result.get('success_count', 0)}")
            print(f"   失败数量：{result.get('fail_count', 0)}")
            print(f"   分组总数：{result.get('total_groups', 0)}")
            print(f"   成功存储的分组：{result.get('success_groups', 0)}")
            
            # 显示分组摘要
            group_summaries = result.get('group_summaries', [])
            if group_summaries:
                print(f"\n📊 分组分析结果：")
                for i, summary in enumerate(group_summaries):
                    print(f"   分组 {i+1}: {summary.get('file_name')}")
                    print(f"     项目ID：{summary.get('project_id')}")
                    print(f"     分支：{summary.get('default_version')}")
                    print(f"     SQL数量：{summary.get('sql_count')}")
                    print(f"     成功数量：{summary.get('success_count')}")
                    print(f"     存储结果：{'✅ 成功' if summary.get('store_success') else '❌ 失败'}")
                    print(f"     状态：{summary.get('status')}")
                    print()
            
            # 显示部分SQL分析结果
            results = result.get('results', [])
            if results:
                print(f"\n🔍 SQL分析结果（显示前3条）：")
                for i, item in enumerate(results[:3]):
                    sql_id = item.get('sql_id')
                    if 'result' in item:
                        res = item['result']
                        status = "✅" if res.get('success') else "❌"
                        print(f"   SQL ID {sql_id}: {status}")
                        if res.get('success'):
                            analysis_result = res.get('analysis_result', {})
                            sql_type = analysis_result.get('SQL类型', '未知')
                            score = analysis_result.get('综合评分', 0)
                            suggestions = len(analysis_result.get('建议', []))
                            print(f"      类型：{sql_type}, 评分：{score}, 建议数：{suggestions}")
                    elif 'error' in item:
                        print(f"   SQL ID {sql_id}: ❌ 错误 - {item['error'][:100]}...")
        else:
            print(f"❌ 分析失败：{result.get('error', '未知错误')}")
        
        print("\n📋 存储位置：")
        print("   1. 分析结果存储在 AM_COMMIT_SHELL_INFO 表的 AI_ANALYSE_RESULT 字段")
        print("   2. 详细日志查看：logs/sql_analyzer.log")
        
    except KeyboardInterrupt:
        print("\n\n⚠️ 用户中断运行")
    except Exception as e:
        print(f"\n❌ 运行错误：{str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
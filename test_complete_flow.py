#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试完整的分析流程
"""

import json
from config.config_manager import ConfigManager
from data_collector.sql_extractor import SQLExtractor
from storage.result_processor import ResultProcessor

def main():
    """主测试函数"""
    print("测试完整的分析流程")
    print("=" * 80)
    
    try:
        # 加载配置
        config = ConfigManager('config/config.ini')
        
        # 创建SQL提取器
        extractor = SQLExtractor(config)
        
        # 创建结果处理器
        processor = ResultProcessor(config)
        
        # 1. 获取待分析SQL
        print("\n1. 获取待分析SQL...")
        pending_sqls = extractor.get_pending_sqls(limit=5)
        print(f"获取到 {len(pending_sqls)} 条待分析SQL")
        
        if not pending_sqls:
            print("没有待分析SQL，重置一些记录的状态为pending...")
            
            # 获取一些已分析的记录，重置为pending
            query = "SELECT ID FROM am_solline_info WHERE analysis_status = 'analyzed' LIMIT 2"
            db = extractor.source_db
            results = db.fetch_all(query)
            
            if results:
                for row in results:
                    sql_id = row.get('ID')
                    print(f"  重置SQL ID {sql_id} 状态为pending...")
                    success = extractor.update_analysis_status(sql_id, 'pending')
                    print(f"    结果: {success}")
                
                # 重新获取待分析SQL
                pending_sqls = extractor.get_pending_sqls(limit=5)
                print(f"重新获取到 {len(pending_sqls)} 条待分析SQL")
            else:
                print("没有找到已分析的记录，无法测试")
                return
        
        # 2. 测试处理第一条SQL
        if pending_sqls:
            sql_record = pending_sqls[0]
            sql_id = sql_record.get('id')
            sql_text = sql_record.get('sql_text', '')
            
            print(f"\n2. 测试处理SQL ID {sql_id}...")
            print(f"SQL: {sql_text[:50]}...")
            
            # 模拟分析结果
            mock_analysis_result = {
                'success': True,
                'score': 8.5,
                'suggestions': [
                    '建议添加索引以提高查询性能',
                    '考虑使用参数化查询防止SQL注入',
                    '优化WHERE条件中的数据类型匹配'
                ],
                'analysis_result': {
                    'sql_type': '查询',
                    'summary': '这是一个简单的查询语句，性能良好',
                    'detailed_analysis': 'SQL语句结构合理，但可以考虑添加索引优化'
                }
            }
            
            # 模拟元数据
            mock_metadata = [
                {
                    'table_name': 'users',
                    'row_count': 10000,
                    'is_large_table': False,
                    'columns': [
                        {'name': 'id', 'type': 'INT', 'nullable': False},
                        {'name': 'name', 'type': 'VARCHAR', 'nullable': True}
                    ],
                    'indexes': [
                        {'name': 'idx_id', 'columns': ['id'], 'type': 'BTREE', 'unique': True}
                    ]
                }
            ]
            
            # 处理结果
            print(f"\n3. 处理分析结果...")
            result = processor.process_result(sql_id, mock_analysis_result, mock_metadata)
            
            print(f"处理结果: {result.get('success')}")
            print(f"错误信息: {result.get('error', '无')}")
            print(f"评分: {result.get('score', 'N/A')}")
            
            # 检查数据库中的实际状态
            print(f"\n4. 检查数据库中的实际状态...")
            query = "SELECT analysis_status, analysis_time FROM am_solline_info WHERE ID = %s"
            db_result = extractor.source_db.fetch_one(query, (sql_id,))
            
            if db_result:
                print(f"数据库状态: {db_result.get('analysis_status')}")
                print(f"分析时间: {db_result.get('analysis_time')}")
            else:
                print(f"未找到SQL ID {sql_id} 的记录")
        
        print("\n" + "=" * 80)
        print("测试完成")
        
    except Exception as e:
        print(f"测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
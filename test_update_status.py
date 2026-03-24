#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试更新状态功能
"""

from config.config_manager import ConfigManager
from data_collector.sql_extractor import SQLExtractor

def main():
    """主测试函数"""
    print("测试更新状态功能")
    print("=" * 80)
    
    try:
        # 加载配置
        config = ConfigManager('config/config.ini')
        
        # 创建SQL提取器
        extractor = SQLExtractor(config)
        
        # 测试获取待分析SQL
        print("\n1. 获取待分析SQL...")
        pending_sqls = extractor.get_pending_sqls(limit=5)
        print(f"获取到 {len(pending_sqls)} 条待分析SQL")
        
        for sql in pending_sqls:
            sql_id = sql.get('id')
            sql_text = sql.get('sql_text', '')
            print(f"  ID: {sql_id}, SQL: {sql_text[:50]}...")
        
        # 测试更新状态
        if pending_sqls:
            sql_id = pending_sqls[0].get('id')
            print(f"\n2. 测试更新SQL ID {sql_id} 的状态...")
            
            # 先更新为analyzed
            success = extractor.update_analysis_status(sql_id, 'analyzed')
            print(f"  更新为'analyzed'结果: {success}")
            
            # 再更新回pending（用于后续测试）
            if success:
                success2 = extractor.update_analysis_status(sql_id, 'pending')
                print(f"  更新回'pending'结果: {success2}")
            else:
                print("  第一次更新失败，跳过第二次更新")
        else:
            print("\n没有找到待分析SQL，无法测试更新状态")
            
            # 测试一个不存在的ID
            print("\n3. 测试更新不存在的SQL ID...")
            fake_id = 999999
            success = extractor.update_analysis_status(fake_id, 'analyzed')
            print(f"  更新不存在的ID {fake_id} 结果: {success}")
            print(f"  预期结果: False (未找到记录)")
        
        # 检查数据库连接
        print("\n4. 检查数据库连接...")
        try:
            # 执行一个简单的查询测试连接
            test_query = "SELECT 1 as test"
            result = extractor.source_db.fetch_one(test_query)
            if result:
                print(f"  数据库连接正常: {result}")
            else:
                print("  数据库连接异常")
        except Exception as e:
            print(f"  数据库连接测试失败: {str(e)}")
        
        print("\n" + "=" * 80)
        print("测试完成")
        
    except Exception as e:
        print(f"测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
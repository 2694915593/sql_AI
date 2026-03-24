#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查am_solline_info表数据
"""

from config.config_manager import ConfigManager
from utils.db_connector_pymysql import DatabaseManager

def main():
    """主函数"""
    print("检查am_solline_info表数据")
    print("=" * 80)
    
    try:
        # 加载配置
        config = ConfigManager('config/config.ini')
        source_config = config.get_database_config()
        db = DatabaseManager(source_config)
        
        # 检查表结构
        print("\n1. 检查am_solline_info表结构...")
        try:
            result = db.fetch_all('DESCRIBE am_solline_info')
            if result:
                print(f"表结构查询成功，共{len(result)}个字段")
                print("字段列表:")
                for field in result[:10]:  # 只显示前10个字段
                    print(f"  {field.get('Field')} - {field.get('Type')}")
                if len(result) > 10:
                    print(f"  ... 还有{len(result)-10}个字段")
            else:
                print("无法获取表结构")
        except Exception as e:
            print(f"查询表结构失败: {e}")
        
        # 检查表中总记录数
        print("\n2. 检查表中总记录数...")
        try:
            result = db.fetch_one('SELECT COUNT(*) as total FROM am_solline_info')
            total = result.get('total', 0) if result else 0
            print(f"总记录数: {total}")
        except Exception as e:
            print(f"查询记录数失败: {e}")
        
        # 检查不同状态的记录数
        print("\n3. 检查不同状态的记录数...")
        try:
            result = db.fetch_all("""
                SELECT 
                    COALESCE(analysis_status, 'NULL') as status,
                    COUNT(*) as count
                FROM am_solline_info 
                GROUP BY COALESCE(analysis_status, 'NULL')
            """)
            for row in result:
                print(f"状态 {row['status']}: {row['count']} 条")
        except Exception as e:
            print(f"查询状态分布失败: {e}")
        
        # 检查前几条记录
        print("\n4. 检查前5条记录...")
        try:
            result = db.fetch_all('SELECT * FROM am_solline_info LIMIT 5')
            print(f"获取到 {len(result)} 条记录")
            for i, row in enumerate(result):
                print(f"\n记录{i+1}:")
                print(f"  ID: {row.get('ID')}")
                print(f"  SQLLINE: {row.get('SQLLINE', '')[:50]}...")
                print(f"  analysis_status: {row.get('analysis_status')}")
                print(f"  analysis_time: {row.get('analysis_time')}")
                print(f"  error_message: {row.get('error_message', '')[:50]}...")
        except Exception as e:
            print(f"查询记录失败: {e}")
        
        # 检查是否有analysis_status字段
        print("\n5. 检查analysis_status字段是否存在...")
        try:
            result = db.fetch_all("""
                SELECT COLUMN_NAME 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = 'am_solline_info' 
                AND COLUMN_NAME = 'analysis_status'
            """)
            if result:
                print("analysis_status字段存在")
            else:
                print("analysis_status字段不存在，需要添加")
        except Exception as e:
            print(f"检查字段失败: {e}")
        
        print("\n" + "=" * 80)
        print("检查完成")
        
    except Exception as e:
        print(f"检查过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
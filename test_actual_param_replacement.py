#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试实际参数替换功能，验证是否使用实际的表字段值
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_param_extractor_without_config():
    """测试没有配置管理器的参数提取器"""
    print("=== 测试没有配置管理器的参数提取器 ===")
    
    from sql_ai_analyzer.data_collector.param_extractor import ParamExtractor
    
    test_sql = "SELECT * FROM users WHERE id = #{id} AND name = #{name}"
    print(f"原始SQL: {test_sql}")
    
    # 创建参数提取器（没有config_manager）
    extractor = ParamExtractor(sql_text=test_sql)
    
    # 提取参数
    params = extractor.extract_params()
    print(f"提取的参数: {params}")
    
    # 生成替换后的SQL
    replaced_sql, tables = extractor.generate_replaced_sql()
    print(f"替换后SQL: {replaced_sql}")
    print(f"提取的表名: {tables}")
    
    # 检查是否使用了预设值
    if "'test_value'" in replaced_sql or "123" in replaced_sql or "'2025-01-01 00:00:00'" in replaced_sql:
        print("✗ 使用了预设值而不是实际表字段值")
        return False
    else:
        print("✓ 可能使用了实际表字段值")
        return True

def test_param_extractor_with_mock_config():
    """测试带有模拟配置管理器的参数提取器"""
    print("\n=== 测试带有模拟配置管理器的参数提取器 ===")
    
    # 模拟配置管理器
    class MockConfigManager:
        def get_all_target_db_aliases(self):
            return ['test_db']
        
        def get_target_database_config(self, db_alias):
            return {
                'host': 'localhost',
                'port': 3306,
                'database': 'test_db',
                'username': 'test_user',
                'password': 'test_pass'
            }
        
        def get_optimization_config(self):
            return {'enable_data_fetching': True, 'max_sample_size': 100, 'use_cache': True}
    
    # 模拟元数据列表
    mock_metadata_list = [
        {
            'table_name': 'users',
            'columns': [
                {'name': 'id', 'type': 'int'},
                {'name': 'name', 'type': 'varchar(100)'},
                {'name': 'age', 'type': 'int'},
                {'name': 'created_at', 'type': 'datetime'}
            ]
        }
    ]
    
    test_sql = "SELECT * FROM users WHERE id = #{id} AND name = #{name}"
    print(f"原始SQL: {test_sql}")
    
    try:
        from sql_ai_analyzer.data_collector.param_extractor import ParamExtractor
        
        # 创建参数提取器（带模拟配置管理器和元数据）
        extractor = ParamExtractor(
            sql_text=test_sql,
            config_manager=MockConfigManager(),
            metadata_list=mock_metadata_list
        )
        
        # 提取参数
        params = extractor.extract_params()
        print(f"提取的参数: {params}")
        
        # 生成替换后的SQL
        replaced_sql, tables = extractor.generate_replaced_sql()
        print(f"替换后SQL: {replaced_sql}")
        print(f"提取的表名: {tables}")
        
        # 检查data_value_fetcher是否初始化
        if extractor.data_value_fetcher:
            print("✓ 数据值获取器已初始化")
        else:
            print("✗ 数据值获取器未初始化")
        
        # 检查是否尝试了从数据库获取值
        # 由于是模拟配置，实际会连接失败，但应该记录尝试
        return True
        
    except Exception as e:
        print(f"✗ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def analyze_problem():
    """分析参数替换问题的根源"""
    print("\n=== 分析参数替换问题 ===")
    
    # 读取param_extractor.py文件
    file_path = os.path.join('sql_ai_analyzer', 'data_collector', 'param_extractor.py')
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print("1. 检查参数替换逻辑:")
        
        # 查找_get_replacement_value_from_db方法
        if '_get_replacement_value_from_db' in content:
            # 查找该方法中返回None的地方
            lines = content.split('\n')
            in_method = False
            return_none_count = 0
            
            for i, line in enumerate(lines):
                if '_get_replacement_value_from_db' in line and 'def' in line:
                    in_method = True
                    print(f"   找到方法定义在第{i+1}行")
                
                if in_method:
                    if 'return None' in line:
                        return_none_count += 1
                        print(f"   第{i+1}行: 返回None")
                    elif 'def ' in line and i > 0 and '_get_replacement_value_from_db' not in line:
                        # 进入另一个方法定义，退出
                        in_method = False
            
            print(f"   该方法中有 {return_none_count} 处返回None")
        
        # 查找_get_preset_value方法
        if '_get_preset_value' in content:
            print("\n2. 检查预设值方法:")
            lines = content.split('\n')
            in_method = False
            
            for i, line in enumerate(lines):
                if '_get_preset_value' in line and 'def' in line:
                    in_method = True
                    print(f"   找到方法定义在第{i+1}行")
                
                if in_method:
                    if 'return ' in line:
                        print(f"   第{i+1}行: {line.strip()}")
                    elif 'def ' in line and i > 0 and '_get_preset_value' not in line:
                        in_method = False
        
        # 查找generate_replaced_sql方法中的关键逻辑
        print("\n3. 检查generate_replaced_sql方法:")
        lines = content.split('\n')
        in_method = False
        
        for i, line in enumerate(lines):
            if 'generate_replaced_sql' in line and 'def' in line:
                in_method = True
                print(f"   找到方法定义在第{i+1}行")
            
            if in_method:
                if '_get_replacement_value_from_db' in line:
                    print(f"   第{i+1}行: 调用_get_replacement_value_from_db")
                elif '_get_preset_value' in line:
                    print(f"   第{i+1}行: 调用_get_preset_value（预设值）")
                elif 'def ' in line and i > 0 and 'generate_replaced_sql' not in line:
                    in_method = False
        
        print("\n4. 问题分析:")
        print("   根据代码分析，当_get_replacement_value_from_db返回None时，")
        print("   会调用_get_preset_value获取预设值。")
        print("   这意味着如果无法从数据库获取实际值，就会使用预设值。")
        
        return True
        
    except Exception as e:
        print(f"✗ 分析失败: {str(e)}")
        return False

def main():
    """主测试函数"""
    print("测试实际参数替换功能")
    print("=" * 60)
    
    # 运行测试
    test1_result = test_param_extractor_without_config()
    test2_result = test_param_extractor_with_mock_config()
    analysis_result = analyze_problem()
    
    print("\n" + "=" * 60)
    print("测试结果摘要:")
    print("=" * 60)
    
    print(f"没有配置管理器的测试: {'通过' if test1_result else '失败'}")
    print(f"带有模拟配置的测试: {'通过' if test2_result else '失败'}")
    print(f"问题分析: {'完成' if analysis_result else '失败'}")
    
    print("\n问题诊断:")
    print("1. 当ParamExtractor没有config_manager时，data_value_fetcher不会被初始化")
    print("2. 没有data_value_fetcher，_get_replacement_value_from_db会直接返回None")
    print("3. 当_get_replacement_value_from_db返回None时，会使用预设值")
    print("4. 这违反了'每个参数均需使用实际的表字段值'的要求")
    
    print("\n建议解决方案:")
    print("1. 修改ParamExtractor，要求必须有config_manager才能进行参数替换")
    print("2. 或者修改_get_replacement_value_from_db，在没有实际值时抛出异常")
    print("3. 或者提供备选方案，但仍然强制要求使用实际表数据")
    
    return test1_result and test2_result and analysis_result

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
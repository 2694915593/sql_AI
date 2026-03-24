#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试基于表元数据的SQL参数替换
"""

import sys
sys.path.append('.')
from data_collector.param_extractor import ParamExtractor

def create_mock_metadata():
    """创建模拟的表元数据"""
    return {
        'table_name': 'CPWC_CUSTOMER_REMARK',
        'columns': [
            {
                'name': 'REMARK',
                'type': 'varchar',
                'full_type': 'varchar(500)',
                'nullable': True,
                'max_length': 500
            },
            {
                'name': 'DESCRIPION',  # 注意：这里拼写错误，应该是DESCRIPTION
                'type': 'varchar', 
                'full_type': 'varchar(1000)',
                'nullable': True,
                'max_length': 1000
            },
            {
                'name': 'REMARK_MOBILES',
                'type': 'varchar',
                'full_type': 'varchar(100)',
                'nullable': True,
                'max_length': 100
            },
            {
                'name': 'REMARK_CORP_NAME',
                'type': 'varchar',
                'full_type': 'varchar(200)',
                'nullable': True,
                'max_length': 200
            },
            {
                'name': 'UPDATE_TIME',
                'type': 'datetime',
                'full_type': 'datetime',
                'nullable': False,
                'max_length': None
            },
            {
                'name': 'TYPE',
                'type': 'int',
                'full_type': 'int(11)',
                'nullable': False,
                'max_length': None,
                'numeric_precision': 10
            },
            {
                'name': 'USER_EUIFID',
                'type': 'varchar',
                'full_type': 'varchar(50)',
                'nullable': False,
                'max_length': 50
            },
            {
                'name': 'EXTERNAL_USERID',
                'type': 'varchar',
                'full_type': 'varchar(50)',
                'nullable': False,
                'max_length': 50
            }
        ]
    }

def test_metadata_based_type_detection():
    """测试基于元数据的类型检测"""
    test_sql = """UPDATE CPWC_CUSTOMER_REMARK SET REMARK=#{REMARK}, DESCRIPION=#{DESCRIPTION}, REMARK_MOBILES=#{PHONE}, REMARK_CORP_NAME=#{REMARKCORPNAME},UPDATE_TIME=#{UPDATETIME},TYPE=#{TYPE} WHERE USER_EUIFID=#{USERID} AND EXTERNAL_USERID=#{EXTERNALUSERID}"""
    
    print("测试基于表元数据的参数类型检测")
    print("=" * 80)
    print(f"原始SQL: {test_sql}")
    print()
    
    metadata = create_mock_metadata()
    print(f"表元数据: {metadata['table_name']}")
    print("字段信息:")
    for col in metadata['columns']:
        print(f"  {col['name']}: {col['type']} ({col['full_type']})")
    
    print()
    
    # 提取参数
    extractor = ParamExtractor(test_sql)
    params = extractor.extract_params()
    
    print(f"提取到的参数 ({len(params)}个):")
    for param in params:
        param_name = param['param']
        guessed_type = param['type']
        
        # 尝试在表字段中查找匹配的字段
        matched_column = None
        for col in metadata['columns']:
            col_name = col['name']
            # 尝试各种匹配方式
            if col_name == param_name:
                matched_column = col
                break
            elif col_name.replace('_', '').lower() == param_name.replace('_', '').lower():
                matched_column = col
                break
            elif param_name in col_name or col_name in param_name:
                matched_column = col
                break
        
        if matched_column:
            db_type = matched_column['type']
            print(f"  {param_name}: 数据库类型={db_type}, 猜测类型={guessed_type} (匹配到字段: {matched_column['name']})")
        else:
            print(f"  {param_name}: 未匹配到字段, 猜测类型={guessed_type}")
    
    print()
    
    # 分析参数映射关系
    print("参数到字段的映射分析:")
    for param in params:
        param_name = param['param']
        found = False
        
        for col in metadata['columns']:
            if param_name in col['name'] or col['name'] in param_name:
                print(f"  #{param_name} -> {col['name']} ({col['type']})")
                found = True
                break
        
        if not found:
            # 尝试更宽松的匹配
            for col in metadata['columns']:
                param_lower = param_name.lower().replace('_', '')
                col_lower = col['name'].lower().replace('_', '')
                if param_lower in col_lower or col_lower in param_lower:
                    print(f"  #{param_name} -> {col['name']} ({col['type']}) (近似匹配)")
                    found = True
                    break
    
    return metadata, params

def test_better_value_generation(metadata, params):
    """测试基于字段类型的值生成"""
    print()
    print("=" * 80)
    print("基于字段类型的值生成测试")
    print("=" * 80)
    
    test_sql = """UPDATE CPWC_CUSTOMER_REMARK SET REMARK=#{REMARK}, DESCRIPION=#{DESCRIPTION}, REMARK_MOBILES=#{PHONE}, REMARK_CORP_NAME=#{REMARKCORPNAME},UPDATE_TIME=#{UPDATETIME},TYPE=#{TYPE} WHERE USER_EUIFID=#{USERID} AND EXTERNAL_USERID=#{EXTERNALUSERID}"""
    
    # 创建参数到字段的映射
    param_to_column = {}
    
    for param in params:
        param_name = param['param']
        for col in metadata['columns']:
            col_name = col['name']
            
            # 精确匹配
            if col_name == param_name:
                param_to_column[param_name] = col
                break
            # 忽略大小写和下划线的匹配
            elif col_name.replace('_', '').lower() == param_name.replace('_', '').lower():
                param_to_column[param_name] = col
                break
            # 包含关系
            elif param_name in col_name or col_name in param_name:
                param_to_column[param_name] = col
                break
    
    # 显示映射结果
    print("参数到字段的映射结果:")
    for param_name, column in param_to_column.items():
        print(f"  #{param_name} -> {column['name']} ({column['type']})")
    
    # 基于字段类型生成值
    print()
    print("基于字段类型生成的值:")
    
    replaced_sql = test_sql
    for param in params:
        param_name = param['param']
        
        if param_name in param_to_column:
            column = param_to_column[param_name]
            db_type = column['type'].lower()
            
            if 'int' in db_type or 'decimal' in db_type or 'float' in db_type or 'double' in db_type:
                # 数字类型
                replaced_value = "123"
                print(f"  #{param_name}: 数字类型 -> {replaced_value}")
            elif 'date' in db_type or 'time' in db_type:
                # 时间类型
                replaced_value = "'2025-01-01 00:00:00'"
                print(f"  #{param_name}: 时间类型 -> {replaced_value}")
            elif 'char' in db_type or 'text' in db_type or 'varchar' in db_type:
                # 字符串类型
                max_len = column.get('max_length', 50)
                # 生成合适长度的字符串
                if max_len and max_len < 20:
                    replaced_value = f"'test'"
                elif max_len and max_len < 100:
                    replaced_value = f"'test_value'"
                else:
                    replaced_value = f"'test_long_value_for_field_{param_name}'"
                print(f"  #{param_name}: 字符串类型 (max={max_len}) -> {replaced_value}")
            else:
                # 默认字符串
                replaced_value = "'test_value'"
                print(f"  #{param_name}: 其他类型 -> {replaced_value}")
        else:
            # 没有匹配到字段，使用默认值
            param_type = param['type']
            if param_type == 'datetime':
                replaced_value = "'2025-01-01 00:00:00'"
            elif param_type == 'number':
                replaced_value = "123"
            else:
                replaced_value = "'test_value'"
            print(f"  #{param_name}: 未匹配到字段，使用猜测类型 {param_type} -> {replaced_value}")
        
        # 替换参数
        param_pattern = f"#{{{param_name}}}"
        replaced_sql = replaced_sql.replace(param_pattern, replaced_value)
    
    print()
    print("生成的SQL:")
    print(replaced_sql)

def main():
    """主函数"""
    print("基于表元数据的SQL参数替换优化")
    print("=" * 80)
    
    metadata, params = test_metadata_based_type_detection()
    test_better_value_generation(metadata, params)
    
    print()
    print("=" * 80)
    print("总结:")
    print("1. 当前系统只能基于参数名猜测类型，不够准确")
    print("2. 通过表元数据可以获取字段的实际类型")
    print("3. 需要建立参数名与字段名的映射关系")
    print("4. 基于实际字段类型可以生成更合适的测试值")

if __name__ == '__main__':
    main()
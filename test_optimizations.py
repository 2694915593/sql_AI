#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试优化功能
1. DataValueFetcher - 从数据库中获取真实数据值替换参数
2. DynamicSQLParser - 处理包含XML标签的动态SQL
"""

import os
import sys
import logging
from datetime import datetime

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from sql_ai_analyzer.config.config_manager import ConfigManager
from sql_ai_analyzer.data_collector.data_value_fetcher import DataValueFetcher
from sql_ai_analyzer.data_collector.dynamic_sql_parser import DynamicSQLParser


def setup_logging():
    """设置日志"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('test_optimizations.log')
        ]
    )
    return logging.getLogger(__name__)


def test_data_value_fetcher(logger):
    """测试数据值获取器"""
    logger.info("=" * 50)
    logger.info("测试数据值获取器 (DataValueFetcher)")
    logger.info("=" * 50)
    
    try:
        # 初始化配置管理器
        config_manager = ConfigManager()
        logger.info("配置管理器初始化成功")
        
        # 初始化数据值获取器
        data_fetcher = DataValueFetcher(config_manager, logger)
        logger.info("数据值获取器初始化成功")
        
        # 测试1：获取数据库连接管理器
        db_alias = "ECUP"
        db_manager = data_fetcher.get_db_manager(db_alias)
        if db_manager:
            logger.info(f"成功获取数据库连接管理器: {db_alias}")
        else:
            logger.warning(f"无法获取数据库连接管理器: {db_alias}")
        
        # 测试2：测试获取列值（需要实际的表名和列名）
        # 这里使用示例数据
        test_tables = [
            {
                'table_name': 'users',
                'columns': [
                    {'name': 'id', 'type': 'int'},
                    {'name': 'username', 'type': 'varchar(50)'},
                    {'name': 'email', 'type': 'varchar(100)'},
                    {'name': 'created_at', 'type': 'datetime'},
                    {'name': 'is_active', 'type': 'boolean'}
                ]
            },
            {
                'table_name': 'orders',
                'columns': [
                    {'name': 'order_id', 'type': 'int'},
                    {'name': 'user_id', 'type': 'int'},
                    {'name': 'amount', 'type': 'decimal(10,2)'},
                    {'name': 'order_date', 'type': 'date'},
                    {'name': 'status', 'type': 'varchar(20)'}
                ]
            }
        ]
        
        logger.info("测试智能匹配列功能...")
        for table in test_tables:
            table_name = table['table_name']
            for column in table['columns'][:2]:  # 只测试前两个列
                column_name = column['name']
                column_type = column['type']
                
                # 测试匹配列
                matched = data_fetcher.find_matching_column(
                    db_alias, table_name, column_name, test_tables
                )
                
                if matched:
                    matched_table, matched_column, column_info = matched
                    logger.info(f"参数 '{column_name}' 匹配到表 '{matched_table}' 的列 '{matched_column}'")
                    
                    # 测试获取替换值
                    replacement_value = data_fetcher.get_replacement_value(
                        db_alias, matched_table, matched_column, column_info['type']
                    )
                    logger.info(f"  替换值: {replacement_value}")
                else:
                    logger.warning(f"参数 '{column_name}' 未找到匹配的列")
        
        logger.info("数据值获取器测试完成")
        return True
        
    except Exception as e:
        logger.error(f"测试数据值获取器时发生错误: {str(e)}", exc_info=True)
        return False


def test_dynamic_sql_parser(logger):
    """测试动态SQL解析器"""
    logger.info("\n" + "=" * 50)
    logger.info("测试动态SQL解析器 (DynamicSQLParser)")
    logger.info("=" * 50)
    
    try:
        # 初始化配置管理器
        config_manager = ConfigManager()
        logger.info("配置管理器初始化成功")
        
        # 初始化动态SQL解析器
        dynamic_parser = DynamicSQLParser(config_manager, logger)
        logger.info("动态SQL解析器初始化成功")
        
        # 测试用例：各种动态SQL
        test_cases = [
            {
                'name': 'MyBatis SELECT with <if>',
                'sql': '''
                    <select id="findUsers" resultType="User">
                        SELECT * FROM users
                        <where>
                            <if test="username != null and username != ''">
                                AND username = #{username}
                            </if>
                            <if test="email != null and email != ''">
                                AND email = #{email}
                            </if>
                            <if test="isActive != null">
                                AND is_active = #{isActive}
                            </if>
                        </where>
                        ORDER BY created_at DESC
                    </select>
                '''
            },
            {
                'name': 'MyBatis INSERT with dynamic fields',
                'sql': '''
                    <insert id="insertUser" parameterType="User">
                        INSERT INTO users
                        <trim prefix="(" suffix=")" suffixOverrides=",">
                            <if test="username != null">username,</if>
                            <if test="email != null">email,</if>
                            <if test="password != null">password,</if>
                            <if test="isActive != null">is_active,</if>
                            created_at
                        </trim>
                        <trim prefix="VALUES (" suffix=")" suffixOverrides=",">
                            <if test="username != null">#{username},</if>
                            <if test="email != null">#{email},</if>
                            <if test="password != null">#{password},</if>
                            <if test="isActive != null">#{isActive},</if>
                            NOW()
                        </trim>
                    </insert>
                '''
            },
            {
                'name': 'MyBatis UPDATE with <set>',
                'sql': '''
                    <update id="updateUser" parameterType="User">
                        UPDATE users
                        <set>
                            <if test="username != null">username = #{username},</if>
                            <if test="email != null">email = #{email},</if>
                            <if test="password != null">password = #{password},</if>
                            <if test="isActive != null">is_active = #{isActive},</if>
                            updated_at = NOW()
                        </set>
                        WHERE id = #{id}
                    </update>
                '''
            },
            {
                'name': 'MyBatis <choose> with <when>',
                'sql': '''
                    <select id="findUsersByStatus" resultType="User">
                        SELECT * FROM users
                        WHERE
                        <choose>
                            <when test="status == 'active'">
                                is_active = 1
                            </when>
                            <when test="status == 'inactive'">
                                is_active = 0
                            </when>
                            <otherwise>
                                is_active IS NOT NULL
                            </otherwise>
                        </choose>
                    </select>
                '''
            },
            {
                'name': 'Simple SQL without dynamic tags',
                'sql': 'SELECT * FROM users WHERE id = #{id} AND status = #{status}'
            }
        ]
        
        # 测试表元数据
        table_metadata = [
            {
                'table_name': 'users',
                'columns': [
                    {'name': 'id', 'type': 'int'},
                    {'name': 'username', 'type': 'varchar(50)'},
                    {'name': 'email', 'type': 'varchar(100)'},
                    {'name': 'password', 'type': 'varchar(100)'},
                    {'name': 'is_active', 'type': 'boolean'},
                    {'name': 'created_at', 'type': 'datetime'},
                    {'name': 'updated_at', 'type': 'datetime'}
                ]
            }
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            logger.info(f"\n测试用例 {i}: {test_case['name']}")
            logger.info(f"原始SQL:\n{test_case['sql'][:200]}...")
            
            # 测试是否是动态SQL
            is_dynamic = dynamic_parser.is_dynamic_sql(test_case['sql'])
            logger.info(f"是否是动态SQL: {is_dynamic}")
            
            if is_dynamic:
                # 测试解析动态SQL
                scenarios = dynamic_parser.parse_dynamic_sql(
                    test_case['sql'], 
                    table_metadata,
                    'ECUP'
                )
                
                if scenarios:
                    logger.info(f"解析成功，生成 {len(scenarios)} 个场景")
                    
                    # 显示最佳场景
                    best_scenario = dynamic_parser.get_best_scenario(scenarios)
                    if best_scenario:
                        logger.info(f"最佳场景 (置信度: {best_scenario['confidence']}):")
                        logger.info(f"  名称: {best_scenario['name']}")
                        logger.info(f"  描述: {best_scenario['description']}")
                        logger.info(f"  SQL: {best_scenario['sql'][:150]}...")
                        logger.info(f"  参数数量: {len(best_scenario['parameters'])}")
                    
                    # 显示所有场景
                    for j, scenario in enumerate(scenarios[:3], 1):  # 只显示前3个
                        logger.info(f"  场景{j}: {scenario['name']} (置信度: {scenario['confidence']})")
                else:
                    logger.warning("解析失败，未生成任何场景")
            else:
                logger.info("不是动态SQL，无需解析")
        
        logger.info("\n动态SQL解析器测试完成")
        return True
        
    except Exception as e:
        logger.error(f"测试动态SQL解析器时发生错误: {str(e)}", exc_info=True)
        return False


def test_integrated_workflow(logger):
    """测试集成工作流"""
    logger.info("\n" + "=" * 50)
    logger.info("测试集成工作流")
    logger.info("=" * 50)
    
    try:
        # 初始化配置管理器
        config_manager = ConfigManager()
        
        # 测试动态SQL解析和数据值获取的集成
        dynamic_sql = '''
            <select id="findActiveUsers" resultType="User">
                SELECT * FROM users
                <where>
                    <if test="minCreatedDate != null">
                        AND created_at >= #{minCreatedDate}
                    </if>
                    <if test="status != null">
                        AND status = #{status}
                    </if>
                    AND is_active = #{isActive}
                </where>
                ORDER BY created_at DESC
                LIMIT #{limit}
            </select>
        '''
        
        # 初始化解析器
        dynamic_parser = DynamicSQLParser(config_manager, logger)
        
        if dynamic_parser.is_dynamic_sql(dynamic_sql):
            logger.info("检测到动态SQL，开始解析...")
            
            # 表元数据
            table_metadata = [
                {
                    'table_name': 'users',
                    'columns': [
                        {'name': 'id', 'type': 'int'},
                        {'name': 'username', 'type': 'varchar(50)'},
                        {'name': 'email', 'type': 'varchar(100)'},
                        {'name': 'status', 'type': 'varchar(20)'},
                        {'name': 'is_active', 'type': 'boolean'},
                        {'name': 'created_at', 'type': 'datetime'}
                    ]
                }
            ]
            
            # 解析动态SQL
            scenarios = dynamic_parser.parse_dynamic_sql(
                dynamic_sql, 
                table_metadata,
                'ECUP'
            )
            
            if scenarios:
                best_scenario = dynamic_parser.get_best_scenario(scenarios)
                if best_scenario:
                    logger.info(f"解析得到的最佳SQL:")
                    logger.info(f"{best_scenario['sql']}")
                    
                    # 现在可以使用DataValueFetcher来获取真实数据值
                    # 这里只是演示，实际应用中会将解析得到的标准SQL传递给ParamExtractor
                    logger.info("如果需要，可以将此SQL传递给ParamExtractor进行参数替换")
        
        logger.info("集成工作流测试完成")
        return True
        
    except Exception as e:
        logger.error(f"测试集成工作流时发生错误: {str(e)}", exc_info=True)
        return False


def main():
    """主函数"""
    logger = setup_logging()
    
    logger.info(f"开始测试优化功能 - {datetime.now()}")
    logger.info("项目根目录: %s", project_root)
    
    # 运行测试
    results = []
    
    # 测试数据值获取器
    results.append(('数据值获取器', test_data_value_fetcher(logger)))
    
    # 测试动态SQL解析器
    results.append(('动态SQL解析器', test_dynamic_sql_parser(logger)))
    
    # 测试集成工作流
    results.append(('集成工作流', test_integrated_workflow(logger)))
    
    # 总结结果
    logger.info("\n" + "=" * 50)
    logger.info("测试总结")
    logger.info("=" * 50)
    
    total_tests = len(results)
    passed_tests = sum(1 for _, passed in results if passed)
    
    for test_name, passed in results:
        status = "✓ 通过" if passed else "✗ 失败"
        logger.info(f"{status} - {test_name}")
    
    logger.info(f"\n总计: {passed_tests}/{total_tests} 项测试通过")
    
    if passed_tests == total_tests:
        logger.info("所有优化功能测试通过！")
        return 0
    else:
        logger.warning(f"有 {total_tests - passed_tests} 项测试失败")
        return 1


if __name__ == '__main__':
    sys.exit(main())
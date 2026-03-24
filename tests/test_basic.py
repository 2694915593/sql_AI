#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基础测试用例
测试AI-SQL质量分析系统的基本功能
"""

import unittest
import os
import sys
from unittest.mock import Mock, patch, MagicMock

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.config_manager import ConfigManager
from data_collector.sql_extractor import SQLExtractor
from data_collector.metadata_collector import MetadataCollector
from ai_integration.model_client import ModelClient
from storage.result_processor import ResultProcessor


class TestConfigManager(unittest.TestCase):
    """测试配置管理器"""
    
    def setUp(self):
        """测试前准备"""
        # 创建临时配置文件
        self.test_config_content = """
[database]
source_host = localhost
source_port = 3306
source_database = test_db
source_username = test_user
source_password = test_pass
source_db_type = mysql

[db_test]
host = test_host
port = 3306
database = test_target_db
username = test_user
password = test_pass
db_type = mysql

[ai_model]
api_url = http://test-api.com/analyze
api_key = test_key
timeout = 30
max_retries = 3
"""
        
        self.config_file = 'test_config.ini'
        with open(self.config_file, 'w', encoding='utf-8') as f:
            f.write(self.test_config_content)
    
    def tearDown(self):
        """测试后清理"""
        if os.path.exists(self.config_file):
            os.remove(self.config_file)
    
    def test_config_loading(self):
        """测试配置加载"""
        config = ConfigManager(self.config_file)
        
        # 测试数据库配置
        db_config = config.get_database_config()
        self.assertEqual(db_config['host'], 'localhost')
        self.assertEqual(db_config['database'], 'test_db')
        self.assertEqual(db_config['db_type'], 'mysql')
        
        # 测试目标数据库配置
        target_config = config.get_target_db_config('db_test')
        self.assertEqual(target_config['host'], 'test_host')
        self.assertEqual(target_config['database'], 'test_target_db')
        
        # 测试AI模型配置
        ai_config = config.get_ai_model_config()
        self.assertEqual(ai_config['api_url'], 'http://test-api.com/analyze')
        self.assertEqual(ai_config['api_key'], 'test_key')
        self.assertEqual(ai_config['timeout'], 30)
    
    def test_missing_config(self):
        """测试缺失配置"""
        # 创建缺少必要段的配置文件
        bad_config_content = """
[database]
source_host = localhost
"""
        
        bad_config_file = 'bad_config.ini'
        with open(bad_config_file, 'w', encoding='utf-8') as f:
            f.write(bad_config_content)
        
        with self.assertRaises(ValueError):
            ConfigManager(bad_config_file)
        
        os.remove(bad_config_file)


class TestSQLExtractor(unittest.TestCase):
    """测试SQL提取器"""
    
    def setUp(self):
        """测试前准备"""
        self.mock_config = Mock()
        self.mock_config.get_database_config.return_value = {
            'host': 'localhost',
            'port': 3306,
            'database': 'test_db',
            'username': 'test_user',
            'password': 'test_pass',
            'db_type': 'mysql'
        }
        
        self.mock_logger = Mock()
    
    @patch('data_collector.sql_extractor.DatabaseManager')
    def test_extract_table_names(self, mock_db_manager):
        """测试表名提取"""
        extractor = SQLExtractor(self.mock_config, self.mock_logger)
        
        # 测试简单SELECT语句
        sql = "SELECT * FROM users WHERE id = 1"
        tables = extractor.extract_table_names(sql)
        self.assertIn('users', tables)
        
        # 测试JOIN语句
        sql = "SELECT u.name, o.amount FROM users u JOIN orders o ON u.id = o.user_id"
        tables = extractor.extract_table_names(sql)
        self.assertIn('users', tables)
        self.assertIn('orders', tables)
        
        # 测试INSERT语句
        sql = "INSERT INTO products (name, price) VALUES ('test', 100)"
        tables = extractor.extract_table_names(sql)
        self.assertIn('products', tables)
        
        # 测试UPDATE语句
        sql = "UPDATE products SET price = 200 WHERE id = 1"
        tables = extractor.extract_table_names(sql)
        self.assertIn('products', tables)
        
        # 测试DELETE语句
        sql = "DELETE FROM temp_logs WHERE created_at < '2024-01-01'"
        tables = extractor.extract_table_names(sql)
        self.assertIn('temp_logs', tables)
    
    def test_clean_table_names(self):
        """测试表名清理"""
        extractor = SQLExtractor(self.mock_config, self.mock_logger)
        
        # 测试带数据库前缀的表名
        tables = ['db.users', 'orders', '`logs`', "'temp'", '  spaces  ']
        cleaned = extractor._clean_table_names(tables)
        
        self.assertEqual(len(cleaned), 4)  # 去重后
        self.assertIn('users', cleaned)
        self.assertIn('orders', cleaned)
        self.assertIn('logs', cleaned)
        self.assertIn('temp', cleaned)
        
        # 测试空表名
        tables = ['', None, 'valid_table']
        cleaned = extractor._clean_table_names(tables)
        self.assertEqual(cleaned, ['valid_table'])


class TestModelClient(unittest.TestCase):
    """测试大模型API客户端"""
    
    def setUp(self):
        """测试前准备"""
        self.mock_config = Mock()
        self.mock_config.get_ai_model_config.return_value = {
            'api_url': 'http://test-api.com/analyze',
            'api_key': 'test_key',
            'timeout': 30,
            'max_retries': 3
        }
        
        self.mock_logger = Mock()
    
    @patch('ai_integration.model_client.requests.post')
    def test_build_request_payload(self, mock_post):
        """测试请求负载构建"""
        client = ModelClient(self.mock_config, self.mock_logger)
        
        request_data = {
            'sql_statement': 'SELECT * FROM users',
            'tables': [
                {
                    'table_name': 'users',
                    'row_count': 1000,
                    'is_large_table': False,
                    'columns': [{'name': 'id', 'type': 'int'}],
                    'indexes': [{'name': 'idx_id', 'columns': ['id']}]
                }
            ],
            'db_alias': 'db_test'
        }
        
        payload = client._build_request_payload(request_data)
        
        self.assertEqual(payload['sql_statement'], 'SELECT * FROM users')
        self.assertEqual(payload['db_alias'], 'db_test')
        self.assertEqual(len(payload['tables']), 1)
        self.assertEqual(payload['tables'][0]['table_name'], 'users')
        self.assertIn('table_statistics', payload)
        self.assertIn('analysis_types', payload)
    
    def test_extract_suggestions(self):
        """测试建议提取"""
        client = ModelClient(self.mock_config, self.mock_logger)
        
        # 测试包含建议的响应
        analysis_result = {
            'optimization_suggestions': ['建议1', '建议2'],
            'suggestions': ['建议3'],
            'other_field': 'value'
        }
        
        suggestions = client._extract_suggestions(analysis_result)
        self.assertEqual(len(suggestions), 3)
        self.assertIn('建议1', suggestions)
        self.assertIn('建议2', suggestions)
        self.assertIn('建议3', suggestions)
        
        # 测试去重
        analysis_result = {
            'suggestions': ['重复建议', '重复建议', '不同建议']
        }
        
        suggestions = client._extract_suggestions(analysis_result)
        self.assertEqual(len(suggestions), 2)
    
    def test_calculate_score(self):
        """测试评分计算"""
        client = ModelClient(self.mock_config, self.mock_logger)
        
        # 测试有评分的情况
        analysis_result = {'score': 8.5}
        score = client._calculate_score(analysis_result)
        self.assertEqual(score, 8.5)
        
        # 测试有质量评分的情况
        analysis_result = {'quality_score': 7.5}
        score = client._calculate_score(analysis_result)
        self.assertEqual(score, 7.5)
        
        # 测试根据建议计算评分
        analysis_result = {
            'suggestions': ['性能优化建议', '严重错误需要修复']
        }
        score = client._calculate_score(analysis_result)
        self.assertLess(score, 10.0)  # 应该有扣分
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 10.0)


class TestResultProcessor(unittest.TestCase):
    """测试结果处理器"""
    
    def setUp(self):
        """测试前准备"""
        self.mock_config = Mock()
        self.mock_logger = Mock()
        
        # 创建模拟的SQL提取器
        self.mock_sql_extractor = Mock()
        self.mock_sql_extractor.update_analysis_status.return_value = True
        self.mock_sql_extractor.source_db = Mock()
        self.mock_sql_extractor.source_db.execute.return_value = 1
    
    @patch('storage.result_processor.SQLExtractor')
    def test_prepare_storage_data(self, mock_sql_extractor_class):
        """测试存储数据准备"""
        mock_sql_extractor_class.return_value = self.mock_sql_extractor
        
        processor = ResultProcessor(self.mock_config, self.mock_logger)
        
        analysis_result = {
            'success': True,
            'analysis_result': {'detail': 'test'},
            'suggestions': ['建议1', '建议2'],
            'score': 8.5
        }
        
        metadata = [
            {
                'table_name': 'users',
                'row_count': 1000,
                'is_large_table': False,
                'columns': [{'name': 'id'}],
                'indexes': [{'name': 'idx_id'}],
                'primary_keys': ['id']
            }
        ]
        
        storage_data = processor._prepare_storage_data(analysis_result, metadata)
        
        self.assertEqual(storage_data['analysis_summary']['score'], 8.5)
        self.assertEqual(storage_data['analysis_summary']['suggestion_count'], 2)
        self.assertIn('detailed_analysis', storage_data)
        self.assertIn('suggestions', storage_data)
        self.assertIn('metadata_summary', storage_data)
        self.assertIn('categorized_suggestions', storage_data)
        
        # 测试元数据摘要
        metadata_summary = storage_data['metadata_summary']
        self.assertEqual(metadata_summary['table_count'], 1)
        self.assertEqual(metadata_summary['total_rows'], 1000)
        self.assertEqual(metadata_summary['large_tables'], 0)
        self.assertEqual(metadata_summary['total_columns'], 1)
        self.assertEqual(metadata_summary['total_indexes'], 1)
    
    def test_categorize_suggestions(self):
        """测试建议分类"""
        processor = ResultProcessor(self.mock_config, self.mock_logger)
        
        suggestions = [
            '性能优化建议：添加索引',
            '安全警告：SQL注入风险',
            '可维护性：添加注释',
            '逻辑错误：条件判断有问题',
            '其他建议'
        ]
        
        categorized = processor._categorize_suggestions(suggestions)
        
        # 检查分类结果
        self.assertIn('performance', categorized)
        self.assertIn('security', categorized)
        self.assertIn('maintainability', categorized)
        self.assertIn('correctness', categorized)
        self.assertIn('other', categorized)
        
        # 检查分类是否正确
        self.assertGreater(len(categorized['performance']), 0)
        self.assertGreater(len(categorized['security']), 0)


if __name__ == '__main__':
    unittest.main()
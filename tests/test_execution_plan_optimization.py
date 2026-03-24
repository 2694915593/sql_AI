#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""执行计划优化相关单元测试"""

import os
import sys
import unittest
from unittest.mock import Mock

# 加入项目根路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_collector.metadata_collector import MetadataCollector


class TestExecutionPlanOptimization(unittest.TestCase):
    """验证执行计划优化逻辑"""

    def setUp(self):
        self.collector = MetadataCollector(config_manager=Mock(), logger=Mock())

    def test_normalize_sql_for_explain(self):
        sql = """
        /* header */
        SELECT  *  FROM  users
        WHERE id = 1; -- tail comment
        """
        normalized = self.collector._normalize_sql_for_explain(sql)
        self.assertEqual(normalized, "SELECT * FROM users WHERE id = 1")

    def test_is_explain_supported_sql(self):
        self.assertTrue(self.collector._is_explain_supported_sql("SELECT * FROM t"))
        self.assertTrue(self.collector._is_explain_supported_sql("WITH cte AS (SELECT 1) SELECT * FROM cte"))
        self.assertFalse(self.collector._is_explain_supported_sql("CREATE TABLE t(id INT)"))

    def test_summarize_execution_plan_mysql(self):
        mysql_plan = [
            {
                "id": 1,
                "select_type": "SIMPLE",
                "table": "users",
                "type": "ALL",
                "key": None,
                "rows": 1000,
                "Extra": "Using where; Using filesort"
            }
        ]
        summary = self.collector._summarize_execution_plan(mysql_plan, "mysql")

        self.assertTrue(summary["has_full_scan"])
        self.assertFalse(summary["key_used"])
        self.assertEqual(summary["estimated_rows"], 1000)
        self.assertIn("all", summary["access_types"])
        self.assertTrue(any("filesort" in w.lower() for w in summary["warnings"]))

    def test_summarize_execution_plan_non_mysql_default(self):
        summary = self.collector._summarize_execution_plan({"Plan": {}}, "postgresql")
        self.assertEqual(summary["estimated_rows"], 0)
        self.assertFalse(summary["has_full_scan"])


if __name__ == "__main__":
    unittest.main()

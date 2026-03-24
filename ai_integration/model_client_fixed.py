#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
大模型API客户端模块
负责调用大模型API进行SQL分析
"""

import json
import time
import requests
import re
from typing import Dict, Any, Optional, List
from utils.logger import LogMixin
from utils.sql_specifications import SQLType, SQLSpecificationsManager, RuleLevel
import ast


class ModelClient(LogMixin):
    """大模型API客户端"""
    
    def __init__(self, config_manager, logger=None):
        """
        初始化API客户端
        
        Args:
            config_manager: 配置管理器
            logger: 日志记录器
        """
        self.config_manager = config_manager
        
        if logger:
            self.set_logger(logger)
        
        # 获取AI模型配置
        self.ai_config = config_manager.get_ai_model_config()
        
        self.logger.info("大模型API客户端初始化完成")
    
    def analyze_sql(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        调用大模型API分析SQL
        
        Args:
            request_data: 请求数据
            
        Returns:
            分析结果
        """
        if not self.ai_config.get('api_url'):
            self.logger.error("未配置大模型API地址")
            return self._create_error_response("未配置大模型API地址")
        
        try:
            # 构建请求数据
            payload = self._build_request_payload(request_data)
            
            # 调用API
            response = self._call_api_with_retry(payload)
            
            # 解析响应
            result = self._parse_response(response)
            
            return result
            
        except Exception as e:
            self.logger.error(f"调用大模型API时发生错误: {str(e)}", exc_info=True)
            return self._create_error_response(str(e))
    
    def _detect_sql_type(self, sql_statement: str) -> SQLType:
        """
        检测SQL类型
        
        Args:
            sql_statement: SQL语句
            
        Returns:
            SQL类型
        """
        sql_upper = sql_statement.strip().upper()
        
        if sql_upper.startswith("SELECT"):
            return SQLType.SELECT
        elif sql_upper.startswith("INSERT"):
            return SQLType.INSERT
        elif sql_upper.startswith("UPDATE"):
            return SQLType.UPDATE
        elif sql_upper.startswith("DELETE"):
            return SQLType.DELETE
        elif sql_upper.startswith("CREATE"):
            return SQLType.CREATE
        elif sql_upper.startswith("ALTER"):
            return SQLType.ALTER
        elif sql_upper.startswith("DROP"):
            return SQLType.DROP
        elif sql_upper.startswith("TRUNCATE"):
            return SQLType.TRUNCATE
        else:
            return SQLType.OTHER
    
    def _build_request_payload(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        构建请求负载 - 优化版，关注关键角度
        
        Args:
            request_data: 原始请求数据
            
        Returns:
            构建好的请求负载
        """
        # 根据新的API格式，只需要一个prompt参数
        sql_statement = request_data.get('sql_statement', '')
        tables = request_data.get('tables', [])
        db_alias = request_data.get('db_alias', '')
        execution_plan = request_data.get('execution_plan', '')
        execution_plan_info = request_data.get('execution_plan_info', {})
        replaced_sql = request_data.get('replaced_sql', '')
        
        # 检测SQL类型
        sql_type = self._detect_sql_type(sql_statement)
        
        # 构建优化版prompt内容，聚焦关键角度
        prompt_parts = []
        
        # 1. SQL语句（必填）
        prompt_parts.append(f"SQL语句：\n{sql_statement}\n")

        # 1.1 动态SQL（参数替换后，如果有）
        if replaced_sql and replaced_sql != sql_statement:
            prompt_parts.append("动态SQL（参数替换后）：")
            prompt_parts.append(replaced_sql)
            prompt_parts.append("")
        
        # 2. 数据库信息（必填）
        prompt_parts.append(f"数据库：{db_alias}\n")
        
        # 3. 表信息（精简版，只保留关键信息）
        if tables:
            prompt_parts.append("涉及的表信息：")
            for i, table in enumerate(tables, 1):
                table_name = table.get('table_name', '未知表')
                row_count = table.get('row_count', 0)
                is_large_table = table.get('is_large_table', False)
                column_count = len(table.get('columns', []))
                index_count = len(table.get('indexes', []))
                has_primary_key = len(table.get('primary_keys', [])) > 0
                
                prompt_parts.append(f"\n表{i}：{table_name}")
                prompt_parts.append(f"  - 行数：{row_count}")
                prompt_parts.append(f"  - 是否大表：{'是' if is_large_table else '否'}")
                prompt_parts.append(f"  - 列数：{column_count}")
                prompt_parts.append(f"  - 索引数：{index_count}")
                prompt_parts.append(f"  - 是否有主键：{'是' if has_primary_key else '否'}")
                
                # 只检查关键列信息
                columns = table.get('columns', [])
                if columns:
                    # 检查是否有NOT NULL约束的列
                    not_null_columns = [col for col in columns if not col.get('nullable', True)]
                    if not_null_columns:
                        prompt_parts.append(f"  - 非空列：{', '.join([col.get('name', '') for col in not_null_columns[:5]])}")
        
        # 4. 执行计划分析（精简版）
        prompt_parts.append("\n执行计划分析：")
        if execution_plan:
            # 只取前500字符
            prompt_parts.append(execution_plan[:500] + ("..." if len(execution_plan) > 500 else ""))
        elif execution_plan_info and execution_plan_info.get('has_execution_plan'):
            plan_summary = execution_plan_info.get('plan_summary', {})
            if isinstance(plan_summary, dict) and plan_summary:
                prompt_parts.append("执行计划关键信息：")
                prompt_parts.append(f"- 是否全表扫描：{'是' if plan_summary.get('has_full_scan', False) else '否'}")
                prompt_parts.append(f"- 是否使用索引：{'是' if plan_summary.get('key_used', False) else '否'}")
                prompt_parts.append(f"- 预估扫描行数：{plan_summary.get('estimated_rows', 0)}")
        
        # 5. 关键分析角度（用户特别关注的方面）- 聚焦规范性评审
        prompt_parts.append("\n请重点关注以下关键规范性角度的分析：")
        critical_angles = [
            "1. 修改列时加属性：检查ALTER TABLE语句修改列时是否保留了原列的属性（如NOT NULL、DEFAULT、COMMENT等）",
            "2. in操作索引失效：检查IN操作是否导致索引失效（特别是IN列表值过多时）",
            "3. 字符集问题：检查字符集是否一致（表、字段、连接字符集），避免乱码和性能问题",
            "4. 注释--问题：检查SQL注释是否正确使用--格式（--后面必须有空格），避免注释错误解析",
            "5. comment问题：检查表和字段是否有合适的COMMENT注释，注释内容是否清晰明确",
            "6. 表参数问题：检查表参数设置是否合理（如ENGINE、CHARSET、COLLATE、ROW_FORMAT等）",
            "7. akm接入：检查AKM（访问密钥管理）相关配置和接入问题，确保敏感信息安全",
            "8. analyze问题：检查ANALYZE统计信息是否准确，是否需要手动更新统计信息",
            "9. dml与ddl之间休眠3秒：检查DDL操作后是否等待足够时间（建议3秒）再执行DML，避免锁冲突",
            "10. 隐式转换：检查SQL语句中是否存在隐式类型转换，可能导致性能问题或数据错误",
            "11. 主键问题：检查表是否有主键，主键设计是否合理（自增、业务主键等）",
            "12. 索引设计：检查索引设计是否合理（联合索引字段顺序、索引冗余、索引数量等）",
            "13. 全表扫描：检查SQL是否可能导致全表扫描，特别是大表的查询",
            "14. 表结构一致性：检查涉及的表结构是否一致（如字段类型、长度、默认值等）",
            "15. 唯一约束字段须添加not null：检查唯一索引字段是否都有NOT NULL约束，确保数据完整性"
        ]
        prompt_parts.extend(critical_angles)
        
        # 6. 相关SQL规范（只选择与关键角度相关的规范）
        prompt_parts.append("\n相关SQL规范（精简版）：")
        manager = SQLSpecificationsManager()
        relevant_rules = manager.get_specifications_by_sql_type(sql_type)
        
        # 过滤出与关键角度相关的规范
        critical_keywords = [
            '隐式转换', '主键', '全表扫描', '修改列', '字符集', '注释', 
            'comment', 'not null', '索引失效', 'analyze', '休眠', 'ddl', 'dml'
        ]
        
        filtered_rules = []
        for rule in relevant_rules:
            rule_content = rule.get('content', '').lower()
            # 检查规则是否包含任何关键角度关键词
            if any(keyword.lower() in rule_content for keyword in critical_keywords):
                filtered_rules.append(rule)
        
        # 最多显示10条相关规范
        for rule in filtered_rules[:10]:
            level_str = rule["level"].value if isinstance(rule["level"], RuleLevel) else rule["level"]
            # 简化规则内容，只保留核心
            simple_content = rule['content']
            if len(simple_content) > 100:
                simple_content = simple_content[:97] + '...'
            prompt_parts.append(f"规范{rule['id']} 【{level_str}】: {simple_content}")
        
        # 7. 分析要求和输出格式
        prompt_parts.append("\n分析要求：")
        prompt_parts.append("1. 基于以上15个关键规范性角度进行分析，优先识别这些问题")
        prompt_parts.append("2. 提供3-5条最关键的改进建议，重点关注规范性内容")
        prompt_parts.append("3. 给出综合评分（0-10分），评分主要基于规范性符合度")
        prompt_parts.append("4. 分析摘要要突出规范性问题的发现和解决方案")
        prompt_parts.append("5. 针对发现的规范性问题提供具体的SQL修改示例")
        
        prompt_parts.append("\n输出格式要求（必须严格遵循JSON格式）：")
        prompt_parts.append('''{
  "建议": ["具体建议1", "具体建议2", "具体建议3"],
  "SQL类型": "查询/更新/插入/删除/建表/修改表/其他",
  "分析摘要": "简明的分析摘要，突出关键规范性角度的问题",
  "综合评分": 0-10,
  "规范性评审": {
    "修改列时加属性": {"检查结果": "通过/未通过", "问题描述": "具体问题描述", "修改建议": "具体修改建议"},
    "in操作索引失效": {"检查结果": "通过/未通过", "问题描述": "具体问题描述", "修改建议": "具体修改建议"},
    "字符集问题": {"检查结果": "通过/未通过", "问题描述": "具体问题描述", "修改建议": "具体修改建议"},
    "注释--问题": {"检查结果": "通过/未通过", "问题描述": "具体问题描述", "修改建议": "具体修改建议"},
    "comment问题": {"检查结果": "通过/未通过", "问题描述": "具体问题描述", "修改建议": "具体修改建议"},
    "表参数问题": {"检查结果": "通过/未通过", "问题描述": "具体问题描述", "修改建议": "具体修改建议"},
    "akm接入": {"检查结果": "通过/未通过", "问题描述": "具体问题描述", "修改建议": "具体修改建议"},
    "analyze问题": {"检查结果": "通过/未通过", "问题描述": "具体问题描述", "修改建议": "具体修改建议"},
    "dml与ddl之间休眠3秒": {"检查结果": "通过/未通过", "问题描述": "具体问题描述", "修改建议": "具体修改建议"},
    "隐式转换": {"检查结果": "通过/未通过", "问题描述": "具体问题描述", "修改建议": "具体修改建议"},
    "主键问题": {"检查结果": "通过/未通过", "问题描述": "具体问题描述", "修改建议": "具体修改建议"},
    "索引设计": {"检查结果": "通过/未通过", "问题描述": "具体问题描述", "修改建议": "具体修改建议"},
    "全表扫描": {"检查结果": "通过/未通过", "问题描述": "具体问题描述", "修改建议": "具体修改建议"},
    "表结构一致性": {"检查结果": "通过/未通过", "问题描述": "具体问题描述", "修改建议": "具体修改建议"},
    "唯一约束字段须添加not null": {"检查结果": "通过/未通过", "问题描述": "具体问题描述", "修改建议": "具体修改建议"}
  },
  "修改建议SQL": ["具体修改后的SQL语句1", "具体修改后的SQL语句2", "具体修改后的SQL语句3"]
}''')
        
        prompt_parts.append("\n重要提示：")
        prompt_parts.append("1. 综合评分范围是0-10分，分数越高表示SQL质量越好，评分主要基于规范性符合度")
        prompt_parts.append("2. 建议和规范性评审要具体，不要泛泛而谈，针对15个关键角度逐一检查")
        prompt_parts.append("3. 重点关注用户指定的15个关键规范性角度，忽略传统的中高低风险分类")
        prompt_parts.append("4. 修改建议SQL必须是可执行的、语法正确的SQL语句，能够直接使用")
        prompt_parts.append("5. 分析摘要要简洁明了，突出主要规范性问题和优化建议")
        prompt_parts.append("\n注意：请只回复JSON格式的内容，不要包含任何解释性文字。")
        
        # 组合所有部分
        prompt = "\n".join(prompt_parts)

        # 记录prompt预览日志
        prompt_preview_head = prompt[:500]
        self.logger.info(
            "构建优化版prompt完成：长度=%s, 预览前500字符=\n%s",
            len(prompt),
            prompt_preview_head
        )
        
        # 新的API只需要prompt参数
        payload = {
            "prompt": prompt
        }
        
        self.logger.debug(f"构建优化请求负载: SQL长度={len(sql_statement)}, 表数量={len(tables)}, prompt长度={len(prompt)}")
        return payload
    
    def _generate_dynamic_sql_examples(self, sql_statement: str, tables: Optional[List[Dict[str, Any]]] = None) -> List[str]:
        """
        生成动态SQL示例用于判断SQL注入漏洞，使用用户真实数据
        
        Args:
            sql_statement: 原始SQL语句
            tables: 表信息列表（包含真实表名和字段名）
            
        Returns:
            动态SQL示例列表
        """
        examples = []
        
        # 分析SQL语句类型
        sql_lower = sql_statement.lower().strip()
        
        # 提取真实表名和字段名
        real_table_name = None
        real_columns = []
        
        if tables and len(tables) > 0:
            # 使用第一个表的真实信息
            first_table = tables[0]
            real_table_name = first_table.get('table_name', '')
            
            # 提取真实字段名
            columns = first_table.get('columns', [])
            for col in columns:
                col_name = col.get('name', '')
                if col_name and col_name not in real_columns:
                    real_columns.append(col_name)
            
            # 如果没有提取到字段，使用一些通用字段名
            if not real_columns:
                real_columns = ['id', 'name', 'value', 'created_at', 'updated_at']
        
        # 如果没有真实表名，使用提取的表名
        if not real_table_name:
            real_table_name = self._extract_table_name(sql_statement)
        
        # 如果没有真实字段，使用通用字段
        if not real_columns:
            real_columns = ['id', 'name', 'value', 'created_at', 'updated_at']
        
        # 使用真实表名和字段名生成示例
        table_name = real_table_name
        column1 = real_columns[0] if len(real_columns) > 0 else 'id'
        column2 = real_columns[1] if len(real_columns) > 1 else 'name'
        column3 = real_columns[2] if len(real_columns) > 2 else 'value'
        
        # 如果是SELECT语句
        if sql_lower.startswith('select'):
            examples.append(f"动态查询示例：SELECT * FROM {table_name} WHERE {column2} = '" + "${user_input}" + "'")
            examples.append(f"参数化查询示例：SELECT * FROM {table_name} WHERE {column2} = ?")
            examples.append(f"存储过程调用示例：EXEC sp_getData '" + "${user_input}" + "'")
            examples.append(f"ORDER BY注入示例：SELECT * FROM {table_name} ORDER BY " + "${column_name}")
            examples.append(f"UNION注入示例：SELECT * FROM {table_name} WHERE {column1} = " + "${id}" + " UNION SELECT 1,2,3 --")
        
        # 如果是INSERT语句
        elif sql_lower.startswith('insert'):
            examples.append(f"动态插入示例：INSERT INTO {table_name} ({column1}, {column2}) VALUES ('" + "${value1}" + "', '" + "${value2}" + "')")
            examples.append(f"参数化插入示例：INSERT INTO {table_name} ({column1}, {column2}) VALUES (?, ?)")
            examples.append(f"批量插入注入示例：INSERT INTO {table_name} VALUES ('" + "${value1}" + "', '" + "${value2}" + "'), ('" + "${value3}" + "', '" + "${value4}" + "')")
        
        # 如果是UPDATE语句
        elif sql_lower.startswith('update'):
            examples.append(f"动态更新示例：UPDATE {table_name} SET {column2} = '" + "${new_value}" + "' WHERE {column1} = '" + "${id}" + "'")
            examples.append(f"参数化更新示例：UPDATE {table_name} SET {column2} = ? WHERE {column1} = ?")
            examples.append(f"多条件更新注入示例：UPDATE {table_name} SET {column2} = '" + "${value1}" + "', {column3} = '" + "${value2}" + "' WHERE {column1} = " + "${id}")
        
        # 如果是DELETE语句
        elif sql_lower.startswith('delete'):
            examples.append(f"动态删除示例：DELETE FROM {table_name} WHERE {column2} = '" + "${value}" + "'")
            examples.append(f"参数化删除示例：DELETE FROM {table_name} WHERE {column2} = ?")
            examples.append(f"条件删除注入示例：DELETE FROM {table_name} WHERE {column1} IN (" + "${id_list}" + ")")
        
        # 通用示例（使用真实表名）
        examples.append(f"字符串拼接示例：SELECT * FROM {table_name} WHERE {column2} LIKE '%" + "${search_term}" + "%'")
        examples.append(f"数字类型注入示例：SELECT * FROM {table_name} WHERE {column1} = " + "${id}")
        examples.append(f"时间类型注入示例：SELECT * FROM {table_name} WHERE created_at > '" + "${start_time}" + "'")
        examples.append(f"布尔盲注示例：SELECT * FROM {table_name} WHERE {column1} = " + "${id}" + " AND 1=1 -- 正常")
        examples.append(f"时间盲注示例：SELECT * FROM {table_name} WHERE {column1} = " + "${id}" + " AND SLEEP(5) -- 延迟执行")
        examples.append(f"报错注入示例：SELECT * FROM {table_name} WHERE {column1} = " + "${id}" + " AND EXTRACTVALUE(1, CONCAT(0x7e, (SELECT @@version), 0x7e))")
        
        # 添加防护建议
        examples.append("\n防护建议：")
        examples.append("1. 使用参数化查询（Prepared Statements）")
        examples.append("2. 使用存储过程")
        examples.append("3. 输入验证和过滤")
        examples.append("4. 最小权限原则")
        examples.append("5. 使用ORM框架")
        
        return examples
    
    def _extract_table_name(self, sql_statement: str) -> str:
        """
        从SQL语句中提取表名（简化版本）
        
        Args:
            sql_statement: SQL语句
            
        Returns:
            提取的表名
        """
        sql_lower = sql_statement.lower().strip()
        
        # 简单提取表名逻辑
        if sql_lower.startswith('select'):
            # SELECT * FROM table_name
            parts = sql_lower.split('from')
            if len(parts) > 1:
                table_part = parts[1].strip().split()[0]
                return table_part.split(',')[0].strip()
        
        elif sql_lower.startswith('insert'):
            # INSERT INTO table_name
            parts = sql_lower.split('into')
            if len(parts) > 1:
                table_part = parts[1].strip().split()[0]
                return table_part.strip()
        
        elif sql_lower.startswith('update'):
            # UPDATE table_name
            parts = sql_lower.split('update')
            if len(parts) > 1:
                table_part = parts[1].strip().split()[0]
                return table_part.strip()
        
        elif sql_lower.startswith('delete'):
            # DELETE FROM table_name
            parts = sql_lower.split('from')
            if len(parts) > 1:
                table_part = parts[1].strip().split()[0]
                return table_part.strip()
        
        # 默认返回通用表名
        return "users"
    
    def _generate_execution_plan(self, sql_statement: str, tables: List[Dict[str, Any]]) -> str:
        """
        生成SQL执行计划分析
        
        Args:
            sql_statement: SQL语句
            tables: 表信息列表
            
        Returns:
            执行计划分析文本
        """
        plan_parts = []
        
        # 分析SQL类型
        sql_lower = sql_statement.lower().strip()
        
        plan_parts.append("SQL执行计划分析：")
        plan_parts.append("=" * 50)
        
        # 1. SQL类型分析
        plan_parts.append("\n1. SQL类型分析：")
        if sql_lower.startswith('select'):
            plan_parts.append("   • 类型：查询语句 (SELECT)")
            plan_parts.append("   • 操作：数据读取")
            plan_parts.append("   • 性能关注点：查询优化、索引使用")
        elif sql_lower.startswith('insert'):
            plan_parts.append("   • 类型：插入语句 (INSERT)")
            plan_parts.append("   • 操作：数据写入")
            plan_parts.append("   • 性能关注点：写入速度、锁竞争")
        elif sql_lower.startswith('update'):
            plan_parts.append("   • 类型：更新语句 (UPDATE)")
            plan_parts.append("   • 操作：数据修改")
            plan_parts.append("   • 性能关注点：行锁、索引维护")
        elif sql_lower.startswith('delete'):
            plan_parts.append("   • 类型：删除语句 (DELETE)")
            plan_parts.append("   • 操作：数据删除")
            plan_parts.append("   • 性能关注点：事务日志、索引维护")
        elif sql_lower.startswith('create'):
            plan_parts.append("   • 类型：建表语句 (CREATE)")
            plan_parts.append("   • 操作：结构创建")
            plan_parts.append("   • 性能关注点：表设计、索引规划")
        elif sql_lower.startswith('alter'):
            plan_parts.append("   • 类型：表结构变更 (ALTER)")
            plan_parts.append("   • 操作：结构修改")
            plan_parts.append("   • 性能关注点：锁表时间、数据迁移")
        else:
            plan_parts.append("   • 类型：其他SQL语句")
            plan_parts.append("   • 操作：未知")
            plan_parts.append("   • 性能关注点：需要具体分析")
        
        # 2. 表信息分析
        plan_parts.append("\n2. 涉及表分析：")
        if tables:
            for i, table in enumerate(tables, 1):
                table_name = table.get('table_name', '未知表')
                row_count = table.get('row_count', 0)
                is_large_table = table.get('is_large_table', False)
                column_count = len(table.get('columns', []))
                index_count = len(table.get('indexes', []))
                
                plan_parts.append(f"\n   表{i}：{table_name}")
                plan_parts.append(f"     • 数据量：{row_count} 行")
                plan_parts.append(f"     • 是否大表：{'是' if is_large_table else '否'}")
                plan_parts.append(f"     • 列数：{column_count}")
                plan_parts.append(f"     • 索引数：{index_count}")
                
                # 索引分析
                indexes = table.get('indexes', [])
                if indexes:
                    plan_parts.append(f"     • 索引详情：")
                    for idx in indexes[:3]:  # 只显示前3个索引
                        idx_name = idx.get('name', '未知索引')
                        idx_columns = ', '.join(idx.get('columns', []))
                        idx_type = idx.get('type', '未知类型')
                        idx_unique = idx.get('unique', False)
                        unique_str = '唯一' if idx_unique else '非唯一'
                        plan_parts.append(f"       - {idx_name}: {idx_columns} ({idx_type}, {unique_str})")
                    if len(indexes) > 3:
                        plan_parts.append(f"       - ... 还有{len(indexes)-3}个索引")
                else:
                    plan_parts.append(f"     • 索引：无索引（全表扫描风险）")
        else:
            plan_parts.append("   未提供表信息，无法进行详细分析")
        
        # 3. 执行计划预测
        plan_parts.append("\n3. 执行计划预测：")
        
        # 基于SQL类型的预测
        if sql_lower.startswith('select'):
            if tables and any(table.get('indexes') for table in tables):
                plan_parts.append("   • 预测：可能使用索引扫描")
                plan_parts.append("   • 建议：检查WHERE条件是否匹配索引")
            else:
                plan_parts.append("   • 预测：可能进行全表扫描")
                plan_parts.append("   • 建议：考虑添加合适的索引")
            
            # 检查是否有JOIN
            if 'join' in sql_lower:
                plan_parts.append("   • 包含JOIN操作：注意连接顺序和连接类型")
            
            # 检查是否有子查询
            if '(' in sql_lower and 'select' in sql_lower[sql_lower.find('('):]:
                plan_parts.append("   • 包含子查询：注意子查询性能")
        
        elif sql_lower.startswith('insert'):
            plan_parts.append("   • 预测：单行插入，性能较好")
            plan_parts.append("   • 建议：批量插入时考虑使用事务")
        
        elif sql_lower.startswith('update') or sql_lower.startswith('delete'):
            plan_parts.append("   • 预测：需要行级锁")
            plan_parts.append("   • 建议：注意锁竞争和事务大小")
            
            # 检查是否有WHERE条件
            if 'where' in sql_lower:
                plan_parts.append("   • 包含WHERE条件：注意条件选择性")
            else:
                plan_parts.append("   • 警告：无WHERE条件，可能影响全表")
        
        # 4. 性能优化建议
        plan_parts.append("\n4. 性能优化建议：")
        
        # 通用建议
        plan_parts.append("   • 确保WHERE条件使用索引")
        plan_parts.append("   • 避免SELECT *，只选择需要的列")
        plan_parts.append("   • 考虑查询结果集大小")
        plan_parts.append("   • 注意JOIN操作的性能")
        plan_parts.append("   • 考虑使用EXPLAIN分析实际执行计划")
        
        # 基于表大小的建议
        if tables:
            for table in tables:
                row_count = table.get('row_count', 0)
                if row_count > 1000000:  # 百万级以上
                    plan_parts.append(f"   • 表{table.get('table_name')}数据量较大({row_count}行)，建议分区或分表")
                elif row_count > 100000:  # 十万级以上
                    plan_parts.append(f"   • 表{table.get('table_name')}数据量中等({row_count}行)，注意索引设计")
        
        # 5. 风险评估
        plan_parts.append("\n5. 执行风险评估：")
        
        risk_factors = []
        
        # 检查风险因素
        if sql_lower.startswith('delete') and 'where' not in sql_lower:
            risk_factors.append("无WHERE条件的DELETE语句（可能删除全表数据）")
        
        if sql_lower.startswith('update') and 'where' not in sql_lower:
            risk_factors.append("无WHERE条件的UPDATE语句（可能更新全表数据）")
        
        if any(table.get('row_count', 0) > 1000000 for table in tables):
            risk_factors.append("涉及大数据量表操作")
        
        if 'join' in sql_lower and len(tables) > 3:
            risk_factors.append("多表JOIN操作复杂度高")
        
        if risk_factors:
            for risk in risk_factors:
                plan_parts.append(f"   • ⚠️ 风险：{risk}")
        else:
            plan_parts.append("   • ✅ 风险较低")
        
        plan_parts.append("\n" + "=" * 50)
        plan_parts.append("注意：以上为基于元数据的预测分析，实际执行计划需通过EXPLAIN命令获取")
        
        return "\n".join(plan_parts)
    
    def _call_api_with_retry(self, payload: Dict[str, Any]) -> requests.Response:
        """
        带重试机制的API调用
        
        Args:
            payload: 请求负载
            
        Returns:
            API响应
        """
        max_retries = self.ai_config.get('max_retries', 3)
        timeout = self.ai_config.get('timeout', 30)
        api_url = self.ai_config.get('api_url', '')
        api_key = self.ai_config.get('api_key', '')
        
        # 使用 x-www-form-urlencoded 格式，但发送可读的文本（不进行URL编码）
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8',
            'Accept': 'application/json'
        }
        
        if api_key:
            headers['Authorization'] = f'Bearer {api_key}'
        
        last_exception = None
        
        for attempt in range(max_retries):
            try:
                self.logger.info(f"调用大模型API (尝试 {attempt + 1}/{max_retries})")
                
                # 提取prompt内容
                prompt_content = payload.get('prompt', '')
                
                # 直接发送可读的文本，不进行URL编码
                # 格式: prompt=可读的文本内容
                data = f'prompt={prompt_content}'
                
                # 记录发送的数据（前200字符用于调试）
                debug_prompt = prompt_content[:200] + "..." if len(prompt_content) > 200 else prompt_content
                self.logger.debug(f"发送的prompt内容（前200字符）: {debug_prompt}")
                self.logger.debug(f"数据长度: {len(data)} 字符")
                self.logger.debug(f"数据前200字符: {data[:200]}...")
                
                response = requests.post(
                    api_url,
                    headers=headers,
                    data=data.encode('utf-8'),  # 显式使用utf-8编码
                    timeout=timeout
                )
                
                # 检查响应状态
                if response.status_code == 200:
                    self.logger.info(f"API调用成功，状态码: {response.status_code}")
                    return response
                else:
                    self.logger.warning(f"API调用返回非200状态码: {response.status_code}, 响应: {response.text[:200]}")
                    
                    # 如果是服务器错误，重试
                    if 500 <= response.status_code < 600:
                        last_exception = Exception(f"服务器错误: {response.status_code}")
                        if attempt < max_retries - 1:
                            time.sleep(2 ** attempt)  # 指数退避
                            continue
                    else:
                        # 客户端错误，不重试
                        raise Exception(f"API调用失败: {response.status_code} - {response.text[:200]}")
            
            except requests.exceptions.Timeout:
                self.logger.warning(f"API调用超时 (尝试 {attempt + 1}/{max_retries})")
                last_exception = Exception("请求超时")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
            
            except requests.exceptions.ConnectionError:
                self.logger.warning(f"API连接错误 (尝试 {attempt + 1}/{max_retries})")
                last_exception = Exception("连接错误")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
            
            except Exception as e:
                self.logger.error(f"API调用异常: {str(e)}")
                last_exception = e
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
        
        # 所有重试都失败
        if last_exception:
            raise last_exception
        else:
            raise Exception("API调用失败，未知错误")
    
    def _parse_response(self, response: requests.Response) -> Dict[str, Any]:
        """
        解析API响应
        
        Args:
            response: API响应
            
        Returns:
            解析后的结果
        """
        try:
            response_text = self._sanitize_response_text(response.text)
            
            # 尝试解析JSON响应
            # try:
            response_data = self._safe_parse_llm_response_text(response_text)
            # except json.JSONDecodeError:
            #     # 如果响应不是JSON，尝试提取JSON部分
            #     self.logger.warning(f"响应不是有效的JSON，尝试提取JSON部分: {response_text[:200]}")
                
            #     # 尝试从文本中提取JSON
            #     json_start = response_text.find('{')
            #     json_end = response_text.rfind('}') + 1
                
            #     if json_start >= 0 and json_end > json_start:
            #         json_str = response_text[json_start:json_end]
            #         try:
            #             response_data = json.loads(json_str)
            #         except json.JSONDecodeError:
            #             # 如果还是失败，创建默认响应
            #             response_data = {
            #                 'error': '响应不是有效的JSON',
            #                 'raw_response': response_text[:500]
            #             }
            #     else:
            #         # 如果没有找到JSON，创建默认响应
            #         response_data = {
            #             'error': '响应不是有效的JSON',
            #             'raw_response': response_text[:500]
            #         }
            
            # 检查响应格式
            if not isinstance(response_data, dict):
                raise ValueError("响应不是有效的JSON对象")
            
            # 标准化响应格式
            result = {
                'success': True,
                'raw_response': response_data,
                'analysis_result': {}
            }
            
            # 检查是否有错误
            if 'error' in response_data:
                result['success'] = False
                result['error'] = response_data['error']
                result['score'] = 0.0
                result['suggestions'] = []
                return result
            
            # 处理新的API响应格式
            # 根据用户反馈，大模型返回的结构是：
            # {
            #   "success": True,
            #   "raw_response": {
            #     "RSP_BODY": {
            #       "head": {},
            #       "TRAN_PROCESS": "aiQA",
            #       "answer": "{\n  \"sql_type\": \"数据操作\",\n  ...}"  # JSON字符串
            #     },
            #     "RSP_HEAD": {...}
            #   },
            #   "analysis_result": {}
            # }
            
            # 首先检查是否有RSP_BODY.answer字段（包含JSON字符串）
            answer_data = None
            if 'raw_response' in response_data:
                raw_response = response_data['raw_response']
                if isinstance(raw_response, dict) and 'RSP_BODY' in raw_response:
                    rsp_body = raw_response['RSP_BODY']
                    if isinstance(rsp_body, dict) and 'answer' in rsp_body:
                        answer_str = rsp_body['answer']
                        self.logger.debug(f"原始answer字符串长度: {len(answer_str)}")
                        self.logger.debug(f"前100字符: {answer_str[:100]}")
                        
                        try:
                            # 尝试解析answer字段中的JSON字符串
                            answer_data = json.loads(answer_str)
                            self.logger.info("成功解析answer字段中的JSON数据")
                            
                            # 检查是否需要二次解析（双重引号的情况）
                            if isinstance(answer_data, str):
                                self.logger.info("解析结果是字符串，需要二次解析")
                                try:
                                    answer_data = json.loads(answer_data)
                                    self.logger.info("二次解析成功")
                                except json.JSONDecodeError as e2:
                                    self.logger.warning(f"二次解析失败: {str(e2)}")
                                    answer_data = None
                                    
                        except json.JSONDecodeError:
                            # 如果answer字段不是有效的JSON，尝试清理后解析
                            self.logger.warning(f"answer字段不是有效的JSON，尝试清理后解析: {answer_str[:200]}")
                            try:
                                # 移除多余的转义字符
                                cleaned_answer = answer_str.replace('\\n', '\n').replace('\\"', '"')
                                # 如果字符串以引号开头和结尾，移除它们
                                if cleaned_answer.startswith('"') and cleaned_answer.endswith('"'):
                                    cleaned_answer = cleaned_answer[1:-1]
                                answer_data = json.loads(cleaned_answer)
                                self.logger.info("成功解析清理后的answer字段数据")
                                
                                # 检查是否需要二次解析
                                if isinstance(answer_data, str):
                                    self.logger.info("清理后解析结果是字符串，需要二次解析")
                                    try:
                                        answer_data = json.loads(answer_data)
                                        self.logger.info("二次解析成功")
                                    except json.JSONDecodeError as e2:
                                        self.logger.warning(f"二次解析失败: {str(e2)}")
                                        answer_data = None
                                        
                            except json.JSONDecodeError as e:
                                self.logger.error(f"无法解析answer字段: {str(e)}")
                                answer_data = None
            
            # 提取建议字段 - 从多个可能的位置提取
            extracted_suggestions = self._extract_all_suggestions(response_data, answer_data)
            
            # 提取其他字段
            extracted_data = self._extract_all_fields(response_data, answer_data)
            
            # 合并结果
            result.update(extracted_data)
            result['suggestions'] = extracted_suggestions
            result['improvement_suggestions'] = extracted_suggestions
            
            # 确保有详细分析字段
            if 'detailed_analysis' not in result:
                result['detailed_analysis'] = result.get('summary', '')
            
            # 将整个分析数据作为分析结果
            if answer_data and isinstance(answer_data, dict):
                result['analysis_result'] = answer_data
            else:
                result['analysis_result'] = response_data
            
            # 获取SQL类型
            sql_type = result.get('sql_type', '未知')
            
            self.logger.info(f"解析API响应成功，SQL类型: {sql_type}, 综合评分: {result.get('score', 'N/A')}, 建议数量: {len(extracted_suggestions)}")
            return result
            
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON解析失败: {str(e)}, 响应文本: {response.text[:200]}")
            raise ValueError(f"响应不是有效的JSON: {str(e)}")
        except Exception as e:
            self.logger.error(f"解析响应时发生错误: {str(e)}")
            raise
    
    def _safe_parse_llm_response_text(self, response_text: str) -> Dict[str, Any]:
        """安全解析大模型响应文本，处理多层转义JSON"""
        response_text = self._sanitize_response_text(response_text)
        
        # 记录原始文本长度用于调试
        self.logger.debug(f"开始解析响应文本，长度: {len(response_text)}")
        self.logger.debug(f"响应文本前200字符: {response_text[:200]}")
        
        # 0) 首先尝试直接解析为JSON（最外层）
        try:
            data = json.loads(response_text)
            if isinstance(data, dict):
                self.logger.debug("✅ 直接JSON解析成功")
                parsed_answer = self._parse_answer_from_dict(data)
                if parsed_answer:
                    return parsed_answer
                return data
        except Exception as e:
            self.logger.debug(f"直接JSON解析失败: {e}")
        
        # 1) 尝试解析为 Python dict
        data = self._try_parse_json(response_text)
        if isinstance(data, dict):
            self.logger.debug("✅ _try_parse_json解析成功")
            parsed_answer = self._parse_answer_from_dict(data)
            if parsed_answer:
                return parsed_answer
            return data

        # 2) 尝试从文本中直接抽取 answer 字段再解析
        extracted_answer = self._extract_answer_from_text(response_text)
        if extracted_answer:
            self.logger.debug(f"从文本中提取到answer字段，长度: {len(extracted_answer)}")
            parsed_answer = self._parse_answer_payload(extracted_answer)
            if parsed_answer:
                self.logger.debug("✅ 成功解析提取的answer字段")
                return parsed_answer

        # 3) 尝试从文本中提取 JSON 子串
        extracted_json = self._extract_json_substring(response_text)
        if extracted_json:
            self.logger.debug(f"从文本中提取到JSON子串，长度: {len(extracted_json)}")
            data = self._try_parse_json(extracted_json)
            if isinstance(data, dict):
                self.logger.debug("✅ 成功解析提取的JSON子串")
                parsed_answer = self._parse_answer_from_dict(data)
                if parsed_answer:
                    return parsed_answer
                return data

        # 4) 尝试多层清理后解析（针对用户提供的格式问题）
        self.logger.debug("尝试多层清理解析...")
        cleaned_text = self._deep_clean_response_text(response_text)
        if cleaned_text != response_text:
            try:
                data = json.loads(cleaned_text)
                if isinstance(data, dict):
                    self.logger.debug("✅ 多层清理后JSON解析成功")
                    parsed_answer = self._parse_answer_from_dict(data)
                    if parsed_answer:
                        return parsed_answer
                    return data
            except Exception as e:
                self.logger.debug(f"多层清理后解析失败: {e}")

        # 5) 最后尝试：如果响应文本以{"RSP_BODY"开头，尝试修复常见格式问题
        if response_text.startswith('{"RSP_BODY"'):
            self.logger.debug("响应以RSP_BODY开头，尝试修复格式问题...")
            fixed_text = self._fix_common_format_issues(response_text)
            if fixed_text != response_text:
                try:
                    data = json.loads(fixed_text)
                    if isinstance(data, dict):
                        self.logger.debug("✅ 修复格式问题后解析成功")
                        parsed_answer = self._parse_answer_from_dict(data)
                        if parsed_answer:
                            return parsed_answer
                        return data
                except Exception as e:
                    self.logger.debug(f"修复格式问题后解析失败: {e}")

        raise ValueError("无法解析响应内容（JSON / Python dict 均失败）")

    def _try_parse_json(self, text: str):
        """尝试将文本解析为 JSON 或 Python dict"""
        if not text:
            return None

        text = self._sanitize_response_text(text)

        # 先尝试 JSON
        try:
            return json.loads(text)
        except Exception:
            pass

        # 再尝试 Python dict
        try:
            return ast.literal_eval(text)
        except Exception:
            return None

    def _parse_answer_from_dict(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """从标准响应 dict 中解析 answer 字段"""
        try:
            # 支持两种格式：
            # 1. {"raw_response": {"RSP_BODY": {"answer": "..."}}}
            # 2. {"RSP_BODY": {"answer": "..."}}  # 用户提供的格式
            
            # 先尝试第一种格式
            if "raw_response" in data:
                raw_response = data.get("raw_response", {})
                if isinstance(raw_response, dict) and "RSP_BODY" in raw_response:
                    answer = raw_response.get("RSP_BODY", {}).get("answer")
                    parsed = self._parse_answer_payload(answer)
                    if parsed:
                        return parsed
            # 再尝试第二种格式（用户提供的格式）
            if "RSP_BODY" in data:
                rsp_body = data.get("RSP_BODY", {})
                answer = rsp_body.get("answer")
                parsed = self._parse_answer_payload(answer)
                if parsed:
                    return parsed
            
            # 还可能是直接包含answer字段的格式
            if "answer" in data:
                parsed = self._parse_answer_payload(data.get("answer"))
                if parsed:
                    return parsed
                
        except Exception as e:
            self.logger.debug(f"_parse_answer_from_dict解析失败: {e}")
            
        return None

    def _parse_answer_payload(self, answer: Any) -> Optional[Dict[str, Any]]:
        """解析 answer 字段的多层转义 JSON"""
        if not isinstance(answer, str):
            return None

        text = self._sanitize_response_text(answer)

        for _ in range(3):
            parsed = self._try_parse_json(text)
            if isinstance(parsed, dict):
                return parsed
            if isinstance(parsed, str):
                text = parsed.strip()
                continue

            # 手动反转义
            text = (
                text.replace("\\r", "\r")
                    .replace("\\n", "\n")
                    .replace("\\t", "\t")
                    .replace("\\\"", '"')
            )

            # 去掉首尾引号
            if (text.startswith('"') and text.endswith('"')) or (text.startswith("'") and text.endswith("'")):
                text = text[1:-1].strip()

        # 尝试从字符串中提取 JSON 子串
        extracted_json = self._extract_json_substring(text)
        if extracted_json:
            parsed = self._try_parse_json(extracted_json)
            if isinstance(parsed, dict):
                return parsed

        return None

    def _extract_answer_from_text(self, text: str) -> Optional[str]:
        """从原始文本中提取 answer 字段内容"""
        if not text:
            return None

        text = self._sanitize_response_text(text)

        import re
        pattern = r"[\"']answer[\"']\s*:\s*([\"'])(.*?)(?<!\\)\1"
        match = re.search(pattern, text, re.S)
        if match:
            return match.group(2)
        return None

    def _extract_json_substring(self, text: str) -> Optional[str]:
        """从文本中提取最外层 JSON 子串"""
        if not text:
            return None

        text = self._sanitize_response_text(text)

        start = text.find('{')
        end = text.rfind('}')
        if start >= 0 and end > start:
            return text[start:end + 1]
        return None

    def _sanitize_response_text(self, text: Optional[str]) -> str:
        """清理响应文本中的不可见字符和前导杂质"""
        if not text:
            return ""

        # 去除BOM与首尾空白
        cleaned = text.lstrip('\ufeff').strip()

        # 移除不可见控制字符（保留常见空白）
        cleaned = ''.join(
            ch for ch in cleaned
            if ch in ('\n', '\r', '\t') or ch >= ' '
        )

        # 如果首个非空白字符不是JSON起始符，尝试从第一个 { 或 [ 截断
        stripped = cleaned.lstrip()
        if stripped and stripped[0] not in ('{', '['):
            first_brace = stripped.find('{')
            first_bracket = stripped.find('[')
            candidates = [idx for idx in (first_brace, first_bracket) if idx >= 0]
            if candidates:
                cut_index = min(candidates)
                cleaned = stripped[cut_index:]

        return cleaned

    def _extract_suggestions(self, analysis_result: Dict[str, Any]) -> list:
        """从分析结果中提取建议"""
        suggestions = []
        
        try:
            # 首先检查是否有直接的suggestions字段
            if 'suggestions' in analysis_result and isinstance(analysis_result['suggestions'], list):
                suggestions.extend(analysis_result['suggestions'])
            
            # 检查其他可能的字段
            suggestion_fields = [
                'optimization_suggestions',
                'recommendations',
                'advice',
                'categorized_suggestions'
            ]
            
            for field in suggestion_fields:
                if field in analysis_result:
                    if isinstance(analysis_result[field], list):
                        suggestions.extend(analysis_result[field])
                    elif isinstance(analysis_result[field], dict):
                        # 如果是字典，提取所有值
                        for value in analysis_result[field].values():
                            if isinstance(value, list):
                                suggestions.extend(value)
            
            # 如果还没有找到建议，尝试从detailed_analysis中提取
            if not suggestions and 'detailed_analysis' in analysis_result:
                detailed = analysis_result['detailed_analysis']
                if 'RSP_BODY' in detailed and 'answer' in detailed['RSP_BODY']:
                    answer_text = detailed['RSP_BODY']['answer']
                    # 从文本中提取建议（简化处理）
                    suggestions.extend(self._extract_suggestions_from_text(answer_text))
            
            # 去重
            unique_suggestions = []
            seen = set()
            for suggestion in suggestions:
                if isinstance(suggestion, dict):
                    suggestion_str = json.dumps(suggestion, sort_keys=True)
                else:
                    suggestion_str = str(suggestion)
                
                if suggestion_str not in seen:
                    seen.add(suggestion_str)
                    unique_suggestions.append(suggestion)
            
            return unique_suggestions
            
        except Exception as e:
            self.logger.warning(f"提取建议时发生错误: {str(e)}")
            return []
    
    def _extract_suggestions_from_text(self, text: str) -> list:
        """从文本中提取建议"""
        suggestions = []
        
        try:
            # 清理文本：移除多余的引号和转义字符
            if text.startswith('"') and text.endswith('"'):
                text = text[1:-1]
            text = text.replace('\\n', '\n').replace('\\"', '"')
            
            # 查找包含"建议"的部分
            lines = text.split('\n')
            in_suggestion_section = False
            in_optimization_section = False
            
            for line in lines:
                line = line.strip()
                
                # 检查是否进入优化建议部分
                if '优化建议' in line or '3. 优化建议' in line:
                    in_optimization_section = True
                    in_suggestion_section = True
                
                # 检查是否进入按严重程度分类建议部分
                if '按严重程度分类建议' in line or '5. 按严重程度分类建议' in line:
                    in_suggestion_section = True
                
                # 如果是建议项（以-、*、•、数字开头，或者包含"建议："）
                if in_suggestion_section:
                    # 清理格式并提取建议
                    suggestion = self._extract_single_suggestion(line)
                    if suggestion:
                        suggestions.append(suggestion)
                
                # 检查是否离开建议部分
                if in_suggestion_section and ('评分' in line or 'score' in line.lower() or 
                                            '综合评分' in line or '4.' in line):
                    in_suggestion_section = False
                    in_optimization_section = False
            
            # 去重
            unique_suggestions = []
            seen = set()
            for suggestion in suggestions:
                # 进一步清理建议文本
                clean_suggestion = suggestion.strip()
                if clean_suggestion and len(clean_suggestion) > 10:  # 过滤太短的项
                    # 移除Markdown格式
                    clean_suggestion = clean_suggestion.replace('**', '').replace('`', '')
                    if clean_suggestion not in seen:
                        seen.add(clean_suggestion)
                        unique_suggestions.append(clean_suggestion)
            
            return unique_suggestions
            
        except Exception as e:
            self.logger.warning(f"从文本提取建议时发生错误: {str(e)}")
            return []
    
    def _extract_single_suggestion(self, line: str) -> str:
        """从单行文本中提取建议"""
        line = line.strip()
        
        # 如果是空行，返回空
        if not line:
            return ""
        
        # 移除列表标记
        if line.startswith('- ') or line.startswith('* ') or line.startswith('• '):
            line = line[2:].strip()
        elif line.startswith('1. ') or line.startswith('2. ') or line.startswith('3. ') or \
             line.startswith('4. ') or line.startswith('5. ') or line.startswith('6. '):
            line = line[3:].strip()
        
        # 检查是否是有效的建议
        if len(line) < 10:  # 太短，可能不是完整的建议
            return ""
        
        # 检查是否包含建议关键词
        suggestion_keywords = ['添加索引', '参数化查询', '数据类型', '索引', '查询', '优化', '建议', '使用', '确保', '检查']
        if any(keyword in line for keyword in suggestion_keywords):
            return line
        
        # 检查是否是优先级分类
        if '优先级' in line or '高优先级' in line or '中优先级' in line or '低优先级' in line:
            return line
        
        return ""
    
    def _calculate_score(self, analysis_result: Dict[str, Any]) -> float:
        """计算SQL质量评分"""
        try:
            # 尝试从响应中获取评分
            if 'score' in analysis_result and isinstance(analysis_result['score'], (int, float)):
                return float(analysis_result['score'])
            
            if 'quality_score' in analysis_result and isinstance(analysis_result['quality_score'], (int, float)):
                return float(analysis_result['quality_score'])
            
            # 如果没有评分，根据建议数量和质量估算
            suggestions = self._extract_suggestions(analysis_result)
            
            if not suggestions:
                return 8.0  # 没有建议，假设质量较好
            # 根据建议类型调整评分
            score = 10.0
            for suggestion in suggestions:
                if isinstance(suggestion, dict):
                    suggestion_text = str(suggestion).lower()
                else:
                    suggestion_text = str(suggestion).lower()
                
                # 严重问题扣分更多
                if any(keyword in suggestion_text for keyword in ['严重', 'critical', 'error', 'bug', '错误']):
                    score -= 2.0
                elif any(keyword in suggestion_text for keyword in ['警告', 'warning', '注意', '注意']):
                    score -= 1.0
                elif any(keyword in suggestion_text for keyword in ['建议', 'suggestion', '优化', 'improve']):
                    score -= 0.5
            
            # 确保评分在0-10之间
            return max(0.0, min(10.0, score))
            
        except Exception as e:
            self.logger.warning(f"计算评分时发生错误: {str(e)}")
            return 5.0  # 默认评分
    
    def _create_error_response(self, error_message: str) -> Dict[str, Any]:
        """创建错误响应"""
        return {
            'success': False,
            'error': error_message,
            'analysis_result': {
                'error': error_message,
                'suggestions': ['请检查API配置或网络连接'],
                'score': 0.0
            },
            'suggestions': ['请检查API配置或网络连接'],
            'score': 0.0
        }
    
    def _remove_comma_before_keywords(self, sql_text: str) -> str:
        """
        移除SQL关键字前的多余逗号
        
        Args:
            sql_text: SQL文本
            
        Returns:
            清理后的SQL文本
        """
        if not sql_text:
            return sql_text
        
        # 需要处理的关键字列表（这些关键字前不应该有逗号）
        keywords = ['WHERE', 'ORDER BY', 'GROUP BY', 'HAVING', 'LIMIT']
        
        result = sql_text
        
        for keyword in keywords:
            # 创建正则表达式模式，匹配逗号+空格+关键字（不区分大小写）
            # 模式：逗号，后面可能有空格，然后是关键字
            pattern = rf',\s*{keyword}'
            replacement = f' {keyword}'
            
            # 使用re.sub进行替换，不区分大小写
            result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
        
        return result
    
    def _fix_sql_structure_if_needed(self, sql_text: str) -> str:
        """
        如果需要，修复SQL语句结构，确保关键部分完整
        
        Args:
            sql_text: SQL文本
            
        Returns:
            修复后的SQL文本
        """
        if not sql_text:
            return sql_text
        
        # 先修复INSERT语句
        fixed = self._fix_insert_structure_if_needed(sql_text)
        
        # 再修复UPDATE语句（SET关键字丢失问题）
        fixed = self._fix_update_statement_if_needed(fixed)
        
        # 最后移除关键字前的多余逗号
        fixed = self._remove_comma_before_keywords(fixed)
        
        return fixed
    
    def remove_xml_tags(self, sql_text: str, mode: str = "normalize") -> Dict[str, Any]:
        """
        调用大模型API移除XML标签
        
        Args:
            sql_text: 包含XML标签的SQL语句
            mode: 处理模式 ("normalize" 或 "extract")
            
        Returns:
            移除XML标签后的结果
        """
        if not self.ai_config.get('api_url'):
            self.logger.error("未配置大模型API地址")
            return self._create_error_response("未配置大模型API地址")
        
        try:
            # 构建XML标签移除专用的请求负载
            payload = self._build_xml_removal_payload(sql_text, mode)
            
            # 调用API
            response = self._call_api_with_retry(payload)
            
            # 解析响应
            result = self._parse_xml_removal_response(response, sql_text)
            
            return result
            
        except Exception as e:
            self.logger.error(f"调用大模型API移除XML标签时发生错误: {str(e)}", exc_info=True)
            return self._create_error_response(str(e))
    
    def _build_xml_removal_payload(self, sql_text: str, mode: str) -> Dict[str, Any]:
        """
        构建XML标签移除专用的请求负载
        
        Args:
            sql_text: 包含XML标签的SQL语句
            mode: 处理模式
            
        Returns:
            构建好的请求负载
        """
        # 构建清晰的指令
        instructions = []
        instructions.append("请将以下包含XML标签的SQL语句转换为标准SQL格式。")
        
        if mode == "normalize":
            instructions.append("要求：移除所有的XML标签（如<select>, <insert>, <update>, <delete>, <query>等），但保留标签内的SQL内容。")
            instructions.append("注意：保留SQL注释、参数占位符（如#{id}）和SQL语句的原始格式。")
        elif mode == "extract":
            instructions.append("要求：提取SQL内容，移除整个XML标签及其内容中不相关的部分。")
            instructions.append("注意：只保留有效的SQL语句部分。")
        
        instructions.append("")
        instructions.append("处理规则：")
        instructions.append("1. 移除所有XML标签，包括开标签、闭标签和自闭合标签")
        instructions.append("2. 处理CDATA块：移除<![CDATA[ 和 ]]>标记，保留其中的内容")
        instructions.append("3. 移除XML标签属性（如<sql type='query'>中的type='query'）")
        instructions.append("4. 处理嵌套标签（如<query><select>...</select></query>）")
        instructions.append("5. 保留SQL语句的完整性，不要修改SQL语法")
        instructions.append("6. 输出中只包含处理后的SQL语句，不要包含解释或额外文本")
        instructions.append("")
        instructions.append("需要处理的SQL语句：")
        instructions.append(f"```sql")
        instructions.append(sql_text)
        instructions.append(f"```")
        instructions.append("")
        instructions.append("请直接输出处理后的SQL语句，不要包含任何其他内容。")
        
        prompt = "\n".join(instructions)
        
        self.logger.info(f"构建XML标签移除专用prompt完成：长度={len(prompt)}, 预览前200字符=\n{prompt[:200]}...")
        
        # 新的API只需要prompt参数
        payload = {
            "prompt": prompt
        }
        
        return payload
    
    def _parse_xml_removal_response(self, response: requests.Response, original_sql: str) -> Dict[str, Any]:
        """
        解析XML标签移除的API响应
        
        Args:
            response: API响应
            original_sql: 原始SQL语句
            
        Returns:
            解析后的结果
        """
        try:
            # 清理响应文本
            response_text = self._sanitize_response_text(response.text)
            
            # 记录原始响应用于调试
            self.logger.debug(f"XML标签移除原始响应长度: {len(response_text)}")
            self.logger.debug(f"XML标签移除原始响应前200字符: {response_text[:200]}")
            
            # 尝试解析响应
            response_data = self._safe_parse_llm_response_text(response_text)
            
            # 从响应中提取处理后的SQL
            processed_sql = self._extract_processed_sql_from_response(response_data, original_sql)
            
            # 验证处理后的SQL
            is_valid = self._validate_processed_sql(processed_sql, original_sql)
            
            if is_valid:
                result = {
                    'success': True,
                    'processed_sql': processed_sql,
                    'original_sql': original_sql,
                    'original_length': len(original_sql),
                    'processed_length': len(processed_sql),
                    'confidence': self._calculate_xml_removal_confidence(processed_sql, original_sql),
                    'response_data': response_data
                }
                self.logger.info(f"XML标签移除成功: 原始长度={len(original_sql)}, 处理后长度={len(processed_sql)}")
                return result
            else:
                self.logger.warning(f"XML标签移除结果验证失败: {processed_sql[:100]}...")
                return {
                    'success': False,
                    'error': '处理结果验证失败',
                    'original_sql': original_sql,
                    'processed_sql': processed_sql,
                    'response_data': response_data
                }
                
        except Exception as e:
            self.logger.error(f"解析XML标签移除响应时发生错误: {str(e)}")
            raise
    
    def _extract_processed_sql_from_response(self, response_data: Dict[str, Any], original_sql: str) -> str:
        """
        从响应数据中提取处理后的SQL
        
        Args:
            response_data: 解析后的响应数据
            original_sql: 原始SQL语句（作为回退）
            
        Returns:
            提取的处理后SQL
        """
        # 尝试从多个位置提取SQL
        processed_sql = original_sql  # 默认使用原始SQL
        
        # 定义可能包含SQL的字段
        sql_fields = ['processed_sql', 'result', 'answer', 'sql', 'content', 'text']
        
        # 搜索数据源
        data_sources = []
        if isinstance(response_data, dict):
            data_sources.append(response_data)
        
        for data_source in data_sources:
            for field in sql_fields:
                if field in data_source:
                    value = data_source[field]
                    if isinstance(value, str) and value.strip():
                        processed_sql = value.strip()
                        break
                if field in data_source:
                    break
        
        # 清理提取的SQL
        processed_sql = self._clean_extracted_sql(processed_sql)
        
        return processed_sql
    
    def _clean_extracted_sql(self, sql_text: str) -> str:
        """
        清理提取的SQL文本，特别保护SQL关键结构和括号结构
        
        Args:
            sql_text: 提取的SQL文本
            
        Returns:
            清理后的SQL文本
        """
        if not sql_text:
            return ""
        
        cleaned = sql_text
        
        # 1. 移除代码块标记（但要小心不要移除括号）
        cleaned = re.sub(r'```[\w]*\s*', '', cleaned)
        cleaned = re.sub(r'```', '', cleaned)
        
        # 2. 移除XML标签（但要小心不要移除括号）
        # 使用更保守的方法，只移除真正的XML标签
        cleaned = re.sub(r'<[^>]+>', ' ', cleaned)
        
        # 3. 移除CDATA标记
        cleaned = re.sub(r'<!\[CDATA\[', '', cleaned)
        cleaned = re.sub(r'\]\]>', '', cleaned)
        
        # 4. 压缩多余空格，但保留换行符（对多行SQL很重要）
        # 先分割为行，单独处理每行
        lines = cleaned.split('\n')
        cleaned_lines = []
        for line in lines:
            line = re.sub(r'\s+', ' ', line.strip())
            if line:
                cleaned_lines.append(line)
        
        # 重新组合，保留换行符（对多行SQL很重要）
        cleaned = '\n'.join(cleaned_lines)
        
        # 5. 修复SQL语句结构（如果缺少关键部分）
        cleaned = self._fix_sql_structure_if_needed(cleaned)
        
        # 6. 移除首尾空白
        cleaned = cleaned.strip()
        
        return cleaned
    
    def _fix_update_statement_if_needed(self, sql_text: str) -> str:
        """
        修复UPDATE语句缺少SET关键字的问题
        
        Args:
            sql_text: SQL文本
            
        Returns:
            修复后的SQL文本
        """
        if not sql_text:
            return sql_text
        
        sql_upper = sql_text.upper()
        
        # 检查是否是UPDATE语句
        if sql_upper.startswith('UPDATE'):
            # 检查是否有SET关键字
            if 'SET' not in sql_upper:
                self.logger.debug("检测到UPDATE语句缺少SET关键字，尝试修复")
                
                # 找到UPDATE后面的表名
                words = sql_text.split()
                if len(words) >= 2:
                    # UPDATE table_name ... 
                    # 在表名后插入SET
                    result_parts = []
                    for i, word in enumerate(words):
                        result_parts.append(word)
                        # 在第二个单词（表名）后插入SET
                        if i == 1:  # 表名位置
                            # 检查下一个单词是否是SET（以防万一）
                            if i + 1 < len(words) and words[i + 1].upper() != 'SET':
                                result_parts.append('SET')
                    
                    fixed_sql = ' '.join(result_parts)
                    
                    # 如果仍然没有SET，确保在表名后添加
                    if 'SET' not in fixed_sql.upper():
                        # 简单的修复：在UPDATE table_name后添加SET
                        import re
                        # 匹配 UPDATE table_name 模式
                        pattern = r'(UPDATE\s+\w+)'
                        fixed_sql = re.sub(pattern, r'\1 SET', fixed_sql, flags=re.IGNORECASE)
                    
                    self.logger.debug(f"修复UPDATE语句结构: 原始长度={len(sql_text)}, 修复后长度={len(fixed_sql)}")
                    return fixed_sql
        
        return sql_text
    
    def _fix_insert_structure_if_needed(self, sql_text: str) -> str:
        """
        如果需要，修复INSERT语句结构，确保括号完整
        
        Args:
            sql_text: SQL文本
            
        Returns:
            修复后的SQL文本
        """
        if not sql_text:
            return sql_text
        
        # 检查是否是INSERT语句
        sql_lower = sql_text.lower().strip()
        if not sql_lower.startswith('insert'):
            return sql_text
        
        # 检查括号数量
        open_paren = sql_text.count('(')
        close_paren = sql_text.count(')')
        
        # 如果括号数量为0，尝试修复
        if open_paren == 0 and close_paren == 0:
            self.logger.debug("检测到INSERT语句缺少括号，尝试修复")
            
            # 查找表名结束位置
            table_name_end = -1
            # 匹配INSERT INTO table_name
            import re
            insert_match = re.search(r'insert\s+into\s+([^\s(]+)', sql_lower)
            if insert_match:
                table_name = insert_match.group(1)
                table_name_end = sql_lower.find(table_name) + len(table_name)
                
                # 查找VALUES关键字
                values_pos = sql_lower.find('values', table_name_end)
                
                # 如果没有VALUES关键字，尝试推断列名和值的分界
                if values_pos <= 0:
                    # 分析SQL结构，尝试找到列名和值的分界点
                    # 列名通常是字段名（大写、下划线分隔）
                    # 值通常是参数（#{...}）或字面值
                    
                    # 按行分割SQL
                    lines = sql_text.split('\n')
                    
                    # 寻找可能的列名部分和值部分
                    column_lines = []
                    value_lines = []
                    in_value_section = False
                    
                    for line in lines:
                        line = line.strip()
                        if not line:
                            continue
                            
                        # 检查是否是值部分（包含参数占位符）
                        if '#{' in line:
                            in_value_section = True
                            
                        if in_value_section:
                            value_lines.append(line)
                        else:
                            # 跳过表名行（已经处理过表名）
                            if not line.lower().startswith('insert') and not line.lower().startswith('into'):
                                column_lines.append(line)
                    
                    if column_lines and value_lines:
                        # 重建SQL
                        columns_part = ', '.join([col.strip().rstrip(',') for col in column_lines])
                        values_part = ', '.join([val.strip().rstrip(',') for val in value_lines])
                        
                        # 移除列名部分末尾可能的多余逗号
                        if columns_part.endswith(','):
                            columns_part = columns_part[:-1]
                        if values_part.endswith(','):
                            values_part = values_part[:-1]
                        
                        # 添加括号和VALUES关键字
                        table_part = sql_text[:table_name_end].strip()
                        fixed_sql = f'{table_part} ({columns_part}) VALUES ({values_part})'
                        
                        self.logger.debug(f"智能修复INSERT语句结构（无VALUES关键字）: 原始长度={len(sql_text)}, 修复后长度={len(fixed_sql)}")
                        return fixed_sql
                
                # 如果有VALUES关键字，使用原来的逻辑
                if values_pos > 0:
                    # 列名部分（表名后到VALUES前）
                    columns_part = sql_text[table_name_end:values_pos].strip()
                    # 值部分（VALUES后）
                    values_part = sql_text[values_pos + 5:].strip()
                    
                    # 清理列名部分（移除多余空格和换行）
                    columns_clean = re.sub(r'\s+', ' ', columns_part).strip()
                    # 清理值部分
                    values_clean = re.sub(r'\s+', ' ', values_part).strip()
                    
                    # 检查列名部分是否看起来像列名（包含逗号）
                    if ',' in columns_clean or any(keyword in columns_clean.lower() for keyword in ['mtm_', 'col', 'field', 'id']):
                        # 在列名部分前后添加括号
                        columns_fixed = f'({columns_clean})'
                    else:
                        # 如果列名部分不包含逗号，可能是一个列名
                        columns_fixed = f'({columns_clean})'
                    
                    # 检查值部分是否看起来像值（包含逗号或参数）
                    if ',' in values_clean or '#{' in values_clean or 'value' in values_clean.lower():
                        # 在值部分前后添加括号
                        # 但要注意可能已经有引号或其他字符
                        values_fixed = f'({values_clean})'
                    else:
                        values_fixed = f'({values_clean})'
                    
                    # 重新组合SQL
                    table_part = sql_text[:table_name_end].strip()
                    fixed_sql = f'{table_part} {columns_fixed} VALUES {values_fixed}'
                    
                    self.logger.debug(f"修复INSERT语句结构（有VALUES关键字）: 原始长度={len(sql_text)}, 修复后长度={len(fixed_sql)}")
                    return fixed_sql
        
        # 如果只有一对括号，但INSERT语句应该有两对括号
        elif open_paren == 1 and close_paren == 1:
            self.logger.debug("检测到INSERT语句只有一对括号，尝试修复")
            
            # 检查括号位置
            first_paren = sql_text.find('(')
            last_paren = sql_text.rfind(')')
            
            # 查找VALUES关键字
            values_pos = sql_lower.find('values')
            
            import re
            if values_pos > 0 and first_paren < values_pos < last_paren:
                # 括号在VALUES之前，这可能是列名括号
                # 需要添加值括号
                
                # 在VALUES后面添加括号
                # 找到VALUES后的内容
                after_values = sql_text[values_pos + 5:].strip()
                
                # 如果VALUES后的内容没有括号，添加
                if not after_values.startswith('('):
                    # 找到值的结束位置
                    # 如果是参数形式，可能以逗号或分号结束
                    end_pos = len(sql_text)
                    for end_char in [',', ';', '\n']:
                        pos = sql_text.find(end_char, values_pos + 5)
                        if pos > 0 and pos < end_pos:
                            end_pos = pos
                    
                    values_content = sql_text[values_pos + 5:end_pos].strip()
                    # 添加括号
                    values_fixed = f'({values_content})'
                    
                    # 重新组合
                    before_values = sql_text[:values_pos + 5].strip()
                    fixed_sql = f'{before_values} {values_fixed}'
                    if end_pos < len(sql_text):
                        fixed_sql += sql_text[end_pos:]
                    
                    self.logger.debug(f"为INSERT语句添加值括号: 原始长度={len(sql_text)}, 修复后长度={len(fixed_sql)}")
                    return fixed_sql
        
        return sql_text
    
    def _extract_all_suggestions(self, response_data: Dict[str, Any], answer_data: Optional[Dict[str, Any]]) -> List[str]:
        """
        从多个可能的位置提取建议
        
        Args:
            response_data: 原始响应数据
            answer_data: 解析后的answer数据
            
        Returns:
            提取的建议列表
        """
        all_suggestions = []
        
        # 定义可能包含建议的字段
        suggestion_fields = [
            '建议', 'suggestions', 'improvement_suggestions', 'recommendations',
            '优化建议', 'improvements', 'recommendation_list'
        ]
        
        # 搜索数据源（按优先级）
        data_sources = []
        if answer_data and isinstance(answer_data, dict):
            data_sources.append(answer_data)
        if response_data and isinstance(response_data, dict):
            data_sources.append(response_data)
        
        for data_source in data_sources:
            for field in suggestion_fields:
                if field in data_source:
                    suggestions = data_source[field]
                    if isinstance(suggestions, list):
                        for suggestion in suggestions:
                            if isinstance(suggestion, str):
                                all_suggestions.append(suggestion)
                            elif suggestion is not None:
                                all_suggestions.append(str(suggestion))
                    elif isinstance(suggestions, dict):
                        # 如果是字典，提取所有值
                        for value in suggestions.values():
                            if isinstance(value, list):
                                for item in value:
                                    if isinstance(item, str):
                                        all_suggestions.append(item)
                                    elif item is not None:
                                        all_suggestions.append(str(item))
                    elif isinstance(suggestions, str):
                        # 如果是字符串，尝试解析逗号分隔的列表
                        parts = [s.strip() for s in suggestions.split(',')]
                        all_suggestions.extend([p for p in parts if p])
        
        # 去重和清理
        cleaned_suggestions = []
        seen = set()
        for suggestion in all_suggestions:
            if isinstance(suggestion, str):
                clean_suggestion = suggestion.strip()
                if clean_suggestion and clean_suggestion not in seen:
                    seen.add(clean_suggestion)
                    cleaned_suggestions.append(clean_suggestion)
        
        self.logger.debug(f"从响应中提取到 {len(cleaned_suggestions)} 条建议")
        return cleaned_suggestions
    
    def _extract_all_fields(self, response_data: Dict[str, Any], answer_data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """
        从多个可能的位置提取所有字段
        
        Args:
            response_data: 原始响应数据
            answer_data: 解析后的answer数据
            
        Returns:
            提取的所有字段
        """
        result = {}
        
        # 定义字段映射
        field_mappings = {
            'sql_type': ['SQL类型', 'sql_type', 'type', 'sqlType'],
            'summary': ['分析摘要', 'summary', 'detailed_analysis', 'analysis_summary'],
            'score': ['综合评分', 'overall_score', 'score', 'quality_score'],
            'risk_assessment': ['风险评估', 'risk_assessment', 'risk_analysis', 'riskAssessment'],
            'modification_suggestions': ['修改建议', 'modification_suggestions', 'sql_modifications'],
            'specifications_compliance': ['规范符合性', 'specifications_compliance', 'compliance']
        }
        
        # 搜索数据源（按优先级）
        data_sources = []
        if answer_data and isinstance(answer_data, dict):
            data_sources.append(answer_data)
        if response_data and isinstance(response_data, dict):
            data_sources.append(response_data)
        
        # 提取字段
        for key, field_names in field_mappings.items():
            for data_source in data_sources:
                found = False
                for field_name in field_names:
                    if field_name in data_source:
                        value = data_source[field_name]
                        if value is not None:
                            result[key] = value
                            found = True
                            break
                if found:
                    break
        
        # 确保有默认值
        if 'sql_type' not in result:
            result['sql_type'] = '未知'
        if 'summary' not in result:
            result['summary'] = ''
        if 'score' not in result:
            result['score'] = 5.0
        if 'risk_assessment' not in result:
            result['risk_assessment'] = {}
        if 'specifications_compliance' not in result:
            result['specifications_compliance'] = {
                'compliant_rules': [],
                'violated_rules': [],
                'compliance_score': 100.0,
                'violation_details': []
            }
        
        # 计算风险评分
        risk_score = self._calculate_risk_score(result.get('risk_assessment', {}))
        result['risk_score'] = risk_score
        
        # 计算规则评分（如果可能）
        if 'rule_analysis' in result:
            rule_score = self._calculate_rule_score(result['rule_analysis'])
            result['rule_score'] = rule_score
        else:
            result['rule_score'] = 5.0
        
        # 提取修改建议SQL
        if 'modification_suggestions' in result:
            mod_suggestions = result['modification_suggestions']
            if isinstance(mod_suggestions, dict):
                sql_modifications = {}
                
                # 提取各种类型的SQL修改建议
                for field_name, sql_key in [
                    ('高风险问题SQL', 'high_risk_sql'),
                    ('中风险问题SQL', 'medium_risk_sql'),
                    ('低风险问题SQL', 'low_risk_sql'),
                    ('性能优化SQL', 'performance_sql')
                ]:
                    if field_name in mod_suggestions:
                        sql_text = mod_suggestions[field_name]
                        if isinstance(sql_text, str) and sql_text.strip():
                            sql_modifications[sql_key] = sql_text
                
                result['sql_modifications'] = sql_modifications
                self.logger.info(f"提取到 {len(sql_modifications)} 个SQL修改建议")
        
        self.logger.debug(f"提取字段完成: SQL类型={result.get('sql_type')}, 评分={result.get('score')}, 规范符合度={result.get('specifications_compliance', {}).get('compliance_score', 'N/A')}")
        return result
    
    def _deep_clean_response_text(self, text: str) -> str:
        """
        深度清理响应文本，处理多层转义和格式问题
        
        Args:
            text: 原始响应文本
            
        Returns:
            清理后的文本
        """
        if not text:
            return ""
        
        self.logger.debug(f"深度清理前文本长度: {len(text)}, 前100字符: {text[:100]}")
        
        # 1. 首先应用基本清理
        cleaned = self._sanitize_response_text(text)
        
        # 2. 处理常见的格式问题：""{ 开头（双重引号问题）
        # 用户提供的格式问题：answer":""{\n  \"sql_type\":
        # 正确格式应该是：answer":"{\n  \"sql_type\":
        # 修复双重引号问题
        if '""{' in cleaned:
            cleaned = cleaned.replace('""{', '"{')
            self.logger.debug("修复了双重引号问题")
        
        # 3. 处理转义字符（多层）
        # 先处理 \\n -> \n
        cleaned = cleaned.replace('\\\\n', '\n').replace('\\n', '\n')
        # 处理 \\" -> \"
        cleaned = cleaned.replace('\\\\"', '\\"').replace('\\"', '"')
        # 处理 \\r -> \r
        cleaned = cleaned.replace('\\\\r', '\r').replace('\\r', '\r')
        # 处理 \\t -> \t
        cleaned = cleaned.replace('\\\\t', '\t').replace('\\t', '\t')
        
        # 4. 如果字符串以引号开头和结尾，但内部还有转义，可能需要移除最外层引号
        cleaned_stripped = cleaned.strip()
        if cleaned_stripped.startswith('"') and cleaned_stripped.endswith('"'):
            # 检查内部是否包含有效的JSON结构
            inner = cleaned_stripped[1:-1]
            # 如果内部以 { 或 [ 开头，可能是有效的JSON
            if inner.strip().startswith(('{', '[')):
                cleaned = inner
                self.logger.debug("移除了最外层引号")
        
        # 5. 修复不完整的转义序列
        # 处理 "\\" 后跟非转义字符的情况
        import re
        cleaned = re.sub(r'\\\\([^\\nr"])', r'\\\1', cleaned)
        
        self.logger.debug(f"深度清理后文本长度: {len(cleaned)}, 前100字符: {cleaned[:100]}")
        return cleaned
    
    def _fix_common_format_issues(self, text: str) -> str:
        """
        修复常见的JSON格式问题
        
        Args:
            text: 可能有格式问题的JSON文本
            
        Returns:
            修复后的文本
        """
        if not text:
            return ""
        
        self.logger.debug(f"修复格式问题前文本长度: {len(text)}")
        
        # 修复用户提供的格式问题：
        # 问题1: "answer":""{"..."}" （双重引号）
        # 问题2: 转义字符过多
        
        fixed = text
        
        # 1. 修复 answer 字段的双重引号问题
        # 匹配模式: "answer":""{ 替换为 "answer":"{
        import re
        fixed = re.sub(r'"answer"\s*:\s*""\{', '"answer":"{', fixed)
        
        # 2. 修复其他字段的双重引号问题
        fixed = re.sub(r'("\w+")\s*:\s*""', r'\1:"', fixed)
        
        # 3. 修复转义字符：将 \\\" 替换为 \"
        fixed = fixed.replace('\\\\\\"', '\\"')
        
        # 4. 修复缺少逗号的问题：在某些情况下，字段之间可能缺少逗号
        # 例如：{"key1":"value1" "key2":"value2"}
        fixed = re.sub(r'("\s*"\s*")', r'","', fixed)
        
        # 5. 修复布尔值被引号包裹的问题
        fixed = re.sub(r':\s*"true"\s*([,}])', r':true\1', fixed)
        fixed = re.sub(r':\s*"false"\s*([,}])', r':false\1', fixed)
        fixed = re.sub(r':\s*"null"\s*([,}])', r':null\1', fixed)
        
        self.logger.debug(f"修复格式问题后文本长度: {len(fixed)}")
        if fixed != text:
            self.logger.debug("修复了JSON格式问题")
        
        return fixed
    
    def _validate_processed_sql(self, processed_sql: str, original_sql: str) -> bool:
        """
        验证处理后的SQL是否有效
        
        Args:
            processed_sql: 处理后的SQL
            original_sql: 原始SQL
            
        Returns:
            是否有效
        """
        if not processed_sql or not processed_sql.strip():
            return False
        
        # 检查长度是否合理
        if len(processed_sql) > len(original_sql) * 2:
            return False
        
        # 检查是否仍然包含明显的XML标签
        if self._contains_xml_tags(processed_sql):
            return False
        
        # 检查是否包含有效的SQL关键字
        sql_keywords = ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'CREATE', 'ALTER', 'DROP', 'FROM', 'WHERE', 'SET']
        sql_upper = processed_sql.upper()
        has_sql_keyword = any(keyword in sql_upper for keyword in sql_keywords)
        
        return has_sql_keyword
    
    def _contains_xml_tags(self, sql_text: str) -> bool:
        """
        检查是否包含XML标签
        
        Args:
            sql_text: SQL语句文本
            
        Returns:
            是否包含XML标签
        """
        if not sql_text or not sql_text.strip():
            return False
        
        xml_patterns = [
            r'<[^>]+>',  # 基本XML标签
            r'<!\[CDATA\[',  # CDATA标记
        ]
        
        for pattern in xml_patterns:
            if re.search(pattern, sql_text):
                return True
        
        return False
    
    def _calculate_xml_removal_confidence(self, processed_sql: str, original_sql: str) -> float:
        """
        计算XML标签移除的置信度
        
        Args:
            processed_sql: 处理后的SQL
            original_sql: 原始SQL
            
        Returns:
            置信度 (0-1)
        """
        confidence = 1.0
        
        # 1. 检查是否移除了XML标签
        if self._contains_xml_tags(processed_sql):
            confidence *= 0.3
        
        # 2. 检查长度变化是否合理
        original_len = len(original_sql)
        processed_len = len(processed_sql)
        
        if original_len > 0:
            length_ratio = processed_len / original_len
            if length_ratio < 0.3 or length_ratio > 1.5:
                confidence *= 0.5
            elif 0.7 <= length_ratio <= 1.2:
                confidence *= 1.2
        
        # 3. 检查是否包含SQL关键字
        sql_keywords = ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'CREATE', 'ALTER', 'DROP']
        sql_upper = processed_sql.upper()
        keyword_count = sum(1 for keyword in sql_keywords if keyword in sql_upper)
        if keyword_count > 0:
            confidence *= (1.0 + 0.1 * keyword_count)
        
        # 确保置信度在0-1之间
        return max(0.0, min(1.0, confidence))
    
    def _calculate_risk_score(self, risk_assessment: Dict[str, Any]) -> float:
        """
        计算风险评分
        
        Args:
            risk_assessment: 风险评估结果
            
        Returns:
            风险评分 (0-10分，越高表示风险越低)
        """
        try:
            if not isinstance(risk_assessment, dict):
                return 5.0
            
            # 初始评分
            score = 10.0
            
            # 高风险问题扣分
            if '高风险问题' in risk_assessment:
                high_risks = risk_assessment['高风险问题']
                if isinstance(high_risks, list):
                    for risk in high_risks:
                        if isinstance(risk, str) and risk.strip():
                            score -= 3.0  # 每个高风险问题扣3分
            
            # 中风险问题扣分
            if '中风险问题' in risk_assessment:
                medium_risks = risk_assessment['中风险问题']
                if isinstance(medium_risks, list):
                    for risk in medium_risks:
                        if isinstance(risk, str) and risk.strip():
                            score -= 1.5  # 每个中风险问题扣1.5分
            
            # 低风险问题扣分
            if '低风险问题' in risk_assessment:
                low_risks = risk_assessment['低风险问题']
                if isinstance(low_risks, list):
                    for risk in low_risks:
                        if isinstance(risk, str) and risk.strip():
                            score -= 0.5  # 每个低风险问题扣0.5分
            
            # 确保评分在0-10之间
            return max(0.0, min(10.0, score))
                
        except Exception as e:
            self.logger.warning(f"计算风险评分时发生错误: {str(e)}")
            return 5.0
    
    def _calculate_rule_score(self, rule_analysis: Dict[str, Any]) -> float:
        """
        计算规则符合性评分
        
        Args:
            rule_analysis: 规则分析结果
            
        Returns:
            规则评分 (0-10分)
        """
        try:
            if not isinstance(rule_analysis, dict):
                return 5.0
            
            total_checks = 0
            passed_checks = 0
            
            # 检查建表规则
            if '建表规则' in rule_analysis:
                table_rules = rule_analysis['建表规则']
                if isinstance(table_rules, dict):
                    # 检查关键规则
                    key_checks = ['主键检查', '索引检查', '数据量评估', '注释检查', '字段类型检查']
                    for check in key_checks:
                        if check in table_rules:
                            total_checks += 1
                            value = table_rules[check]
                            if isinstance(value, str) and '通过' in value or '合理' in value or '完整' in value:
                                passed_checks += 1
            
            # 检查表结构变更规则
            if '表结构变更规则' in rule_analysis:
                alter_rules = rule_analysis['表结构变更规则']
                if isinstance(alter_rules, dict):
                    # 检查关键规则
                    key_checks = ['影响范围评估', '联机影响评估', '注释检查']
                    for check in key_checks:
                        if check in alter_rules:
                            total_checks += 1
                            value = alter_rules[check]
                            if isinstance(value, str) and '完整' in value or '合理' in value:
                                passed_checks += 1
            
            # 检查索引规则
            if '索引规则' in rule_analysis:
                index_rules = rule_analysis['索引规则']
                if isinstance(index_rules, dict):
                    # 检查关键规则
                    key_checks = ['索引冗余检查', '索引设计合理性']
                    for check in key_checks:
                        if check in index_rules:
                            total_checks += 1
                            value = index_rules[check]
                            if isinstance(value, str) and '无冗余' in value or '合理' in value:
                                passed_checks += 1
            
            # 检查数据量规则
            if '数据量规则' in rule_analysis:
                data_rules = rule_analysis['数据量规则']
                if isinstance(data_rules, dict):
                    # 检查关键规则
                    key_checks = ['SQL耗时评估', '备份策略', '数据核对']
                    for check in key_checks:
                        if check in data_rules:
                            total_checks += 1
                            value = data_rules[check]
                            if isinstance(value, str) and ('毫秒级' in value or '有' in value or '已核对' in value):
                                passed_checks += 1
            
            # 计算评分
            if total_checks > 0:
                score = (passed_checks / total_checks) * 10.0
                return round(score, 1)
            else:
                return 5.0
                
        except Exception as e:
            self.logger.warning(f"计算规则评分时发生错误: {str(e)}")
            return 5.0

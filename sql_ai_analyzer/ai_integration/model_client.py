#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
大模型API客户端模块
负责调用大模型API进行SQL分析
"""

import json
import time
import requests
from typing import Dict, Any, Optional, List
from utils.logger import LogMixin
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
    
    def _build_request_payload(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        构建请求负载
        
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
        
        # 构建prompt内容
        prompt_parts = []
        
        # 1. SQL语句
        prompt_parts.append(f"SQL语句：\n{sql_statement}\n")
        
        # 2. 数据库信息
        prompt_parts.append(f"数据库：{db_alias}\n")
        
        # 3. 表信息
        if tables:
            prompt_parts.append("涉及的表信息：")
            for i, table in enumerate(tables, 1):
                table_name = table.get('table_name', '未知表')
                row_count = table.get('row_count', 0)
                is_large_table = table.get('is_large_table', False)
                column_count = len(table.get('columns', []))
                index_count = len(table.get('indexes', []))
                ddl = table.get('ddl', '')
                
                prompt_parts.append(f"\n表{i}：{table_name}")
                prompt_parts.append(f"  - 行数：{row_count}")
                prompt_parts.append(f"  - 是否大表：{'是' if is_large_table else '否'}")
                prompt_parts.append(f"  - 列数：{column_count}")
                prompt_parts.append(f"  - 索引数：{index_count}")
                
                # 添加DDL信息（如果存在）
                if ddl and ddl != f"CREATE TABLE {table_name} (/* 无法获取完整DDL */)":
                    prompt_parts.append(f"  - DDL：")
                    # 将DDL按行分割，每行前面加两个空格
                    ddl_lines = ddl.split('\n')
                    for line in ddl_lines:
                        prompt_parts.append(f"    {line}")
                else:
                    prompt_parts.append(f"  - DDL：无法获取完整DDL")
                
                # 添加列信息
                columns = table.get('columns', [])
                if columns:
                    prompt_parts.append(f"  - 列信息：")
                    for col in columns[:5]:  # 只显示前5列
                        col_name = col.get('name', '未知')
                        col_type = col.get('type', '未知')
                        nullable = col.get('nullable', True)
                        prompt_parts.append(f"    * {col_name} ({col_type}) {'可空' if nullable else '非空'}")
                    if len(columns) > 5:
                        prompt_parts.append(f"    * ... 还有{len(columns)-5}列")
                
                # 添加索引信息（如果存在）
                indexes = table.get('indexes', [])
                if indexes:
                    prompt_parts.append(f"  - 索引信息：")
                    for idx in indexes[:3]:  # 只显示前3个索引
                        idx_name = idx.get('name', '未知索引')
                        idx_columns = ', '.join(idx.get('columns', []))
                        idx_type = idx.get('type', '未知类型')
                        idx_unique = idx.get('unique', False)
                        unique_str = '唯一' if idx_unique else '非唯一'
                        prompt_parts.append(f"    * {idx_name}: {idx_columns} ({idx_type}, {unique_str})")
                    if len(indexes) > 3:
                        prompt_parts.append(f"    * ... 还有{len(indexes)-3}个索引")
        
        # 4. 动态SQL示例（用于判断SQL注入漏洞）- 使用真实表名和字段名
        prompt_parts.append("\n动态SQL示例（用于判断SQL注入漏洞）：")
        prompt_parts.append("请分析以下动态SQL示例是否存在SQL注入风险：")
        
        # 生成动态SQL示例，使用真实表名和字段名
        dynamic_sql_examples = self._generate_dynamic_sql_examples(sql_statement, tables)
        for example in dynamic_sql_examples:
            prompt_parts.append(f"- {example}")
        
        # 5. SQL执行计划分析
        prompt_parts.append("\nSQL执行计划分析：")
        if execution_plan:
            # 如果提供了执行计划，直接使用
            prompt_parts.append(execution_plan)
        else:
            # 如果没有提供执行计划，生成基于元数据的执行计划分析
            generated_plan = self._generate_execution_plan(sql_statement, tables)
            prompt_parts.append(generated_plan)
        
        # 6. SQL评审规则（根据用户提供的详细规则）
        prompt_parts.append("\n请根据以下SQL评审规则进行分析：")
        
        # 6.1 建表规则
        prompt_parts.append("\n1. 建表规则：")
        prompt_parts.append("   • 是否涉及历史表")
        prompt_parts.append("   • 联机、定时、批量是否评估完全")
        prompt_parts.append("   • 主键/索引：必须有主键")
        prompt_parts.append("   • 联机查询：联机查询走索引或主键")
        prompt_parts.append("   • 数据量：表预期数据量做好评估，以应对后续业务调用")
        prompt_parts.append("   • 注释：表、字段有注释")
        prompt_parts.append("   • 数据量增长：上线后，一周内数据量预估，如表增长较快，需要说明清理或归档策略")
        prompt_parts.append("   • 分组分区：建表前考虑使用场景，访问量大数据量大的是否可以分组分区")
        prompt_parts.append("   • 字段类型：金额类型字段用decimal")
        
        # 6.2 表结构变更规则
        prompt_parts.append("\n2. 表结构变更规则：")
        prompt_parts.append("   • 是否涉及历史表")
        prompt_parts.append("   • 联机、定时、批量是否评估完全")
        prompt_parts.append("   • 影响范围：对应表的联机、定时、批量评估完全")
        prompt_parts.append("   • 联机影响：对应表是否为热点表，表结构修改的时间点是否影响联机（热点表24点后再变更），执行表结构变更耗时")
        prompt_parts.append("   • 注释：变更后类型定义合理（如字段类型调整），必须写注释")
        
        # 6.3 新建/修改索引规则
        prompt_parts.append("\n3. 新建/修改索引规则：")
        prompt_parts.append("   • 索引无冗余")
        prompt_parts.append("   • 执行后索引总数")
        prompt_parts.append("   • 索引添加前后耗时对比")
        prompt_parts.append("   • 是否热点表")
        prompt_parts.append("   • 更新表结构时间")
        prompt_parts.append("   • 索引个数：不超过5个，组合索引：列的个数控制在3个字段及以内，不能超过5个")
        prompt_parts.append("   • 索引设计：考虑索引字段的顺序：结合业务场景，是否合理，能建联合索引的不建单列索引")
        prompt_parts.append("   • 执行计划：新建/修改索引前后执行计划")
        
        # 6.4 数据量规则
        prompt_parts.append("\n4. 数据量规则：")
        prompt_parts.append("   • 生产表数据量（是否十万、百万级以上）")
        prompt_parts.append("   • 影响范围：应用中与索引相关的sql执行耗时")
        prompt_parts.append("   • SQL耗时：秒级")
        prompt_parts.append("   • 插入、更新、删除数据")
        prompt_parts.append("   • 是否已核对生产数据")
        prompt_parts.append("   • 大数据量变更：对表数据大量删除、导入、更新，且影响联机交易，需立即执行analyze提升SQL性能（OB3x默认每日2:00定时合并），执行后一直需要手动执行")
        prompt_parts.append("   • 备份：删除数据较大时，及时备份")
        prompt_parts.append("   • 变更前后核对：核对生产数据，是否与预期变更一致")
        prompt_parts.append("   • SQL耗时：插入、更新、删除数据，建表，耗时：毫秒级(或无感知)")
        
        # 7. 分析要求
        prompt_parts.append("\n请基于以上规则分析SQL语句，重点关注：")
        prompt_parts.append("1. SQL类型识别：判断是建表、表结构变更、索引操作还是数据操作")
        prompt_parts.append("2. 规则符合性检查：根据SQL类型检查对应的规则")
        prompt_parts.append("3. 风险评估：识别潜在的风险和问题")
        prompt_parts.append("4. 建议改进：提供具体的改进建议")
        prompt_parts.append("5. 综合评分：给出综合评分（0-10分）")
        
        # 8. 输出格式要求
        prompt_parts.append("\n请严格按照以下JSON格式回复，不要包含任何其他内容：")
        prompt_parts.append('''{
  "sql_type": "建表/表结构变更/索引操作/数据操作/查询",
  "rule_analysis": {
    "建表规则": {
      "涉及历史表": true/false,
      "评估完全": true/false,
      "主键检查": "通过/未通过",
      "索引检查": "通过/未通过",
      "数据量评估": "合理/不合理",
      "注释检查": "完整/不完整",
      "字段类型检查": "合理/不合理"
    },
    "表结构变更规则": {
      "涉及历史表": true/false,
      "评估完全": true/false,
      "影响范围评估": "完整/不完整",
      "联机影响评估": "合理/不合理",
      "注释检查": "完整/不完整"
    },
    "索引规则": {
      "索引冗余检查": "无冗余/有冗余",
      "索引总数": 数字,
      "索引设计合理性": "合理/不合理",
      "执行计划分析": "有/无"
    },
    "数据量规则": {
      "数据量级别": "十万以下/十万级/百万级/千万级以上",
      "SQL耗时评估": "毫秒级/秒级/分钟级",
      "备份策略": "有/无",
      "数据核对": "已核对/未核对"
    }
  },
  "risk_assessment": {
    "高风险问题": ["问题1", "问题2"],
    "中风险问题": ["问题1", "问题2"],
    "低风险问题": ["问题1", "问题2"]
  },
  "improvement_suggestions": ["建议1", "建议2", "建议3"],
  "overall_score": 0-10,
  "summary": "综合分析总结"
}''')
        
        prompt_parts.append("\n注意：请只回复JSON格式的内容，不要包含任何解释性文字。")
        
        # 组合所有部分
        prompt = "\n".join(prompt_parts)
        
        # 新的API只需要prompt参数
        payload = {
            "prompt": prompt
        }
        
        self.logger.debug(f"构建请求负载: SQL长度={len(sql_statement)}, 表数量={len(tables)}, prompt长度={len(prompt)}")
        return payload
    
    def _generate_dynamic_sql_examples(self, sql_statement: str, tables: List[Dict[str, Any]] = None) -> List[str]:
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
            response_text = response.text.strip()
            
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
            
            # 如果从answer字段解析到了数据，使用它
            if answer_data and isinstance(answer_data, dict):
                analysis_data = answer_data
                self.logger.info(f"使用answer字段中的分析数据，SQL类型: {analysis_data.get('sql_type', '未知')}")
            else:
                # 否则使用原始的response_data
                analysis_data = response_data
                self.logger.info("使用原始响应数据")
            
            # 处理分析数据（根据我们要求的SQL评审规则格式）
            # 我们要求大模型返回以下格式：
            # {
            #   "sql_type": "建表/表结构变更/索引操作/数据操作/查询",
            #   "rule_analysis": {...},
            #   "risk_assessment": {...},
            #   "improvement_suggestions": [...],
            #   "overall_score": 0-10,
            #   "summary": "..."
            # }
            
            # 提取SQL类型
            if 'sql_type' in analysis_data:
                result['sql_type'] = analysis_data['sql_type']
            
            # 提取规则分析
            if 'rule_analysis' in analysis_data:
                rule_analysis = analysis_data['rule_analysis']
                result['rule_analysis'] = rule_analysis
                
                # 计算规则符合性评分（确保rule_analysis是字典）
                if isinstance(rule_analysis, dict):
                    rule_score = self._calculate_rule_score(rule_analysis)
                    result['rule_score'] = rule_score
                else:
                    result['rule_score'] = 5.0
            
            # 提取风险评估
            if 'risk_assessment' in analysis_data:
                risk_assessment = analysis_data['risk_assessment']
                result['risk_assessment'] = risk_assessment
                
                # 计算风险评分（确保risk_assessment是字典）
                if isinstance(risk_assessment, dict):
                    risk_score = self._calculate_risk_score(risk_assessment)
                    result['risk_score'] = risk_score
                else:
                    result['risk_score'] = 5.0
            
            # 提取改进建议
            if 'improvement_suggestions' in analysis_data:
                improvement_suggestions = analysis_data['improvement_suggestions']
                result['improvement_suggestions'] = improvement_suggestions
                result['suggestions'] = improvement_suggestions
            
            # 提取综合评分
            if 'overall_score' in analysis_data:
                overall_score = analysis_data['overall_score']
                result['score'] = float(overall_score)
            else:
                # 如果没有综合评分，基于规则评分和风险评分计算
                rule_score = result.get('rule_score', 5.0)
                risk_score = result.get('risk_score', 5.0)
                result['score'] = (rule_score + risk_score) / 2.0
            
            # 提取总结
            if 'summary' in analysis_data:
                result['summary'] = analysis_data['summary']
                result['detailed_analysis'] = analysis_data['summary']
            
            # 如果没有提取到建议，使用改进建议或创建空列表
            if 'suggestions' not in result:
                result['suggestions'] = result.get('improvement_suggestions', [])
            
            # 如果没有详细分析，使用总结
            if 'detailed_analysis' not in result:
                result['detailed_analysis'] = result.get('summary', '')
            
            # 将整个分析数据作为分析结果
            result['analysis_result'] = analysis_data
            
            # 获取SQL类型
            sql_type = result.get('sql_type', '未知')
            
            self.logger.info(f"解析API响应成功，SQL类型: {sql_type}, 综合评分: {result.get('score', 'N/A')}")
            return result
            
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON解析失败: {str(e)}, 响应文本: {response.text[:200]}")
            raise ValueError(f"响应不是有效的JSON: {str(e)}")
        except Exception as e:
            self.logger.error(f"解析响应时发生错误: {str(e)}")
            raise
    
    def _safe_parse_llm_response_text(self, response_text: str) -> Dict[str, Any]:

        try:
            # ① 最外层：Python dict 字符串
            data = ast.literal_eval(response_text)
        except Exception as e:
            raise ValueError(f"无法解析最外层响应（非 Python dict）：{e}")

        # ② 尝试解析 answer（如果存在）
        try:
            answer = (
                data.get("raw_response", {})
                    .get("RSP_BODY", {})
                    .get("answer")
            )
        except AttributeError:
            return data

        if not isinstance(answer, str):
            return data

        try:
            # ③ answer 是“被转义的 JSON 字符串”，先反转义
            answer_str = ast.literal_eval(answer)

            # ④ 再 parse JSON
            answer_json = json.loads(answer_str)

            return answer_json if isinstance(answer_json, dict) else data

        except Exception as e:
            self.logger.warning(f"answer 字段解析失败，回退原始数据: {e}")
            return data

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
    
    def test_connection(self) -> bool:
        """
        测试API连接
        
        Returns:
            连接是否成功
        """
        try:
            if not self.ai_config.get('api_url'):
                self.logger.error("未配置API地址")
                return False
            
            # 发送简单的测试请求
            test_payload = {
                "sql_statement": "SELECT 1",
                "tables": [],
                "test": True
            }
            
            response = self._call_api_with_retry(test_payload)
            
            if response.status_code == 200:
                self.logger.info("API连接测试成功")
                return True
            else:
                self.logger.warning(f"API连接测试失败，状态码: {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"API连接测试异常: {str(e)}")
            return False
    
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

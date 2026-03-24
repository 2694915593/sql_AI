#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
动态SQL解析器模块
负责处理包含XML标签的动态SQL（如MyBatis的动态SQL）
"""

import re
import json
from typing import Dict, Any, List, Optional, Tuple, Set
from utils.logger import LogMixin
from ai_integration.model_client import ModelClient


class DynamicSQLParser(LogMixin):
    """动态SQL解析器，处理包含XML标签的动态SQL"""
    
    def __init__(self, config_manager, logger=None, model_client=None):
        """
        初始化动态SQL解析器
        
        Args:
            config_manager: 配置管理器
            logger: 日志记录器
            model_client: 大模型客户端（可选）
        """
        self.config_manager = config_manager
        
        if logger:
            self.set_logger(logger)
        
        # 初始化大模型客户端
        if model_client:
            self.model_client = model_client
        else:
            from ai_integration.model_client import ModelClient
            self.model_client = ModelClient(config_manager, logger)
        
        # 获取优化配置
        self.optimization_config = config_manager.get_optimization_config()
        self.enable_dynamic_sql_parsing = self.optimization_config.get('enable_dynamic_sql_parsing', True)
        self.dynamic_sql_timeout = self.optimization_config.get('dynamic_sql_timeout', 30)
        self.max_dynamic_sql_retries = self.optimization_config.get('max_dynamic_sql_retries', 3)
        
        # 常见动态SQL标签
        self.dynamic_tags = {
            'select': ['<select', '</select>'],
            'insert': ['<insert', '</insert>'],
            'update': ['<update', '</update>'],
            'delete': ['<delete', '</delete>'],
            'if': ['<if', '</if>'],
            'where': ['<where', '</where>'],
            'set': ['<set', '</set>'],
            'foreach': ['<foreach', '</foreach>'],
            'choose': ['<choose', '</choose>'],
            'when': ['<when', '</when>'],
            'otherwise': ['<otherwise', '</otherwise>'],
            'trim': ['<trim', '</trim>'],
            'bind': ['<bind', '/>'],
            'include': ['<include', '/>']
        }
        
        self.logger.info("动态SQL解析器初始化完成")
    
    def is_dynamic_sql(self, sql_text: str) -> bool:
        """
        检查是否是动态SQL（包含XML标签）
        
        Args:
            sql_text: SQL文本
            
        Returns:
            是否是动态SQL
        """
        if not sql_text or not isinstance(sql_text, str):
            return False
        
        # 检查是否包含任何动态SQL标签
        sql_lower = sql_text.lower()
        
        for tag, patterns in self.dynamic_tags.items():
            for pattern in patterns:
                if pattern in sql_lower:
                    return True
        
        # 检查是否包含XML样式的标签（以<开头，以>结尾）
        xml_pattern = r'<[a-zA-Z_][^>]*>'
        if re.search(xml_pattern, sql_lower):
            return True
        
        return False
    
    def parse_dynamic_sql(self, sql_text: str, table_metadata: List[Dict[str, Any]] = None, 
                         db_alias: str = '') -> List[Dict[str, Any]]:
        """
        解析动态SQL，返回可能的几种标准SQL场景
        
        Args:
            sql_text: 动态SQL文本
            table_metadata: 表元数据列表
            db_alias: 数据库别名
            
        Returns:
            解析后的标准SQL场景列表
        """
        if not self.enable_dynamic_sql_parsing:
            self.logger.warning("动态SQL解析功能已禁用，跳过解析")
            return []
        
        if not self.is_dynamic_sql(sql_text):
            self.logger.debug("不是动态SQL，无需解析")
            return []
        
        self.logger.info("开始解析动态SQL")
        
        try:
            # 第一层：尝试基础标签解析
            basic_scenarios = self._parse_with_basic_rules(sql_text)
            
            if basic_scenarios and len(basic_scenarios) > 0:
                self.logger.info(f"基础规则解析成功，生成 {len(basic_scenarios)} 个场景")
                return basic_scenarios
            
            # 第二层：调用大模型智能解析
            self.logger.info("基础规则解析失败，尝试调用大模型智能解析")
            ai_scenarios = self._parse_with_ai(sql_text, table_metadata, db_alias)
            
            if ai_scenarios and len(ai_scenarios) > 0:
                self.logger.info(f"大模型解析成功，生成 {len(ai_scenarios)} 个场景")
                return ai_scenarios
            
            self.logger.warning("动态SQL解析失败，所有方法都未能生成有效场景")
            return []
            
        except Exception as e:
            self.logger.error(f"解析动态SQL时发生错误: {str(e)}", exc_info=True)
            return []
    
    def _parse_with_basic_rules(self, sql_text: str) -> List[Dict[str, Any]]:
        """
        使用基础规则解析动态SQL
        
        Args:
            sql_text: 动态SQL文本
            
        Returns:
            解析后的标准SQL场景列表
        """
        scenarios = []
        sql_lower = sql_text.lower()
        
        # 尝试提取最外层的SQL语句标签
        outer_tag = None
        for tag, patterns in self.dynamic_tags.items():
            start_pattern = patterns[0]
            if start_pattern in sql_lower:
                outer_tag = tag
                break
        
        if not outer_tag:
            # 如果没有找到明显的标签，尝试提取SQL内容
            return self._extract_sql_from_mixed_content(sql_text)
        
        # 根据标签类型处理
        if outer_tag in ['select', 'insert', 'update', 'delete']:
            # 对于SQL语句标签，尝试提取SQL主体
            sql_body = self._extract_sql_from_xml_tag(sql_text, outer_tag)
            if sql_body:
                # 处理SQL主体中的动态标签
                processed_sql = self._process_inner_dynamic_tags(sql_body)
                
                # 生成基础场景
                scenario = {
                    'name': f'基础{outer_tag.capitalize()}场景',
                    'description': f'从<{outer_tag}>标签提取的基础SQL',
                    'sql': processed_sql,
                    'confidence': 0.7,
                    'parameters': self._extract_parameters(processed_sql)
                }
                scenarios.append(scenario)
        
        # 尝试生成几种可能的场景
        scenarios.extend(self._generate_basic_scenarios(sql_text, outer_tag))
        
        return scenarios
    
    def _extract_sql_from_xml_tag(self, sql_text: str, tag_name: str) -> Optional[str]:
        """
        从XML标签中提取SQL内容
        
        Args:
            sql_text: 包含XML标签的SQL文本
            tag_name: 标签名
            
        Returns:
            提取的SQL内容
        """
        # 构建正则表达式模式
        start_pattern = f'<{tag_name}[^>]*>'
        end_pattern = f'</{tag_name}>'
        
        # 查找开始标签
        start_match = re.search(start_pattern, sql_text, re.IGNORECASE | re.DOTALL)
        if not start_match:
            return None
        
        # 查找结束标签
        end_match = re.search(end_pattern, sql_text[start_match.end():], re.IGNORECASE | re.DOTALL)
        if not end_match:
            return None
        
        # 提取标签间的内容
        content_start = start_match.end()
        content_end = start_match.end() + end_match.start()
        content = sql_text[content_start:content_end].strip()
        
        return content
    
    def _extract_sql_from_mixed_content(self, sql_text: str) -> List[Dict[str, Any]]:
        """
        从混合内容中提取SQL
        
        Args:
            sql_text: 混合内容文本
            
        Returns:
            提取的SQL场景列表
        """
        scenarios = []
        
        # 尝试查找看起来像SQL的部分
        sql_patterns = [
            r'\bselect\b.*?\bfrom\b.*?(?:where\b.*?)?(?:;|$)',  # SELECT语句
            r'\binsert\s+into\b.*?\bvalues\b.*?(?:;|$)',  # INSERT语句
            r'\bupdate\b.*?\bset\b.*?(?:where\b.*?)?(?:;|$)',  # UPDATE语句
            r'\bdelete\s+from\b.*?(?:where\b.*?)?(?:;|$)',  # DELETE语句
        ]
        
        for pattern in sql_patterns:
            matches = re.findall(pattern, sql_text, re.IGNORECASE | re.DOTALL)
            for match in matches:
                if len(match.strip()) > 10:  # 确保不是太短的片段
                    sql = match.strip()
                    # 清理SQL（移除可能的标签残留）
                    sql = self._clean_sql_fragment(sql)
                    
                    scenario = {
                        'name': '提取的SQL片段',
                        'description': '从混合内容中提取的SQL语句',
                        'sql': sql,
                        'confidence': 0.5,
                        'parameters': self._extract_parameters(sql)
                    }
                    scenarios.append(scenario)
        
        return scenarios
    
    def _clean_sql_fragment(self, sql: str) -> str:
        """清理SQL片段中的标签残留"""
        if not sql:
            return ""
        
        # 移除XML标签
        sql = re.sub(r'<[^>]+>', '', sql)
        # 移除CDATA标记
        sql = re.sub(r'<!\[CDATA\[|\]\]>', '', sql)
        # 移除多余的空格和换行
        sql = ' '.join(sql.split())
        
        # 检查并修复可能的SQL关键字丢失问题
        sql = self._fix_sql_keywords_if_needed(sql)
        
        return sql
    
    def _fix_sql_keywords_if_needed(self, sql: str) -> str:
        """
        修复SQL关键字丢失问题
        
        Args:
            sql: SQL语句
            
        Returns:
            修复后的SQL语句
        """
        if not sql:
            return sql
        
        sql_upper = sql.upper()
        
        # 修复UPDATE语句缺少SET关键字的问题
        if sql_upper.startswith('UPDATE'):
            if 'SET' not in sql_upper:
                # 找到UPDATE后面的表名
                words = sql.split()
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
                        pattern = r'(UPDATE\s+\w+)'
                        fixed_sql = re.sub(pattern, r'\1 SET', fixed_sql, flags=re.IGNORECASE)
                    
                    return fixed_sql
        
        # 修复INSERT语句缺少VALUES关键字的问题
        elif sql_upper.startswith('INSERT'):
            # 检查INSERT语句格式
            if 'VALUES' not in sql_upper and 'SELECT' not in sql_upper:
                # 查找INSERT INTO table_name (columns) 模式或INSERT INTO table_name 模式
                # 模式1: INSERT INTO table_name (columns) ...
                pattern1 = r'INSERT\s+(?:INTO\s+)?\w+\s*\([^)]+\)'
                # 模式2: INSERT INTO table_name ... (没有列名括号)
                pattern2 = r'INSERT\s+(?:INTO\s+)?\w+'
                
                # 先尝试模式1 (有列名括号)
                match = re.search(pattern1, sql, re.IGNORECASE)
                if match:
                    # 在列列表后添加VALUES
                    insert_part = match.group(0)
                    rest_part = sql[match.end():].strip()
                    if rest_part:
                        # 检查是否已经有VALUES关键字
                        if not rest_part.upper().startswith('VALUES'):
                            # 添加VALUES关键字
                            fixed_sql = insert_part + ' VALUES ' + rest_part
                            return fixed_sql
                else:
                    # 尝试模式2 (没有列名括号)
                    match = re.search(pattern2, sql, re.IGNORECASE)
                    if match:
                        # 找到表名后的位置
                        insert_part = match.group(0)
                        rest_part = sql[match.end():].strip()
                        if rest_part:
                            # 检查是否已经有VALUES关键字
                            if not rest_part.upper().startswith('VALUES'):
                                # 检查rest_part是否以(开头，表示VALUES列表
                                if rest_part.startswith('('):
                                    # 直接添加VALUES关键字
                                    fixed_sql = insert_part + ' VALUES ' + rest_part
                                else:
                                    # 可能是其他格式，尝试添加VALUES
                                    fixed_sql = insert_part + ' VALUES ' + rest_part
                                return fixed_sql
        
        # 修复DELETE语句缺少FROM关键字的问题（某些数据库允许省略FROM）
        elif sql_upper.startswith('DELETE'):
            if not sql_upper.startswith('DELETE FROM'):
                # 检查DELETE后面是否有表名
                pattern = r'DELETE\s+(\w+)'
                match = re.match(pattern, sql, re.IGNORECASE)
                if match:
                    # DELETE table_name ... -> DELETE FROM table_name ...
                    table_name = match.group(1)
                    rest = sql[match.end():].strip()
                    fixed_sql = f'DELETE FROM {table_name} {rest}'
                    return fixed_sql
        
        # 修复SELECT语句缺少FROM关键字的问题（某些特殊情况）
        elif sql_upper.startswith('SELECT'):
            # 检查SELECT语句是否简单到可能丢失FROM
            # 这里只处理非常明显的情况
            if 'FROM' not in sql_upper and '*' in sql:
                # 简单的SELECT * table_name 格式
                pattern = r'SELECT\s+\*\s+(\w+)'
                match = re.match(pattern, sql, re.IGNORECASE)
                if match:
                    table_name = match.group(1)
                    rest = sql[match.end():].strip()
                    fixed_sql = f'SELECT * FROM {table_name} {rest}'
                    return fixed_sql
        
        return sql
    
    def _process_inner_dynamic_tags(self, sql_body: str) -> str:
        """
        处理SQL主体中的动态标签

        Args:
            sql_body: SQL主体文本

        Returns:
            处理后的SQL
        """
        processed = sql_body

        # 处理<if>标签：假设条件为真
        processed = self._process_if_tags(processed)

        # 处理<where>标签：转换为WHERE
        processed = self._process_where_tags(processed)

        # 处理<set>标签：转换为SET
        processed = self._process_set_tags(processed)

        # 处理<foreach>标签：生成一个循环项
        processed = self._process_foreach_tags(processed)
        
        # 处理其他标签
        processed = self._process_other_tags(processed)
        
        # 清理结果
        processed = self._clean_processed_sql(processed)
        
        return processed
    
    def _process_if_tags(self, sql: str) -> str:
        """处理<if>标签"""
        # 简单处理：移除<if test="...">和</if>，保留内容
        # 假设条件为真，所以保留内容
        pattern = r'<if\s+[^>]*>(.*?)</if>'
        def replace_if(match):
            return match.group(1).strip()
        
        result = re.sub(pattern, replace_if, sql, flags=re.IGNORECASE | re.DOTALL)
        
        # 处理嵌套的<if>标签（多次处理）
        while re.search(pattern, result, re.IGNORECASE | re.DOTALL):
            result = re.sub(pattern, replace_if, result, flags=re.IGNORECASE | re.DOTALL)
        
        return result
    
    def _process_where_tags(self, sql: str) -> str:
        """处理<where>标签"""
        # 将<where>转换为WHERE，并移除</where>
        # 注意：需要处理<where>标签内的条件逻辑
        pattern = r'<where>(.*?)</where>'
        def replace_where(match):
            content = match.group(1).strip()
            # 如果内容以AND或OR开头，移除它们（<where>标签会自动处理）
            content = re.sub(r'^\s*(AND|OR)\s+', '', content, flags=re.IGNORECASE)
            return f'WHERE {content}'
        
        result = re.sub(pattern, replace_where, sql, flags=re.IGNORECASE | re.DOTALL)
        return result
    
    def _process_set_tags(self, sql: str) -> str:
        """处理<set>标签"""
        # 将<set>转换为SET，并移除</set>
        pattern = r'<set>(.*?)</set>'
        def replace_set(match):
            content = match.group(1).strip()
            # 如果内容以逗号结尾，移除它
            content = re.sub(r',\s*$', '', content)
            return f'SET {content}'
        
        result = re.sub(pattern, replace_set, sql, flags=re.IGNORECASE | re.DOTALL)
        return result
    
    def _process_foreach_tags(self, sql: str) -> str:
        """处理<foreach>标签"""
        # 处理<foreach>标签，生成一个示例项
        pattern = r'<foreach\s+[^>]*>(.*?)</foreach>'
        
        def replace_foreach(match):
            content = match.group(1).strip()
            # 提取属性信息（如collection, item, separator等）
            tag_start = match.string.rfind('<foreach', 0, match.start())
            if tag_start >= 0:
                tag_end = match.string.find('>', tag_start)
                if tag_end > tag_start:
                    tag_content = match.string[tag_start:tag_end]
                    # 提取collection属性
                    collection_match = re.search(r'collection\s*=\s*["\']([^"\']+)["\']', tag_content, re.IGNORECASE)
                    if collection_match:
                        collection_name = collection_match.group(1)
                        # 生成一个示例项
                        # 例如：#{item.id} -> #{collection_name[0].id}
                        # 这里简化处理，直接使用参数占位符
                        content = content.replace('#{item.', f'#{{{collection_name}.')
            
            return content
        
        result = re.sub(pattern, replace_foreach, sql, flags=re.IGNORECASE | re.DOTALL)
        return result
    
    def _process_other_tags(self, sql: str) -> str:
        """处理其他动态标签"""
        # 处理<choose>/<when>/<otherwise>标签
        # 选择第一个<when>条件
        choose_pattern = r'<choose>(.*?)</choose>'
        
        def replace_choose(match):
            choose_content = match.group(1)
            # 查找第一个<when>标签
            when_pattern = r'<when\s+[^>]*>(.*?)</when>'
            when_match = re.search(when_pattern, choose_content, re.IGNORECASE | re.DOTALL)
            if when_match:
                return when_match.group(1).strip()
            
            # 如果没有<when>，查找<otherwise>
            otherwise_pattern = r'<otherwise>(.*?)</otherwise>'
            otherwise_match = re.search(otherwise_pattern, choose_content, re.IGNORECASE | re.DOTALL)
            if otherwise_match:
                return otherwise_match.group(1).strip()
            
            return ''
        
        result = re.sub(choose_pattern, replace_choose, sql, flags=re.IGNORECASE | re.DOTALL)
        
        # 处理<trim>标签（简化处理，移除标签）
        result = re.sub(r'<trim\s+[^>]*>', '', result, flags=re.IGNORECASE)
        result = re.sub(r'</trim>', '', result, flags=re.IGNORECASE)
        
        # 处理<bind>标签（移除）
        result = re.sub(r'<bind\s+[^>]*/>', '', result, flags=re.IGNORECASE)
        
        # 处理<include>标签（移除）
        result = re.sub(r'<include\s+[^>]*/>', '', result, flags=re.IGNORECASE)
        
        return result
    
    def _clean_processed_sql(self, sql: str) -> str:
        """清理处理后的SQL"""
        # 移除多余的空白字符
        sql = ' '.join(sql.split())
        
        # 确保SQL语句以分号结尾
        if not sql.endswith(';'):
            sql = sql + ';'
        
        # 修复可能的语法问题
        # 例如：WHERE AND -> WHERE
        sql = re.sub(r'WHERE\s+AND\s+', 'WHERE ', sql, flags=re.IGNORECASE)
        sql = re.sub(r'WHERE\s+OR\s+', 'WHERE ', sql, flags=re.IGNORECASE)
        
        # 移除WHERE后面的空条件
        sql = re.sub(r'WHERE\s*;', ';', sql, flags=re.IGNORECASE)
        
        return sql
    
    def _generate_basic_scenarios(self, sql_text: str, outer_tag: str) -> List[Dict[str, Any]]:
        """
        生成几种基本的SQL场景
        
        Args:
            sql_text: 原始SQL文本
            outer_tag: 最外层标签
            
        Returns:
            生成的场景列表
        """
        scenarios = []
        
        if outer_tag == 'select':
            # 为SELECT语句生成几种可能的场景
            scenarios.extend(self._generate_select_scenarios(sql_text))
        elif outer_tag == 'insert':
            # 为INSERT语句生成几种可能的场景
            scenarios.extend(self._generate_insert_scenarios(sql_text))
        elif outer_tag == 'update':
            # 为UPDATE语句生成几种可能的场景
            scenarios.extend(self._generate_update_scenarios(sql_text))
        elif outer_tag == 'delete':
            # 为DELETE语句生成几种可能的场景
            scenarios.extend(self._generate_delete_scenarios(sql_text))
        
        return scenarios
    
    def _generate_select_scenarios(self, sql_text: str) -> List[Dict[str, Any]]:
        """为SELECT语句生成场景"""
        scenarios = []
        
        # 场景1：基础SELECT（所有条件为真）
        base_sql = self._process_inner_dynamic_tags(sql_text)
        if base_sql and len(base_sql) > 10:
            scenarios.append({
                'name': '基础查询场景',
                'description': '所有条件为真的SELECT语句',
                'sql': base_sql,
                'confidence': 0.7,
                'parameters': self._extract_parameters(base_sql)
            })
        
        # 场景2：无WHERE条件的SELECT
        # 尝试移除WHERE条件
        no_where_sql = re.sub(r'WHERE\s+.*?(?:ORDER\s+BY|GROUP\s+BY|HAVING|LIMIT|;|$)', '', base_sql, 
                             flags=re.IGNORECASE | re.DOTALL)
        if no_where_sql != base_sql and len(no_where_sql) > 10:
            scenarios.append({
                'name': '无WHERE条件查询',
                'description': '移除所有WHERE条件的SELECT语句',
                'sql': no_where_sql,
                'confidence': 0.6,
                'parameters': self._extract_parameters(no_where_sql)
            })
        
        # 场景3：有限结果集查询
        # 添加LIMIT子句
        if 'LIMIT' not in base_sql.upper() and 'SELECT' in base_sql.upper():
            limit_sql = base_sql
            if limit_sql.endswith(';'):
                limit_sql = limit_sql[:-1] + ' LIMIT 10;'
            else:
                limit_sql = limit_sql + ' LIMIT 10'
            scenarios.append({
                'name': '有限结果查询',
                'description': '添加LIMIT 10限制的SELECT语句',
                'sql': limit_sql,
                'confidence': 0.5,
                'parameters': self._extract_parameters(limit_sql)
            })
        
        return scenarios
    
    def _generate_insert_scenarios(self, sql_text: str) -> List[Dict[str, Any]]:
        """为INSERT语句生成场景"""
        scenarios = []
        
        # 场景1：基础INSERT
        base_sql = self._process_inner_dynamic_tags(sql_text)
        if base_sql and len(base_sql) > 10:
            scenarios.append({
                'name': '基础插入场景',
                'description': '所有字段都有的INSERT语句',
                'sql': base_sql,
                'confidence': 0.7,
                'parameters': self._extract_parameters(base_sql)
            })
        
        # 场景2：最小字段插入
        # 尝试减少字段数量（简化处理）
        if base_sql and 'VALUES' in base_sql.upper():
            # 提取表名
            table_match = re.search(r'INSERT\s+INTO\s+(\w+)', base_sql, re.IGNORECASE)
            if table_match:
                table_name = table_match.group(1)
                # 创建简化版本（假设只有必要的字段）
                simple_sql = f"INSERT INTO {table_name} (id, name) VALUES (#id, #name);"
                scenarios.append({
                    'name': '最小字段插入',
                    'description': '只包含必要字段的简化INSERT语句',
                    'sql': simple_sql,
                    'confidence': 0.5,
                    'parameters': self._extract_parameters(simple_sql)
                })
        
        return scenarios
    
    def _generate_update_scenarios(self, sql_text: str) -> List[Dict[str, Any]]:
        """为UPDATE语句生成场景"""
        scenarios = []
        
        # 场景1：基础UPDATE
        base_sql = self._process_inner_dynamic_tags(sql_text)
        if base_sql and len(base_sql) > 10:
            scenarios.append({
                'name': '基础更新场景',
                'description': '所有SET字段都有的UPDATE语句',
                'sql': base_sql,
                'confidence': 0.7,
                'parameters': self._extract_parameters(base_sql)
            })
        
        # 场景2：单字段更新
        if base_sql and 'SET' in base_sql.upper():
            # 提取第一个SET字段
            set_match = re.search(r'SET\s+(.*?)(?:WHERE|;)', base_sql, re.IGNORECASE | re.DOTALL)
            if set_match:
                set_clause = set_match.group(1)
                # 提取第一个字段赋值
                first_field_match = re.search(r'(\w+)\s*=\s*[^,]+', set_clause)
                if first_field_match:
                    field_name = first_field_match.group(1)
                    # 创建简化版本
                    table_match = re.search(r'UPDATE\s+(\w+)', base_sql, re.IGNORECASE)
                    if table_match:
                        table_name = table_match.group(1)
                        simple_sql = f"UPDATE {table_name} SET {field_name} = #{field_name} WHERE id = #{id};"
                        scenarios.append({
                            'name': '单字段更新',
                            'description': '只更新单个字段的简化UPDATE语句',
                            'sql': simple_sql,
                            'confidence': 0.5,
                            'parameters': self._extract_parameters(simple_sql)
                        })
        
        return scenarios
    
    def _generate_delete_scenarios(self, sql_text: str) -> List[Dict[str, Any]]:
        """为DELETE语句生成场景"""
        scenarios = []
        
        # 场景1：基础DELETE
        base_sql = self._process_inner_dynamic_tags(sql_text)
        if base_sql and len(base_sql) > 10:
            scenarios.append({
                'name': '基础删除场景',
                'description': '有WHERE条件的DELETE语句',
                'sql': base_sql,
                'confidence': 0.7,
                'parameters': self._extract_parameters(base_sql)
            })
        
        # 场景2：谨慎删除（添加LIMIT）
        if base_sql and 'DELETE' in base_sql.upper() and 'LIMIT' not in base_sql.upper():
            limit_sql = base_sql
            if limit_sql.endswith(';'):
                limit_sql = limit_sql[:-1] + ' LIMIT 1;'
            else:
                limit_sql = limit_sql + ' LIMIT 1'
            scenarios.append({
                'name': '谨慎删除',
                'description': '添加LIMIT 1限制的安全DELETE语句',
                'sql': limit_sql,
                'confidence': 0.6,
                'parameters': self._extract_parameters(limit_sql)
            })
        
        return scenarios
    
    def _extract_parameters(self, sql: str) -> List[Dict[str, Any]]:
        """
        从SQL中提取参数
        
        Args:
            sql: SQL语句
            
        Returns:
            参数列表
        """
        params = []
        # 查找#{参数名}格式的参数
        param_pattern = r'#\{([^}]+)\}'
        matches = re.findall(param_pattern, sql)
        
        for param_name in matches:
            param_info = {
                'name': param_name,
                'type': self._guess_param_type(param_name),
                'position': sql.find(f'#{{{param_name}}}')
            }
            params.append(param_info)
        
        return params
    
    def _guess_param_type(self, param_name: str) -> str:
        """
        根据参数名猜测参数类型
        
        Args:
            param_name: 参数名
            
        Returns:
            参数类型
        """
        param_lower = param_name.lower()
        
        # 布尔相关参数
        bool_patterns = ['is_', 'has_', 'can_', 'enable', 'disable', 'active', 'inactive', 'valid', 'invalid']
        if any(param_lower.startswith(pattern) for pattern in bool_patterns):
            return 'boolean'
        
        # 检查常见布尔参数名
        bool_keywords = ['flag', 'status', 'deleted', 'enabled', 'disabled', 'visible', 'hidden']
        if any(keyword in param_lower for keyword in bool_keywords):
            return 'boolean'
        
        # 时间相关参数
        time_patterns = ['time', 'date', 'datetime', 'timestamp', 'create', 'update', 'modify']
        if any(pattern in param_lower for pattern in time_patterns):
            return 'datetime'
        
        # 数字相关参数
        num_patterns = ['id', 'num', 'no', 'count', 'amount', 'quantity', 'qty', 'price', 'cost']
        if any(pattern in param_lower for pattern in num_patterns):
            return 'number'
        
        # 默认字符串类型
        return 'string'
    
    def _parse_with_ai(self, sql_text: str, table_metadata: List[Dict[str, Any]] = None, 
                      db_alias: str = '') -> List[Dict[str, Any]]:
        """
        调用大模型智能解析动态SQL
        
        Args:
            sql_text: 动态SQL文本
            table_metadata: 表元数据列表
            db_alias: 数据库别名
            
        Returns:
            解析后的标准SQL场景列表
        """
        try:
            # 构建请求数据
            request_data = {
                'dynamic_sql': sql_text,
                'db_alias': db_alias,
                'request_type': 'dynamic_sql_parsing'
            }
            
            if table_metadata:
                request_data['tables'] = table_metadata
            
            # 调用大模型API
            # 注意：这里需要扩展ModelClient以支持动态SQL解析请求
            # 暂时使用现有的analyze_sql方法，但需要调整prompt
            ai_response = self._call_ai_for_dynamic_sql(sql_text, table_metadata, db_alias)
            
            # 解析AI响应
            scenarios = self._parse_ai_response(ai_response)
            
            return scenarios
            
        except Exception as e:
            self.logger.error(f"调用大模型解析动态SQL失败: {str(e)}", exc_info=True)
            return []
    
    def _call_ai_for_dynamic_sql(self, sql_text: str, table_metadata: List[Dict[str, Any]] = None,
                                db_alias: str = '') -> Dict[str, Any]:
        """
        调用大模型解析动态SQL
        
        Args:
            sql_text: 动态SQL文本
            table_metadata: 表元数据列表
            db_alias: 数据库别名
            
        Returns:
            AI响应数据
        """
        # 构建专门的prompt用于动态SQL解析
        prompt = self._build_dynamic_sql_prompt(sql_text, table_metadata, db_alias)
        
        # 创建请求数据
        request_data = {
            'sql_statement': sql_text,
            'tables': table_metadata or [],
            'db_alias': db_alias,
            'prompt': prompt
        }
        
        # 调用大模型API
        try:
            response = self.model_client.analyze_sql(request_data)
            return response
        except Exception as e:
            self.logger.error(f"调用大模型API失败: {str(e)}")
            raise
    
    def _build_dynamic_sql_prompt(self, sql_text: str, table_metadata: List[Dict[str, Any]] = None,
                                 db_alias: str = '') -> str:
        """
        构建动态SQL解析的prompt
        
        Args:
            sql_text: 动态SQL文本
            table_metadata: 表元数据列表
            db_alias: 数据库别名
            
        Returns:
            prompt文本
        """
        prompt_parts = []
        
        prompt_parts.append("请帮我解析以下动态SQL语句，生成几种可能的标准SQL场景。")
        prompt_parts.append("动态SQL可能包含XML标签（如<select>, <if>, <where>等），需要转换为标准SQL。")
        prompt_parts.append("")
        
        prompt_parts.append("动态SQL语句：")
        prompt_parts.append(sql_text)
        prompt_parts.append("")
        
        if db_alias:
            prompt_parts.append(f"数据库：{db_alias}")
            prompt_parts.append("")
        
        if table_metadata:
            prompt_parts.append("表结构信息：")
            for i, table in enumerate(table_metadata[:3], 1):  # 只显示前3个表
                table_name = table.get('table_name', '未知表')
                columns = table.get('columns', [])
                prompt_parts.append(f"表{i}：{table_name}")
                if columns:
                    for col in columns[:5]:  # 只显示前5个字段
                        col_name = col.get('name', '未知')
                        col_type = col.get('type', '未知')
                        prompt_parts.append(f"  - {col_name} ({col_type})")
                prompt_parts.append("")
        
        prompt_parts.append("请生成3-5种可能的SQL场景，考虑不同的参数组合和条件分支。")
        prompt_parts.append("每种场景应包括：")
        prompt_parts.append("1. 场景名称")
        prompt_parts.append("2. 场景描述")
        prompt_parts.append("3. 完整的标准SQL语句")
        prompt_parts.append("4. 使用的参数列表")
        prompt_parts.append("5. 置信度（0-1之间）")
        prompt_parts.append("")
        
        prompt_parts.append("请以JSON格式回复，结构如下：")
        prompt_parts.append('''{
  "scenarios": [
    {
      "name": "场景名称",
      "description": "场景描述",
      "sql": "完整的标准SQL语句",
      "parameters": [
        {"name": "参数名", "type": "参数类型", "description": "参数描述"}
      ],
      "confidence": 0.8
    }
  ]
}''')
        
        return "\n".join(prompt_parts)
    
    def _parse_ai_response(self, ai_response: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        解析AI响应，提取SQL场景
        
        Args:
            ai_response: AI响应数据
            
        Returns:
            SQL场景列表
        """
        scenarios = []
        
        try:
            # 尝试从AI响应中提取场景
            if 'analysis_result' in ai_response:
                analysis_result = ai_response['analysis_result']
                if isinstance(analysis_result, dict):
                    # 检查是否有scenarios字段
                    if 'scenarios' in analysis_result and isinstance(analysis_result['scenarios'], list):
                        for scenario in analysis_result['scenarios']:
                            if isinstance(scenario, dict) and 'sql' in scenario:
                                # 标准化场景格式
                                standardized = self._standardize_scenario(scenario)
                                scenarios.append(standardized)
            
            # 如果从analysis_result中没有找到，尝试从raw_response中查找
            if not scenarios and 'raw_response' in ai_response:
                raw_response = ai_response['raw_response']
                # 尝试解析raw_response中的场景
                parsed_scenarios = self._extract_scenarios_from_raw_response(raw_response)
                scenarios.extend(parsed_scenarios)
            
        except Exception as e:
            self.logger.error(f"解析AI响应失败: {str(e)}")
        
        return scenarios
    
    def _extract_scenarios_from_raw_response(self, raw_response: Any) -> List[Dict[str, Any]]:
        """从原始响应中提取场景"""
        scenarios = []
        
        try:
            # 如果raw_response是字符串，尝试解析为JSON
            if isinstance(raw_response, str):
                try:
                    parsed = json.loads(raw_response)
                    return self._extract_scenarios_from_parsed(parsed)
                except json.JSONDecodeError:
                    # 如果不是JSON，尝试从文本中提取SQL语句
                    return self._extract_sql_from_text(raw_response)
            
            # 如果raw_response是字典或列表
            elif isinstance(raw_response, (dict, list)):
                return self._extract_scenarios_from_parsed(raw_response)
                
        except Exception as e:
            self.logger.debug(f"从原始响应提取场景失败: {str(e)}")
        
        return scenarios
    
    def _extract_scenarios_from_parsed(self, parsed_data: Any) -> List[Dict[str, Any]]:
        """从解析的数据中提取场景"""
        scenarios = []
        
        if isinstance(parsed_data, dict):
            # 检查是否有scenarios字段
            if 'scenarios' in parsed_data and isinstance(parsed_data['scenarios'], list):
                for scenario in parsed_data['scenarios']:
                    if isinstance(scenario, dict) and 'sql' in scenario:
                        standardized = self._standardize_scenario(scenario)
                        scenarios.append(standardized)
            
            # 检查其他可能的字段
            for key, value in parsed_data.items():
                if isinstance(value, list) and key.lower() in ['sql_list', 'queries', 'statements']:
                    for item in value:
                        if isinstance(item, str) and item.strip():
                            scenario = {
                                'name': f'提取的SQL语句',
                                'description': f'从{key}字段提取的SQL',
                                'sql': item.strip(),
                                'confidence': 0.5,
                                'parameters': self._extract_parameters(item.strip())
                            }
                            scenarios.append(scenario)
        
        elif isinstance(parsed_data, list):
            for item in parsed_data:
                if isinstance(item, str) and item.strip():
                    scenario = {
                        'name': '提取的SQL语句',
                        'description': '从列表提取的SQL',
                        'sql': item.strip(),
                        'confidence': 0.5,
                        'parameters': self._extract_parameters(item.strip())
                    }
                    scenarios.append(scenario)
        
        return scenarios
    
    def _extract_sql_from_text(self, text: str) -> List[Dict[str, Any]]:
        """从文本中提取SQL语句"""
        scenarios = []
        
        # 查找SQL语句模式
        sql_patterns = [
            r'```sql\s*(.*?)\s*```',  # Markdown代码块
            r'```\s*(SELECT.*?)\s*```',  # SELECT语句代码块
            r'```\s*(INSERT.*?)\s*```',  # INSERT语句代码块
            r'```\s*(UPDATE.*?)\s*```',  # UPDATE语句代码块
            r'```\s*(DELETE.*?)\s*```',  # DELETE语句代码块
            r'SELECT\s+.*?\s+FROM\s+.*?(?:WHERE\s+.*?)?(?:;|$)',  # SELECT语句
            r'INSERT\s+INTO\s+.*?\s+VALUES\s+.*?(?:;|$)',  # INSERT语句
            r'UPDATE\s+.*?\s+SET\s+.*?(?:WHERE\s+.*?)?(?:;|$)',  # UPDATE语句
            r'DELETE\s+FROM\s+.*?(?:WHERE\s+.*?)?(?:;|$)',  # DELETE语句
        ]
        
        for pattern in sql_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE | re.DOTALL)
            for match in matches:
                sql = match.strip()
                if len(sql) > 10:  # 确保不是太短的片段
                    scenario = {
                        'name': '从文本提取的SQL',
                        'description': '从AI响应文本中提取的SQL语句',
                        'sql': sql,
                        'confidence': 0.4,
                        'parameters': self._extract_parameters(sql)
                    }
                    scenarios.append(scenario)
        
        return scenarios
    
    def _standardize_scenario(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """标准化场景格式"""
        standardized = {
            'name': scenario.get('name', '未命名场景'),
            'description': scenario.get('description', ''),
            'sql': scenario.get('sql', ''),
            'confidence': float(scenario.get('confidence', 0.5)),
            'parameters': scenario.get('parameters', [])
        }
        
        # 如果SQL中没有参数信息，但提供了参数列表，则提取参数
        if not standardized['parameters'] and standardized['sql']:
            standardized['parameters'] = self._extract_parameters(standardized['sql'])
        
        # 确保SQL语句以分号结尾
        if standardized['sql'] and not standardized['sql'].endswith(';'):
            standardized['sql'] = standardized['sql'] + ';'
        
        return standardized
    
    def get_best_scenario(self, scenarios: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        获取最佳的场景
        
        Args:
            scenarios: 场景列表
            
        Returns:
            最佳场景或None
        """
        if not scenarios:
            return None
        
        # 按置信度排序，选择置信度最高的
        sorted_scenarios = sorted(scenarios, key=lambda x: x.get('confidence', 0), reverse=True)
        return sorted_scenarios[0]


# 测试函数
def test_dynamic_sql_parser():
    """测试动态SQL解析器"""
    print("DynamicSQLParser 模块加载成功")
    print("功能：")
    print("1. 检测动态SQL（包含XML标签）")
    print("2. 基础规则解析动态SQL标签")
    print("3. 调用大模型智能解析复杂动态SQL")
    print("4. 生成多种可能的SQL场景")


if __name__ == '__main__':
    test_dynamic_sql_parser()
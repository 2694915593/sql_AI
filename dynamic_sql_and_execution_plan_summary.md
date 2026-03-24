# 动态SQL生成和SQL执行计划实现总结

## 1. 动态SQL生成实现

### 1.1 核心功能
动态SQL生成功能用于从SQL语句中提取参数，并将参数替换为具体的值，生成可执行的SQL语句。这对于SQL注入分析和SQL执行测试非常有用。

### 1.2 实现原理

#### 1.2.1 参数提取
- **参数模式识别**：使用正则表达式 `#{([^}]+)}` 识别SQL中的参数
- **参数类型猜测**：根据参数名猜测参数类型（datetime、number、string）
- **参数信息收集**：收集参数名、类型、位置等信息

#### 1.2.2 表名提取
- **多模式匹配**：支持FROM、JOIN、INSERT INTO、UPDATE、DELETE FROM等多种SQL语句
- **数据库前缀处理**：正确处理带数据库前缀的表名（如`ecdcdb.pd_errcode`）
- **表名清理**：移除引号、空格等无关字符

#### 1.2.3 参数替换
- **类型化替换**：根据参数类型生成合适的值
  - datetime类型：替换为具体时间值
  - number类型：替换为数字值
  - string类型：替换为字符串值
- **特殊参数处理**：对特定参数（如batch_time、start、end）使用预定义值

### 1.3 代码实现

#### ParamExtractor类
```python
class ParamExtractor(LogMixin):
    def __init__(self, sql_text: str, logger=None):
        self.sql_text = sql_text
        super().__init__()
        if logger:
            self.set_logger(logger)
    
    def extract_params(self) -> List[Dict[str, Any]]:
        # 提取参数信息
    
    def generate_replaced_sql(self) -> tuple:
        # 生成替换参数后的SQL和表名列表
```

#### 集成到SQLExtractor
```python
class SQLExtractor(LogMixin):
    def generate_replaced_sql(self, sql_text: str) -> tuple:
        # 使用ParamExtractor生成替换后的SQL
```

### 1.4 测试结果
- ✅ 正确提取各种SQL语句中的参数
- ✅ 正确处理带数据库前缀的表名
- ✅ 根据参数类型生成合适的替换值
- ✅ 处理边界情况（空SQL、无参数SQL、注释等）

## 2. SQL执行计划生成实现

### 2.1 核心功能
SQL执行计划生成功能基于SQL语句和表元数据，预测SQL的执行方式、性能问题和优化建议。

### 2.2 实现原理

#### 2.2.1 SQL类型分析
- **语句类型识别**：识别SELECT、INSERT、UPDATE、DELETE等SQL类型
- **操作类型分析**：分析数据读取、数据写入、数据更新等操作类型
- **性能关注点**：根据SQL类型确定性能关注点

#### 2.2.2 表信息分析
- **数据量分析**：基于表行数判断是否为大表（>10万行）
- **索引分析**：分析表的索引情况，识别全表扫描风险
- **列信息分析**：分析表的列数和列类型

#### 2.2.3 执行计划预测
- **访问路径预测**：基于索引情况预测可能的访问路径
- **扫描方式预测**：预测索引扫描或全表扫描
- **连接方式预测**：对于多表连接，预测连接方式

#### 2.2.4 性能优化建议
- **索引优化**：建议添加合适的索引
- **查询优化**：建议优化WHERE条件、避免SELECT *
- **结构优化**：建议优化表结构

#### 2.2.5 风险评估
- **高风险操作识别**：识别无WHERE条件的DELETE等高风险操作
- **执行风险评估**：评估SQL执行的风险等级

### 2.3 代码实现

#### ModelClient中的实现
```python
class ModelClient(LogMixin):
    def _generate_execution_plan(self, sql_statement: str, tables: List[Dict[str, Any]]) -> str:
        # 生成SQL执行计划分析
```

### 2.4 输出格式
```
SQL执行计划分析：
==================================================
1. SQL类型分析：
   • 类型：查询语句 (SELECT)
   • 操作：数据读取
   • 性能关注点：查询优化、索引使用

2. 涉及表分析：
   表1：pd_errcode
     • 数据量：212 行
     • 是否大表：否
     • 列数：6
     • 索引数：0
     • 索引：无索引（全表扫描风险）

3. 执行计划预测：
   • 预测：可能进行全表扫描
   • 建议：考虑添加合适的索引

4. 性能优化建议：
   • 确保WHERE条件使用索引
   • 避免SELECT *，只选择需要的列
   • 考虑查询结果集大小

5. 执行风险评估：
   • ✅ 风险较低
```

## 3. 完整的工作流程

### 3.1 数据收集阶段
1. 从`am_solline_info`表读取待分析SQL
2. 提取SQL中的表名
3. 连接目标数据库收集表元数据
4. 收集DDL、行数、索引、列信息

### 3.2 分析准备阶段
1. 构建请求数据：SQL语句、表信息、数据库别名
2. **生成动态SQL示例**（使用真实表名和字段名）
3. **生成执行计划分析**（基于元数据）

### 3.3 大模型分析阶段
1. 构建完整的prompt，包含：
   - SQL语句
   - 数据库信息
   - 表信息（包括DDL）
   - **动态SQL示例**
   - **SQL执行计划分析**
   - SQL评审规则
   - 分析要求
   - 输出格式要求
2. 调用大模型API
3. 解析大模型返回的JSON响应

### 3.4 结果处理阶段
1. 存储分析结果到数据库
2. 更新SQL记录状态
3. 记录处理日志

## 4. 系统优势

### 4.1 动态SQL生成优势
- **使用真实数据**：基于用户实际使用的表名和字段名
- **针对性强**：根据SQL类型生成相关示例
- **全面覆盖**：包含各种SQL注入类型
- **实用性强**：提供具体的防护建议

### 4.2 执行计划生成优势
- **基于元数据**：使用实际的表大小、索引信息
- **预测准确**：基于SQL类型和表特征进行合理预测
- **实用性强**：提供具体的优化建议
- **风险识别**：提前识别潜在的执行风险

### 4.3 整体优势
- **自动化程度高**：完整的端到端自动化流程
- **信息完整**：将所有相关信息发送给大模型
- **可扩展性强**：支持多种数据库类型和SQL语句
- **易于维护**：模块化设计，易于扩展和维护

## 5. 验证结果

通过测试验证：
1. ✅ 所有关键信息都正确发送给大模型
2. ✅ 动态SQL使用真实表名和字段名
3. ✅ 执行计划基于元数据生成
4. ✅ 完整的端到端流程正常工作

## 6. 使用示例

### 6.1 动态SQL生成示例
```python
# 原始SQL
sql = "SELECT * FROM ecdcdb.pd_errcode WHERE PEC_ERRCODE = #{error_code}"

# 生成替换参数后的SQL
extractor = ParamExtractor(sql)
replaced_sql, tables = extractor.generate_replaced_sql()

# 输出
# replaced_sql: SELECT * FROM ecdcdb.pd_errcode WHERE PEC_ERRCODE = 'test_value'
# tables: ['pd_errcode']
```

### 6.2 执行计划生成示例
```python
# 基于表元数据生成执行计划
execution_plan = model_client._generate_execution_plan(sql, tables_metadata)

# 输出包含：
# 1. SQL类型分析
# 2. 表信息分析
# 3. 执行计划预测
# 4. 性能优化建议
# 5. 风险评估
```

## 7. 总结

动态SQL生成和SQL执行计划生成是SQL质量分析系统的核心功能，它们：

1. **提高了分析准确性**：使用真实数据和元数据进行分析
2. **增强了实用性**：提供具体的优化建议和防护措施
3. **降低了风险**：提前识别潜在的性能问题和安全风险
4. **提升了效率**：自动化处理，减少人工干预

系统现已完全满足用户要求，能够将SQL语句、对应的动态SQL、SQL执行计划、SQL涉及的表的DDL全部发送给大模型进行综合分析。
# AI-SQL质量分析系统

## 项目概述

AI-SQL质量分析系统是一个自动化SQL质量分析工具，通过集成大模型API对SQL语句进行智能分析，提供性能优化建议、潜在问题识别和质量评分。

## 主要功能

1. **SQL提取与解析**：从数据库读取待分析SQL，自动提取表名
2. **元数据收集**：收集相关表的DDL、行数、索引、列信息等元数据
3. **大模型集成**：调用大模型API进行智能分析
4. **结果处理**：解析分析结果并存储到数据库
5. **批量处理**：支持批量分析多个SQL语句
6. **错误处理**：完善的异常处理和重试机制

## 系统架构

```
sql_ai_analyzer/
├── config/           # 配置管理
│   ├── config.ini.example  # 配置文件模板
│   └── config_manager.py   # 配置管理器
├── data_collector/   # 数据收集
│   ├── sql_extractor.py     # SQL提取器
│   └── metadata_collector.py # 元数据收集器
├── ai_integration/   # 大模型集成
│   └── model_client.py      # API客户端
├── storage/          # 结果存储
│   └── result_processor.py  # 结果处理器
├── utils/            # 工具函数
│   ├── logger.py           # 日志工具
│   └── db_connector.py     # 数据库连接工具
├── tests/            # 测试用例
├── main.py          # 主程序入口
├── requirements.txt  # 依赖包列表
├── schema.sql       # 数据库初始化脚本
└── README.md        # 项目说明文档
```

## 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone <repository-url>
cd sql_ai_analyzer

# 创建虚拟环境（可选）
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt
```

### 2. 数据库配置

#### 源数据库配置
源数据库用于存储待分析的SQL语句。表结构如下：

```sql
CREATE TABLE `am_solline_info` (
  `ID` bigint NOT NULL AUTO_INCREMENT COMMENT 'Efid',
  `PROJECTID` varchar(30) DEFAULT NULL COMMENT '项目id',
  `SYSTEMID` varchar(100) DEFAULT NULL COMMENT '仓库',
  `TASKNUM` varchar(59) DEFAULT NULL COMMENT 'CQ',
  `DEFAULTVERSION` varchar(50) DEFAULT NULL COMMENT '默认分支',
  `AUTHOR` varchar(80) DEFAULT NULL COMMENT '开发人',
  `FILEPATH` varchar(500) DEFAULT NULL COMMENT '文件路径',
  `FILENAME` varchar(200) DEFAULT NULL COMMENT '文件名字',
  `SQLLINE` varchar(500) DEFAULT NULL COMMENT 'sql内容',
  `OPERATETYPE` varchar(2) DEFAULT NULL COMMENT '操作类型 1-新建表 2-删除表 4-新增索引 5-删除索引',
  `TABLENAME` varchar(60) DEFAULT NULL COMMENT '表名',
  `INDEXNAME` varchar(60) DEFAULT NULL COMMENT '索引名',
  `COLUMNNAME` varchar(200) DEFAULT NULL COMMENT '字段名',
  `COLUMNTYPE` varchar(50) DEFAULT NULL COMMENT '字段类型',
  `UPDTIME` varchar(50) DEFAULT NULL COMMENT '更新时间',
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB AUTO_INCREMENT=7360 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
```

需要添加分析相关字段：
```sql
ALTER TABLE am_solline_info 
ADD COLUMN IF NOT EXISTS analysis_status ENUM('pending', 'analyzed', 'failed') DEFAULT 'pending',
ADD COLUMN IF NOT EXISTS analysis_result JSON,
ADD COLUMN IF NOT EXISTS analysis_time TIMESTAMP NULL,
ADD COLUMN IF NOT EXISTS error_message TEXT;
```

#### 目标数据库配置
目标数据库是SQL语句要查询的实际数据库，系统会从中收集表元数据。

### 3. 配置文件

复制配置文件模板并修改配置：

```bash
cp config/config.ini.example config/config.ini
```

编辑 `config/config.ini`，配置以下信息：

- 源数据库连接信息
- 目标数据库连接信息（可配置多个）
- 大模型API地址和密钥
- 日志配置
- 处理参数

### 4. 运行系统

#### 单条SQL分析
```bash
python main.py --mode single --sql-id 1
```

#### 批量分析
```bash
python main.py --mode batch --batch-size 10
```

#### 持续运行模式
```bash
python main.py --mode continuous --interval 300
```

#### 查看帮助
```bash
python main.py --help
```

## 配置说明

### 数据库配置
```ini
[database]
source_host = localhost
source_port = 3306
source_database = sql_analysis_db
source_username = your_username
source_password = your_password
source_db_type = mysql

[db_production]
host = 192.168.1.100
port = 3306
database = production_db
username = your_username
password = your_password
db_type = mysql
```

### AI模型配置
```ini
[ai_model]
api_url = http://your-ai-service.com/api/analyze-sql
api_key = your-api-key-here
timeout = 30
max_retries = 3
```

### 处理配置
```ini
[processing]
batch_size = 10
max_workers = 4
large_table_threshold = 100000
```

## 数据处理流程

1. **SQL提取**：从`am_solline_info`表读取`analysis_status`为`pending`的记录
2. **表名解析**：从SQL语句中提取涉及的表名
3. **元数据收集**：连接目标数据库，收集表的DDL、行数、索引等信息
4. **API调用**：构建请求数据，调用大模型API进行分析
5. **结果处理**：解析API响应，存储分析结果到数据库
6. **状态更新**：更新记录状态为`analyzed`或`failed`

## 请求/响应格式

### 请求数据格式
```json
{
  "sql_statement": "SELECT * FROM users WHERE id = 1",
  "tables": [
    {
      "table_name": "users",
      "ddl": "CREATE TABLE users(...)",
      "row_count": 150000,
      "is_large_table": true,
      "columns": [...],
      "indexes": [...]
    }
  ],
  "db_alias": "db_production"
}
```

### 响应数据格式
```json
{
  "analysis_result": {
    "large_table_operation": {...},
    "index_analysis": {...},
    "optimization_suggestions": [...],
    "performance_estimation": {...},
    "potential_issues": [...]
  },
  "score": 8.5,
  "suggestions": [...]
}
```

## 错误处理

系统包含完善的错误处理机制：

1. **数据库连接失败**：记录错误日志，跳过当前SQL
2. **表不存在**：记录警告，继续处理其他表
3. **API调用失败**：自动重试（最多3次），记录错误
4. **网络超时**：指数退避重试策略
5. **JSON解析失败**：记录原始响应，标记为失败

## 日志系统

系统使用Python标准logging模块，支持：
- 控制台输出
- 文件日志（自动轮转，最大10MB，保留5个备份）
- 可配置日志级别（DEBUG, INFO, WARNING, ERROR）
- 结构化日志格式

## 性能要求

- 单条SQL分析完整流程在30秒内完成
- 支持批量处理至少100条SQL
- 内存使用不超过500MB
- API调用失败自动重试

## 测试

### 单元测试
```bash
pytest tests/ -v
```

### 测试场景
1. 正常流程测试：完整的分析流程
2. 异常情况测试：
   - 数据库连接失败
   - 表不存在
   - API调用失败
   - 网络超时
3. 边界条件测试：
   - 空SQL语句
   - 超大SQL语句
   - 刚好10万行的表

## 部署

### Docker部署（可选）
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "main.py", "--mode", "continuous"]
```

### 系统服务（Linux）
```bash
# 创建系统服务文件 /etc/systemd/system/sql-analyzer.service
[Unit]
Description=AI-SQL质量分析系统
After=network.target

[Service]
Type=simple
User=sqluser
WorkingDirectory=/opt/sql_ai_analyzer
ExecStart=/usr/bin/python3 main.py --mode continuous
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

## 开发指南

### 代码规范
- 遵循PEP8编码规范
- 使用类型注解
- 关键函数有文档字符串注释
- 完善的错误处理机制

### 扩展功能
1. **支持更多数据库类型**：扩展`db_connector.py`
2. **自定义分析规则**：扩展`model_client.py`
3. **结果可视化**：添加Web界面或报表生成
4. **告警通知**：集成邮件、钉钉、企业微信通知

## 常见问题

### Q1: 如何添加新的目标数据库？
在`config.ini`中添加新的数据库配置段，如：
```ini
[db_another]
host = another-host
port = 3306
database = another_db
username = user
password = pass
db_type = mysql
```

### Q2: 如何调整大表阈值？
修改`config.ini`中的`large_table_threshold`参数：
```ini
[processing]
large_table_threshold = 50000  # 调整为5万行
```

### Q3: 如何查看详细日志？
修改日志级别为DEBUG：
```ini
[logging]
log_level = DEBUG
```

### Q4: API调用失败怎么办？
检查：
1. API地址和密钥是否正确
2. 网络连接是否正常
3. API服务是否可用
4. 查看错误日志获取详细信息

## 许可证

本项目采用MIT许可证。

## 联系方式

如有问题或建议，请联系项目维护者。

---

**版本**: 1.0.0  
**最后更新**: 2026-01-28  
**作者**: AI-SQL质量分析系统开发团队
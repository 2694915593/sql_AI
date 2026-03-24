# 多数据库配置和使用指南

## 需求描述
一条SQL可能在A库，也可能在B库，需要在配置中心配置两个一样名称的不同数据库，扫描的时候需要扫两个。

## 解决方案已实现

### 1. 配置文件格式
系统已经支持多数据库实例配置。可以在配置文件中为同一个数据库别名配置多个实例：

```ini
# config.ini 示例
[database]
source_host = localhost
source_port = 3306
source_database = sql_analysis_db
source_username = root
source_password = 123456
source_db_type = mysql

# 生产数据库 - 多个实例
[db_production:1]
host = localhost
port = 3306
database = production_db_a
username = root
password = 123456
db_type = mysql

[db_production:2]
host = localhost
port = 3306
database = production_db_b
username = root
password = 123456
db_type = mysql

# 测试数据库 - 单实例（保持兼容）
[db_test]
host = localhost
port = 3306
database = test_db
username = root
password = 123456
db_type = mysql

# ECUP系统 - 多个实例
[ECUP:1]
host = localhost
port = 3306
database = ecup_a_db
username = root
password = 123456
db_type = mysql

[ECUP:2]
host = localhost
port = 3306
database = ecup_b_db
username = root
password = 123456
db_type = mysql

[ai_model]
api_url = http://182.207.164.154:4004/aiQA.do
api_key = your-api-key-here
timeout = 60
max_retries = 3

[logging]
log_level = INFO
log_file = logs/sql_analyzer.log
log_format = %%(asctime)s - %%(name)s - %%(levelname)s - %%(message)s
```

### 2. 配置说明
- **格式**: `[数据库别名:实例编号]`，实例编号从1开始
- **兼容性**: 传统单实例格式 `[db_production]` 仍然支持
- **实例标识**: 系统自动为每个配置分配实例索引和实例别名

### 3. 使用方法

#### 3.1 从所有实例收集元数据
```python
from config.config_manager import ConfigManager
from data_collector.metadata_collector import MetadataCollector

config = ConfigManager()
metadata_collector = MetadataCollector(config, logger)

# 从所有实例收集表元数据
table_names = ['users', 'orders']
all_metadata = metadata_collector.collect_metadata_from_all_instances('db_production', table_names)

print(f"从 {len(set(m.get('instance_alias') for m in all_metadata))} 个实例收集到 {len(all_metadata)} 个表的元数据")
```

#### 3.2 依次尝试所有实例直到找到表
```python
# 依次尝试所有实例，直到找到表为止
found_metadata = metadata_collector.collect_metadata_until_found('db_production', table_names)

if found_metadata:
    instance_alias = found_metadata[0].get('instance_alias')
    print(f"表在实例 {instance_alias} 中找到")
else:
    print("在所有实例中都未找到表")
```

#### 3.3 从特定实例收集元数据
```python
# 从特定实例索引收集元数据（索引从0开始）
instance_0_metadata = metadata_collector.collect_metadata('db_production', table_names, instance_index=0)
instance_1_metadata = metadata_collector.collect_metadata('db_production', table_names, instance_index=1)
```

#### 3.4 在找到表的实例上获取执行计划
```python
# 生成替换参数后的SQL
replaced_sql = "SELECT * FROM users WHERE id = 123"

# 在找到表的实例上获取执行计划
if found_metadata:
    instance_index = found_metadata[0].get('instance_index', 0)
    plan_result = metadata_collector.get_execution_plan('db_production', replaced_sql, instance_index)
    
    if plan_result.get('has_execution_plan', False):
        print(f"在实例 {found_metadata[0].get('instance_alias')} 上成功获取执行计划")
```

### 4. 主程序集成
主程序 `main.py` 已经集成了多数据库功能：

1. 使用 `collect_metadata_until_found()` 找到表存在的实例
2. 在找到的实例上获取执行计划
3. 使用 `collect_metadata_from_all_instances()` 收集所有实例的元数据供AI分析
4. 结果中包含实例信息

### 5. 数据库表关联
在 `am_solline_info` 表中：
- `SYSTEMID` 字段用作数据库别名
- 如果 `SYSTEMID = 'db_production'`，会扫描所有 `db_production` 实例
- 如果 `SYSTEMID = 'ECUP'`，会扫描所有 `ECUP` 实例

### 6. 测试方法
```bash
# 运行多数据库功能测试
python sql_ai_analyzer/test_multi_db.py

# 查看示例配置文件
cat sql_ai_analyzer/example_multi_db_config.ini

# 查看设计文档
cat sql_ai_analyzer/multi_db_design.md
```

### 7. 配置验证
使用测试配置文件验证配置是否正确解析：
```python
from config.config_manager import ConfigManager

config = ConfigManager('sql_ai_analyzer/config/test_multi_db.ini')
aliases = config.get_all_target_db_aliases()
print(f"所有数据库别名: {aliases}")

for alias in aliases:
    all_configs = config.get_all_target_db_configs(alias)
    print(f"数据库 '{alias}' 有 {len(all_configs)} 个实例")
```

## 总结
您的需求已经实现：
1. ✅ **配置相同名称的不同数据库**：使用 `[db_alias:1]`、`[db_alias:2]` 格式
2. ✅ **扫描时需要扫两个**：系统会自动扫描所有实例
   - `collect_metadata_from_all_instances()` 扫描所有实例
   - `collect_metadata_until_found()` 依次尝试直到找到表
3. ✅ **执行计划在正确实例上获取**：在找到表的实例上执行EXPLAIN
4. ✅ **向后兼容**：传统单实例配置格式仍然支持

## 后续使用建议
1. 更新您的 `config.ini` 文件，使用多实例格式配置数据库
2. 确保 `am_solline_info` 表的 `SYSTEMID` 字段与配置中的数据库别名对应
3. 系统会自动处理多数据库扫描逻辑
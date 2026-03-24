# 多数据库扫描方案设计

## 需求分析
用户需要支持"一条SQL可能在a库，也可能在b库"的场景，需要在配置中心配置两个一样名称的不同数据库，扫描的时候需要扫两个。

## 当前架构分析
1. 当前系统已经支持多数据库配置（通过`[db_production]`, `[db_test]`等配置段）
2. `ConfigManager.get_target_db_config(db_alias)`方法根据别名返回单个数据库配置
3. `MetadataCollector.collect_metadata(db_alias, table_names)`使用单个数据库配置收集元数据
4. 数据库别名存储在`am_solline_info`表的`db_alias`字段中

## 设计方案

### 方案一：配置文件格式扩展
扩展配置文件格式，支持为同一个别名配置多个数据库实例：

```ini
# 单个数据库实例（保持向后兼容）
[db_production]
host = localhost
port = 3306
database = production_db
username = root
password = 123456
db_type = mysql

# 多个数据库实例支持（新格式）
[db_production:1]
host = localhost
port = 3306
database = production_a_db
username = root
password = 123456
db_type = mysql

[db_production:2]
host = localhost
port = 3307
database = production_b_db
username = root
password = 123456
db_type = mysql
```

### 方案二：使用数组索引（更简洁）
```ini
# 传统单个数据库配置（保持兼容）
[db_production]
host = localhost
port = 3306
database = production_db
username = root
password = 123456
db_type = mysql

# 新的多实例配置格式
[db_production_instances]
count = 2

[db_production_instance1]
host = localhost
port = 3306
database = production_a_db
username = root
password = 123456
db_type = mysql

[db_production_instance2]
host = localhost
port = 3307
database = production_b_db
username = root
password = 123456
db_type = mysql
```

## 选择方案
选择**方案一**，因为它：
1. 更直观：使用`db_alias:index`格式明确表示多个实例
2. 易于解析：通过冒号分割别名和索引
3. 向后兼容：传统的`[db_alias]`格式仍然有效

## 实现步骤

### 1. 修改ConfigManager类
- 添加`get_all_target_db_configs(db_alias)`方法，返回所有匹配的数据库配置
- 修改现有的`get_target_db_config`方法，兼容旧格式（返回第一个配置）
- 添加`get_target_db_config_by_index(db_alias, index)`方法，按索引获取特定配置

### 2. 修改MetadataCollector类
- 修改`collect_metadata`方法，支持从多个数据库实例收集元数据
- 策略：依次尝试每个数据库实例，直到找到表为止；或者从所有实例收集（如果表存在于多个实例）
- 添加`collect_metadata_from_all`方法，从所有实例收集

### 3. 修改执行计划获取逻辑
- 修改`get_execution_plan`方法，可能需要选择特定的数据库实例来获取执行计划
- 策略：使用第一个可用的数据库实例，或者让用户指定索引

### 4. 配置文件更新示例
更新config.ini示例：

```ini
[db_production:1]
host = localhost
port = 3306
database = production_a
username = root
password = 123456
db_type = mysql

[db_production:2]
host = localhost
port = 3307
database = production_b
username = root
password = 123456
db_type = mysql

# 保持旧格式兼容
[db_production]
host = localhost
port = 3306
database = production_legacy
username = root
password = 123456
db_type = mysql
```

## 使用场景

### 场景一：表存在于某个数据库实例
系统按顺序检查每个实例，直到找到表为止。例如：
1. 尝试`db_production:1`（production_a数据库），找到表 → 使用该实例的元数据
2. 如果未找到，尝试`db_production:2`（production_b数据库）

### 场景二：表存在于多个实例
系统可以从所有实例收集元数据，并标记每个实例的来源。这对于验证多个环境的一致性很有用。

### 场景三：执行计划
对于执行计划，需要选择具体的数据库实例。策略：
1. 使用第一个可用的实例
2. 让用户指定索引
3. 根据SQL语句中的表名选择匹配的实例

## 迁移策略
1. 保持向后兼容：现有的`[db_alias]`格式仍然有效
2. 逐步迁移：用户可以先将单个数据库配置改为多实例格式
3. 文档更新：提供示例和迁移指南
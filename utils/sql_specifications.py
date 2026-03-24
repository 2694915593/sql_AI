#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SQL规范管理器模块
负责存储、管理和查询SQL规范
"""

import re
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum


class SQLType(Enum):
    """SQL类型枚举"""
    SELECT = "select"
    INSERT = "insert"
    UPDATE = "update"
    DELETE = "delete"
    CREATE = "create"
    ALTER = "alter"
    DROP = "drop"
    TRUNCATE = "truncate"
    OTHER = "other"


class RuleLevel(Enum):
    """规则级别枚举"""
    MANDATORY = "强制"
    RECOMMENDED = "推荐"
    SUGGESTION = "建议"


class SQLSpecificationsManager:
    """
    SQL规范管理器
    管理SQL规范的结构化存储和查询
    """
    
    def __init__(self):
        """初始化规范管理器"""
        self.specifications = self._initialize_specifications()
        self._build_index()
    
    def _initialize_specifications(self) -> Dict[str, Any]:
        """
        初始化SQL规范数据结构
        基于用户提供的规范文档
        """
        return {
            "字符集规范": {
                "category": "字符集规范",
                "description": "数据库字符集和字符序设置规范",
                "rules": [
                    {
                        "id": "2.1.1",
                        "level": RuleLevel.MANDATORY,
                        "content": "字符集与字符序的设置直接影响数据存储和查询结果。字符集应设置为utf8mb4，并根据业务场景选择字符序：\n"
                                  "1.utf8mb4_bin（推荐）：基于二进制编码进行排序比较，大小写敏感（如'A' = 'a' 返回false)\n"
                                  "2.utf8mb4_general_ci：采用Unicode规则进行排序比较，不区分大小写（如'A' = 'a' 返回 true)",
                        "description": "字符集和字符序设置规范",
                        "sql_types": [SQLType.CREATE, SQLType.ALTER],
                        "applicable_scenarios": ["建表", "表结构变更"]
                    },
                    {
                        "id": "2.1.2",
                        "level": RuleLevel.MANDATORY,
                        "content": "默认情况下，字符集/字符序逐级继承，若显式指定，必须保证表、列字符集/字符序与数据库保持一致（建议数据库与租户保持一致），租户级、表（【v3.2.3】）、列字符集/字符序设置后不可修改。",
                        "description": "字符集继承规范",
                        "sql_types": [SQLType.CREATE, SQLType.ALTER],
                        "applicable_scenarios": ["建表", "表结构变更"]
                    }
                ]
            },
            "命名规范": {
                "category": "命名规范",
                "description": "数据库对象命名规范",
                "rules": [
                    {
                        "id": "2.2.1",
                        "level": RuleLevel.MANDATORY,
                        "content": "普通租户名：小写32字符 ，t+应用标识(4位)+环境标识(3位)+租户编号(XX，从00开始)，其中环境标识生产为prd，测试为SIT/DEV/UAT/UA1/UA2/UAC，如tecifsit00。",
                        "description": "普通租户命名规范",
                        "sql_types": [SQLType.CREATE],
                        "applicable_scenarios": ["创建数据库", "创建租户"]
                    },
                    {
                        "id": "2.2.2",
                        "level": RuleLevel.MANDATORY,
                        "content": "单元化租户名：小写32字符 ，t+应用标识(4位)+环境标识(3位)+ZONE类型(G/C/R)+租户编号(XX，从00开始)。",
                        "description": "单元化租户命名规范",
                        "sql_types": [SQLType.CREATE],
                        "applicable_scenarios": ["创建数据库", "创建租户"]
                    },
                    {
                        "id": "2.2.3",
                        "level": RuleLevel.MANDATORY,
                        "content": "数据库名：子系统标识(4位)+应用模块名(最多4位，可选）+ db，例如：gabsdb 或 ibcsbatcdb。",
                        "description": "数据库命名规范",
                        "sql_types": [SQLType.CREATE],
                        "applicable_scenarios": ["创建数据库"]
                    }
                ]
            },
            "业务表规范": {
                "category": "业务表规范",
                "description": "业务表设计和操作规范",
                "rules": [
                    {
                        "id": "2.3.1",
                        "level": RuleLevel.MANDATORY,
                        "content": "表名和列名禁止大小写混用，禁止反闭包（backquote，即`）表名和列名。",
                        "description": "表名和列名大小写规范",
                        "sql_types": [SQLType.CREATE, SQLType.ALTER, SQLType.SELECT, SQLType.INSERT, SQLType.UPDATE, SQLType.DELETE],
                        "applicable_scenarios": ["所有SQL操作"]
                    },
                    {
                        "id": "2.3.2",
                        "level": RuleLevel.MANDATORY,
                        "content": "表名和列名只能使用字母、数字和下划线，并且必须以字母开头，不得使用系统保留字和特殊字符。表名禁止两个下划线中间只出现数字。",
                        "description": "表名和列名命名规范",
                        "sql_types": [SQLType.CREATE, SQLType.ALTER],
                        "applicable_scenarios": ["建表", "表结构变更"]
                    },
                    {
                        "id": "2.3.4",
                        "level": RuleLevel.MANDATORY,
                        "content": "定义表结构时，表或列须用属性comment加上注释。",
                        "description": "表和列注释规范",
                        "sql_types": [SQLType.CREATE, SQLType.ALTER],
                        "applicable_scenarios": ["建表", "表结构变更"]
                    },
                    {
                        "id": "2.3.8",
                        "level": RuleLevel.MANDATORY,
                        "content": "单分区数据量安全水位线为2TB，当超过1TB需及时清理，否则集群可能会有严重风险。\n"
                                  "1.【v3.2.3】不支持将非分表变更为分区表。\n"
                                  "2.【v4.2.1】支持将非分区表转换为分区表，但该操作属于Offline DDL。",
                        "description": "分区表数据量规范",
                        "sql_types": [SQLType.CREATE, SQLType.ALTER],
                        "applicable_scenarios": ["分区表操作"]
                    },
                    {
                        "id": "2.3.13",
                        "level": RuleLevel.MANDATORY,
                        "content": "分区表的查询或修改必须带上分区键。",
                        "description": "分区表操作规范",
                        "sql_types": [SQLType.SELECT, SQLType.UPDATE, SQLType.DELETE],
                        "applicable_scenarios": ["分区表查询", "分区表修改"]
                    },
                    {
                        "id": "2.3.14",
                        "level": RuleLevel.MANDATORY,
                        "content": "禁止使用生成列作为分区键。",
                        "description": "分区键选择规范",
                        "sql_types": [SQLType.CREATE, SQLType.ALTER],
                        "applicable_scenarios": ["创建分区表", "修改分区表"]
                    }
                ]
            },
            "字段规范": {
                "category": "字段规范",
                "description": "字段类型和使用规范",
                "rules": [
                    {
                        "id": "2.4.1",
                        "level": RuleLevel.MANDATORY,
                        "content": "小数类型使用decimal类型存储，禁止使用double、float、varchar。",
                        "description": "小数类型规范",
                        "sql_types": [SQLType.CREATE, SQLType.ALTER],
                        "applicable_scenarios": ["建表", "表结构变更"]
                    },
                    {
                        "id": "2.4.2",
                        "level": RuleLevel.MANDATORY,
                        "content": "当字段类型为字符串（char，varchar等）时，禁止直接对该字段数据进行数值函数计算，否则会出现非预期结果。",
                        "description": "字符串字段计算规范",
                        "sql_types": [SQLType.SELECT, SQLType.UPDATE],
                        "applicable_scenarios": ["查询", "更新"]
                    },
                    {
                        "id": "2.4.3",
                        "level": RuleLevel.MANDATORY,
                        "content": "表上强制添加创建和变更时间字段，字段类型DATETIME（6）。字段名须符合数管部字段规范，如创建时间字段CREATE_TIME ，加上DEFAULT CURRENT_TIMESTAMP（6）属性；变更时间字段UPDATE_TIME，加上DEFAULT CURRENT_TIMESTAMP（6） ON UPDATE CURRENT_TIMESTAMP（6）属性。",
                        "description": "时间字段规范",
                        "sql_types": [SQLType.CREATE, SQLType.ALTER],
                        "applicable_scenarios": ["建表", "表结构变更"]
                    },
                    {
                        "id": "2.4.4",
                        "level": RuleLevel.MANDATORY,
                        "content": "禁止使用枚举数据类型。",
                        "description": "枚举类型使用规范",
                        "sql_types": [SQLType.CREATE, SQLType.ALTER],
                        "applicable_scenarios": ["建表", "表结构变更"]
                    },
                    {
                        "id": "2.4.5",
                        "level": RuleLevel.MANDATORY,
                        "content": "修改列名、列长度等属性时，须带上列的原属性值，以避免原来的列定义被覆盖而无法恢复（列定义可通过 'show create table 表名'查看）。",
                        "description": "列属性修改规范",
                        "sql_types": [SQLType.ALTER],
                        "applicable_scenarios": ["表结构变更"]
                    },
                    {
                        "id": "2.4.6",
                        "level": RuleLevel.MANDATORY,
                        "content": "【v3.2.3】禁止使用定义为STORED类型且依赖其他列值计算的生成列。",
                        "description": "生成列使用规范",
                        "sql_types": [SQLType.CREATE, SQLType.ALTER],
                        "applicable_scenarios": ["建表", "表结构变更"]
                    }
                ]
            },
            "自增列和序列规范": {
                "category": "自增列和序列规范",
                "description": "自增列和序列使用规范",
                "rules": [
                    {
                        "id": "2.5.1",
                        "level": RuleLevel.MANDATORY,
                        "content": "创建序列必须指定cache大小，cache值可设置为:\ncache大小 = 租户交易的tps*60*60*24/100",
                        "description": "序列cache大小规范",
                        "sql_types": [SQLType.CREATE],
                        "applicable_scenarios": ["创建序列"]
                    },
                    {
                        "id": "2.5.2",
                        "level": RuleLevel.MANDATORY,
                        "content": "序列禁止添加order属性。",
                        "description": "序列order属性规范",
                        "sql_types": [SQLType.CREATE],
                        "applicable_scenarios": ["创建序列"]
                    },
                    {
                        "id": "2.5.3",
                        "level": RuleLevel.MANDATORY,
                        "content": "自增列/序列字段使用bigint类型存储，禁止使用int类型，防止存储溢出。",
                        "description": "自增列类型规范",
                        "sql_types": [SQLType.CREATE, SQLType.ALTER],
                        "applicable_scenarios": ["建表", "表结构变更"]
                    },
                    {
                        "id": "2.5.4",
                        "level": RuleLevel.MANDATORY,
                        "content": "禁止使用自增列作为分区键。因为当使用自增列作为分区键时，不保证自增列的值分区内自增，并且性能损耗较大。",
                        "description": "自增列作为分区键规范",
                        "sql_types": [SQLType.CREATE, SQLType.ALTER],
                        "applicable_scenarios": ["创建分区表", "修改分区表"]
                    },
                    {
                        "id": "2.5.5",
                        "level": RuleLevel.MANDATORY,
                        "content": "noorder选项的序列不保证全局单调递增，发生切主时等特定情况下值会跳变，应用要避免跳变带来的值变大或变小的影响。",
                        "description": "序列noorder选项规范",
                        "sql_types": [SQLType.CREATE],
                        "applicable_scenarios": ["创建序列"]
                    }
                ]
            },
            "索引规范": {
                "category": "索引规范",
                "description": "索引设计和使用规范",
                "rules": [
                    {
                        "id": "2.6.2",
                        "level": RuleLevel.MANDATORY,
                        "content": "禁止创建全文索引。",
                        "description": "全文索引规范",
                        "sql_types": [SQLType.CREATE, SQLType.ALTER],
                        "applicable_scenarios": ["创建索引", "修改索引"]
                    },
                    {
                        "id": "2.6.3",
                        "level": RuleLevel.MANDATORY,
                        "content": "联机TP交易SQL语句运行时必须使用对应的索引，涉及大表时尤为注意。",
                        "description": "索引使用规范",
                        "sql_types": [SQLType.SELECT, SQLType.UPDATE, SQLType.DELETE],
                        "applicable_scenarios": ["查询", "更新", "删除"]
                    },
                    {
                        "id": "2.6.8",
                        "level": RuleLevel.MANDATORY,
                        "content": "唯一索引的所有字段须添加not null约束。",
                        "description": "唯一索引字段规范",
                        "sql_types": [SQLType.CREATE, SQLType.ALTER],
                        "applicable_scenarios": ["创建索引", "修改索引"]
                    }
                ]
            },
            "其他禁用类规范": {
                "category": "其他禁用类规范",
                "description": "其他禁止使用的数据库功能",
                "rules": [
                    {
                        "id": "2.7.1",
                        "level": RuleLevel.MANDATORY,
                        "content": "禁止在应用程序设计阶段使用外键、临时表（CREATE TEMPORARY TABLE）、存储过程以及触发器。",
                        "description": "禁用功能规范",
                        "sql_types": [SQLType.CREATE],
                        "applicable_scenarios": ["所有创建操作"]
                    },
                    {
                        "id": "2.7.2",
                        "level": RuleLevel.MANDATORY,
                        "content": "通用表达式CTE recursive递归行数禁止超过1000。",
                        "description": "CTE递归行数规范",
                        "sql_types": [SQLType.SELECT],
                        "applicable_scenarios": ["查询"]
                    },
                    {
                        "id": "2.7.3",
                        "level": RuleLevel.MANDATORY,
                        "content": "【v3.2.3 bp8及下】禁用get_format函数。",
                        "description": "禁用函数规范",
                        "sql_types": [SQLType.SELECT, SQLType.UPDATE, SQLType.INSERT, SQLType.DELETE],
                        "applicable_scenarios": ["所有数据操作"]
                    },
                    {
                        "id": "2.7.4",
                        "level": RuleLevel.MANDATORY,
                        "content": "SQL单行注释需以--开头，符号后必须加空格再写注释内容，否则可能导致语法解析错误。",
                        "description": "SQL注释规范",
                        "sql_types": [SQLType.SELECT, SQLType.INSERT, SQLType.UPDATE, SQLType.DELETE, SQLType.CREATE, SQLType.ALTER],
                        "applicable_scenarios": ["所有SQL操作"]
                    }
                ]
            },
            "查询语句规范": {
                "category": "查询语句规范",
                "description": "SELECT查询语句规范",
                "rules": [
                    {
                        "id": "3.1.1",
                        "level": RuleLevel.MANDATORY,
                        "content": "应用程序中，SELECT语句必须指定具体字段名称，禁止写成 'select *'。",
                        "description": "SELECT字段规范",
                        "sql_types": [SQLType.SELECT],
                        "applicable_scenarios": ["查询"]
                    },
                    {
                        "id": "3.1.3",
                        "level": RuleLevel.MANDATORY,
                        "content": "禁止大表查询使用全表扫描。\n"
                                  "1.表关联查询时因关联表字符集/字符序不一致导致隐式转换",
                        "description": "全表扫描规范",
                        "sql_types": [SQLType.SELECT],
                        "applicable_scenarios": ["查询"]
                    },
                    {
                        "id": "3.1.5",
                        "level": RuleLevel.MANDATORY,
                        "content": "SQL语句中禁止使用数据库保留字。",
                        "description": "数据库保留字规范",
                        "sql_types": [SQLType.SELECT, SQLType.INSERT, SQLType.UPDATE, SQLType.DELETE, SQLType.CREATE, SQLType.ALTER],
                        "applicable_scenarios": ["所有SQL操作"]
                    },
                    {
                        "id": "3.1.10",
                        "level": RuleLevel.MANDATORY,
                        "content": "在不确定结果集大小如非主键、非唯一键查询或关联查询，应使用物理分页(即SQL中使用limit)，避免出现大结果集造成程序 JVM OOM。",
                        "description": "物理分页规范",
                        "sql_types": [SQLType.SELECT],
                        "applicable_scenarios": ["查询"]
                    },
                    {
                        "id": "3.1.12",
                        "level": RuleLevel.MANDATORY,
                        "content": "在使用SOFA-ODP组件的场景下，SQL谓词中禁用反单引号（backquote,即`）修饰分区键。",
                        "description": "分区键修饰规范",
                        "sql_types": [SQLType.SELECT],
                        "applicable_scenarios": ["查询"]
                    },
                    {
                        "id": "3.1.13",
                        "level": RuleLevel.MANDATORY,
                        "content": "业务逻辑要求查询结果有序或稳定时，需添加order by排序，且排序字段必须唯一或者组合唯一（非空），否则会造成结果不稳定（即每次查询结果集顺序不一致）。分页查询或join表关联后row_number() over() 获取序号场景，尤为注意。",
                        "description": "排序稳定性规范",
                        "sql_types": [SQLType.SELECT],
                        "applicable_scenarios": ["查询"]
                    },
                    {
                        "id": "3.1.19",
                        "level": RuleLevel.MANDATORY,
                        "content": "case when表达式应控制在150个以内，case when表达式过多可能会导致性能下降或租户内存被打爆；",
                        "description": "CASE WHEN表达式数量规范",
                        "sql_types": [SQLType.SELECT, SQLType.UPDATE],
                        "applicable_scenarios": ["查询", "更新"]
                    },
                    {
                        "id": "3.1.20",
                        "level": RuleLevel.MANDATORY,
                        "content": "CASE WHEN 语句必须显式定义ELSE分支并明确返回值，避免因隐式返回NULL 值而出现非预期的结果。",
                        "description": "CASE WHEN ELSE分支规范",
                        "sql_types": [SQLType.SELECT, SQLType.UPDATE],
                        "applicable_scenarios": ["查询", "更新"]
                    }
                ]
            },
            "多表关联查询语句规范": {
                "category": "多表关联查询语句规范",
                "description": "多表关联查询规范",
                "rules": [
                    {
                        "id": "3.2.3",
                        "level": RuleLevel.MANDATORY,
                        "content": "多表关联必须有关联条件，禁止出现笛卡尔积（explain 看到 CARTESIAN 关键字）。",
                        "description": "关联条件规范",
                        "sql_types": [SQLType.SELECT],
                        "applicable_scenarios": ["查询"]
                    },
                    {
                        "id": "3.2.5",
                        "level": RuleLevel.MANDATORY,
                        "content": "子查询内SELECT列表字段禁止引用外表。",
                        "description": "子查询字段引用规范",
                        "sql_types": [SQLType.SELECT],
                        "applicable_scenarios": ["查询"]
                    }
                ]
            },
            "增删改语句规范": {
                "category": "增删改语句规范",
                "description": "INSERT、UPDATE、DELETE语句规范",
                "rules": [
                    {
                        "id": "3.3.1",
                        "level": RuleLevel.MANDATORY,
                        "content": "删改语句必须带where条件或使用limit物理分页，避免形成大事务。",
                        "description": "删改语句条件规范",
                        "sql_types": [SQLType.UPDATE, SQLType.DELETE],
                        "applicable_scenarios": ["更新", "删除"]
                    },
                    {
                        "id": "3.3.3",
                        "level": RuleLevel.MANDATORY,
                        "content": "【v3.2.3】为应对数据库DDL异步处理机制，收到成功返回后需等待至少3秒并检查确认后再执行DML操作，包括但不限于TRUNCATE TABLE确认数据清空、CREATE/DROP/ALTER 表（分区）、列、序列等数据库对象、约束的检查确认，重试至少三次若失败需人工处置。",
                        "description": "DDL异步处理规范",
                        "sql_types": [SQLType.CREATE, SQLType.ALTER, SQLType.DROP, SQLType.TRUNCATE],
                        "applicable_scenarios": ["结构变更"]
                    },
                    {
                        "id": "3.3.4",
                        "level": RuleLevel.MANDATORY,
                        "content": "INSERT时必须指定列，以避免数据表出现结构上变化时造成程序错误，如在表中增加了一个字段；",
                        "description": "INSERT列指定规范",
                        "sql_types": [SQLType.INSERT],
                        "applicable_scenarios": ["插入"]
                    },
                    {
                        "id": "3.3.6",
                        "level": RuleLevel.MANDATORY,
                        "content": "执行INSERT INTO table_name(list_of_columns) VALUES (list_of_values) ON DUPLICATE KEY UPDATE语句时，对于非空字段无论是否需要更新，禁止传入null值；",
                        "description": "ON DUPLICATE KEY UPDATE规范",
                        "sql_types": [SQLType.INSERT],
                        "applicable_scenarios": ["插入"]
                    },
                    {
                        "id": "3.3.7",
                        "level": RuleLevel.MANDATORY,
                        "content": "在对分区表执行DROP或TRUNCATE分区操作时，需注意执行期间全局索引会失效。",
                        "description": "分区表操作索引失效规范",
                        "sql_types": [SQLType.DROP, SQLType.TRUNCATE],
                        "applicable_scenarios": ["删除分区", "清空分区"]
                    }
                ]
            },
            "事务规范": {
                "category": "事务规范",
                "description": "事务使用规范",
                "rules": [
                    {
                        "id": "3.4.1",
                        "level": RuleLevel.MANDATORY,
                        "content": "应用程序中禁止设置timezone，SQL_mode和isolation_level变量。",
                        "description": "数据库变量设置规范",
                        "sql_types": [SQLType.SELECT, SQLType.INSERT, SQLType.UPDATE, SQLType.DELETE],
                        "applicable_scenarios": ["所有数据操作"]
                    },
                    {
                        "id": "3.4.2",
                        "level": RuleLevel.MANDATORY,
                        "content": "事务隔离级别应使用默认的RC 读已提交，目前RR和serialize 对并发限制较大，且OB不支持读未提交，即脏读。",
                        "description": "事务隔离级别规范",
                        "sql_types": [SQLType.SELECT, SQLType.INSERT, SQLType.UPDATE, SQLType.DELETE],
                        "applicable_scenarios": ["所有数据操作"]
                    },
                    {
                        "id": "3.4.3",
                        "level": RuleLevel.MANDATORY,
                        "content": "禁止事务内第一条查询SQL为如下几种写法，避免生成远程执行计划。",
                        "description": "事务内查询规范",
                        "sql_types": [SQLType.SELECT],
                        "applicable_scenarios": ["查询"]
                    }
                ]
            },
            "其他规范": {
                "category": "其他规范",
                "description": "其他SQL使用规范",
                "rules": [
                    {
                        "id": "3.5.1",
                        "level": RuleLevel.MANDATORY,
                        "content": "在使用if(expr1, expr2, expr3)函数时，expr1不能为字符类型，否则SQL语句的执行结果可能会不符合预期。\n"
                                  "反例：if(c5, 'cc', '123')，其中c5为字符类型，if函数会尝试将c5的值转成数值类型，转换可能会失败，若为select语句，SQL语句执行成功但结果为'123'，同时报warning，若为update语句会直接报错",
                        "description": "IF函数参数类型规范",
                        "sql_types": [SQLType.SELECT, SQLType.UPDATE],
                        "applicable_scenarios": ["查询", "更新"]
                    },
                    {
                        "id": "3.5.2",
                        "level": RuleLevel.MANDATORY,
                        "content": "SQL Hint必须经过验证确保其有效性，避免因语法错误或位置不当等原因导致HINT被忽略。",
                        "description": "SQL Hint使用规范",
                        "sql_types": [SQLType.SELECT, SQLType.INSERT, SQLType.UPDATE, SQLType.DELETE],
                        "applicable_scenarios": ["所有数据操作"]
                    },
                    {
                        "id": "3.5.3",
                        "level": RuleLevel.MANDATORY,
                        "content": "禁止使用optimize table语法，因在OceanBase中该指令无法重整表结构，且可能引发schema同步延迟风险。",
                        "description": "OPTIMIZE TABLE使用规范",
                        "sql_types": [SQLType.OTHER],
                        "applicable_scenarios": ["表维护"]
                    }
                ]
            }
        }
    
    def _build_index(self):
        """构建索引以提高查询性能"""
        self._sql_type_index = {}
        self._rule_id_index = {}
        
        for category, category_data in self.specifications.items():
            for rule in category_data["rules"]:
                rule_id = rule["id"]
                self._rule_id_index[rule_id] = rule
                
                for sql_type in rule["sql_types"]:
                    if sql_type not in self._sql_type_index:
                        self._sql_type_index[sql_type] = []
                    self._sql_type_index[sql_type].append(rule)
    
    def get_specifications_by_sql_type(self, sql_type: SQLType) -> List[Dict[str, Any]]:
        """
        根据SQL类型获取相关规范
        
        Args:
            sql_type: SQL类型
            
        Returns:
            相关规范列表
        """
        return self._sql_type_index.get(sql_type, [])
    
    def get_specifications_by_category(self, category: str) -> Dict[str, Any]:
        """
        根据分类获取规范
        
        Args:
            category: 规范分类
            
        Returns:
            分类规范数据
        """
        return self.specifications.get(category, {})
    
    def get_rule_by_id(self, rule_id: str) -> Optional[Dict[str, Any]]:
        """
        根据规则ID获取规则
        
        Args:
            rule_id: 规则ID
            
        Returns:
            规则数据
        """
        return self._rule_id_index.get(rule_id)
    
    def get_all_categories(self) -> List[str]:
        """
        获取所有规范分类
        
        Returns:
            分类列表
        """
        return list(self.specifications.keys())
    
    def get_specifications_summary(self) -> Dict[str, Any]:
        """
        获取规范摘要
        
        Returns:
            规范摘要信息
        """
        total_rules = 0
        mandatory_rules = 0
        
        for category, category_data in self.specifications.items():
            category_rules = len(category_data["rules"])
            total_rules += category_rules
            
            for rule in category_data["rules"]:
                if rule["level"] == RuleLevel.MANDATORY:
                    mandatory_rules += 1
        
        return {
            "total_categories": len(self.specifications),
            "total_rules": total_rules,
            "mandatory_rules": mandatory_rules,
            "recommended_rules": total_rules - mandatory_rules,
            "categories": self.get_all_categories()
        }
    
    def generate_detailed_specifications_report(self) -> str:
        """
        生成详细规范报告
        
        Returns:
            规范报告文本
        """
        report_parts = []
        
        for category, category_data in self.specifications.items():
            report_parts.append(f"## {category}")
            report_parts.append(f"{category_data['description']}")
            report_parts.append("")
            
            for rule in category_data["rules"]:
                level_str = rule["level"].value if isinstance(rule["level"], RuleLevel) else rule["level"]
                sql_types = [t.value if isinstance(t, SQLType) else t for t in rule["sql_types"]]
                
                report_parts.append(f"### {rule['id']} 【{level_str}】")
                report_parts.append(f"**内容：** {rule['content']}")
                report_parts.append(f"**描述：** {rule['description']}")
                report_parts.append(f"**适用SQL类型：** {', '.join(sql_types)}")
                report_parts.append(f"**适用场景：** {', '.join(rule.get('applicable_scenarios', []))}")
                report_parts.append("")
        
        return "\n".join(report_parts)
    
    def detect_sql_type(self, sql: str) -> SQLType:
        """
        检测SQL类型
        
        Args:
            sql: SQL语句
            
        Returns:
            SQL类型
        """
        sql_upper = sql.strip().upper()
        
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
    
    def check_sql_against_specifications(self, sql: str, sql_type: Optional[SQLType] = None) -> Dict[str, Any]:
        """
        检查SQL语句是否符合规范
        
        Args:
            sql: SQL语句
            sql_type: SQL类型，如果为None则自动检测
            
        Returns:
            检查结果
        """
        if sql_type is None:
            sql_type = self.detect_sql_type(sql)
        
        relevant_rules = self.get_specifications_by_sql_type(sql_type)
        
        compliant_rules = []
        violated_rules = []
        violations = []
        
        # 这里可以实现具体的规范检查逻辑
        # 目前先返回规则列表，具体的检查逻辑可以在后续实现
        for rule in relevant_rules:
            rule_id = rule["id"]
            rule_content = rule["content"]
            
            # 简单检查示例：检查SELECT语句是否使用SELECT *
            if sql_type == SQLType.SELECT and rule_id == "3.1.1":
                if re.search(r'SELECT\s+\*\s+FROM', sql, re.IGNORECASE):
                    violated_rules.append(rule_id)
                    violations.append({
                        "rule_id": rule_id,
                        "description": rule["description"],
                        "message": "SELECT语句使用了SELECT *，违反了规范3.1.1",
                        "suggestion": "指定具体的字段名，如SELECT id, name FROM table"
                    })
                else:
                    compliant_rules.append(rule_id)
            else:
                # 对于其他规则，暂时标记为符合
                compliant_rules.append(rule_id)
        
        return {
            "sql": sql,
            "sql_type": sql_type.value,
            "total_rules_checked": len(relevant_rules),
            "compliant_rules": compliant_rules,
            "violated_rules": violated_rules,
            "violations": violations,
            "compliance_score": (len(compliant_rules) / len(relevant_rules) * 100) if relevant_rules else 100
        }


def create_sql_specifications_checklist(sql_type: SQLType) -> Dict[str, Any]:
    """
    创建SQL规范检查清单
    
    Args:
        sql_type: SQL类型
        
    Returns:
        检查清单
    """
    manager = SQLSpecificationsManager()
    relevant_rules = manager.get_specifications_by_sql_type(sql_type)
    
    checklist = {}
    for rule in relevant_rules:
        category = rule.get("category", "其他")
        if category not in checklist:
            checklist[category] = {
                "description": "相关规范检查项",
                "items": []
            }
        
        level_str = rule["level"].value if isinstance(rule["level"], RuleLevel) else rule["level"]
        checklist[category]["items"].append({
            "rule_id": rule["id"],
            "level": level_str,
            "description": rule["description"],
            "content": rule["content"][:100] + "..." if len(rule["content"]) > 100 else rule["content"],
            "check_function": None  # 可以在这里指定检查函数
        })
    
    return checklist


def integrate_specifications_into_prompt(prompt_parts: List[str], sql_type: SQLType) -> List[str]:
    """
    将SQL规范集成到提示词中
    
    Args:
        prompt_parts: 原始提示词部分
        sql_type: SQL类型
        
    Returns:
        增强后的提示词部分
    """
    manager = SQLSpecificationsManager()
    relevant_rules = manager.get_specifications_by_sql_type(sql_type)
    
    enhanced_parts = prompt_parts.copy()
    
    # 添加SQL规范要求部分
    enhanced_parts.append("\nSQL规范要求：")
    enhanced_parts.append("请根据以下SQL规范对SQL语句进行分析和优化：")
    enhanced_parts.append("")
    
    # 按分类组织规则
    from .specifications_prompt_generator import SpecificationsPromptGenerator
    generator = SpecificationsPromptGenerator()
    
    rules_by_category = {}
    for rule in relevant_rules:
        category = generator._get_rule_category(rule)
        if category not in rules_by_category:
            rules_by_category[category] = []
        rules_by_category[category].append(rule)
    
    # 生成分类化的规范提示
    for category, rules in rules_by_category.items():
        enhanced_parts.append(f"【{category}】")
        for rule in rules[:10]:  # 每个分类最多10条规则，避免过长
            level_str = rule["level"].value if hasattr(rule["level"], "value") else rule["level"]
            # 简化内容，保留关键信息
            simplified_content = generator._simplify_rule_content(rule["content"])
            # 在规则ID前加上"规范"前缀，如"规范3.1.1"
            enhanced_parts.append(f"  规范{rule['id']} 【{level_str}】: {simplified_content}")
        enhanced_parts.append("")
    
    # 根据SQL类型添加特定规范标题
    sql_type_str = ""
    if sql_type == SQLType.SELECT:
        sql_type_str = "SELECT语句规范"
    elif sql_type == SQLType.INSERT:
        sql_type_str = "INSERT语句规范"
    elif sql_type == SQLType.UPDATE:
        sql_type_str = "UPDATE语句规范"
    elif sql_type == SQLType.DELETE:
        sql_type_str = "DELETE语句规范"
    elif sql_type == SQLType.CREATE:
        sql_type_str = "CREATE语句规范"
    elif sql_type == SQLType.ALTER:
        sql_type_str = "ALTER语句规范"
    
    if sql_type_str:
        enhanced_parts.insert(enhanced_parts.index("\nSQL规范要求：") + 3, f"{sql_type_str}:")
    
    enhanced_parts.append("基于以上SQL规范的分析要求：")
    enhanced_parts.append("1. 检查SQL语句是否符合相关规范")
    enhanced_parts.append("2. 如果违反规范，提供具体的修改建议")
    enhanced_parts.append("3. 在修改建议SQL中确保符合所有相关规范")
    enhanced_parts.append("4. 在风险评估中标注违反规范的问题")
    enhanced_parts.append("5. 给出基于规范符合性的综合评分")
    enhanced_parts.append("")
    
    return enhanced_parts


# 测试函数
def test_sql_specifications_module():
    """测试SQL规范模块"""
    manager = SQLSpecificationsManager()
    
    print("=" * 60)
    print("测试SQL规范模块")
    print("=" * 60)
    
    # 测试规范摘要
    summary = manager.get_specifications_summary()
    print(f"规范分类数: {summary['total_categories']}")
    print(f"规范总条款数: {summary['total_rules']}")
    print(f"强制条款数: {summary['mandatory_rules']}")
    
    # 测试按SQL类型获取规范
    select_rules = manager.get_specifications_by_sql_type(SQLType.SELECT)
    print(f"\nSELECT相关规范数量: {len(select_rules)}")
    
    # 测试SQL类型检测
    test_sqls = [
        "SELECT * FROM users",
        "INSERT INTO users (id, name) VALUES (1, 'test')",
        "UPDATE users SET name = 'new' WHERE id = 1",
        "CREATE TABLE users (id INT PRIMARY KEY)"
    ]
    
    print("\nSQL类型检测测试:")
    for sql in test_sqls:
        sql_type = manager.detect_sql_type(sql)
        print(f"  {sql[:30]}... -> {sql_type.value}")
    
    # 测试规范检查
    print("\n规范检查测试:")
    check_result = manager.check_sql_against_specifications("SELECT * FROM users")
    print(f"  合规规则数: {len(check_result['compliant_rules'])}")
    print(f"  违规规则数: {len(check_result['violated_rules'])}")
    print(f"  合规评分: {check_result['compliance_score']:.1f}%")
    
    return True


if __name__ == "__main__":
    test_sql_specifications_module()
-- AI-SQL质量分析系统数据库初始化脚本
-- 创建源数据库和表结构

-- 创建源数据库
CREATE DATABASE IF NOT EXISTS sql_analysis_db;
USE sql_analysis_db;

-- 根据实际表结构创建待分析SQL信息表
-- 注意：实际表结构可能已经存在，这里提供的是参考结构
-- 实际表结构如下：
/*
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
*/

-- 为了支持AI分析功能，我们需要添加一些额外的字段
-- 如果表已存在，可以使用ALTER TABLE添加这些字段
ALTER TABLE am_solline_info 
ADD COLUMN IF NOT EXISTS analysis_status ENUM('pending', 'analyzed', 'failed') DEFAULT 'pending' COMMENT '分析状态',
ADD COLUMN IF NOT EXISTS analysis_result JSON COMMENT '分析结果',
ADD COLUMN IF NOT EXISTS analysis_time TIMESTAMP NULL COMMENT '分析时间',
ADD COLUMN IF NOT EXISTS error_message TEXT COMMENT '错误信息',
ADD COLUMN IF NOT EXISTS sql_issue_type ENUM('none', 'db2_syntax', 'table_extraction_failed', 'execution_plan_failed', 'other') DEFAULT 'none' COMMENT 'SQL问题类型',
ADD COLUMN IF NOT EXISTS sql_issue_details TEXT COMMENT 'SQL问题详情',
ADD INDEX IF NOT EXISTS idx_analysis_status (analysis_status),
ADD INDEX IF NOT EXISTS idx_tablename (TABLENAME),
ADD INDEX IF NOT EXISTS idx_sql_issue_type (sql_issue_type);

-- 创建分析结果详情表（可选，用于更详细的结果存储）
CREATE TABLE IF NOT EXISTS analysis_details (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sql_id INT NOT NULL COMMENT '关联的SQL记录ID',
    analysis_type VARCHAR(50) COMMENT '分析类型',
    analysis_data JSON COMMENT '分析数据',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    FOREIGN KEY (sql_id) REFERENCES am_solline_info(id) ON DELETE CASCADE,
    INDEX idx_sql_id (sql_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='分析结果详情表';

-- 创建系统日志表
CREATE TABLE IF NOT EXISTS system_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    level VARCHAR(20) COMMENT '日志级别',
    module VARCHAR(50) COMMENT '模块名称',
    message TEXT COMMENT '日志消息',
    details JSON COMMENT '详细信息',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_level (level),
    INDEX idx_module (module),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='系统日志表';

-- 插入测试数据
INSERT INTO am_solline_info (sql_text, db_alias, table_names, status) VALUES
('SELECT * FROM users WHERE id = 1', 'db_production', 'users', 'pending'),
('SELECT u.name, o.amount FROM users u JOIN orders o ON u.id = o.user_id', 'db_production', 'users,orders', 'pending'),
('SELECT * FROM transaction_logs WHERE create_date > ''2024-01-01''', 'db_production', 'transaction_logs', 'pending'),
('UPDATE products SET price = price * 1.1 WHERE category = ''electronics''', 'db_production', 'products', 'pending'),
('DELETE FROM temp_logs WHERE created_at < DATE_SUB(NOW(), INTERVAL 30 DAY)', 'db_production', 'temp_logs', 'pending');

-- 创建示例目标数据库表（用于测试元数据收集）
-- 注意：这些表应该在实际的目标数据库中创建
/*
-- 在目标数据库中执行以下SQL：
CREATE DATABASE IF NOT EXISTS production_db;
USE production_db;

CREATE TABLE users (
    id INT PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_email (email)
);

CREATE TABLE orders (
    id INT PRIMARY KEY,
    user_id INT,
    amount DECIMAL(10,2),
    status VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    INDEX idx_user_id (user_id),
    INDEX idx_status (status)
);

CREATE TABLE transaction_logs (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    action VARCHAR(50),
    amount DECIMAL(15,2),
    create_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_create_date (create_date),
    INDEX idx_user_id (user_id)
);

CREATE TABLE products (
    id INT PRIMARY KEY,
    name VARCHAR(200),
    category VARCHAR(50),
    price DECIMAL(10,2),
    stock INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_category (category),
    INDEX idx_price (price)
);

CREATE TABLE temp_logs (
    id INT PRIMARY KEY AUTO_INCREMENT,
    message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_created_at (created_at)
);
*/
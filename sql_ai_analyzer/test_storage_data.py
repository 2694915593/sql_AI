#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试精简后的存储数据
"""

import json
from config.config_manager import ConfigManager
from ai_integration.model_client import ModelClient
from storage.result_processor import ResultProcessor

def test_storage_data():
    """测试精简后的存储数据"""
    print("=" * 80)
    print("测试精简后的存储数据")
    print("=" * 80)
    
    # 加载配置
    config = ConfigManager('config/config.ini')
    
    # 创建实例
    model_client = ModelClient(config)
    result_processor = ResultProcessor(config)
    
    # 模拟API响应（使用用户提供的报文）
    mock_response = {
        "suggestions": [],
        "analysis_summary": {
            "score": 8,
            "has_warnings": False,
            "suggestion_count": 0,
            "has_critical_issues": False,
            "has_optimization_suggestions": False
        },
        "metadata_summary": {
            "tables": [
                {
                    "row_count": 212,
                    "table_name": "pd_errcode",
                    "index_count": 0,
                    "column_count": 6,
                    "is_large_table": False,
                    "has_primary_key": True
                }
            ],
            "total_rows": 212,
            "table_count": 1,
            "large_tables": 0,
            "total_columns": 6,
            "total_indexes": 0
        },
        "detailed_analysis": {
            "RSP_BODY": {
                "head": {},
                "answer": "\"### SQL语句质量分析\\n\\n#### 1. 性能问题\\n- **缺少索引**：当前表 `pd_errcode` 没有定义任何索引。虽然表的行数较少（212行），但随着数据量的增长，插入操作可能会变得缓慢。特别是如果后续需要频繁查询或更新特定记录，缺乏索引会导致全表扫描。\\n- **全表扫描**：由于没有索引，插入操作可能会导致全表扫描，尤其是在表数据量较大时。\\n\\n#### 2. 潜在问题\\n- **SQL注入风险**：当前SQL语句是静态的，没有使用参数化查询，因此在实际应用中需要注意防止SQL注入攻击。\\n- **数据类型不匹配**：从DDL中可以看到，`PEC_LASTUPDATE` 列的默认值是 `'CURRENT_TIMESTAMP'`，但在插入语句中使用了具体的时间戳。这不会导致错误，但需要注意一致性。\\n- **数据完整性**：`PEC_CLASS` 列的数据类型为 `varchar(6)`，但在插入语句中使用的值是 `'1'`，虽然不会引起错误，但需要注意是否符合业务逻辑。\\n\\n#### 3. 优化建议\\n- **添加索引**：为了提高查询和更新性能，建议为经常用于查询的列（如 `PEC_ERRCODE` 和 `PEC_LANGUAGE`）添加索引。\\n  ```sql\\n  CREATE INDEX idx_pec_errcode ON pd_errcode (PEC_ERRCODE);\\n  CREATE INDEX idx_pec_language ON pd_errcode (PEC_LANGUAGE);\\n  ```\\n- **参数化查询**：在实际应用中，建议使用参数化查询来防止SQL注入攻击。\\n  ```java\\n  // 示例代码（Java + JDBC）\\n  String sql = \\\"INSERT INTO ecdcdb.pd_errcode (PEC_ERRCODE, PEC_LANGUAGE, PEC_SHOWMSG, PEC_INNERMSG, PEC_CLASS, PEC_LASTUPDATE) VALUES (?, ?, ?, ?, ?, ?)\\\";\\n  PreparedStatement pstmt = connection.prepareStatement(sql);\\n  pstmt.setString(1, \\\"20070004AC0010\\\");\\n  pstmt.setString(2, \\\"zh_CN\\\");\\n  pstmt.setString(3, \\\"命中金融惩戒名单，终止交易\\\");\\n  pstmt.setString(4, \\\"命中金融惩戒名单，终止交易\\\");\\n  pstmt.setString(5, \\\"1\\\");\\n  pstmt.setTimestamp(6, Timestamp.valueOf(\\\"2024-10-18 18:55:53.615353\\\"));\\n  pstmt.executeUpdate();\\n  ```\\n- **数据类型一致性**：确保插入的数据类型与表定义一致，特别是对于时间戳和字符串长度。\\n\\n#### 4. 综合评分\\n- **评分**：7/10\\n  - **优点**：SQL语句结构清晰，数据插入正确。\\n  - **缺点**：缺少索引，存在潜在的SQL注入风险，数据类型一致性需要关注。\\n\\n#### 5. 按严重程度分类建议\\n- **高优先级**：\\n  - 添加索引以提高查询和更新性能。\\n  - 使用参数化查询防止SQL注入攻击。\\n- **中优先级**：\\n  - 确保数据类型一致性，特别是在插入时间戳和字符串时。\\n- **低优先级**：\\n  - 定期检查表的性能，确保随着数据量增长不会出现性能瓶颈。\\n\\n通过以上优化，可以显著提升SQL语句的性能和安全性。\"",
                "prompt": "SQL语句：\nINSERT INTO ecdcdb.pd_errcode\r\n(PEC_ERRCODE, PEC_LANGUAGE, PEC_SHOWMSG, PEC_INNERMSG, PEC_CLASS, PEC_LASTUPDATE)\r\nVALUES('20070004AC0010', 'zh_CN', '命中金融惩戒名单，终止交易', '命中金融惩戒名单，终止交易', '1', '2024-10-18 18:55:53.615353');\r\n\n\n数据库：ECDC_SQL_SHELL_CTM\n\n涉及的表信息：\n\n表1：pd_errcode\n  - 行数：212\n  - 是否大表：否\n  - 列数：6\n  - 索引数：0\n  - DDL：\n    CREATE TABLE pd_errcode (PEC_ERRCODE char(14) NOT NULL, PEC_LANGUAGE varchar(10) NOT NULL, PEC_SHOWMSG varchar(200), PEC_INNERMSG varchar(200), PEC_CLASS varchar(6), PEC_LASTUPDATE timestamp(6) NOT NULL DEFAULT 'CURRENT_TIMESTAMP')\n  - 列信息：\n    * PEC_ERRCODE (char) 非空\n    * PEC_LANGUAGE (varchar) 非空\n    * PEC_SHOWMSG (varchar) 可空\n    * PEC_INNERMSG (varchar) 可空\n    * PEC_CLASS (varchar) 可空\n    * ... 还有1列\n\n请分析以上SQL语句的质量，包括：\n1. 性能问题（如缺少索引、全表扫描等）\n2. 潜在问题（如SQL注入风险、数据类型不匹配等）\n3. 优化建议\n4. 给出综合评分（0-10分）\n5. 按严重程度分类建议",
                "TRAN_PROCESS": "aiQA"
            },
            "RSP_HEAD": {
                "TRACE_NO": "SDSS118-38-115-8487196302",
                "TRAN_SUCCESS": "1"
            }
        },
        "categorized_suggestions": {}
    }
    
    # 模拟元数据
    mock_metadata = [
        {
            "table_name": "pd_errcode",
            "row_count": 212,
            "is_large_table": False,
            "ddl": "CREATE TABLE pd_errcode (PEC_ERRCODE char(14) NOT NULL, PEC_LANGUAGE varchar(10) NOT NULL, PEC_SHOWMSG varchar(200), PEC_INNERMSG varchar(200), PEC_CLASS varchar(6), PEC_LASTUPDATE timestamp(6) NOT NULL DEFAULT 'CURRENT_TIMESTAMP')",
            "columns": [
                {"name": "PEC_ERRCODE", "type": "char", "nullable": False},
                {"name": "PEC_LANGUAGE", "type": "varchar", "nullable": False},
                {"name": "PEC_SHOWMSG", "type": "varchar", "nullable": True},
                {"name": "PEC_INNERMSG", "type": "varchar", "nullable": True},
                {"name": "PEC_CLASS", "type": "varchar", "nullable": True},
                {"name": "PEC_LASTUPDATE", "type": "timestamp", "nullable": False}
            ],
            "indexes": [],
            "primary_keys": ["PEC_ERRCODE", "PEC_LANGUAGE"]
        }
    ]
    
    # 解析API响应
    print("1. 解析API响应:")
    print("-" * 40)
    
    class MockResponse:
        def __init__(self, data):
            self.status_code = 200
            self._data = data
            
        def json(self):
            return self._data
            
        @property
        def text(self):
            return json.dumps(self._data)
    
    mock_resp = MockResponse(mock_response)
    parsed_result = model_client._parse_response(mock_resp)
    
    print(f"✅ 解析成功")
    print(f"   评分: {parsed_result.get('score', 'N/A')}")
    print(f"   建议数量: {len(parsed_result.get('suggestions', []))}")
    
    # 准备存储数据
    print("\n2. 准备存储数据:")
    print("-" * 40)
    
    storage_data = result_processor._prepare_storage_data(parsed_result, mock_metadata)
    
    print(f"✅ 存储数据准备成功")
    print(f"   数据大小: {len(json.dumps(storage_data, ensure_ascii=False))} 字符")
    
    # 显示存储数据的结构
    print("\n3. 存储数据结构:")
    print("-" * 40)
    
    print("分析摘要:")
    analysis_summary = storage_data.get('analysis_summary', {})
    print(f"  • 评分: {analysis_summary.get('score', 'N/A')}")
    print(f"  • 建议数量: {analysis_summary.get('suggestion_count', 0)}")
    print(f"  • 是否有严重问题: {analysis_summary.get('has_critical_issues', False)}")
    print(f"  • 是否有警告: {analysis_summary.get('has_warnings', False)}")
    print(f"  • 是否有优化建议: {analysis_summary.get('has_optimization_suggestions', False)}")
    
    print("\n详细分析:")
    detailed_analysis = storage_data.get('detailed_analysis', '')
    print(f"  • 长度: {len(detailed_analysis)} 字符")
    print(f"  • 预览: {detailed_analysis[:100]}...")
    
    print("\n建议:")
    suggestions = storage_data.get('suggestions', [])
    print(f"  • 数量: {len(suggestions)}")
    for i, suggestion in enumerate(suggestions[:3], 1):
        print(f"  {i}. {suggestion[:80]}...")
    if len(suggestions) > 3:
        print(f"  ... 还有{len(suggestions)-3}条建议")
    
    print("\n元数据摘要:")
    metadata_summary = storage_data.get('metadata_summary', {})
    print(f"  • 表数量: {metadata_summary.get('table_count', 0)}")
    print(f"  • 总行数: {metadata_summary.get('total_rows', 0)}")
    print(f"  • 总列数: {metadata_summary.get('total_columns', 0)}")
    print(f"  • 总索引数: {metadata_summary.get('total_indexes', 0)}")
    
    print("\n分类建议:")
    categorized = storage_data.get('categorized_suggestions', {})
    for category, items in categorized.items():
        print(f"  • {category}: {len(items)} 条建议")
    
    # 检查是否包含不必要的报文信息
    print("\n4. 检查是否包含不必要的报文信息:")
    print("-" * 40)
    
    storage_json = json.dumps(storage_data, ensure_ascii=False)
    
    unnecessary_keys = ['RSP_HEAD', 'TRAN_PROCESS', 'TRACE_NO', 'TRAN_SUCCESS', 'prompt']
    found_unnecessary = []
    
    for key in unnecessary_keys:
        if key in storage_json:
            found_unnecessary.append(key)
    
    if found_unnecessary:
        print(f"❌ 发现不必要的报文信息: {found_unnecessary}")
    else:
        print("✅ 没有发现不必要的报文信息")
    
    # 检查原始报文是否被完整存储
    print("\n5. 检查原始报文是否被完整存储:")
    print("-" * 40)
    
    original_keys = list(mock_response.keys())
    stored_keys = list(storage_data.keys())
    
    print(f"原始报文键: {original_keys}")
    print(f"存储数据键: {stored_keys}")
    
    # 检查是否存储了完整的原始报文
    if 'detailed_analysis' in storage_data and isinstance(storage_data['detailed_analysis'], str):
        print("✅ 详细分析已提取为文本，没有存储完整的RSP_BODY结构")
    else:
        print("❌ 可能存储了完整的原始报文结构")
    
    # 显示精简效果
    print("\n6. 精简效果:")
    print("-" * 40)
    
    original_size = len(json.dumps(mock_response, ensure_ascii=False))
    stored_size = len(json.dumps(storage_data, ensure_ascii=False))
    
    print(f"原始报文大小: {original_size} 字符")
    print(f"存储数据大小: {stored_size} 字符")
    print(f"精简比例: {((original_size - stored_size) / original_size * 100):.1f}%")
    
    print("\n" + "=" * 80)
    print("测试总结")
    print("=" * 80)
    
    print("✅ 存储数据精简成功!")
    print("\n现在只存储以下必要内容:")
    print("1. 分析摘要（评分、建议数量、问题类型）")
    print("2. 详细分析文本（提取的answer内容）")
    print("3. 清理后的建议列表")
    print("4. 元数据摘要（表统计信息）")
    print("5. 分类建议（按性能、安全、可维护性等分类）")
    
    print("\n不再存储以下不必要内容:")
    print("• RSP_HEAD（报文头信息）")
    print("• TRAN_PROCESS（交易处理信息）")
    print("• TRACE_NO（跟踪号）")
    print("• TRAN_SUCCESS（交易成功标志）")
    print("• prompt（原始的prompt内容）")
    print("• 完整的RSP_BODY结构")
    
    print(f"\n精简效果: 数据大小减少 {((original_size - stored_size) / original_size * 100):.1f}%")

def main():
    """主函数"""
    print("测试存储数据精简")
    print("=" * 80)
    
    test_storage_data()

if __name__ == '__main__':
    main()
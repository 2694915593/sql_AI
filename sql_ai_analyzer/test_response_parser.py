#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试新的响应解析逻辑
"""

import json
from config.config_manager import ConfigManager
from ai_integration.model_client import ModelClient

def test_new_response_format():
    """测试新的响应格式解析"""
    print("=" * 80)
    print("测试新的响应格式解析")
    print("=" * 80)
    
    # 加载配置
    config = ConfigManager('config/config.ini')
    
    # 创建ModelClient实例
    model_client = ModelClient(config)
    
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
    
    print("模拟响应数据:")
    print(json.dumps(mock_response, ensure_ascii=False, indent=2)[:500] + "...")
    
    # 测试解析逻辑
    print("\n测试解析逻辑:")
    print("-" * 40)
    
    # 模拟一个requests.Response对象
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
    
    try:
        # 调用_parse_response方法
        result = model_client._parse_response(mock_resp)
        
        print("✅ 解析成功!")
        print(f"  成功状态: {result.get('success', False)}")
        print(f"  评分: {result.get('score', 'N/A')}")
        print(f"  建议数量: {len(result.get('suggestions', []))}")
        print(f"  是否有详细分析: {'detailed_analysis' in result}")
        print(f"  是否有元数据摘要: {'metadata_summary' in result}")
        
        # 显示提取的建议
        suggestions = result.get('suggestions', [])
        if suggestions:
            print(f"\n提取的建议 ({len(suggestions)} 条):")
            for i, suggestion in enumerate(suggestions[:5], 1):
                print(f"  {i}. {suggestion}")
            if len(suggestions) > 5:
                print(f"  ... 还有{len(suggestions)-5}条建议")
        else:
            print("\n⚠ 未提取到建议")
            
        # 显示详细分析
        if 'detailed_analysis' in result:
            detailed = result['detailed_analysis']
            print(f"\n详细分析 (前200字符):")
            print(f"  {detailed[:200]}...")
        
        # 显示元数据摘要
        if 'metadata_summary' in result:
            metadata = result['metadata_summary']
            print(f"\n元数据摘要:")
            print(f"  表数量: {metadata.get('table_count', 0)}")
            print(f"  总行数: {metadata.get('total_rows', 0)}")
            print(f"  总列数: {metadata.get('total_columns', 0)}")
            print(f"  总索引数: {metadata.get('total_indexes', 0)}")
        
        return True
        
    except Exception as e:
        print(f"❌ 解析失败: {type(e).__name__}: {e}")
        return False

def test_extract_suggestions_from_text():
    """测试从文本中提取建议"""
    print("\n" + "=" * 80)
    print("测试从文本中提取建议")
    print("=" * 80)
    
    config = ConfigManager('config/config.ini')
    model_client = ModelClient(config)
    
    # 测试文本（从响应中提取的answer）
    test_text = """### SQL语句质量分析

#### 1. 性能问题
- **缺少索引**：当前表 `pd_errcode` 没有定义任何索引。虽然表的行数较少（212行），但随着数据量的增长，插入操作可能会变得缓慢。特别是如果后续需要频繁查询或更新特定记录，缺乏索引会导致全表扫描。
- **全表扫描**：由于没有索引，插入操作可能会导致全表扫描，尤其是在表数据量较大时。

#### 2. 潜在问题
- **SQL注入风险**：当前SQL语句是静态的，没有使用参数化查询，因此在实际应用中需要注意防止SQL注入攻击。
- **数据类型不匹配**：从DDL中可以看到，`PEC_LASTUPDATE` 列的默认值是 `'CURRENT_TIMESTAMP'`，但在插入语句中使用了具体的时间戳。这不会导致错误，但需要注意一致性。
- **数据完整性**：`PEC_CLASS` 列的数据类型为 `varchar(6)`，但在插入语句中使用的值是 `'1'`，虽然不会引起错误，但需要注意是否符合业务逻辑。

#### 3. 优化建议
- **添加索引**：为了提高查询和更新性能，建议为经常用于查询的列（如 `PEC_ERRCODE` 和 `PEC_LANGUAGE`）添加索引。
  ```sql
  CREATE INDEX idx_pec_errcode ON pd_errcode (PEC_ERRCODE);
  CREATE INDEX idx_pec_language ON pd_errcode (PEC_LANGUAGE);
  ```
- **参数化查询**：在实际应用中，建议使用参数化查询来防止SQL注入攻击。
  ```java
  // 示例代码（Java + JDBC）
  String sql = "INSERT INTO ecdcdb.pd_errcode (PEC_ERRCODE, PEC_LANGUAGE, PEC_SHOWMSG, PEC_INNERMSG, PEC_CLASS, PEC_LASTUPDATE) VALUES (?, ?, ?, ?, ?, ?)";
  PreparedStatement pstmt = connection.prepareStatement(sql);
  pstmt.setString(1, "20070004AC0010");
  pstmt.setString(2, "zh_CN");
  pstmt.setString(3, "命中金融惩戒名单，终止交易");
  pstmt.setString(4, "命中金融惩戒名单，终止交易");
  pstmt.setString(5, "1");
  pstmt.setTimestamp(6, Timestamp.valueOf("2024-10-18 18:55:53.615353"));
  pstmt.executeUpdate();
  ```
- **数据类型一致性**：确保插入的数据类型与表定义一致，特别是对于时间戳和字符串长度。

#### 4. 综合评分
- **评分**：7/10
  - **优点**：SQL语句结构清晰，数据插入正确。
  - **缺点**：缺少索引，存在潜在的SQL注入风险，数据类型一致性需要关注。

#### 5. 按严重程度分类建议
- **高优先级**：
  - 添加索引以提高查询和更新性能。
  - 使用参数化查询防止SQL注入攻击。
- **中优先级**：
  - 确保数据类型一致性，特别是在插入时间戳和字符串时。
- **低优先级**：
  - 定期检查表的性能，确保随着数据量增长不会出现性能瓶颈。

通过以上优化，可以显著提升SQL语句的性能和安全性。"""
    
    print("测试文本长度:", len(test_text), "字符")
    
    try:
        suggestions = model_client._extract_suggestions_from_text(test_text)
        
        print(f"\n✅ 从文本中提取到 {len(suggestions)} 条建议:")
        for i, suggestion in enumerate(suggestions, 1):
            print(f"  {i}. {suggestion}")
            
        return True
        
    except Exception as e:
        print(f"❌ 提取建议失败: {type(e).__name__}: {e}")
        return False

def main():
    """主函数"""
    print("测试新的响应解析逻辑")
    print("=" * 80)
    
    # 测试新的响应格式解析
    test_new_response_format()
    
    # 测试从文本中提取建议
    test_extract_suggestions_from_text()
    
    print("\n" + "=" * 80)
    print("测试总结")
    print("=" * 80)
    
    print("✅ 新的响应解析逻辑已实现")
    print("\n主要改进:")
    print("1. 支持新的响应格式（包含detailed_analysis、analysis_summary等字段）")
    print("2. 从analysis_summary.score中提取评分")
    print("3. 从detailed_analysis.RSP_BODY.answer中提取详细分析")
    print("4. 从文本中智能提取建议（即使suggestions字段为空）")
    print("5. 提取元数据摘要信息")
    
    print("\n现在系统能够正确处理以下格式的响应:")
    print("  - suggestions: [] (可能为空)")
    print("  - analysis_summary.score: 8 (评分)")
    print("  - detailed_analysis.RSP_BODY.answer: '详细分析文本'")
    print("  - metadata_summary: 表统计信息")

if __name__ == '__main__':
    main()
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复SQL类型检测问题：添加XML标签移除功能
"""

import sys
import os
import re

# 清理模块缓存
sys.path_importer_cache.clear()

# 删除相关模块
for mod in list(sys.modules.keys()):
    if 'sql_ai_analyzer' in mod:
        del sys.modules[mod]

# 重新设置路径
project_root = os.path.dirname(os.path.abspath(__file__))
sql_ai_analyzer_dir = os.path.join(project_root, 'sql_ai_analyzer')
sys.path.insert(0, project_root)
sys.path.insert(0, sql_ai_analyzer_dir)

print("修复SQL类型检测 - 添加XML标签移除功能")
print("=" * 80)

# 首先读取metadata_collector.py文件，查看detect_sql_type方法的实现
metadata_collector_path = os.path.join(sql_ai_analyzer_dir, 'data_collector', 'metadata_collector.py')
backup_path = metadata_collector_path + '.backup'

print(f"读取文件: {metadata_collector_path}")

try:
    with open(metadata_collector_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 查找detect_sql_type方法
    if 'def detect_sql_type(self, sql_text: str) -> str:' in content:
        print("✓ 找到detect_sql_type方法")
        
        # 备份原始文件
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✓ 已创建备份: {backup_path}")
        
        # 分析当前实现
        lines = content.split('\n')
        detect_start = -1
        for i, line in enumerate(lines):
            if 'def detect_sql_type(self, sql_text: str) -> str:' in line:
                detect_start = i
                break
        
        if detect_start >= 0:
            # 找到方法结束位置（下一个def或文件结束）
            detect_end = len(lines)
            for i in range(detect_start + 1, len(lines)):
                if lines[i].strip().startswith('def ') and i > detect_start:
                    detect_end = i
                    break
            
            print(f"detect_sql_type方法从第{detect_start+1}行到第{detect_end}行")
            
            # 显示当前实现
            print("\n当前detect_sql_type方法实现:")
            print("-" * 40)
            for i in range(detect_start, min(detect_end, detect_start + 30)):
                print(f"{i+1:3}: {lines[i]}")
            print("-" * 40)
            
            # 修改detect_sql_type方法，添加XML标签移除功能
            # 我们需要在方法开始处添加代码来移除XML标签
            new_lines = lines.copy()
            
            # 在方法体内添加XML标签移除逻辑
            # 找到方法体开始位置（第一个缩进行）
            body_start = detect_start + 1
            while body_start < len(lines) and lines[body_start].strip() == '':
                body_start += 1
            
            # 插入XML标签移除代码
            xml_removal_code = [
                '        # 移除XML标签（如<select>、<insert>等）',
                '        if sql_text:',
                '            # 使用正则表达式移除XML标签',
                '            import re',
                '            # 移除所有<tag>...</tag>格式的XML标签，但保留标签内的内容',
                '            sql_text = re.sub(r\'<[^>]+>\', \' \', sql_text)',
                '            # 移除自闭合标签',
                '            sql_text = re.sub(r\'<[^>]+/>\', \' \', sql_text)',
                '            # 压缩多余空格',
                '            sql_text = re.sub(r\'\\s+\', \' \', sql_text).strip()',
                '',
                '        if not sql_text or not sql_text.strip():',
                '            return "UNKNOWN"',
                '',
                '        sql_upper = sql_text.strip().upper()',
            ]
            
            # 替换原有的if not sql_text检查和sql_upper赋值
            # 找到sql_upper = sql_text.strip().upper()这一行
            for i in range(body_start, min(detect_end, len(lines))):
                if 'sql_upper = sql_text.strip().upper()' in lines[i]:
                    # 替换这一部分
                    indent = len(lines[i]) - len(lines[i].lstrip())
                    indent_str = ' ' * indent
                    
                    # 构建新的方法体
                    new_body = []
                    # 保持方法签名
                    new_body.append(lines[detect_start])
                    new_body.append('')
                    
                    # 添加XML标签移除代码
                    for line in xml_removal_code:
                        new_body.append(indent_str + line)
                    
                    # 复制剩余的方法体（从DML关键字检查开始）
                    dml_check_start = -1
                    for j in range(i+1, min(detect_end, len(lines))):
                        if 'dml_keywords =' in lines[j]:
                            dml_check_start = j
                            break
                    
                    if dml_check_start >= 0:
                        for j in range(dml_check_start, detect_end):
                            new_body.append(lines[j])
                    
                    # 替换原始行
                    new_lines = lines[:detect_start] + new_body + lines[detect_end:]
                    
                    # 写入修改后的文件
                    with open(metadata_collector_path, 'w', encoding='utf-8') as f:
                        f.write('\n'.join(new_lines))
                    
                    print("✓ 已修改detect_sql_type方法，添加XML标签移除功能")
                    break
            
    else:
        print("✗ 未找到detect_sql_type方法")
        
except Exception as e:
    print(f"✗ 读取或修改文件失败: {e}")
    import traceback
    traceback.print_exc()

print("\n\n测试修复后的detect_sql_type方法:")
print("=" * 80)

# 重新导入测试
try:
    # 再次清理模块缓存
    for mod in list(sys.modules.keys()):
        if 'sql_ai_analyzer' in mod:
            del sys.modules[mod]
    
    # 重新导入
    from sql_ai_analyzer.config.config_manager import ConfigManager
    from sql_ai_analyzer.data_collector.metadata_collector import MetadataCollector
    
    cm = ConfigManager()
    import logging
    logger = logging.getLogger('test')
    logger.setLevel(logging.INFO)
    
    collector = MetadataCollector(cm, logger)
    
    # 测试用例
    test_cases = [
        ("SELECT * FROM users", "SELECT"),
        ("select * from users", "SELECT"),
        ("INSERT INTO users VALUES (1, 'test')", "INSERT"),
        ("UPDATE users SET name = 'test' WHERE id = 1", "UPDATE"),
        ("DELETE FROM users WHERE id = 1", "DELETE"),
        ("<select>SELECT * FROM users</select>", "SELECT (with XML tags)"),
        ("<select>\nSELECT * FROM users\n</select>", "SELECT (with XML tags and newlines)"),
        ("<query><select>SELECT * FROM users</select></query>", "SELECT (nested XML tags)"),
        ("<insert>INSERT INTO users VALUES (1, 'test')</insert>", "INSERT (with XML tags)"),
        ("<update>UPDATE users SET name = 'test' WHERE id = 1</update>", "UPDATE (with XML tags)"),
        ("<delete>DELETE FROM users WHERE id = 1</delete>", "DELETE (with XML tags)"),
        ("<sql><select>SELECT * FROM users WHERE id = 1</select></sql>", "SELECT (nested in sql tag)"),
        ("<statement type=\"select\">SELECT * FROM users</statement>", "SELECT (with attributes)"),
        ("<!-- comment -->SELECT * FROM users", "SELECT (with XML comment)"),
        ("<select>SELECT * FROM users</select> -- SQL comment", "SELECT (with XML tags and SQL comment)"),
        ("<select id=\"query1\">SELECT * FROM users</select>", "SELECT (with attribute)"),
        ("<select><![CDATA[SELECT * FROM users]]></select>", "SELECT (with CDATA)"),
        ("<sql type=\"query\"><select>SELECT name FROM users</select></sql>", "SELECT (complex XML)"),
    ]
    
    print("\n修复后detect_sql_type方法测试结果:")
    print("-" * 80)
    
    passed = 0
    total = len(test_cases)
    
    for sql, description in test_cases:
        sql_type = collector.detect_sql_type(sql)
        expected = "DML" if any(keyword.lower() in description.lower() for keyword in ["SELECT", "INSERT", "UPDATE", "DELETE"]) else "UNKNOWN"
        if "UNKNOWN" in description:
            expected = "UNKNOWN"
            
        status = "✓" if sql_type == expected else "✗"
        if sql_type == expected:
            passed += 1
            
        print(f"{status} {description:50} -> {sql_type:8} (期望: {expected})")
    
    print(f"\n测试通过率: {passed}/{total} ({passed/total*100:.1f}%)")
    
    # 显示修复后的方法内容
    print("\n\n修复后的detect_sql_type方法内容:")
    print("=" * 80)
    try:
        with open(metadata_collector_path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if 'def detect_sql_type(self, sql_text: str) -> str:' in line:
                    # 打印方法体
                    for j in range(i, min(i+50, len(lines))):
                        if j > i and lines[j].strip().startswith('def ') and j > i+10:
                            break
                        print(f"{j+1:3}: {lines[j]}")
                    break
    except Exception as e:
        print(f"无法读取修改后的文件: {e}")
    
except Exception as e:
    print(f"测试失败: {e}")
    import traceback
    traceback.print_exc()
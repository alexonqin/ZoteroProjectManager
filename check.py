#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查指定项目的 zotero.sqlite 中的 items 表
用法: python check.py
"""

import sqlite3
from pathlib import Path

# 修改为你 test 项目的实际路径
PROJECT_PATH = r"D:\ZoteroLibrary\test"  # 例如：D:\ZoteroLibrary\test

def main():
    data_path = Path(PROJECT_PATH) / "data" / "zotero.sqlite"
    if not data_path.exists():
        print(f"错误: 未找到数据库文件 {data_path}")
        return

    conn = sqlite3.connect(str(data_path))
    cursor = conn.cursor()

    # 1. 查看 items 表结构
    cursor.execute("PRAGMA table_info(items)")
    columns = cursor.fetchall()
    print("items 表的列:")
    for col in columns:
        print(f"  {col[1]} ({col[2]})")

    # 2. 统计总记录数
    cursor.execute("SELECT COUNT(*) FROM items")
    total = cursor.fetchone()[0]
    print(f"\nitems 表总记录数: {total}")

    # 3. 查看前 10 条记录（key, itemTypeID, dateAdded）
    cursor.execute("SELECT key, itemTypeID, dateAdded FROM items LIMIT 10")
    rows = cursor.fetchall()
    print("\n前 10 条 items 记录 (key, itemTypeID, dateAdded):")
    for row in rows:
        print(f"  key: {row[0]}, itemTypeID: {row[1]}, dateAdded: {row[2]}")

    # 4. 按 itemTypeID 分组统计
    cursor.execute("SELECT itemTypeID, COUNT(*) FROM items GROUP BY itemTypeID")
    type_counts = cursor.fetchall()
    print("\n按 itemTypeID 分组统计:")
    for tid, cnt in type_counts:
        print(f"  itemTypeID {tid}: {cnt}")

    # 5. 查询 itemTypes 表，显示类型名称
    cursor.execute("SELECT itemTypeID, typeName FROM itemTypes")
    types = cursor.fetchall()
    print("\nitemTypes 表:")
    for tid, name in types:
        print(f"  {tid}: {name}")

    conn.close()

if __name__ == "__main__":
    main()
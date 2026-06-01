#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""完全清理資料庫"""

import mysql.connector

config = {
    'host': 'ticketdb-ticket63.f.aivencloud.com',
    'port': 13599,
    'user': 'avnadmin',
    'password': 'AVNS_QqNVFqacdQinAgGmXY9',
    'database': 'defaultdb',
    'ssl_verify_cert': False,
    'ssl_verify_identity': False,
    'use_pure': True,
    'autocommit': True
}

conn = mysql.connector.connect(**config)
cursor = conn.cursor()

print("禁用外鍵檢查...")
cursor.execute("SET FOREIGN_KEY_CHECKS=0")
print("✓ 已禁用")

print("\n清理所有表...")
cursor.execute("SHOW TABLES")
tables = cursor.fetchall()

for table in tables:
    table_name = table[0]
    try:
        cursor.execute(f"DROP TABLE `{table_name}`")
        print(f"  ✓ {table_name} 已移除")
    except Exception as e:
        print(f"  ❌ {table_name}: {e}")

print("\n啟用外鍵檢查...")
cursor.execute("SET FOREIGN_KEY_CHECKS=1")
print("✓ 已啟用")

cursor.close()
conn.close()
print("\n✅ 資料庫完全清理")

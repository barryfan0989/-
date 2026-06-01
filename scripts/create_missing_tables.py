#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""建立缺失的表"""

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
    'autocommit': False
}

print("連接資料庫...")
conn = mysql.connector.connect(**config)
cursor = conn.cursor()

# 建立 artist_categories
print("\n建立 artist_categories 表...")
try:
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS artist_categories (
      id INT AUTO_INCREMENT PRIMARY KEY,
      artist_id INT NOT NULL COMMENT '藝人ID',
      genre VARCHAR(255) COMMENT '類型/流派',
      language VARCHAR(50) COMMENT '語言',
      created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY (artist_id) REFERENCES artists(id) ON DELETE CASCADE,
      INDEX idx_artist_id (artist_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """)
    print("  ✓ artist_categories 建立成功")
except Exception as e:
    print(f"  ❌ 失敗: {e}")

# 建立 event_tickets
print("\n建立 event_tickets 表...")
try:
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS event_tickets (
      id INT AUTO_INCREMENT PRIMARY KEY,
      event_id INT NOT NULL COMMENT '活動ID',
      ticket_type VARCHAR(255) COMMENT '票種',
      price INT COMMENT '票價',
      created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
      updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
      FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE,
      INDEX idx_event_id (event_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """)
    print("  ✓ event_tickets 建立成功")
except Exception as e:
    print(f"  ❌ 失敗: {e}")

# 建立 VIEW
print("\n建立 v_all_events_summary VIEW...")
try:
    cursor.execute("""
    CREATE OR REPLACE VIEW v_all_events_summary AS
    SELECT
      e.id AS event_id,
      e.name AS event_name,
      e.source_site,
      e.event_time,
      e.ticket_sale_time,
      e.event_url,
      v.id AS venue_id,
      v.name AS venue_name,
      v.address AS venue_address,
      v.city,
      v.description AS venue_description,
      GROUP_CONCAT(DISTINCT a.name SEPARATOR ', ') AS artists,
      GROUP_CONCAT(DISTINCT ac.genre SEPARATOR ', ') AS genres,
      GROUP_CONCAT(DISTINCT ac.language SEPARATOR ', ') AS languages,
      GROUP_CONCAT(DISTINCT CONCAT(et.ticket_type, ':', et.price) SEPARATOR '; ') AS tickets,
      e.scraped_at,
      e.created_at
    FROM events e
    LEFT JOIN venues v ON e.venue_id = v.id
    LEFT JOIN event_artists ea ON e.id = ea.event_id
    LEFT JOIN artists a ON ea.artist_id = a.id
    LEFT JOIN artist_categories ac ON a.id = ac.artist_id
    LEFT JOIN event_tickets et ON e.id = et.event_id
    GROUP BY e.id, e.name, e.source_site, e.event_time, e.ticket_sale_time, e.event_url, 
             v.id, v.name, v.address, v.city, v.description, e.scraped_at, e.created_at
    """)
    print("  ✓ v_all_events_summary VIEW 建立成功")
except Exception as e:
    print(f"  ❌ 失敗: {e}")

conn.commit()
cursor.close()
conn.close()

print("\n✅ 完成所有設定")

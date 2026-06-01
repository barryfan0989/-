#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""清理舊表並建立新表"""

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

# 先刪除 VIEW（因為它們可能依賴表）
print("\n清理舊的 VIEW...")
views_to_drop = ['v_all_events_summary', '活動聯合檢視', 'concert_overview']
for view in views_to_drop:
    try:
        cursor.execute(f"DROP VIEW IF EXISTS {view}")
        print(f"  ✓ {view} 已移除")
    except Exception as e:
        print(f"  ❌ {view} 移除失敗: {e}")

# 刪除外鍵關聯，再刪除表
print("\n清理舊的表...")
tables_to_drop = [
    'event_artists', 'event_tickets', 'artist_categories', 'artist_news',
    'artist_segments', 'artists_news', 'event_schedules', 'event_segments',
    'ticket_pricing', 'ticket_pricings', 'sales_channels', 'budget_recommendation_logs',
    'reminders', 'artists', 'events', 'venues', 'users',
    'import_log', 'venue_locations', 'concerts',
    '活動聯合檢視', '藝人', '活動', '活動地點', '使用者', '售票平台'
]

for table in tables_to_drop:
    try:
        cursor.execute(f"DROP TABLE IF EXISTS `{table}`")
        print(f"  ✓ {table} 已移除")
    except Exception as e:
        print(f"  ⚠ {table} 移除失敗: {e}")

conn.commit()

# 重新建立表
print("\n建立新表...")

# 1. users
print("\n  1. 建立 users 表...")
try:
    cursor.execute("""
    CREATE TABLE users (
      id INT AUTO_INCREMENT PRIMARY KEY,
      email VARCHAR(255) NOT NULL UNIQUE COMMENT '電郵地址',
      password_hash VARCHAR(255) NOT NULL COMMENT '密碼雜湊',
      registered_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '註冊時間',
      updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新時間'
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='使用者表'
    """)
    print("    ✓ users 建立成功")
except Exception as e:
    print(f"    ❌ 失敗: {e}")

# 2. artists
print("  2. 建立 artists 表...")
try:
    cursor.execute("""
    CREATE TABLE artists (
      id INT AUTO_INCREMENT PRIMARY KEY,
      name VARCHAR(255) NOT NULL UNIQUE COMMENT '藝人名稱',
      wiki_intro LONGTEXT COMMENT '維基百科介紹',
      wiki_url VARCHAR(512) COMMENT '維基百科連結',
      created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '建立時間',
      updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新時間'
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='藝人表'
    """)
    print("    ✓ artists 建立成功")
except Exception as e:
    print(f"    ❌ 失敗: {e}")

# 3. artist_categories
print("  3. 建立 artist_categories 表...")
try:
    cursor.execute("""
    CREATE TABLE artist_categories (
      id INT AUTO_INCREMENT PRIMARY KEY,
      artist_id INT NOT NULL COMMENT '藝人ID',
      genre VARCHAR(255) COMMENT '類型/流派',
      language VARCHAR(50) COMMENT '語言',
      created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '建立時間',
      FOREIGN KEY (artist_id) REFERENCES artists(id) ON DELETE CASCADE,
      INDEX idx_artist_id (artist_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='藝人分類表'
    """)
    print("    ✓ artist_categories 建立成功")
except Exception as e:
    print(f"    ❌ 失敗: {e}")

# 4. artist_news
print("  4. 建立 artist_news 表...")
try:
    cursor.execute("""
    CREATE TABLE artist_news (
      id INT AUTO_INCREMENT PRIMARY KEY,
      artist_id INT NOT NULL COMMENT '藝人ID',
      title VARCHAR(512) NOT NULL COMMENT '新聞標題',
      url VARCHAR(512) COMMENT '新聞連結',
      published_at DATETIME COMMENT '發布時間',
      created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '建立時間',
      updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新時間',
      FOREIGN KEY (artist_id) REFERENCES artists(id) ON DELETE CASCADE,
      INDEX idx_artist_id (artist_id),
      INDEX idx_published_at (published_at)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='藝人新聞表'
    """)
    print("    ✓ artist_news 建立成功")
except Exception as e:
    print(f"    ❌ 失敗: {e}")

# 5. venues
print("  5. 建立 venues 表...")
try:
    cursor.execute("""
    CREATE TABLE venues (
      id INT AUTO_INCREMENT PRIMARY KEY,
      name VARCHAR(255) NOT NULL UNIQUE COMMENT '場館名稱',
      address VARCHAR(512) COMMENT '場館地址',
      city VARCHAR(100) COMMENT '城市',
      description LONGTEXT COMMENT '場館介紹',
      created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '建立時間',
      updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新時間'
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='場館表'
    """)
    print("    ✓ venues 建立成功")
except Exception as e:
    print(f"    ❌ 失敗: {e}")

# 6. events
print("  6. 建立 events 表...")
try:
    cursor.execute("""
    CREATE TABLE events (
      id INT AUTO_INCREMENT PRIMARY KEY,
      venue_id INT COMMENT '場館ID',
      name VARCHAR(512) NOT NULL COMMENT '活動名稱',
      source_site VARCHAR(100) NOT NULL COMMENT '來源網站',
      ticket_sale_time DATETIME COMMENT '購票時間',
      event_time DATETIME COMMENT '演出時間',
      event_url VARCHAR(512) NOT NULL COMMENT '活動網址',
      scraped_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '爬蟲時間',
      created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '建立時間',
      updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新時間',
      FOREIGN KEY (venue_id) REFERENCES venues(id) ON DELETE SET NULL,
      INDEX idx_source_site (source_site),
      INDEX idx_event_time (event_time),
      INDEX idx_venue_id (venue_id),
      UNIQUE KEY uk_event_url (event_url)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='活動表'
    """)
    print("    ✓ events 建立成功")
except Exception as e:
    print(f"    ❌ 失敗: {e}")

# 7. event_tickets
print("  7. 建立 event_tickets 表...")
try:
    cursor.execute("""
    CREATE TABLE event_tickets (
      id INT AUTO_INCREMENT PRIMARY KEY,
      event_id INT NOT NULL COMMENT '活動ID',
      ticket_type VARCHAR(255) COMMENT '票種',
      price INT COMMENT '票價',
      created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '建立時間',
      updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新時間',
      FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE,
      INDEX idx_event_id (event_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='票券表'
    """)
    print("    ✓ event_tickets 建立成功")
except Exception as e:
    print(f"    ❌ 失敗: {e}")

# 8. event_artists
print("  8. 建立 event_artists 表...")
try:
    cursor.execute("""
    CREATE TABLE event_artists (
      event_id INT NOT NULL,
      artist_id INT NOT NULL,
      created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '建立時間',
      PRIMARY KEY (event_id, artist_id),
      FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE,
      FOREIGN KEY (artist_id) REFERENCES artists(id) ON DELETE CASCADE,
      INDEX idx_artist_id (artist_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='活動與藝人多對多關係表'
    """)
    print("    ✓ event_artists 建立成功")
except Exception as e:
    print(f"    ❌ 失敗: {e}")

# 9. VIEW
print("  9. 建立 v_all_events_summary VIEW...")
try:
    cursor.execute("""
    CREATE VIEW v_all_events_summary AS
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
    print("    ✓ v_all_events_summary VIEW 建立成功")
except Exception as e:
    print(f"    ❌ 失敗: {e}")

conn.commit()
cursor.close()
conn.close()

print("\n" + "=" * 70)
print("✅ 資料庫建表完成")
print("=" * 70)

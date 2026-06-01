#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""建立 VIEW"""

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

view_sql = """CREATE OR REPLACE VIEW v_all_events_summary AS
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
         v.id, v.name, v.address, v.city, v.description, e.scraped_at, e.created_at"""

try:
    cursor.execute(view_sql)
    conn.commit()
    print("✓ VIEW v_all_events_summary 建立成功")
except Exception as e:
    print(f"❌ VIEW 建立失敗: {e}")
    conn.rollback()

cursor.close()
conn.close()
print("✓ 完成")

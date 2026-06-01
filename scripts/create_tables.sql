-- ============================================================================
-- 售票網站資料整合系統 - MySQL 建表腳本
-- ============================================================================

-- 使用指定資料庫
USE defaultdb;

-- ============================================================================
-- 1. users - 使用者表
-- ============================================================================
CREATE TABLE IF NOT EXISTS users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  email VARCHAR(255) NOT NULL UNIQUE COMMENT '電郵地址',
  password_hash VARCHAR(255) NOT NULL COMMENT '密碼雜湊',
  registered_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '註冊時間',
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新時間'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='使用者表';

-- ============================================================================
-- 2. artists - 藝人表
-- ============================================================================
CREATE TABLE IF NOT EXISTS artists (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(255) NOT NULL UNIQUE COMMENT '藝人名稱',
  wiki_intro LONGTEXT COMMENT '維基百科介紹',
  wiki_url VARCHAR(512) COMMENT '維基百科連結',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '建立時間',
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新時間'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='藝人表';

-- ============================================================================
-- 3. artist_categories - 藝人分類表
-- ============================================================================
CREATE TABLE IF NOT EXISTS artist_categories (
  id INT AUTO_INCREMENT PRIMARY KEY,
  artist_id INT NOT NULL COMMENT '藝人ID',
  genre VARCHAR(255) COMMENT '類型/流派（如：華語流行）',
  language VARCHAR(50) COMMENT '語言（如：繁體中文、英文）',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '建立時間',
  FOREIGN KEY (artist_id) REFERENCES artists(id) ON DELETE CASCADE,
  INDEX idx_artist_id (artist_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='藝人分類表';

-- ============================================================================
-- 4. artist_news - 藝人新聞表
-- ============================================================================
CREATE TABLE IF NOT EXISTS artist_news (
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='藝人新聞表';

-- ============================================================================
-- 5. venues - 場館表
-- ============================================================================
CREATE TABLE IF NOT EXISTS venues (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(255) NOT NULL UNIQUE COMMENT '場館名稱',
  address VARCHAR(512) COMMENT '場館地址',
  city VARCHAR(100) COMMENT '城市',
  description LONGTEXT COMMENT '場館介紹',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '建立時間',
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新時間'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='場館表';

-- ============================================================================
-- 6. events - 活動表
-- ============================================================================
CREATE TABLE IF NOT EXISTS events (
  id INT AUTO_INCREMENT PRIMARY KEY,
  venue_id INT COMMENT '場館ID',
  name VARCHAR(512) NOT NULL COMMENT '活動名稱',
  source_site VARCHAR(100) NOT NULL COMMENT '來源網站（Indievox, KKTIX, ticket.com.tw, ibon, Kham）',
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='活動表';

-- ============================================================================
-- 7. event_tickets - 票券表
-- ============================================================================
CREATE TABLE IF NOT EXISTS event_tickets (
  id INT AUTO_INCREMENT PRIMARY KEY,
  event_id INT NOT NULL COMMENT '活動ID',
  ticket_type VARCHAR(255) COMMENT '票種（如：全票、學生票）',
  price INT COMMENT '票價（單位：元）',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '建立時間',
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新時間',
  FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE,
  INDEX idx_event_id (event_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='票券表';

-- ============================================================================
-- 8. event_artists - 多對多橋樑表（活動與藝人）
-- ============================================================================
CREATE TABLE IF NOT EXISTS event_artists (
  event_id INT NOT NULL,
  artist_id INT NOT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '建立時間',
  PRIMARY KEY (event_id, artist_id),
  FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE,
  FOREIGN KEY (artist_id) REFERENCES artists(id) ON DELETE CASCADE,
  INDEX idx_artist_id (artist_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='活動與藝人多對多關係表';

-- ============================================================================
-- 9. v_all_events_summary - 活動摘要檢視表
-- ============================================================================
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
         v.id, v.name, v.address, v.city, v.description, e.scraped_at, e.created_at;

-- ============================================================================
-- 建表完成
-- ============================================================================

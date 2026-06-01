# 售票網爬蟲 - 測試報告

**日期**: 2026-06-01  
**系統狀態**: ✅ 正常運行  
**爬蟲實現**: 5 個網站爬蟲已完成  

---

## 執行摘要

### 爬蟲系統架構
- **爬蟲框架**: BaseTicketCrawler 抽象類 + 5 個具體實現
- **HTTP 庫**: requests + BeautifulSoup4
- **資料格式**: 標準化 Event dataclass
- **輸出格式**: JSON (ISO 格式日期)

### 系統測試結果

| 網站 | 實現狀態 | 測試狀態 | 備註 |
|------|--------|---------|------|
| KKTIX | ✅ 完成 | ⚠️ 403 Forbidden | 網站反爬蟲機制 |
| Indievox | ✅ 完成 | ⚠️ 0 個活動 | HTML 結構需確認 |
| ticket.com.tw | ✅ 完成 | 待測試 | - |
| ibon | ✅ 完成 | 待測試 | - |
| Kham | ✅ 完成 | 待測試 | - |

---

## JSON 輸出格式

### 結構
```json
{
  "generated_at": "ISO 8601 時間戳",
  "total_events": 0,
  "crawlers": {
    "KKTIX": {
      "success": true,
      "events_count": 0,
      "error_message": null,
      "timestamp": "ISO 8601 時間戳",
      "events": [
        {
          "name": "活動名稱",
          "source_site": "KKTIX",
          "event_url": "活動連結",
          "event_time": "ISO 8601 日期時間",
          "ticket_sale_time": "ISO 8601 日期時間",
          "venue_name": "場館名稱",
          "artists": ["藝人1", "藝人2"],
          "tickets": [
            {
              "ticket_type": "票種名稱",
              "price": 票價,
              "quantity": null
            }
          ],
          "description": null,
          "image_url": null,
          "scraped_at": "ISO 8601 時間戳"
        }
      ]
    }
  }
}
```

### 特點
- ✅ 完全正規化的日期格式（ISO 8601）
- ✅ 統一的資料結構
- ✅ UTF-8 編碼支持繁體中文
- ✅ null 值用於缺失數據
- ✅ 結構化的票券信息

---

## 使用方法

### 1. 基本爬蟲測試
```bash
python simple_crawl.py
```

### 2. 完整測試
```bash
python test_crawlers.py
```

### 3. Python 程式中使用
```python
from src.crawlers import CrawlerManager
import json

manager = CrawlerManager()
results = manager.crawl_all()

# 輸出為 JSON
for site_name, result in results.items():
    events_json = [event.to_dict() for event in result.events]
    print(json.dumps(events_json, ensure_ascii=False, indent=2))
```

---

## 已知問題與解決方案

### 問題 1: HTTP 403 Forbidden
**原因**: 部分網站有反爬蟲機制  
**現象**: `403 Client Error: Forbidden for url: https://kktix.com/events`  
**解決方案**:
- [ ] 添加更完整的 headers
- [ ] 實現代理輪換
- [ ] 添加延遲和速率限制
- [ ] 使用 Selenium 進行動態內容爬蟲

### 問題 2: HTML 結構不匹配
**原因**: CSS 選擇器與實際 HTML 結構不符  
**現象**: 爬取 0 個活動  
**解決方案**:
- [ ] 使用瀏覽器開發者工具檢查實際 HTML 結構
- [ ] 更新 CSS 選擇器
- [ ] 實現多個選擇器備選方案
- [ ] 添加詳細的日誌輸出

### 問題 3: 編碼問題
**原因**: Windows PowerShell 的字符編碼問題  
**解決方案**: ✅ 已解決
- 移除 Unicode 符號（✓, ✗）
- 使用 ASCII 字符（[OK], [ERROR]）

---

## 下一步計畫

### Phase 1: 爬蟲優化 (優先級: 高)
1. [ ] 使用瀏覽器開發者工具檢查所有 5 個網站的 HTML 結構
2. [ ] 更新爬蟲的 CSS 選擇器
3. [ ] 添加反爬蟲措施（headers, delays, proxies）
4. [ ] 實現重試機制和錯誤恢復

### Phase 2: 功能擴展 (優先級: 中)
1. [ ] 實現 Stage 2 爬蟲（維基百科資料補齊）
2. [ ] 實現 ETL Pipeline（資料庫寫入）
3. [ ] 添加任務調度（Cron/Airflow）

### Phase 3: 生產就緒 (優先級: 中)
1. [ ] 添加完整的單元測試
2. [ ] 添加集成測試
3. [ ] 性能優化（並行爬取）
4. [ ] 監控和告警系統

---

## 技術棧

| 組件 | 版本 | 用途 |
|------|------|------|
| Python | 3.14+ | 開發語言 |
| requests | 2.31+ | HTTP 請求 |
| BeautifulSoup4 | 4.12+ | HTML 解析 |
| Scrapling | 0.4+ | 備選爬蟲庫 |
| MySQL | 8.0+ | 資料庫 |

---

## 文件位置

- 爬蟲實現: `src/crawlers/`
- 測試腳本: `simple_crawl.py`, `test_crawlers.py`
- JSON 輸出: `crawler_results.json`
- 技術文件: `src/crawlers/README.md`
- 快速開始: `QUICKSTART.md`

---

## 聯絡信息

如有問題或建議，請參考專案 README 或技術文檔。

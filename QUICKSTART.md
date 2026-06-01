# 快速開始指南

## 安裝依賴

```bash
pip install -r requirements.txt
```

## 方式 1：使用爬蟲管理器爬取所有網站

```python
from src.crawlers import CrawlerManager

# 建立管理器（預設爬取所有已註冊的網站）
manager = CrawlerManager()

# 爬取
results = manager.crawl_all()

# 打印摘要
manager.print_summary()

# 取得所有活動
all_events = manager.get_all_events()
print(f"總共爬取 {len(all_events)} 個活動")
```

## 方式 2：爬取單個網站

```python
from src.crawlers import CrawlerManager

# 只爬取 KKTIX 和 Indievox
manager = CrawlerManager(sites=["KKTIX", "Indievox"])
results = manager.crawl_all()

# 取得 KKTIX 的結果
kktix_result = results["KKTIX"]
if kktix_result.success:
    print(f"成功爬取 {kktix_result.events_count} 個活動")
    for event in kktix_result.events[:3]:
        print(f"  - {event.name}")
```

## 方式 3：直接使用爬蟲

```python
from src.crawlers import CrawlerFactory

# 列出所有可用的爬蟲
print(CrawlerFactory.list_crawlers())

# 建立 KKTIX 爬蟲
crawler = CrawlerFactory.get_crawler("KKTIX")

# 執行爬蟲
result = crawler.crawl()

if result.success:
    for event in result.events:
        print(event)
else:
    print(f"爬蟲失敗: {result.error_message}")
```

## 方式 4：將活動匯出為 JSON

```python
import json
from src.crawlers import CrawlerManager

manager = CrawlerManager()
results = manager.crawl_all()

all_events = manager.get_all_events()

# 轉換為 JSON
events_json = [event.to_dict() for event in all_events]

# 寫入檔案
with open("events.json", "w", encoding="utf-8") as f:
    json.dump(events_json, f, ensure_ascii=False, indent=2)

print(f"已將 {len(all_events)} 個活動匯出到 events.json")
```

## 方式 5：過濾與分析活動

```python
from src.crawlers import CrawlerManager

manager = CrawlerManager()
results = manager.crawl_all()

all_events = manager.get_all_events()

# 過濾：只顯示有藝人資訊的活動
events_with_artists = [e for e in all_events if e.artists]
print(f"有藝人資訊的活動: {len(events_with_artists)}/{len(all_events)}")

# 過濾：只顯示有票價的活動
events_with_tickets = [e for e in all_events if e.tickets]
print(f"有票價資訊的活動: {len(events_with_tickets)}/{len(all_events)}")

# 統計：按來源網站分類
from collections import Counter
source_counts = Counter(e.source_site for e in all_events)
print("按網站分類:")
for site, count in source_counts.most_common():
    print(f"  {site}: {count} 個活動")

# 找出最便宜的票
if events_with_tickets:
    cheapest_event = min(
        events_with_tickets,
        key=lambda e: min(t.price for t in e.tickets)
    )
    cheapest_ticket = min(cheapest_event.tickets, key=lambda t: t.price)
    print(f"\n最便宜的票:")
    print(f"  活動: {cheapest_event.name}")
    print(f"  網站: {cheapest_event.source_site}")
    print(f"  票種: {cheapest_ticket.ticket_type}")
    print(f"  票價: {cheapest_ticket.price} 元")
```

## 常見錯誤與解決方案

### 錯誤 1：`ModuleNotFoundError: No module named 'src'`

**解決方案**：確保在專案根目錄執行，或調整 Python path：

```python
import sys
sys.path.insert(0, '/path/to/project')
from src.crawlers import CrawlerManager
```

### 錯誤 2：`ImportError: No module named 'scrapling'`

**解決方案**：安裝 Scrapling

```bash
pip install scrapling
```

### 錯誤 3：爬蟲返回空列表或錯誤

**解決方案**：
1. 檢查網站是否在線
2. 檢查爬蟲的 CSS selector 是否有效（網站結構可能已變更）
3. 查看日誌輸出了解具體錯誤

## 進階使用

### 自訂爬蟲

```python
from src.crawlers import BaseTicketCrawler, CrawlerFactory
from src.crawlers.data_models import Event, Ticket
from datetime import datetime

class MyCustomCrawler(BaseTicketCrawler):
    def __init__(self):
        super().__init__("MyWebsite", timeout=60)
    
    def _crawl_impl(self):
        events = []
        # ... 你的爬蟲邏輯 ...
        return events

# 註冊
CrawlerFactory.register("MyWebsite", MyCustomCrawler)

# 使用
from src.crawlers import CrawlerManager
manager = CrawlerManager(sites=["MyWebsite"])
results = manager.crawl_all()
```

### 並行爬取

```python
from concurrent.futures import ThreadPoolExecutor
from src.crawlers import CrawlerFactory

def crawl_site(site_name):
    crawler = CrawlerFactory.get_crawler(site_name)
    return site_name, crawler.crawl()

sites = ["KKTIX", "Indievox", "ticket.com.tw", "ibon", "Kham"]

with ThreadPoolExecutor(max_workers=3) as executor:
    results = dict(executor.map(crawl_site, sites))

for site_name, result in results.items():
    print(f"{site_name}: {result.events_count} 個活動")
```

## 後續步驟

1. **測試爬蟲**：確保各個爬蟲能正常工作
2. **實作 Stage 2**：補齊藝人與場館資訊
3. **實作 Data Pipeline**：將爬蟲數據寫入 MySQL
4. **建立 CLI/Scheduler**：自動化爬蟲執行

## 更多資訊

詳細文件請參考 `src/crawlers/README.md`

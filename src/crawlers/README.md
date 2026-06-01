# Stage 1 爬蟲系統 - 售票網活動爬蟲

## 概述

Stage 1 爬蟲系統是一個使用 **Scrapling** 作為核心的售票網爬蟲框架，支持五大台灣售票平台：
- KKTIX
- Indievox
- ticket.com.tw（拓元）
- ibon
- Kham（寬宏）

系統採用 **Strategy Pattern** 設計，通過 `BaseTicketCrawler` 抽象類定義統一介面，各具體爬蟲實現自己的邏輯。

## 系統架構

```
src/crawlers/
├── __init__.py                 # 模組初始化與爬蟲註冊
├── data_models.py              # 資料模型（Event, Ticket, CrawlResult）
├── base_crawler.py             # 基礎爬蟲抽象類
├── stage1_crawlers.py          # 具體爬蟲實現（5 個網站）
├── crawler_manager.py          # 爬蟲工廠與管理器
├── examples.py                 # 使用範例
└── README.md                   # 本檔
```

## 核心概念

### 1. 資料模型

#### `Ticket` (票券)
```python
@dataclass
class Ticket:
    ticket_type: str      # 票種（例：全票、學生票）
    price: int            # 票價（新台幣）
    quantity: Optional[int] = None  # 售票數量
```

#### `Event` (活動)
```python
@dataclass
class Event:
    name: str                          # 活動名稱
    source_site: str                   # 來源網站
    event_url: str                     # 活動網址
    event_time: Optional[datetime]     # 演出時間
    ticket_sale_time: Optional[datetime]  # 購票時間
    venue_name: Optional[str]          # 場館名稱
    artists: List[str]                 # 藝人列表
    tickets: List[Ticket]              # 票券列表
    description: Optional[str]         # 活動描述
    image_url: Optional[str]           # 海報連結
    scraped_at: Optional[datetime]     # 爬蟲時間戳
```

#### `CrawlResult` (爬蟲結果)
```python
@dataclass
class CrawlResult:
    success: bool                 # 爬蟲是否成功
    events: List[Event]           # 爬取的活動列表
    error_message: Optional[str]  # 錯誤訊息
    events_count: int             # 活動計數
    timestamp: datetime           # 執行時間戳
```

### 2. 基礎爬蟲類 - `BaseTicketCrawler`

所有具體爬蟲必須繼承此類，並實作 `_crawl_impl()` 方法。

**功能**：
- 統一的異常處理與日誌記錄
- 資料驗證與去重
- 工具方法：`parse_datetime()`, `clean_price()`, `clean_text()`

**示例**：
```python
from src.crawlers import BaseTicketCrawler
from src.crawlers.data_models import Event, Ticket

class MyCustomCrawler(BaseTicketCrawler):
    def __init__(self):
        super().__init__("MyWebsite")
    
    def _crawl_impl(self) -> List[Event]:
        # 實作你的爬蟲邏輯
        events = []
        # ... 爬取邏輯 ...
        return events
```

### 3. 爬蟲工廠 - `CrawlerFactory`

使用工廠模式集中管理爬蟲實例。

**註冊爬蟲**：
```python
CrawlerFactory.register("MyWebsite", MyCustomCrawler)
```

**取得爬蟲**：
```python
crawler = CrawlerFactory.get_crawler("KKTIX")
```

**列出所有爬蟲**：
```python
sites = CrawlerFactory.list_crawlers()
# ['KKTIX', 'Indievox', 'ticket.com.tw', 'ibon', 'Kham']
```

### 4. 爬蟲管理器 - `CrawlerManager`

協調多個爬蟲的批量執行。

**爬取所有網站**：
```python
manager = CrawlerManager()  # 預設爬取所有已註冊的網站
results = manager.crawl_all()
```

**爬取指定網站**：
```python
manager = CrawlerManager(sites=["KKTIX", "Indievox"])
results = manager.crawl_all()
```

**爬取單個網站**：
```python
result = manager.crawl_single("KKTIX")
```

**取得所有活動**：
```python
all_events = manager.get_all_events()
```

**打印摘要**：
```python
manager.print_summary()
```

## 使用範例

### 範例 1：爬取單個網站

```python
from src.crawlers import CrawlerManager

manager = CrawlerManager(sites=["KKTIX"])
results = manager.crawl_all()

kktix_result = results["KKTIX"]
if kktix_result.success:
    for event in kktix_result.events:
        print(f"{event.name} @ {event.venue_name}")
        print(f"  演出時間：{event.event_time}")
        print(f"  藝人：{', '.join(event.artists)}")
        for ticket in event.tickets:
            print(f"    {ticket.ticket_type}: {ticket.price} 元")
```

### 範例 2：爬取所有網站

```python
from src.crawlers import CrawlerManager

manager = CrawlerManager()
results = manager.crawl_all()
manager.print_summary()

# 取得所有活動
all_events = manager.get_all_events()
print(f"總共爬取 {len(all_events)} 個活動")
```

### 範例 3：直接使用爬蟲

```python
from src.crawlers import CrawlerFactory

crawler = CrawlerFactory.get_crawler("Indievox")
result = crawler.crawl()

if result.success:
    for event in result.events:
        print(event)
```

### 範例 4：將活動轉換為 JSON

```python
import json
from src.crawlers import CrawlerManager

manager = CrawlerManager(sites=["KKTIX"])
results = manager.crawl_all()
events = results["KKTIX"].events

# 轉換為 JSON
events_json = [event.to_dict() for event in events]
print(json.dumps(events_json, ensure_ascii=False, indent=2))
```

## 具體爬蟲實現

### KKTIX Crawler

支援爬取 KKTIX 平台的演唱會活動。

```python
from src.crawlers import KKTIXCrawler

crawler = KKTIXCrawler()
result = crawler.crawl()
```

### Indievox Crawler

支援爬取 Indievox 平台的演唱會活動。

```python
from src.crawlers import IndievoxCrawler

crawler = IndievoxCrawler()
result = crawler.crawl()
```

### Ticket.com.tw (拓元) Crawler

支援爬取拓元平台的演唱會活動。

```python
from src.crawlers import TuoYuanCrawler

crawler = TuoYuanCrawler()
result = crawler.crawl()
```

### ibon Crawler

支援爬取 ibon 平台的演唱會活動。

```python
from src.crawlers import IBonCrawler

crawler = IBonCrawler()
result = crawler.crawl()
```

### Kham (寬宏) Crawler

支援爬取寬宏平台的演唱會活動。

```python
from src.crawlers import KhamCrawler

crawler = KhamCrawler()
result = crawler.crawl()
```

## 關鍵特性

### 1. 統一的資料結構

所有爬蟲回傳相同格式的 `Event` 物件，便於後續 ETL pipeline 處理。

### 2. 錯誤處理與去重

- 自動過濾缺少必要欄位的活動
- 根據 URL 去重
- 完整的日誌記錄

### 3. 工具方法

- `parse_datetime(date_str, format_str)` - 日期解析
- `clean_price(price_str)` - 票價提取
- `clean_text(text)` - 文本清理

### 4. 可擴展性

新增支持的網站只需：
1. 新建爬蟲類繼承 `BaseTicketCrawler`
2. 實作 `_crawl_impl()` 方法
3. 在 `__init__.py` 中註冊

```python
# 新增爬蟲
class NewSiteCrawler(BaseTicketCrawler):
    def __init__(self):
        super().__init__("NewSite")
    
    def _crawl_impl(self):
        # ... 實作邏輯 ...
        pass

# 註冊
CrawlerFactory.register("NewSite", NewSiteCrawler)
```

## 配置與環境變數

建議使用 `.env` 檔案存放敏感資訊：

```env
# .env
SCRAPLING_TIMEOUT=30
SCRAPLING_RETRY_COUNT=3
LOG_LEVEL=INFO
```

## 性能優化建議

1. **並行爬取**：使用 `concurrent.futures` 或 `asyncio` 並行執行多個爬蟲
2. **快取機制**：針對重複的爬蟲請求進行快取
3. **速率限制**：在 `_crawl_impl()` 中加入 `time.sleep()` 避免被封
4. **代理輪換**：使用代理池在多個 IP 之間輪換

## 常見問題

### Q1：如何處理網站結構變更？

更新對應爬蟲類的 CSS selector，例如更新 `_parse_kktix_event()` 中的選擇器。

### Q2：如何支持分頁爬取？

在 `_crawl_impl()` 中迴圈多個頁面的 URL，例如：

```python
def _crawl_impl(self):
    events = []
    for page in range(1, 11):  # 爬取 10 頁
        url = f"{self.base_url}/events?page={page}"
        # ... 爬取邏輯 ...
    return events
```

### Q3：如何調試爬蟲？

檢查日誌輸出，爬蟲會輸出詳細的解析過程。

## 下一步

完成 Stage 1 爬蟲後，請繼續：

1. **Stage 2 爬蟲**：使用維基百科補齊藝人與場館資訊
2. **Data Pipeline**：實現 ETL 流程將爬蟲數據持久化到 MySQL

## 文件參考

- [Scrapling 官方文件](https://github.com/D4Vinci/Scrapling)
- Python dataclass 文件
- 策略模式（Strategy Pattern）

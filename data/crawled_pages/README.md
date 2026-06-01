# crawled_pages

此資料夾用於儲存爬蟲抓取的原始頁面或中繼資料，目的是統一管理各售票站的抓取輸出，方便後續解析與重現抓取流程。

結構：
- `crawled_pages/`
  - `indievox/`：Indievox 原始檔（HTML、JSON）
  - `kktix/`：KKTIX 原始檔
  - `ticket_com_tw/`：ticket.com.tw（拓元）原始檔
  - `ibon/`：ibon 原始檔
  - `kham/`：寬宏（Kham）原始檔

使用建議：
- 每次抓取請把輸出依時間或 event id 放入對應網站資料夾內，例如 `indievox/2026-06-01_event123.html`。
- 若想統一由爬蟲程式寫入，請在爬蟲設定中把輸出路徑設定為 `crawled_pages/<site>/`。
- 目前尚未自動移動現有 `downloaded_files`，若需要我可以幫忙整理。

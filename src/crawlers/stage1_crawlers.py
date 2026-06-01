#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Stage 1 爬蟲 - 具體實現
"""

from typing import List, Optional
from datetime import datetime
import re
import json

try:
    import requests
    from bs4 import BeautifulSoup
    from curl_cffi import requests as curl_requests
except ImportError:
    pass

from scrapling import Selector
from scrapling.fetchers import Fetcher

from .base_crawler import BaseTicketCrawler
from .data_models import Event, Ticket


class KKTIXCrawler(BaseTicketCrawler):
    """KKTIX 售票網爬蟲"""
    
    def __init__(self):
        super().__init__("KKTIX", timeout=30)
        self.base_url = "https://kktix.com"
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
        
    def _is_concert(self, name: str, description: str) -> bool:
        concert_keywords = [
            '演唱會', '音樂會', '音樂祭', '音樂節', 'Live House', 'Livehouse', 
            '巡迴演唱', '巡迴公演', '獨奏會', '演奏會', '音樂劇', 'Live Tour', 'Concert'
        ]
        exclude_keywords = [
            '體育', '賽事', '職棒', '職籃', '聯賽', '籃球', '棒球', '說明會', 
            '講座', '論壇', '課程', '工作坊', '分享會', '展覽', '展出', '展演', 
            '體驗', '野餐', '市集', '劇本殺', '桌遊', '見面會', '粉絲見面會', '簽名會'
        ]
        
        name_lower = name.lower()
        desc_lower = description.lower() if description else ""
        
        has_concert_kw = any(kw.lower() in name_lower or kw.lower() in desc_lower for kw in concert_keywords)
        has_exclude_kw = any(kw.lower() in name_lower or kw.lower() in desc_lower for kw in exclude_keywords)
        
        return has_concert_kw and not has_exclude_kw

    def _crawl_impl(self) -> List[Event]:
        events = []
        try:
            url = f"{self.base_url}/events.json"
            self.logger.info(f"正在從 {url} 獲取 KKTIX 活動列表...")
            resp = Fetcher.get(url, headers=self.headers, impersonate="chrome120", timeout=self.timeout, follow_redirects=True)
            if resp.status != 200:
                self.logger.error(f"KKTIX crawl 失敗: status code {resp.status}")
                return []
            data = resp.json()
            entries = data.get('entry', [])
            self.logger.info(f"成功取得 {len(entries)} 個 KKTIX 活動")
            
            for entry in entries:
                title = entry.get('title', '')
                event_url = entry.get('url', '')
                summary = entry.get('summary', '')
                content = entry.get('content', '')
                
                if not self._is_concert(title, summary + " " + content):
                    continue
                
                self.logger.info(f"開始處理符合的 KKTIX 活動: {title}")
                event = self._fetch_and_parse_detail(title, event_url, entry)
                if event:
                    events.append(event)
                    
        except Exception as e:
            self.logger.error(f"KKTIX crawl 失敗: {e}")
        return events

    def _fetch_and_parse_detail(self, name: str, url: str, entry: dict) -> Optional[Event]:
        try:
            resp = Fetcher.get(url, headers=self.headers, impersonate="chrome120", timeout=self.timeout, follow_redirects=True)
            if resp.status != 200:
                self.logger.warning(f"無法取得詳情頁: {url}, HTTP: {resp.status}")
                return None
                
            json_ld_tags = resp.find_all('script', type='application/ld+json')
            
            event = Event(
                name=name,
                source_site="KKTIX",
                event_url=url,
                scraped_at=datetime.now()
            )
            
            # 預設從 entry content 解析時間和地點
            content = entry.get('content', '')
            time_match = re.search(r'時間：([^\n]+)', content)
            location_match = re.search(r'地點：([^\n]+)', content)
            
            if time_match:
                time_str = time_match.group(1).split('~')[0].strip()
                dt_match = re.search(r'(\d{4}/\d{2}/\d{2}\s+\d{2}:\d{2})', time_str)
                if dt_match:
                    event.event_time = self.parse_datetime(dt_match.group(1), "%Y/%m/%d %H:%M")
            
            if location_match:
                loc_str = location_match.group(1).strip()
                if '/' in loc_str:
                    parts = loc_str.split('/')
                    event.venue_name = parts[0].strip()
                else:
                    event.venue_name = loc_str
            
            # 從描述或標題提取藝人
            desc_text = resp.get_all_text()
            artist_match = re.search(r'(?:演出者|藝人|歌手|主演)[：:]\s*([^\n，,;]+)', desc_text)
            if artist_match:
                artist_raw = artist_match.group(1).strip()
                artists = [a.strip() for a in re.split(r'[,，、&/]|and', artist_raw) if a.strip()]
                event.artists = [a for a in artists if len(a) > 0][:5]
            
            # 尋找海報
            og_image = resp.find('meta', property='og:image')
            if og_image:
                event.image_url = og_image.attrib.get('content')
            
            event.description = entry.get('summary', '')
            
            # 開始解析 JSON-LD
            ld_parsed = False
            for tag in json_ld_tags:
                try:
                    ld = json.loads(tag.text)
                    if isinstance(ld, list):
                        ld = ld[0]
                    
                    if ld.get('@type') == 'Event':
                        if ld.get('startDate'):
                            try:
                                # KKTIX date format: "2026-05-29T19:00:00.000+08:00"
                                # datetime.fromisoformat handles it
                                date_str = ld.get('startDate')
                                # Strip milliseconds or timezone if needed, but fromisoformat in newer python is robust
                                event.event_time = datetime.fromisoformat(date_str)
                            except:
                                pass
                        
                        loc = ld.get('location', {})
                        if loc.get('name'):
                            event.venue_name = loc.get('name')
                        
                        # 解析票價
                        offers = ld.get('offers', [])
                        tickets = []
                        
                        def parse_offer(off):
                            t_name = off.get('name', '一般票')
                            t_price = off.get('price', 0)
                            return Ticket(ticket_type=t_name, price=int(float(t_price)))
                            
                        if isinstance(offers, list):
                            for offer in offers:
                                tickets.append(parse_offer(offer))
                        elif isinstance(offers, dict):
                            tickets.append(parse_offer(offers))
                        
                        if tickets:
                            event.tickets = tickets
                            
                        ld_parsed = True
                        break
                except Exception as je:
                    self.logger.warning(f"解析 JSON-LD 出錯: {je}")
            
            if not event.tickets:
                event.tickets = [Ticket(ticket_type='待定', price=0)]
                
            return event
        except Exception as e:
            self.logger.error(f"解析活動詳情出錯 {url}: {e}")
            return None


class IndievoxCrawler(BaseTicketCrawler):
    """Indievox 售票網爬蟲"""
    
    def __init__(self):
        super().__init__("Indievox", timeout=30)
        self.base_url = "https://www.indievox.com"
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
        
    def _is_concert(self, name: str, text: str) -> bool:
        concert_keywords = [
            '演唱會', '音樂會', '音樂祭', '音樂節', 'Live House', 'Livehouse', 
            '巡迴演唱', '巡迴公演', '獨奏會', '演奏會', '音樂劇', 'Live Tour', 'Concert'
        ]
        exclude_keywords = [
            '體育', '賽事', '職棒', '職籃', '聯賽', '籃球', '棒球', '說明會', 
            '講座', '論壇', '課程', '工作坊', '分享會', '展覽', '展出', '展演', 
            '體驗', '野餐', '市集', '劇本殺', '桌遊', '見面會', '粉絲見面會', '簽名會'
        ]
        
        name_lower = name.lower()
        text_lower = text.lower() if text else ""
        
        has_concert_kw = any(kw.lower() in name_lower or kw.lower() in text_lower for kw in concert_keywords)
        has_exclude_kw = any(kw.lower() in name_lower or kw.lower() in text_lower for kw in exclude_keywords)
        
        return not has_exclude_kw

    def _crawl_impl(self) -> List[Event]:
        events = []
        try:
            url = f"{self.base_url}/events"
            self.logger.info(f"正在從 {url} 獲取 Indievox 活動列表...")
            resp = Fetcher.get(url, headers=self.headers, impersonate="chrome120", timeout=self.timeout, follow_redirects=True)
            if resp.status != 200:
                self.logger.error(f"Indievox crawl 失敗: status code {resp.status}")
                return []
            
            links = [a for a in resp.find_all('a') if a.attrib.get('href') and ('/activity/detail/' in a.attrib.get('href') or '/activity/game/' in a.attrib.get('href'))]
            
            detail_urls = set()
            for a in links:
                if 'banner-url' in a.attrib.get('class', ''):
                    continue
                href = a.attrib.get('href')
                if href:
                    if not href.startswith('http'):
                        href = self.base_url + href
                    detail_urls.add(href)
            
            self.logger.info(f"找到 {len(detail_urls)} 個 Indievox 活動連結")
            
            for idx, d_url in enumerate(list(detail_urls)[:30]):
                self.logger.info(f"正在處理第 {idx+1}/{len(detail_urls)} 個 Indievox 活動: {d_url}")
                event = self._fetch_and_parse_detail(d_url)
                if event:
                    events.append(event)
                    
        except Exception as e:
            self.logger.error(f"Indievox crawl 失敗: {e}")
        return events

    def _fetch_and_parse_detail(self, url: str) -> Optional[Event]:
        try:
            resp = Fetcher.get(url, headers=self.headers, impersonate="chrome120", timeout=self.timeout, follow_redirects=True)
            if resp.status != 200:
                return None
                
            title_tag = resp.find('h2') or resp.find('h1')
            name = title_tag.get_all_text().strip() if title_tag else "未知活動"
            
            desc_text = resp.get_all_text()
            
            if not self._is_concert(name, desc_text):
                self.logger.debug(f"過濾非演唱會/表演活動: {name}")
                return None
                
            event = Event(
                name=name,
                source_site="Indievox",
                event_url=url,
                scraped_at=datetime.now()
            )
            
            # 解析日期和時間
            date_match = re.search(r'演出日期及時間：\s*([^\n]+)', desc_text)
            if date_match:
                raw_date = date_match.group(1).strip()
                clean_date = re.sub(r'[\(（][^）\)]+[\)）]', '', raw_date)
                clean_date = ' '.join(clean_date.split())
                event.event_time = self.parse_datetime(clean_date, "%Y/%m/%d %H:%M")
                
            # 解析場館
            venue_match = re.search(r'演出地點：\s*([^\n（(]+)', desc_text)
            if venue_match:
                event.venue_name = venue_match.group(1).strip()
            else:
                event.venue_name = "未知場館"
                
            # 解析藝人
            artists_match = re.search(r'演出者：\s*([^\n]+)', desc_text)
            if artists_match:
                artists_raw = artists_match.group(1).strip()
                artists = [a.strip() for a in re.split(r'[,，、&/]|and', artists_raw) if a.strip()]
                event.artists = [a for a in artists if len(a) > 0][:5]
                
            # 解析售票時間
            sale_match = re.search(r'售票時間：\s*([^\n]+)', desc_text)
            if sale_match:
                raw_sale = sale_match.group(1).strip()
                clean_sale = re.sub(r'[\(（][^）\)]+[\)）]', '', raw_sale)
                dt_match = re.search(r'(\d{4}/\d{2}/\d{2}\s+\d{2}:\d{2})', clean_sale)
                if dt_match:
                    event.ticket_sale_time = self.parse_datetime(dt_match.group(1), "%Y/%m/%d %H:%M")
                    
            # 解析票券與票價
            price_match = re.search(r'票價：\s*([^\n]+)', desc_text)
            tickets = []
            if price_match:
                prices_raw = price_match.group(1).strip()
                parts = prices_raw.split('/')
                for part in parts:
                    price_val = self.clean_price(part)
                    if price_val is not None:
                        t_type = part.replace(str(price_val), '').replace('元', '').strip()
                        t_type = re.sub(r'[\(（][^）\)]+[\)）]', '', t_type).strip()
                        if not t_type:
                            t_type = "一般票"
                        tickets.append(Ticket(ticket_type=t_type, price=price_val))
            if tickets:
                event.tickets = tickets
            else:
                event.tickets = [Ticket(ticket_type="待定", price=0)]
                
            img_tag = resp.find('img', class_='title-img') or resp.find('img')
            if img_tag:
                event.image_url = img_tag.attrib.get('src')
                if event.image_url and not event.image_url.startswith('http'):
                    event.image_url = self.base_url + event.image_url
                    
            event.description = desc_text[:1000]
            
            return event
        except Exception as e:
            self.logger.error(f"解析 Indievox 活動出錯: {e}")
            return None


class TuoYuanCrawler(BaseTicketCrawler):
    """ticket.com.tw（年代售票）爬蟲"""
    
    def __init__(self):
        super().__init__("ticket.com.tw", timeout=30)
        self.base_url = "https://ticket.com.tw"
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
        
    def _is_concert(self, name: str, text: str) -> bool:
        concert_keywords = [
            '演唱會', '音樂會', '音樂祭', '音樂節', 'Live House', 'Livehouse', 
            '巡迴演唱', '巡迴公演', '獨奏會', '演奏會', '音樂劇', 'Live Tour', 'Concert'
        ]
        exclude_keywords = [
            '體育', '賽事', '職棒', '職籃', '聯賽', '籃球', '棒球', '說明會', 
            '講座', '論壇', '課程', '工作坊', '分享會', '展覽', '展出', '展演', 
            '體驗', '野餐', '市集', '劇本殺', '桌遊', '見面會', '粉絲見面會', '簽名會'
        ]
        
        name_lower = name.lower()
        text_lower = text.lower() if text else ""
        
        has_concert_kw = any(kw.lower() in name_lower or kw.lower() in text_lower for kw in concert_keywords)
        has_exclude_kw = any(kw.lower() in name_lower or kw.lower() in text_lower for kw in exclude_keywords)
        
        return has_concert_kw and not has_exclude_kw

    def _crawl_impl(self) -> List[Event]:
        events = []
        try:
            url = f"{self.base_url}/application/UTK01/UTK0101_06.aspx?TYPE=1&CATEGORY=163"
            self.logger.info(f"正在從 {url} 獲取 Era 活動列表...")
            resp = Fetcher.get(url, headers=self.headers, impersonate="chrome120", timeout=self.timeout, follow_redirects=True)
            if resp.status != 200:
                self.logger.error(f"Era crawl 失敗: status code {resp.status}")
                return []
            
            links = [a for a in resp.find_all('a') if a.attrib.get('href') and 'PRODUCT_ID=' in a.attrib.get('href')]
            
            detail_urls = set()
            for a in links:
                href = a.attrib.get('href')
                if href:
                    if not href.startswith('http'):
                        if href.startswith('/'):
                            href = self.base_url + href
                        else:
                            href = self.base_url + "/application/UTK02/" + href.split('/')[-1]
                    detail_urls.add(href)
            
            self.logger.info(f"找到 {len(detail_urls)} 個 Era 活動連結")
            
            for idx, d_url in enumerate(list(detail_urls)[:15]):
                self.logger.info(f"正在處理第 {idx+1}/{len(detail_urls)} 個 Era 活動: {d_url}")
                event = self._fetch_and_parse_detail(d_url)
                if event:
                    events.append(event)
                    
        except Exception as e:
            self.logger.error(f"Era crawl 失敗: {e}")
        return events

    def _fetch_and_parse_detail(self, url: str) -> Optional[Event]:
        try:
            resp = Fetcher.get(url, headers=self.headers, impersonate="chrome120", timeout=self.timeout, follow_redirects=True)
            if resp.status != 200:
                return None
                
            title_tag = resp.find('h1') or resp.find('h2')
            if not title_tag:
                title_tag = resp.find('title')
            name = title_tag.get_all_text().strip() if title_tag else "未知活動"
            name = name.replace("年代售票 | ", "").replace("寬宏售票系統", "").strip()
            
            desc_text = resp.get_all_text()
            if not self._is_concert(name, desc_text):
                self.logger.debug(f"過濾非演唱會/表演活動: {name}")
                return None
                
            event = Event(
                name=name,
                source_site="ticket.com.tw",
                event_url=url,
                scraped_at=datetime.now()
            )
            
            img_tag = resp.find('meta', property='og:image')
            if img_tag:
                event.image_url = img_tag.attrib.get('content')
            else:
                for img in resp.find_all('img'):
                    src = img.attrib.get('src', '')
                    if 'media/' in src or 'ADImage/' in src:
                        event.image_url = src
                        break
                    
            if event.image_url and not event.image_url.startswith('http'):
                event.image_url = self.base_url + event.image_url
                
            event.description = desc_text[:1000]
            
            # 解析啟售時間
            sale_match = re.search(r'(?:開賣時間|售票時間|啟售時間)[：:]\s*([^\n]+)', desc_text)
            if sale_match:
                raw_sale = sale_match.group(1).strip()
                clean_sale = re.sub(r'[\(（][^）\)]+[\)）]', '', raw_sale)
                dt_match = re.search(r'(\d{4}[年/]\d{2}[月/]\d{2}[日]?\s*(?:中午)?\s*\d{2}點?(?::\d{2})?)', clean_sale)
                if dt_match:
                    sale_str = dt_match.group(1)
                    sale_str = sale_str.replace('年', '/').replace('月', '/').replace('日', '').replace('點', ':00').replace('中午', '').strip()
                    try:
                        event.ticket_sale_time = datetime.strptime(sale_str, "%Y/%m/%d %H:%M")
                    except:
                        pass
            
            # 解析 table.itable 取得時間與票價
            table = None
            for tbl in resp.find_all('table'):
                cls = tbl.attrib.get('class', '')
                if 'itable' in cls or 'table' in cls:
                    table = tbl
                    break
                    
            tickets_dict = {}
            earliest_time = None
            venue_name = None
            
            if table:
                rows = table.find_all('tr')
                for row in rows:
                    cols = row.find_all('td') or row.find_all('th')
                    if len(cols) >= 3:
                        col_texts = [c.get_all_text().strip() for c in cols]
                        if "日期" in col_texts[0] or "地點" in col_texts[1] or "票價" in col_texts[2]:
                            continue
                            
                        date_raw = col_texts[0]
                        clean_date = re.sub(r'[\(（][^）\)]+[\)）]', '', date_raw)
                        clean_date = ' '.join(clean_date.split())
                        v_raw = col_texts[1]
                        p_raw = col_texts[2]
                        
                        dt_match = re.search(r'(\d{4}/\d{2}/\d{2}\s*\d{2}:\d{2})', clean_date)
                        if dt_match:
                            try:
                                dt_val = datetime.strptime(dt_match.group(1).replace(' ', ''), "%Y/%m/%d%H:%M")
                            except:
                                try:
                                    dt_val = datetime.strptime(clean_date.strip(), "%Y/%m/%d %H:%M")
                                except:
                                    dt_val = None
                            if dt_val:
                                if earliest_time is None or dt_val < earliest_time:
                                    earliest_time = dt_val
                                    
                        if not venue_name:
                            venue_name = v_raw
                            
                        prices = re.split(r'[/,，、\s]', p_raw)
                        for p in prices:
                            price_val = self.clean_price(p)
                            if price_val:
                                tickets_dict[f"票價 {price_val}"] = price_val
                                
            event.event_time = earliest_time
            event.venue_name = venue_name or "未知場館"
            
            if tickets_dict:
                event.tickets = [Ticket(ticket_type=k, price=v) for k, v in tickets_dict.items()]
            else:
                event.tickets = [Ticket(ticket_type="待定", price=0)]
                
            return event
        except Exception as e:
            self.logger.error(f"解析 Era 活動出錯: {e}")
            return None


class IBonCrawler(BaseTicketCrawler):
    """ibon 售票網爬蟲"""
    
    def __init__(self):
        super().__init__("ibon", timeout=30)
        self.base_url = "https://ticket.ibon.com.tw"
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
        
    def _is_concert(self, name: str, description: str) -> bool:
        concert_keywords = [
            '演唱會', '音樂會', '音樂祭', '音樂節', 'Live House', 'Livehouse', 
            '巡迴演唱', '巡迴公演', '獨奏會', '演奏會', '音樂劇', 'Live Tour', 'Concert'
        ]
        exclude_keywords = [
            '體育', '賽事', '職棒', '職籃', '聯賽', '籃球', '棒球', '說明會', 
            '講座', '論壇', '課程', '工作坊', '分享會', '展覽', '展出', '展演', 
            '體驗', '野餐', '市集', '劇本殺', '桌遊', '見面會', '粉絲見面會', '簽名會'
        ]
        
        name_lower = name.lower()
        desc_lower = description.lower() if description else ""
        
        has_concert_kw = any(kw.lower() in name_lower or kw.lower() in desc_lower for kw in concert_keywords)
        has_exclude_kw = any(kw.lower() in name_lower or kw.lower() in desc_lower for kw in exclude_keywords)
        
        return has_concert_kw and not has_exclude_kw

    def _crawl_impl(self) -> List[Event]:
        events = []
        driver = None
        try:
            from seleniumbase import Driver
            import json
            import time
            
            self.logger.info("啟動 SeleniumBase UC 模式加載 ibon 娛樂...")
            driver = Driver(uc=True, headless=True)
            
            # 加載娛樂首頁
            driver.get(f"{self.base_url}/index/entertainment")
            time.sleep(8)
            
            # 關閉彈窗 Alert
            try:
                alert = driver.switch_to.alert
                alert.accept()
            except:
                pass
                
            self.logger.info("發送 POST FormData 請求 API 獲取首頁活動清單...")
            js_code = """
            const formData = new FormData();
            formData.append('pattern', 'entertainment');
            return fetch('/api/ActivityInfo/GetIndexData', {
                method: 'POST',
                body: formData
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('HTTP error ' + response.status);
                }
                return response.json();
            })
            .catch(err => {
                return { error: err.message };
            });
            """
            result_data = driver.execute_script(js_code)
            
            if "error" in result_data:
                self.logger.error(f"獲取 ibon API 失敗: {result_data['error']}")
                return []
                
            activity_list = result_data.get('Item', {}).get('List', [])
            self.logger.info(f"從 API 獲得 {len(activity_list)} 個 ibon 活動")
            
            # 過濾娛樂與音樂類別的活動
            filtered_activities = []
            for act in activity_list:
                if act.get('ActivityCategoryCode') == 'entertainment':
                    name = act.get('ActivityName', '')
                    if self._is_concert(name, name):
                        filtered_activities.append(act)
                        
            self.logger.info(f"篩選出 {len(filtered_activities)} 個表演/演唱會活動")
            
            # 逐一透過 JS fetch 詳情 API 獲取資料
            for idx, act in enumerate(filtered_activities[:15]):
                act_id = act.get('ActivityID')
                self.logger.info(f"正在獲取第 {idx+1}/{len(filtered_activities)} 個 ibon 活動詳情: ID {act_id}")
                
                js_detail = f"""
                const formData = new FormData();
                formData.append('id', '{act_id}');
                return fetch('/api/ActivityInfo/GetDetailData', {{
                    method: 'POST',
                    body: formData
                }})
                .then(r => r.json())
                .catch(err => ({{ error: err.message }}));
                """
                detail_data = driver.execute_script(js_detail)
                
                if "error" in detail_data or not detail_data.get('Item'):
                    continue
                    
                detail_item = detail_data['Item']
                name = detail_item.get('ActivityName', '').strip()
                content_html = detail_item.get('ActivityContent', '')
                
                # 解析地點與價格
                venue, tickets = self._parse_ibon_content(content_html)
                
                event = Event(
                    name=name,
                    source_site="ibon",
                    event_url=f"https://ticket.ibon.com.tw/ActivityInfo/Details/{act_id}",
                    venue_name=venue,
                    tickets=tickets,
                    scraped_at=datetime.now()
                )
                
                # 演出時間
                if detail_item.get('ActivitySDate'):
                    try:
                        event.event_time = datetime.fromisoformat(detail_item.get('ActivitySDate'))
                    except:
                        pass
                
                # 售票時間
                if detail_item.get('ActivityTicketSDate'):
                    try:
                        event.ticket_sale_time = datetime.fromisoformat(detail_item.get('ActivityTicketSDate'))
                    except:
                        pass
                        
                # 藝人名單
                kw = detail_item.get('ActivityKeyword', '')
                if kw:
                    # 去除逗號分割的關鍵字，過濾長度小於 5 且不包含常見排除字的作為藝人
                    artists = [k.strip() for k in kw.split(',') if k.strip()]
                    event.artists = [a for a in artists if a not in ['GL', '泰星', '見面會', '演唱會']][:5]
                    
                # 海報
                event.image_url = detail_item.get('ActivityImageURL')
                event.description = content_html[:1000]
                
                events.append(event)
                
        except Exception as e:
            self.logger.error(f"ibon 爬取失敗: {e}")
        finally:
            if driver:
                try:
                    driver.quit()
                except:
                    pass
        return events

    def _parse_ibon_content(self, html_content: str):
        selector = Selector(html_content)
        text = selector.get_all_text()
        
        # 1. 解析場館
        venue = None
        venue_match = re.search(r'(?:活動地點|演出地點|地點)[：｜|:\s]+([^\n<（(]+)', text)
        if venue_match:
            venue = venue_match.group(1).strip()
        else:
            common_venues = ['小巨蛋', '體育館', 'WESTAR', 'Legacy', 'Zepp', '展覽館', '文化中心', '體育場', '音樂廳']
            for v in common_venues:
                if v in text:
                    for line in text.split('\n'):
                        if v in line and '地點' in line:
                            venue = line.split('地點')[-1].replace('｜', '').replace('：', '').strip()
                            break
                    if venue:
                        break
        venue = venue or "未知場館"
        
        # 2. 解析價格
        tickets = []
        price_patterns = [
            r'([^｜|\n;:：]{1,20}(?:區|票|席|套票))[^\d]*?(?:NT\$|\$)\s*([\d,]+)',
            r'([^｜|\n;:：]{1,20}(?:區|票|席|套票))[^\d]*?([\d,]+)\s*元'
        ]
        
        seen_prices = set()
        for pat in price_patterns:
            for match in re.finditer(pat, text):
                t_type = match.group(1).strip()
                t_type = re.sub(r'[*◉●\-\s]', '', t_type)
                price_str = match.group(2).replace(',', '')
                try:
                    price = int(price_str)
                    if price > 0 and price not in seen_prices:
                        tickets.append(Ticket(ticket_type=t_type, price=price))
                        seen_prices.add(price)
                except:
                    pass
                    
        if not tickets:
            simple_prices = re.findall(r'(?:NT\$|\$)\s*([\d,]+)|([\d,]+)\s*元', text)
            for p_tup in simple_prices:
                p_str = p_tup[0] or p_tup[1]
                p_str = p_str.replace(',', '')
                try:
                    price = int(p_str)
                    if price > 0 and price not in seen_prices:
                        tickets.append(Ticket(ticket_type="一般票", price=price))
                        seen_prices.add(price)
                except:
                    pass
                    
        if not tickets:
            tickets = [Ticket(ticket_type="待定", price=0)]
            
        return venue, tickets


class KhamCrawler(BaseTicketCrawler):
    """Kham（寬宏售票）爬蟲"""
    
    def __init__(self):
        super().__init__("Kham", timeout=30)
        self.base_url = "https://kham.com.tw"
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
        
    def _is_concert(self, name: str, text: str) -> bool:
        concert_keywords = [
            '演唱會', '音樂會', '音樂祭', '音樂節', 'Live House', 'Livehouse', 
            '巡迴演唱', '巡迴公演', '獨奏會', '演奏會', '音樂劇', 'Live Tour', 'Concert'
        ]
        exclude_keywords = [
            '體育', '賽事', '職棒', '職籃', '聯賽', '籃球', '棒球', '說明會', 
            '講座', '論壇', '課程', '工作坊', '分享會', '展覽', '展出', '展演', 
            '體驗', '野餐', '市集', '劇本殺', '桌遊', '見面會', '粉絲見面會', '簽名會'
        ]
        
        name_lower = name.lower()
        text_lower = text.lower() if text else ""
        
        has_concert_kw = any(kw.lower() in name_lower or kw.lower() in text_lower for kw in concert_keywords)
        has_exclude_kw = any(kw.lower() in name_lower or kw.lower() in text_lower for kw in exclude_keywords)
        
        return has_concert_kw and not has_exclude_kw

    def _crawl_impl(self) -> List[Event]:
        events = []
        try:
            url = f"{self.base_url}/application/UTK01/UTK0101_06.aspx?TYPE=1&CATEGORY=205"
            self.logger.info(f"正在從 {url} 獲取 Kham 活動列表...")
            resp = Fetcher.get(url, headers=self.headers, impersonate="chrome120", timeout=self.timeout, follow_redirects=True)
            if resp.status != 200:
                self.logger.error(f"Kham crawl 失敗: status code {resp.status}")
                return []
            
            links = [a for a in resp.find_all('a') if a.attrib.get('href') and 'PRODUCT_ID=' in a.attrib.get('href')]
            
            detail_urls = set()
            for a in links:
                href = a.attrib.get('href')
                if href:
                    if not href.startswith('http'):
                        if href.startswith('/'):
                            href = self.base_url + href
                        else:
                            href = self.base_url + "/application/UTK02/" + href.split('/')[-1]
                    detail_urls.add(href)
            
            self.logger.info(f"找到 {len(detail_urls)} 個 Kham 活動連結")
            
            for idx, d_url in enumerate(list(detail_urls)[:15]):
                self.logger.info(f"正在處理第 {idx+1}/{len(detail_urls)} 個 Kham 活動: {d_url}")
                event = self._fetch_and_parse_detail(d_url)
                if event:
                    events.append(event)
                    
        except Exception as e:
            self.logger.error(f"Kham crawl 失敗: {e}")
        return events

    def _fetch_and_parse_detail(self, url: str) -> Optional[Event]:
        try:
            resp = Fetcher.get(url, headers=self.headers, impersonate="chrome120", timeout=self.timeout, follow_redirects=True)
            if resp.status != 200:
                return None
                
            title_tag = resp.find('h1') or resp.find('h2')
            if not title_tag:
                title_tag = resp.find('title')
            name = title_tag.get_all_text().strip() if title_tag else "未知活動"
            name = name.replace("年代售票 | ", "").replace("寬宏售票系統", "").strip()
            
            desc_text = resp.get_all_text()
            if not self._is_concert(name, desc_text):
                self.logger.debug(f"過濾非演唱會/表演活動: {name}")
                return None
                
            event = Event(
                name=name,
                source_site="Kham",
                event_url=url,
                scraped_at=datetime.now()
            )
            
            img_tag = resp.find('meta', property='og:image')
            if img_tag:
                event.image_url = img_tag.attrib.get('content')
            else:
                for img in resp.find_all('img'):
                    src = img.attrib.get('src', '')
                    if 'media/' in src or 'ADImage/' in src:
                        event.image_url = src
                        break
                    
            if event.image_url and not event.image_url.startswith('http'):
                event.image_url = self.base_url + event.image_url
                
            event.description = desc_text[:1000]
            
            # 解析啟售時間
            sale_match = re.search(r'(?:開賣時間|售票時間|啟售時間)[：:]\s*([^\n]+)', desc_text)
            if sale_match:
                raw_sale = sale_match.group(1).strip()
                clean_sale = re.sub(r'[\(（][^）\)]+[\)）]', '', raw_sale)
                dt_match = re.search(r'(\d{4}[年/]\d{2}[月/]\d{2}[日]?\s*(?:中午)?\s*\d{2}點?(?::\d{2})?)', clean_sale)
                if dt_match:
                    sale_str = dt_match.group(1)
                    sale_str = sale_str.replace('年', '/').replace('月', '/').replace('日', '').replace('點', ':00').replace('中午', '').strip()
                    try:
                        event.ticket_sale_time = datetime.strptime(sale_str, "%Y/%m/%d %H:%M")
                    except:
                        pass
            
            # 解析 table.itable 取得時間與票價
            table = None
            for tbl in resp.find_all('table'):
                cls = tbl.attrib.get('class', '')
                if 'itable' in cls or 'table' in cls:
                    table = tbl
                    break
                    
            tickets_dict = {}
            earliest_time = None
            venue_name = None
            
            if table:
                rows = table.find_all('tr')
                for row in rows:
                    cols = row.find_all('td') or row.find_all('th')
                    if len(cols) >= 3:
                        col_texts = [c.get_all_text().strip() for c in cols]
                        if "日期" in col_texts[0] or "地點" in col_texts[1] or "票價" in col_texts[2]:
                            continue
                            
                        date_raw = col_texts[0]
                        clean_date = re.sub(r'[\(（][^）\)]+[\)）]', '', date_raw)
                        clean_date = ' '.join(clean_date.split())
                        v_raw = col_texts[1]
                        p_raw = col_texts[2]
                        
                        dt_match = re.search(r'(\d{4}/\d{2}/\d{2}\s*\d{2}:\d{2})', clean_date)
                        if dt_match:
                            try:
                                dt_val = datetime.strptime(dt_match.group(1).replace(' ', ''), "%Y/%m/%d%H:%M")
                            except:
                                try:
                                    dt_val = datetime.strptime(clean_date.strip(), "%Y/%m/%d %H:%M")
                                except:
                                    dt_val = None
                            if dt_val:
                                if earliest_time is None or dt_val < earliest_time:
                                    earliest_time = dt_val
                                    
                        if not venue_name:
                            venue_name = v_raw
                            
                        prices = re.split(r'[/,，、\s]', p_raw)
                        for p in prices:
                            price_val = self.clean_price(p)
                            if price_val:
                                tickets_dict[f"票價 {price_val}"] = price_val
                                
            event.event_time = earliest_time
            event.venue_name = venue_name or "未知場館"
            
            if tickets_dict:
                event.tickets = [Ticket(ticket_type=k, price=v) for k, v in tickets_dict.items()]
            else:
                event.tickets = [Ticket(ticket_type="待定", price=0)]
                
            return event
        except Exception as e:
            self.logger.error(f"解析 Kham 活動出錯: {e}")
            return None

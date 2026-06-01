#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
售票網爬蟲 - 基礎爬蟲類別
使用 Strategy Pattern 與 OOP 設計，定義所有爬蟲必須遵循的介面
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime
import logging
from .data_models import Event, CrawlResult


class BaseTicketCrawler(ABC):
    """
    售票網爬蟲基礎類別
    
    所有具體爬蟲類別必須繼承此類並實作 crawl() 方法。
    提供統一的異常處理、日誌記錄、暫停機制。
    """
    
    def __init__(self, site_name: str, timeout: int = 30, retry_count: int = 3):
        """
        初始化爬蟲
        
        Args:
            site_name: 網站名稱（例：KKTIX, Indievox）
            timeout: 請求超時時間（秒）
            retry_count: 重試次數
        """
        self.site_name = site_name
        self.timeout = timeout
        self.retry_count = retry_count
        self.logger = self._setup_logger()
        self.session = None  # 子類可自行初始化 session（requests、httpx 等）
    
    def _setup_logger(self) -> logging.Logger:
        """設置日誌記錄"""
        logger = logging.getLogger(f"{self.__class__.__name__}.{self.site_name}")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def crawl(self) -> CrawlResult:
        """
        爬蟲入口方法
        
        Returns:
            CrawlResult: 包含爬取的活動列表或錯誤資訊
        """
        try:
            self.logger.info(f"開始爬取 {self.site_name} 售票資訊...")
            
            # 呼叫具體實作的爬蟲邏輯
            events = self._crawl_impl()
            
            # 驗證並清理數據
            valid_events = self._validate_events(events)
            
            self.logger.info(f"爬取完成：成功獲得 {len(valid_events)} 個活動")
            
            return CrawlResult(
                success=True,
                events=valid_events,
                timestamp=datetime.now()
            )
        
        except Exception as e:
            error_msg = f"爬取 {self.site_name} 時出錯: {str(e)}"
            self.logger.error(error_msg)
            return CrawlResult(
                success=False,
                error_message=error_msg,
                timestamp=datetime.now()
            )
        
        finally:
            self._cleanup()
    
    @abstractmethod
    def _crawl_impl(self) -> List[Event]:
        """
        具體爬蟲實作（由子類覆寫）
        
        Returns:
            List[Event]: 爬取的活動列表
            
        Raises:
            Exception: 如遇到無法恢復的錯誤
        """
        pass
    
    def _validate_events(self, events: List[Event]) -> List[Event]:
        """
        驗證並清理活動數據
        
        - 移除缺少必要欄位的活動
        - 移除重複的活動（根據 URL）
        - 設置爬蟲時間戳
        """
        valid_events = []
        seen_urls = set()
        
        for event in events:
            # 檢查必要欄位
            if not event.name or not event.event_url or not event.source_site:
                self.logger.warning(f"活動缺少必要欄位，已略過: {event}")
                continue
            
            # 檢查重複
            if event.event_url in seen_urls:
                self.logger.debug(f"活動已存在，已略過: {event.name}")
                continue
            
            # 設置爬蟲時間戳
            if not event.scraped_at:
                event.scraped_at = datetime.now()
            
            seen_urls.add(event.event_url)
            valid_events.append(event)
        
        return valid_events
    
    def _cleanup(self):
        """清理資源（子類可覆寫）"""
        if self.session:
            try:
                self.session.close()
            except Exception as e:
                self.logger.warning(f"關閉 session 時出錯: {e}")
    
    # ========== 工具方法 ==========
    
    @staticmethod
    def parse_datetime(date_str: str, format_str: str = "%Y-%m-%d %H:%M:%S") -> Optional[datetime]:
        """
        解析日期字符串
        
        Args:
            date_str: 日期字符串
            format_str: 日期格式
            
        Returns:
            datetime 物件，若解析失敗則返回 None
        """
        try:
            return datetime.strptime(date_str, format_str)
        except (ValueError, TypeError):
            return None
    
    @staticmethod
    def clean_price(price_str: str) -> Optional[int]:
        """
        清理票價字符串，提取數字
        
        Args:
            price_str: 票價字符串（例："$1200"）
            
        Returns:
            整數票價，若無法提取則返回 None
        """
        try:
            # 移除所有非數字字符
            price_num = ''.join(filter(str.isdigit, price_str))
            return int(price_num) if price_num else None
        except (ValueError, TypeError):
            return None
    
    @staticmethod
    def clean_text(text: str) -> str:
        """
        清理文本（移除多餘空白、換行等）
        
        Args:
            text: 原始文本
            
        Returns:
            清理後的文本
        """
        if not text:
            return ""
        return ' '.join(text.split())

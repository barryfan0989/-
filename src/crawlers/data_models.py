#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
售票網爬蟲 - 資料模型定義
統一的資料結構，用於各爬蟲和 ETL pipeline
"""

from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime


@dataclass
class Ticket:
    """票券資訊"""
    ticket_type: str  # 票種（例：全票、學生票、早鳥票）
    price: int  # 票價（單位：新台幣）
    quantity: Optional[int] = None  # 售票數量（可選）
    
    def __repr__(self):
        return f"Ticket({self.ticket_type}: {self.price}元)"


@dataclass
class Event:
    """活動資訊 (Stage 1 爬蟲的輸出)"""
    name: str  # 活動名稱
    source_site: str  # 來源網站（Indievox, KKTIX, ticket.com.tw, ibon, Kham）
    event_url: str  # 活動網址
    event_time: Optional[datetime] = None  # 演出時間
    ticket_sale_time: Optional[datetime] = None  # 購票時間
    venue_name: Optional[str] = None  # 場館名稱
    artists: List[str] = field(default_factory=list)  # 藝人名稱列表
    tickets: List[Ticket] = field(default_factory=list)  # 票券資訊列表
    description: Optional[str] = None  # 活動描述
    image_url: Optional[str] = None  # 活動海報連結
    scraped_at: Optional[datetime] = None  # 爬蟲時間戳
    
    def __repr__(self):
        artists_str = ", ".join(self.artists) if self.artists else "未知"
        tickets_str = ", ".join([f"{t.ticket_type}({t.price})" for t in self.tickets]) if self.tickets else "無票券資訊"
        return f"Event({self.name} | {artists_str} | {tickets_str})"
    
    def to_dict(self):
        """轉換為字典格式"""
        return {
            'name': self.name,
            'source_site': self.source_site,
            'event_url': self.event_url,
            'event_time': self.event_time.isoformat() if self.event_time else None,
            'ticket_sale_time': self.ticket_sale_time.isoformat() if self.ticket_sale_time else None,
            'venue_name': self.venue_name,
            'artists': self.artists,
            'tickets': [
                {
                    'ticket_type': t.ticket_type,
                    'price': t.price,
                    'quantity': t.quantity
                } for t in self.tickets
            ],
            'description': self.description,
            'image_url': self.image_url,
            'scraped_at': self.scraped_at.isoformat() if self.scraped_at else None
        }


@dataclass
class CrawlResult:
    """爬蟲執行結果"""
    success: bool  # 是否成功
    events: List[Event] = field(default_factory=list)  # 爬取的活動列表
    error_message: Optional[str] = None  # 錯誤訊息
    events_count: int = 0  # 成功爬取的活動數
    timestamp: datetime = field(default_factory=datetime.now)  # 執行時間戳
    
    def __post_init__(self):
        if not self.error_message:
            self.events_count = len(self.events)
    
    def __repr__(self):
        status = "✓ 成功" if self.success else "✗ 失敗"
        return f"CrawlResult({status} | {self.events_count} 活動)"

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
售票網爬蟲模組 - 初始化與註冊
"""

from .crawler_manager import CrawlerFactory
from .stage1_crawlers import (
    KKTIXCrawler,
    IndievoxCrawler,
    TuoYuanCrawler,
    IBonCrawler,
    KhamCrawler
)

# 註冊所有爬蟲
CrawlerFactory.register("KKTIX", KKTIXCrawler)
CrawlerFactory.register("Indievox", IndievoxCrawler)
CrawlerFactory.register("ticket.com.tw", TuoYuanCrawler)
CrawlerFactory.register("ibon", IBonCrawler)
CrawlerFactory.register("Kham", KhamCrawler)

__all__ = [
    'CrawlerFactory',
    'CrawlerManager',
    'BaseTicketCrawler',
    'KKTIXCrawler',
    'IndievoxCrawler',
    'TuoYuanCrawler',
    'IBonCrawler',
    'KhamCrawler',
    'Event',
    'Ticket',
    'CrawlResult'
]

from .crawler_manager import CrawlerManager
from .base_crawler import BaseTicketCrawler
from .data_models import Event, Ticket, CrawlResult

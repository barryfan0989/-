#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
售票網爬蟲 - 爬蟲工廠與管理器
負責統一管理所有爬蟲實例
"""

from typing import Dict, List
from abc import ABC
from .base_crawler import BaseTicketCrawler
from .data_models import CrawlResult


class CrawlerFactory:
    """爬蟲工廠類 - 用於建立和管理爬蟲實例"""
    
    _crawlers: Dict[str, type] = {}
    
    @classmethod
    def register(cls, site_name: str, crawler_class: type):
        """
        註冊爬蟲類
        
        Args:
            site_name: 網站名稱
            crawler_class: 爬蟲類（應繼承 BaseTicketCrawler）
        """
        if not issubclass(crawler_class, BaseTicketCrawler):
            raise TypeError(f"{crawler_class} 必須繼承 BaseTicketCrawler")
        cls._crawlers[site_name] = crawler_class
    
    @classmethod
    def get_crawler(cls, site_name: str) -> BaseTicketCrawler:
        """
        取得爬蟲實例
        
        Args:
            site_name: 網站名稱
            
        Returns:
            爬蟲實例
            
        Raises:
            KeyError: 如果網站未註冊
        """
        if site_name not in cls._crawlers:
            raise KeyError(f"未找到網站 '{site_name}' 的爬蟲，已註冊的網站: {list(cls._crawlers.keys())}")
        return cls._crawlers[site_name]()
    
    @classmethod
    def list_crawlers(cls) -> List[str]:
        """列出所有已註冊的爬蟲"""
        return list(cls._crawlers.keys())


class CrawlerManager:
    """爬蟲管理器 - 協調多個爬蟲的執行"""
    
    def __init__(self, sites: List[str] = None):
        """
        初始化爬蟲管理器
        
        Args:
            sites: 要爬取的網站名稱列表，若為 None 則爬取所有已註冊的網站
        """
        if sites is None:
            self.sites = CrawlerFactory.list_crawlers()
        else:
            self.sites = sites
        self.results = {}
    
    def crawl_all(self) -> Dict[str, CrawlResult]:
        """
        爬取所有指定的網站
        
        Returns:
            {網站名稱: CrawlResult} 的字典
        """
        print(f"\n{'='*70}")
        print(f"開始爬取 {len(self.sites)} 個售票網站")
        print(f"{'='*70}\n")
        
        for i, site_name in enumerate(self.sites, 1):
            print(f"[{i}/{len(self.sites)}] 爬取 {site_name}...")
            try:
                crawler = CrawlerFactory.get_crawler(site_name)
                result = crawler.crawl()
                self.results[site_name] = result
                
                if result.success:
                    print(f"  [OK] 成功：獲得 {result.events_count} 個活動\n")
                else:
                    print(f"  [ERROR] 失敗：{result.error_message}\n")
            except Exception as e:
                print(f"  [ERROR] 異常：{str(e)}\n")
                self.results[site_name] = CrawlResult(
                    success=False,
                    error_message=f"爬蟲管理器異常: {str(e)}"
                )
        
        return self.results
    
    def crawl_single(self, site_name: str) -> CrawlResult:
        """
        爬取單個網站
        
        Args:
            site_name: 網站名稱
            
        Returns:
            CrawlResult
        """
        print(f"爬取 {site_name}...")
        try:
            crawler = CrawlerFactory.get_crawler(site_name)
            result = crawler.crawl()
            self.results[site_name] = result
            return result
        except Exception as e:
            result = CrawlResult(
                success=False,
                error_message=str(e)
            )
            self.results[site_name] = result
            return result
    
    def get_all_events(self):
        """
        取得所有爬取的活動
        
        Returns:
            所有活動的列表
        """
        all_events = []
        for result in self.results.values():
            if result.success:
                all_events.extend(result.events)
        return all_events
    
    def print_summary(self):
        """打印爬取摘要"""
        print(f"\n{'='*70}")
        print("爬取摘要")
        print(f"{'='*70}\n")
        
        total_events = 0
        success_count = 0
        
        for site_name, result in self.results.items():
            status = "[OK]" if result.success else "[ERROR]"
            events_count = result.events_count if result.success else 0
            print(f"{site_name:20} {status:10} {events_count:5} 個活動")
            
            if result.success:
                total_events += events_count
                success_count += 1
        
        print(f"\n總計：{success_count}/{len(self.results)} 個網站成功爬取，共 {total_events} 個活動")
        print(f"{'='*70}\n")

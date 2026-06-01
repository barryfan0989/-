#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Stage 1 爬蟲 - 使用範例
"""

import sys
import json
from datetime import datetime

# 新增專案路徑
sys.path.insert(0, '/path/to/project')

from src.crawlers import CrawlerManager, CrawlerFactory


def example_crawl_single_site():
    """範例：爬取單個網站"""
    print("【範例 1】爬取單個網站 - KKTIX\n")
    
    # 建立爬蟲管理器
    manager = CrawlerManager(sites=["KKTIX"])
    
    # 爬取
    results = manager.crawl_all()
    
    # 取得結果
    kktix_result = results["KKTIX"]
    
    if kktix_result.success:
        print(f"成功爬取 {kktix_result.events_count} 個活動\n")
        
        # 打印前 3 個活動
        for i, event in enumerate(kktix_result.events[:3], 1):
            print(f"活動 {i}:")
            print(f"  名稱: {event.name}")
            print(f"  網址: {event.event_url}")
            print(f"  場館: {event.venue_name}")
            print(f"  時間: {event.event_time}")
            print(f"  藝人: {', '.join(event.artists) if event.artists else '未知'}")
            print(f"  票券: {len(event.tickets)} 種")
            for ticket in event.tickets:
                print(f"    - {ticket.ticket_type}: {ticket.price} 元")
            print()
    else:
        print(f"爬取失敗: {kktix_result.error_message}\n")


def example_crawl_all_sites():
    """範例：爬取所有網站"""
    print("【範例 2】爬取所有網站\n")
    
    # 建立爬蟲管理器（預設爬取所有已註冊的網站）
    manager = CrawlerManager()
    
    # 爬取所有網站
    results = manager.crawl_all()
    
    # 打印摘要
    manager.print_summary()
    
    # 取得所有活動
    all_events = manager.get_all_events()
    print(f"總共爬取 {len(all_events)} 個活動\n")


def example_get_specific_crawler():
    """範例：直接取得特定爬蟲並使用"""
    print("【範例 3】直接使用爬蟲\n")
    
    # 列出所有已註冊的爬蟲
    print("已註冊的爬蟲:")
    for site in CrawlerFactory.list_crawlers():
        print(f"  - {site}")
    
    print("\n爬取 Indievox...\n")
    
    # 取得 Indievox 爬蟲
    crawler = CrawlerFactory.get_crawler("Indievox")
    
    # 執行爬蟲
    result = crawler.crawl()
    
    if result.success:
        print(f"✓ 成功爬取 {result.events_count} 個活動")
        
        # 序列化為 JSON
        events_json = [event.to_dict() for event in result.events[:2]]
        print(f"\n前 2 個活動（JSON 格式）:")
        print(json.dumps(events_json, ensure_ascii=False, indent=2))
    else:
        print(f"✗ 爬取失敗: {result.error_message}")


def example_filter_events():
    """範例：過濾活動"""
    print("【範例 4】過濾活動\n")
    
    manager = CrawlerManager()
    results = manager.crawl_all()
    
    all_events = manager.get_all_events()
    
    # 過濾：只顯示有藝人資訊的活動
    events_with_artists = [e for e in all_events if e.artists]
    print(f"有藝人資訊的活動: {len(events_with_artists)}/{len(all_events)}\n")
    
    # 過濾：只顯示有票價資訊的活動
    events_with_tickets = [e for e in all_events if e.tickets]
    print(f"有票價資訊的活動: {len(events_with_tickets)}/{len(all_events)}\n")
    
    # 過濾：找出最便宜的票
    if events_with_tickets:
        cheapest_event = min(events_with_tickets, key=lambda e: min(t.price for t in e.tickets))
        cheapest_ticket = min(cheapest_event.tickets, key=lambda t: t.price)
        print(f"最便宜的票:")
        print(f"  活動: {cheapest_event.name}")
        print(f"  票種: {cheapest_ticket.ticket_type}")
        print(f"  票價: {cheapest_ticket.price} 元")


if __name__ == "__main__":
    print("=" * 70)
    print("Stage 1 爬蟲系統 - 使用範例")
    print("=" * 70)
    print()
    
    # 執行範例
    try:
        # example_crawl_single_site()
        # example_crawl_all_sites()
        # example_get_specific_crawler()
        # example_filter_events()
        
        print("請取消註解相應的函數呼叫以執行範例")
        print("\n可用的範例:")
        print("  1. example_crawl_single_site() - 爬取單個網站")
        print("  2. example_crawl_all_sites() - 爬取所有網站")
        print("  3. example_get_specific_crawler() - 直接使用爬蟲")
        print("  4. example_filter_events() - 過濾活動")
    
    except Exception as e:
        print(f"錯誤: {e}")
        import traceback
        traceback.print_exc()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Stage 1 爬蟲測試 - 爬取並輸出 JSON
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# 加入專案路徑
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.crawlers import CrawlerManager, CrawlerFactory


def normalize_datetime(dt):
    """將 datetime 物件轉換為 ISO 格式字符串"""
    if dt is None:
        return None
    if isinstance(dt, datetime):
        return dt.isoformat()
    return str(dt)


def event_to_dict(event):
    """將 Event 物件轉換為字典（正規化日期）"""
    event_dict = event.to_dict()
    
    # 轉換日期欄位為 ISO 格式
    event_dict['event_time'] = normalize_datetime(event_dict.get('event_time'))
    event_dict['ticket_sale_time'] = normalize_datetime(event_dict.get('ticket_sale_time'))
    event_dict['scraped_at'] = normalize_datetime(event_dict.get('scraped_at'))
    
    return event_dict


def test_single_crawler(site_name):
    """測試單個爬蟲"""
    print(f"\n{'='*70}")
    print(f"測試爬蟲: {site_name}")
    print(f"{'='*70}\n")
    
    try:
        crawler = CrawlerFactory.get_crawler(site_name)
        print(f"✓ 已獲得爬蟲實例: {crawler.__class__.__name__}")
        print(f"  網站: {crawler.site_name}")
        print(f"  超時: {crawler.timeout}s")
        print(f"  重試: {crawler.retry_count} 次\n")
        
        print(f"正在爬取 {site_name}...\n")
        result = crawler.crawl()
        
        print(f"爬取結果:")
        print(f"  成功: {result.success}")
        print(f"  活動數: {result.events_count}")
        print(f"  執行時間: {result.timestamp.isoformat()}")
        
        if result.error_message:
            print(f"  錯誤訊息: {result.error_message}")
        
        # 輸出前 3 個活動的詳細資訊
        if result.success and result.events:
            print(f"\n前 {min(3, len(result.events))} 個活動:\n")
            
            for i, event in enumerate(result.events[:3], 1):
                print(f"活動 {i}:")
                print(f"  名稱: {event.name}")
                print(f"  來源: {event.source_site}")
                print(f"  網址: {event.event_url}")
                print(f"  場館: {event.venue_name}")
                print(f"  演出時間: {event.event_time}")
                print(f"  購票時間: {event.ticket_sale_time}")
                print(f"  藝人數: {len(event.artists)}")
                if event.artists:
                    print(f"    {', '.join(event.artists[:3])}" + 
                          ("..." if len(event.artists) > 3 else ""))
                print(f"  票種數: {len(event.tickets)}")
                if event.tickets:
                    for ticket in event.tickets[:2]:
                        print(f"    - {ticket.ticket_type}: {ticket.price} 元")
                    if len(event.tickets) > 2:
                        print(f"    ... 還有 {len(event.tickets) - 2} 種票")
                print()
        
        return result
    
    except Exception as e:
        print(f"✗ 爬蟲錯誤: {e}")
        import traceback
        traceback.print_exc()
        return None


def save_results_to_json(results, output_file="crawler_results.json"):
    """將結果儲存為 JSON"""
    output_data = {
        "generated_at": datetime.now().isoformat(),
        "total_events": 0,
        "crawlers": {}
    }
    
    for site_name, result in results.items():
        if result:
            events_data = [
                event_to_dict(event) 
                for event in result.events
            ]
            
            output_data["crawlers"][site_name] = {
                "success": result.success,
                "events_count": result.events_count,
                "error_message": result.error_message,
                "timestamp": result.timestamp.isoformat(),
                "events": events_data
            }
            
            output_data["total_events"] += len(events_data)
    
    # 寫入 JSON
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✓ 結果已儲存到: {output_file}")
    return output_data


def test_all_crawlers():
    """測試所有爬蟲"""
    print("開始測試所有爬蟲...\n")
    
    sites = CrawlerFactory.list_crawlers()
    print(f"找到 {len(sites)} 個已註冊的爬蟲:")
    for site in sites:
        print(f"  - {site}")
    
    results = {}
    
    # 測試每個爬蟲
    for site_name in sites:
        result = test_single_crawler(site_name)
        results[site_name] = result
    
    # 儲存結果
    output_data = save_results_to_json(results, "crawler_results.json")
    
    # 打印摘要
    print(f"\n{'='*70}")
    print("測試摘要")
    print(f"{'='*70}\n")
    
    print(f"總共爬取的活動: {output_data['total_events']}")
    print(f"成功的爬蟲:")
    
    for site_name, crawler_data in output_data['crawlers'].items():
        status = "✓" if crawler_data['success'] else "✗"
        print(f"  {status} {site_name}: {crawler_data['events_count']} 個活動")
    
    return output_data


def test_using_manager():
    """使用 CrawlerManager 測試"""
    print(f"\n{'='*70}")
    print("使用 CrawlerManager 測試")
    print(f"{'='*70}\n")
    
    # 測試所有網站
    sites_to_crawl = CrawlerFactory.list_crawlers()
    
    manager = CrawlerManager(sites=sites_to_crawl)
    print(f"爬蟲管理器已初始化，將爬取: {', '.join(sites_to_crawl)}\n")
    
    results = manager.crawl_all()
    
    # 打印摘要
    manager.print_summary()
    
    # 準備 JSON 輸出
    output_data = {
        "generated_at": datetime.now().isoformat(),
        "total_events": 0,
        "crawlers": {}
    }
    
    for site_name, result in results.items():
        events_data = [
            event_to_dict(event) 
            for event in result.events
        ]
        
        output_data["crawlers"][site_name] = {
            "success": result.success,
            "events_count": result.events_count,
            "error_message": result.error_message,
            "timestamp": result.timestamp.isoformat(),
            "events": events_data
        }
        
        output_data["total_events"] += len(events_data)
    
    # 儲存 JSON
    output_file = "crawler_manager_results.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n[OK] 結果已儲存到: {output_file}")
    print(f"[OK] 總共爬取 {output_data['total_events']} 個活動\n")
    
    return output_data


if __name__ == "__main__":
    print("="*70)
    print("Stage 1 爬蟲系統 - 測試與 JSON 輸出")
    print("="*70)
    
    try:
        # 測試方式 1：使用 CrawlerManager
        output_data = test_using_manager()
        
        # 列印部分 JSON 輸出（前 3 個活動）
        print("\n" + "="*70)
        print("JSON 輸出示例（前 3 個活動）")
        print("="*70 + "\n")
        
        sample_data = {
            "generated_at": output_data["generated_at"],
            "total_events": output_data["total_events"],
            "sample_crawlers": {}
        }
        
        for site_name, crawler_data in output_data['crawlers'].items():
            sample_data["sample_crawlers"][site_name] = {
                "success": crawler_data['success'],
                "events_count": crawler_data['events_count'],
                "sample_events": crawler_data['events'][:3]
            }
        
        print(json.dumps(sample_data, ensure_ascii=False, indent=2))
        
    except Exception as e:
        print(f"\n✗ 測試失敗: {e}")
        import traceback
        traceback.print_exc()

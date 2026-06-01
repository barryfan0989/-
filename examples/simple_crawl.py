#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
簡單的爬蟲測試 - 輸出正規化 JSON
"""

import sys
import json
from pathlib import Path
from datetime import datetime

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.crawlers import CrawlerManager


def main():
    print("="*70)
    print("售票網爬蟲 - 爬取並輸出 JSON")
    print("="*70)
    print()
    
    # 建立管理器
    manager = CrawlerManager(sites=["KKTIX", "Indievox"])
    
    print("開始爬取...")
    print("-"*70 + "\n")
    
    # 執行爬蟲
    results = manager.crawl_all()
    
    # 準備 JSON 輸出
    output_data = {
        "generated_at": datetime.now().isoformat(),
        "total_events": 0,
        "crawlers": {}
    }
    
    for site_name, result in results.items():
        # 轉換事件為字典
        events_data = []
        for event in result.events:
            event_dict = event.to_dict()
            # 正規化日期
            for date_field in ['event_time', 'ticket_sale_time', 'scraped_at']:
                if event_dict.get(date_field):
                    dt = event_dict[date_field]
                    if isinstance(dt, datetime):
                        event_dict[date_field] = dt.isoformat()
            events_data.append(event_dict)
        
        output_data["crawlers"][site_name] = {
            "success": result.success,
            "events_count": result.events_count,
            "error_message": result.error_message,
            "timestamp": result.timestamp.isoformat(),
            "events": events_data
        }
        
        output_data["total_events"] += len(events_data)
    
    # 打印摘要
    print("-"*70)
    print("爬取結果摘要")
    print("-"*70)
    manager.print_summary()
    
    # 打印 JSON
    print("\n" + "="*70)
    print("JSON 輸出格式")
    print("="*70 + "\n")
    print(json.dumps(output_data, ensure_ascii=False, indent=2))
    
    # 保存到檔案
    output_file = "crawler_results.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n[OK] 結果已保存到: {output_file}")
    print(f"[OK] 總共爬取: {output_data['total_events']} 個活動\n")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n[ERROR] 執行失敗: {e}")
        import traceback
        traceback.print_exc()

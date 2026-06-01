#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試 Scrapling Fetcher API
"""

from scrapling import Fetcher

fetcher = Fetcher()
print('測試 Fetcher.get() 的返回值...\n')

try:
    response = fetcher.get('https://www.indievox.com', timeout=10)
    print(f'返回類型: {type(response)}')
    print(f'返回值屬性: {[m for m in dir(response) if not m.startswith("_")]}')
    
    # 嘗試獲取不同的屬性
    if hasattr(response, 'text'):
        print(f'\n有 text 屬性，長度: {len(response.text)}')
        print(f'前 300 字符: {response.text[:300]}')
    
    if hasattr(response, 'content'):
        print(f'\n有 content 屬性，類型: {type(response.content)}')
        if isinstance(response.content, (str, bytes)):
            content_str = response.content if isinstance(response.content, str) else response.content.decode('utf-8', errors='ignore')
            print(f'長度: {len(content_str)}')
            print(f'前 300 字符: {content_str[:300]}')
    
    if hasattr(response, '__str__'):
        print(f'\n 直接 str(): {str(response)[:300]}')
    
    print(f'\n完整屬性輸出: {response}')

except Exception as e:
    print(f'錯誤: {e}')
    import traceback
    traceback.print_exc()

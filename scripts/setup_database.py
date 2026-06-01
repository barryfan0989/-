#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
售票網站資料整合系統 - MySQL 建表執行腳本
"""

import sys
import os
import ssl
import mysql.connector
from mysql.connector import errorcode

# 資料庫連線設定
DB_CONFIG = {
    'host': 'ticketdb-ticket63.f.aivencloud.com',
    'port': 13599,
    'user': 'avnadmin',
    'password': 'AVNS_QqNVFqacdQinAgGmXY9',
    'database': 'defaultdb',
    'ssl_disabled': False,
    'autocommit': False,
    'use_pure': True,
    'connection_timeout': 10
}

def read_sql_file(file_path):
    """讀取 SQL 腳本檔案"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"❌ 錯誤：找不到 SQL 檔案 {file_path}")
        sys.exit(1)

def execute_sql(connection, sql_script):
    """執行 SQL 腳本（分割 SQL 敘述句）"""
    cursor = connection.cursor()
    
    # 更精確的 SQL 分割方法：根據 '-- ' 分隔符和 ';' 結尾
    statements = []
    current_statement = []
    in_string = False
    string_char = None
    
    for line in sql_script.split('\n'):
        stripped = line.strip()
        
        # 跳過註解行
        if stripped.startswith('--'):
            continue
        
        if not stripped:
            continue
            
        current_statement.append(line)
        
        # 檢查是否有結尾的 `;`
        if ';' in line:
            stmt = '\n'.join(current_statement).strip()
            if stmt and not stmt.startswith('--'):
                statements.append(stmt)
            current_statement = []
    
    executed = 0
    errors = []
    
    for i, statement in enumerate(statements, 1):
        if not statement or statement.startswith('--'):
            continue
        
        try:
            cursor.execute(statement)
            executed += 1
            print(f"✓ 執行敘述句 {i} 成功")
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                print(f"⚠ 敘述句 {i}：表已存在（略過）")
            elif err.errno == errorcode.ER_DUP_ENTRY:
                print(f"⚠ 敘述句 {i}：重複項（略過）")
            else:
                error_msg = f"敘述句 {i} 失敗：{err.msg}"
                print(f"❌ {error_msg}")
                errors.append(error_msg)
        except Exception as err:
            error_msg = f"敘述句 {i} 異常：{str(err)}"
            print(f"❌ {error_msg}")
            errors.append(error_msg)
    
    cursor.close()
    
    return executed, errors

def main():
    """主函數"""
    print("=" * 70)
    print("📊 售票網站資料整合系統 - MySQL 建表執行腳本")
    print("=" * 70)
    
    # 取得 SQL 腳本路徑
    script_dir = os.path.dirname(os.path.abspath(__file__))
    sql_file = os.path.join(script_dir, 'create_tables.sql')
    
    print(f"\n📖 讀取 SQL 腳本：{sql_file}")
    sql_script = read_sql_file(sql_file)
    print(f"✓ 已讀取 SQL 腳本")
    
    # 連接資料庫
    print(f"\n🔗 連接資料庫...")
    print(f"   主機：{DB_CONFIG['host']}:{DB_CONFIG['port']}")
    print(f"   使用者：{DB_CONFIG['user']}")
    print(f"   資料庫：{DB_CONFIG['database']}")
    
    try:
        # 建立 SSL 上下文（Aiven 使用自簽憑證）
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        connection = mysql.connector.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            database=DB_CONFIG['database'],
            ssl_verify_cert=False,
            ssl_verify_identity=False,
            use_pure=True,
            connection_timeout=10,
            autocommit=False
        )
        print("✓ 資料庫連接成功")
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("❌ 錯誤：使用者名稱或密碼不正確")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("❌ 錯誤：資料庫不存在")
        else:
            print(f"❌ 連接失敗：{err}")
        sys.exit(1)
    except Exception as err:
        print(f"❌ 連接異常：{err}")
        sys.exit(1)
    
    # 執行 SQL 腳本
    print(f"\n⚙️  執行 SQL 腳本...")
    try:
        executed, errors = execute_sql(connection, sql_script)
        
        if errors:
            print(f"\n⚠️  警告：執行過程中遇到 {len(errors)} 個錯誤（部分可忽略）")
        
        # 提交變更
        connection.commit()
        print(f"\n✓ 變更已提交")
        
    except Exception as err:
        connection.rollback()
        print(f"❌ 執行異常：{err}")
        sys.exit(1)
    finally:
        connection.close()
        print("✓ 資料庫連接已關閉")
    
    print("\n" + "=" * 70)
    print("✅ 建表完成")
    print("=" * 70)

if __name__ == '__main__':
    main()

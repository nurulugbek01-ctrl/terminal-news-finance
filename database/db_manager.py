import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "stocks.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stocks (
            ticker TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            halal_status TEXT NOT NULL,
            notes TEXT
        )
    ''')
    
    # Расширенная база данных тикеров
    initial_data = [
        ("AAPL", "Apple Inc.", "Verified", "Халяль (Долг < 30%, процентный доход минимален)"),
        ("TSLA", "Tesla Inc.", "Verified", "Халяль (Производственный сектор)"),
        ("NVDA", "NVIDIA Corporation", "Verified", "Халяль (Лидер в сфере ИИ и чипов)"),
        ("MSFT", "Microsoft Corp.", "Verified", "Халяль (ПО и облачные сервисы)"),
        ("GOOGL", "Alphabet Inc.", "Verified", "Халяль (IT и поисковые сервисы)"),
        ("HIMS", "Hims & Hers Health, Inc.", "Watch", "Телемедицина. Требуется проверка финансового отчета"),
        ("AMD", "Advanced Micro Devices", "Verified", "Халяль (Полупроводники)"),
        ("META", "Meta Platforms", "Verified", "Халяль (Социальные медиа)"),
        ("INTC", "Intel Corp.", "Watch", "Высокий уровень долга, требуется регулярный мониторинг")
    ]
    
    for item in initial_data:
        cursor.execute('''
            INSERT OR REPLACE INTO stocks (ticker, name, halal_status, notes)
            VALUES (?, ?, ?, ?)
        ''', item)
        
    conn.commit()
    conn.close()

def get_all_stocks():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT ticker, name, halal_status, notes FROM stocks")
    rows = cursor.fetchall()
    conn.close()
    return rows
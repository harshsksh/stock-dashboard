import aiosqlite
import os
from datetime import datetime, timedelta

class Database:
    def __init__(self, db_path="data/stocks.db"):
        self.db_path = db_path
        # Ensure data directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    async def init_db(self):
        """Initialize database with required tables"""
        async with aiosqlite.connect(self.db_path) as db:
            # Companies table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS companies (
                    symbol TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    sector TEXT
                )
            """)
            
            # Stock data table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS stock_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    date DATE NOT NULL,
                    open REAL,
                    high REAL,
                    low REAL,
                    close REAL,
                    volume INTEGER,
                    daily_return REAL,
                    ma_7 REAL,
                    UNIQUE(symbol, date)
                )
            """)
            
            # Create indexes for faster queries
            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_symbol_date 
                ON stock_data(symbol, date)
            """)
            
            await db.commit()
            print("✅ Database initialized successfully")
    
    async def get_companies(self):
        """Get all companies"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM companies ORDER BY name") as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
    
    async def get_stock_data(self, symbol: str, days: int = 30):
        """Get stock data for last N days"""
        date_from = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            query = """
                SELECT * FROM stock_data 
                WHERE symbol = ? AND date >= ?
                ORDER BY date DESC
            """
            async with db.execute(query, (symbol, date_from)) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
    
    async def get_all_stock_data(self, symbol: str):
        """Get all available stock data for a symbol"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            query = """
                SELECT * FROM stock_data 
                WHERE symbol = ?
                ORDER BY date DESC
            """
            async with db.execute(query, (symbol,)) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
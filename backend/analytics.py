import aiosqlite
from datetime import datetime, timedelta
import statistics

class StockAnalytics:
    def __init__(self, db):
        self.db = db
    
    async def get_52_week_summary(self, symbol: str):
        """Get 52-week high, low, and average statistics"""
        date_from = (datetime.now() - timedelta(weeks=52)).strftime('%Y-%m-%d')
        
        async with aiosqlite.connect(self.db.db_path) as db:
            db.row_factory = aiosqlite.Row
            
            query = """
                SELECT 
                    MAX(high) as week_52_high,
                    MIN(low) as week_52_low,
                    AVG(close) as avg_close,
                    AVG(volume) as avg_volume,
                    COUNT(*) as trading_days
                FROM stock_data 
                WHERE symbol = ? AND date >= ?
            """
            async with db.execute(query, (symbol, date_from)) as cursor:
                row = await cursor.fetchone()
                
                if not row or row['trading_days'] == 0:
                    return None
                
                query_current = """
                    SELECT close, date FROM stock_data 
                    WHERE symbol = ? 
                    ORDER BY date DESC LIMIT 1
                """
                async with db.execute(query_current, (symbol,)) as cursor2:
                    current_row = await cursor2.fetchone()
                    current_price = current_row['close'] if current_row else None
                    current_date = current_row['date'] if current_row else None
                
                return {
                    "symbol": symbol,
                    "week_52_high": round(row['week_52_high'], 2),
                    "week_52_low": round(row['week_52_low'], 2),
                    "avg_close": round(row['avg_close'], 2),
                    "current_price": round(current_price, 2) if current_price else None,
                    "current_date": current_date,
                    "avg_volume": int(row['avg_volume']),
                    "trading_days": row['trading_days']
                }
    
    async def compare_stocks(self, symbol1: str, symbol2: str):
        """Compare performance of two stocks"""
        summary1 = await self.get_52_week_summary(symbol1)
        summary2 = await self.get_52_week_summary(symbol2)
        
        if not summary1 or not summary2:
            return None
        
        # Check for None values to avoid division errors
        if (summary1.get('current_price') is None or summary1.get('avg_close') is None or
            summary2.get('current_price') is None or summary2.get('avg_close') is None or
            summary1['avg_close'] == 0 or summary2['avg_close'] == 0):
            return None
        
        perf1 = ((summary1['current_price'] - summary1['avg_close']) / summary1['avg_close']) * 100
        perf2 = ((summary2['current_price'] - summary2['avg_close']) / summary2['avg_close']) * 100
        
        return {
            "comparison": {
                symbol1: summary1,
                symbol2: summary2
            },
            "insights": {
                "better_performer": symbol1 if perf1 > perf2 else symbol2,
                "symbol1_performance": round(perf1, 2),
                "symbol2_performance": round(perf2, 2),
                "performance_difference": round(abs(perf1 - perf2), 2)
            }
        }
    
    async def get_top_gainers(self, limit: int = 5):
        """Get top gaining stocks"""
        async with aiosqlite.connect(self.db.db_path) as db:
            db.row_factory = aiosqlite.Row
            
            query = """
                SELECT 
                    symbol,
                    AVG(daily_return) as avg_return,
                    COUNT(*) as days
                FROM stock_data 
                WHERE date >= date('now', '-30 days')
                AND daily_return IS NOT NULL
                GROUP BY symbol
                HAVING days >= 20
                ORDER BY avg_return DESC
                LIMIT ?
            """
            async with db.execute(query, (limit,)) as cursor:
                rows = await cursor.fetchall()
                return [{
                    "symbol": row['symbol'],
                    "avg_return": round(row['avg_return'], 2),
                    "days": row['days']
                } for row in rows]
    
    async def get_top_losers(self, limit: int = 5):
        """Get top losing stocks"""
        async with aiosqlite.connect(self.db.db_path) as db:
            db.row_factory = aiosqlite.Row
            
            query = """
                SELECT 
                    symbol,
                    AVG(daily_return) as avg_return,
                    COUNT(*) as days
                FROM stock_data 
                WHERE date >= date('now', '-30 days')
                AND daily_return IS NOT NULL
                GROUP BY symbol
                HAVING days >= 20
                ORDER BY avg_return ASC
                LIMIT ?
            """
            async with db.execute(query, (limit,)) as cursor:
                rows = await cursor.fetchall()
                return [{
                    "symbol": row['symbol'],
                    "avg_return": round(row['avg_return'], 2),
                    "days": row['days']
                } for row in rows]
    
    async def get_volatility(self, symbol: str):
        """Calculate volatility score"""
        async with aiosqlite.connect(self.db.db_path) as db:
            db.row_factory = aiosqlite.Row
            
            query = """
                SELECT daily_return 
                FROM stock_data 
                WHERE symbol = ? 
                AND date >= date('now', '-90 days')
                AND daily_return IS NOT NULL
                ORDER BY date DESC
            """
            async with db.execute(query, (symbol,)) as cursor:
                rows = await cursor.fetchall()
                
                if not rows or len(rows) < 10:
                    return None
                
                returns = [row['daily_return'] for row in rows]
                volatility = statistics.stdev(returns)
                mean_return = statistics.mean(returns)
                
                if volatility < 1.5:
                    classification = "Low"
                elif volatility < 3.0:
                    classification = "Moderate"
                else:
                    classification = "High"
                
                return {
                    "symbol": symbol,
                    "volatility_score": round(volatility, 2),
                    "classification": classification,
                    "mean_return": round(mean_return, 2),
                    "data_points": len(returns)
                }
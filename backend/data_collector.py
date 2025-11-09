import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import aiosqlite

class DataCollector:
    def __init__(self, db):
        self.db = db
        # Popular Indian stocks (NSE)
        self.symbols = {
            'RELIANCE.NS': ('RELIANCE', 'Reliance Industries', 'Energy'),
            'TCS.NS': ('TCS', 'Tata Consultancy Services', 'IT'),
            'INFY.NS': ('INFY', 'Infosys', 'IT'),
            'HDFCBANK.NS': ('HDFCBANK', 'HDFC Bank', 'Banking'),
            'ICICIBANK.NS': ('ICICIBANK', 'ICICI Bank', 'Banking'),
            'HINDUNILVR.NS': ('HINDUNILVR', 'Hindustan Unilever', 'FMCG'),
            'ITC.NS': ('ITC', 'ITC Limited', 'FMCG'),
            'SBIN.NS': ('SBIN', 'State Bank of India', 'Banking'),
            'BHARTIARTL.NS': ('BHARTIARTL', 'Bharti Airtel', 'Telecom'),
            'WIPRO.NS': ('WIPRO', 'Wipro', 'IT')
        }
    
    async def collect_initial_data(self):
        """Collect initial stock data for all symbols"""
        async with aiosqlite.connect(self.db.db_path) as db:
            # Insert companies
            for yf_symbol, (symbol, name, sector) in self.symbols.items():
                await db.execute(
                    "INSERT OR IGNORE INTO companies (symbol, name, sector) VALUES (?, ?, ?)",
                    (symbol, name, sector)
                )
            
            await db.commit()
            
            # Fetch stock data
            end_date = datetime.now()
            start_date = end_date - timedelta(days=365)
            
            for yf_symbol, (symbol, name, sector) in self.symbols.items():
                try:
                    print(f"Fetching data for {name}...")
                    stock = yf.Ticker(yf_symbol)
                    df = stock.history(start=start_date, end=end_date)
                    
                    if not df.empty:
                        # Calculate metrics
                        df['daily_return'] = ((df['Close'] - df['Open']) / df['Open']) * 100
                        df['ma_7'] = df['Close'].rolling(window=7).mean()
                        
                        # Insert data
                        for date, row in df.iterrows():
                            await db.execute("""
                                INSERT OR REPLACE INTO stock_data 
                                (symbol, date, open, high, low, close, volume, daily_return, ma_7)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """, (
                                symbol,
                                date.strftime('%Y-%m-%d'),
                                round(row['Open'], 2),
                                round(row['High'], 2),
                                round(row['Low'], 2),
                                round(row['Close'], 2),
                                int(row['Volume']),
                                round(row['daily_return'], 2) if pd.notna(row['daily_return']) else None,
                                round(row['ma_7'], 2) if pd.notna(row['ma_7']) else None
                            ))
                        
                        print(f"Collected {len(df)} records for {name}")
                        
                except Exception as e:
                    print(f"Error fetching {name}: {e}")
            
            await db.commit()
            print("Data collection completed!")
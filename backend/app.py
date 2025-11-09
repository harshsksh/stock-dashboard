from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from typing import List, Optional
import uvicorn
from database import Database
from analytics import StockAnalytics
from data_collector import DataCollector

# Initialize components
db = Database()
analytics = StockAnalytics(db)
collector = DataCollector(db)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database and collect data on startup"""
    print("🚀 Starting Stock Intelligence API...")
    await db.init_db()
    print("📊 Collecting stock data...")
    await collector.collect_initial_data()
    print("✅ Ready to serve requests!")
    yield
    # Cleanup code can go here if needed

app = FastAPI(
    title="Stock Intelligence API",
    description="Real-time stock data analytics platform",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Stock Intelligence API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/companies")
async def get_companies():
    """Get list of all available companies"""
    companies = await db.get_companies()
    return {
        "companies": companies,
        "count": len(companies)
    }

@app.get("/data/{symbol}")
async def get_stock_data(symbol: str, days: int = 30):
    """Get last N days of stock data for a symbol"""
    data = await db.get_stock_data(symbol, days)
    if not data:
        raise HTTPException(status_code=404, detail=f"Symbol {symbol} not found")
    return {
        "symbol": symbol,
        "data": data,
        "count": len(data)
    }

@app.get("/summary/{symbol}")
async def get_summary(symbol: str):
    """Get 52-week summary statistics for a symbol"""
    summary = await analytics.get_52_week_summary(symbol)
    if not summary:
        raise HTTPException(status_code=404, detail=f"Symbol {symbol} not found")
    return summary

@app.get("/compare")
async def compare_stocks(symbol1: str, symbol2: str):
    """Compare performance of two stocks"""
    comparison = await analytics.compare_stocks(symbol1, symbol2)
    if not comparison:
        raise HTTPException(
            status_code=404,
            detail="One or both symbols not found"
        )
    return comparison

@app.get("/insights/gainers")
async def get_top_gainers(limit: int = 5):
    """Get top gaining stocks"""
    gainers = await analytics.get_top_gainers(limit)
    return {"gainers": gainers, "count": len(gainers)}

@app.get("/insights/losers")
async def get_top_losers(limit: int = 5):
    """Get top losing stocks"""
    losers = await analytics.get_top_losers(limit)
    return {"losers": losers, "count": len(losers)}

@app.get("/insights/volatility/{symbol}")
async def get_volatility(symbol: str):
    """Get volatility score for a symbol"""
    volatility = await analytics.get_volatility(symbol)
    if not volatility:
        raise HTTPException(status_code=404, detail=f"Symbol {symbol} not found")
    return volatility

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
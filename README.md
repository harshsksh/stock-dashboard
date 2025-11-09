# Stock Intelligence Dashboard

A comprehensive stock market analytics platform built with FastAPI and modern web technologies.

## Features
- Real-time stock data from NSE
- REST API with Swagger documentation
- Interactive visualization dashboard
- Advanced analytics (52-week summary, comparisons)
- Top gainers/losers insights

## Setup Instructions

### 1. Clone Repository
git clone <your-repo-url>
cd stock-intelligence-dashboard

### 2. Install Dependencies
pip install -r backend/requirements.txt

### 3. Run Backend
cd backend
python app.py

### 4. Open Frontend
Open frontend/index.html in your browser

### 5. API Documentation
Visit: http://localhost:8000/docs

## API Endpoints
- GET /companies - List all companies
- GET /data/{symbol} - Get stock data
- GET /summary/{symbol} - 52-week summary
- GET /compare - Compare two stocks
- GET /insights/gainers - Top gainers
- GET /insights/losers - Top losers

## Technologies
- Backend: FastAPI, Python 3.9+
- Database: SQLite (async)
- Frontend: HTML5, CSS3, JavaScript
- Visualization: Chart.js
- Data: yfinance API
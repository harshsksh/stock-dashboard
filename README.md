# Stock Intelligence Dashboard

A comprehensive stock market analytics platform built with FastAPI and modern web technologies.

## Features
- Real-time stock data from NSE
- REST API with Swagger documentation
- Interactive visualization dashboard
- Advanced analytics (52-week summary, comparisons)
- Top gainers/losers insights

## Prerequisites
- Python 3.9 or higher
- pip (Python package manager)
- Modern web browser (Chrome, Firefox, Edge, etc.)

## Setup Instructions

### Step 1: Navigate to Project Directory
```bash
cd stock-dashboard
```

### Step 2: Install Python Dependencies
Install all required Python packages:
```bash
pip install -r backend/requirements.txt
```

**Note for Windows users:** If you encounter permission issues, use:
```bash
pip install --user -r backend/requirements.txt
```

### Step 3: Run the Backend Server
Navigate to the backend directory and start the FastAPI server:
```bash
cd backend
python app.py
```

**Alternative method (using uvicorn directly):**
```bash
cd backend
python -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

The backend will:
- Initialize the SQLite database
- Collect stock data from yfinance API (this may take a few minutes)
- Start the API server on `http://localhost:8000`

You should see output like:
```
🚀 Starting Stock Intelligence API...
✅ Database initialized successfully
📊 Collecting stock data...
✅ Ready to serve requests!
```

### Step 4: Open the Frontend
Once the backend is running, open the frontend in your browser:

**Option 1: Direct file open**
- Navigate to the `frontend` folder
- Double-click `index.html` to open in your default browser

**Option 2: Using a local server (recommended)**
For better CORS handling, use a simple HTTP server:

**Python 3:**
```bash
cd frontend
python -m http.server 8080
```
Then open: `http://localhost:8080`

**Node.js (if installed):**
```bash
cd frontend
npx http-server -p 8080
```

### Step 5: Access the Application
- **Frontend Dashboard:** `http://localhost:8080` (or file:// path if opened directly)
- **API Documentation (Swagger UI):** `http://localhost:8000/docs`
- **Alternative API Docs (ReDoc):** `http://localhost:8000/redoc`
- **API Root:** `http://localhost:8000`

## Running with Docker (Optional)

### Build the Docker Image
```bash
docker build -t stock-dashboard .
```

### Run the Container
```bash
docker run -p 8000:8000 stock-dashboard
```

The API will be available at `http://localhost:8000`

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
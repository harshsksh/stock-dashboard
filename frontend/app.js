const API_URL = 'http://localhost:8000';
let chart = null;
let currentSymbol = null;
let allCompanies = [];

document.addEventListener('DOMContentLoaded', () => {
    // Test backend connection first
    testBackendConnection().then(() => {
        loadCompanies();
        loadInsights();
    });
    
    // Add search functionality
    const searchInput = document.getElementById('search');
    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            filterCompanies(e.target.value);
        });
    }
});

async function testBackendConnection() {
    try {
        console.log('Testing backend connection to:', API_URL);
        const response = await fetch(API_URL + '/');
        if (response.ok) {
            const data = await response.json();
            console.log('✅ Backend is running:', data);
        } else {
            console.error('❌ Backend responded with status:', response.status);
        }
    } catch (error) {
        console.error('❌ Cannot connect to backend:', error);
        console.error('Please ensure the backend is running on', API_URL);
        alert('Cannot connect to backend!\n\nPlease ensure:\n1. Backend is running\n2. Backend is on ' + API_URL + '\n3. No firewall is blocking the connection');
    }
}

async function loadCompanies() {
    try {
        console.log('Fetching companies from:', API_URL + '/companies');
        const response = await fetch(API_URL + '/companies');
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('Companies received:', data);
        allCompanies = data.companies || [];
        
        if (allCompanies.length === 0) {
            console.warn('No companies found. Backend may not have collected data yet.');
            const list = document.getElementById('companies-list');
            if (list) {
                list.innerHTML = '<p style="color: #666; padding: 20px;">No companies available. Please ensure backend has finished collecting data.</p>';
            }
            return;
        }
        
        const list = document.getElementById('companies-list');
        if (!list) {
            console.error('Companies list element not found');
            return;
        }
        
        list.innerHTML = ''; // Clear any existing content
        allCompanies.forEach(company => {
            const div = document.createElement('div');
            div.className = 'company-item';
            div.innerHTML = '<h4>' + company.name + '</h4><p>' + company.symbol + '</p>';
            div.onclick = () => {
                console.log('Company clicked:', company.symbol);
                loadStockData(company.symbol);
            };
            list.appendChild(div);
        });
        
        console.log(`Loaded ${allCompanies.length} companies`);
    } catch (error) {
        console.error('Error loading companies:', error);
        const list = document.getElementById('companies-list');
        if (list) {
            list.innerHTML = '<p style="color: red; padding: 20px;">Error loading companies. Is the backend running on ' + API_URL + '?</p>';
        }
    }
}

async function loadStockData(symbol, days = 30) {
    if (!symbol) {
        console.warn('No symbol provided to loadStockData');
        return;
    }
    currentSymbol = symbol;
    try {
        const url = API_URL + '/data/' + encodeURIComponent(symbol) + '?days=' + days;
        console.log(`Loading data for ${symbol} (${days} days)...`);
        console.log(`Request URL: ${url}`);
        
        const response = await fetch(url);
        
        if (!response.ok) {
            const errorText = await response.text();
            console.error(`HTTP ${response.status} Error:`, errorText);
            
            if (response.status === 404) {
                const errorData = await response.json().catch(() => ({ detail: 'Symbol not found' }));
                alert(`Symbol "${symbol}" not found in database.\n\nPlease ensure:\n1. Backend is running on ${API_URL}\n2. Data collection has completed\n3. Symbol exists in database`);
            } else {
                alert(`Error ${response.status}: ${errorText}`);
            }
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        
        if (!data.data || data.data.length === 0) {
            console.error('No data available for symbol:', symbol);
            alert(`No data available for ${symbol}. Please ensure the backend has collected data.`);
            return;
        }
        
        console.log(`Received ${data.data.length} data points`);
        console.log('Sample data:', data.data[0]);
        
        const dates = data.data.map(d => d.date).reverse();
        const prices = data.data.map(d => d.close).reverse();
        
        // Validate and filter out null/undefined values
        const validData = dates.map((date, idx) => ({
            date: date,
            price: prices[idx]
        })).filter(item => item.date && item.price != null);
        
        if (validData.length === 0) {
            console.error('No valid data points after filtering');
            alert('No valid data available for this symbol.');
            return;
        }
        
        const validDates = validData.map(item => item.date);
        const validPrices = validData.map(item => parseFloat(item.price));
        
        console.log(`Valid data points: ${validDates.length}`);
        console.log('First date:', validDates[0], 'First price:', validPrices[0]);
        console.log('Last date:', validDates[validDates.length - 1], 'Last price:', validPrices[validPrices.length - 1]);
        
        // Hide placeholder and show chart
        const placeholder = document.getElementById('chart-placeholder');
        const chartElement = document.getElementById('stockChart');
        
        // Destroy existing chart if it exists
        if (chart) {
            chart.destroy();
            chart = null;
        }
        
        if (!chartElement) {
            console.error('Chart element not found');
            return;
        }
        
        // Check if Chart.js is loaded
        if (typeof Chart === 'undefined') {
            console.error('Chart.js is not loaded. Please check the CDN link.');
            if (placeholder) placeholder.innerHTML = '<p style="color: red;">Chart.js library failed to load. Please check your internet connection.</p>';
            return;
        }
        
        // Hide placeholder and show canvas
        if (placeholder) placeholder.style.display = 'none';
        chartElement.style.display = 'block';
        
        const ctx = chartElement.getContext('2d');
        
        chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: validDates,
                datasets: [{
                    label: 'Close Price (₹)',
                    data: validPrices,
                    borderColor: '#667eea',
                    backgroundColor: 'rgba(102, 126, 234, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4,
                    pointRadius: 0,
                    pointHoverRadius: 5
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: true,
                        position: 'top'
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: false,
                        title: {
                            display: true,
                            text: 'Price (₹)'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Date'
                        }
                    }
                }
            }
        });
        
        console.log('Chart created successfully');
        loadSummary(symbol);
    } catch (error) {
        console.error('Error loading stock data:', error);
    }
}

async function loadSummary(symbol) {
    try {
        const response = await fetch(API_URL + '/summary/' + symbol);
        const data = await response.json();
        
        document.getElementById('stock-header').innerHTML = '<h2>' + symbol + '</h2>';
        
        const statsGrid = document.getElementById('stats-grid');
        statsGrid.innerHTML = '<div class="stat-card"><h3>Current Price</h3><div class="value">' + 
            data.current_price + '</div></div>' +
            '<div class="stat-card"><h3>52W High</h3><div class="value">' + 
            data.week_52_high + '</div></div>' +
            '<div class="stat-card"><h3>52W Low</h3><div class="value">' + 
            data.week_52_low + '</div></div>';
    } catch (error) {
        console.error('Error:', error);
    }
}

async function loadInsights() {
    try {
        const gainersRes = await fetch(API_URL + '/insights/gainers?limit=5');
        const gainersData = await gainersRes.json();
        
        const losersRes = await fetch(API_URL + '/insights/losers?limit=5');
        const losersData = await losersRes.json();
        
        const gainersList = document.getElementById('gainers-list');
        gainersList.innerHTML = ''; // Clear existing items
        gainersData.gainers.forEach(g => {
            const div = document.createElement('div');
            div.className = 'insight-item positive';
            div.innerHTML = '<span>' + g.symbol + '</span><span>+' + g.avg_return + '%</span>';
            gainersList.appendChild(div);
        });
        
        const losersList = document.getElementById('losers-list');
        losersList.innerHTML = ''; // Clear existing items
        losersData.losers.forEach(l => {
            const div = document.createElement('div');
            div.className = 'insight-item negative';
            div.innerHTML = '<span>' + l.symbol + '</span><span>' + l.avg_return + '%</span>';
            losersList.appendChild(div);
        });
    } catch (error) {
        console.error('Error:', error);
    }
}

function filterCompanies(searchTerm) {
    const list = document.getElementById('companies-list');
    const filtered = allCompanies.filter(company => 
        company.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        company.symbol.toLowerCase().includes(searchTerm.toLowerCase())
    );
    
    list.innerHTML = '';
    filtered.forEach(company => {
        const div = document.createElement('div');
        div.className = 'company-item';
        div.innerHTML = '<h4>' + company.name + '</h4><p>' + company.symbol + '</p>';
        div.onclick = () => loadStockData(company.symbol);
        list.appendChild(div);
    });
}
const API_URL = 'http://localhost:8000';
let chart = null;
let currentSymbol = null;
let allCompanies = [];

document.addEventListener('DOMContentLoaded', () => {
    loadCompanies();
    loadInsights();
});

async function loadCompanies() {
    try {
        const response = await fetch(API_URL + '/companies');
        const data = await response.json();
        allCompanies = data.companies;
        
        const list = document.getElementById('companies-list');
        allCompanies.forEach(company => {
            const div = document.createElement('div');
            div.className = 'company-item';
            div.innerHTML = '<h4>' + company.name + '</h4><p>' + company.symbol + '</p>';
            div.onclick = () => loadStockData(company.symbol);
            list.appendChild(div);
        });
    } catch (error) {
        console.error('Error:', error);
    }
}

async function loadStockData(symbol, days = 30) {
    currentSymbol = symbol;
    try {
        const response = await fetch(API_URL + '/data/' + symbol + '?days=' + days);
        const data = await response.json();
        
        const dates = data.data.map(d => d.date).reverse();
        const prices = data.data.map(d => d.close).reverse();
        
        if (chart) chart.destroy();
        
        const ctx = document.getElementById('stockChart').getContext('2d');
        chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: dates,
                datasets: [{
                    label: 'Close Price',
                    data: prices,
                    borderColor: '#667eea',
                    tension: 0.4
                }]
            }
        });
        
        loadSummary(symbol);
    } catch (error) {
        console.error('Error:', error);
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
        gainersData.gainers.forEach(g => {
            const div = document.createElement('div');
            div.className = 'insight-item positive';
            div.innerHTML = '<span>' + g.symbol + '</span><span>+' + g.avg_return + '%</span>';
            gainersList.appendChild(div);
        });
        
        const losersList = document.getElementById('losers-list');
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
// ===================================
// AI Stock Predictor - Frontend App
// ===================================

// State Management
const state = {
    currentStock: null,
    theme: localStorage.getItem('theme') || 'light',
    chart: null
};

// API Base URL
const API_BASE = window.location.origin;

// Initialize App
document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    initEventListeners();
    loadMarketSummary();
});

// Theme Management
function initTheme() {
    document.documentElement.setAttribute('data-theme', state.theme);
}

function toggleTheme() {
    state.theme = state.theme === 'light' ? 'dark' : 'light';
    localStorage.setItem('theme', state.theme);
    document.documentElement.setAttribute('data-theme', state.theme);

    // Recreate chart with new theme
    if (state.chart) {
        const stockData = state.currentStock;
        if (stockData) {
            createPriceChart(stockData.historical_data, stockData.prediction);
        }
    }
}

// Event Listeners
function initEventListeners() {
    const themeToggle = document.getElementById('themeToggle');
    const searchInput = document.getElementById('searchInput');
    const searchResults = document.getElementById('searchResults');

    themeToggle.addEventListener('click', toggleTheme);

    // Search with debounce
    let searchTimeout;
    searchInput.addEventListener('input', (e) => {
        clearTimeout(searchTimeout);
        const query = e.target.value.trim();

        if (query.length < 2) {
            searchResults.classList.remove('active');
            return;
        }

        searchTimeout = setTimeout(() => {
            searchStocks(query);
        }, 300);
    });

    // Close search results when clicking outside
    document.addEventListener('click', (e) => {
        if (!e.target.closest('.search-container')) {
            searchResults.classList.remove('active');
        }
    });
}

// API Functions
async function searchStocks(query) {
    try {
        const response = await fetch(`${API_BASE}/api/search?q=${encodeURIComponent(query)}&limit=10`);
        const results = await response.json();
        displaySearchResults(results);
    } catch (error) {
        console.error('Search error:', error);
    }
}

async function loadMarketSummary() {
    try {
        console.log('Loading market summary...');
        const response = await fetch(`${API_BASE}/api/market-summary`);
        const data = await response.json();

        console.log('Market summary data:', data);

        displayMarketIndices(data.indices);
        displayMarketNews(data.news);
    } catch (error) {
        console.error('Market summary error:', error);
        // Show fallback message
        const niftyCard = document.getElementById('niftyCard');
        const sensexCard = document.getElementById('sensexCard');
        niftyCard.querySelector('.index-value').textContent = 'Loading...';
        sensexCard.querySelector('.index-value').textContent = 'Loading...';
    }
}

async function loadStockAnalysis(symbol) {
    const stockAnalysis = document.getElementById('stockAnalysis');
    const loadingOverlay = document.getElementById('loadingOverlay');

    stockAnalysis.style.display = 'block';
    loadingOverlay.classList.remove('hidden');

    try {
        console.log(`Loading analysis for ${symbol}...`);
        const response = await fetch(`${API_BASE}/api/stock/${encodeURIComponent(symbol)}`);

        if (!response.ok) {
            throw new Error('Stock not found');
        }

        const data = await response.json();
        console.log('Stock data received:', data);
        state.currentStock = data;

        displayStockAnalysis(data);

        // Scroll to analysis
        stockAnalysis.scrollIntoView({ behavior: 'smooth', block: 'start' });
    } catch (error) {
        console.error('Stock analysis error:', error);
        alert(`Error loading stock data: ${error.message}. Please try again.`);
        stockAnalysis.style.display = 'none';
    } finally {
        loadingOverlay.classList.add('hidden');
    }
}

// Display Functions
function displaySearchResults(results) {
    const searchResults = document.getElementById('searchResults');

    if (results.length === 0) {
        searchResults.innerHTML = '<div style="padding: 1rem; text-align: center; color: var(--text-secondary);">No results found</div>';
        searchResults.classList.add('active');
        return;
    }

    searchResults.innerHTML = results.map(stock => `
        <div class="search-result-item" onclick="selectStock('${stock.symbol}')">
            <div class="search-result-name">${stock.name}</div>
            <div class="search-result-symbol">${stock.symbol} • ${stock.exchange}</div>
        </div>
    `).join('');

    searchResults.classList.add('active');
}

function selectStock(symbol) {
    const searchResults = document.getElementById('searchResults');
    const searchInput = document.getElementById('searchInput');

    searchResults.classList.remove('active');
    searchInput.value = '';

    loadStockAnalysis(symbol);
}

function displayMarketIndices(indices) {
    if (indices.nifty50) {
        const niftyCard = document.getElementById('niftyCard');
        const change = indices.nifty50.change;
        const changePercent = indices.nifty50.change_percent;
        const isPositive = change >= 0;

        niftyCard.querySelector('.index-value').textContent = `₹${formatNumber(indices.nifty50.value)}`;
        niftyCard.querySelector('.index-change').innerHTML = `
            ${isPositive ? '▲' : '▼'} ₹${formatNumber(Math.abs(change))} (${formatNumber(Math.abs(changePercent), 2)}%)
        `;
        niftyCard.querySelector('.index-change').className = `index-change ${isPositive ? 'positive' : 'negative'}`;
    }

    if (indices.sensex) {
        const sensexCard = document.getElementById('sensexCard');
        const change = indices.sensex.change;
        const changePercent = indices.sensex.change_percent;
        const isPositive = change >= 0;

        sensexCard.querySelector('.index-value').textContent = `₹${formatNumber(indices.sensex.value)}`;
        sensexCard.querySelector('.index-change').innerHTML = `
            ${isPositive ? '▲' : '▼'} ₹${formatNumber(Math.abs(change))} (${formatNumber(Math.abs(changePercent), 2)}%)
        `;
        sensexCard.querySelector('.index-change').className = `index-change ${isPositive ? 'positive' : 'negative'}`;
    }
}

function displayMarketNews(news) {
    const marketNews = document.getElementById('marketNews');

    if (!news || news.length === 0) {
        marketNews.innerHTML = '<p style="text-align: center; color: var(--text-secondary);">No market news available</p>';
        return;
    }

    marketNews.innerHTML = news.map(article => `
        <div class="market-news-item" onclick="window.open('${article.url}', '_blank')">
            <h3 class="news-title">${article.title}</h3>
            <div class="news-meta">
                <span>${article.source}</span>
                <span>•</span>
                <span>${formatDate(article.published_at)}</span>
                <span class="news-sentiment ${article.sentiment.label}">${article.sentiment.label.toUpperCase()}</span>
            </div>
        </div>
    `).join('');
}

function displayStockAnalysis(data) {
    displayStockHeader(data.fundamentals);
    displayFundamentals(data.fundamentals);
    displayVerdict(data.ai_summary.verdict);
    createPriceChart(data.historical_data, data.prediction);
    displayTechnicalIndicators(data.technical_indicators);
    displayNewsAndSentiment(data.news, data.sentiment);
    displayAISummary(data.ai_summary);
}

function displayStockHeader(fundamentals) {
    const stockHeader = document.getElementById('stockHeader');
    const change = fundamentals.change;
    const changePercent = fundamentals.change_percent;
    const isPositive = change >= 0;

    stockHeader.innerHTML = `
        <div class="stock-name">${fundamentals.name}</div>
        <div class="stock-symbol">${fundamentals.symbol} • ${fundamentals.sector}</div>
        <div class="stock-price-info">
            <div class="stock-price">₹${formatNumber(fundamentals.cmp, 2)}</div>
            <div class="stock-change ${isPositive ? 'positive' : 'negative'}">
                ${isPositive ? '▲' : '▼'} ₹${formatNumber(Math.abs(change), 2)} (${formatNumber(Math.abs(changePercent), 2)}%)
            </div>
        </div>
    `;
}

function displayFundamentals(fundamentals) {
    const fundamentalsGrid = document.getElementById('fundamentalsGrid');

    const items = [
        { label: 'Market Cap', value: `₹${formatNumber(fundamentals.market_cap / 10000000, 2)} Cr` },
        { label: 'P/E Ratio', value: formatNumber(fundamentals.pe_ratio, 2) },
        { label: 'Dividend Yield', value: `${formatNumber(fundamentals.dividend_yield, 2)}%` },
        { label: 'ROE', value: `${formatNumber(fundamentals.roe, 2)}%` },
        { label: '52W High', value: `₹${formatNumber(fundamentals['52_week_high'], 2)}` },
        { label: '52W Low', value: `₹${formatNumber(fundamentals['52_week_low'], 2)}` },
        { label: 'Beta', value: formatNumber(fundamentals.beta, 2) },
        { label: 'EPS', value: `₹${formatNumber(fundamentals.eps, 2)}` }
    ];

    fundamentalsGrid.innerHTML = items.map(item => `
        <div class="fundamental-item">
            <div class="fundamental-label">${item.label}</div>
            <div class="fundamental-value">${item.value}</div>
        </div>
    `).join('');
}

function displayVerdict(verdict) {
    const verdictContent = document.getElementById('verdictContent');

    verdictContent.innerHTML = `
        <div class="verdict-badge ${verdict.verdict.toLowerCase()}">${verdict.verdict}</div>
        <div class="verdict-confidence">Confidence: ${verdict.confidence}%</div>
        <div class="verdict-reasons">
            <h4>Key Factors</h4>
            <ul>
                ${verdict.reasons.map(reason => `<li>${reason}</li>`).join('')}
            </ul>
        </div>
        <p style="margin-top: 1rem; font-size: 0.875rem; color: var(--text-tertiary); text-align: center;">
            ${verdict.disclaimer}
        </p>
    `;
}

function createPriceChart(historicalData, prediction) {
    const ctx = document.getElementById('priceChart');

    // Destroy existing chart
    if (state.chart) {
        state.chart.destroy();
    }

    const isDark = state.theme === 'dark';
    const textColor = isDark ? '#cbd5e1' : '#475569';
    const gridColor = isDark ? '#334155' : '#e2e8f0';

    // Prepare data
    const historicalDates = historicalData.dates;
    const historicalPrices = historicalData.close;

    // Generate future dates
    const lastDate = new Date(historicalDates[historicalDates.length - 1]);
    const futureDates = [];
    for (let i = 1; i <= 7; i++) {
        const futureDate = new Date(lastDate);
        futureDate.setDate(lastDate.getDate() + i);
        futureDates.push(futureDate.toISOString().split('T')[0]);
    }

    const allDates = [...historicalDates.slice(-60), ...futureDates];
    const historicalPricesSliced = historicalPrices.slice(-60);

    // Create prediction line (starts from last historical price)
    const predictionLine = new Array(60).fill(null);
    predictionLine.push(historicalPricesSliced[historicalPricesSliced.length - 1]);
    predictionLine.push(...prediction.predictions);

    state.chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: allDates,
            datasets: [
                {
                    label: 'Historical Price',
                    data: [...historicalPricesSliced, ...new Array(8).fill(null)],
                    borderColor: '#6366f1',
                    backgroundColor: 'rgba(99, 102, 241, 0.1)',
                    borderWidth: 2,
                    tension: 0.4,
                    fill: true
                },
                {
                    label: 'Predicted Price',
                    data: predictionLine,
                    borderColor: '#06b6d4',
                    backgroundColor: 'rgba(6, 182, 212, 0.1)',
                    borderWidth: 2,
                    borderDash: [5, 5],
                    tension: 0.4,
                    fill: false
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            interaction: {
                intersect: false,
                mode: 'index'
            },
            plugins: {
                legend: {
                    labels: {
                        color: textColor,
                        font: {
                            family: 'Inter'
                        }
                    }
                },
                tooltip: {
                    backgroundColor: isDark ? '#1e293b' : '#ffffff',
                    titleColor: textColor,
                    bodyColor: textColor,
                    borderColor: gridColor,
                    borderWidth: 1
                }
            },
            scales: {
                x: {
                    ticks: {
                        color: textColor,
                        maxRotation: 45,
                        minRotation: 45
                    },
                    grid: {
                        color: gridColor
                    }
                },
                y: {
                    ticks: {
                        color: textColor,
                        callback: function (value) {
                            return '₹' + value.toFixed(2);
                        }
                    },
                    grid: {
                        color: gridColor
                    }
                }
            }
        }
    });

    // Display chart legend info
    const chartLegend = document.getElementById('chartLegend');
    chartLegend.innerHTML = `
        <strong>Prediction Metrics:</strong> 
        MAPE: ${formatNumber(prediction.backtest_metrics?.mape || 0, 2)}% | 
        R²: ${formatNumber(prediction.backtest_metrics?.r2 || 0, 3)} | 
        Trend: ${prediction.trend} (${formatNumber(prediction.change_percent, 2)}%)
    `;
}

function displayTechnicalIndicators(indicators) {
    const technicalGrid = document.getElementById('technicalGrid');

    const latest = indicators.latest || {};

    const items = [
        { label: 'RSI (14)', value: formatNumber(latest.rsi_current, 2) },
        { label: 'MACD', value: formatNumber(latest.macd_current, 4) },
        { label: 'Price vs SMA20', value: `${formatNumber(latest.price_vs_sma20, 2)}%` },
        { label: 'Price vs SMA50', value: `${formatNumber(latest.price_vs_sma50, 2)}%` },
        { label: 'Price vs SMA200', value: `${formatNumber(latest.price_vs_sma200, 2)}%` }
    ];

    technicalGrid.innerHTML = items.map(item => `
        <div class="technical-item">
            <div class="technical-label">${item.label}</div>
            <div class="technical-value">${item.value}</div>
        </div>
    `).join('');
}

function displayNewsAndSentiment(news, sentiment) {
    const sentimentSummary = document.getElementById('sentimentSummary');
    const newsList = document.getElementById('newsList');

    // Sentiment summary
    sentimentSummary.innerHTML = `
        <div class="sentiment-label ${sentiment.label}">${sentiment.label.toUpperCase()}</div>
        <div style="color: var(--text-secondary); margin-top: 0.5rem;">
            Positive: ${sentiment.positive_count} | Negative: ${sentiment.negative_count} | Neutral: ${sentiment.neutral_count}
        </div>
    `;

    // News list
    if (news.length === 0) {
        newsList.innerHTML = '<p style="text-align: center; color: var(--text-secondary);">No recent news available</p>';
        return;
    }

    newsList.innerHTML = news.map(article => `
        <div class="news-item" onclick="window.open('${article.url}', '_blank')">
            <h4 class="news-title">${article.title}</h4>
            <div class="news-meta">
                <span>${article.source}</span>
                <span>•</span>
                <span>${formatDate(article.published_at)}</span>
                <span class="news-sentiment ${article.sentiment.label}">${article.sentiment.label.toUpperCase()}</span>
            </div>
        </div>
    `).join('');
}

function displayAISummary(aiSummary) {
    const summaryContent = document.getElementById('summaryContent');

    summaryContent.innerHTML = `
        <div class="summary-section">
            <h3>📊 Technical Analysis</h3>
            <p>${aiSummary.technical_summary}</p>
        </div>
        <div class="summary-section">
            <h3>💼 Fundamental Analysis</h3>
            <p>${aiSummary.fundamental_summary}</p>
        </div>
        <div class="summary-section">
            <h3>📰 News Sentiment</h3>
            <p>${aiSummary.sentiment_summary}</p>
        </div>
        <div class="summary-section">
            <h3>🔮 Price Prediction</h3>
            <p>${aiSummary.prediction_summary}</p>
        </div>
    `;
}

// Utility Functions
function formatNumber(num, decimals = 0) {
    if (num === null || num === undefined || isNaN(num)) return 'N/A';
    return Number(num).toLocaleString('en-IN', {
        minimumFractionDigits: decimals,
        maximumFractionDigits: decimals
    });
}

function formatDate(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));

    if (diffHours < 24) {
        return `${diffHours}h ago`;
    } else if (diffHours < 48) {
        return 'Yesterday';
    } else {
        return date.toLocaleDateString('en-IN', { month: 'short', day: 'numeric' });
    }
}

// Make selectStock globally available
window.selectStock = selectStock;

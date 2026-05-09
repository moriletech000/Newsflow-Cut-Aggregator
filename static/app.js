// Global state
let allArticles = [];
let currentFilters = {
    source: 'All',
    category: 'All',
    country: 'All',
    region: 'All',
    search: ''
};

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    initializeClock();
    initializeFilters();
    initializeSearch();
    initializeRefreshButton();
    loadArticles();
});

// Clock and date
function initializeClock() {
    const updateTime = () => {
        const now = new Date();
        
        // Update date
        const dateOptions = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
        document.getElementById('currentDate').textContent = now.toLocaleDateString('en-US', dateOptions);
        
        // Update live time
        const timeOptions = { hour: '2-digit', minute: '2-digit', second: '2-digit' };
        document.getElementById('liveTime').textContent = now.toLocaleTimeString('en-US', timeOptions);
    };
    
    updateTime();
    setInterval(updateTime, 1000);
}

// Load articles from API
async function loadArticles() {
    try {
        showLoading();
        
        const params = new URLSearchParams();
        if (currentFilters.source !== 'All') params.append('source', currentFilters.source);
        if (currentFilters.category !== 'All') params.append('category', currentFilters.category);
        if (currentFilters.country !== 'All') params.append('country', currentFilters.country);
        if (currentFilters.region !== 'All') params.append('region', currentFilters.region);
        if (currentFilters.search) params.append('q', currentFilters.search);
        
        const response = await fetch(`/api/news?${params.toString()}`);
        const data = await response.json();
        
        allArticles = data.articles;
        
        // Update stats
        updateStats(data);
        
        // Show warning if there are errors
        if (data.has_error) {
            document.getElementById('warningBanner').style.display = 'block';
        } else {
            document.getElementById('warningBanner').style.display = 'none';
        }
        
        // Render articles
        renderArticles(allArticles);
        
        // Update ticker
        updateTicker(allArticles);
        
    } catch (error) {
        console.error('Error loading articles:', error);
        showError();
    }
}

// Show loading state
function showLoading() {
    document.getElementById('loadingState').style.display = 'block';
    document.getElementById('articlesContainer').style.display = 'none';
    document.getElementById('emptyState').style.display = 'none';
}

// Update stats
function updateStats(data) {
    const articleCount = data.count;
    const sources = new Set(data.articles.map(a => a.source));
    const sourceCount = sources.size;
    
    document.getElementById('articleCount').textContent = articleCount;
    document.getElementById('sourceCount').textContent = sourceCount;
    document.getElementById('footerArticles').textContent = `${articleCount} articles`;
    document.getElementById('footerSources').textContent = `${sourceCount} sources`;
    
    if (data.last_update) {
        const updateDate = new Date(data.last_update);
        const timeStr = updateDate.toLocaleString('en-US', {
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
        document.getElementById('footerUpdate').textContent = `Last updated: ${timeStr}`;
    }
}

// Render articles
function renderArticles(articles) {
    document.getElementById('loadingState').style.display = 'none';
    
    if (articles.length === 0) {
        document.getElementById('articlesContainer').style.display = 'none';
        document.getElementById('emptyState').style.display = 'block';
        return;
    }
    
    document.getElementById('articlesContainer').style.display = 'block';
    document.getElementById('emptyState').style.display = 'none';
    
    // Hero article (first article)
    const heroContainer = document.getElementById('heroArticle');
    if (articles.length > 0) {
        heroContainer.innerHTML = createHeroArticle(articles[0]);
    }
    
    // Secondary articles (next 2 articles)
    const secondaryContainer = document.getElementById('secondaryArticles');
    const secondaryArticles = articles.slice(1, 3);
    secondaryContainer.innerHTML = secondaryArticles.map(article => createArticleCard(article)).join('');
    
    // Main feed (remaining articles)
    const mainFeedContainer = document.getElementById('mainFeed');
    const mainArticles = articles.slice(3);
    mainFeedContainer.innerHTML = mainArticles.map(article => createArticleCard(article)).join('');
}

// Create hero article HTML
function createHeroArticle(article) {
    return `
        <div class="hero-article">
            <div class="hero-source">
                <i class="fas fa-map-marker-alt"></i> ${escapeHtml(article.country)} • 
                <i class="fas fa-globe"></i> ${escapeHtml(article.region)} • 
                <i class="fas fa-tag"></i> ${escapeHtml(article.category)}
            </div>
            <h2 class="hero-title">${escapeHtml(article.title)}</h2>
            <p class="hero-summary">${escapeHtml(article.summary)}</p>
            <div class="hero-meta">
                <span class="hero-date">
                    <i class="fas fa-clock"></i> ${escapeHtml(article.published)}
                </span>
                <a href="${escapeHtml(article.link)}" target="_blank" rel="noopener noreferrer" class="hero-link">
                    Read Story <i class="fas fa-arrow-right"></i>
                </a>
            </div>
        </div>
    `;
}

// Create article card HTML
function createArticleCard(article) {
    return `
        <div class="article-card">
            <div class="article-source">
                <i class="fas fa-map-marker-alt"></i> ${escapeHtml(article.country)} • 
                <i class="fas fa-tag"></i> ${escapeHtml(article.category)}
            </div>
            <h3 class="article-title">${escapeHtml(article.title)}</h3>
            <p class="article-summary">${escapeHtml(article.summary)}</p>
            <div class="article-footer">
                <span class="article-date">
                    <i class="fas fa-clock"></i> ${escapeHtml(article.published)}
                </span>
                <a href="${escapeHtml(article.link)}" target="_blank" rel="noopener noreferrer" class="article-link">
                    Read <i class="fas fa-arrow-right"></i>
                </a>
            </div>
        </div>
    `;
}

// Update ticker
function updateTicker(articles) {
    const tickerContent = document.getElementById('tickerContent');
    const headlines = articles.slice(0, 20).map(a => a.title);
    
    // Duplicate headlines for seamless loop
    const tickerHTML = [...headlines, ...headlines].map(headline => 
        `<span class="ticker-item">${escapeHtml(headline)}</span><span class="ticker-separator">•</span>`
    ).join('');
    
    tickerContent.innerHTML = tickerHTML;
}

// Initialize filters
function initializeFilters() {
    // Get unique data from initial load
    fetch('/api/news')
        .then(response => response.json())
        .then(data => {
            // Get unique regions
            const regions = [...new Set(data.articles.map(a => a.region))].sort();
            const regionFilters = document.getElementById('regionFilters');
            regions.forEach(region => {
                const button = document.createElement('button');
                button.className = 'chip';
                button.dataset.region = region;
                button.textContent = region;
                regionFilters.appendChild(button);
            });
            
            // Get unique countries
            const countries = [...new Set(data.articles.map(a => a.country))].sort();
            const countryFilters = document.getElementById('countryFilters');
            countries.forEach(country => {
                const button = document.createElement('button');
                button.className = 'chip';
                button.dataset.country = country;
                button.textContent = country;
                countryFilters.appendChild(button);
            });
            
            // Add click handlers
            regionFilters.addEventListener('click', handleRegionFilter);
            countryFilters.addEventListener('click', handleCountryFilter);
        });
    
    // Category filters
    document.getElementById('categoryFilters').addEventListener('click', handleCategoryFilter);
}

// Handle region filter
function handleRegionFilter(e) {
    if (e.target.classList.contains('chip')) {
        // Remove active from all
        document.querySelectorAll('#regionFilters .chip').forEach(chip => {
            chip.classList.remove('active');
        });
        
        // Add active to clicked
        e.target.classList.add('active');
        
        // Update filter
        currentFilters.region = e.target.dataset.region;
        loadArticles();
    }
}

// Handle country filter
function handleCountryFilter(e) {
    if (e.target.classList.contains('chip')) {
        // Remove active from all
        document.querySelectorAll('#countryFilters .chip').forEach(chip => {
            chip.classList.remove('active');
        });
        
        // Add active to clicked
        e.target.classList.add('active');
        
        // Update filter
        currentFilters.country = e.target.dataset.country;
        loadArticles();
    }
}

// Handle category filter
function handleCategoryFilter(e) {
    if (e.target.classList.contains('chip')) {
        // Remove active from all
        document.querySelectorAll('#categoryFilters .chip').forEach(chip => {
            chip.classList.remove('active');
        });
        
        // Add active to clicked
        e.target.classList.add('active');
        
        // Update filter
        currentFilters.category = e.target.dataset.category;
        loadArticles();
    }
}

// Initialize search
function initializeSearch() {
    const searchInput = document.getElementById('searchInput');
    let debounceTimer;
    
    searchInput.addEventListener('input', (e) => {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => {
            currentFilters.search = e.target.value;
            loadArticles();
        }, 300);
    });
}

// Initialize refresh button
function initializeRefreshButton() {
    const refreshButton = document.getElementById('refreshButton');
    
    refreshButton.addEventListener('click', async () => {
        refreshButton.classList.add('loading');
        refreshButton.disabled = true;
        
        try {
            const response = await fetch('/api/refresh');
            const data = await response.json();
            
            if (data.success) {
                showToast(`Feed updated — ${data.count} articles loaded`);
                await loadArticles();
            }
        } catch (error) {
            console.error('Error refreshing:', error);
            showToast('Error refreshing feed');
        } finally {
            refreshButton.classList.remove('loading');
            refreshButton.disabled = false;
        }
    });
}

// Show toast notification
function showToast(message) {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.classList.add('show');
    
    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

// Show error state
function showError() {
    document.getElementById('loadingState').style.display = 'none';
    document.getElementById('articlesContainer').style.display = 'none';
    document.getElementById('emptyState').style.display = 'block';
    document.querySelector('.empty-state h2').textContent = 'Error loading articles';
    document.querySelector('.empty-state p').textContent = 'Please try refreshing the page';
}

// Escape HTML to prevent XSS
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

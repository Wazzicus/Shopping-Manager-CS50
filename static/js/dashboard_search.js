document.addEventListener('DOMContentLoaded', function() {
    const dashboardSearchInput = document.getElementById('dashboardSearchInput');
    const dashboardClearBtn = document.getElementById('dashboardClearSearchBtn');
    const dashboardMainSearchBtn = document.getElementById('dashboardMainSearchBtn');
    let dashboardClearTimeoutId = null;
    if (dashboardSearchInput && dashboardClearBtn && dashboardMainSearchBtn) {
        function updateDashboardClearButtonVisibility(delayAppearance = false) {
            if (dashboardClearTimeoutId) { clearTimeout(dashboardClearTimeoutId); dashboardClearTimeoutId = null; }
            const hasText = dashboardSearchInput.value.length > 0;
            const hasFocus = document.activeElement === dashboardSearchInput;
            if (hasText && hasFocus) {
                if (delayAppearance) {
                    dashboardClearTimeoutId = setTimeout(() => { dashboardClearBtn.style.display = 'flex'; }, 150);
                } else { dashboardClearBtn.style.display = 'flex'; }
            } else { dashboardClearBtn.style.display = 'none'; }
        }
        dashboardSearchInput.addEventListener('input', () => updateDashboardClearButtonVisibility(false));
        dashboardSearchInput.addEventListener('focus', () => { dashboardMainSearchBtn.classList.remove('expanded'); updateDashboardClearButtonVisibility(true); });
        dashboardSearchInput.addEventListener('blur', () => {
        dashboardClearBtn.style.display = 'none';
        if (dashboardClearTimeoutId) { clearTimeout(dashboardClearTimeoutId); dashboardClearTimeoutId = null; }
            setTimeout(() => { if (document.activeElement !== dashboardSearchInput) { dashboardMainSearchBtn.classList.add('expanded'); } }, 150);
        });
        dashboardClearBtn.addEventListener('click', () => {
        dashboardSearchInput.value = ''; dashboardClearBtn.style.display = 'none';
        if (dashboardClearTimeoutId) { clearTimeout(dashboardClearTimeoutId); dashboardClearTimeoutId = null; }
        dashboardSearchInput.focus();
        });
        if (document.activeElement !== dashboardSearchInput) { dashboardMainSearchBtn.classList.add('expanded'); }
        else { dashboardMainSearchBtn.classList.remove('expanded'); updateDashboardClearButtonVisibility(true); }
    }
    
    const searchForm = document.getElementById('dashboardListSearchForm');
    const searchInput = document.getElementById('dashboardSearchInput');
    const clearSearchBtn = document.getElementById('dashboardClearSearchBtn');
    const searchResultsContainer = document.getElementById('dashboardContent');
    const searchSpinner = document.getElementById('dashboardSearchSpinner');
    const mainSearchBtn = document.getElementById('dashboardMainSearchBtn');
    let debounceTimer;

    // Clear search results
    function clearSearchResults() {
        searchResultsContainer.innerHTML = '';
        searchInput.value = '';
        searchInput.focus();
    }

    function performSearch() {
        const query = searchInput.value.trim();
        
        if (query.length < MIN_SEARCH_LENGTH && query.length > 0) return;
        
        searchSpinner.classList.remove('d-none');
        
        fetch(`${searchForm.action}?q=${encodeURIComponent(query)}`, {
            method: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest'  // This triggers is_ajax=True in Flask
            }
        })
        .then(response => response.json())
        .then(data => {
            // Extract HTML from the JSON response
            resultsContainer.innerHTML = data.html;
            searchResultsContainer.classList.remove('d-none');
        })
        .catch(error => {
            console.error('Search error:', error);
        })
        .finally(() => {
            searchSpinner.classList.add('d-none');
        });
    }
    // Debounce search input
    function debounceSearch(query) {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => {
            if (query.length >= 2) {
                performSearch(query);
            } else {
                searchResultsContainer.innerHTML = '';
            }
        }, 300);
    }

    // Event listeners
    searchInput.addEventListener('input', (e) => {
        const query = e.target.value.trim();
        debounceSearch(query);
    });

    clearSearchBtn.addEventListener('click', clearSearchResults);

    searchForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const query = searchInput.value.trim();
        if (query) {
            performSearch(query);
        } else {
            clearSearchResults();
        }
    });

    // Initialize if there's a search query
    if (searchInput.value.trim()) {
        performSearch(searchInput.value.trim());
    }
});
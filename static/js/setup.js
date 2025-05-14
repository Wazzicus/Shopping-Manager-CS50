// js/setup.js
document.addEventListener('DOMContentLoaded', () => {
    setupToggleSlider('householdTab', 'tabSlider');
    const householdTabList = document.querySelectorAll('#householdTab button[data-bs-toggle="tab"]');
    householdTabList.forEach(tabEl => {
        tabEl.addEventListener('shown.bs.tab', event => {
        });
    });

    
    if (window.location.hash) {
        const tabId = window.location.hash.substring(1); 
        const tabToActivate = document.getElementById(tabId);

        if (tabToActivate && tabToActivate.matches('button[data-bs-toggle="tab"]')) {
            const tab = new bootstrap.Tab(tabToActivate);
            if (tab) { 
               tab.show();
            }
        }
    }
    setupToggleSlider('householdTab', 'tabSlider');
});
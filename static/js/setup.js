// setup.js

document.addEventListener('DOMContentLoaded', () => {
    setupToggleSlider('householdTab', 'tabSlider');
    const joinForm = document.getElementById('joinHouseholdForm');
    const createForm = document.getElementById('createHouseholdForm');
    const joinTabPane = document.getElementById('join-tab-pane');
    const createTabPane = document.getElementById('create-tab-pane');

    // Function to ensure correct form visibility based on active tab pane
    function syncFormVisibility() {
        if (joinTabPane && joinForm) {
            if (joinTabPane.classList.contains('active')) {
                joinForm.classList.remove('hidden');
            } else {
                joinForm.classList.add('hidden');
            }
        }
        if (createTabPane && createForm) {
            if (createTabPane.classList.contains('active')) {
                createForm.classList.remove('hidden');
            } else {
                createForm.classList.add('hidden');
            }
        }
    }

    // Initial sync based on HTML active classes
    syncFormVisibility();

    // Listen to Bootstrap tab shown events
    const tabContainer = document.getElementById('householdTab');
    if (tabContainer) {
        tabContainer.addEventListener('shown.bs.tab', function(event) {
            
            syncFormVisibility();
        });
    }

    // Handle deep linking via hash
    if (window.location.hash) {
        const hash = window.location.hash.substring(1);
        const tabToActivate = document.getElementById(`${hash}-tab`);
        if (tabToActivate) {
            const tab = new bootstrap.Tab(tabToActivate); 
           
    } else {
        
        const defaultActiveTab = document.querySelector('#householdTab .nav-link.active');
        if (!defaultActiveTab && document.getElementById('join-tab')) {
             const tab = new bootstrap.Tab(document.getElementById('join-tab'));
             tab.show();
        }
    }
}});
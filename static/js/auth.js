// auth.js

document.addEventListener('DOMContentLoaded', () => {
    setupToggleSlider('toggleTab', 'tabSlider');
    const loginForm = document.getElementById('login_form');
    const registerForm = document.getElementById('register_form');
    const loginTabPane = document.getElementById('login-tab-pane');
    const registerTabPane = document.getElementById('register-tab-pane');

    // Function to ensure correct form visibility based on active tab pane
    function syncFormVisibility() {
        if (loginTabPane && loginForm) {
            if (loginTabPane.classList.contains('active')) {
                loginForm.classList.remove('hidden');
            } else {
                loginForm.classList.add('hidden');
            }
        }
        if (registerTabPane && registerForm) {
            if (registerTabPane.classList.contains('active')) {
                registerForm.classList.remove('hidden');
            } else {
                registerForm.classList.add('hidden');
            }
        }
    }

    // Initial sync based on HTML active classes
    syncFormVisibility();

    // Listen to Bootstrap tab shown events
    const tabContainer = document.getElementById('toggleTab');
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
        
        const defaultActiveTab = document.querySelector('#toggleTab .nav-link.active');
        if (!defaultActiveTab && document.getElementById('login-tab')) {
             const tab = new bootstrap.Tab(document.getElementById('login-tab'));
             tab.show();
        }
    }
}});
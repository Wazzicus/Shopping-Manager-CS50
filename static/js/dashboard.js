document.addEventListener('DOMContentLoaded', () => {
    const dashboardNewListInput = document.getElementById('dashboardNewListInput');
    const dashboardClearBtn2 = document.getElementById('dashboardClearBtn2');
    const dashboardNewListBtn = document.getElementById('dashboardNewListBtn');
    const dashboardListAddForm = document.getElementById('dashboardListAddForm');
    const dashboardNewListSpinner = document.getElementById('dashboardNewListSpinner');
    let dashboardClearTimeoutId = null;

    if (dashboardNewListInput && dashboardClearBtn2 && dashboardNewListBtn && dashboardListAddForm) {
        // Update clear button visibility
        function updateDashboardClearButtonVisibility(delayAppearance = false) {
            if (dashboardClearTimeoutId) {
                clearTimeout(dashboardClearTimeoutId);
                dashboardClearTimeoutId = null;
            }
            
            const hasText = dashboardNewListInput.value.length > 0;
            const hasFocus = document.activeElement === dashboardNewListInput;
            
            if (hasText && hasFocus) {
                if (delayAppearance) {
                    dashboardClearTimeoutId = setTimeout(() => {
                        dashboardClearBtn2.classList.add('visible');
                    }, 150);
                } else {
                    dashboardClearBtn2.classList.add('visible');
                }
            } else {
                dashboardClearBtn2.classList.remove('visible');
            }
        }

        // Input event handler
        dashboardNewListInput.addEventListener('input', () => {
            updateDashboardClearButtonVisibility(false);
            
            // Toggle expanded class based on input value
            if (dashboardNewListInput.value.trim().length > 0) {
                dashboardNewListBtn.classList.remove('expanded');
            } else {
                dashboardNewListBtn.classList.add('expanded');
            }
        });

        // Focus event handler
        dashboardNewListInput.addEventListener('focus', () => {
            dashboardNewListBtn.classList.remove('expanded');
            updateDashboardClearButtonVisibility(true);
        });

        // Blur event handler
        dashboardNewListInput.addEventListener('blur', () => {
            dashboardClearBtn2.classList.remove('visible');
            
            if (dashboardClearTimeoutId) {
                clearTimeout(dashboardClearTimeoutId);
                dashboardClearTimeoutId = null;
            }
            
            setTimeout(() => {
                if (document.activeElement !== dashboardNewListInput) {
                    if (dashboardNewListInput.value.trim().length === 0) {
                        dashboardNewListBtn.classList.add('expanded');
                    }
                }
            }, 150);
        });

        // Clear button click handler
        dashboardClearBtn2.addEventListener('click', () => {
            dashboardNewListInput.value = '';
            dashboardClearBtn2.classList.remove('visible');
            
            if (dashboardClearTimeoutId) {
                clearTimeout(dashboardClearTimeoutId);
                dashboardClearTimeoutId = null;
            }
            
            dashboardNewListInput.focus();
            dashboardNewListBtn.classList.add('expanded');
        });

        // Form submission handler
        dashboardListAddForm.addEventListener('submit', async (e) => {            
            const listName = dashboardNewListInput.value.trim();
            const validation = validateListName(listName);
            
            if (!validation.valid) {
                showToast(validation.message, 'error');
                dashboardNewListInput.focus();
                return;
            }
            
            try {
                // Show loading state
                dashboardNewListBtn.disabled = true;
                dashboardNewListSpinner.classList.remove('d-none');
                dashboardNewListBtn.querySelector('i').classList.add('d-none');
                
                
                    // Reset form
                    dashboardNewListInput.value = '';
                    dashboardNewListBtn.classList.add('expanded');
                    
            } catch (error) {
                console.error('Error:', error);
                showToast(error.message || 'An error occurred while creating the list', 'error');
            } finally {
                // Reset loading state
                dashboardNewListBtn.disabled = false;
                dashboardNewListSpinner.classList.add('d-none');
                dashboardNewListBtn.querySelector('i').classList.remove('d-none');
                
                // Return focus to input
                dashboardNewListInput.focus();
            }
        });

        // Initialize state
        if (document.activeElement !== dashboardNewListInput) {
            dashboardNewListBtn.classList.add('expanded');
        } else {
            dashboardNewListBtn.classList.remove('expanded');
            updateDashboardClearButtonVisibility(true);
        }
    }

});
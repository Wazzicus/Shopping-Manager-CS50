// dashboard.js

document.addEventListener('DOMContentLoaded', () => {
    const dashboardNewListInput = document.getElementById('dashboardNewListInput');
    const dashboardClearBtn2 = document.getElementById('dashboardClearBtn2');
    const dashboardNewListBtn = document.getElementById('dashboardNewListBtn');
    const dashboardListAddForm = document.getElementById('dashboardListAddForm');
    const dashboardNewListSpinner = document.getElementById('dashboardNewListSpinner');
    let dashboardClearTimeoutId = null;

    if (dashboardNewListInput && dashboardClearBtn2 && dashboardNewListBtn && dashboardListAddForm) {

        // Toggle visibility of clear button based on input content and focus
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

        // Update clear button and submit button style on input change
        dashboardNewListInput.addEventListener('input', () => {
            updateDashboardClearButtonVisibility(false);

            if (dashboardNewListInput.value.trim().length > 0) {
                dashboardNewListBtn.classList.remove('expanded');
            } else {
                dashboardNewListBtn.classList.add('expanded');
            }
        });

        // On focus, remove expanded style and show clear button with delay
        dashboardNewListInput.addEventListener('focus', () => {
            dashboardNewListBtn.classList.remove('expanded');
            updateDashboardClearButtonVisibility(true);
        });

        // On blur, hide clear button and possibly restore expanded style
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

        // Clear input and reset styles on clear button click
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

        // Handle form submission to create a new list
        dashboardListAddForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const listName = dashboardNewListInput.value.trim();
            const validation = validateListName(listName);
            
            if (!validation.valid) {
                showToast(validation.message, 'error');
                dashboardNewListInput.focus();
                return;
            }
            
            try {
                dashboardNewListBtn.disabled = true;
                dashboardNewListSpinner.classList.remove('d-none');
                dashboardNewListBtn.querySelector('i').classList.add('d-none');

                // Add list creation logic here
                
                dashboardNewListInput.value = '';
                dashboardNewListBtn.classList.add('expanded');
            } catch (error) {
                showToast(error.message || 'An error occurred while creating the list', 'error');
            } finally {
                dashboardNewListBtn.disabled = false;
                dashboardNewListSpinner.classList.add('d-none');
                dashboardNewListBtn.querySelector('i').classList.remove('d-none');
                dashboardNewListInput.focus();
            }
        });

        // Initialize submit button style based on input focus state
        if (document.activeElement !== dashboardNewListInput) {
            dashboardNewListBtn.classList.add('expanded');
        } else {
            dashboardNewListBtn.classList.remove('expanded');
            updateDashboardClearButtonVisibility(true);
        }
    }
});

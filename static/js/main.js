/**
 * main.js
 * Site-wide JavaScript including toasts, theme toggle, search bar,
 * confirmation modal handling, and page loader logic.
 */

// --- Global Utility Functions ---

/**
 * Displays a Bootstrap Toast notification.
 * Assumes specific HTML template exists (#toastTemplate) and a .toast-container.
 * @param {string} message - The main message content for the toast body.
 * @param {string} category - Type of toast ('success', 'danger', 'warning', 'info', 'primary', 'secondary', 'light', 'dark'). Default is 'info'.
 * @param {number} delay - How long the toast stays visible in milliseconds. Default 5000. Set to 0 for non-autohiding.
 * @param {string} title - Optional title for the toast header. Default is 'Notification'.
 */
function showToast(message, category = 'info', delay = 5000, title = 'Notification') {
    // console.log(`DEBUG: showToast function started. Msg: "${message}", Cat: "${category}"`);
    const toastTemplate = document.getElementById('toastTemplate');
    const toastContainer = document.querySelector('.toast-container');

    if (!toastTemplate || !toastContainer) {
        console.error('Toast template (#toastTemplate) or container (.toast-container) not found.');
        alert(`${title} (${category}): ${message}`);
        return;
    }

    try {
        const toastClone = toastTemplate.content.cloneNode(true);
        const toastElement = toastClone.querySelector('.toast');
        const toastTitleElement = toastClone.querySelector('.toast-title');
        const toastBodyElement = toastClone.querySelector('.toast-body');
        const toastTimestampElement = toastClone.querySelector('.toast-timestamp');

        if (!toastElement || !toastTitleElement || !toastBodyElement) {
             console.error('Toast template is missing required elements (.toast, .toast-title, .toast-body).');
             return;
        }

        toastTitleElement.textContent = title;
        toastBodyElement.textContent = message;

        if (toastTimestampElement) {
            toastTimestampElement.textContent = 'Just now';
        }

        const bgClasses = ['bg-success', 'bg-danger', 'bg-warning', 'bg-info', 'bg-primary', 'bg-secondary', 'bg-light', 'bg-dark'];
        toastElement.classList.remove(...bgClasses, 'text-white', 'text-dark');

        const categoryClass = `bg-${category}`;
        toastElement.classList.add(categoryClass);

        if (category !== 'light' && category !== 'warning' && category !== 'info') {
            toastElement.classList.add('text-white');
        } else {
            toastElement.classList.add('text-dark');
        }

        toastContainer.appendChild(toastElement);

        const options = {};
        if (delay > 0) {
            options.delay = delay;
            options.autohide = true;
        } else {
            options.autohide = false;
        }
        const bsToast = new bootstrap.Toast(toastElement, options);

        toastElement.addEventListener('hidden.bs.toast', () => {
            toastElement.remove();
        });

        bsToast.show();

    } catch (error) {
        console.error("Error creating or showing toast:", error);
        alert(`${title} (${category}): ${message}`);
    }
}

/**
 * Toggles the data-bs-theme attribute on the body element.
 */
function toggleTheme() {
    const currentTheme = document.body.getAttribute('data-bs-theme');
    if (currentTheme === 'dark') {
        document.body.setAttribute('data-bs-theme', 'light');
        // localStorage.setItem('theme', 'light');
    } else {
        document.body.setAttribute('data-bs-theme', 'dark');
        // localStorage.setItem('theme', 'dark');
    }
}


// --- Initialization code runs after DOM is loaded ---
document.addEventListener('DOMContentLoaded', () => {

    // --- Theme Initialization ---
    const themeToggleButton = document.getElementById('darkModeToggle');
    if (themeToggleButton) {
        themeToggleButton.addEventListener('click', toggleTheme);
    }


    // --- Confirmation Modal Logic ---
    const confirmationModalElement = document.getElementById('confirmModal');
    const confirmBtn = document.getElementById('confirmBtn');
    const modalTitleElement = document.getElementById('confirmModalLabel');
    const modalBodyElement = confirmationModalElement?.querySelector('.modal-body');
    let actionUrl = null;
    let redirectUrl = null;
    let originalConfirmBtnText = 'Confirm';

    if (confirmationModalElement && confirmBtn && modalTitleElement && modalBodyElement) {
        originalConfirmBtnText = confirmBtn.textContent;

        confirmationModalElement.addEventListener('show.bs.modal', (event) => {
            const button = event.relatedTarget;
            if (!button) return;

            modalTitleElement.textContent = button.getAttribute('data-modal-title') || 'Confirm Action';
            modalBodyElement.textContent = button.getAttribute('data-modal-body') || 'Are you sure?';
            confirmBtn.textContent = button.getAttribute('data-modal-confirm-text') || originalConfirmBtnText;
            confirmBtn.className = 'btn';
            confirmBtn.classList.add(button.getAttribute('data-modal-confirm-class') || 'btn-primary');
            actionUrl = button.getAttribute('data-action-url');
            redirectUrl = button.getAttribute('data-redirect-url');
            confirmBtn.setAttribute('data-original-text', confirmBtn.textContent);
            confirmationModalElement.dataset.targetElementSelector = button.getAttribute('data-target-element-selector');
        });

        confirmationModalElement.addEventListener('hidden.bs.modal', () => {
            actionUrl = null; redirectUrl = null; confirmBtn.disabled = false;
            confirmBtn.innerHTML = confirmBtn.getAttribute('data-original-text') || originalConfirmBtnText;
            delete confirmationModalElement.dataset.targetElementSelector;
        });

        confirmBtn.addEventListener('click', async () => {
            if (!actionUrl) {
                console.error("Action URL not set for confirmation modal.");
                return;
            }

            confirmBtn.disabled = true;
            confirmBtn.innerHTML = `<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Processing...`;

            try {
                const csrfTokenVal = document.querySelector('meta[name="csrf-token"]')?.content;
                if (!csrfTokenVal) throw new Error("CSRF token missing");

                const response = await fetch(actionUrl, {
                    method: 'POST',
                    headers: { 'X-CSRFToken': csrfTokenVal, 'X-Requested-With': 'XMLHttpRequest' }
                });

                const modalInstance = bootstrap.Modal.getInstance(confirmationModalElement);
                let result = {};
                try { result = await response.json(); }
                catch (e) {
                    result = { success: response.ok, message: response.ok ? 'Action completed (no JSON).' : `Request failed: ${response.status}` };
                }

                if (response.ok && result.success) {
                    if (modalInstance) modalInstance.hide();
                    showToast(result.message || 'Action completed successfully.', 'success');

                    // --- CORRECTED: Retrieve selector from modal's dataset ---
                    const targetSelector = confirmationModalElement.dataset.targetElementSelector;
                    console.log("Dispatching modalActionSuccess. Selector:", targetSelector); // DEBUG

                    document.body.dispatchEvent(new CustomEvent('modalActionSuccess', {
                        detail: {
                            actionUrl: actionUrl,
                            response: result,
                            targetElementSelector: targetSelector // Use the directly stored selector
                        }
                    }));
                    // --- End custom event dispatch ---

                    const finalRedirectUrl = result.redirect_url || redirectUrl; 

                    if (finalRedirectUrl) {
                        setTimeout(() => { window.location.href = finalRedirectUrl; }, 1000); 
                    }
                } else {
                    showToast(result.message || `Action failed (Status: ${response.status})`, 'danger');
                    confirmBtn.disabled = false;
                    confirmBtn.innerHTML = confirmBtn.getAttribute('data-original-text') || originalConfirmBtnText;
                }
            } catch (error) {
                console.error("Error performing modal action:", error);
                showToast(`Error: ${error.message || 'Network error or issue processing request.'}`, 'danger');
                confirmBtn.disabled = false;
                confirmBtn.innerHTML = confirmBtn.getAttribute('data-original-text') || originalConfirmBtnText;
            }
        });
    }

    // --- Page Loader Logic ---
    const pageLoader = document.querySelector('#pageLoader');
    if (pageLoader) {
        // console.log("Page loader element found, attaching navigation listeners.");
        function showLoader() {
            pageLoader.classList.remove('hidden');
            // console.log("Loader shown.");
        }
        const navLinksSelector = 'a[href]:not([href^="#"]):not([target="_blank"]):not([download]):not([rel="external"]):not([href^="javascript:"]):not([href^="mailto:"]):not([href^="tel:"])';
        const navLinks = document.querySelectorAll(navLinksSelector);
        navLinks.forEach(link => {
            link.addEventListener('click', (event) => {
                 if (!link.hasAttribute('data-bs-toggle') && !link.closest('.no-loader')) {
                    // console.log("Navigation link clicked:", link.href);
                    showLoader();
                 }
            });
        });
        const navFormsSelector = 'form:not(.ajax-form)';
        const navForms = document.querySelectorAll(navFormsSelector);
        navForms.forEach(form => {
             form.addEventListener('submit', () => {
                // console.log("Non-AJAX Form submitted, showing loader:", form.action);
                showLoader();
             });
        });
        window.addEventListener('pageshow', function(event) {
            if (event.persisted) {
                // console.log("Page shown from bfcache, ensuring loader is hidden.");
                pageLoader.classList.add('hidden');
            }
        });
    }

    // --- Footer Year ---
    const yearSpan = document.getElementById('year');
    if (yearSpan) {
        yearSpan.textContent = new Date().getFullYear();
    }
}); // End DOMContentLoaded

const navFormsSelector = 'form:not(#addItemForm):not(.ajax-form)';
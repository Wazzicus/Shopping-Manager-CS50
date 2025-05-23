/**
 * main.js
 * Site-wide JavaScript including toasts, theme toggle, search bar,
 * confirmation modal handling, and page loader logic.
 */

// --- Global Utility Functions ---

/**
 * Displays a Bootstrap Toast notification.
 * @param {string} message - Toast message body.
 * @param {string} category - Toast category for styling.
 * @param {number} delay - Duration toast is visible in ms.
 * @param {string} title - Optional toast title.
 */

// Show Toast Function
function showToast(message, category = 'info', delay = 5000, title = 'Notification') {
    const toastTemplate = document.getElementById('toastTemplate');
    const toastContainer = document.querySelector('.toast-container');

    if (!toastTemplate || !toastContainer) {
        alert(`${title} (${category}): ${message}`);
        return;
    }

    try {
        const toastClone = toastTemplate.content.cloneNode(true);
        const toastElement = toastClone.querySelector('.toast');
        const toastTitleElement = toastClone.querySelector('.toast-title');
        const toastBodyElement = toastClone.querySelector('.toast-body');
        const toastTimestampElement = toastClone.querySelector('.toast-timestamp');

        if (!toastElement || !toastTitleElement || !toastBodyElement) return;

        toastTitleElement.textContent = title;
        toastBodyElement.textContent = message;

        if (toastTimestampElement) {
            toastTimestampElement.textContent = 'Just now';
        }

        const bgClasses = ['bg-success', 'bg-danger', 'bg-warning', 'bg-info', 'bg-primary', 'bg-secondary', 'bg-light', 'bg-dark'];
        toastElement.classList.remove(...bgClasses, 'text-white', 'text-dark');
        toastElement.classList.add(`bg-${category}`);

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
        alert(`${title} (${category}): ${message}`);
    }
}

// Gets CSRF token
function getCSRFToken() {
    const metaTag = document.querySelector('meta[name="csrf-token"]');
    return metaTag ? metaTag.content : '';
}

document.addEventListener('DOMContentLoaded', () => {   
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
            confirmBtn.classList.add(button.getAttribute('data-modal-confirm-class') || 'btn-danger', 'w-100');
            actionUrl = button.getAttribute('data-action-url');
            redirectUrl = button.getAttribute('data-redirect-url');
            confirmBtn.setAttribute('data-original-text', confirmBtn.textContent);
            confirmationModalElement.dataset.targetElementSelector = button.getAttribute('data-target-element-selector');
        });

        confirmationModalElement.addEventListener('hidden.bs.modal', () => {
            actionUrl = null;
            redirectUrl = null;
            confirmBtn.disabled = false;
            confirmBtn.innerHTML = confirmBtn.getAttribute('data-original-text') || originalConfirmBtnText;
            delete confirmationModalElement.dataset.targetElementSelector;
        });

        confirmBtn.addEventListener('click', async () => {
            if (!actionUrl) return;

            confirmBtn.disabled = true;
            confirmBtn.innerHTML = `<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Processing...`;

            try {
                const csrfTokenVal = getCSRFToken();
                if (!csrfTokenVal) throw new Error("CSRF token missing");

                const response = await fetch(actionUrl, {
                    method: 'POST',
                    headers: { 'X-CSRFToken': csrfTokenVal, 'X-Requested-With': 'XMLHttpRequest' }
                });

                const modalInstance = bootstrap.Modal.getInstance(confirmationModalElement);
                let result = {};
                try {
                    result = await response.json();
                } catch {
                    result = { success: response.ok, message: response.ok ? 'Action completed (no JSON).' : `Request failed: ${response.status}` };
                }

                if (response.ok && result.success) {
                    if (modalInstance) modalInstance.hide();
                    showToast(result.message || 'Action completed successfully.', 'success');

                    const targetSelector = confirmationModalElement.dataset.targetElementSelector;

                    document.body.dispatchEvent(new CustomEvent('modalActionSuccess', {
                        detail: {
                            actionUrl,
                            response: result,
                            targetElementSelector: targetSelector
                        }
                    }));

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
                showToast(`Error: ${error.message || 'Network error or issue processing request.'}`, 'danger');
                confirmBtn.disabled = false;
                confirmBtn.innerHTML = confirmBtn.getAttribute('data-original-text') || originalConfirmBtnText;
            }
        });
    }

    // Page Loader Logic
    const pageLoader = document.querySelector('#pageLoader');
    if (pageLoader) {
        function showLoader() {
            pageLoader.classList.remove('hidden');
        }
        const navLinksSelector = 'a[href]:not([href^="#"]):not([target="_blank"]):not([download]):not([rel="external"]):not([href^="javascript:"]):not([href^="mailto:"]):not([href^="tel:"])';
        const navLinks = document.querySelectorAll(navLinksSelector);
        navLinks.forEach(link => {
            link.addEventListener('click', () => {
                if (!link.hasAttribute('data-bs-toggle') && !link.closest('.no-loader')) {
                    showLoader();
                }
            });
        });
        const navFormsSelector = 'form:not(.ajax-form)';
        const navForms = document.querySelectorAll(navFormsSelector);
        navForms.forEach(form => {
            form.addEventListener('submit', () => {
                showLoader();
            });
        });
        window.addEventListener('pageshow', (event) => {
            if (event.persisted) {
                pageLoader.classList.add('hidden');
            }
        });
    }

    // Footer Year
    const yearSpan = document.getElementById('year');
    if (yearSpan) {
        yearSpan.textContent = new Date().getFullYear();
    }
});

const navFormsSelector = 'form:not(#addItemForm):not(.ajax-form)';

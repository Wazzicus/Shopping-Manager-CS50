/**
 * view_list.js
 * Handles interactions specific to the shopping list view page:
 * - AJAX for toggling item purchase status
 * - AJAX for adding items (with quantity and measure)
 * - Inline editing of item names
 * - Updating the custom segmented progress bar with flex-basis animation
 * Relies on global showToast() defined in main.js
 */

document.addEventListener('DOMContentLoaded', () => {
    // Ensure global showToast function exists
    if (typeof showToast !== 'function') {
        console.error("showToast function is not defined. Make sure main.js is loaded first.");
        // Define a fallback alert if showToast is missing
        window.showToast = function(message, category = 'info') { // Fallback
            alert(`${category.toUpperCase()}: ${message}`);
        };
    }

    const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content;
    const listContainer = document.getElementById('itemList');
    const listHeader = document.querySelector('.list-header');
    const addItemForm = document.getElementById('addItemForm');
    const addItemButton = document.getElementById('button-add-item');
    const newItemInput = document.getElementById('newItemNameInput');
    const newItemQuantityInput = document.getElementById('newItemQuantityInput');
    const newItemMeasureInput = document.getElementById('newItemMeasureInput');

    let isSaving = false;

    if (!csrfToken) {
        console.error('CSRF token not found.');
        showToast('Error: CSRF token missing. Please refresh.', 'danger');
        return;
    }

    // --- Progress Bar Elements & Update Function ---
    const progressTrackElement = listHeader?.querySelector('.custom-progress-track');
    const filledSegment = progressTrackElement?.querySelector('.custom-progress-filled');
    const gapSegment = progressTrackElement?.querySelector('.custom-progress-gap');
    const unfilledSegment = progressTrackElement?.querySelector('.custom-progress-unfilled');
    const percentageLabel = listHeader?.querySelector('#progressPercentageLabel');

    const GAP_WIDTH_PX = 4;

    function updateProgressBar() {
        if (!progressTrackElement || !filledSegment || !gapSegment || !unfilledSegment) { return; }
        if (!percentageLabel) { console.warn("Percentage label for progress bar (#progressPercentageLabel) not found."); }

        const listItems = listContainer?.querySelectorAll('li.list-group-item.item-row') || [];
        const totalItems = listItems.length;
        const purchasedItems = listContainer?.querySelectorAll('li.list-group-item.item-row.item-purchased')?.length || 0;

        let percentage = totalItems > 0 ? (purchasedItems / totalItems) * 100 : 0;
        percentage = Math.min(100, Math.max(0, percentage));
        const percentageInt = Math.round(percentage);

        progressTrackElement.setAttribute('aria-valuenow', percentageInt);
        filledSegment.style.width = percentage + '%';
        filledSegment.style.flexBasis = percentage + '%';

        if (percentage >= 100) {
            gapSegment.style.display = 'none';
            unfilledSegment.style.width = '0%';
            unfilledSegment.style.flexBasis = '0%';
            unfilledSegment.classList.add('is-empty');
        } else if (percentage <= 0) {
            gapSegment.style.display = 'none';
            filledSegment.style.width = '0%';
            filledSegment.style.flexBasis = '0%';
            unfilledSegment.style.width = '100%';
            unfilledSegment.style.flexBasis = '100%';
            unfilledSegment.classList.remove('is-empty');
        } else {
            gapSegment.style.display = 'block';
            gapSegment.style.width = `${GAP_WIDTH_PX}px`;
            gapSegment.style.flexBasis = `${GAP_WIDTH_PX}px`;
            const unfilledBasis = `calc(100% - ${percentage}% - ${GAP_WIDTH_PX}px)`;
            unfilledSegment.style.width = unfilledBasis;
            unfilledSegment.style.flexBasis = unfilledBasis;
            unfilledSegment.classList.remove('is-empty');
        }
        if (percentageLabel) {
            percentageLabel.textContent = percentageInt + '%';
        }
    }

    // --- Toggle Purchase Status AJAX Function ---
    async function togglePurchaseStatus(button, itemId, listItemElement) {
        if (!listItemElement) { showToast('Could not perform action: item structure error.', 'danger'); return; }
        const itemNameElement = listItemElement.querySelector('.item-name-column .item-name-line .item-name');
        if (!itemId || !itemNameElement) { showToast('Could not perform action: item details missing.', 'danger'); return; }
        const originalHTML = button.innerHTML;
        button.disabled = true;
        button.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>';
        try {
            const url = `/shopping/list/item/${itemId}/toggle_purchase`;
            const response = await fetch(url, { method: 'POST', headers: { 'X-CSRFToken': csrfToken, 'X-Requested-With': 'XMLHttpRequest' } });
            const result = await response.json();
            if (response.ok && result.success) {
                const newStatus = result.purchased_status;
                listItemElement.classList.toggle('item-purchased', newStatus);
                itemNameElement.classList.toggle('text-decoration-line-through', newStatus);
                const iconClass = newStatus ? 'bi-arrow-counterclockwise' : 'bi-check-circle';
                const buttonText = newStatus ? ' Undo' : ' Mark as Purchased';
                button.innerHTML = `<i class="bi ${iconClass}"></i><span class="d-none d-md-inline">${buttonText}</span>`;
                button.classList.remove('btn-success', 'btn-outline-secondary');
                button.classList.add(newStatus ? 'btn-outline-secondary' : 'btn-success');
                updateProgressBar();
                showToast(result.message || 'Status updated!', 'success');
            } else {
                showToast(result.message || 'Could not update purchase status.', 'danger');
                button.innerHTML = originalHTML;
            }
        } catch (error) {
            showToast(error.message || 'Network error or issue processing request.', 'danger');
            button.innerHTML = originalHTML;
        } finally {
            button.disabled = false;
        }
    }

    // --- Add Item AJAX Function ---
    async function addItem(itemName, quantity, measure, listId) {
        try {
            const url = `/shopping/list/${listId}`;
            const response = await fetch(url, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken, 'X-Requested-With': 'XMLHttpRequest' },
                body: JSON.stringify({ name: itemName, quantity: quantity, measure: measure }),
            });
            const result = await response.json();
            if (response.ok && result.success) {
                const newItemData = result.item;
                if (!newItemData || !newItemData.id || !newItemData.name) { showToast("Error processing server response.", "danger"); return; }
                const ul = document.getElementById('itemList');
                const placeholder = document.getElementById('emptyListPlaceholder');
                if (placeholder) {
                    if (placeholder.tagName === 'LI') { placeholder.remove(); }
                    else { placeholder.classList.add('d-none'); }
                }
                if (!ul) { console.error("Could not find #itemList to append new item to."); return; }
                const li = createListItemElement(newItemData, csrfToken);
                ul.appendChild(li);
                if (newItemInput) newItemInput.value = '';
                if (newItemQuantityInput) newItemQuantityInput.value = '';
                if (newItemMeasureInput) newItemMeasureInput.value = '';
                updateProgressBar();
                showToast(result.message || 'Item added!', 'success');
            } else {
                 showToast(result.message || "Failed to add item.", 'danger');
            }
        } catch (error) {
            showToast("Network error adding item. Please try again.", 'danger');
        }
    }

    // --- Function to create List Item HTML (Helper - Includes Profile Pic in Pill) ---
    function createListItemElement(itemData, csrfTokenValue) {
        const li = document.createElement('li');
        li.className = 'list-group-item item-row';
        if (itemData.purchased) li.classList.add('item-purchased');
        li.setAttribute('data-item-id', itemData.id);


        const safeName = (itemData.name || '').replace(/</g, "&lt;").replace(/>/g, "&gt;");
        const addedByName = itemData.added_by_name || 'N/A'; 
        const safeAddedBy = addedByName.replace(/</g, "&lt;").replace(/>/g, "&gt;");
        const profilePicUrl = itemData.profile_pic_url || "/static/images/default_avatar.png"; // Fallback

        const safeQuantity = itemData.quantity !== null && itemData.quantity !== undefined ? String(itemData.quantity).replace(/</g, "&lt;").replace(/>/g, "&gt;") : '';
        const safeMeasure = (itemData.measure || '').replace(/</g, "&lt;").replace(/>/g, "&gt;");

        const editUrl = `/shopping/list/item/${itemData.id}/edit`;
        const toggleUrl = `/shopping/list/item/${itemData.id}/toggle_purchase`;
        const deleteUrl = `/shopping/list/item/${itemData.id}/delete`;

        const toggleBtnClass = itemData.purchased ? 'btn-outline-secondary' : 'btn-success';
        const toggleIconClass = itemData.purchased ? 'bi-arrow-counterclockwise' : 'bi-check-circle';
        const toggleBtnText = itemData.purchased ? ' Undo' : ' Mark Purchased';
        const nameClass = itemData.purchased ? 'item-name editable text-decoration-line-through' : 'item-name editable';

        let quantityDisplayHTML = `<span class="item-quantity-measure text-muted">-</span>`;
        if (itemData.quantity || itemData.measure) {
            let qtyText = itemData.quantity !== null && itemData.quantity !== undefined ? safeQuantity : '1';
            quantityDisplayHTML = `<span class="item-quantity-measure">(${qtyText} ${safeMeasure})</span>`;
        }

        li.innerHTML = `
            <div class="row w-100 align-items-center gy-2">
                <div class="col-md-5 col-12 item-name-column">
                    <div class="item-name-line">
                        <span class="${nameClass}" style="cursor: pointer;">${safeName}</span>
                    </div>
                    <input type="text" class="form-control item-edit-input d-none" value="${safeName}">
                    <small class="item-details-text d-block mt-1">
                        Added by:
                        <span class="added-by-pill bg-secondary">
                            <img src="${profilePicUrl}"
                                 class="profile-pic-thumb"
                                 alt="${safeAddedBy}'s profile picture"
                                 onerror="this.style.display='none'; this.nextElementSibling.style.marginLeft='0';">
                            <span class="added-by-name">${safeAddedBy}</span>
                        </span>
                    </small>
                    <div class="edit-error text-danger mt-1 w-100" style="display: none;"></div>
                </div>
                <div class="col-md-3 col-6 item-quantity-column">
                    ${quantityDisplayHTML}
                </div>
                <div class="col-md-4 col-6 item-actions-column">
                    <a href="${editUrl}" class="btn btn-sm btn-outline-secondary me-1 mb-1 mb-md-0">
                        <i class="bi bi-pencil-square"></i><span class="d-none d-md-inline"> Edit</span>
                    </a>
                    <form method="post" action="${toggleUrl}" style="display: inline-block;" class="me-1 mb-1 mb-md-0 toggle-purchase-form ajax-form">
                        <input type="hidden" name="csrf_token" value="${csrfTokenValue}">
                        <button type="submit" class="btn btn-sm ${toggleBtnClass} toggle-purchase-btn" data-item-id="${itemData.id}">
                            <i class="bi ${toggleIconClass}"></i><span class="d-none d-md-inline">${toggleBtnText}</span>
                        </button>
                    </form>
                    <button type="button" class="btn btn-sm btn-outline-danger delete-item-btn mb-1 mb-md-0"
                            data-bs-toggle="modal" data-bs-target="#confirmModal"
                            data-modal-title="Confirm Item Deletion"
                            data-modal-body="Are you sure you want to delete the item '${safeName}'?"
                            data-modal-confirm-text="Delete Item" data-modal-confirm-class="btn-danger"
                            data-action-url="${deleteUrl}"
                            data-target-element-selector="li[data-item-id='${itemData.id}']">
                        <i class="bi bi-trash"></i><span class="d-none d-md-inline"> Delete</span>
                    </button>
                </div>
            </div>
        `;
        return li;
    }

    // --- Inline Editing Helper Functions ---
    function enterItemEditMode(spanElement) {
        const nameColumn = spanElement.closest('.item-name-column');
        if (!nameColumn) return;
        const nameLine = nameColumn.querySelector('.item-name-line');
        const inputElement = nameColumn.querySelector('.item-edit-input');
        const originalValue = spanElement.textContent.trim();

        if (!inputElement || !nameLine) return;

        inputElement.value = originalValue;
        nameLine.classList.add('d-none');
        inputElement.classList.remove('d-none');
        inputElement.select();
        inputElement.dataset.originalValue = originalValue;
    }

    function exitItemEditMode(inputElement, savedName) {
        const nameColumn = inputElement.closest('.item-name-column');
        if (!nameColumn) return;
        const nameLine = nameColumn.querySelector('.item-name-line');
        const spanElement = nameLine?.querySelector('.item-name');
        const errorElement = nameColumn.querySelector('.edit-error');

        if (!spanElement || !nameLine) return;

        if (savedName !== undefined) {
            spanElement.textContent = savedName;
        }
        nameLine.classList.remove('d-none');
        inputElement.classList.add('d-none');
        if (errorElement) {
            errorElement.textContent = '';
            errorElement.style.display = 'none';
        }
        delete inputElement.dataset.originalValue;
    }

    function cancelItemEditMode(inputElement) {
        const originalValue = inputElement.dataset.originalValue;
        inputElement.value = originalValue !== undefined ? originalValue : '';
        exitItemEditMode(inputElement);
    }

    async function saveItemName(inputElement) {
        if (isSaving) return;
        const listItemElement = inputElement.closest('.list-group-item');
        const nameColumn = inputElement.closest('.item-name-column');
        const errorElement = nameColumn?.querySelector('.edit-error');
        const itemId = listItemElement?.dataset.itemId;
        const newName = inputElement.value.trim();
        const originalName = inputElement.dataset.originalValue || nameColumn?.querySelector('.item-name-line .item-name')?.textContent.trim();

        if (!itemId || !nameColumn) { console.error("Missing itemId or nameColumn for saving."); return; }
        if (!newName) {
            if (errorElement) { errorElement.textContent = 'Item name cannot be empty.'; errorElement.style.display = 'block';}
            inputElement.focus(); return;
        }
        if (newName === originalName) { exitItemEditMode(inputElement, originalName); return; }
        isSaving = true; inputElement.disabled = true;
        if (errorElement) errorElement.style.display = 'none';
        try {
            const url = `/shopping/list/item/${itemId}/update_name`;
            const response = await fetch(url, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken, 'X-Requested-With': 'XMLHttpRequest' },
                body: JSON.stringify({ new_name: newName })
            });
            const result = await response.json();
            if (response.ok && result.success) {
                exitItemEditMode(inputElement, result.new_name);
                showToast(`Item renamed to "${result.new_name}".`, 'success');
            } else {
                if (errorElement) { errorElement.textContent = result.message || 'Failed to save.'; errorElement.style.display = 'block';}
                else { showToast(result.message || 'Failed to save item name.', 'danger'); }
                inputElement.disabled = false; inputElement.focus();
            }
        } catch (error) {
            inputElement.disabled = false;
            if (errorElement) { errorElement.textContent = 'Network error. Please try again.'; errorElement.style.display = 'block';}
            else { showToast('Network error. Could not save item name.', 'danger');}
            inputElement.focus();
        } finally {
            isSaving = false;
        }
    }

    // --- Event Listeners Setup ---
    if (listContainer) {
        listContainer.addEventListener('click', async (event) => {
            const toggleButton = event.target.closest('.toggle-purchase-btn');
            if (toggleButton) {
                event.preventDefault();
                const itemId = toggleButton.dataset.itemId;
                const listItemElement = toggleButton.closest('.list-group-item.item-row');
                if (itemId && listItemElement) { await togglePurchaseStatus(toggleButton, itemId, listItemElement); }
                return;
            }
            const itemNameSpan = event.target.closest('.item-name-line .item-name.editable');
            if (itemNameSpan && itemNameSpan.classList.contains('editable')) {
                 if (!isSaving) { enterItemEditMode(itemNameSpan); }
                 return;
            }
        });
        listContainer.addEventListener('focusout', (event) => {
             if (event.target.classList.contains('item-edit-input')) {
                 setTimeout(async () => {
                     if (document.activeElement !== event.target && !isSaving) {
                         await saveItemName(event.target);
                     }
                 }, 150);
             }
        });
        listContainer.addEventListener('keydown', async (event) => {
            if (event.target.classList.contains('item-edit-input')) {
                if (event.key === 'Enter') {
                    event.preventDefault();
                    await saveItemName(event.target);
                } else if (event.key === 'Escape') {
                    cancelItemEditMode(event.target);
                }
            }
        });
    } else { console.warn('#itemList container not found for event listeners.'); }

    if (addItemForm && newItemInput && addItemButton) {
         addItemForm.addEventListener('submit', async function(event) {
            event.preventDefault();
            const itemName = newItemInput.value.trim();
            const quantity = newItemQuantityInput?.value.trim() || null;
            const measure = newItemMeasureInput?.value.trim() || null;
            const listId = addItemForm.dataset.listId;
            if (!itemName) {
                showToast("Please enter an item name.", 'warning');
                newItemInput.focus();
                return;
            }
            const originalButtonHTML = addItemButton.innerHTML;
            addItemButton.disabled = true;
            addItemButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Adding...';
            await addItem(itemName, quantity, measure, listId);
            addItemButton.disabled = false;
            addItemButton.innerHTML = originalButtonHTML;
         });
    } else { console.warn("Add item form elements not all found."); }

    document.body.addEventListener('modalActionSuccess', (event) => {
        if (event.detail && event.detail.actionUrl && event.detail.actionUrl.includes('/delete')) {
            if(event.detail.targetElementSelector) {
                const elementToRemove = document.querySelector(event.detail.targetElementSelector);
                if (elementToRemove && elementToRemove.closest('#itemList')) {
                    elementToRemove.remove();
                    updateProgressBar();
                }
            } else {
                updateProgressBar();
            }
        }
    });

    // --- Initial Progress Bar Calculation ---
    updateProgressBar();

}); // End DOMContentLoaded

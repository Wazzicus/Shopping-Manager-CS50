// settings.js

// Handle display name change
function changeDisplayName() {
    const input = document.getElementById('nameChangeForm').querySelector('#new_name');
    const newName = input.value.trim();
    const currentDisplay = document.getElementById('currentDisplayName');
    const initialName = document.getElementById('initialDisplayName').value.trim();

    if (!newName || newName === initialName) {
        showToast('Please enter a different display name', 'error');
        return;
    }

    const btn = document.getElementById('changeNameBtn');
    const spinner = btn.querySelector('.spinner-border');
    const btnText = btn.querySelector('.button-text');

    // Disable button & show spinner
    btn.disabled = true;
    spinner.classList.remove('d-none');
    btnText.textContent = 'Updating...';

    fetch('/settings/change-name', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken(),
        },
        body: JSON.stringify({ new_name: newName })
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(err => { throw err; });
        }
        return response.json();
    })
    .then(data => {
        showToast(data.message || 'Display name updated successfully', 'success');
        updateDisplayNameUI(newName);
        input.value = '';
        document.getElementById('initialDisplayName').value = newName;
    })
    .catch(error => {
        showToast(error.error || 'Failed to update display name', 'error');
        console.error('Error:', error);
    })
    .finally(() => {
        // Re-enable button & reset spinner
        btn.disabled = false;
        spinner.classList.add('d-none');
        btnText.textContent = 'Change Display Name';
    });
}

// Update display name visually with animation
function updateDisplayNameUI(newName) {
    const displayElements = document.querySelectorAll('.current-display-name, .user-name-display');

    displayElements.forEach(el => {
        el.style.transition = 'opacity 0.3s ease';
        el.style.opacity = '0';
        setTimeout(() => {
            el.textContent = newName;
            el.style.opacity = '1';
        }, 300);
    });
}

// Setup event listeners
document.addEventListener('DOMContentLoaded', function () {
    const btn = document.getElementById('changeNameBtn');
    if (btn) {
        btn.addEventListener('click', changeDisplayName);
    }
});

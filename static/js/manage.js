// manage.js

// Function to handle household renaming
function renameHousehold() {
    const newNameInput = document.getElementById('newHouseholdName');
    const newName = newNameInput.value.trim();
    
    if (!newName) {
        showToast('Please enter a new household name', 'error');
        return;
    }

    const renameBtn = document.getElementById('newHouseholdNameBtn');
    renameBtn.disabled = true;
    renameBtn.classList.add('btn-loading');

    fetch(document.getElementById('renameHouseholdForm').action, {
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
        showToast(data.message || 'Household renamed successfully', 'success');
        updateHouseholdNameDisplay(newName);
        newNameInput.value = '';
    })
    .catch(error => {
        showToast(error.error || 'Failed to rename household', 'error');
        console.error('Error:', error);
    })
    .finally(() => {
        renameBtn.disabled = false;
        renameBtn.classList.remove('btn-loading');
    });
}

function updateHouseholdNameDisplay(newName) {
    // Update all elements with the household name
    const nameElements = document.querySelectorAll('.household-name, .household-name-display');
    
    nameElements.forEach(el => {
        el.style.transition = 'opacity 0.3s ease';
        el.style.opacity = '0';
        
        setTimeout(() => {
            el.textContent = newName;
            el.style.opacity = '1';
        }, 300);
    });
};

// Function to regenerate join code
function regenerateJoinCode() {
    const btn = document.getElementById('regenerateJoinCodeBtn');
    const url = btn.dataset.url;
    
    btn.disabled = true;
    btn.classList.add('btn-loading');

    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken(),
        }
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(err => { throw err; });
        }
        return response.json();
    })
    .then(data => {
        showToast('Join code regenerated successfully', 'success');
        updateJoinCodeDisplay(data.new_code);
    })
    .catch(error => {
        showToast(error.error || 'Failed to regenerate join code', 'error');
        console.error('Error:', error);
    })
    .finally(() => {
        btn.disabled = false;
        btn.classList.remove('btn-loading');
    });
}

// Function to update join code display with fade animation
function updateJoinCodeDisplay(newCode) {
    const joinCodeElement = document.getElementById('householdJoinCode');
    if (joinCodeElement) {
        // Create fade animation
        joinCodeElement.style.transition = 'opacity 0.3s ease';
        joinCodeElement.style.opacity = '0';
        
        setTimeout(() => {
            joinCodeElement.textContent = newCode;
            joinCodeElement.style.opacity = '1';
        }, 300);
    }
}


// Initialize form submission
document.addEventListener('DOMContentLoaded', function() {
    const renameForm = document.getElementById('renameHouseholdForm');
    if (renameForm) {
        renameForm.addEventListener('submit', function(e) {
            e.preventDefault();
            renameHousehold();
        });
    }

    const renameBtn = document.getElementById('newHouseholdNameBtn');
    if (renameBtn) {
        renameBtn.addEventListener('click', renameHousehold);
    }

    const regenerateBtn = document.getElementById('regenerateJoinCodeBtn');
    if (regenerateBtn) {
        regenerateBtn.addEventListener('click', regenerateJoinCode);
    }
});
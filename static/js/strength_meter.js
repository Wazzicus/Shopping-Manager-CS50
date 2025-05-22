// strength_meter.js
document.addEventListener('DOMContentLoaded', () => {
    const newPassword = document.getElementById('newPassword');
    const confirmPassword = document.getElementById('confirmPassword');
    const strengthFeedback = document.getElementById('strengthFeedback');
    const matchFeedback = document.getElementById('matchFeedback');
    const submitButton = document.getElementById('PasswordBtn');

    function updateStrengthMeter() {
        const password = newPassword.value;
        if (password.length === 0) {
            strengthFeedback.textContent = '';
            return;
        }
        const result = zxcvbn(password);
        const score = result.score;

        const messages = [
            'Very weak 🟥',
            'Weak 🟧',
            'Fair 🟨',
            'Good 🟩',
            'Strong 🟦'
        ];
        strengthFeedback.textContent = `Strength: ${messages[score]}`;
    }

    function checkMatch() {
        if (confirmPassword.value.length === 0) {
            matchFeedback.textContent = '';
            submitButton.disabled = false;
            return;
        }
        if (newPassword.value === confirmPassword.value) {
            matchFeedback.textContent = '✅ Passwords match';
            matchFeedback.classList.remove('text-danger');
            matchFeedback.classList.add('text-success');
            submitButton.disabled = false;
        } else {
            matchFeedback.textContent = '❌ Passwords do not match';
            matchFeedback.classList.remove('text-success');
            matchFeedback.classList.add('text-danger');
            submitButton.disabled = true;
        }
    }

    newPassword.addEventListener('input', () => {
        updateStrengthMeter();
        checkMatch();
    });

    confirmPassword.addEventListener('input', checkMatch);
});
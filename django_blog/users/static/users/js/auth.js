// Initialize form validation and enhance UX
document.addEventListener('DOMContentLoaded', function() {
    // Add floating labels
    const formGroups = document.querySelectorAll('.form-group');
    formGroups.forEach(group => {
        const input = group.querySelector('input, textarea');
        if (input) {
            // Add active class if input has value
            if (input.value) {
                input.parentElement.classList.add('active');
            }
            
            // Add/remove active class on focus/blur
            input.addEventListener('focus', function() {
                this.parentElement.classList.add('active');
            });
            
            input.addEventListener('blur', function() {
                if (!this.value) {
                    this.parentElement.classList.remove('active');
                }
            });
        }
    });

    // Password strength indicator
    const passwordInput = document.querySelector('input[type="password"]');
    if (passwordInput) {
        passwordInput.addEventListener('input', function() {
            const strengthMeter = document.getElementById('password-strength');
            if (strengthMeter) {
                const strength = checkPasswordStrength(this.value);
                updateStrengthMeter(strengthMeter, strength);
            }
        });
    }
});

function checkPasswordStrength(password) {
    let strength = 0;
    
    // Length check
    if (password.length >= 8) strength++;
    
    // Contains numbers
    if (/\d/.test(password)) strength++;
    
    // Contains letters
    if (/[a-zA-Z]/.test(password)) strength++;
    
    // Contains special characters
    if (/[^A-Za-z0-9]/.test(password)) strength++;
    
    return Math.min(strength, 4); // Cap at 4
}

function updateStrengthMeter(meter, strength) {
    const strengthText = ['Very Weak', 'Weak', 'Fair', 'Good', 'Strong'];
    const strengthClass = ['very-weak', 'weak', 'fair', 'good', 'strong'];
    
    meter.textContent = strengthText[strength];
    meter.className = `strength-${strengthClass[strength]}`;
}

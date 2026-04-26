// Toggle Password Visibility with futuristic animation
function togglePassword() {
    const passwordField = document.getElementById('password');
    const toggleIcon = document.querySelector('.toggle-password');
    
    if (passwordField.type === "password") {
        passwordField.type = "text";
        toggleIcon.textContent = "🌌";
    } else {
        passwordField.type = "password";
        toggleIcon.textContent = "👁";
    }
}

// For Register page confirm password
function togglePasswordConfirm() {
    const confirmField = document.getElementById('confirm_password');
    const icons = document.querySelectorAll('.toggle-password');
    if (icons.length > 1) {
        const toggleIcon = icons[1];
        if (confirmField.type === "password") {
            confirmField.type = "text";
            toggleIcon.textContent = "🌌";
        } else {
            confirmField.type = "password";
            toggleIcon.textContent = "👁";
        }
    }
}

// OTP Verification with galactic effect
function verifyOTP() {
    const otpInput = document.getElementById('otp');
    if (!otpInput) return;

    const otpValue = otpInput.value.trim();
    
    if (otpValue.length === 6) {
        const btn = document.querySelector('.btn-verify');
        btn.textContent = "🔄 Verifying...";
        btn.style.background = "#22d3ee";
        
        setTimeout(() => {
            alert("✅ Neural Link Established!\n\nWelcome to the Secure System.");
            window.location.href = "/dashboard";
        }, 1200);
    } else {
        alert("⚠️ Invalid Neural Code. Please enter 6 digits.");
    }
}

// Add subtle glow effect on load
document.addEventListener('DOMContentLoaded', function() {
    const loginCard = document.querySelector('.login-card');
    if (loginCard) {
        loginCard.style.opacity = "0";
        setTimeout(() => {
            loginCard.style.transition = "opacity 1.2s ease";
            loginCard.style.opacity = "1";
        }, 300);
    }
});
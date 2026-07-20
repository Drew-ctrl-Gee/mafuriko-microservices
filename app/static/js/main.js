// Auto-hide flash messages after 5 seconds
setTimeout(() => {
    document.querySelectorAll('.flash').forEach(flash => {
        flash.style.animation = 'slideIn 0.3s ease reverse';
        setTimeout(() => flash.remove(), 300);
    });
}, 5000);
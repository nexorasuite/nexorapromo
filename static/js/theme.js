// Theme Toggle Script
(function() {
    const html = document.documentElement;
    const savedTheme = localStorage.getItem('theme');
    
    // Set initial theme
    if (savedTheme === 'dark' || (!savedTheme && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
        html.classList.add('dark');
    }
    
    // Update toggle button
    function updateToggleIcon() {
        const toggles = document.querySelectorAll('#theme-toggle, #header-theme-toggle');
        const isDark = html.classList.contains('dark');
        
        toggles.forEach(toggle => {
            const moonIcon = toggle.querySelector('.fa-moon');
            const sunIcon = toggle.querySelector('.fa-sun');
            
            if (moonIcon) {
                if (isDark) {
                    moonIcon.classList.add('hidden');
                    if (sunIcon) sunIcon.classList.remove('hidden');
                } else {
                    moonIcon.classList.remove('hidden');
                    if (sunIcon) sunIcon.classList.add('hidden');
                }
            }
        });
    }
    
    // Toggle theme
    document.addEventListener('click', (e) => {
        if (e.target.id === 'theme-toggle' || e.target.id === 'header-theme-toggle' || 
            e.target.closest('#theme-toggle') || e.target.closest('#header-theme-toggle')) {
            html.classList.toggle('dark');
            localStorage.setItem('theme', html.classList.contains('dark') ? 'dark' : 'light');
            updateToggleIcon();
        }
    });
    
    updateToggleIcon();
})();

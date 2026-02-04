// Theme Management
class ThemeManager {
    constructor() {
        this.loadTheme();
        this.setupThemeToggle();
    }

    loadTheme() {
        const savedTheme = localStorage.getItem('theme');
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        const isDark = savedTheme === 'dark' || (!savedTheme && prefersDark);
        
        if (isDark) {
            document.documentElement.classList.add('dark');
        }
    }

    setupThemeToggle() {
        const toggleButtons = document.querySelectorAll('#theme-toggle, #header-theme-toggle');
        toggleButtons.forEach(btn => {
            btn.addEventListener('click', () => this.toggleTheme());
        });
    }

    toggleTheme() {
        document.documentElement.classList.toggle('dark');
        const isDark = document.documentElement.classList.contains('dark');
        localStorage.setItem('theme', isDark ? 'dark' : 'light');
    }
}

// Notification/Toast System
class Notification {
    static show(message, type = 'info', duration = 3000) {
        const toast = document.createElement('div');
        toast.className = `animate-fade-in fixed bottom-6 right-6 px-6 py-4 rounded-lg text-white font-semibold shadow-lg max-w-sm z-50`;
        
        const colors = {
            success: 'bg-green-500',
            error: 'bg-red-500',
            warning: 'bg-yellow-500',
            info: 'bg-blue-500'
        };
        
        toast.classList.add(colors[type] || colors.info);
        toast.textContent = message;
        
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transition = 'opacity 0.3s ease';
            setTimeout(() => toast.remove(), 300);
        }, duration);
    }
}

// API Helper
class API {
    static async get(url) {
        return fetch(url).then(r => {
            if (!r.ok) throw new Error(`API Error: ${r.status}`);
            return r.json();
        });
    }

    static async post(url, data) {
        return fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        }).then(r => {
            if (!r.ok) throw new Error(`API Error: ${r.status}`);
            return r.json();
        });
    }

    static async formSubmit(url, formData) {
        return fetch(url, {
            method: 'POST',
            body: formData
        }).then(r => {
            if (!r.ok) throw new Error(`API Error: ${r.status}`);
            return r.json();
        });
    }

    static async delete(url) {
        return fetch(url, {
            method: 'DELETE'
        }).then(r => {
            if (!r.ok) throw new Error(`API Error: ${r.status}`);
            return r.json();
        });
    }
}

// Utility Functions
const Utils = {
    formatDate: (date) => {
        return new Date(date).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    },

    truncate: (str, len = 50) => {
        return str.length > len ? str.substring(0, len) + '...' : str;
    },

    debounce: (func, wait) => {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    showConfirm: (message) => {
        return confirm(message);
    }
};

// Initialize theme manager when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new ThemeManager();
});

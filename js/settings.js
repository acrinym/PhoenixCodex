/**
 * Settings Management for Phoenix Codex Web Application
 * Handles user preferences and application configuration
 */

class SettingsManager {
    constructor() {
        this.settings = this.loadSettings();
        this.defaultSettings = {
            theme: 'dark',
            autoSave: true,
            visualizationMode: '3d',
            fontSize: 'medium',
            showDebugInfo: false,
            maxResults: 100,
            animationSpeed: 1.0,
            enableTooltips: true
        };
    }

    /**
     * Load settings from localStorage
     */
    loadSettings() {
        try {
            const stored = localStorage.getItem('phoenixCodexSettings');
            return stored ? JSON.parse(stored) : {};
        } catch (error) {
            console.warn('Error loading settings:', error);
            return {};
        }
    }

    /**
     * Save settings to localStorage
     */
    saveSettings() {
        try {
            localStorage.setItem('phoenixCodexSettings', JSON.stringify(this.settings));
            this.dispatchSettingsChange();
        } catch (error) {
            console.error('Error saving settings:', error);
        }
    }

    /**
     * Get a setting value
     */
    get(key) {
        return this.settings.hasOwnProperty(key) 
            ? this.settings[key] 
            : this.defaultSettings[key];
    }

    /**
     * Set a setting value
     */
    set(key, value) {
        this.settings[key] = value;
        this.saveSettings();
    }

    /**
     * Reset all settings to defaults
     */
    reset() {
        this.settings = {};
        this.saveSettings();
    }

    /**
     * Get all settings with defaults applied
     */
    getAll() {
        return { ...this.defaultSettings, ...this.settings };
    }

    /**
     * Dispatch settings change event
     */
    dispatchSettingsChange() {
        const event = new CustomEvent('settingsChanged', {
            detail: this.getAll()
        });
        document.dispatchEvent(event);
    }

    /**
     * Apply theme to document
     */
    applyTheme() {
        const theme = this.get('theme');
        document.documentElement.setAttribute('data-theme', theme);
        document.body.className = document.body.className.replace(/theme-\w+/g, '');
        document.body.classList.add(`theme-${theme}`);
    }

    /**
     * Initialize settings UI
     */
    initializeUI() {
        this.applyTheme();
        
        // Listen for settings form submissions
        document.addEventListener('submit', (event) => {
            if (event.target.classList.contains('settings-form')) {
                event.preventDefault();
                this.handleFormSubmit(event.target);
            }
        });

        // Listen for theme toggle
        document.addEventListener('click', (event) => {
            if (event.target.classList.contains('theme-toggle')) {
                this.toggleTheme();
            }
        });
    }

    /**
     * Handle settings form submission
     */
    handleFormSubmit(form) {
        const formData = new FormData(form);
        
        for (const [key, value] of formData.entries()) {
            // Convert string values to appropriate types
            let processedValue = value;
            
            if (value === 'true') processedValue = true;
            else if (value === 'false') processedValue = false;
            else if (!isNaN(value) && value !== '') processedValue = Number(value);
            
            this.set(key, processedValue);
        }
        
        // Show success message
        this.showMessage('Settings saved successfully!', 'success');
    }

    /**
     * Toggle between light and dark theme
     */
    toggleTheme() {
        const currentTheme = this.get('theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        this.set('theme', newTheme);
        this.applyTheme();
    }

    /**
     * Show a message to the user
     */
    showMessage(message, type = 'info') {
        const messageElement = document.createElement('div');
        messageElement.className = `message message-${type}`;
        messageElement.textContent = message;
        
        // Style the message
        Object.assign(messageElement.style, {
            position: 'fixed',
            top: '20px',
            right: '20px',
            padding: '10px 20px',
            borderRadius: '4px',
            zIndex: '10000',
            opacity: '0',
            transition: 'opacity 0.3s ease'
        });
        
        // Add type-specific styling
        const styles = {
            success: { backgroundColor: '#28a745', color: 'white' },
            error: { backgroundColor: '#dc3545', color: 'white' },
            warning: { backgroundColor: '#ffc107', color: 'black' },
            info: { backgroundColor: '#17a2b8', color: 'white' }
        };
        
        Object.assign(messageElement.style, styles[type] || styles.info);
        
        document.body.appendChild(messageElement);
        
        // Animate in
        setTimeout(() => { messageElement.style.opacity = '1'; }, 10);
        
        // Remove after 3 seconds
        setTimeout(() => {
            messageElement.style.opacity = '0';
            setTimeout(() => {
                if (messageElement.parentNode) {
                    messageElement.parentNode.removeChild(messageElement);
                }
            }, 300);
        }, 3000);
    }
}

// Create global settings instance
window.PhoenixSettings = new SettingsManager();

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.PhoenixSettings.initializeUI();
    });
} else {
    window.PhoenixSettings.initializeUI();
}

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SettingsManager;
}
// Phoenix Codex - Main Application
import { VisualizationManager } from './visualization.js';
import { TimelineManager } from './timeline.js';
import { SearchManager } from './search.js';
import { SettingsManager } from './settings.js';
import { NotificationManager, DataManager } from './utils.js';

class PhoenixCodexApp {
    constructor() {
        this.currentTab = 'dashboard';
        this.data = [];
        this.isLoading = false;
        
        // Initialize managers
        this.visualizationManager = new VisualizationManager();
        this.timelineManager = new TimelineManager();
        this.searchManager = new SearchManager();
        this.settingsManager = new SettingsManager();
        this.notificationManager = new NotificationManager();
        this.dataManager = new DataManager();
        
        this.init();
    }
    
    async init() {
        try {
            this.showLoading(true);
            
            // Initialize event listeners
            this.initEventListeners();
            
            // Load sample data by default
            await this.loadSampleData();
            
            // Initialize dashboard
            this.updateDashboard();
            
            this.showLoading(false);
            this.notificationManager.show('Phoenix Codex loaded successfully!', 'success');
            
        } catch (error) {
            console.error('Failed to initialize Phoenix Codex:', error);
            this.notificationManager.show('Failed to initialize application', 'error');
            this.showLoading(false);
        }
    }
    
    initEventListeners() {
        // Tab navigation
        document.querySelectorAll('.nav-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const tab = e.currentTarget.dataset.tab;
                this.switchTab(tab);
            });
        });
        
        // Theme selector
        const themeSelector = document.getElementById('theme-selector');
        if (themeSelector) {
            themeSelector.addEventListener('change', (e) => {
                this.changeTheme(e.target.value);
            });
        }
        
        // Performance mode
        const performanceMode = document.getElementById('performance-mode');
        if (performanceMode) {
            performanceMode.addEventListener('change', (e) => {
                this.changePerformanceMode(e.target.value);
            });
        }
        
        // Animation toggle
        const animationToggle = document.getElementById('enable-animations');
        if (animationToggle) {
            animationToggle.addEventListener('change', (e) => {
                this.toggleAnimations(e.target.checked);
            });
        }
    }
    
    switchTab(tabName) {
        // Update navigation buttons
        document.querySelectorAll('.nav-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
        
        // Update tab content
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
        });
        document.getElementById(tabName).classList.add('active');
        
        this.currentTab = tabName;
        
        // Initialize tab-specific functionality
        this.initializeTab(tabName);
    }
    
    initializeTab(tabName) {
        switch (tabName) {
            case 'dashboard':
                this.updateDashboard();
                break;
            case 'visualization':
                this.visualizationManager.init();
                break;
            case 'timeline':
                this.timelineManager.init();
                break;
            case 'search':
                this.searchManager.init();
                break;
            case 'settings':
                this.settingsManager.init();
                break;
        }
    }
    
    async loadSampleData() {
        try {
            // Try to load sample data from the existing file
            const response = await fetch('sample_visualization_data.json');
            if (response.ok) {
                this.data = await response.json();
            } else {
                // Fallback to generated sample data
                this.data = this.generateSampleData();
            }
            
            this.dataManager.setData(this.data);
            this.notificationManager.show(`Loaded ${this.data.length} data entries`, 'success');
            
        } catch (error) {
            console.warn('Could not load sample data, generating fallback:', error);
            this.data = this.generateSampleData();
            this.dataManager.setData(this.data);
        }
    }
    
    generateSampleData() {
        const sampleData = [];
        const sources = ['Amanda', 'Phoenix', 'Dad', 'Mom', 'Alex', 'Emma', 'Mike'];
        const types = ['conversation', 'thought', 'memory', 'event'];
        const tags = ['love', 'music', 'travel', 'food', 'family', 'deep', 'casual', 'important'];
        
        const startDate = new Date('2024-01-01');
        const endDate = new Date('2024-12-31');
        
        for (let i = 0; i < 100; i++) {
            const date = new Date(startDate.getTime() + Math.random() * (endDate.getTime() - startDate.getTime()));
            const source = sources[Math.floor(Math.random() * sources.length)];
            const type = types[Math.floor(Math.random() * types.length)];
            const tagCount = Math.floor(Math.random() * 3) + 1;
            const itemTags = [];
            
            for (let j = 0; j < tagCount; j++) {
                const tag = tags[Math.floor(Math.random() * tags.length)];
                if (!itemTags.includes(tag)) {
                    itemTags.push(tag);
                }
            }
            
            sampleData.push({
                date: date.toISOString().split('T')[0],
                content: `${source} talked about ${itemTags[0]}. This is a sample conversation entry with some additional details. The conversation covered various topics and included multiple people.`,
                type: type,
                source: source,
                tags: itemTags
            });
        }
        
        return sampleData.sort((a, b) => new Date(a.date) - new Date(b.date));
    }
    
    updateDashboard() {
        if (!this.data || this.data.length === 0) return;
        
        // Update statistics
        const totalEntries = this.data.length;
        const uniqueSources = new Set(this.data.map(item => item.source)).size;
        const dates = this.data.map(item => new Date(item.date)).sort((a, b) => a - b);
        const dateRange = dates.length > 1 ? 
            `${dates[0].toLocaleDateString()} - ${dates[dates.length - 1].toLocaleDateString()}` : 
            dates[0]?.toLocaleDateString() || '-';
        const avgContentLength = Math.round(
            this.data.reduce((sum, item) => sum + item.content.length, 0) / totalEntries
        );
        
        document.getElementById('total-entries').textContent = totalEntries;
        document.getElementById('unique-sources').textContent = uniqueSources;
        document.getElementById('date-range').textContent = dateRange;
        document.getElementById('avg-content-length').textContent = avgContentLength;
        
        // Update charts
        this.updateContentTypesChart();
        this.updateTimelineChart();
        this.updateTagsCloud();
        
        // Update settings info
        document.getElementById('settings-data-count').textContent = totalEntries;
        document.getElementById('last-updated').textContent = new Date().toLocaleString();
    }
    
    updateContentTypesChart() {
        const canvas = document.getElementById('content-types-chart');
        if (!canvas) return;
        
        const ctx = canvas.getContext('2d');
        const typeCounts = {};
        
        this.data.forEach(item => {
            typeCounts[item.type] = (typeCounts[item.type] || 0) + 1;
        });
        
        const labels = Object.keys(typeCounts);
        const data = Object.values(typeCounts);
        const colors = [
            '#ff6b35', '#f7931e', '#ffd23f', '#2d5a27',
            '#4a7c59', '#6b8e23', '#ff8c42', '#ff6b6b'
        ];
        
        // Clear previous chart
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        // Draw pie chart
        const centerX = canvas.width / 2;
        const centerY = canvas.height / 2;
        const radius = Math.min(centerX, centerY) - 20;
        
        let currentAngle = 0;
        const total = data.reduce((sum, val) => sum + val, 0);
        
        data.forEach((value, index) => {
            const sliceAngle = (value / total) * 2 * Math.PI;
            
            ctx.beginPath();
            ctx.moveTo(centerX, centerY);
            ctx.arc(centerX, centerY, radius, currentAngle, currentAngle + sliceAngle);
            ctx.closePath();
            ctx.fillStyle = colors[index % colors.length];
            ctx.fill();
            
            // Draw label
            const labelAngle = currentAngle + sliceAngle / 2;
            const labelX = centerX + (radius + 20) * Math.cos(labelAngle);
            const labelY = centerY + (radius + 20) * Math.sin(labelAngle);
            
            ctx.fillStyle = '#2c1810';
            ctx.font = '12px Inter';
            ctx.textAlign = 'center';
            ctx.fillText(labels[index], labelX, labelY);
            
            currentAngle += sliceAngle;
        });
    }
    
    updateTimelineChart() {
        const canvas = document.getElementById('timeline-chart');
        if (!canvas) return;
        
        const ctx = canvas.getContext('2d');
        
        // Group data by month
        const monthlyData = {};
        this.data.forEach(item => {
            const month = item.date.substring(0, 7); // YYYY-MM
            monthlyData[month] = (monthlyData[month] || 0) + 1;
        });
        
        const months = Object.keys(monthlyData).sort();
        const counts = months.map(month => monthlyData[month]);
        
        // Clear canvas
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        if (months.length === 0) return;
        
        // Draw line chart
        const padding = 40;
        const chartWidth = canvas.width - 2 * padding;
        const chartHeight = canvas.height - 2 * padding;
        
        const maxCount = Math.max(...counts);
        const minCount = Math.min(...counts);
        const range = maxCount - minCount || 1;
        
        ctx.strokeStyle = '#ff6b35';
        ctx.lineWidth = 3;
        ctx.beginPath();
        
        months.forEach((month, index) => {
            const x = padding + (index / (months.length - 1)) * chartWidth;
            const y = canvas.height - padding - ((counts[index] - minCount) / range) * chartHeight;
            
            if (index === 0) {
                ctx.moveTo(x, y);
            } else {
                ctx.lineTo(x, y);
            }
        });
        
        ctx.stroke();
        
        // Draw points
        ctx.fillStyle = '#ff6b35';
        months.forEach((month, index) => {
            const x = padding + (index / (months.length - 1)) * chartWidth;
            const y = canvas.height - padding - ((counts[index] - minCount) / range) * chartHeight;
            
            ctx.beginPath();
            ctx.arc(x, y, 4, 0, 2 * Math.PI);
            ctx.fill();
        });
        
        // Draw labels
        ctx.fillStyle = '#2c1810';
        ctx.font = '10px Inter';
        ctx.textAlign = 'center';
        months.forEach((month, index) => {
            const x = padding + (index / (months.length - 1)) * chartWidth;
            const y = canvas.height - 10;
            ctx.fillText(month.substring(5), x, y); // Show only MM
        });
    }
    
    updateTagsCloud() {
        const container = document.getElementById('tags-cloud');
        if (!container) return;
        
        // Count tag frequencies
        const tagCounts = {};
        this.data.forEach(item => {
            item.tags.forEach(tag => {
                tagCounts[tag] = (tagCounts[tag] || 0) + 1;
            });
        });
        
        // Sort by frequency and take top 20
        const sortedTags = Object.entries(tagCounts)
            .sort(([,a], [,b]) => b - a)
            .slice(0, 20);
        
        // Clear container
        container.innerHTML = '';
        
        // Add tags
        sortedTags.forEach(([tag, count]) => {
            const tagElement = document.createElement('span');
            tagElement.className = 'tag';
            tagElement.textContent = `${tag} (${count})`;
            tagElement.style.fontSize = `${Math.max(10, Math.min(16, 10 + count * 2))}px`;
            tagElement.addEventListener('click', () => {
                this.searchManager.searchByTag(tag);
                this.switchTab('search');
            });
            container.appendChild(tagElement);
        });
    }
    
    changeTheme(theme) {
        document.body.className = `theme-${theme}`;
        this.notificationManager.show(`Theme changed to ${theme}`, 'success');
    }
    
    changePerformanceMode(mode) {
        // Update visualization performance settings
        this.visualizationManager.setPerformanceMode(mode);
        this.notificationManager.show(`Performance mode set to ${mode}`, 'success');
    }
    
    toggleAnimations(enabled) {
        // Update animation settings across all components
        this.visualizationManager.setAnimationsEnabled(enabled);
        this.timelineManager.setAnimationsEnabled(enabled);
        this.notificationManager.show(`Animations ${enabled ? 'enabled' : 'disabled'}`, 'success');
    }
    
    showLoading(show) {
        const overlay = document.getElementById('loading-overlay');
        if (overlay) {
            overlay.style.display = show ? 'flex' : 'none';
        }
        this.isLoading = show;
    }
    
    getData() {
        return this.data;
    }
    
    setData(newData) {
        this.data = newData;
        this.dataManager.setData(newData);
        this.updateDashboard();
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.phoenixCodexApp = new PhoenixCodexApp();
});

// Export for use in other modules
export { PhoenixCodexApp }; 
// Phoenix Codex - Timeline Module
import { DataManager } from './utils.js';

class TimelineManager {
    constructor() {
        this.data = [];
        this.filteredData = [];
        this.currentFilter = 'all';
        this.dateRange = { start: null, end: null };
        this.animationsEnabled = true;
        this.isInitialized = false;
        
        this.dataManager = new DataManager();
    }
    
    init() {
        if (this.isInitialized) return;
        
        this.data = this.dataManager.getData();
        this.filteredData = [...this.data];
        
        this.setupEventListeners();
        this.updateTimeline();
        
        this.isInitialized = true;
    }
    
    setupEventListeners() {
        // Date range picker
        const startDateInput = document.getElementById('start-date');
        const endDateInput = document.getElementById('end-date');
        const applyDateRangeBtn = document.getElementById('apply-date-range');
        
        if (startDateInput && endDateInput && applyDateRangeBtn) {
            applyDateRangeBtn.addEventListener('click', () => {
                this.applyDateRange();
            });
        }
        
        // Type filter
        const typeFilter = document.getElementById('timeline-type-filter');
        if (typeFilter) {
            typeFilter.addEventListener('change', (e) => {
                this.filterByType(e.target.value);
            });
        }
    }
    
    applyDateRange() {
        const startDateInput = document.getElementById('start-date');
        const endDateInput = document.getElementById('end-date');
        
        if (startDateInput && endDateInput) {
            const startDate = startDateInput.value ? new Date(startDateInput.value) : null;
            const endDate = endDateInput.value ? new Date(endDateInput.value) : null;
            
            this.dateRange = { start: startDate, end: endDate };
            this.updateTimeline();
        }
    }
    
    filterByType(type) {
        this.currentFilter = type;
        this.updateTimeline();
    }
    
    updateTimeline() {
        // Apply filters
        this.filteredData = this.data.filter(item => {
            // Type filter
            if (this.currentFilter !== 'all' && item.type !== this.currentFilter) {
                return false;
            }
            
            // Date range filter
            if (this.dateRange.start || this.dateRange.end) {
                const itemDate = new Date(item.date);
                
                if (this.dateRange.start && itemDate < this.dateRange.start) {
                    return false;
                }
                
                if (this.dateRange.end && itemDate > this.dateRange.end) {
                    return false;
                }
            }
            
            return true;
        });
        
        this.renderTimeline();
    }
    
    renderTimeline() {
        const container = document.getElementById('timeline-visualization');
        if (!container) return;
        
        // Clear container
        container.innerHTML = '';
        
        if (this.filteredData.length === 0) {
            container.innerHTML = `
                <div style="text-align: center; padding: 2rem; color: #666;">
                    <i class="fas fa-calendar-times" style="font-size: 3rem; margin-bottom: 1rem; opacity: 0.5;"></i>
                    <p>No data matches the current filters</p>
                </div>
            `;
            return;
        }
        
        // Sort by date
        const sortedData = this.filteredData.sort((a, b) => new Date(a.date) - new Date(b.date));
        
        // Create timeline
        const timeline = document.createElement('div');
        timeline.className = 'timeline';
        timeline.style.cssText = `
            position: relative;
            padding: 2rem 0;
            max-height: 600px;
            overflow-y: auto;
        `;
        
        // Add timeline line
        const timelineLine = document.createElement('div');
        timelineLine.style.cssText = `
            position: absolute;
            left: 50px;
            top: 0;
            bottom: 0;
            width: 2px;
            background: linear-gradient(to bottom, var(--primary), var(--secondary));
            border-radius: 1px;
        `;
        timeline.appendChild(timelineLine);
        
        // Create timeline items
        sortedData.forEach((item, index) => {
            const timelineItem = this.createTimelineItem(item, index);
            timeline.appendChild(timelineItem);
        });
        
        container.appendChild(timeline);
        
        // Add scroll animation if enabled
        if (this.animationsEnabled) {
            this.animateTimelineItems();
        }
    }
    
    createTimelineItem(item, index) {
        const timelineItem = document.createElement('div');
        timelineItem.className = 'timeline-item';
        timelineItem.style.cssText = `
            position: relative;
            margin: 2rem 0;
            padding-left: 80px;
            opacity: 0;
            transform: translateX(-20px);
            transition: all 0.5s ease;
        `;
        
        // Timeline dot
        const dot = document.createElement('div');
        dot.style.cssText = `
            position: absolute;
            left: 44px;
            top: 0;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: var(--primary);
            border: 3px solid white;
            box-shadow: 0 0 0 2px var(--primary);
            z-index: 2;
        `;
        timelineItem.appendChild(dot);
        
        // Content card
        const contentCard = document.createElement('div');
        contentCard.style.cssText = `
            background: white;
            border-radius: 8px;
            padding: 1rem;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            border-left: 4px solid var(--primary);
            transition: all 0.3s ease;
        `;
        
        // Header
        const header = document.createElement('div');
        header.style.cssText = `
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 0.5rem;
        `;
        
        const title = document.createElement('h4');
        title.textContent = item.source;
        title.style.cssText = `
            margin: 0;
            color: var(--dark);
            font-weight: 600;
        `;
        
        const date = document.createElement('span');
        date.textContent = new Date(item.date).toLocaleDateString();
        date.style.cssText = `
            font-size: 0.875rem;
            color: #666;
        `;
        
        header.appendChild(title);
        header.appendChild(date);
        contentCard.appendChild(header);
        
        // Type badge
        const typeBadge = document.createElement('span');
        typeBadge.textContent = item.type;
        typeBadge.style.cssText = `
            display: inline-block;
            padding: 0.25rem 0.5rem;
            background: var(--lighter);
            color: var(--primary);
            border-radius: 4px;
            font-size: 0.75rem;
            font-weight: 500;
            text-transform: uppercase;
            margin-bottom: 0.5rem;
        `;
        contentCard.appendChild(typeBadge);
        
        // Content
        const content = document.createElement('p');
        content.textContent = item.content;
        content.style.cssText = `
            margin: 0.5rem 0;
            color: var(--dark);
            line-height: 1.5;
        `;
        contentCard.appendChild(content);
        
        // Tags
        if (item.tags && item.tags.length > 0) {
            const tagsContainer = document.createElement('div');
            tagsContainer.style.cssText = `
                display: flex;
                gap: 0.25rem;
                flex-wrap: wrap;
                margin-top: 0.5rem;
            `;
            
            item.tags.forEach(tag => {
                const tagElement = document.createElement('span');
                tagElement.textContent = tag;
                tagElement.style.cssText = `
                    padding: 0.125rem 0.375rem;
                    background: var(--accent);
                    color: white;
                    border-radius: 12px;
                    font-size: 0.75rem;
                    font-weight: 500;
                `;
                tagsContainer.appendChild(tagElement);
            });
            
            contentCard.appendChild(tagsContainer);
        }
        
        // Hover effects
        contentCard.addEventListener('mouseenter', () => {
            contentCard.style.transform = 'translateY(-2px)';
            contentCard.style.boxShadow = '0 4px 16px rgba(0, 0, 0, 0.15)';
        });
        
        contentCard.addEventListener('mouseleave', () => {
            contentCard.style.transform = 'translateY(0)';
            contentCard.style.boxShadow = '0 2px 8px rgba(0, 0, 0, 0.1)';
        });
        
        timelineItem.appendChild(contentCard);
        
        return timelineItem;
    }
    
    animateTimelineItems() {
        const timelineItems = document.querySelectorAll('.timeline-item');
        
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateX(0)';
                }
            });
        }, {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        });
        
        timelineItems.forEach(item => {
            observer.observe(item);
        });
    }
    
    setAnimationsEnabled(enabled) {
        this.animationsEnabled = enabled;
    }
    
    getFilteredData() {
        return this.filteredData;
    }
    
    getStatistics() {
        const totalItems = this.filteredData.length;
        const typeCounts = {};
        const sourceCounts = {};
        const tagCounts = {};
        
        this.filteredData.forEach(item => {
            // Type counts
            typeCounts[item.type] = (typeCounts[item.type] || 0) + 1;
            
            // Source counts
            sourceCounts[item.source] = (sourceCounts[item.source] || 0) + 1;
            
            // Tag counts
            item.tags.forEach(tag => {
                tagCounts[tag] = (tagCounts[tag] || 0) + 1;
            });
        });
        
        return {
            totalItems,
            typeCounts,
            sourceCounts,
            tagCounts
        };
    }
}

export { TimelineManager }; 
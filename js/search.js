// Phoenix Codex - Search Module
import { DataManager } from './utils.js';

class SearchManager {
    constructor() {
        this.data = [];
        this.searchResults = [];
        this.currentPage = 1;
        this.itemsPerPage = 10;
        this.searchOptions = {
            semantic: false,
            caseSensitive: false,
            includeTags: true
        };
        this.isInitialized = false;
        
        this.dataManager = new DataManager();
    }
    
    init() {
        if (this.isInitialized) return;
        
        this.data = this.dataManager.getData();
        this.setupEventListeners();
        
        this.isInitialized = true;
    }
    
    setupEventListeners() {
        // Search button
        const searchBtn = document.getElementById('search-btn');
        const searchInput = document.getElementById('search-query');
        
        if (searchBtn && searchInput) {
            searchBtn.addEventListener('click', () => {
                this.performSearch();
            });
            
            searchInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.performSearch();
                }
            });
        }
        
        // Search options
        const semanticSearch = document.getElementById('semantic-search');
        const caseSensitive = document.getElementById('case-sensitive');
        const includeTags = document.getElementById('include-tags');
        
        if (semanticSearch) {
            semanticSearch.addEventListener('change', (e) => {
                this.searchOptions.semantic = e.target.checked;
            });
        }
        
        if (caseSensitive) {
            caseSensitive.addEventListener('change', (e) => {
                this.searchOptions.caseSensitive = e.target.checked;
            });
        }
        
        if (includeTags) {
            includeTags.addEventListener('change', (e) => {
                this.searchOptions.includeTags = e.target.checked;
            });
        }
    }
    
    performSearch() {
        const searchInput = document.getElementById('search-query');
        if (!searchInput) return;
        
        const query = searchInput.value.trim();
        if (!query) {
            this.showNoResults('Please enter a search query');
            return;
        }
        
        this.searchResults = this.searchData(query);
        this.currentPage = 1;
        this.displayResults();
    }
    
    searchData(query) {
        const results = [];
        const searchTerms = this.searchOptions.caseSensitive ? 
            [query] : 
            query.toLowerCase().split(' ').filter(term => term.length > 0);
        
        this.data.forEach((item, index) => {
            let score = 0;
            let matchedFields = [];
            
            // Search in content
            const content = this.searchOptions.caseSensitive ? 
                item.content : 
                item.content.toLowerCase();
            
            searchTerms.forEach(term => {
                if (content.includes(term)) {
                    score += 10;
                    matchedFields.push('content');
                }
            });
            
            // Search in source
            const source = this.searchOptions.caseSensitive ? 
                item.source : 
                item.source.toLowerCase();
            
            searchTerms.forEach(term => {
                if (source.includes(term)) {
                    score += 5;
                    matchedFields.push('source');
                }
            });
            
            // Search in type
            const type = this.searchOptions.caseSensitive ? 
                item.type : 
                item.type.toLowerCase();
            
            searchTerms.forEach(term => {
                if (type.includes(term)) {
                    score += 3;
                    matchedFields.push('type');
                }
            });
            
            // Search in tags if enabled
            if (this.searchOptions.includeTags && item.tags) {
                item.tags.forEach(tag => {
                    const tagLower = this.searchOptions.caseSensitive ? tag : tag.toLowerCase();
                    searchTerms.forEach(term => {
                        if (tagLower.includes(term)) {
                            score += 2;
                            matchedFields.push('tags');
                        }
                    });
                });
            }
            
            // Semantic search (simple keyword expansion)
            if (this.searchOptions.semantic) {
                score += this.semanticSearch(item, searchTerms);
            }
            
            if (score > 0) {
                results.push({
                    item,
                    score,
                    matchedFields: [...new Set(matchedFields)],
                    index
                });
            }
        });
        
        // Sort by score (highest first)
        results.sort((a, b) => b.score - a.score);
        
        return results;
    }
    
    semanticSearch(item, searchTerms) {
        let semanticScore = 0;
        
        // Simple semantic relationships
        const semanticMap = {
            'love': ['heart', 'romance', 'affection', 'care'],
            'music': ['song', 'melody', 'rhythm', 'sound'],
            'travel': ['journey', 'trip', 'adventure', 'explore'],
            'food': ['meal', 'cooking', 'dining', 'cuisine'],
            'family': ['parent', 'child', 'sibling', 'relative'],
            'work': ['job', 'career', 'profession', 'business'],
            'friend': ['companion', 'buddy', 'pal', 'mate'],
            'home': ['house', 'residence', 'dwelling', 'living'],
            'school': ['education', 'learning', 'study', 'academic'],
            'health': ['wellness', 'fitness', 'medical', 'exercise']
        };
        
        searchTerms.forEach(term => {
            Object.entries(semanticMap).forEach(([key, related]) => {
                if (term.includes(key) || related.some(word => term.includes(word))) {
                    // Check if item content contains related terms
                    const content = item.content.toLowerCase();
                    related.forEach(relatedTerm => {
                        if (content.includes(relatedTerm)) {
                            semanticScore += 1;
                        }
                    });
                }
            });
        });
        
        return semanticScore;
    }
    
    searchByTag(tag) {
        const searchInput = document.getElementById('search-query');
        if (searchInput) {
            searchInput.value = tag;
        }
        this.searchOptions.includeTags = true;
        this.performSearch();
    }
    
    displayResults() {
        const container = document.getElementById('results-container');
        const paginationContainer = document.getElementById('results-pagination');
        
        if (!container) return;
        
        if (this.searchResults.length === 0) {
            this.showNoResults('No results found');
            return;
        }
        
        // Calculate pagination
        const totalPages = Math.ceil(this.searchResults.length / this.itemsPerPage);
        const startIndex = (this.currentPage - 1) * this.itemsPerPage;
        const endIndex = startIndex + this.itemsPerPage;
        const pageResults = this.searchResults.slice(startIndex, endIndex);
        
        // Clear container
        container.innerHTML = '';
        
        // Add results count
        const resultsCount = document.createElement('div');
        resultsCount.style.cssText = `
            margin-bottom: 1rem;
            color: var(--dark);
            font-weight: 500;
        `;
        resultsCount.textContent = `Found ${this.searchResults.length} result${this.searchResults.length !== 1 ? 's' : ''}`;
        container.appendChild(resultsCount);
        
        // Create result items
        pageResults.forEach(result => {
            const resultElement = this.createResultItem(result);
            container.appendChild(resultElement);
        });
        
        // Create pagination
        if (totalPages > 1) {
            this.createPagination(paginationContainer, totalPages);
        } else {
            paginationContainer.innerHTML = '';
        }
    }
    
    createResultItem(result) {
        const resultDiv = document.createElement('div');
        resultDiv.className = 'result-item';
        
        const header = document.createElement('div');
        header.className = 'result-header';
        
        const title = document.createElement('div');
        title.className = 'result-title';
        title.textContent = result.item.source;
        
        const meta = document.createElement('div');
        meta.className = 'result-meta';
        meta.textContent = `${result.item.type} • ${new Date(result.item.date).toLocaleDateString()} • Score: ${result.score}`;
        
        header.appendChild(title);
        header.appendChild(meta);
        resultDiv.appendChild(header);
        
        const content = document.createElement('div');
        content.className = 'result-content';
        
        // Highlight matched terms
        let highlightedContent = result.item.content;
        if (!this.searchOptions.caseSensitive) {
            const searchInput = document.getElementById('search-query');
            if (searchInput) {
                const query = searchInput.value.toLowerCase();
                const regex = new RegExp(`(${query.split(' ').join('|')})`, 'gi');
                highlightedContent = result.item.content.replace(regex, '<mark>$1</mark>');
            }
        }
        
        content.innerHTML = highlightedContent;
        resultDiv.appendChild(content);
        
        // Add matched fields indicator
        if (result.matchedFields.length > 0) {
            const fieldsDiv = document.createElement('div');
            fieldsDiv.style.cssText = `
                margin-top: 0.5rem;
                font-size: 0.75rem;
                color: var(--primary);
            `;
            fieldsDiv.textContent = `Matched in: ${result.matchedFields.join(', ')}`;
            resultDiv.appendChild(fieldsDiv);
        }
        
        // Add tags
        if (result.item.tags && result.item.tags.length > 0) {
            const tagsDiv = document.createElement('div');
            tagsDiv.className = 'result-tags';
            
            result.item.tags.forEach(tag => {
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
                tagsDiv.appendChild(tagElement);
            });
            
            resultDiv.appendChild(tagsDiv);
        }
        
        return resultDiv;
    }
    
    createPagination(container, totalPages) {
        container.innerHTML = '';
        
        const pagination = document.createElement('div');
        pagination.className = 'pagination';
        
        // Previous button
        const prevBtn = document.createElement('button');
        prevBtn.className = 'pagination-btn';
        prevBtn.textContent = '← Previous';
        prevBtn.disabled = this.currentPage === 1;
        prevBtn.addEventListener('click', () => {
            if (this.currentPage > 1) {
                this.currentPage--;
                this.displayResults();
            }
        });
        pagination.appendChild(prevBtn);
        
        // Page numbers
        const maxVisiblePages = 5;
        let startPage = Math.max(1, this.currentPage - Math.floor(maxVisiblePages / 2));
        let endPage = Math.min(totalPages, startPage + maxVisiblePages - 1);
        
        if (endPage - startPage + 1 < maxVisiblePages) {
            startPage = Math.max(1, endPage - maxVisiblePages + 1);
        }
        
        for (let i = startPage; i <= endPage; i++) {
            const pageBtn = document.createElement('button');
            pageBtn.className = 'pagination-btn';
            pageBtn.textContent = i;
            pageBtn.classList.toggle('active', i === this.currentPage);
            pageBtn.addEventListener('click', () => {
                this.currentPage = i;
                this.displayResults();
            });
            pagination.appendChild(pageBtn);
        }
        
        // Next button
        const nextBtn = document.createElement('button');
        nextBtn.className = 'pagination-btn';
        nextBtn.textContent = 'Next →';
        nextBtn.disabled = this.currentPage === totalPages;
        nextBtn.addEventListener('click', () => {
            if (this.currentPage < totalPages) {
                this.currentPage++;
                this.displayResults();
            }
        });
        pagination.appendChild(nextBtn);
        
        container.appendChild(pagination);
    }
    
    showNoResults(message) {
        const container = document.getElementById('results-container');
        const paginationContainer = document.getElementById('results-pagination');
        
        if (container) {
            container.innerHTML = `
                <div style="text-align: center; padding: 2rem; color: #666;">
                    <i class="fas fa-search" style="font-size: 3rem; margin-bottom: 1rem; opacity: 0.5;"></i>
                    <p>${message}</p>
                </div>
            `;
        }
        
        if (paginationContainer) {
            paginationContainer.innerHTML = '';
        }
    }
    
    getSearchStatistics() {
        return {
            totalResults: this.searchResults.length,
            currentPage: this.currentPage,
            itemsPerPage: this.itemsPerPage,
            totalPages: Math.ceil(this.searchResults.length / this.itemsPerPage)
        };
    }
    
    exportResults(format = 'json') {
        if (this.searchResults.length === 0) {
            return null;
        }
        
        const exportData = this.searchResults.map(result => ({
            ...result.item,
            searchScore: result.score,
            matchedFields: result.matchedFields
        }));
        
        if (format === 'json') {
            return JSON.stringify(exportData, null, 2);
        } else if (format === 'csv') {
            return this.convertToCSV(exportData);
        }
        
        return null;
    }
    
    convertToCSV(data) {
        if (data.length === 0) return '';
        
        const headers = ['date', 'source', 'type', 'content', 'tags', 'searchScore', 'matchedFields'];
        const csvRows = [headers.join(',')];
        
        data.forEach(item => {
            const row = headers.map(header => {
                let value = item[header];
                if (Array.isArray(value)) {
                    value = value.join(';');
                }
                return `"${String(value).replace(/"/g, '""')}"`;
            });
            csvRows.push(row.join(','));
        });
        
        return csvRows.join('\n');
    }
}

export { SearchManager }; 
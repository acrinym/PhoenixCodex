"""
Visualization Tools for AmandaMap and Phoenix Codex
Comprehensive visualization system with multiple chart types and interactive features
"""

import json
import re
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import networkx as nx
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
import seaborn as sns
from dataclasses import dataclass
import threading
import queue

# Set style for better looking plots
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

@dataclass
class VisualizationConfig:
    """Configuration for visualization settings"""
    theme: str = "light"
    color_palette: str = "husl"
    figure_size: Tuple[int, int] = (12, 8)
    dpi: int = 100
    animation_speed: float = 0.1
    auto_refresh: bool = True
    refresh_interval: int = 30  # seconds

class TimelineVisualizer:
    """Timeline visualization for events and conversations"""
    
    def __init__(self, config: VisualizationConfig = None):
        self.config = config or VisualizationConfig()
        self.data = []
        self.fig = None
        self.ax = None
        
    def load_data(self, data: List[Dict]):
        """Load timeline data"""
        self.data = []
        for item in data:
            if 'date' in item and 'content' in item:
                try:
                    date = datetime.fromisoformat(item['date'].replace('Z', '+00:00'))
                    self.data.append({
                        'date': date,
                        'content': item['content'],
                        'type': item.get('type', 'event'),
                        'source': item.get('source', 'unknown'),
                        'tags': item.get('tags', [])
                    })
                except (ValueError, TypeError):
                    continue
        self.data.sort(key=lambda x: x['date'])
        
    def create_timeline(self, figsize: Tuple[int, int] = None) -> Figure:
        """Create a timeline visualization"""
        if not self.data:
            raise ValueError("No data loaded for timeline visualization")
            
        figsize = figsize or self.config.figure_size
        self.fig, self.ax = plt.subplots(figsize=figsize, dpi=self.config.dpi)
        
        # Group by type
        type_groups = defaultdict(list)
        for item in self.data:
            type_groups[item['type']].append(item)
            
        colors = plt.cm.Set3(np.linspace(0, 1, len(type_groups)))
        
        for i, (event_type, events) in enumerate(type_groups.items()):
            dates = [event['date'] for event in events]
            y_positions = [i] * len(dates)
            
            self.ax.scatter(dates, y_positions, 
                           c=[colors[i]], 
                           s=100, 
                           alpha=0.7, 
                           label=event_type,
                           edgecolors='black',
                           linewidth=1)
            
            # Add text labels for important events
            for event in events:
                if len(event['content']) > 50:
                    content_preview = event['content'][:50] + "..."
                else:
                    content_preview = event['content']
                    
                self.ax.annotate(content_preview,
                                xy=(event['date'], i),
                                xytext=(10, 10),
                                textcoords='offset points',
                                fontsize=8,
                                bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8),
                                arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))
        
        self.ax.set_title('AmandaMap & Phoenix Codex Timeline', fontsize=16, fontweight='bold')
        self.ax.set_xlabel('Date', fontsize=12)
        self.ax.set_ylabel('Event Type', fontsize=12)
        self.ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        self.ax.grid(True, alpha=0.3)
        
        # Format x-axis dates
        self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        self.ax.xaxis.set_major_locator(mdates.MonthLocator())
        plt.setp(self.ax.xaxis.get_majorticklabels(), rotation=45)
        
        plt.tight_layout()
        return self.fig

class RelationshipGraphVisualizer:
    """Network graph visualization for relationships and connections"""
    
    def __init__(self, config: VisualizationConfig = None):
        self.config = config or VisualizationConfig()
        self.graph = nx.Graph()
        self.pos = None
        
    def build_graph_from_data(self, data: List[Dict]):
        """Build network graph from data"""
        self.graph.clear()
        
        # Extract entities and relationships
        entities = set()
        relationships = []
        
        for item in data:
            content = item.get('content', '')
            source = item.get('source', 'unknown')
            
            # Extract names/entities using regex
            names = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', content)
            entities.update(names)
            entities.add(source)
            
            # Create relationships
            for name in names:
                if name != source:
                    relationships.append((source, name))
        
        # Add nodes and edges
        for entity in entities:
            self.graph.add_node(entity, size=len([e for e in entities if e == entity]))
            
        for rel in relationships:
            if self.graph.has_edge(rel[0], rel[1]):
                self.graph[rel[0]][rel[1]]['weight'] += 1
            else:
                self.graph.add_edge(rel[0], rel[1], weight=1)
                
    def create_network_graph(self, figsize: Tuple[int, int] = None) -> Figure:
        """Create network graph visualization"""
        if not self.graph.nodes():
            raise ValueError("No graph data available")
            
        figsize = figsize or self.config.figure_size
        fig, ax = plt.subplots(figsize=figsize, dpi=self.config.dpi)
        
        # Calculate node sizes based on degree
        node_sizes = [self.graph.degree(node) * 100 for node in self.graph.nodes()]
        
        # Calculate edge weights
        edge_weights = [self.graph[u][v]['weight'] for u, v in self.graph.edges()]
        
        # Position nodes using spring layout
        self.pos = nx.spring_layout(self.graph, k=1, iterations=50)
        
        # Draw the graph
        nx.draw(self.graph, self.pos,
                node_color='lightblue',
                node_size=node_sizes,
                width=edge_weights,
                edge_color='gray',
                with_labels=True,
                font_size=8,
                font_weight='bold',
                alpha=0.7)
        
        ax.set_title('Relationship Network Graph', fontsize=16, fontweight='bold')
        plt.tight_layout()
        return fig

class ContentAnalysisVisualizer:
    """Content analysis and pattern visualization"""
    
    def __init__(self, config: VisualizationConfig = None):
        self.config = config or VisualizationConfig()
        
    def analyze_content_patterns(self, data: List[Dict]) -> Dict:
        """Analyze content patterns"""
        analysis = {
            'word_frequency': Counter(),
            'topic_distribution': defaultdict(int),
            'sentiment_trends': [],
            'content_lengths': [],
            'time_distribution': defaultdict(int)
        }
        
        for item in data:
            content = item.get('content', '')
            date = item.get('date', '')
            source = item.get('source', 'unknown')
            
            # Word frequency
            words = re.findall(r'\b\w+\b', content.lower())
            analysis['word_frequency'].update(words)
            
            # Content length
            analysis['content_lengths'].append(len(content))
            
            # Time distribution
            if date:
                try:
                    dt = datetime.fromisoformat(date.replace('Z', '+00:00'))
                    hour = dt.hour
                    analysis['time_distribution'][hour] += 1
                except:
                    pass
                    
            # Topic distribution (simple keyword-based)
            topics = self._extract_topics(content)
            for topic in topics:
                analysis['topic_distribution'][topic] += 1
                
        return analysis
        
    def _extract_topics(self, content: str) -> List[str]:
        """Extract topics from content"""
        topics = []
        content_lower = content.lower()
        
        topic_keywords = {
            'love': ['love', 'heart', 'romance', 'relationship'],
            'work': ['work', 'job', 'career', 'business'],
            'family': ['family', 'mom', 'dad', 'parent'],
            'friends': ['friend', 'buddy', 'pal'],
            'hobbies': ['hobby', 'interest', 'passion'],
            'travel': ['travel', 'trip', 'vacation', 'journey'],
            'food': ['food', 'eat', 'cook', 'meal'],
            'music': ['music', 'song', 'band', 'concert'],
            'technology': ['tech', 'computer', 'phone', 'app']
        }
        
        for topic, keywords in topic_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                topics.append(topic)
                
        return topics
        
    def create_content_analysis_dashboard(self, data: List[Dict], figsize: Tuple[int, int] = None) -> Figure:
        """Create comprehensive content analysis dashboard"""
        analysis = self.analyze_content_patterns(data)
        figsize = figsize or self.config.figure_size
        
        fig = plt.figure(figsize=(figsize[0] * 1.5, figsize[1] * 1.2), dpi=self.config.dpi)
        
        # Create subplots
        gs = fig.add_gridspec(2, 3, hspace=0.3, wspace=0.3)
        
        # 1. Word frequency (top 10)
        ax1 = fig.add_subplot(gs[0, 0])
        top_words = dict(analysis['word_frequency'].most_common(10))
        ax1.bar(range(len(top_words)), list(top_words.values()))
        ax1.set_title('Top 10 Words')
        ax1.set_xticks(range(len(top_words)))
        ax1.set_xticklabels(list(top_words.keys()), rotation=45, ha='right')
        
        # 2. Topic distribution
        ax2 = fig.add_subplot(gs[0, 1])
        topics = dict(analysis['topic_distribution'])
        if topics:
            ax2.pie(list(topics.values()), labels=list(topics.keys()), autopct='%1.1f%%')
            ax2.set_title('Topic Distribution')
        
        # 3. Content length distribution
        ax3 = fig.add_subplot(gs[0, 2])
        ax3.hist(analysis['content_lengths'], bins=20, alpha=0.7, edgecolor='black')
        ax3.set_title('Content Length Distribution')
        ax3.set_xlabel('Length (characters)')
        ax3.set_ylabel('Frequency')
        
        # 4. Time distribution
        ax4 = fig.add_subplot(gs[1, :2])
        hours = sorted(analysis['time_distribution'].keys())
        counts = [analysis['time_distribution'][hour] for hour in hours]
        ax4.bar(hours, counts, alpha=0.7, edgecolor='black')
        ax4.set_title('Activity by Hour of Day')
        ax4.set_xlabel('Hour')
        ax4.set_ylabel('Number of Entries')
        ax4.set_xticks(range(0, 24, 2))
        
        # 5. Word cloud (simplified as bar chart)
        ax5 = fig.add_subplot(gs[1, 2])
        # Show word frequency as horizontal bars
        top_15_words = dict(analysis['word_frequency'].most_common(15))
        y_pos = range(len(top_15_words))
        ax5.barh(y_pos, list(top_15_words.values()))
        ax5.set_yticks(y_pos)
        ax5.set_yticklabels(list(top_15_words.keys()))
        ax5.set_title('Word Frequency')
        ax5.set_xlabel('Count')
        
        fig.suptitle('Content Analysis Dashboard', fontsize=16, fontweight='bold')
        plt.tight_layout()
        return fig

class InteractiveVisualizationApp:
    """Interactive visualization application with multiple tools"""
    
    def __init__(self, root: tk.Tk = None):
        self.root = root or tk.Tk()
        self.root.title("AmandaMap & Phoenix Codex Visualizer")
        self.root.geometry("1400x900")
        
        self.config = VisualizationConfig()
        self.data = []
        self.current_visualization = None
        self.canvas = None
        self.toolbar = None
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the user interface"""
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Control panel
        control_frame = ttk.LabelFrame(main_frame, text="Controls", padding=10)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Data loading
        ttk.Button(control_frame, text="Load Data", command=self.load_data).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Export Visualization", command=self.export_visualization).pack(side=tk.LEFT, padx=5)
        
        # Visualization type selector
        ttk.Label(control_frame, text="Visualization:").pack(side=tk.LEFT, padx=(20, 5))
        self.viz_type = tk.StringVar(value="timeline")
        viz_combo = ttk.Combobox(control_frame, textvariable=self.viz_type, 
                                 values=["timeline", "network", "content_analysis", "dashboard"],
                                 state="readonly", width=15)
        viz_combo.pack(side=tk.LEFT, padx=5)
        viz_combo.bind('<<ComboboxSelected>>', self.update_visualization)
        
        # Settings
        ttk.Button(control_frame, text="Settings", command=self.show_settings).pack(side=tk.RIGHT, padx=5)
        
        # Visualization area
        viz_frame = ttk.LabelFrame(main_frame, text="Visualization", padding=10)
        viz_frame.pack(fill=tk.BOTH, expand=True)
        
        # Canvas for matplotlib
        self.canvas_frame = ttk.Frame(viz_frame)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.pack(fill=tk.X, pady=(10, 0))
        
    def load_data(self):
        """Load data from file"""
        try:
            from tkinter import filedialog
            filename = filedialog.askopenfilename(
                title="Select data file",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            
            if filename:
                with open(filename, 'r', encoding='utf-8') as f:
                    self.data = json.load(f)
                    
                self.status_var.set(f"Loaded {len(self.data)} items from {filename}")
                self.update_visualization()
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load data: {str(e)}")
            
    def update_visualization(self, event=None):
        """Update the current visualization"""
        if not self.data:
            self.status_var.set("No data loaded")
            return
            
        try:
            # Clear previous visualization
            for widget in self.canvas_frame.winfo_children():
                widget.destroy()
                
            viz_type = self.viz_type.get()
            
            if viz_type == "timeline":
                visualizer = TimelineVisualizer(self.config)
                visualizer.load_data(self.data)
                fig = visualizer.create_timeline()
                
            elif viz_type == "network":
                visualizer = RelationshipGraphVisualizer(self.config)
                visualizer.build_graph_from_data(self.data)
                fig = visualizer.create_network_graph()
                
            elif viz_type == "content_analysis":
                visualizer = ContentAnalysisVisualizer(self.config)
                fig = visualizer.create_content_analysis_dashboard(self.data)
                
            elif viz_type == "dashboard":
                fig = self.create_comprehensive_dashboard()
                
            else:
                raise ValueError(f"Unknown visualization type: {viz_type}")
                
            # Create canvas
            self.canvas = FigureCanvasTkAgg(fig, self.canvas_frame)
            self.canvas.draw()
            self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
            # Add toolbar
            self.toolbar = NavigationToolbar2Tk(self.canvas, self.canvas_frame)
            self.toolbar.update()
            
            self.status_var.set(f"Visualization updated: {viz_type}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create visualization: {str(e)}")
            
    def create_comprehensive_dashboard(self) -> Figure:
        """Create a comprehensive dashboard with multiple visualizations"""
        fig = plt.figure(figsize=(16, 12), dpi=self.config.dpi)
        
        # Create subplots
        gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
        
        # Timeline
        ax1 = fig.add_subplot(gs[0, :2])
        timeline_viz = TimelineVisualizer(self.config)
        timeline_viz.load_data(self.data)
        timeline_viz.create_timeline()
        ax1.clear()
        ax1.plot([item['date'] for item in timeline_viz.data[:10]], 
                 range(len(timeline_viz.data[:10])), 'o-')
        ax1.set_title('Recent Timeline')
        
        # Network graph
        ax2 = fig.add_subplot(gs[0, 2])
        network_viz = RelationshipGraphVisualizer(self.config)
        network_viz.build_graph_from_data(self.data)
        if network_viz.graph.nodes():
            nx.draw(network_viz.graph, ax=ax2, with_labels=False, 
                   node_size=50, alpha=0.7)
        ax2.set_title('Relationship Network')
        
        # Content analysis
        ax3 = fig.add_subplot(gs[1, :])
        content_viz = ContentAnalysisVisualizer(self.config)
        analysis = content_viz.analyze_content_patterns(self.data)
        top_words = dict(analysis['word_frequency'].most_common(10))
        ax3.bar(range(len(top_words)), list(top_words.values()))
        ax3.set_title('Word Frequency')
        ax3.set_xticks(range(len(top_words)))
        ax3.set_xticklabels(list(top_words.keys()), rotation=45)
        
        # Statistics
        ax4 = fig.add_subplot(gs[2, :])
        stats_text = f"""
        Total Entries: {len(self.data)}
        Date Range: {min([item.get('date', '') for item in self.data if item.get('date')])} to {max([item.get('date', '') for item in self.data if item.get('date')])}
        Sources: {len(set(item.get('source', '') for item in self.data))}
        Average Content Length: {np.mean([len(item.get('content', '')) for item in self.data]):.1f} characters
        """
        ax4.text(0.1, 0.5, stats_text, transform=ax4.transAxes, 
                fontsize=12, verticalalignment='center')
        ax4.set_title('Statistics')
        ax4.axis('off')
        
        fig.suptitle('Comprehensive Dashboard', fontsize=16, fontweight='bold')
        plt.tight_layout()
        return fig
        
    def export_visualization(self):
        """Export current visualization"""
        if not self.canvas:
            messagebox.showwarning("Warning", "No visualization to export")
            return
            
        try:
            from tkinter import filedialog
            filename = filedialog.asksaveasfilename(
                title="Save visualization",
                defaultextension=".png",
                filetypes=[("PNG files", "*.png"), ("PDF files", "*.pdf"), ("All files", "*.*")]
            )
            
            if filename:
                self.canvas.figure.savefig(filename, dpi=300, bbox_inches='tight')
                self.status_var.set(f"Visualization saved to {filename}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export visualization: {str(e)}")
            
    def show_settings(self):
        """Show visualization settings dialog"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Visualization Settings")
        settings_window.geometry("400x300")
        
        # Settings controls
        ttk.Label(settings_window, text="Figure Size:").pack(pady=5)
        size_frame = ttk.Frame(settings_window)
        size_frame.pack(pady=5)
        
        width_var = tk.StringVar(value=str(self.config.figure_size[0]))
        height_var = tk.StringVar(value=str(self.config.figure_size[1]))
        
        ttk.Label(size_frame, text="Width:").pack(side=tk.LEFT)
        ttk.Entry(size_frame, textvariable=width_var, width=10).pack(side=tk.LEFT, padx=5)
        ttk.Label(size_frame, text="Height:").pack(side=tk.LEFT, padx=(10, 0))
        ttk.Entry(size_frame, textvariable=height_var, width=10).pack(side=tk.LEFT, padx=5)
        
        # Theme selection
        ttk.Label(settings_window, text="Theme:").pack(pady=5)
        theme_var = tk.StringVar(value=self.config.theme)
        theme_combo = ttk.Combobox(settings_window, textvariable=theme_var,
                                  values=["light", "dark"], state="readonly")
        theme_combo.pack(pady=5)
        
        # Apply button
        def apply_settings():
            try:
                self.config.figure_size = (int(width_var.get()), int(height_var.get()))
                self.config.theme = theme_var.get()
                self.update_visualization()
                settings_window.destroy()
            except ValueError:
                messagebox.showerror("Error", "Invalid figure size values")
                
        ttk.Button(settings_window, text="Apply", command=apply_settings).pack(pady=20)
        
    def run(self):
        """Run the visualization app"""
        self.root.mainloop()

def create_visualization_app(data: List[Dict] = None) -> InteractiveVisualizationApp:
    """Create and return a visualization app instance"""
    app = InteractiveVisualizationApp()
    if data:
        app.data = data
        app.update_visualization()
    return app

# Example usage functions
def visualize_timeline(data: List[Dict], save_path: str = None) -> Figure:
    """Create and optionally save a timeline visualization"""
    visualizer = TimelineVisualizer()
    visualizer.load_data(data)
    fig = visualizer.create_timeline()
    
    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches='tight')
        
    return fig

def visualize_relationships(data: List[Dict], save_path: str = None) -> Figure:
    """Create and optionally save a relationship network visualization"""
    visualizer = RelationshipGraphVisualizer()
    visualizer.build_graph_from_data(data)
    fig = visualizer.create_network_graph()
    
    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches='tight')
        
    return fig

def visualize_content_analysis(data: List[Dict], save_path: str = None) -> Figure:
    """Create and optionally save a content analysis visualization"""
    visualizer = ContentAnalysisVisualizer()
    fig = visualizer.create_content_analysis_dashboard(data)
    
    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches='tight')
        
    return fig

if __name__ == "__main__":
    # Example usage
    app = InteractiveVisualizationApp()
    app.run() 
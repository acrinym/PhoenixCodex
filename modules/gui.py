"""Enhanced GUI components for the GPT Export & Index tool with Avalonia features."""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import json
from pathlib import Path
from typing import Dict, Any, Optional

# Import our backported Avalonia features
from .advanced_indexer import AdvancedIndexer, SearchResult, SearchOptions
from .tagmap_generator import TagMapGenerator, TagMapEntry
from .progress_service import ProgressService, ConsoleProgressCallback
from .settings_service import SettingsService, ApplicationSettings

# Import existing GUI components
from .legacy_tool_v6_3 import App, apply_styles, theme_styles

class EnhancedApp(App):
    """Enhanced GUI with Avalonia backported features."""
    
    def __init__(self, master):
        super().__init__(master)
        
        # Initialize Avalonia backported services
        self.settings_service = SettingsService()
        self.progress_service = ProgressService()
        self.advanced_indexer = AdvancedIndexer()
        self.tagmap_generator = TagMapGenerator()
        
        # Add progress callback for GUI
        self.progress_callback = ConsoleProgressCallback()
        self.progress_service.add_callback(self.progress_callback)
        
        # Enhanced GUI state
        self.advanced_index_data = None
        self.tagmap_data = None
        
        # Create additional tabs for Avalonia features
        self.create_advanced_features_tabs()
        
    def create_advanced_features_tabs(self):
        """Create tabs for Avalonia backported features."""
        
        # Advanced Indexing Tab
        self.advanced_index_tab = ttk.Frame(self.notebook, style='TFrame', padding=10)
        self.notebook.add(self.advanced_index_tab, text='Advanced Indexing')
        self.create_advanced_index_tab_content(self.advanced_index_tab)
        
        # Tagmap Management Tab
        self.tagmap_tab = ttk.Frame(self.notebook, style='TFrame', padding=10)
        self.notebook.add(self.tagmap_tab, text='Tagmap Management')
        self.create_tagmap_tab_content(self.tagmap_tab)
        
        # Settings Management Tab
        self.settings_tab = ttk.Frame(self.notebook, style='TFrame', padding=10)
        self.notebook.add(self.settings_tab, text='Settings Management')
        self.create_settings_tab_content(self.settings_tab)
        
        # Progress Monitoring Tab
        self.progress_tab = ttk.Frame(self.notebook, style='TFrame', padding=10)
        self.notebook.add(self.progress_tab, text='Progress Monitor')
        self.create_progress_tab_content(self.progress_tab)
        
        # Visualization Tab
        self.visualization_tab = ttk.Frame(self.notebook, style='TFrame', padding=10)
        self.notebook.add(self.visualization_tab, text='📊 Visualization')
        self.create_visualization_tab_content(self.visualization_tab)
        
        # SMS Parser Tab
        self.sms_tab = ttk.Frame(self.notebook, style='TFrame', padding=10)
        self.notebook.add(self.sms_tab, text='📱 SMS Parser')
        self.create_sms_tab_content(self.sms_tab)
    
    def create_advanced_index_tab_content(self, parent_tab):
        """Create content for Advanced Indexing tab."""
        
        # Folder Selection
        folder_frame = ttk.LabelFrame(parent_tab, text="Folder Selection", padding="10")
        folder_frame.pack(fill=tk.X, pady=5)
        
        self.advanced_folder_var = tk.StringVar()
        ttk.Entry(folder_frame, textvariable=self.advanced_folder_var, width=50).pack(side=tk.LEFT, padx=5)
        ttk.Button(folder_frame, text="Browse", command=self.browse_advanced_folder).pack(side=tk.LEFT, padx=5)
        
        # Index Options
        options_frame = ttk.LabelFrame(parent_tab, text="Index Options", padding="10")
        options_frame.pack(fill=tk.X, pady=5)
        
        # Force rebuild option
        self.force_rebuild_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="Force Rebuild", variable=self.force_rebuild_var).pack(anchor=tk.W)
        
        # Index file selection
        index_file_frame = ttk.Frame(options_frame)
        index_file_frame.pack(fill=tk.X, pady=5)
        ttk.Label(index_file_frame, text="Index File:").pack(side=tk.LEFT)
        self.index_file_var = tk.StringVar()
        
        # Load last used index path
        last_index_path = self.settings_service.get_last_advanced_index_path()
        if last_index_path:
            self.index_file_var.set(last_index_path)
        
        ttk.Entry(index_file_frame, textvariable=self.index_file_var, width=40).pack(side=tk.LEFT, padx=5)
        ttk.Button(index_file_frame, text="Browse", command=self.browse_index_file).pack(side=tk.LEFT, padx=5)
        
        # Show last used path info
        if last_index_path:
            info_frame = ttk.Frame(options_frame)
            info_frame.pack(fill=tk.X, pady=2)
            ttk.Label(info_frame, text=f"Last used: {last_index_path}", 
                     font=("TkDefaultFont", 8), foreground="gray").pack(side=tk.LEFT)
        
        # Action Buttons
        button_frame = ttk.Frame(parent_tab)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="Build Advanced Index", 
                  command=self.build_advanced_index).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Load Index", 
                  command=self.load_advanced_index).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Show Index Stats", 
                  command=self.show_index_stats).pack(side=tk.LEFT, padx=5)
        
        # Search Section
        search_frame = ttk.LabelFrame(parent_tab, text="Advanced Search", padding="10")
        search_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Search query
        query_frame = ttk.Frame(search_frame)
        query_frame.pack(fill=tk.X, pady=5)
        ttk.Label(query_frame, text="Search Query:").pack(side=tk.LEFT)
        self.advanced_search_var = tk.StringVar()
        ttk.Entry(query_frame, textvariable=self.advanced_search_var, width=50).pack(side=tk.LEFT, padx=5)
        ttk.Button(query_frame, text="Search", command=self.advanced_search).pack(side=tk.LEFT, padx=5)
        
        # Search options
        search_options_frame = ttk.Frame(search_frame)
        search_options_frame.pack(fill=tk.X, pady=5)
        
        self.case_sensitive_advanced_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(search_options_frame, text="Case Sensitive", 
                       variable=self.case_sensitive_advanced_var).pack(side=tk.LEFT, padx=5)
        
        self.fuzzy_search_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(search_options_frame, text="Fuzzy Search", 
                       variable=self.fuzzy_search_var).pack(side=tk.LEFT, padx=5)
        
        # Search results
        results_frame = ttk.Frame(search_frame)
        results_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Create treeview for results
        columns = ('File', 'Score', 'Category', 'Preview')
        self.search_tree = ttk.Treeview(results_frame, columns=columns, show='headings')
        
        for col in columns:
            self.search_tree.heading(col, text=col)
            self.search_tree.column(col, width=150)
        
        scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.search_tree.yview)
        self.search_tree.configure(yscrollcommand=scrollbar.set)
        
        self.search_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def create_tagmap_tab_content(self, parent_tab):
        """Create content for Tagmap Management tab."""
        
        # Tagmap file selection
        file_frame = ttk.LabelFrame(parent_tab, text="Tagmap File", padding="10")
        file_frame.pack(fill=tk.X, pady=5)
        
        self.tagmap_file_var = tk.StringVar()
        ttk.Entry(file_frame, textvariable=self.tagmap_file_var, width=50).pack(side=tk.LEFT, padx=5)
        ttk.Button(file_frame, text="Browse", command=self.browse_tagmap_file).pack(side=tk.LEFT, padx=5)
        
        # Tagmap actions
        actions_frame = ttk.LabelFrame(parent_tab, text="Tagmap Actions", padding="10")
        actions_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(actions_frame, text="Generate Tagmap", 
                  command=self.generate_tagmap).pack(side=tk.LEFT, padx=5)
        ttk.Button(actions_frame, text="Load Tagmap", 
                  command=self.load_tagmap).pack(side=tk.LEFT, padx=5)
        ttk.Button(actions_frame, text="Update Tagmap", 
                  command=self.update_tagmap).pack(side=tk.LEFT, padx=5)
        ttk.Button(actions_frame, text="Show Tagmap Stats", 
                  command=self.show_tagmap_stats).pack(side=tk.LEFT, padx=5)
        
        # Tagmap entries display
        entries_frame = ttk.LabelFrame(parent_tab, text="Tagmap Entries", padding="10")
        entries_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Create treeview for tagmap entries
        columns = ('Title', 'Category', 'Date', 'Tags', 'Preview')
        self.tagmap_tree = ttk.Treeview(entries_frame, columns=columns, show='headings')
        
        for col in columns:
            self.tagmap_tree.heading(col, text=col)
            self.tagmap_tree.column(col, width=120)
        
        scrollbar = ttk.Scrollbar(entries_frame, orient=tk.VERTICAL, command=self.tagmap_tree.yview)
        self.tagmap_tree.configure(yscrollcommand=scrollbar.set)
        
        self.tagmap_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def create_settings_tab_content(self, parent_tab):
        """Create content for Settings Management tab."""
        
        # Settings display
        display_frame = ttk.LabelFrame(parent_tab, text="Current Settings", padding="10")
        display_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Create text widget for settings display
        self.settings_text = tk.Text(display_frame, height=20, width=80)
        scrollbar = ttk.Scrollbar(display_frame, orient=tk.VERTICAL, command=self.settings_text.yview)
        self.settings_text.configure(yscrollcommand=scrollbar.set)
        
        self.settings_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Settings actions
        actions_frame = ttk.Frame(parent_tab)
        actions_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(actions_frame, text="Show Settings", 
                  command=self.show_settings).pack(side=tk.LEFT, padx=5)
        ttk.Button(actions_frame, text="Reset to Defaults", 
                  command=self.reset_settings).pack(side=tk.LEFT, padx=5)
        ttk.Button(actions_frame, text="Export Settings", 
                  command=self.export_settings).pack(side=tk.LEFT, padx=5)
        ttk.Button(actions_frame, text="Import Settings", 
                  command=self.import_settings).pack(side=tk.LEFT, padx=5)
    
    def create_progress_tab_content(self, parent_tab):
        """Create content for Progress Monitor tab."""
        
        # Progress display
        progress_frame = ttk.LabelFrame(parent_tab, text="Operation Progress", padding="10")
        progress_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Progress bar
        self.progress_bar = ttk.Progressbar(progress_frame, mode='determinate')
        self.progress_bar.pack(fill=tk.X, pady=5)
        
        # Progress text
        self.progress_text = tk.Text(progress_frame, height=15, width=80)
        progress_scrollbar = ttk.Scrollbar(progress_frame, orient=tk.VERTICAL, command=self.progress_text.yview)
        self.progress_text.configure(yscrollcommand=progress_scrollbar.set)
        
        self.progress_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        progress_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Progress actions
        actions_frame = ttk.Frame(parent_tab)
        actions_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(actions_frame, text="Clear Progress", 
                  command=self.clear_progress).pack(side=tk.LEFT, padx=5)
        ttk.Button(actions_frame, text="Save Progress Log", 
                  command=self.save_progress_log).pack(side=tk.LEFT, padx=5)
    
    def create_visualization_tab_content(self, parent_tab):
        """Create content for Visualization tab."""
        
        # Data Selection Frame
        data_frame = ttk.LabelFrame(parent_tab, text="Data Selection", padding="10")
        data_frame.pack(fill=tk.X, pady=5)
        
        # Data file selection
        data_file_frame = ttk.Frame(data_frame)
        data_file_frame.pack(fill=tk.X, pady=5)
        ttk.Label(data_file_frame, text="Data File:").pack(side=tk.LEFT)
        self.visualization_data_var = tk.StringVar()
        ttk.Entry(data_file_frame, textvariable=self.visualization_data_var, width=50).pack(side=tk.LEFT, padx=5)
        ttk.Button(data_file_frame, text="Browse", command=self.browse_visualization_data).pack(side=tk.LEFT, padx=5)
        
        # Visualization Type Frame
        viz_type_frame = ttk.LabelFrame(parent_tab, text="Visualization Type", padding="10")
        viz_type_frame.pack(fill=tk.X, pady=5)
        
        # Visualization type selection
        self.viz_type_var = tk.StringVar(value="interactive")
        viz_types = [
            ("Interactive Dashboard", "interactive"),
            ("Timeline", "timeline"),
            ("Network Graph", "network"),
            ("Content Analysis", "content_analysis"),
            ("Comprehensive Dashboard", "dashboard")
        ]
        
        for text, value in viz_types:
            ttk.Radiobutton(viz_type_frame, text=text, variable=self.viz_type_var, 
                           value=value).pack(anchor=tk.W, pady=2)
        
        # Output Options Frame
        output_frame = ttk.LabelFrame(parent_tab, text="Output Options", padding="10")
        output_frame.pack(fill=tk.X, pady=5)
        
        # Save to file option
        self.save_viz_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(output_frame, text="Save to File", variable=self.save_viz_var, 
                       command=self.toggle_output_file).pack(anchor=tk.W)
        
        # Output file selection (initially disabled)
        self.output_file_frame = ttk.Frame(output_frame)
        self.output_file_var = tk.StringVar()
        ttk.Label(self.output_file_frame, text="Output File:").pack(side=tk.LEFT)
        ttk.Entry(self.output_file_frame, textvariable=self.output_file_var, width=40).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.output_file_frame, text="Browse", command=self.browse_output_file).pack(side=tk.LEFT, padx=5)
        
        # Action Buttons
        button_frame = ttk.Frame(parent_tab)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="🎨 Launch Visualization", 
                  command=self.launch_visualization).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="📊 Quick Preview", 
                  command=self.quick_preview).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="🔄 Refresh Data", 
                  command=self.refresh_visualization_data).pack(side=tk.LEFT, padx=5)
    
    def create_sms_tab_content(self, parent_tab):
        """Create content for SMS Parser tab."""
        
        # File Selection Frame
        file_frame = ttk.LabelFrame(parent_tab, text="SMS File Selection", padding="10")
        file_frame.pack(fill=tk.X, pady=5)
        
        # SMS file selection
        sms_file_frame = ttk.Frame(file_frame)
        sms_file_frame.pack(fill=tk.X, pady=5)
        ttk.Label(sms_file_frame, text="SMS XML File:").pack(side=tk.LEFT)
        self.sms_file_var = tk.StringVar()
        ttk.Entry(sms_file_frame, textvariable=self.sms_file_var, width=50).pack(side=tk.LEFT, padx=5)
        ttk.Button(sms_file_frame, text="Browse", command=self.browse_sms_file).pack(side=tk.LEFT, padx=5)
        
        # Output Options Frame
        output_frame = ttk.LabelFrame(parent_tab, text="Output Options", padding="10")
        output_frame.pack(fill=tk.X, pady=5)
        
        # Output directory
        output_dir_frame = ttk.Frame(output_frame)
        output_dir_frame.pack(fill=tk.X, pady=5)
        ttk.Label(output_dir_frame, text="Output Directory:").pack(side=tk.LEFT)
        self.sms_output_dir_var = tk.StringVar(value="data")
        ttk.Entry(output_dir_frame, textvariable=self.sms_output_dir_var, width=40).pack(side=tk.LEFT, padx=5)
        ttk.Button(output_dir_frame, text="Browse", command=self.browse_sms_output_dir).pack(side=tk.LEFT, padx=5)
        
        # Format selection
        format_frame = ttk.Frame(output_frame)
        format_frame.pack(fill=tk.X, pady=5)
        ttk.Label(format_frame, text="Output Format:").pack(side=tk.LEFT)
        self.sms_format_var = tk.StringVar(value="both")
        format_options = [
            ("AmandaMap Only", "amandamap"),
            ("Phoenix Codex Only", "phoenix"),
            ("Both Formats", "both")
        ]
        for text, value in format_options:
            ttk.Radiobutton(format_frame, text=text, variable=self.sms_format_var, 
                           value=value).pack(side=tk.LEFT, padx=10)
        
        # Append mode checkbox
        append_frame = ttk.Frame(output_frame)
        append_frame.pack(fill=tk.X, pady=5)
        self.sms_append_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(append_frame, text="Append to existing files (don't overwrite)", 
                       variable=self.sms_append_var).pack(side=tk.LEFT)
        
        # Action Buttons
        button_frame = ttk.Frame(parent_tab)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="📱 Parse SMS File", 
                  command=self.parse_sms_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="📊 Show Summary", 
                  command=self.show_sms_summary).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="🎨 Visualize Conversations", 
                  command=self.visualize_sms_conversations).pack(side=tk.LEFT, padx=5)
    
    # Advanced Indexing Methods
    def browse_advanced_folder(self):
        """Browse for folder to index."""
        folder = filedialog.askdirectory()
        if folder:
            self.advanced_folder_var.set(folder)
            # Auto-set index file name
            index_file = Path(folder) / "advanced_index.json"
            self.index_file_var.set(str(index_file))
    
    def browse_index_file(self):
        """Browse for index file."""
        filename = filedialog.askopenfilename(
            title="Select Index File",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            self.index_file_var.set(filename)
            # Save the selected path
            self.settings_service.set_last_advanced_index_path(filename)
    
    def build_advanced_index(self):
        """Build advanced index in background thread."""
        folder = self.advanced_folder_var.get()
        index_file = self.index_file_var.get()
        force_rebuild = self.force_rebuild_var.get()
        
        if not folder or not index_file:
            messagebox.showerror("Error", "Please select both folder and index file.")
            return
        
        def build_task():
            try:
                self.progress_service.start_operation("Building Advanced Index")
                
                # Build the index
                index_data = self.advanced_indexer.build_index(
                    Path(folder),
                    Path(index_file),
                    force_rebuild=force_rebuild,
                    progress_callback=self.update_progress
                )
                
                self.advanced_index_data = index_data
                self.progress_service.complete_operation("Advanced index built successfully")
                
                # Save the index path
                self.settings_service.set_last_advanced_index_path(index_file)
                
                # Update GUI in main thread
                self.master.after(0, lambda: self.update_status_bar(f"Advanced index built: {len(index_data.get('files', {}))} files"))
                
            except Exception as e:
                self.progress_service.complete_operation(f"Error building index: {e}")
                self.master.after(0, lambda: messagebox.showerror("Error", f"Failed to build index: {e}"))
        
        threading.Thread(target=build_task, daemon=True).start()
    
    def load_advanced_index(self):
        """Load existing advanced index."""
        index_file = self.index_file_var.get()
        
        if not index_file:
            messagebox.showerror("Error", "Please select an index file.")
            return
        
        try:
            self.advanced_index_data = self.advanced_indexer.load_index(Path(index_file))
            # Save the index path
            self.settings_service.set_last_advanced_index_path(index_file)
            self.update_status_bar(f"Loaded advanced index: {len(self.advanced_index_data.get('files', {}))} files")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load index: {e}")
    
    def show_index_stats(self):
        """Show advanced index statistics."""
        if not self.advanced_index_data:
            messagebox.showinfo("Info", "No index loaded. Please build or load an index first.")
            return
        
        stats = self.advanced_indexer.get_index_stats(self.advanced_index_data)
        
        stats_text = f"""Advanced Index Statistics:
        
Total Files: {stats.get('total_files', 0)}
Total Tokens: {stats.get('total_tokens', 0)}
Categories: {', '.join(stats.get('categories', []))}
Average File Size: {stats.get('avg_file_size', 0):.2f} KB
Index Size: {stats.get('index_size', 0):.2f} KB
        """
        
        messagebox.showinfo("Index Statistics", stats_text)
    
    def advanced_search(self):
        """Perform advanced search."""
        if not self.advanced_index_data:
            messagebox.showerror("Error", "No index loaded. Please build or load an index first.")
            return
        
        query = self.advanced_search_var.get()
        if not query:
            messagebox.showerror("Error", "Please enter a search query.")
            return
        
        # Clear previous results
        for item in self.search_tree.get_children():
            self.search_tree.delete(item)
        
        try:
            search_options = SearchOptions(
                case_sensitive=self.case_sensitive_advanced_var.get(),
                use_fuzzy=self.fuzzy_search_var.get(),
                max_results=50
            )
            
            results = self.advanced_indexer.search(
                self.advanced_index_data,
                query,
                search_options
            )
            
            # Populate results
            for result in results:
                self.search_tree.insert('', 'end', values=(
                    result.file_path,
                    f"{result.relevance_score:.3f}",
                    result.category,
                    result.preview[:50] + "..." if len(result.preview) > 50 else result.preview
                ))
            
            self.update_status_bar(f"Found {len(results)} results")
            
        except Exception as e:
            messagebox.showerror("Error", f"Search failed: {e}")
    
    # Tagmap Methods
    def browse_tagmap_file(self):
        """Browse for tagmap file."""
        filename = filedialog.askopenfilename(
            title="Select Tagmap File",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            self.tagmap_file_var.set(filename)
    
    def generate_tagmap(self):
        """Generate tagmap from folder."""
        folder = self.advanced_folder_var.get()
        tagmap_file = self.tagmap_file_var.get()
        
        if not folder or not tagmap_file:
            messagebox.showerror("Error", "Please select both folder and tagmap file.")
            return
        
        def generate_task():
            try:
                self.progress_service.start_operation("Generating Tagmap")
                
                entries = self.tagmap_generator.generate_tagmap(
                    Path(folder),
                    Path(tagmap_file)
                )
                
                self.tagmap_data = entries
                self.progress_service.complete_operation(f"Tagmap generated: {len(entries)} entries")
                
                # Update GUI in main thread
                self.master.after(0, lambda: self.populate_tagmap_tree())
                
            except Exception as e:
                self.progress_service.complete_operation(f"Error generating tagmap: {e}")
                self.master.after(0, lambda: messagebox.showerror("Error", f"Failed to generate tagmap: {e}"))
        
        threading.Thread(target=generate_task, daemon=True).start()
    
    def load_tagmap(self):
        """Load existing tagmap."""
        tagmap_file = self.tagmap_file_var.get()
        
        if not tagmap_file:
            messagebox.showerror("Error", "Please select a tagmap file.")
            return
        
        try:
            self.tagmap_data = self.tagmap_generator.load_tagmap(Path(tagmap_file))
            self.populate_tagmap_tree()
            self.update_status_bar(f"Loaded tagmap: {len(self.tagmap_data)} entries")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load tagmap: {e}")
    
    def update_tagmap(self):
        """Update existing tagmap."""
        if not self.tagmap_data:
            messagebox.showinfo("Info", "No tagmap loaded. Please load a tagmap first.")
            return
        
        tagmap_file = self.tagmap_file_var.get()
        
        if not tagmap_file:
            messagebox.showerror("Error", "Please select a tagmap file.")
            return
        
        try:
            updated_entries = self.tagmap_generator.update_tagmap(
                Path(tagmap_file),
                self.tagmap_data
            )
            
            self.tagmap_data = updated_entries
            self.populate_tagmap_tree()
            self.update_status_bar(f"Updated tagmap: {len(updated_entries)} entries")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update tagmap: {e}")
    
    def show_tagmap_stats(self):
        """Show tagmap statistics."""
        if not self.tagmap_data:
            messagebox.showinfo("Info", "No tagmap loaded. Please load a tagmap first.")
            return
        
        stats = self.tagmap_generator.get_tagmap_stats(self.tagmap_data)
        
        stats_text = f"""Tagmap Statistics:
        
Total Entries: {stats.get('total_entries', 0)}
Categories: {', '.join(stats.get('categories', []))}
Average Tags per Entry: {stats.get('avg_tags_per_entry', 0):.2f}
Cross-references: {stats.get('cross_references', 0)}
        """
        
        messagebox.showinfo("Tagmap Statistics", stats_text)
    
    def populate_tagmap_tree(self):
        """Populate tagmap tree with entries."""
        # Clear existing entries
        for item in self.tagmap_tree.get_children():
            self.tagmap_tree.delete(item)
        
        if not self.tagmap_data:
            return
        
        # Add entries
        for entry in self.tagmap_data:
            self.tagmap_tree.insert('', 'end', values=(
                entry.title,
                entry.category,
                entry.date,
                ', '.join(entry.tags),
                entry.preview[:50] + "..." if len(entry.preview) > 50 else entry.preview
            ))
    
    # Settings Methods
    def show_settings(self):
        """Display current settings."""
        settings = self.settings_service.get_all_settings()
        
        # Clear and populate settings text
        self.settings_text.delete(1.0, tk.END)
        
        # Add a special section for index paths at the top
        last_advanced_index = self.settings_service.get_last_advanced_index_path()
        last_regular_index = self.settings_service.get_last_index_path()
        
        index_paths_info = f"""=== INDEX PATHS ===
Last Advanced Index Path: {last_advanced_index or 'None'}
Last Regular Index Path: {last_regular_index or 'None'}

=== ALL SETTINGS ===
"""
        
        self.settings_text.insert(1.0, index_paths_info + json.dumps(settings, indent=2, default=str))
    
    def reset_settings(self):
        """Reset settings to defaults."""
        if messagebox.askyesno("Confirm", "Are you sure you want to reset all settings to defaults?"):
            self.settings_service.reset_to_defaults()
            messagebox.showinfo("Success", "Settings reset to defaults.")
            self.show_settings()
    
    def export_settings(self):
        """Export settings to file."""
        filename = filedialog.asksaveasfilename(
            title="Export Settings",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                self.settings_service.export_settings(Path(filename))
                messagebox.showinfo("Success", f"Settings exported to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export settings: {e}")
    
    def import_settings(self):
        """Import settings from file."""
        filename = filedialog.askopenfilename(
            title="Import Settings",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                self.settings_service.import_settings(Path(filename))
                messagebox.showinfo("Success", f"Settings imported from {filename}")
                self.show_settings()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to import settings: {e}")
    
    # Progress Methods
    def update_progress(self, message: str):
        """Update progress display."""
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"GUI update_progress called: {message}")
        
        # Update progress text area
        self.master.after(0, lambda: self.progress_text.insert(tk.END, f"{message}\n"))
        self.master.after(0, lambda: self.progress_text.see(tk.END))
        
        # Also update status bar for visibility
        self.master.after(0, lambda: self.update_status_bar(f"Progress: {message}"))
    
    def update_status_bar(self, message: str):
        """Update the status bar with a message."""
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Status bar update: {message}")
        # For now, just log the message since we don't have a status bar widget
        # In the future, this could update an actual status bar widget
    
    def clear_progress(self):
        """Clear progress display."""
        self.progress_text.delete(1.0, tk.END)
    
    def save_progress_log(self):
        """Save progress log to file."""
        filename = filedialog.asksaveasfilename(
            title="Save Progress Log",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(self.progress_text.get(1.0, tk.END))
                messagebox.showinfo("Success", f"Progress log saved to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save progress log: {e}")
    
    # Visualization Methods
    def browse_visualization_data(self):
        """Browse for visualization data file."""
        filename = filedialog.askopenfilename(
            title="Select Visualization Data File",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            self.visualization_data_var.set(filename)
    
    def browse_output_file(self):
        """Browse for output file."""
        filename = filedialog.asksaveasfilename(
            title="Select Output File",
            defaultextension=".png",
            filetypes=[
                ("PNG files", "*.png"),
                ("PDF files", "*.pdf"),
                ("All files", "*.*")
            ]
        )
        if filename:
            self.output_file_var.set(filename)
    
    def toggle_output_file(self):
        """Toggle output file frame visibility."""
        if self.save_viz_var.get():
            self.output_file_frame.pack(fill=tk.X, pady=5)
        else:
            self.output_file_frame.pack_forget()
    
    def launch_visualization(self):
        """Launch the selected visualization."""
        data_file = self.visualization_data_var.get()
        viz_type = self.viz_type_var.get()
        save_to_file = self.save_viz_var.get()
        output_file = self.output_file_var.get() if save_to_file else None
        
        if not data_file:
            messagebox.showerror("Error", "Please select a data file.")
            return
        
        if save_to_file and not output_file:
            messagebox.showerror("Error", "Please select an output file.")
            return
        
        try:
            # Import visualization tools
            from .visualization_tools import (
                TimelineVisualizer, RelationshipGraphVisualizer,
                ContentAnalysisVisualizer, InteractiveVisualizationApp,
                visualize_timeline, visualize_relationships, visualize_content_analysis
            )
            
            # Load data
            with open(data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.update_progress(f"📊 Loaded {len(data)} items for visualization")
            
            if viz_type == "interactive":
                # Launch interactive app
                app = InteractiveVisualizationApp()
                app.data = data
                app.update_visualization()
                self.update_progress("🎨 Launching interactive visualization app...")
                app.run()
                
            elif viz_type == "timeline":
                fig = visualize_timeline(data, output_file)
                if not output_file:
                    import matplotlib.pyplot as plt
                    plt.show()
                self.update_progress(f"📅 Timeline visualization {'saved' if output_file else 'displayed'}")
                
            elif viz_type == "network":
                fig = visualize_relationships(data, output_file)
                if not output_file:
                    import matplotlib.pyplot as plt
                    plt.show()
                self.update_progress(f"🕸️ Network visualization {'saved' if output_file else 'displayed'}")
                
            elif viz_type == "content_analysis":
                fig = visualize_content_analysis(data, output_file)
                if not output_file:
                    import matplotlib.pyplot as plt
                    plt.show()
                self.update_progress(f"📊 Content analysis visualization {'saved' if output_file else 'displayed'}")
                
            elif viz_type == "dashboard":
                # Create comprehensive dashboard
                visualizer = ContentAnalysisVisualizer()
                fig = visualizer.create_content_analysis_dashboard(data)
                if output_file:
                    fig.savefig(output_file, dpi=300, bbox_inches='tight')
                else:
                    import matplotlib.pyplot as plt
                    plt.show()
                self.update_progress(f"📈 Dashboard visualization {'saved' if output_file else 'displayed'}")
            
            messagebox.showinfo("Success", f"Visualization completed successfully!")
            
        except ImportError as e:
            error_msg = f"Visualization dependencies not available: {e}"
            self.update_progress(f"❌ {error_msg}")
            messagebox.showerror("Error", error_msg + "\n\nInstall with: pip install matplotlib seaborn networkx pandas")
        except Exception as e:
            error_msg = f"Visualization failed: {e}"
            self.update_progress(f"❌ {error_msg}")
            messagebox.showerror("Error", error_msg)
    
    def quick_preview(self):
        """Generate a quick preview of the visualization."""
        data_file = self.visualization_data_var.get()
        
        if not data_file:
            messagebox.showerror("Error", "Please select a data file.")
            return
        
        try:
            # Load data and show basic info
            with open(data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Show data summary
            summary = f"""
Data Summary:
- Total items: {len(data)}
- Date range: {min([item.get('date', 'Unknown') for item in data])} to {max([item.get('date', 'Unknown') for item in data])}
- Content types: {set([item.get('type', 'Unknown') for item in data])}
- Average content length: {sum([len(str(item.get('content', ''))) for item in data]) // len(data)} characters
            """
            
            messagebox.showinfo("Quick Preview", summary)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate preview: {e}")
    
    def refresh_visualization_data(self):
        """Refresh visualization data from current index."""
        if not self.advanced_index_data:
            messagebox.showerror("Error", "No index data available. Please build or load an index first.")
            return
        
        try:
            # Convert index data to visualization format
            viz_data = []
            for file_path, file_data in self.advanced_index_data.get('files', {}).items():
                for entry in file_data.get('entries', []):
                    viz_data.append({
                        'date': entry.get('timestamp', 'Unknown'),
                        'content': entry.get('content', ''),
                        'type': entry.get('type', 'conversation'),
                        'source': file_path,
                        'tags': entry.get('tags', [])
                    })
            
            # Save to temporary file
            temp_file = Path("temp_visualization_data.json")
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(viz_data, f, indent=2, default=str)
            
            self.visualization_data_var.set(str(temp_file))
            self.update_progress(f"🔄 Refreshed visualization data: {len(viz_data)} items")
            messagebox.showinfo("Success", f"Refreshed visualization data with {len(viz_data)} items")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to refresh visualization data: {e}")
    
    # SMS Parser Methods
    def browse_sms_file(self):
        """Browse for SMS XML file."""
        filename = filedialog.askopenfilename(
            title="Select SMS XML File",
            filetypes=[("XML files", "*.xml"), ("All files", "*.*")]
        )
        if filename:
            self.sms_file_var.set(filename)
    
    def browse_sms_output_dir(self):
        """Browse for SMS output directory."""
        directory = filedialog.askdirectory(title="Select Output Directory")
        if directory:
            self.sms_output_dir_var.set(directory)
    
    def parse_sms_file(self):
        """Parse SMS file and export to selected format."""
        sms_file = self.sms_file_var.get()
        output_dir = self.sms_output_dir_var.get()
        output_format = self.sms_format_var.get()
        append_mode = self.sms_append_var.get()
        
        if not sms_file:
            messagebox.showerror("Error", "Please select an SMS XML file.")
            return
        
        try:
            from .sms_parser import SMSParser
            
            # Initialize parser
            parser = SMSParser()
            
            # Create output directory
            output_path = Path(output_dir)
            output_path.mkdir(exist_ok=True)
            
            # Determine output files
            amandamap_file = output_path / "amandamap_sms_conversations.json"
            phoenix_file = output_path / "phoenix_sms_conversations.json"
            
            # Check append mode
            if append_mode:
                self.update_progress(f"📱 Parsing SMS file in APPEND mode: {sms_file}")
                if amandamap_file.exists() and output_format in ['amandamap', 'both']:
                    self.update_progress(f"   AmandaMap file exists: {amandamap_file}")
                if phoenix_file.exists() and output_format in ['phoenix', 'both']:
                    self.update_progress(f"   Phoenix Codex file exists: {phoenix_file}")
            else:
                self.update_progress(f"📱 Parsing SMS file in OVERWRITE mode: {sms_file}")
            
            # Parse SMS file with append mode
            conversations = parser.parse_sms_file(
                Path(sms_file),
                append_mode=append_mode,
                amandamap_file=amandamap_file if output_format in ['amandamap', 'both'] else None,
                phoenix_file=phoenix_file if output_format in ['phoenix', 'both'] else None
            )
            
            if not conversations:
                messagebox.showerror("Error", "No conversations found in SMS file.")
                return
            
            self.update_progress(f"✅ Parsed {len(conversations)} conversation entries")
            if append_mode:
                self.update_progress(f"   Added {parser.new_entries_count} new entries")
                self.update_progress(f"   Skipped {parser.skipped_entries_count} existing entries")
            
            # Export based on format
            if output_format in ['amandamap', 'both']:
                if parser.export_to_amandamap(amandamap_file, append_mode=append_mode):
                    self.update_progress(f"✅ Exported AmandaMap format: {amandamap_file}")
            
            if output_format in ['phoenix', 'both']:
                if parser.export_to_phoenix_codex(phoenix_file, append_mode=append_mode):
                    self.update_progress(f"✅ Exported Phoenix Codex format: {phoenix_file}")
            
            success_msg = f"SMS parsing completed successfully!\n\nParsed {len(conversations)} conversation entries."
            if append_mode:
                success_msg += f"\nAdded {parser.new_entries_count} new entries"
                success_msg += f"\nSkipped {parser.skipped_entries_count} existing entries"
            
            messagebox.showinfo("Success", success_msg)
            
        except Exception as e:
            error_msg = f"SMS parsing failed: {e}"
            self.update_progress(f"❌ {error_msg}")
            messagebox.showerror("Error", error_msg)
    
    def show_sms_summary(self):
        """Show SMS conversation summary."""
        sms_file = self.sms_file_var.get()
        
        if not sms_file:
            messagebox.showerror("Error", "Please select an SMS XML file.")
            return
        
        try:
            from .sms_parser import SMSParser
            
            # Initialize parser and parse file
            parser = SMSParser()
            conversations = parser.parse_sms_file(Path(sms_file))
            
            if not conversations:
                messagebox.showerror("Error", "No conversations found in SMS file.")
                return
            
            # Get summary
            summary = parser.get_conversation_summary()
            
            # Create summary text
            summary_text = f"""
SMS Conversation Summary
========================

Total Messages: {summary.get('total_messages', 0)}
Amanda Messages: {summary.get('amanda_messages', 0)}
Justin Messages: {summary.get('justin_messages', 0)}
Date Range: {summary.get('date_range', 'Unknown')}

Conversation Types:
"""
            for conv_type, count in summary.get('conversation_types', {}).items():
                summary_text += f"  {conv_type.upper()}: {count}\n"
            
            if summary.get('most_common_tags'):
                summary_text += "\nMost Common Tags:\n"
                for tag, count in summary['most_common_tags']:
                    summary_text += f"  {tag}: {count}\n"
            
            messagebox.showinfo("SMS Summary", summary_text)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate SMS summary: {e}")
    
    def visualize_sms_conversations(self):
        """Visualize SMS conversations using the visualization tools."""
        sms_file = self.sms_file_var.get()
        
        if not sms_file:
            messagebox.showerror("Error", "Please select an SMS XML file.")
            return
        
        try:
            from .sms_parser import SMSParser
            
            # Parse SMS file
            parser = SMSParser()
            conversations = parser.parse_sms_file(Path(sms_file))
            
            if not conversations:
                messagebox.showerror("Error", "No conversations found in SMS file.")
                return
            
            # Convert to visualization format
            viz_data = []
            for conv in conversations:
                viz_data.append({
                    'date': conv.timestamp,
                    'content': conv.content,
                    'type': 'conversation',
                    'source': conv.source,
                    'tags': conv.tags,
                    'sender': conv.sender,
                    'receiver': conv.receiver
                })
            
            # Save to temporary file for visualization
            temp_file = Path("temp_sms_visualization_data.json")
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(viz_data, f, indent=2, default=str)
            
            # Launch visualization
            from .visualization_tools import InteractiveVisualizationApp
            app = InteractiveVisualizationApp()
            app.data = viz_data
            app.update_visualization()
            self.update_progress("🎨 Launching SMS conversation visualization...")
            app.run()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to visualize SMS conversations: {e}")

# Export the enhanced app
__all__ = ["EnhancedApp", "App", "apply_styles"]

#!/usr/bin/env python3
"""
Enhanced Dataset Builder GUI with Advanced Performance Settings

Provides a comprehensive GUI for the enhanced dataset builder with:
- Performance settings configuration
- Real-time monitoring
- Advanced threading controls
- CUDA/GPU settings
- Memory management controls
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import time
import queue
from pathlib import Path
from typing import Dict, Any, Optional
import json
from concurrent.futures import ThreadPoolExecutor

from enhanced_dataset_builder import (
    PerformanceSettings, ProcessingMetrics, PerformanceMonitor,
    FileProcessor, DatasetEntry
)


class EnhancedDatasetBuilderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🚀 Enhanced AmandaMap Dataset Builder")
        self.root.geometry("1000x800")
        self.root.resizable(True, True)
        
        # Initialize settings
        self.settings = PerformanceSettings()
        self.metrics = ProcessingMetrics()
        self.monitor = PerformanceMonitor(self.settings)
        self.file_processor = FileProcessor(self.settings)
        
        # Variables
        self.input_folder = tk.StringVar()
        self.amandamap_output = tk.StringVar(value="amandamapexportfile.json")
        self.phoenix_output = tk.StringVar(value="phoenixcodexexport.json")
        self.include_csv = tk.BooleanVar(value=True)
        self.verbose_mode = tk.BooleanVar(value=True)
        self.file_types = tk.StringVar(value="md,txt,json")
        
        # Performance settings variables
        self.max_threads = tk.IntVar(value=self.settings.max_threads)
        self.use_multiprocessing = tk.BooleanVar(value=self.settings.use_multiprocessing)
        self.max_cpu_percent = tk.DoubleVar(value=self.settings.max_cpu_percent)
        self.max_memory_gb = tk.DoubleVar(value=self.settings.max_memory_usage_gb)
        self.enable_cuda = tk.BooleanVar(value=self.settings.enable_cuda)
        self.batch_size = tk.IntVar(value=self.settings.batch_size)
        self.enable_ram_processing = tk.BooleanVar(value=self.settings.use_ram_processing)
        self.enable_file_cache = tk.BooleanVar(value=self.settings.enable_file_cache)
        self.enable_performance_monitoring = tk.BooleanVar(value=self.settings.enable_performance_monitoring)
        
        # Processing state
        self.is_processing = False
        self.total_files = 0
        self.processed_files = 0
        self.entries = []
        
        # Thread communication
        self.message_queue = queue.Queue()
        self.processing_thread = None
        
        self.setup_ui()
        self.check_queue()
        self.start_monitoring()
        
    def setup_ui(self):
        # Main frame with scrollbar
        main_canvas = tk.Canvas(self.root)
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=main_canvas.yview)
        scrollable_frame = ttk.Frame(main_canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        )
        
        main_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        main_canvas.configure(yscrollcommand=scrollbar.set)
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Title
        title_label = ttk.Label(scrollable_frame, text="🚀 Enhanced AmandaMap Dataset Builder", 
                                font=("Arial", 18, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # File selection frame
        file_frame = ttk.LabelFrame(scrollable_frame, text="📁 File Selection", padding="10")
        file_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        file_frame.columnconfigure(1, weight=1)
        
        # Input folder selection
        ttk.Label(file_frame, text="📁 Input Folder:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(file_frame, textvariable=self.input_folder, width=60).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(5, 5))
        ttk.Button(file_frame, text="Browse", command=self.browse_input_folder).grid(row=0, column=2)
        
        # AmandaMap output file selection
        ttk.Label(file_frame, text="🗺️ AmandaMap Output:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(file_frame, textvariable=self.amandamap_output, width=60).grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(5, 5))
        ttk.Button(file_frame, text="Browse", command=self.browse_amandamap_output).grid(row=1, column=2)
        
        # Phoenix Codex output file selection
        ttk.Label(file_frame, text="🪶 Phoenix Codex Output:").grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Entry(file_frame, textvariable=self.phoenix_output, width=60).grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(5, 5))
        ttk.Button(file_frame, text="Browse", command=self.browse_phoenix_output).grid(row=2, column=2)
        
        # File types
        ttk.Label(file_frame, text="📄 File types:").grid(row=3, column=0, sticky=tk.W, pady=5)
        ttk.Entry(file_frame, textvariable=self.file_types, width=30).grid(row=3, column=1, sticky=tk.W, padx=(5, 0))
        ttk.Label(file_frame, text="(comma-separated, e.g., md,txt,json)").grid(row=3, column=2, sticky=tk.W, padx=(5, 0))
        
        # Performance Settings Frame
        perf_frame = ttk.LabelFrame(scrollable_frame, text="⚡ Performance Settings", padding="10")
        perf_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        perf_frame.columnconfigure(1, weight=1)
        
        # Threading settings
        ttk.Label(perf_frame, text="🧵 Threading:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        ttk.Label(perf_frame, text="Max Threads:").grid(row=1, column=0, sticky=tk.W, pady=2)
        thread_spinbox = ttk.Spinbox(perf_frame, from_=1, to=32, textvariable=self.max_threads, width=10)
        thread_spinbox.grid(row=1, column=1, sticky=tk.W, padx=(5, 0))
        
        ttk.Checkbutton(perf_frame, text="Use Multiprocessing", variable=self.use_multiprocessing).grid(row=2, column=0, sticky=tk.W, pady=2)
        
        # CPU settings
        ttk.Label(perf_frame, text="🖥️ CPU Control:", font=("Arial", 10, "bold")).grid(row=3, column=0, sticky=tk.W, pady=(10, 5))
        
        ttk.Label(perf_frame, text="Max CPU %:").grid(row=4, column=0, sticky=tk.W, pady=2)
        cpu_scale = ttk.Scale(perf_frame, from_=10, to=100, variable=self.max_cpu_percent, orient=tk.HORIZONTAL)
        cpu_scale.grid(row=4, column=1, sticky=(tk.W, tk.E), padx=(5, 0))
        ttk.Label(perf_frame, textvariable=tk.StringVar(value=f"{self.max_cpu_percent.get():.0f}%")).grid(row=4, column=2, sticky=tk.W, padx=(5, 0))
        
        # Memory settings
        ttk.Label(perf_frame, text="💾 Memory Control:", font=("Arial", 10, "bold")).grid(row=5, column=0, sticky=tk.W, pady=(10, 5))
        
        ttk.Label(perf_frame, text="Max Memory (GB):").grid(row=6, column=0, sticky=tk.W, pady=2)
        memory_scale = ttk.Scale(perf_frame, from_=1, to=16, variable=self.max_memory_gb, orient=tk.HORIZONTAL)
        memory_scale.grid(row=6, column=1, sticky=(tk.W, tk.E), padx=(5, 0))
        ttk.Label(perf_frame, textvariable=tk.StringVar(value=f"{self.max_memory_gb.get():.1f}GB")).grid(row=6, column=2, sticky=tk.W, padx=(5, 0))
        
        # GPU settings
        ttk.Label(perf_frame, text="🎮 GPU Acceleration:", font=("Arial", 10, "bold")).grid(row=7, column=0, sticky=tk.W, pady=(10, 5))
        
        ttk.Checkbutton(perf_frame, text="Enable CUDA/GPU", variable=self.enable_cuda).grid(row=8, column=0, sticky=tk.W, pady=2)
        
        # Processing settings
        ttk.Label(perf_frame, text="⚙️ Processing:", font=("Arial", 10, "bold")).grid(row=9, column=0, sticky=tk.W, pady=(10, 5))
        
        ttk.Label(perf_frame, text="Batch Size:").grid(row=10, column=0, sticky=tk.W, pady=2)
        batch_spinbox = ttk.Spinbox(perf_frame, from_=10, to=1000, textvariable=self.batch_size, width=10)
        batch_spinbox.grid(row=10, column=1, sticky=tk.W, padx=(5, 0))
        
        ttk.Checkbutton(perf_frame, text="RAM Processing", variable=self.enable_ram_processing).grid(row=11, column=0, sticky=tk.W, pady=2)
        ttk.Checkbutton(perf_frame, text="File Caching", variable=self.enable_file_cache).grid(row=11, column=1, sticky=tk.W, pady=2)
        ttk.Checkbutton(perf_frame, text="Performance Monitoring", variable=self.enable_performance_monitoring).grid(row=12, column=0, sticky=tk.W, pady=2)
        
        # Options frame
        options_frame = ttk.LabelFrame(scrollable_frame, text="📊 Output Options", padding="10")
        options_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        options_frame.columnconfigure(1, weight=1)
        
        ttk.Checkbutton(options_frame, text="📊 Include CSV output", variable=self.include_csv).grid(row=0, column=0, sticky=tk.W)
        ttk.Checkbutton(options_frame, text="🔍 Verbose mode", variable=self.verbose_mode).grid(row=0, column=1, sticky=tk.W)
        
        # Performance Monitoring Frame
        monitor_frame = ttk.LabelFrame(scrollable_frame, text="📈 Performance Monitor", padding="10")
        monitor_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        monitor_frame.columnconfigure(0, weight=1)
        
        # Real-time metrics
        self.cpu_label = ttk.Label(monitor_frame, text="CPU: 0%")
        self.cpu_label.grid(row=0, column=0, sticky=tk.W)
        
        self.memory_label = ttk.Label(monitor_frame, text="Memory: 0MB")
        self.memory_label.grid(row=1, column=0, sticky=tk.W)
        
        self.gpu_label = ttk.Label(monitor_frame, text="GPU: Not Available")
        self.gpu_label.grid(row=2, column=0, sticky=tk.W)
        
        self.thread_label = ttk.Label(monitor_frame, text="Threads: 0")
        self.thread_label.grid(row=3, column=0, sticky=tk.W)
        
        # Progress frame
        progress_frame = ttk.LabelFrame(scrollable_frame, text="📈 Progress", padding="10")
        progress_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        progress_frame.columnconfigure(0, weight=1)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Status labels
        self.status_label = ttk.Label(progress_frame, text="Ready to process files")
        self.status_label.grid(row=1, column=0, sticky=tk.W)
        
        self.file_label = ttk.Label(progress_frame, text="")
        self.file_label.grid(row=2, column=0, sticky=tk.W)
        
        self.stats_label = ttk.Label(progress_frame, text="")
        self.stats_label.grid(row=3, column=0, sticky=tk.W)
        
        # Performance stats
        self.perf_stats_label = ttk.Label(progress_frame, text="")
        self.perf_stats_label.grid(row=4, column=0, sticky=tk.W)
        
        # Log text area
        log_frame = ttk.LabelFrame(scrollable_frame, text="📝 Log", padding="10")
        log_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        # Scrollbar for log
        log_scrollbar = ttk.Scrollbar(log_frame)
        log_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Log text widget
        self.log_text = tk.Text(log_frame, height=10, yscrollcommand=log_scrollbar.set)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        log_scrollbar.config(command=self.log_text.yview)
        
        # Buttons frame
        button_frame = ttk.Frame(scrollable_frame)
        button_frame.grid(row=7, column=0, columnspan=3, pady=20)
        
        self.process_button = ttk.Button(button_frame, text="🚀 Start Processing", command=self.start_processing)
        self.process_button.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="⚙️ Save Settings", command=self.save_settings).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="📊 Performance Report", command=self.show_performance_report).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="🗑️ Clear Log", command=self.clear_log).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="❌ Exit", command=self.root.quit).pack(side=tk.LEFT)
        
        # Configure scrollable frame weights
        scrollable_frame.columnconfigure(0, weight=1)
        
    def check_queue(self):
        """Check for messages from the processing thread"""
        try:
            while True:
                message = self.message_queue.get_nowait()
                self.handle_message(message)
        except queue.Empty:
            pass
        finally:
            # Schedule the next check
            self.root.after(100, self.check_queue)
    
    def start_monitoring(self):
        """Start performance monitoring"""
        def monitor_loop():
            while True:
                try:
                    metrics = self.monitor.get_current_metrics()
                    
                    # Update GUI labels
                    self.root.after(0, lambda: self.cpu_label.config(text=f"CPU: {metrics['cpu_percent']:.1f}%"))
                    self.root.after(0, lambda: self.memory_label.config(text=f"Memory: {metrics['process_memory_mb']:.1f}MB"))
                    
                    if 'gpu_memory_used_mb' in metrics:
                        self.root.after(0, lambda: self.gpu_label.config(text=f"GPU: {metrics['gpu_memory_used_mb']:.1f}MB"))
                    else:
                        self.root.after(0, lambda: self.gpu_label.config(text="GPU: Not Available"))
                    
                    # Check resource limits
                    within_limits, warnings = self.monitor.check_resource_limits()
                    if not within_limits and self.is_processing:
                        for warning in warnings:
                            self.log_message(f"⚠️ {warning}")
                    
                    time.sleep(1)  # Update every second
                    
                except Exception as e:
                    print(f"Monitoring error: {e}")
                    time.sleep(5)
        
        monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        monitor_thread.start()
    
    def handle_message(self, message):
        """Handle messages from the processing thread"""
        msg_type = message.get('type')
        
        if msg_type == 'log':
            self.log_message(message['text'])
        elif msg_type == 'progress':
            self.update_progress(message['current'], message['total'], 
                                 message.get('status', ''), message.get('file_name', ''))
        elif msg_type == 'stats':
            self.update_stats(message.get('counts', {}), message.get('processed_files', 0))
        elif msg_type == 'performance':
            self.update_performance_stats(message['metrics'])
        elif msg_type == 'finished':
            self.finish_processing()
        elif msg_type == 'error':
            messagebox.showerror("Processing Error", message['text'])
            self.finish_processing()
    
    def browse_input_folder(self):
        folder = filedialog.askdirectory(title="Select Input Folder")
        if folder:
            self.input_folder.set(folder)
            self.log_message(f"📁 Selected input folder: {folder}")
            
    def browse_amandamap_output(self):
        file = filedialog.asksaveasfilename(
            title="Save AmandaMap Output File",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if file:
            self.amandamap_output.set(file)
            self.log_message(f"🗺️ Selected AmandaMap output file: {file}")
    
    def browse_phoenix_output(self):
        file = filedialog.asksaveasfilename(
            title="Save Phoenix Codex Output File",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if file:
            self.phoenix_output.set(file)
            self.log_message(f"🪶 Selected Phoenix Codex output file: {file}")
    
    def log_message(self, message):
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        
    def clear_log(self):
        self.log_text.delete(1.0, tk.END)
        
    def update_progress(self, current, total, status="", file_name=""):
        if total > 0:
            progress = (current / total) * 100
            self.progress_var.set(progress)
            
        self.status_label.config(text=status)
        if file_name:
            self.file_label.config(text=f"📖 Processing: {file_name}")
    
    def update_stats(self, counts, processed_files):
        if counts:
            total = sum(counts.values())
            stats_text = f"📊 Results: {total} entries from {processed_files} files"
            self.stats_label.config(text=stats_text)
        else:
            self.stats_label.config(text="")
    
    def update_performance_stats(self, metrics):
        """Update performance statistics display"""
        if metrics:
            stats_text = (f"⚡ Performance: {metrics.get('files_per_second', 0):.1f} files/sec, "
                          f"{metrics.get('entries_per_second', 0):.1f} entries/sec")
            self.perf_stats_label.config(text=stats_text)
    
    def save_settings(self):
        """Save current settings to file"""
        try:
            # Update settings from GUI variables
            self.settings.max_threads = self.max_threads.get()
            self.settings.use_multiprocessing = self.use_multiprocessing.get()
            self.settings.max_cpu_percent = self.max_cpu_percent.get()
            self.settings.max_memory_usage_gb = self.max_memory_gb.get()
            self.settings.enable_cuda = self.enable_cuda.get()
            self.settings.batch_size = self.batch_size.get()
            self.settings.use_ram_processing = self.enable_ram_processing.get()
            self.settings.enable_file_cache = self.enable_file_cache.get()
            self.settings.enable_performance_monitoring = self.enable_performance_monitoring.get()
            
            # Save to file
            settings_file = "enhanced_dataset_settings.json"
            with open(settings_file, 'w') as f:
                json.dump(self.settings.__dict__, f, indent=2)
            
            self.log_message(f"✅ Settings saved to {settings_file}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {e}")
    
    def show_performance_report(self):
        """Show detailed performance report"""
        try:
            summary = self.monitor.get_performance_summary()
            
            if summary:
                report = f"""
📊 Performance Report
====================
Average Memory: {summary.get('avg_memory_mb', 0):.1f}MB
Peak Memory: {summary.get('max_memory_mb', 0):.1f}MB
Average CPU: {summary.get('avg_cpu_percent', 0):.1f}%
Peak CPU: {summary.get('max_cpu_percent', 0):.1f}%
Monitoring Duration: {summary.get('monitoring_duration', 0):.1f}s
Total Samples: {summary.get('total_samples', 0)}
"""
                
                # Create a new window for the report
                report_window = tk.Toplevel(self.root)
                report_window.title("Performance Report")
                report_window.geometry("500x400")
                
                text_widget = tk.Text(report_window, wrap=tk.WORD)
                text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
                text_widget.insert(tk.END, report)
                text_widget.config(state=tk.DISABLED)
                
            else:
                messagebox.showinfo("Performance Report", "No performance data available yet.")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate performance report: {e}")
    
    def start_processing(self):
        if self.is_processing:
            return
            
        input_folder = self.input_folder.get().strip()
        amandamap_output = self.amandamap_output.get().strip()
        phoenix_output = self.phoenix_output.get().strip()
        
        if not input_folder:
            messagebox.showerror("Error", "Please select an input folder!")
            return
            
        if not amandamap_output or not phoenix_output:
            messagebox.showerror("Error", "Please specify both AmandaMap and Phoenix Codex output files!")
            return
            
        if not Path(input_folder).exists():
            messagebox.showerror("Error", f"Input folder does not exist: {input_folder}")
            return
        
        # Update settings from GUI
        self.save_settings()
        
        # Start processing in a separate thread
        self.is_processing = True
        self.process_button.config(text="⏸️ Processing...", state="disabled")
        self.progress_var.set(0)
        self.clear_log()
        
        self.processing_thread = threading.Thread(
            target=self.process_files_async, 
            args=(input_folder, amandamap_output, phoenix_output),
            daemon=True
        )
        self.processing_thread.start()
    
    def process_files_async(self, input_folder, amandamap_output, phoenix_output):
        """Process files in a separate thread with async-like behavior"""
        try:
            self.message_queue.put({'type': 'log', 'text': "🚀 Starting enhanced dataset building process..."})
            
            # Update settings
            self.settings.max_threads = self.max_threads.get()
            self.settings.use_multiprocessing = self.use_multiprocessing.get()
            self.settings.max_cpu_percent = self.max_cpu_percent.get()
            self.settings.max_memory_usage_gb = self.max_memory_gb.get()
            self.settings.enable_cuda = self.enable_cuda.get()
            self.settings.batch_size = self.batch_size.get()
            self.settings.use_ram_processing = self.enable_ram_processing.get()
            self.settings.enable_file_cache = self.enable_file_cache.get()
            self.settings.enable_performance_monitoring = self.enable_performance_monitoring.get()
            
            # Reinitialize components with new settings
            self.monitor = PerformanceMonitor(self.settings)
            self.file_processor = FileProcessor(self.settings)
            
            self.message_queue.put({'type': 'log', 'text': f"⚙️ Performance Settings:"})
            self.message_queue.put({'type': 'log', 'text': f"    • Max Threads: {self.settings.max_threads}"})
            self.message_queue.put({'type': 'log', 'text': f"    • Max CPU: {self.settings.max_cpu_percent:.1f}%"})
            self.message_queue.put({'type': 'log', 'text': f"    • Max Memory: {self.settings.max_memory_usage_gb:.1f}GB"})
            self.message_queue.put({'type': 'log', 'text': f"    • CUDA Enabled: {self.settings.enable_cuda}"})
            self.message_queue.put({'type': 'log', 'text': f"    • Batch Size: {self.settings.batch_size}"})
            self.message_queue.put({'type': 'log', 'text': f"    • RAM Processing: {self.settings.use_ram_processing}"})
            
            folder = Path(input_folder)
            file_types = [ft.strip() for ft in self.file_types.get().split(",")]
            
            self.message_queue.put({'type': 'log', 'text': f"📁 Input folder: {input_folder}"})
            self.message_queue.put({'type': 'log', 'text': f"🗺️ AmandaMap output: {amandamap_output}"})
            self.message_queue.put({'type': 'log', 'text': f"🪶 Phoenix Codex output: {phoenix_output}"})
            self.message_queue.put({'type': 'log', 'text': f"📄 File types: {', '.join(file_types)}"})
            
            # Collect all file paths
            all_files = []
            for file_type in file_types:
                all_files.extend(list(folder.rglob(f"*.{file_type}")))
                
            self.message_queue.put({'type': 'log', 'text': f"🔍 Found {len(all_files)} files to process"})
            
            if len(all_files) == 0:
                self.message_queue.put({'type': 'log', 'text': "⚠️ No files found to process!"})
                self.message_queue.put({'type': 'finished'})
                return
            
            # Process files sequentially to avoid high RAM usage
            self.message_queue.put({'type': 'log', 'text': "📄 Processing files sequentially..."})

            counts = self.file_processor.process_files_streaming(
                all_files,
                amandamap_output,
                phoenix_output,
            )

            self.message_queue.put({'type': 'log', 'text': f"✅ Processing complete!"})
            self.message_queue.put({'type': 'log', 'text': f"🗺️ AmandaMap entries found: {counts.get('AmandaMap', 0)}"})
            self.message_queue.put({'type': 'log', 'text': f"🪶 Phoenix Codex entries found: {counts.get('PhoenixCodex', 0)}"})

            # Final statistics
            self.message_queue.put({'type': 'stats', 'counts': counts, 'processed_files': len(all_files)})
            
            # Final performance summary
            self.metrics.end_time = time.time()
            self.message_queue.put({'type': 'log', 'text': f"⏱️ Total processing time: {self.metrics.duration:.1f} seconds"})
            self.message_queue.put({'type': 'log', 'text': f"📈 Average speed: {self.metrics.files_per_second:.1f} files/sec"})
            self.message_queue.put({'type': 'log', 'text': f"📊 Average speed: {self.metrics.entries_per_second:.1f} entries/sec"})
            
            self.message_queue.put({'type': 'log', 'text': "🎉 Enhanced dataset building complete! Your data is ready for analysis."})
            self.message_queue.put({
                'type': 'progress',
                'current': len(all_files),
                'total': len(all_files),
                'status': "✅ Processing complete!"
            })
            
            self.message_queue.put({'type': 'finished'})
            
        except Exception as e:
            self.message_queue.put({'type': 'error', 'text': f"Fatal error: {e}"})
        finally:
            # Cleanup
            if hasattr(self, 'file_processor'):
                self.file_processor.cleanup()
            self.message_queue.put({'type': 'finished'})
    
    def finish_processing(self):
        self.is_processing = False
        self.process_button.config(text="🚀 Start Processing", state="normal")


if __name__ == "__main__":
    root = tk.Tk()
    app = EnhancedDatasetBuilderGUI(root)
    root.mainloop()
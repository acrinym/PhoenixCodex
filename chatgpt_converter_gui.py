#!/usr/bin/env python3
"""
🔄 ChatGPT Export Converter GUI
Quick converter for ChatGPT JSON exports with Markdown/JSON bidirectional conversion.
Includes optional message isolation, filtering, and bulk operations.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
import threading
from dataclasses import dataclass
from datetime import datetime
import re
try:
    from bs4 import BeautifulSoup
    HAS_BEAUTIFULSOUP = True
except ImportError:
    HAS_BEAUTIFULSOUP = False

@dataclass
class ConversionJob:
    input_file: Path
    output_dir: Path
    input_format: str  # "json", "md"
    output_format: str  # "json", "md"
    isolate: bool = False
    filter_by_role: Optional[str] = None
    combine_files: bool = False


class ChatGPTExportConverter:
    """Core conversion logic for ChatGPT exports."""
    
    @staticmethod
    def parse_chatgpt_json(json_file: Path) -> Dict[str, Any] | List[Dict[str, Any]]:
        """Parse ChatGPT JSON export file. Supports both formats:
        - Individual chat format: {"title": "...", "mapping": {...}}
        - Bulk format: [{"title": "...", "mapping": {...}}, ...]
        """
        with open(json_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    @staticmethod
    def detect_format(data) -> str:
        """Detect if data is bulk format (array) or individual format (dict)."""
        if isinstance(data, list):
            return "bulk"
        elif isinstance(data, dict):
            return "individual"
        return "unknown"
    
    @staticmethod
    def extract_conversations(data) -> List[Dict[str, Any]]:
        """Extract conversations from either format.
        Returns list of conversation dicts."""
        if isinstance(data, list):
            # Bulk format: already an array
            return data
        elif isinstance(data, dict):
            # Individual format: wrap in list
            return [data]
        return []
    
    @staticmethod
    def extract_messages(data: Dict[str, Any]) -> List[Dict[str, str]]:
        """Extract messages from a single ChatGPT conversation."""
        messages = []
        mapping = data.get('mapping', {})
        
        for node_id, node in mapping.items():
            if node.get('message') and node['message'].get('content', {}).get('parts'):
                msg = node['message']
                role = msg['author'].get('role', 'unknown')
                content_parts = msg['content'].get('parts', [])
                content = ''.join(
                    part if isinstance(part, str) else ''
                    for part in content_parts
                )
                
                if content.strip():
                    messages.append({
                        'role': role,
                        'content': content,
                        'timestamp': msg.get('create_time')
                    })
        
        return messages
    
    @staticmethod
    def messages_to_markdown(title: str, messages: List[Dict[str, str]]) -> str:
        """Convert messages to Markdown format."""
        md_lines = [f"# {title}\n"]
        
        for msg in messages:
            role = msg['role'].upper()
            content = msg['content']
            
            # Add timestamp if available
            if msg.get('timestamp'):
                timestamp = datetime.fromtimestamp(msg['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
                md_lines.append(f"**[{role}]** _{timestamp}_\n")
            else:
                md_lines.append(f"**[{role}]**\n")
            
            md_lines.append(content)
            md_lines.append("\n---\n")
        
        return '\n'.join(md_lines)
    
    @staticmethod
    def messages_to_json(title: str, messages: List[Dict[str, str]]) -> str:
        """Convert messages to JSON format."""
        export = {
            'title': title,
            'export_date': datetime.now().isoformat(),
            'total_messages': len(messages),
            'messages': messages
        }
        return json.dumps(export, indent=2, ensure_ascii=False)
    
    @staticmethod
    def parse_claude_html(html_file: Path) -> Dict[str, Any]:
        """Parse Claude HTML export file."""
        if not HAS_BEAUTIFULSOUP:
            raise ImportError("beautifulsoup4 is required for HTML parsing. Install with: pip install beautifulsoup4")
        
        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Extract title
        title_tag = soup.find('title')
        title = title_tag.string if title_tag else html_file.stem
        
        return {
            'title': title,
            'soup': soup,
            'html': html_content
        }
    
    @staticmethod
    def extract_messages_from_html(data: Dict[str, Any]) -> List[Dict[str, str]]:
        """Extract messages from Claude HTML structure."""
        messages = []
        soup = data.get('soup')
        
        if not soup:
            return messages
        
        # Find all message divs (msg-user or msg-assistant)
        msg_divs = soup.find_all('div', class_=re.compile(r'msg-(user|assistant)'))
        
        for msg_div in msg_divs:
            # Determine role
            if 'msg-user' in msg_div.get('class', []):
                role = 'user'
            elif 'msg-assistant' in msg_div.get('class', []):
                role = 'assistant'
            else:
                continue
            
            # Extract text content
            msg_body = msg_div.find('div', class_='msg-body')
            if msg_body:
                # Get all text, preserving structure
                text_content = msg_body.find('div', class_='text-content')
                if text_content:
                    # Extract text from all tags
                    content = text_content.get_text(separator='\n').strip()
                elif msg_body:
                    content = msg_body.get_text(separator='\n').strip()
                else:
                    content = ''
                
                if content:
                    messages.append({
                        'role': role,
                        'content': content
                    })
        
        return messages
    
    @staticmethod
    def markdown_to_messages(md_content: str) -> List[Dict[str, str]]:
        """Parse Markdown back to messages."""
        messages = []
        
        # Split by role headers
        role_pattern = r'\*\*\[(USER|ASSISTANT|SYSTEM)\]\*\*'
        sections = re.split(role_pattern, md_content)
        
        for i in range(1, len(sections), 2):
            if i + 1 < len(sections):
                role = sections[i].lower()
                content = sections[i + 1].strip()
                
                # Remove timestamp if present
                content = re.sub(r'^_\d{4}-\d{2}-\d{2}.*?_\n', '', content)
                content = content.replace('---\n', '').strip()
                
                if content:
                    messages.append({
                        'role': role,
                        'content': content
                    })
        
        return messages
    
    @staticmethod
    def apply_filter(messages: List[Dict[str, str]], role_filter: Optional[str]) -> List[Dict[str, str]]:
        """Filter messages by role."""
        if not role_filter or role_filter.lower() == 'all':
            return messages
        
        return [m for m in messages if m['role'].lower() == role_filter.lower()]


class ConverterGUI:
    """GUI for ChatGPT converter."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("🔄 ChatGPT Export Converter")
        self.root.geometry("1200x700")
        self.root.resizable(True, True)
        
        self.converter = ChatGPTExportConverter()
        self.current_data = None
        self.is_processing = False
        
        # Styling
        style = ttk.Style()
        style.theme_use('clam')
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the GUI interface."""
        # Main notebook (tabs)
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Tab 1: Converter
        converter_frame = ttk.Frame(notebook)
        notebook.add(converter_frame, text="🔄 Converter")
        self.setup_converter_tab(converter_frame)
        
        # Tab 2: Batch Operations
        batch_frame = ttk.Frame(notebook)
        notebook.add(batch_frame, text="📦 Batch")
        self.setup_batch_tab(batch_frame)
        
        # Tab 3: Preview
        preview_frame = ttk.Frame(notebook)
        notebook.add(preview_frame, text="👁️ Preview")
        self.setup_preview_tab(preview_frame)
    
    def setup_converter_tab(self, parent):
        """Setup main converter tab."""
        # File selection frame
        file_frame = ttk.LabelFrame(parent, text="File Selection", padding=10)
        file_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(file_frame, text="Input File:").grid(row=0, column=0, sticky='w')
        self.input_var = tk.StringVar()
        ttk.Entry(file_frame, textvariable=self.input_var).grid(row=0, column=1, sticky='ew', padx=5)
        ttk.Button(file_frame, text="Browse", command=self.browse_input).grid(row=0, column=2)
        
        ttk.Label(file_frame, text="Output Dir:").grid(row=1, column=0, sticky='w')
        self.output_dir_var = tk.StringVar(value=str(Path.home() / "Downloads"))
        ttk.Entry(file_frame, textvariable=self.output_dir_var).grid(row=1, column=1, sticky='ew', padx=5)
        ttk.Button(file_frame, text="Browse", command=self.browse_output).grid(row=1, column=2)
        
        file_frame.columnconfigure(1, weight=1)
        
        # Conversion options frame
        options_frame = ttk.LabelFrame(parent, text="Conversion Options", padding=10)
        options_frame.pack(fill='x', padx=10, pady=10)
        
        # Input/Output formats
        ttk.Label(options_frame, text="Input Format:").grid(row=0, column=0, sticky='w')
        self.input_format_var = tk.StringVar(value="json")
        ttk.Combobox(options_frame, textvariable=self.input_format_var, 
                    values=["json", "md", "html"], state='readonly', width=10).grid(row=0, column=1, sticky='w')
        
        ttk.Label(options_frame, text="Output Format:").grid(row=0, column=2, sticky='w')
        self.output_format_var = tk.StringVar(value="md")
        ttk.Combobox(options_frame, textvariable=self.output_format_var, 
                    values=["md", "json"], state='readonly', width=10).grid(row=0, column=3, sticky='w')
        
        # Filter options
        ttk.Label(options_frame, text="Filter Messages:").grid(row=1, column=0, sticky='w')
        self.filter_var = tk.StringVar(value="All")
        ttk.Combobox(options_frame, textvariable=self.filter_var, 
                    values=["All", "User", "Assistant", "System"], state='readonly').grid(row=1, column=1, sticky='ew')
        
        # Checkboxes
        self.isolate_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="Isolate Responses", variable=self.isolate_var).grid(row=2, column=0, sticky='w')
        
        self.timestamps_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Include Timestamps", variable=self.timestamps_var).grid(row=2, column=1, sticky='w')
        
        self.combine_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="Extract from Bulk (conversations.json)", variable=self.combine_var).grid(row=2, column=2, sticky='w')
        
        options_frame.columnconfigure(1, weight=1)
        options_frame.columnconfigure(3, weight=1)
        
        # Status frame
        status_frame = ttk.LabelFrame(parent, text="Status", padding=10)
        status_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.status_text = scrolledtext.ScrolledText(status_frame, height=10, width=80, state='disabled')
        self.status_text.pack(fill='both', expand=True)
        
        # Button frame
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill='x', padx=10, pady=10)
        
        self.convert_btn = ttk.Button(button_frame, text="🚀 Convert", command=self.convert_file)
        self.convert_btn.pack(side='left', padx=5)
        
        ttk.Button(button_frame, text="Clear Log", command=self.clear_log).pack(side='left', padx=5)
        
        self.progress_var = tk.DoubleVar()
        progress = ttk.Progressbar(button_frame, variable=self.progress_var, maximum=100)
        progress.pack(side='right', fill='x', expand=True, padx=5)
    
    def setup_batch_tab(self, parent):
        """Setup batch operations tab."""
        ttk.Label(parent, text="Batch Processing", font=('Arial', 12, 'bold')).pack(padx=10, pady=10)
        
        # Folder selection
        folder_frame = ttk.LabelFrame(parent, text="Batch Conversion", padding=10)
        folder_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(folder_frame, text="Input Folder:").grid(row=0, column=0, sticky='w')
        self.batch_input_var = tk.StringVar()
        ttk.Entry(folder_frame, textvariable=self.batch_input_var).grid(row=0, column=1, sticky='ew', padx=5)
        ttk.Button(folder_frame, text="Browse", command=self.browse_batch_input).grid(row=0, column=2)
        
        ttk.Label(folder_frame, text="Output Folder:").grid(row=1, column=0, sticky='w')
        self.batch_output_var = tk.StringVar(value=str(Path.home() / "Downloads" / "batch_export"))
        ttk.Entry(folder_frame, textvariable=self.batch_output_var).grid(row=1, column=1, sticky='ew', padx=5)
        ttk.Button(folder_frame, text="Browse", command=self.browse_batch_output).grid(row=1, column=2)
        
        folder_frame.columnconfigure(1, weight=1)
        
        # Batch options
        options_frame = ttk.LabelFrame(parent, text="Batch Options", padding=10)
        options_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(options_frame, text="Output Format:").pack(anchor='w')
        self.batch_format_var = tk.StringVar(value="md")
        ttk.Radiobutton(options_frame, text="Markdown (.md)", variable=self.batch_format_var, 
                       value="md").pack(anchor='w')
        ttk.Radiobutton(options_frame, text="JSON (.json)", variable=self.batch_format_var, 
                       value="json").pack(anchor='w')
        
        self.batch_recursive_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Recursive (Include Subdirs)", 
                       variable=self.batch_recursive_var).pack(anchor='w')
        
        # Status
        self.batch_status = scrolledtext.ScrolledText(parent, height=8, width=80, state='disabled')
        self.batch_status.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Buttons
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Button(button_frame, text="🚀 Start Batch", command=self.batch_convert).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Clear Log", command=lambda: self.clear_text(self.batch_status)).pack(side='left', padx=5)
        
        self.batch_progress = ttk.Progressbar(button_frame, maximum=100)
        self.batch_progress.pack(side='right', fill='x', expand=True, padx=5)
    
    def setup_preview_tab(self, parent):
        """Setup preview tab."""
        ttk.Label(parent, text="Message Preview", font=('Arial', 12, 'bold')).pack(padx=10, pady=10)
        
        # Preview text
        self.preview_text = scrolledtext.ScrolledText(parent, height=25, width=100, wrap='word')
        self.preview_text.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Button frame
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Button(button_frame, text="Load File", command=self.load_for_preview).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Clear", command=lambda: self.preview_text.delete('1.0', 'end')).pack(side='left', padx=5)
    
    def browse_input(self):
        """Browse for input file."""
        file = filedialog.askopenfile(filetypes=[("JSON Files", "*.json"), ("Markdown Files", "*.md"), ("All Files", "*.*")])
        if file:
            self.input_var.set(file.name)
            self.log_message(f"Selected input: {file.name}")
    
    def browse_output(self):
        """Browse for output directory."""
        folder = filedialog.askdirectory()
        if folder:
            self.output_dir_var.set(folder)
            self.log_message(f"Selected output: {folder}")
    
    def browse_batch_input(self):
        """Browse for batch input folder."""
        folder = filedialog.askdirectory()
        if folder:
            self.batch_input_var.set(folder)
    
    def browse_batch_output(self):
        """Browse for batch output folder."""
        folder = filedialog.askdirectory()
        if folder:
            self.batch_output_var.set(folder)
    
    def log_message(self, message: str):
        """Log message to status text."""
        self.status_text.config(state='normal')
        self.status_text.insert('end', f"[{datetime.now().strftime('%H:%M:%S')}] {message}\n")
        self.status_text.see('end')
        self.status_text.config(state='disabled')
    
    def clear_log(self):
        """Clear log."""
        self.clear_text(self.status_text)
    
    def clear_text(self, widget):
        """Clear any scrolled text widget."""
        widget.config(state='normal')
        widget.delete('1.0', 'end')
        widget.config(state='disabled')
    
    def convert_file(self):
        """Convert a single file."""
        if self.is_processing:
            messagebox.showwarning("Warning", "Processing in progress!")
            return
        
        input_file = Path(self.input_var.get())
        if not input_file.exists():
            messagebox.showerror("Error", f"Input file not found: {input_file}")
            return
        
        output_dir = Path(self.output_dir_var.get())
        output_dir.mkdir(parents=True, exist_ok=True)
        
        job = ConversionJob(
            input_file=input_file,
            output_dir=output_dir,
            input_format=self.input_format_var.get(),
            output_format=self.output_format_var.get(),
            isolate=self.isolate_var.get(),
            filter_by_role=self.filter_var.get() if self.filter_var.get() != "All" else None
        )
        
        threading.Thread(target=self._do_convert, args=(job,), daemon=True).start()
    
    def _do_convert(self, job: ConversionJob):
        """Execute conversion in thread."""
        self.is_processing = True
        self.convert_btn.config(state='disabled')
        
        try:
            self.log_message(f"Converting {job.input_file.name}...")
            
            # Parse input
            if job.input_format == 'html':
                # Claude HTML format
                data = self.converter.parse_claude_html(job.input_file)
                title = data.get('title', job.input_file.stem)
                messages = self.converter.extract_messages_from_html(data)
                
                self.log_message(f"Extracted {len(messages)} messages from HTML")
                
                # Apply filter
                if job.filter_by_role:
                    messages = self.converter.apply_filter(messages, job.filter_by_role)
                    self.log_message(f"After filter: {len(messages)} messages")
                
                # Convert to output format
                if job.output_format == 'md':
                    output_content = self.converter.messages_to_markdown(title, messages)
                    output_file = job.output_dir / f"{job.input_file.stem}.md"
                else:  # json
                    output_content = self.converter.messages_to_json(title, messages)
                    output_file = job.output_dir / f"{job.input_file.stem}.json"
                
                # Write output
                output_file.write_text(output_content, encoding='utf-8')
                self.log_message(f"✅ Saved to: {output_file}")
                self.log_message(f"File size: {output_file.stat().st_size / 1024:.1f} KB")
                
            elif job.input_format == 'json':
                data = self.converter.parse_chatgpt_json(job.input_file)
                file_format = self.converter.detect_format(data)
                
                # Handle bulk format (conversations.json)
                if file_format == 'bulk' and job.isolate:
                    conversations = self.converter.extract_conversations(data)
                    self.log_message(f"Detected bulk format with {len(conversations)} conversations")
                    total_processed = 0
                    
                    for conv in conversations:
                        title = conv.get('title', 'Untitled')
                        messages = self.converter.extract_messages(conv)
                        
                        if job.filter_by_role:
                            messages = self.converter.apply_filter(messages, job.filter_by_role)
                        
                        # Convert each conversation
                        if messages:
                            if job.output_format == 'md':
                                output_content = self.converter.messages_to_markdown(title, messages)
                                safe_title = "".join(c for c in title if c.isalnum() or c in ' -_')[:50]
                                output_file = job.output_dir / f"{safe_title}.md"
                            else:
                                output_content = self.converter.messages_to_json(title, messages)
                                safe_title = "".join(c for c in title if c.isalnum() or c in ' -_')[:50]
                                output_file = job.output_dir / f"{safe_title}.json"
                            
                            output_file.write_text(output_content, encoding='utf-8')
                            total_processed += len(messages)
                            self.log_message(f"  ✓ {title} ({len(messages)} messages)")
                    
                    self.log_message(f"✅ Extracted {len(conversations)} conversations ({total_processed} total messages)")
                else:
                    # Handle individual format
                    if file_format == 'bulk':
                        # Bulk format but not isolated - convert first conversation
                        conversations = self.converter.extract_conversations(data)
                        conv_data = conversations[0] if conversations else {}
                        self.log_message(f"Converting first conversation from bulk file...")
                    else:
                        conv_data = data
                    
                    title = conv_data.get('title', job.input_file.stem)
                    messages = self.converter.extract_messages(conv_data)
                    
                    self.log_message(f"Extracted {len(messages)} messages")
                    
                    # Apply filter
                    if job.filter_by_role:
                        messages = self.converter.apply_filter(messages, job.filter_by_role)
                        self.log_message(f"After filter: {len(messages)} messages")
                    
                    # Convert to output format
                    if job.output_format == 'md':
                        output_content = self.converter.messages_to_markdown(title, messages)
                        output_file = job.output_dir / f"{job.input_file.stem}.md"
                    else:  # json
                        output_content = self.converter.messages_to_json(title, messages)
                        output_file = job.output_dir / f"{job.input_file.stem}.json"
                    
                    # Write output
                    output_file.write_text(output_content, encoding='utf-8')
                    self.log_message(f"✅ Saved to: {output_file}")
                    self.log_message(f"File size: {output_file.stat().st_size / 1024:.1f} KB")
            else:  # md
                with open(job.input_file, 'r', encoding='utf-8') as f:
                    md_content = f.read()
                title = job.input_file.stem
                messages = self.converter.markdown_to_messages(md_content)
                
                # Convert to output format
                if job.output_format == 'md':
                    output_content = md_content
                    output_file = job.output_dir / f"{job.input_file.stem}.md"
                else:  # json
                    output_content = self.converter.messages_to_json(title, messages)
                    output_file = job.output_dir / f"{job.input_file.stem}.json"
                
                output_file.write_text(output_content, encoding='utf-8')
                self.log_message(f"✅ Saved to: {output_file}")
                self.log_message(f"File size: {output_file.stat().st_size / 1024:.1f} KB")
            
        except Exception as e:
            self.log_message(f"❌ Error: {str(e)}")
            messagebox.showerror("Error", f"Conversion failed: {str(e)}")
        finally:
            self.is_processing = False
            self.convert_btn.config(state='normal')
    
    def batch_convert(self):
        """Convert all files in a folder."""
        input_folder = Path(self.batch_input_var.get())
        if not input_folder.exists():
            messagebox.showerror("Error", f"Folder not found: {input_folder}")
            return
        
        threading.Thread(target=self._do_batch_convert, args=(input_folder,), daemon=True).start()
    
    def _do_batch_convert(self, input_folder: Path):
        """Execute batch conversion."""
        self.batch_status.config(state='normal')
        self.batch_status.delete('1.0', 'end')
        self.batch_status.config(state='disabled')
        
        output_folder = Path(self.batch_output_var.get())
        output_folder.mkdir(parents=True, exist_ok=True)
        
        # Find files
        pattern = "**/*.json" if self.batch_recursive_var.get() else "*.json"
        files = list(input_folder.glob(pattern))
        
        self.log_batch(f"Found {len(files)} JSON files to convert")
        
        for i, input_file in enumerate(files, 1):
            self.batch_progress['value'] = (i / len(files)) * 100
            self.root.update()
            
            try:
                data = self.converter.parse_chatgpt_json(input_file)
                title = data.get('title', input_file.stem)
                messages = self.converter.extract_messages(data)
                
                output_format = self.batch_format_var.get()
                if output_format == 'md':
                    content = self.converter.messages_to_markdown(title, messages)
                    output_file = output_folder / f"{input_file.stem}.md"
                else:
                    content = self.converter.messages_to_json(title, messages)
                    output_file = output_folder / f"{input_file.stem}.json"
                
                output_file.write_text(content, encoding='utf-8')
                self.log_batch(f"✅ {i}/{len(files)}: {input_file.name}")
                
            except Exception as e:
                self.log_batch(f"❌ {i}/{len(files)}: {input_file.name} - {str(e)}")
        
        self.log_batch(f"✅ Batch complete! Saved to {output_folder}")
    
    def log_batch(self, message: str):
        """Log to batch status."""
        self.batch_status.config(state='normal')
        self.batch_status.insert('end', f"{message}\n")
        self.batch_status.see('end')
        self.batch_status.config(state='disabled')
    
    def load_for_preview(self):
        """Load a file for preview."""
        file = filedialog.askopenfile(filetypes=[("JSON Files", "*.json"), ("Markdown Files", "*.md")])
        if not file:
            return
        
        try:
            input_file = Path(file.name)
            
            if input_file.suffix == '.json':
                data = self.converter.parse_chatgpt_json(input_file)
                title = data.get('title', input_file.stem)
                messages = self.converter.extract_messages(data)
                preview_content = self.converter.messages_to_markdown(title, messages[:5])  # First 5
            else:
                with open(input_file, 'r', encoding='utf-8') as f:
                    preview_content = f.read()[:2000]  # First 2000 chars
            
            self.preview_text.config(state='normal')
            self.preview_text.delete('1.0', 'end')
            self.preview_text.insert('1.0', preview_content)
            self.preview_text.config(state='disabled')
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load file: {str(e)}")


def main():
    root = tk.Tk()
    app = ConverterGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()

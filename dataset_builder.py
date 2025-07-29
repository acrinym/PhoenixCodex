import re
import argparse
import json
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import time
import queue
import asyncio
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict
from modules.amandamap_parser import find_entries, find_thresholds
from modules.json_scanner import scan_json_for_amandamap

# Enhanced regex patterns from Avalonia app
_PHX_RE = re.compile(r"(.*?(?:Phoenix Codex).*?)(?=\n\s*\n|$)", re.IGNORECASE | re.S)
_WHISPER_RE = re.compile(r"(.*?(?:Whispered Flame|Flame Vow).*?)(?=\n\s*\n|$)", re.IGNORECASE | re.S)

# AmandaMap patterns from Avalonia app
_AMANDA_THRESHOLD_PATTERN = re.compile(
    r"AmandaMap Threshold(?:\s*(\d+))?\s*:?(.*?)(?=\n\s*AmandaMap Threshold|$)",
    re.IGNORECASE | re.S
)

_AMANDA_ENTRY_PATTERN = re.compile(
    r"(.*?(?:Archived in the AmandaMap|Logged in the AmandaMap|Logged to the amandamap|log this in the amandamap).*?)(?=\n\s*\n|$)",
    re.IGNORECASE | re.S
)

# Emoji-based numbered entry patterns
_EMOJI_NUMBERED_PATTERN = re.compile(
    r"🔥|🔱|🔊|📡|🕯️|🪞|🌀|🌙|🪧\s*(?P<type>\w+)\s*(?P<number>\d+):(?P<title>.*)",
    re.IGNORECASE
)

# Real-world AmandaMap logging patterns
_AMANDA_LOGGING_PATTERN = re.compile(
    r"(?:Anchoring this as|Adding to|Recording in|AmandaMap update|Logging AmandaMap|Logging to the amandamap|Log this in the amandamap)\s*" +
    r"(?:AmandaMap\s+)?(?:Threshold|Flame Vow|Field Pulse|Whispered Flame)\s*" +
    r"(?:#?\d+)?\s*:?\s*(?P<title>.*?)(?:\s*Status:|$)",
    re.IGNORECASE | re.S
)

_FIELD_PULSE_PATTERN = re.compile(
    r"(?:AmandaMap\s+)?Field Pulse\s*#?\s*(?P<number>\d+)\s*:?\s*(?P<title>.*?)(?:\s*Status:|$)",
    re.IGNORECASE | re.S
)

_WHISPERED_FLAME_PATTERN = re.compile(
    r"(?:AmandaMap\s+)?Whispered Flame\s*#?\s*(?P<number>\d+)\s*:?\s*(?P<title>.*?)(?:\s*Status:|$)",
    re.IGNORECASE | re.S
)

_FLAME_VOW_PATTERN = re.compile(
    r"(?:AmandaMap\s+)?Flame Vow\s*:?\s*(?P<title>.*?)(?:\s*Status:|$)",
    re.IGNORECASE | re.S
)

# Phoenix Codex patterns from Avalonia app
_PHOENIX_CODEX_PATTERN = re.compile(
    r"🪶\s*(?P<title>.*?)(?=\n\s*\n|$)",
    re.IGNORECASE | re.S
)

_PHOENIX_SECTION_PATTERN = re.compile(
    r"(.*?(?:Phoenix Codex|PhoenixCodex).*?)(?=\n\s*\n|$)",
    re.IGNORECASE | re.S
)

_PHOENIX_TOOLS_PATTERN = re.compile(
    r"(.*?(?:Phoenix Codex & Energetic Tools|Phoenix Codex & Tools).*?)(?=\n\s*\n|$)",
    re.IGNORECASE | re.S
)

_PHOENIX_ENTRY_PATTERN = re.compile(
    r"🪶\s*(?P<type>\w+)\s*(?P<number>\d+):(?P<title>.*)",
    re.IGNORECASE
)

# Phoenix Codex logging patterns
_PHOENIX_LOGGING_PATTERN = re.compile(
    r"(?:Anchoring this in|Recording|Logging as|Adding to)\s*Phoenix Codex\s*" +
    r"(?:Threshold|SilentAct|Ritual Log|Collapse Event)\s*" +
    r"(?:#?\d+)?\s*:?\s*(?P<title>.*?)(?:\s*Status:|$)",
    re.IGNORECASE | re.S
)

_PHOENIX_THRESHOLD_PATTERN = re.compile(
    r"(?:Phoenix Codex\s+)?Threshold\s*(?P<number>\d+)?\s*:?\s*(?P<title>.*?)(?:\s*Status:|$)",
    re.IGNORECASE | re.S
)

_PHOENIX_SILENT_ACT_PATTERN = re.compile(
    r"(?:Phoenix Codex\s+)?SilentAct\s*:?\s*(?P<title>.*?)(?:\s*Status:|$)",
    re.IGNORECASE | re.S
)

_PHOENIX_RITUAL_PATTERN = re.compile(
    r"(?:Phoenix Codex\s+)?Ritual Log\s*:?\s*(?P<title>.*?)(?:\s*Status:|$)",
    re.IGNORECASE | re.S
)

_PHOENIX_COLLAPSE_PATTERN = re.compile(
    r"(?:Phoenix Codex\s+)?Collapse Event\s*:?\s*(?P<title>.*?)(?:\s*Status:|$)",
    re.IGNORECASE | re.S
)

# Chat timestamp pattern
_CHAT_TIMESTAMP_PATTERN = re.compile(r"\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\]")

# Amanda chat classification keywords from Avalonia app
_AMANDA_KEYWORDS = [
    "amanda", "she said", "amanda told me", "when we were on the phone", 
    "she just texted me", "she sent me", "amanda just called", "she sent me a message"
]

_AMANDA_GENERIC_PHRASES = [
    "she said", "when we were on the phone", "she just texted me", 
    "she sent me", "just called", "sent me a message"
]

# Phoenix Codex keywords for classification
_PHOENIX_CODEX_KEYWORDS = [
    "phoenix codex", "phoenixcodex", "🪶", "onyx", "akshara", "hermes", 
    "field ethics", "wand cycles", "servitor logs", "ritual formats", 
    "sacred writing", "tone protocols"
]

# Content classification patterns from Avalonia app
_POSITIVE_INDICATORS = [
    # Personal growth language
    "i learned", "i discovered", "i realized", "i understand", "i think", "i believe",
    "personal growth", "self-improvement", "development", "growth", "learning",
    
    # Emotional processing
    "feeling", "emotion", "healing", "emotional", "processing", "reflection",
    "self-reflection", "introspection", "awareness", "consciousness",
    
    # Practical advice
    "how to", "steps to", "tips for", "advice", "strategy", "approach",
    "technique", "method", "process", "guidance", "support",
    
    # Relationship content
    "communication", "understanding", "connection", "relationship", "interaction",
    "dialogue", "conversation", "sharing", "listening", "empathy",
    
    # Life skills
    "organization", "productivity", "time management", "planning", "skills",
    "practical", "real-world", "application", "implementation"
]

_NEGATIVE_INDICATORS = [
    # Magical terms (OFF LIMITS)
    "spell", "ritual", "magic", "witch", "witchcraft", "magical", "enchantment",
    "incantation", "casting", "supernatural", "mystical", "esoteric", "occult",
    "magic user", "practitioner", "wizard", "sorcerer", "mage", "shaman",
    
    # Magical practices
    "casting spells", "performing rituals", "magical practice", "witchcraft practice",
    "magical symbols", "magical tools", "magical ceremonies", "magical traditions",
    
    # Supernatural content
    "supernatural", "paranormal", "mystical", "esoteric", "occult", "divine",
    "spiritual", "metaphysical", "transcendental", "otherworldly"
]


@dataclass
class DatasetEntry:
    file: str
    type: str
    text: str
    number: Optional[int] = None
    is_amanda_related: bool = False
    is_phoenix_codex: bool = False
    confidence: float = 0.0
    category: str = ""
    classification_reason: str = ""


class DatasetBuilderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("📊 AmandaMap Dataset Builder")
        self.root.geometry("700x600")
        self.root.resizable(True, True)
        
        # Variables
        self.input_folder = tk.StringVar()
        self.output_file = tk.StringVar(value="dataset.json")
        self.include_csv = tk.BooleanVar(value=True)
        self.verbose_mode = tk.BooleanVar(value=True)
        self.file_types = tk.StringVar(value="md,txt,json")
        self.max_file_size = tk.IntVar(value=10*1024*1024)  # 10MB
        
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
        
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="📊 AmandaMap Dataset Builder", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Input folder selection
        ttk.Label(main_frame, text="📁 Input Folder:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.input_folder, width=50).grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(5, 5))
        ttk.Button(main_frame, text="Browse", command=self.browse_input_folder).grid(row=1, column=2)
        
        # Output file selection
        ttk.Label(main_frame, text="💾 Output File:").grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.output_file, width=50).grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(5, 5))
        ttk.Button(main_frame, text="Browse", command=self.browse_output_file).grid(row=2, column=2)
        
        # Options frame
        options_frame = ttk.LabelFrame(main_frame, text="⚙️ Options", padding="10")
        options_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=20)
        options_frame.columnconfigure(1, weight=1)
        
        # Checkboxes
        ttk.Checkbutton(options_frame, text="📊 Include CSV output", variable=self.include_csv).grid(row=0, column=0, sticky=tk.W)
        ttk.Checkbutton(options_frame, text="🔍 Verbose mode", variable=self.verbose_mode).grid(row=0, column=1, sticky=tk.W)
        
        # File types
        ttk.Label(options_frame, text="📄 File types:").grid(row=1, column=0, sticky=tk.W, pady=(10, 5))
        ttk.Entry(options_frame, textvariable=self.file_types, width=30).grid(row=1, column=1, sticky=tk.W, padx=(5, 0))
        ttk.Label(options_frame, text="(comma-separated, e.g., md,txt,json)").grid(row=1, column=2, sticky=tk.W, padx=(5, 0))
        
        # Max file size
        ttk.Label(options_frame, text="📏 Max file size (MB):").grid(row=2, column=0, sticky=tk.W, pady=(10, 5))
        self.size_spinbox = ttk.Spinbox(options_frame, from_=1, to=1000, textvariable=tk.IntVar(value=10), width=10)
        self.size_spinbox.grid(row=2, column=1, sticky=tk.W, padx=(5, 0))
        self.size_spinbox.bind('<KeyRelease>', self.update_max_file_size)
        
        # Progress frame
        progress_frame = ttk.LabelFrame(main_frame, text="📈 Progress", padding="10")
        progress_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=20)
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
        
        # Log text area
        log_frame = ttk.LabelFrame(main_frame, text="📝 Log", padding="10")
        log_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=20)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        # Scrollbar for log
        log_scrollbar = ttk.Scrollbar(log_frame)
        log_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Log text widget
        self.log_text = tk.Text(log_frame, height=8, yscrollcommand=log_scrollbar.set)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        log_scrollbar.config(command=self.log_text.yview)
        
        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=6, column=0, columnspan=3, pady=20)
        
        self.process_button = ttk.Button(button_frame, text="🚀 Start Processing", command=self.start_processing)
        self.process_button.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="🗑️ Clear Log", command=self.clear_log).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="❌ Exit", command=self.root.quit).pack(side=tk.LEFT)
        
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
    
    def handle_message(self, message):
        """Handle messages from the processing thread"""
        msg_type = message.get('type')
        
        if msg_type == 'log':
            self.log_message(message['text'])
        elif msg_type == 'progress':
            self.update_progress(message['current'], message['total'], 
                               message.get('status', ''), message.get('file_name', ''))
        elif msg_type == 'stats':
            self.update_stats(message['entries'], message['processed_files'])
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
            
    def browse_output_file(self):
        file = filedialog.asksaveasfilename(
            title="Save Output File",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if file:
            self.output_file.set(file)
            self.log_message(f"💾 Selected output file: {file}")
            
    def update_max_file_size(self, event=None):
        try:
            size_mb = int(event.widget.get())
            self.max_file_size.set(size_mb * 1024 * 1024)
        except ValueError:
            pass
            
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
        
    def start_processing(self):
        if self.is_processing:
            return
            
        input_folder = self.input_folder.get().strip()
        output_file = self.output_file.get().strip()
        
        if not input_folder:
            messagebox.showerror("Error", "Please select an input folder!")
            return
            
        if not output_file:
            messagebox.showerror("Error", "Please specify an output file!")
            return
            
        if not Path(input_folder).exists():
            messagebox.showerror("Error", f"Input folder does not exist: {input_folder}")
            return
            
        # Start processing in a separate thread
        self.is_processing = True
        self.process_button.config(text="⏸️ Processing...", state="disabled")
        self.progress_var.set(0)
        self.clear_log()
        
        self.processing_thread = threading.Thread(
            target=self.process_files_async, 
            args=(input_folder, output_file),
            daemon=True
        )
        self.processing_thread.start()
        
    def process_files_async(self, input_folder, output_file):
        """Process files in a separate thread with async-like behavior"""
        try:
            self.message_queue.put({'type': 'log', 'text': "🚀 Starting dataset building process..."})
            
            folder = Path(input_folder)
            file_types = [ft.strip() for ft in self.file_types.get().split(",")]
            max_size = self.max_file_size.get()
            
            self.message_queue.put({'type': 'log', 'text': f"📁 Input folder: {input_folder}"})
            self.message_queue.put({'type': 'log', 'text': f"💾 Output file: {output_file}"})
            self.message_queue.put({'type': 'log', 'text': f"📄 File types: {', '.join(file_types)}"})
            self.message_queue.put({'type': 'log', 'text': f"📏 Max file size: {max_size // (1024*1024)}MB"})
            
            # Count total files
            total_files = 0
            for file_type in file_types:
                total_files += len(list(folder.rglob(f"*.{file_type}")))
                
            self.message_queue.put({'type': 'log', 'text': f"🔍 Found {total_files} files to process"})
            
            if total_files == 0:
                self.message_queue.put({'type': 'log', 'text': "⚠️ No files found to process!"})
                self.message_queue.put({'type': 'finished'})
                return
                
            # Process files in batches for better responsiveness
            entries = []
            processed_files = 0
            batch_size = 10  # Process 10 files at a time
            
            for file_type in file_types:
                file_paths = list(folder.rglob(f"*.{file_type}"))
                
                for i in range(0, len(file_paths), batch_size):
                    batch = file_paths[i:i + batch_size]
                    
                    for path in batch:
                        if path.stat().st_size > max_size:
                            if self.verbose_mode.get():
                                self.message_queue.put({
                                    'type': 'log', 
                                    'text': f"⏭️ Skipping large file: {path.name} ({path.stat().st_size // 1024}KB)"
                                })
                            continue
                            
                        processed_files += 1
                        self.message_queue.put({
                            'type': 'progress',
                            'current': processed_files,
                            'total': total_files,
                            'status': f"Processing file {processed_files} of {total_files}",
                            'file_name': path.name
                        })
                        
                        try:
                            if file_type == "json":
                                th, en = scan_json_for_amandamap(path)
                                for num, seg in th:
                                    entries.append(
                                        DatasetEntry(file=str(path), type="Threshold", text=seg, number=num)
                                    )
                                for seg in en:
                                    entries.append(DatasetEntry(file=str(path), type="AmandaMap", text=seg))
                            else:
                                entries.extend(scan_file_enhanced(path))
                                
                            if self.verbose_mode.get():
                                self.message_queue.put({'type': 'log', 'text': f"✅ Processed: {path.name}"})
                                
                        except Exception as e:
                            self.message_queue.put({'type': 'log', 'text': f"⚠️ Error processing {path.name}: {e}"})
                    
                    # Small delay to keep GUI responsive
                    time.sleep(0.01)
                        
            # Write output
            self.message_queue.put({'type': 'log', 'text': f"\n📊 Processing complete!"})
            self.message_queue.put({'type': 'log', 'text': f"📈 Found {len(entries)} entries across {processed_files} files"})
            
            # Group entries by type
            entry_types = {}
            for entry in entries:
                entry_types[entry.type] = entry_types.get(entry.type, 0) + 1
                
            self.message_queue.put({'type': 'log', 'text': "📊 Entry breakdown:"})
            for entry_type, count in entry_types.items():
                self.message_queue.put({'type': 'log', 'text': f"   • {entry_type}: {count} entries"})
                
            # Write JSON
            try:
                with open(output_file, "w", encoding="utf-8") as f:
                    json.dump([asdict(e) for e in entries], f, indent=2)
                self.message_queue.put({'type': 'log', 'text': f"💾 Successfully wrote {len(entries)} entries to {output_file}"})
            except Exception as e:
                self.message_queue.put({'type': 'error', 'text': f"Error writing JSON file: {e}"})
                return
                
            # Write CSV if requested
            if self.include_csv.get():
                try:
                    import csv
                    csv_path = Path(output_file).with_suffix(".csv")
                    with csv_path.open("w", newline="", encoding="utf-8") as fcsv:
                        writer = csv.DictWriter(fcsv, fieldnames=["file", "type", "text", "number"])
                        writer.writeheader()
                        for e in entries:
                            writer.writerow(asdict(e))
                    self.message_queue.put({'type': 'log', 'text': f"📊 Successfully wrote CSV output to {csv_path}"})
                except Exception as e:
                    self.message_queue.put({'type': 'log', 'text': f"❌ Error writing CSV file: {e}"})
                    
            self.message_queue.put({'type': 'log', 'text': "🎉 Dataset building complete! Your data is ready for analysis."})
            self.message_queue.put({
                'type': 'progress',
                'current': total_files,
                'total': total_files,
                'status': "✅ Processing complete!"
            })
            
            # Update stats
            self.message_queue.put({
                'type': 'stats',
                'entries': entries,
                'processed_files': processed_files
            })
            
        except Exception as e:
            self.message_queue.put({'type': 'error', 'text': f"Fatal error: {e}"})
        finally:
            self.message_queue.put({'type': 'finished'})
            
    def finish_processing(self):
        self.is_processing = False
        self.process_button.config(text="🚀 Start Processing", state="normal")
        
    def update_stats(self, entries, processed_files):
        if entries:
            entry_types = {}
            for entry in entries:
                entry_types[entry.type] = entry_types.get(entry.type, 0) + 1
                
            stats_text = f"📊 Results: {len(entries)} entries from {processed_files} files"
            self.stats_label.config(text=stats_text)
        else:
            self.stats_label.config(text="")


def is_amanda_related_chat(chat_text: str) -> bool:
    """Determines if a chat message is Amanda-related based on keywords/phrases."""
    if not chat_text or not chat_text.strip():
        return False
    
    text = chat_text.lower()
    has_amanda = "amanda" in text
    
    for keyword in _AMANDA_KEYWORDS:
        if keyword.lower() in text:
            # If it's a generic phrase, require 'amanda' also present
            if keyword.lower() in _AMANDA_GENERIC_PHRASES:
                return has_amanda
            return True
    
    return False


def is_phoenix_codex_related_chat(chat_text: str) -> bool:
    """Determines if a chat message is Phoenix Codex related."""
    if not chat_text or not chat_text.strip():
        return False
    
    text = chat_text.lower()
    
    for keyword in _PHOENIX_CODEX_KEYWORDS:
        if keyword.lower() in text:
            return True
    
    return False


def classify_content(content: str) -> Tuple[bool, float, str, str]:
    """Classify content using the same logic as the Avalonia app."""
    if not content or not content.strip():
        return False, 0.0, "", ""
    
    text = content.lower()
    positive_score = 0
    negative_score = 0
    
    # Count positive indicators
    for indicator in _POSITIVE_INDICATORS:
        if indicator.lower() in text:
            positive_score += 1
    
    # Count negative indicators
    for indicator in _NEGATIVE_INDICATORS:
        if indicator.lower() in text:
            negative_score += 1
    
    # Calculate confidence
    total_indicators = positive_score + negative_score
    if total_indicators == 0:
        return False, 0.0, "", ""
    
    confidence = positive_score / total_indicators if total_indicators > 0 else 0.0
    is_phoenix_codex = positive_score > negative_score and confidence > 0.6
    
    # Generate reason
    reason = f"Positive indicators: {positive_score}, Negative indicators: {negative_score}, Confidence: {confidence:.2f}"
    
    # Determine category
    category = "Personal Growth" if positive_score > negative_score else "Other"
    
    return is_phoenix_codex, confidence, reason, category


def extract_date_from_text(text: str) -> str:
    """Extract date from text using various patterns."""
    # Try chat timestamp pattern
    timestamp_match = _CHAT_TIMESTAMP_PATTERN.search(text)
    if timestamp_match:
        return timestamp_match.group(1)
    
    # Try other date patterns
    date_patterns = [
        r"(\d{4}-\d{2}-\d{2})",
        r"(\d{2}/\d{2}/\d{4})",
        r"(\d{2}-\d{2}-\d{4})",
    ]
    
    for pattern in date_patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1)
    
    return ""


def extract_title_from_text(text: str) -> str:
    """Extract title from text."""
    lines = text.split('\n')
    for line in lines:
        line = line.strip()
        if line and not line.startswith('#') and not line.startswith('['):
            return line[:100]  # Limit title length
    return "Untitled"


def extract_content_after_match(full_content: str, match) -> str:
    """Extract content after a regex match."""
    start_pos = match.end()
    end_pos = full_content.find('\n\n', start_pos)
    if end_pos == -1:
        end_pos = len(full_content)
    
    return full_content[start_pos:end_pos].strip()


def scan_file_enhanced(path: Path) -> List[DatasetEntry]:
    """Enhanced file scanning with all patterns from Avalonia app."""
    text = path.read_text(encoding="utf-8", errors="ignore")
    entries: List[DatasetEntry] = []
    
    # Extract AmandaMap Threshold entries
    for match in _AMANDA_THRESHOLD_PATTERN.finditer(text):
        number_group = match.group(1)
        text_group = match.group(2)
        
        number = int(number_group) if number_group else None
        raw_content = text_group.strip()
        
        entry = DatasetEntry(
            file=str(path),
            type="Threshold",
            text=raw_content,
            number=number,
            is_amanda_related=is_amanda_related_chat(raw_content)
        )
        entries.append(entry)
    
    # Extract emoji-based numbered entries
    for match in _EMOJI_NUMBERED_PATTERN.finditer(text):
        entry_type = match.group("type").strip()
        number_str = match.group("number")
        title = match.group("title").strip()
        
        if number_str:
            number = int(number_str)
            raw_content = extract_content_after_match(text, match)
            
            entry = DatasetEntry(
                file=str(path),
                type=entry_type,
                text=raw_content,
                number=number,
                is_amanda_related=is_amanda_related_chat(raw_content)
            )
            entries.append(entry)
    
    # Extract real-world AmandaMap logging statements
    for match in _AMANDA_LOGGING_PATTERN.finditer(text):
        title = match.group("title").strip()
        if title:
            raw_content = extract_content_after_match(text, match)
            
            entry = DatasetEntry(
                file=str(path),
                type="AmandaMap",
                text=raw_content,
                is_amanda_related=is_amanda_related_chat(raw_content)
            )
            entries.append(entry)
    
    # Extract Field Pulse entries
    for match in _FIELD_PULSE_PATTERN.finditer(text):
        number_str = match.group("number")
        title = match.group("title").strip()
        raw_content = extract_content_after_match(text, match)
        
        number = int(number_str) if number_str else None
        
        entry = DatasetEntry(
            file=str(path),
            type="FieldPulse",
            text=raw_content,
            number=number,
            is_amanda_related=is_amanda_related_chat(raw_content)
        )
        entries.append(entry)
    
    # Extract Whispered Flame entries
    for match in _WHISPERED_FLAME_PATTERN.finditer(text):
        number_str = match.group("number")
        title = match.group("title").strip()
        raw_content = extract_content_after_match(text, match)
        
        number = int(number_str) if number_str else None
        
        entry = DatasetEntry(
            file=str(path),
            type="WhisperedFlame",
            text=raw_content,
            number=number,
            is_amanda_related=is_amanda_related_chat(raw_content)
        )
        entries.append(entry)
    
    # Extract Flame Vow entries
    for match in _FLAME_VOW_PATTERN.finditer(text):
        title = match.group("title").strip()
        raw_content = extract_content_after_match(text, match)
        
        entry = DatasetEntry(
            file=str(path),
            type="FlameVow",
            text=raw_content,
            is_amanda_related=is_amanda_related_chat(raw_content)
        )
        entries.append(entry)
    
    # Extract Phoenix Codex entries
    for match in _PHOENIX_CODEX_PATTERN.finditer(text):
        title = match.group("title").strip()
        raw_content = extract_content_after_match(text, match)
        
        is_phoenix, confidence, reason, category = classify_content(raw_content)
        
        entry = DatasetEntry(
            file=str(path),
            type="PhoenixCodex",
            text=raw_content,
            is_phoenix_codex=is_phoenix,
            confidence=confidence,
            category=category,
            classification_reason=reason
        )
        entries.append(entry)
    
    # Extract Phoenix Codex numbered entries
    for match in _PHOENIX_ENTRY_PATTERN.finditer(text):
        entry_type = match.group("type").strip()
        number_str = match.group("number")
        title = match.group("title").strip()
        
        if number_str:
            number = int(number_str)
            raw_content = extract_content_after_match(text, match)
            
            is_phoenix, confidence, reason, category = classify_content(raw_content)
            
            entry = DatasetEntry(
                file=str(path),
                type=f"PhoenixCodex{entry_type}",
                text=raw_content,
                number=number,
                is_phoenix_codex=is_phoenix,
                confidence=confidence,
                category=category,
                classification_reason=reason
            )
            entries.append(entry)
    
    # Extract Phoenix Codex logging statements
    for match in _PHOENIX_LOGGING_PATTERN.finditer(text):
        title = match.group("title").strip()
        raw_content = extract_content_after_match(text, match)
        
        is_phoenix, confidence, reason, category = classify_content(raw_content)
        
        entry = DatasetEntry(
            file=str(path),
            type="PhoenixCodex",
            text=raw_content,
            is_phoenix_codex=is_phoenix,
            confidence=confidence,
            category=category,
            classification_reason=reason
        )
        entries.append(entry)
    
    # Extract Phoenix Codex Threshold entries
    for match in _PHOENIX_THRESHOLD_PATTERN.finditer(text):
        number_str = match.group("number")
        title = match.group("title").strip()
        raw_content = extract_content_after_match(text, match)
        
        number = int(number_str) if number_str else None
        is_phoenix, confidence, reason, category = classify_content(raw_content)
        
        entry = DatasetEntry(
            file=str(path),
            type="PhoenixCodexThreshold",
            text=raw_content,
            number=number,
            is_phoenix_codex=is_phoenix,
            confidence=confidence,
            category=category,
            classification_reason=reason
        )
        entries.append(entry)
    
    # Extract Phoenix Codex Silent Act entries
    for match in _PHOENIX_SILENT_ACT_PATTERN.finditer(text):
        title = match.group("title").strip()
        raw_content = extract_content_after_match(text, match)
        
        is_phoenix, confidence, reason, category = classify_content(raw_content)
        
        entry = DatasetEntry(
            file=str(path),
            type="PhoenixCodexSilentAct",
            text=raw_content,
            is_phoenix_codex=is_phoenix,
            confidence=confidence,
            category=category,
            classification_reason=reason
        )
        entries.append(entry)
    
    # Extract Phoenix Codex Ritual entries
    for match in _PHOENIX_RITUAL_PATTERN.finditer(text):
        title = match.group("title").strip()
        raw_content = extract_content_after_match(text, match)
        
        is_phoenix, confidence, reason, category = classify_content(raw_content)
        
        entry = DatasetEntry(
            file=str(path),
            type="PhoenixCodexRitual",
            text=raw_content,
            is_phoenix_codex=is_phoenix,
            confidence=confidence,
            category=category,
            classification_reason=reason
        )
        entries.append(entry)
    
    # Extract Phoenix Codex Collapse entries
    for match in _PHOENIX_COLLAPSE_PATTERN.finditer(text):
        title = match.group("title").strip()
        raw_content = extract_content_after_match(text, match)
        
        is_phoenix, confidence, reason, category = classify_content(raw_content)
        
        entry = DatasetEntry(
            file=str(path),
            type="PhoenixCodexCollapse",
            text=raw_content,
            is_phoenix_codex=is_phoenix,
            confidence=confidence,
            category=category,
            classification_reason=reason
        )
        entries.append(entry)
    
    # Also run the original patterns for backward compatibility
    for num, seg in find_thresholds(text):
        entries.append(
            DatasetEntry(
                file=str(path),
                type="Threshold",
                text=seg,
                number=num,
                is_amanda_related=is_amanda_related_chat(seg)
            )
        )

    for seg in find_entries(text):
        entries.append(DatasetEntry(
            file=str(path), 
            type="AmandaMap", 
            text=seg,
            is_amanda_related=is_amanda_related_chat(seg)
        ))

    for seg in extract_keyword_segments(text, "AmandaMap"):
        if seg.lower() not in [e.text.lower() for e in entries]:
            entries.append(DatasetEntry(
                file=str(path), 
                type="AmandaMap", 
                text=seg,
                is_amanda_related=is_amanda_related_chat(seg)
            ))

    for seg in extract_phoenix_entries(text):
        is_phoenix, confidence, reason, category = classify_content(seg)
        entries.append(DatasetEntry(
            file=str(path), 
            type="PhoenixCodex", 
            text=seg,
            is_phoenix_codex=is_phoenix,
            confidence=confidence,
            category=category,
            classification_reason=reason
        ))

    for seg in extract_whisper_entries(text):
        entries.append(DatasetEntry(
            file=str(path), 
            type="WhisperedFlame", 
            text=seg,
            is_amanda_related=is_amanda_related_chat(seg)
        ))
    
    return entries


def _next_paragraphs(paragraphs: List[str], i: int) -> str:
    parts = [paragraphs[i]]
    if i + 1 < len(paragraphs):
        parts.append(paragraphs[i + 1])
    return '\n\n'.join(parts)


def extract_keyword_segments(text: str, keyword: str) -> List[str]:
    paragraphs = re.split(r"\n\s*\n", text)
    result = []
    for idx, para in enumerate(paragraphs):
        if keyword.lower() in para.lower():
            result.append(_next_paragraphs(paragraphs, idx).strip())
    return result


def extract_phoenix_entries(text: str) -> List[str]:
    return [m.group(1).strip() for m in _PHX_RE.finditer(text)]


def extract_whisper_entries(text: str) -> List[str]:
    return [m.group(1).strip() for m in _WHISPER_RE.finditer(text)]


if __name__ == "__main__":
    root = tk.Tk()
    app = DatasetBuilderGUI(root)
    root.mainloop()

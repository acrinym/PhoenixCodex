#!/usr/bin/env python3
"""
Enhanced Dataset Builder with Advanced Performance Settings

Features:
- Multi-threading with configurable thread count
- CPU usage control and monitoring
- CUDA/GPU acceleration support
- RAM-based processing with disk streaming
- Advanced caching and memory management
- Real-time performance monitoring
- Configurable batch processing
- Progress tracking with detailed metrics
"""

import re
import argparse
import json
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import time
import queue
import asyncio
import multiprocessing
import psutil
import os
import gc
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass, asdict, field
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
import logging
import numpy as np
from collections import defaultdict, deque
import pickle
import tempfile
import shutil

# Try to import CUDA-related libraries
try:
    import cupy as cp
    import cupyx.scipy.ndimage as cp_ndimage
    CUDA_AVAILABLE = True
except ImportError:
    CUDA_AVAILABLE = False

try:
    import torch
    import torch.nn.functional as F
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

# Import existing modules
from modules.amandamap_parser import find_entries, find_thresholds
from modules.json_scanner import scan_json_for_amandamap
from modules.performance_optimizer import PerformanceOptimizer, OptimizationConfig
from modules.settings_service import SettingsService

# Enhanced regex patterns (same as original)
_PHX_RE = re.compile(r"(.*?(?:Phoenix Codex).*?)(?=\n\s*\n|$)", re.IGNORECASE | re.S)
_WHISPER_RE = re.compile(r"(.*?(?:Whispered Flame|Flame Vow).*?)(?=\n\s*\n|$)", re.IGNORECASE | re.S)

# AmandaMap patterns
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

# Phoenix Codex patterns
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

# Classification keywords
_AMANDA_KEYWORDS = [
    "amanda", "she said", "amanda told me", "when we were on the phone", 
    "she just texted me", "she sent me", "amanda just called", "she sent me a message"
]

_AMANDA_GENERIC_PHRASES = [
    "she said", "when we were on the phone", "she just texted me", 
    "she sent me", "just called", "sent me a message"
]

_PHOENIX_CODEX_KEYWORDS = [
    "phoenix codex", "phoenixcodex", "🪶", "onyx", "akshara", "hermes", 
    "field ethics", "wand cycles", "servitor logs", "ritual formats", 
    "sacred writing", "tone protocols"
]

_POSITIVE_INDICATORS = [
    "i learned", "i discovered", "i realized", "i understand", "i think", "i believe",
    "personal growth", "self-improvement", "development", "growth", "learning",
    "feeling", "emotion", "healing", "emotional", "processing", "reflection",
    "self-reflection", "introspection", "awareness", "consciousness",
    "how to", "steps to", "tips for", "advice", "strategy", "approach",
    "technique", "method", "process", "guidance", "support",
    "communication", "understanding", "connection", "relationship", "interaction",
    "dialogue", "conversation", "sharing", "listening", "empathy",
    "organization", "productivity", "time management", "planning", "skills",
    "practical", "real-world", "application", "implementation"
]

_NEGATIVE_INDICATORS = [
    "spell", "ritual", "magic", "witch", "witchcraft", "magical", "enchantment",
    "incantation", "casting", "supernatural", "mystical", "esoteric", "occult",
    "magic user", "practitioner", "wizard", "sorcerer", "mage", "shaman",
    "casting spells", "performing rituals", "magical practice", "witchcraft practice",
    "magical symbols", "magical tools", "magical ceremonies", "magical traditions",
    "supernatural", "paranormal", "mystical", "esoteric", "occult", "divine",
    "spiritual", "metaphysical", "transcendental", "otherworldly"
]


@dataclass
class DatasetEntry:
    file: str
    type: str
    text: str
    number: Optional[int] = None
    sequential_id: Optional[str] = None  # For handling duplicates like "23a", "23b"
    is_amanda_related: bool = False
    is_phoenix_codex: bool = False
    confidence: float = 0.0
    category: str = ""
    classification_reason: str = ""
    processing_time: float = 0.0
    memory_usage: int = 0


@dataclass
class PerformanceSettings:
    """Advanced performance configuration settings."""
    # Threading settings
    max_threads: int = min(multiprocessing.cpu_count(), 8)
    use_multiprocessing: bool = False
    thread_pool_size: int = 4
    
    # CPU usage control
    max_cpu_percent: float = 80.0
    cpu_affinity: Optional[List[int]] = None
    enable_cpu_monitoring: bool = True
    
    # Memory settings
    max_memory_usage_gb: float = 4.0
    memory_warning_threshold_gb: float = 3.0
    enable_memory_monitoring: bool = True
    auto_garbage_collection: bool = True
    gc_threshold: int = 1000  # Objects before GC
    
    # CUDA/GPU settings
    enable_cuda: bool = False
    cuda_device: int = 0
    gpu_memory_limit_gb: float = 2.0
    use_mixed_precision: bool = True
    
    # Processing settings
    batch_size: int = 100
    chunk_size: int = 8192
    use_ram_processing: bool = True
    ram_buffer_size_mb: int = 512
    enable_streaming: bool = True
    
    # Caching settings
    enable_file_cache: bool = True
    cache_size_mb: int = 100
    enable_result_cache: bool = True
    result_cache_size: int = 1000
    
    # Monitoring settings
    enable_performance_monitoring: bool = True
    log_performance_metrics: bool = True
    performance_log_interval: int = 30  # seconds
    
    # File processing settings
    max_file_size_mb: int = 50
    skip_large_files: bool = True
    enable_file_compression: bool = False
    compression_level: int = 6
    
    # Output settings
    enable_progress_tracking: bool = True
    progress_update_interval: float = 0.5  # seconds
    enable_detailed_logging: bool = True
    
    def __post_init__(self):
        """Validate and adjust settings based on system capabilities."""
        # Adjust thread count based on CPU cores
        cpu_count = multiprocessing.cpu_count()
        if self.max_threads > cpu_count:
            self.max_threads = cpu_count
        
        # Check CUDA availability
        if self.enable_cuda and not CUDA_AVAILABLE:
            self.enable_cuda = False
            print("⚠️ CUDA not available, disabling GPU acceleration")
        
        # Check PyTorch availability
        if self.enable_cuda and not TORCH_AVAILABLE:
            self.enable_cuda = False
            print("⚠️ PyTorch not available, disabling GPU acceleration")
        
        # Adjust memory settings based on system
        total_memory = psutil.virtual_memory().total / (1024**3)  # GB
        if self.max_memory_usage_gb > total_memory * 0.8:
            self.max_memory_usage_gb = total_memory * 0.8
            print(f"⚠️ Adjusted max memory usage to {self.max_memory_usage_gb:.1f}GB")


@dataclass
class ProcessingMetrics:
    """Tracks processing performance metrics."""
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None
    total_files: int = 0
    processed_files: int = 0
    total_entries: int = 0
    memory_peak_mb: float = 0.0
    cpu_peak_percent: float = 0.0
    gpu_memory_peak_mb: float = 0.0
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    @property
    def duration(self) -> float:
        return (self.end_time or time.time()) - self.start_time
    
    @property
    def files_per_second(self) -> float:
        if self.duration > 0:
            return self.processed_files / self.duration
        return 0.0
    
    @property
    def entries_per_second(self) -> float:
        if self.duration > 0:
            return self.total_entries / self.duration
        return 0.0


class PerformanceMonitor:
    """Monitors system performance during processing."""
    
    def __init__(self, settings: PerformanceSettings):
        self.settings = settings
        self.process = psutil.Process()
        self.metrics_history = deque(maxlen=1000)
        self.start_time = time.time()
        
    def get_current_metrics(self) -> Dict[str, float]:
        """Get current system metrics."""
        memory = psutil.virtual_memory()
        cpu_percent = psutil.cpu_percent(interval=0.1)
        
        metrics = {
            'memory_usage_mb': memory.used / (1024 * 1024),
            'memory_percent': memory.percent,
            'cpu_percent': cpu_percent,
            'process_memory_mb': self.process.memory_info().rss / (1024 * 1024),
            'process_cpu_percent': self.process.cpu_percent(),
            'uptime': time.time() - self.start_time
        }
        
        # GPU metrics if CUDA is available
        if self.settings.enable_cuda and CUDA_AVAILABLE:
            try:
                gpu_memory = cp.cuda.runtime.memGetInfo()
                metrics['gpu_memory_used_mb'] = (gpu_memory[1] - gpu_memory[0]) / (1024 * 1024)
                metrics['gpu_memory_total_mb'] = gpu_memory[1] / (1024 * 1024)
            except Exception as e:
                metrics['gpu_memory_error'] = str(e)
        
        self.metrics_history.append(metrics)
        return metrics
    
    def check_resource_limits(self) -> Tuple[bool, List[str]]:
        """Check if resource usage is within limits."""
        metrics = self.get_current_metrics()
        warnings = []
        
        # Memory check
        if metrics['memory_percent'] > 90:
            warnings.append(f"High memory usage: {metrics['memory_percent']:.1f}%")
        
        if metrics['process_memory_mb'] > self.settings.max_memory_usage_gb * 1024:
            warnings.append(f"Process memory limit exceeded: {metrics['process_memory_mb']:.1f}MB")
        
        # CPU check
        if metrics['cpu_percent'] > self.settings.max_cpu_percent:
            warnings.append(f"High CPU usage: {metrics['cpu_percent']:.1f}%")
        
        # GPU check
        if self.settings.enable_cuda and 'gpu_memory_used_mb' in metrics:
            if metrics['gpu_memory_used_mb'] > self.settings.gpu_memory_limit_gb * 1024:
                warnings.append(f"GPU memory limit exceeded: {metrics['gpu_memory_used_mb']:.1f}MB")
        
        return len(warnings) == 0, warnings
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary statistics."""
        if not self.metrics_history:
            return {}
        
        memory_values = [m['memory_usage_mb'] for m in self.metrics_history]
        cpu_values = [m['cpu_percent'] for m in self.metrics_history]
        
        summary = {
            'avg_memory_mb': np.mean(memory_values),
            'max_memory_mb': np.max(memory_values),
            'avg_cpu_percent': np.mean(cpu_values),
            'max_cpu_percent': np.max(cpu_values),
            'total_samples': len(self.metrics_history),
            'monitoring_duration': time.time() - self.start_time
        }
        
        return summary


class MemoryManager:
    """Manages memory usage and optimization."""
    
    def __init__(self, settings: PerformanceSettings):
        self.settings = settings
        self.process = psutil.Process()
        self.gc_counter = 0
        
    def get_memory_usage(self) -> float:
        """Get current memory usage in MB."""
        return self.process.memory_info().rss / (1024 * 1024)
    
    def check_memory_limit(self) -> bool:
        """Check if memory usage is within limits."""
        return self.get_memory_usage() < self.settings.max_memory_usage_gb * 1024
    
    def force_garbage_collection(self) -> int:
        """Force garbage collection and return collected objects count."""
        collected = gc.collect()
        self.gc_counter += 1
        return collected
    
    def optimize_memory(self) -> Dict[str, Any]:
        """Perform memory optimization."""
        before_memory = self.get_memory_usage()
        
        # Force garbage collection
        collected = self.force_garbage_collection()
        
        # Clear caches if memory is still high
        if self.get_memory_usage() > self.settings.memory_warning_threshold_gb * 1024:
            # Clear Python's internal caches
            import sys
            sys.modules.clear()
            
        after_memory = self.get_memory_usage()
        
        return {
            'before_mb': before_memory,
            'after_mb': after_memory,
            'freed_mb': before_memory - after_memory,
            'collected_objects': collected
        }


class CUDAProcessor:
    """Handles CUDA/GPU acceleration for text processing."""
    
    def __init__(self, settings: PerformanceSettings):
        self.settings = settings
        self.device = None
        self.initialized = False
        
        if settings.enable_cuda and CUDA_AVAILABLE:
            try:
                self.device = cp.cuda.Device(settings.cuda_device)
                self.device.use()
                self.initialized = True
                print(f"✅ CUDA initialized on device {settings.cuda_device}")
            except Exception as e:
                print(f"❌ CUDA initialization failed: {e}")
                self.initialized = False
    
    def is_available(self) -> bool:
        """Check if CUDA processing is available."""
        return self.initialized and self.settings.enable_cuda
    
    def process_text_batch(self, texts: List[str]) -> List[Dict[str, Any]]:
        """Process a batch of texts using GPU acceleration."""
        if not self.is_available():
            return []
        
        try:
            # Convert texts to GPU arrays
            text_lengths = [len(text) for text in texts]
            max_length = max(text_lengths)
            
            # Pad texts to uniform length
            padded_texts = [text.ljust(max_length) for text in texts]
            
            # Convert to GPU arrays
            text_arrays = cp.array([list(text.encode('utf-8')) for text in padded_texts])
            
            # Perform GPU-accelerated text analysis
            # This is a simplified example - in practice, you'd implement more sophisticated
            # text processing algorithms that benefit from GPU parallelism
            
            # Character frequency analysis
            char_counts = cp.sum(text_arrays > 0, axis=1)
            
            # Convert back to CPU
            results = []
            for i, text in enumerate(texts):
                results.append({
                    'text': text,
                    'length': int(char_counts[i]),
                    'processed_on_gpu': True
                })
            
            return results
            
        except Exception as e:
            print(f"❌ GPU processing error: {e}")
            return []
    
    def cleanup(self):
        """Clean up GPU memory."""
        if self.is_available():
            try:
                cp.get_default_memory_pool().free_all_blocks()
                print("✅ GPU memory cleaned up")
            except Exception as e:
                print(f"❌ GPU cleanup error: {e}")


class SequentialNumberManager:
    """Manages sequential numbering and handles duplicates with letter suffixes."""
    
    def __init__(self):
        self.amandamap_numbers = {}  # {number: count} for AmandaMap entries
        self.phoenix_numbers = {}    # {number: count} for Phoenix Codex entries
        self.amandamap_entries = []  # List of all AmandaMap entries
        self.phoenix_entries = []    # List of all Phoenix Codex entries
    
    def get_sequential_id(self, number: int, entry_type: str) -> str:
        """Generate sequential ID with letter suffix for duplicates."""
        if entry_type.lower().startswith('amandamap') or entry_type.lower() in ['threshold', 'fieldpulse', 'whisperedflame', 'flamevow']:
            # AmandaMap entries
            if number not in self.amandamap_numbers:
                self.amandamap_numbers[number] = 1
                return str(number)
            else:
                self.amandamap_numbers[number] += 1
                return f"{number}{chr(96 + self.amandamap_numbers[number])}"  # a, b, c, etc.
        else:
            # Phoenix Codex entries
            if number not in self.phoenix_numbers:
                self.phoenix_numbers[number] = 1
                return str(number)
            else:
                self.phoenix_numbers[number] += 1
                return f"{number}{chr(96 + self.phoenix_numbers[number])}"  # a, b, c, etc.
    
    def add_entry(self, entry: 'DatasetEntry'):
        """Add entry to the appropriate list."""
        if entry.is_amanda_related or entry.type.lower().startswith('amandamap') or entry.type.lower() in ['threshold', 'fieldpulse', 'whisperedflame', 'flamevow']:
            self.amandamap_entries.append(entry)
        elif entry.is_phoenix_codex or entry.type.lower().startswith('phoenix'):
            self.phoenix_entries.append(entry)
    
    def get_amandamap_entries(self) -> List['DatasetEntry']:
        """Get all AmandaMap entries."""
        return self.amandamap_entries
    
    def get_phoenix_entries(self) -> List['DatasetEntry']:
        """Get all Phoenix Codex entries."""
        return self.phoenix_entries


class FileProcessor:
    """Handles file processing with advanced features."""
    
    def __init__(self, settings: PerformanceSettings):
        self.settings = settings
        self.memory_manager = MemoryManager(settings)
        self.cuda_processor = CUDAProcessor(settings)
        self.file_cache = {}
        self.result_cache = {}
        self.sequential_manager = SequentialNumberManager()
        self.verbose_mode = True  # Default to verbose mode
        
    def should_process_file(self, file_path: Path) -> Tuple[bool, str]:
        """Check if file should be processed based on size and type."""
        try:
            file_size = file_path.stat().st_size
            file_size_mb = file_size / (1024 * 1024)
            
            if file_size_mb > self.settings.max_file_size_mb:
                return False, f"File too large: {file_size_mb:.1f}MB"
            
            return True, "OK"
            
        except Exception as e:
            return False, f"Error checking file: {e}"
    
    def read_file_optimized(self, file_path: Path) -> str:
        """Read file with optimization and caching."""
        # Check cache first
        if self.settings.enable_file_cache and str(file_path) in self.file_cache:
            return self.file_cache[str(file_path)]
        
        try:
            # Read file in chunks for large files
            if file_path.stat().st_size > self.settings.chunk_size * 10:
                content = ""
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    while True:
                        chunk = f.read(self.settings.chunk_size)
                        if not chunk:
                            break
                        content += chunk
            else:
                content = file_path.read_text(encoding='utf-8', errors='ignore')
            
            # Cache the result
            if self.settings.enable_file_cache:
                self.file_cache[str(file_path)] = content
            
            return content
            
        except Exception as e:
            print(f"❌ Error reading file {file_path}: {e}")
            return ""
    
    def process_file_batch(self, file_paths: List[Path]) -> List[DatasetEntry]:
        """Process a batch of files with optimization."""
        entries = []
        
        for file_path in file_paths:
            should_process, reason = self.should_process_file(file_path)
            if not should_process:
                print(f"⏭️ Skipping {file_path.name}: {reason}")
                continue
            
            try:
                start_time = time.time()
                content = self.read_file_optimized(file_path)
                
                # Process content
                file_entries = self.scan_file_enhanced(file_path, content)
                
                # Add processing metrics
                processing_time = time.time() - start_time
                memory_usage = self.memory_manager.get_memory_usage()
                
                for entry in file_entries:
                    entry.processing_time = processing_time
                    entry.memory_usage = int(memory_usage * 1024 * 1024)  # Convert to bytes
                
                entries.extend(file_entries)
                
                # Memory management
                if self.memory_manager.get_memory_usage() > self.settings.memory_warning_threshold_gb * 1024:
                    self.memory_manager.optimize_memory()
                
            except Exception as e:
                print(f"❌ Error processing {file_path}: {e}")
        
        return entries
    
    def scan_file_enhanced(self, path: Path, text: str) -> List[DatasetEntry]:
        """Enhanced file scanning with all patterns."""
        entries: List[DatasetEntry] = []
        
        # Extract AmandaMap Threshold entries
        for match in _AMANDA_THRESHOLD_PATTERN.finditer(text):
            number_group = match.group(1)
            text_group = match.group(2)
            
            if text_group is None:
                continue
                
            number = int(number_group) if number_group else None
            raw_content = text_group.strip()
            
            # Generate sequential ID for duplicates
            sequential_id = None
            if number is not None:
                sequential_id = self.sequential_manager.get_sequential_id(number, "Threshold")
            
            entry = DatasetEntry(
                file=str(path),
                type="Threshold",
                text=raw_content,
                number=number,
                sequential_id=sequential_id,
                is_amanda_related=self.is_amanda_related_chat(raw_content)
            )
            entries.append(entry)
            self.sequential_manager.add_entry(entry)
        
        # Extract emoji-based numbered entries
        for match in _EMOJI_NUMBERED_PATTERN.finditer(text):
            entry_type_group = match.group("type")
            number_str = match.group("number")
            title_group = match.group("title")
            
            if entry_type_group is None or title_group is None:
                continue
                
            entry_type = entry_type_group.strip()
            title = title_group.strip()
            
            if number_str:
                number = int(number_str)
                raw_content = self.extract_content_after_match(text, match)
                
                # Generate sequential ID for duplicates
                sequential_id = self.sequential_manager.get_sequential_id(number, entry_type)
                
                entry = DatasetEntry(
                    file=str(path),
                    type=entry_type,
                    text=raw_content,
                    number=number,
                    sequential_id=sequential_id,
                    is_amanda_related=self.is_amanda_related_chat(raw_content)
                )
                entries.append(entry)
                self.sequential_manager.add_entry(entry)
        
        # Extract real-world AmandaMap logging statements
        for match in _AMANDA_LOGGING_PATTERN.finditer(text):
            title_group = match.group("title")
            if title_group is None:
                continue
                
            title = title_group.strip()
            if title:
                raw_content = self.extract_content_after_match(text, match)
                
                entry = DatasetEntry(
                    file=str(path),
                    type="AmandaMap",
                    text=raw_content,
                    is_amanda_related=self.is_amanda_related_chat(raw_content)
                )
                entries.append(entry)
        
        # Extract Field Pulse entries
        for match in _FIELD_PULSE_PATTERN.finditer(text):
            number_str = match.group("number")
            title_group = match.group("title")
            
            if title_group is None:
                continue
                
            title = title_group.strip()
            raw_content = self.extract_content_after_match(text, match)
            
            number = int(number_str) if number_str else None
            
            entry = DatasetEntry(
                file=str(path),
                type="FieldPulse",
                text=raw_content,
                number=number,
                is_amanda_related=self.is_amanda_related_chat(raw_content)
            )
            entries.append(entry)
        
        # Extract Whispered Flame entries
        for match in _WHISPERED_FLAME_PATTERN.finditer(text):
            number_str = match.group("number")
            title_group = match.group("title")
            
            if title_group is None:
                continue
                
            title = title_group.strip()
            raw_content = self.extract_content_after_match(text, match)
            
            number = int(number_str) if number_str else None
            
            entry = DatasetEntry(
                file=str(path),
                type="WhisperedFlame",
                text=raw_content,
                number=number,
                is_amanda_related=self.is_amanda_related_chat(raw_content)
            )
            entries.append(entry)
        
        # Extract Flame Vow entries
        for match in _FLAME_VOW_PATTERN.finditer(text):
            title_group = match.group("title")
            
            if title_group is None:
                continue
                
            title = title_group.strip()
            raw_content = self.extract_content_after_match(text, match)
            
            entry = DatasetEntry(
                file=str(path),
                type="FlameVow",
                text=raw_content,
                is_amanda_related=self.is_amanda_related_chat(raw_content)
            )
            entries.append(entry)
        
        # Extract Phoenix Codex entries
        for match in _PHOENIX_CODEX_PATTERN.finditer(text):
            title = match.group("title").strip()
            raw_content = self.extract_content_after_match(text, match)
            
            is_phoenix, confidence, reason, category = self.classify_content(raw_content)
            
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
                raw_content = self.extract_content_after_match(text, match)
                
                is_phoenix, confidence, reason, category = self.classify_content(raw_content)
                
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
            raw_content = self.extract_content_after_match(text, match)
            
            is_phoenix, confidence, reason, category = self.classify_content(raw_content)
            
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
            raw_content = self.extract_content_after_match(text, match)
            
            number = int(number_str) if number_str else None
            is_phoenix, confidence, reason, category = self.classify_content(raw_content)
            
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
            raw_content = self.extract_content_after_match(text, match)
            
            is_phoenix, confidence, reason, category = self.classify_content(raw_content)
            
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
            raw_content = self.extract_content_after_match(text, match)
            
            is_phoenix, confidence, reason, category = self.classify_content(raw_content)
            
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
            raw_content = self.extract_content_after_match(text, match)
            
            is_phoenix, confidence, reason, category = self.classify_content(raw_content)
            
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
                    is_amanda_related=self.is_amanda_related_chat(seg)
                )
            )

        for seg in find_entries(text):
            entries.append(DatasetEntry(
                file=str(path), 
                type="AmandaMap", 
                text=seg,
                is_amanda_related=self.is_amanda_related_chat(seg)
            ))

        for seg in self.extract_keyword_segments(text, "AmandaMap"):
            if seg.lower() not in [e.text.lower() for e in entries]:
                entries.append(DatasetEntry(
                    file=str(path), 
                    type="AmandaMap", 
                    text=seg,
                    is_amanda_related=self.is_amanda_related_chat(seg)
                ))

        for seg in self.extract_phoenix_entries(text):
            is_phoenix, confidence, reason, category = self.classify_content(seg)
            entries.append(DatasetEntry(
                file=str(path), 
                type="PhoenixCodex", 
                text=seg,
                is_phoenix_codex=is_phoenix,
                confidence=confidence,
                category=category,
                classification_reason=reason
            ))

        for seg in self.extract_whisper_entries(text):
            entries.append(DatasetEntry(
                file=str(path), 
                type="WhisperedFlame", 
                text=seg,
                is_amanda_related=self.is_amanda_related_chat(seg)
            ))
        
        return entries
    
    def is_amanda_related_chat(self, chat_text: str) -> bool:
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
    
    def classify_content(self, content: str) -> Tuple[bool, float, str, str]:
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
    
    def extract_content_after_match(self, full_content: str, match) -> str:
        """Extract content after a regex match."""
        start_pos = match.end()
        end_pos = full_content.find('\n\n', start_pos)
        if end_pos == -1:
            end_pos = len(full_content)
        
        return full_content[start_pos:end_pos].strip()
    
    def extract_keyword_segments(self, text: str, keyword: str) -> List[str]:
        paragraphs = re.split(r"\n\s*\n", text)
        result = []
        for idx, para in enumerate(paragraphs):
            if keyword.lower() in para.lower():
                result.append(self._next_paragraphs(paragraphs, idx).strip())
        return result
    
    def _next_paragraphs(self, paragraphs: List[str], i: int) -> str:
        parts = [paragraphs[i]]
        if i + 1 < len(paragraphs):
            parts.append(paragraphs[i + 1])
        return '\n\n'.join(parts)
    
    def extract_phoenix_entries(self, text: str) -> List[str]:
        return [m.group(1).strip() for m in _PHX_RE.finditer(text)]
    
    def extract_whisper_entries(self, text: str) -> List[str]:
        return [m.group(1).strip() for m in _WHISPER_RE.finditer(text)]
    
    def process_files_streaming(
        self,
        file_paths: List[Path],
        amandamap_file: str = "amandamapexportfile.json",
        phoenix_file: str = "phoenixcodexexport.json",
    ) -> Dict[str, int]:
        """Process files sequentially, exporting results as we go.

        This avoids building huge in-memory lists that previously stalled
        processing after ~30 files.  Instead, entries are written to disk
        immediately and only lightweight counters are kept in RAM.
        """

        # Track counts for final reporting
        entry_counts: Dict[str, int] = defaultdict(int)

        for file_path in file_paths:
            should_process, reason = self.should_process_file(file_path)
            if not should_process:
                print(f"⏭️ Skipping {file_path.name}: {reason}")
                continue

            content = ""
            try:
                start_time = time.time()
                content = self.read_file_optimized(file_path)
                file_entries = self.scan_file_enhanced(file_path, content)

                processing_time = time.time() - start_time
                memory_usage = self.memory_manager.get_memory_usage()

                # Temporary holders for this file's results so we can flush
                amandamap_batch: List[Dict[str, Any]] = []
                phoenix_batch: List[Dict[str, Any]] = []

                for entry in file_entries:
                    entry.processing_time = processing_time
                    entry.memory_usage = int(memory_usage * 1024 * 1024)

                    entry_counts[entry.type] += 1

                    if (
                        entry.is_amanda_related
                        or entry.type.lower().startswith("amandamap")
                        or entry.type.lower()
                        in ["threshold", "fieldpulse", "whisperedflame", "flamevow"]
                    ):
                        amandamap_batch.append(asdict(entry))
                        entry_counts["AmandaMap"] += 1
                    elif entry.is_phoenix_codex or entry.type.lower().startswith("phoenix"):
                        phoenix_batch.append(asdict(entry))
                        entry_counts["PhoenixCodex"] += 1

                # Immediately write batches to disk to free RAM
                if amandamap_batch:
                    self.append_entries_to_file(amandamap_batch, amandamap_file)
                if phoenix_batch:
                    self.append_entries_to_file(phoenix_batch, phoenix_file)

                if self.verbose_mode:
                    print(
                        f"✅ Processed {file_path.name}: {len(file_entries)} entries"
                    )

            except Exception as e:
                print(f"❌ Error processing {file_path}: {e}")
            finally:
                if self.settings.enable_file_cache:
                    self.file_cache.pop(str(file_path), None)
                del content
                self.memory_manager.force_garbage_collection()

        return dict(entry_counts)

    def append_entries_to_file(self, entries: List[Dict[str, Any]], file_path: str) -> None:
        """Append entries to a JSON file, creating it if needed."""
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        existing: List[Dict[str, Any]] = []
        if path.exists():
            try:
                with open(path, "r", encoding="utf-8") as f:
                    existing = json.load(f)
            except Exception:
                existing = []

        existing.extend(entries)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(existing, f, indent=2, ensure_ascii=False)
    
    def export_to_separate_files(self, amandamap_entries: List[DatasetEntry], phoenix_entries: List[DatasetEntry], 
                                amandamap_file: str = "amandamapexportfile.json", 
                                phoenix_file: str = "phoenixcodexexport.json"):
        """Export entries to separate files with append functionality."""
        
        # Export AmandaMap entries
        amandamap_data = []
        for entry in amandamap_entries:
            entry_dict = asdict(entry)
            amandamap_data.append(entry_dict)
        
        # Load existing AmandaMap data if file exists
        existing_amandamap = []
        if Path(amandamap_file).exists():
            try:
                with open(amandamap_file, 'r', encoding='utf-8') as f:
                    existing_amandamap = json.load(f)
                print(f"📄 Loaded {len(existing_amandamap)} existing AmandaMap entries")
            except Exception as e:
                print(f"⚠️ Error loading existing AmandaMap file: {e}")
        
        # Append new entries
        existing_amandamap.extend(amandamap_data)
        
        # Save AmandaMap file
        with open(amandamap_file, 'w', encoding='utf-8') as f:
            json.dump(existing_amandamap, f, indent=2, ensure_ascii=False)
        print(f"💾 Exported {len(amandamap_entries)} AmandaMap entries to {amandamap_file}")
        
        # Export Phoenix Codex entries
        phoenix_data = []
        for entry in phoenix_entries:
            entry_dict = asdict(entry)
            phoenix_data.append(entry_dict)
        
        # Load existing Phoenix Codex data if file exists
        existing_phoenix = []
        if Path(phoenix_file).exists():
            try:
                with open(phoenix_file, 'r', encoding='utf-8') as f:
                    existing_phoenix = json.load(f)
                print(f"📄 Loaded {len(existing_phoenix)} existing Phoenix Codex entries")
            except Exception as e:
                print(f"⚠️ Error loading existing Phoenix Codex file: {e}")
        
        # Append new entries
        existing_phoenix.extend(phoenix_data)
        
        # Save Phoenix Codex file
        with open(phoenix_file, 'w', encoding='utf-8') as f:
            json.dump(existing_phoenix, f, indent=2, ensure_ascii=False)
        print(f"💾 Exported {len(phoenix_entries)} Phoenix Codex entries to {phoenix_file}")
    
    def cleanup(self):
        """Clean up resources."""
        self.file_cache.clear()
        self.result_cache.clear()
        self.cuda_processor.cleanup()
        self.memory_manager.force_garbage_collection() 
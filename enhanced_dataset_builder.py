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
from tempfile import SpooledTemporaryFile
import orjson

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
from amandamap_parser import (
    extract_from_file,
    extract_from_text,
    extract_from_json,
    extract_chat_timestamps,
    ParsedEntry,
)
from modules.performance_optimizer import PerformanceOptimizer, OptimizationConfig
from modules.settings_service import SettingsService


@dataclass
class DatasetEntry:
    file: str
    type: str
    text: str
    number: Optional[int] = None
    title: str = ""
    date: Optional[str] = None
    core_themes: List[str] = field(default_factory=list)
    sequential_id: Optional[str] = None  # For handling duplicates like "23a", "23b"
    is_amanda_related: bool = False
    is_phoenix_codex: bool = False
    confidence: float = 0.0
    category: str = ""
    classification_reason: str = ""
    processing_time: float = 0.0
    memory_usage: int = 0


def _process_file(args):
    """Worker function to parse a single file's content.

    This uses the standalone AmandaMap/Phoenix Codex parser so each process can
    operate independently without touching disk again. It returns the index of
    the file along with a list of serialized entry dictionaries ready for
    streaming to the RAM-backed temporary store.
    """

    idx, path_str, content = args
    start_time = time.time()
    p = Path(path_str)

    first, _ = extract_chat_timestamps(content)
    default_date = first.strftime("%Y-%m-%d") if first else None

    if p.suffix.lower() == ".json":
        parsed: List[ParsedEntry] = extract_from_json(content, str(p), default_date)
    else:
        parsed = extract_from_text(content, str(p), default_date)

    processing_time = time.time() - start_time
    entries: List[Dict[str, Any]] = []

    for pe in parsed:
        entry = DatasetEntry(
            file=pe.source,
            type=pe.type,
            text=pe.description,
            number=pe.number,
            title=pe.title,
            date=pe.date,
            core_themes=pe.core_themes,
            is_amanda_related=pe.is_amanda_related,
            is_phoenix_codex=pe.type.lower().startswith("phoenix"),
        )
        entry.processing_time = processing_time
        entries.append(asdict(entry))

    return idx, entries


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
        """Parse a file using the standalone AmandaMap/Phoenix Codex parser."""
        parsed_entries: List[ParsedEntry] = extract_from_file(path)
        entries: List[DatasetEntry] = []
        for p in parsed_entries:
            entries.append(
                DatasetEntry(
                    file=p.source,
                    type=p.type,
                    text=p.description,
                    number=p.number,
                    title=p.title,
                    date=p.date,
                    core_themes=p.core_themes,
                    is_amanda_related=p.is_amanda_related,
                    is_phoenix_codex=p.type.lower().startswith("phoenix"),
                )
            )
        return entries
    
    def is_amanda_related_chat(self, chat_text: str) -> bool:
        return False

    def classify_content(self, content: str) -> Tuple[bool, float, str, str]:
        return False, 0.0, "", ""

    def extract_content_after_match(self, full_content: str, match) -> str:
        return ""

    def extract_keyword_segments(self, text: str, keyword: str) -> List[str]:
        return []

    def _next_paragraphs(self, paragraphs: List[str], i: int) -> str:
        return ""

    def extract_phoenix_entries(self, text: str) -> List[str]:
        return []

    def extract_whisper_entries(self, text: str) -> List[str]:
        return []
    
    def process_files_streaming(
        self,
        file_paths: List[Path],
        output_file: str = "AmandaMap_PhoenixCodex_Output.json",
        num_workers: Optional[int] = None,
    ) -> Dict[str, int]:
        """Process files using an in-RAM multiprocessing pipeline.

        All input files are first read fully into memory. A worker pool then
        parses them in parallel, streaming each resulting entry into a
        RAM-backed ``SpooledTemporaryFile``. Memory for a file is released as
        soon as its entries are written. After all workers finish, the temporary
        file is flushed once to ``output_file`` as a single JSON array.
        """

        if num_workers is None:
            num_workers = max(1, multiprocessing.cpu_count() - 1)

        entry_counts: Dict[str, int] = defaultdict(int)

        files_in_memory: List[Tuple[int, str, str]] = []
        for idx, file_path in enumerate(file_paths):
            should_process, reason = self.should_process_file(file_path)
            if not should_process:
                print(f"⏭️ Skipping {file_path.name}: {reason}")
                continue
            try:
                with file_path.open("r", encoding="utf-8", errors="ignore") as f:
                    files_in_memory.append((len(files_in_memory), str(file_path), f.read()))
            except Exception as e:
                print(f"❌ Error reading {file_path}: {e}")

        with SpooledTemporaryFile(max_size=1024 * 1024 * 200, mode="w+b") as tmpfile:
            with multiprocessing.Pool(processes=num_workers) as pool:
                for idx, entries in pool.imap_unordered(_process_file, files_in_memory):
                    for entry in entries:
                        tmpfile.write(orjson.dumps(entry))
                        tmpfile.write(b"\n")
                        entry_counts[entry["type"]] += 1
                    files_in_memory[idx] = None
                    self.memory_manager.force_garbage_collection()

            tmpfile.seek(0)
            with open(output_file, "wb") as out:
                out.write(b"[")
                first = True
                for line in tmpfile:
                    if not first:
                        out.write(b",")
                    else:
                        first = False
                    out.write(line.strip())
                out.write(b"]")

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
            
    def cleanup(self):
        """Clean up resources."""
        self.file_cache.clear()
        self.result_cache.clear()
        self.cuda_processor.cleanup()
        self.memory_manager.force_garbage_collection()
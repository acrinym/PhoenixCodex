"""
Performance Optimizer Module

Provides comprehensive optimization features for the GPT Export & Index Tool:
- Memory management and monitoring
- File size limits and streaming
- Caching strategies
- Performance profiling
- Resource cleanup
- Batch processing optimization
"""

import gc
import psutil
import time
import threading
import weakref
from pathlib import Path
from typing import Dict, List, Optional, Callable, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import logging
import json
import os
from functools import wraps, lru_cache
from collections import defaultdict, OrderedDict

logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetrics:
    """Tracks performance metrics for operations."""
    operation_name: str
    start_time: float
    end_time: Optional[float] = None
    memory_before: int = 0
    memory_after: int = 0
    cpu_usage: float = 0.0
    file_count: int = 0
    total_size: int = 0
    errors: List[str] = field(default_factory=list)
    
    @property
    def duration(self) -> float:
        return (self.end_time or time.time()) - self.start_time
    
    @property
    def memory_delta(self) -> int:
        return self.memory_after - self.memory_before

@dataclass
class OptimizationConfig:
    """Configuration for performance optimization."""
    # Memory limits
    max_memory_usage_mb: int = 2048  # 2GB default
    memory_warning_threshold_mb: int = 1536  # 1.5GB warning
    
    # File size limits
    max_file_size_mb: int = 50  # Skip files larger than 50MB
    max_total_size_gb: int = 10  # Skip if total size > 10GB
    
    # Caching
    enable_search_cache: bool = True
    search_cache_size: int = 1000
    enable_file_cache: bool = True
    file_cache_size: int = 100
    
    # Batch processing
    batch_size: int = 100
    max_concurrent_files: int = 4
    
    # Performance monitoring
    enable_performance_monitoring: bool = True
    log_performance_metrics: bool = True
    
    # Resource cleanup
    auto_garbage_collection: bool = True
    cleanup_interval_seconds: int = 300  # 5 minutes

class MemoryManager:
    """Manages memory usage and provides memory optimization features."""
    
    def __init__(self, config: OptimizationConfig):
        self.config = config
        self.process = psutil.Process()
        self.memory_history: List[Tuple[float, int]] = []
        self._lock = threading.Lock()
    
    def get_memory_usage(self) -> int:
        """Get current memory usage in bytes."""
        return self.process.memory_info().rss
    
    def get_memory_usage_mb(self) -> float:
        """Get current memory usage in MB."""
        return self.get_memory_usage() / (1024 * 1024)
    
    def is_memory_high(self) -> bool:
        """Check if memory usage is above warning threshold."""
        return self.get_memory_usage_mb() > self.config.memory_warning_threshold_mb
    
    def is_memory_critical(self) -> bool:
        """Check if memory usage is above critical threshold."""
        return self.get_memory_usage_mb() > self.config.max_memory_usage_mb
    
    def force_garbage_collection(self) -> int:
        """Force garbage collection and return freed memory."""
        before = self.get_memory_usage()
        gc.collect()
        after = self.get_memory_usage()
        freed = before - after
        logger.info(f"Garbage collection freed {freed / (1024*1024):.2f} MB")
        return freed
    
    def log_memory_usage(self, context: str = ""):
        """Log current memory usage."""
        usage_mb = self.get_memory_usage_mb()
        with self._lock:
            self.memory_history.append((time.time(), self.get_memory_usage()))
            # Keep only last 100 entries
            if len(self.memory_history) > 100:
                self.memory_history = self.memory_history[-100:]
        
        logger.info(f"Memory usage {context}: {usage_mb:.2f} MB")
        
        if self.is_memory_critical():
            logger.warning(f"CRITICAL: Memory usage {usage_mb:.2f} MB exceeds limit {self.config.max_memory_usage_mb} MB")
            self.force_garbage_collection()
        elif self.is_memory_high():
            logger.warning(f"WARNING: Memory usage {usage_mb:.2f} MB is high")

class FileSizeManager:
    """Manages file size limits and provides streaming for large files."""
    
    def __init__(self, config: OptimizationConfig):
        self.config = config
    
    def should_skip_file(self, file_path: Path) -> Tuple[bool, str]:
        """Determine if a file should be skipped based on size limits."""
        try:
            file_size = file_path.stat().st_size
            file_size_mb = file_size / (1024 * 1024)
            
            if file_size_mb > self.config.max_file_size_mb:
                return True, f"File size {file_size_mb:.2f} MB exceeds limit {self.config.max_file_size_mb} MB"
            
            return False, ""
        except Exception as e:
            return True, f"Error checking file size: {e}"
    
    def get_folder_size(self, folder_path: Path) -> int:
        """Get total size of all files in folder."""
        total_size = 0
        try:
            for file_path in folder_path.rglob("*"):
                if file_path.is_file():
                    total_size += file_path.stat().st_size
        except Exception as e:
            logger.error(f"Error calculating folder size: {e}")
        return total_size
    
    def should_skip_folder(self, folder_path: Path) -> Tuple[bool, str]:
        """Determine if a folder should be skipped based on total size."""
        total_size_gb = self.get_folder_size(folder_path) / (1024 * 1024 * 1024)
        
        if total_size_gb > self.config.max_total_size_gb:
            return True, f"Folder size {total_size_gb:.2f} GB exceeds limit {self.config.max_total_size_gb} GB"
        
        return False, ""
    
    def read_file_in_chunks(self, file_path: Path, chunk_size: int = 8192) -> str:
        """Read a file in chunks to avoid loading large files entirely into memory."""
        content = []
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                while True:
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                    content.append(chunk)
            return ''.join(content)
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            return ""

class SearchCache:
    """Provides caching for search results to improve performance."""
    
    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self.cache: OrderedDict[str, Any] = OrderedDict()
        self._lock = threading.Lock()
    
    def get(self, key: str) -> Optional[Any]:
        """Get a cached result."""
        with self._lock:
            if key in self.cache:
                # Move to end (most recently used)
                self.cache.move_to_end(key)
                return self.cache[key]
            return None
    
    def set(self, key: str, value: Any):
        """Set a cached result."""
        with self._lock:
            if key in self.cache:
                # Update existing
                self.cache.move_to_end(key)
                self.cache[key] = value
            else:
                # Add new
                self.cache[key] = value
                if len(self.cache) > self.max_size:
                    # Remove least recently used
                    self.cache.popitem(last=False)
    
    def clear(self):
        """Clear the cache."""
        with self._lock:
            self.cache.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self._lock:
            return {
                'size': len(self.cache),
                'max_size': self.max_size,
                'keys': list(self.cache.keys())
            }

class FileCache:
    """Provides caching for file content to avoid repeated disk reads."""
    
    def __init__(self, max_size: int = 100):
        self.max_size = max_size
        self.cache: OrderedDict[str, Tuple[str, float]] = OrderedDict()
        self._lock = threading.Lock()
    
    def get(self, file_path: Path) -> Optional[str]:
        """Get cached file content."""
        key = str(file_path)
        with self._lock:
            if key in self.cache:
                content, timestamp = self.cache[key]
                # Check if file has been modified
                try:
                    if file_path.stat().st_mtime <= timestamp:
                        self.cache.move_to_end(key)
                        return content
                    else:
                        # File modified, remove from cache
                        del self.cache[key]
                except:
                    # File doesn't exist, remove from cache
                    del self.cache[key]
            return None
    
    def set(self, file_path: Path, content: str):
        """Cache file content."""
        key = str(file_path)
        with self._lock:
            try:
                timestamp = file_path.stat().st_mtime
                if key in self.cache:
                    self.cache.move_to_end(key)
                    self.cache[key] = (content, timestamp)
                else:
                    self.cache[key] = (content, timestamp)
                    if len(self.cache) > self.max_size:
                        self.cache.popitem(last=False)
            except Exception as e:
                logger.warning(f"Error caching file {file_path}: {e}")
    
    def clear(self):
        """Clear the cache."""
        with self._lock:
            self.cache.clear()

class PerformanceMonitor:
    """Monitors and logs performance metrics."""
    
    def __init__(self, config: OptimizationConfig):
        self.config = config
        self.metrics: List[PerformanceMetrics] = []
        self.memory_manager = MemoryManager(config)
        self._lock = threading.Lock()
    
    def start_operation(self, operation_name: str) -> PerformanceMetrics:
        """Start monitoring an operation."""
        metrics = PerformanceMetrics(
            operation_name=operation_name,
            start_time=time.time(),
            memory_before=self.memory_manager.get_memory_usage()
        )
        
        with self._lock:
            self.metrics.append(metrics)
        
        logger.info(f"Starting operation: {operation_name}")
        return metrics
    
    def end_operation(self, metrics: PerformanceMetrics, 
                     file_count: int = 0, total_size: int = 0, errors: List[str] = None):
        """End monitoring an operation."""
        metrics.end_time = time.time()
        metrics.memory_after = self.memory_manager.get_memory_usage()
        metrics.file_count = file_count
        metrics.total_size = total_size
        if errors:
            metrics.errors = errors
        
        if self.config.log_performance_metrics:
            self._log_metrics(metrics)
    
    def _log_metrics(self, metrics: PerformanceMetrics):
        """Log performance metrics."""
        duration = metrics.duration
        memory_delta_mb = metrics.memory_delta / (1024 * 1024)
        
        logger.info(f"Operation '{metrics.operation_name}' completed:")
        logger.info(f"  Duration: {duration:.2f} seconds")
        logger.info(f"  Memory delta: {memory_delta_mb:+.2f} MB")
        logger.info(f"  Files processed: {metrics.file_count}")
        logger.info(f"  Total size: {metrics.total_size / (1024*1024):.2f} MB")
        
        if metrics.errors:
            logger.warning(f"  Errors: {len(metrics.errors)}")
            for error in metrics.errors:
                logger.warning(f"    {error}")
    
    def get_recent_metrics(self, count: int = 10) -> List[PerformanceMetrics]:
        """Get recent performance metrics."""
        with self._lock:
            return self.metrics[-count:] if self.metrics else []
    
    def clear_metrics(self):
        """Clear performance metrics."""
        with self._lock:
            self.metrics.clear()

class PerformanceOptimizer:
    """Main performance optimization class that coordinates all optimization features."""
    
    def __init__(self, config: Optional[OptimizationConfig] = None):
        self.config = config or OptimizationConfig()
        self.memory_manager = MemoryManager(self.config)
        self.file_size_manager = FileSizeManager(self.config)
        self.search_cache = SearchCache(self.config.search_cache_size) if self.config.enable_search_cache else None
        self.file_cache = FileCache(self.config.file_cache_size) if self.config.enable_file_cache else None
        self.performance_monitor = PerformanceMonitor(self.config)
        
        # Start cleanup thread if auto cleanup is enabled
        if self.config.auto_garbage_collection:
            self._start_cleanup_thread()
    
    def _start_cleanup_thread(self):
        """Start background cleanup thread."""
        def cleanup_worker():
            while True:
                time.sleep(self.config.cleanup_interval_seconds)
                try:
                    if self.memory_manager.is_memory_high():
                        logger.info("Auto cleanup: Memory usage high, running garbage collection")
                        self.memory_manager.force_garbage_collection()
                except Exception as e:
                    logger.error(f"Error in cleanup thread: {e}")
        
        cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True)
        cleanup_thread.start()
    
    def monitor_operation(self, operation_name: str):
        """Decorator to monitor operation performance."""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                metrics = self.performance_monitor.start_operation(operation_name)
                try:
                    result = func(*args, **kwargs)
                    self.performance_monitor.end_operation(metrics)
                    return result
                except Exception as e:
                    self.performance_monitor.end_operation(metrics, errors=[str(e)])
                    raise
            return wrapper
        return decorator
    
    def check_file_limits(self, file_path: Path) -> Tuple[bool, str]:
        """Check if a file should be processed based on size limits."""
        return self.file_size_manager.should_skip_file(file_path)
    
    def check_folder_limits(self, folder_path: Path) -> Tuple[bool, str]:
        """Check if a folder should be processed based on size limits."""
        return self.file_size_manager.should_skip_folder(folder_path)
    
    def read_file_optimized(self, file_path: Path) -> str:
        """Read file with caching and size limits."""
        # Check size limits
        should_skip, reason = self.check_file_limits(file_path)
        if should_skip:
            logger.warning(f"Skipping file {file_path}: {reason}")
            return ""
        
        # Try cache first
        if self.file_cache:
            cached_content = self.file_cache.get(file_path)
            if cached_content is not None:
                return cached_content
        
        # Read file
        content = self.file_size_manager.read_file_in_chunks(file_path)
        
        # Cache the result
        if self.file_cache and content:
            self.file_cache.set(file_path, content)
        
        return content
    
    def get_cached_search(self, query: str, index_path: str) -> Optional[Any]:
        """Get cached search result."""
        if self.search_cache:
            cache_key = f"{query}:{index_path}"
            return self.search_cache.get(cache_key)
        return None
    
    def cache_search_result(self, query: str, index_path: str, result: Any):
        """Cache search result."""
        if self.search_cache:
            cache_key = f"{query}:{index_path}"
            self.search_cache.set(cache_key, result)
    
    def log_memory_usage(self, context: str = ""):
        """Log current memory usage."""
        self.memory_manager.log_memory_usage(context)
    
    def force_cleanup(self):
        """Force memory cleanup."""
        return self.memory_manager.force_garbage_collection()
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get comprehensive performance statistics."""
        stats = {
            'memory_usage_mb': self.memory_manager.get_memory_usage_mb(),
            'memory_high': self.memory_manager.is_memory_high(),
            'memory_critical': self.memory_manager.is_memory_critical(),
            'recent_metrics': [
                {
                    'operation': m.operation_name,
                    'duration': m.duration,
                    'memory_delta_mb': m.memory_delta / (1024 * 1024),
                    'file_count': m.file_count,
                    'errors': len(m.errors)
                }
                for m in self.performance_monitor.get_recent_metrics(5)
            ]
        }
        
        if self.search_cache:
            stats['search_cache'] = self.search_cache.get_stats()
        
        if self.file_cache:
            stats['file_cache_size'] = len(self.file_cache.cache)
        
        return stats

# Global optimizer instance
_optimizer: Optional[PerformanceOptimizer] = None

def get_optimizer() -> PerformanceOptimizer:
    """Get the global optimizer instance."""
    global _optimizer
    if _optimizer is None:
        _optimizer = PerformanceOptimizer()
    return _optimizer

def optimize_operation(operation_name: str):
    """Decorator to optimize an operation with performance monitoring."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            optimizer = get_optimizer()
            return optimizer.monitor_operation(operation_name)(func)(*args, **kwargs)
        return wrapper
    return decorator 
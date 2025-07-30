"""
Progress Service Module

Backports the progress reporting functionality from the Avalonia app's ProgressService.cs.
Provides consistent progress tracking across operations with callbacks and status updates.
"""

import time
import threading
from typing import Optional, Callable, Any, List
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class ProgressInfo:
    """Represents progress information for an operation."""
    message: str
    current: int
    total: int
    percentage: float
    start_time: float
    estimated_remaining: Optional[float] = None

class ProgressService:
    """Service for tracking and reporting progress of long-running operations."""
    
    def __init__(self):
        self.current_operation: Optional[str] = None
        self.progress_info: Optional[ProgressInfo] = None
        self.callbacks: List[Callable[[ProgressInfo], None]] = []
        self._lock = threading.Lock()
        self._start_time: Optional[float] = None
    
    def start_operation(self, operation_name: str) -> None:
        """Start a new operation."""
        with self._lock:
            self.current_operation = operation_name
            self._start_time = time.time()
            self.progress_info = ProgressInfo(
                message=f"Starting {operation_name}",
                current=0,
                total=0,
                percentage=0.0,
                start_time=self._start_time
            )
            logger.info(f"Started operation: {operation_name}")
    
    def report_progress(
        self, 
        message: str, 
        current: int, 
        total: int,
        estimated_remaining: Optional[float] = None
    ) -> None:
        """Report progress for the current operation."""
        with self._lock:
            if self.progress_info is None:
                return
            
            percentage = (current / total * 100) if total > 0 else 0.0
            
            # Calculate estimated remaining time
            if self._start_time and current > 0:
                elapsed = time.time() - self._start_time
                if current > 0:
                    rate = elapsed / current
                    estimated_remaining = rate * (total - current)
            
            self.progress_info = ProgressInfo(
                message=message,
                current=current,
                total=total,
                percentage=percentage,
                start_time=self._start_time or time.time(),
                estimated_remaining=estimated_remaining
            )
            
            # Notify callbacks
            for callback in self.callbacks:
                try:
                    callback(self.progress_info)
                except Exception as e:
                    logger.error(f"Error in progress callback: {e}")
    
    def report_message(self, message: str) -> None:
        """Report a status message without progress."""
        with self._lock:
            if self.progress_info is None:
                return
            
            self.progress_info.message = message
            
            # Notify callbacks
            for callback in self.callbacks:
                try:
                    callback(self.progress_info)
                except Exception as e:
                    logger.error(f"Error in progress callback: {e}")
    
    def complete_operation(self, message: Optional[str] = None) -> None:
        """Complete the current operation."""
        with self._lock:
            if self.progress_info is None:
                return
            
            completion_message = message or f"Completed {self.current_operation}"
            self.progress_info = ProgressInfo(
                message=completion_message,
                current=self.progress_info.total,
                total=self.progress_info.total,
                percentage=100.0,
                start_time=self._start_time or time.time(),
                estimated_remaining=0.0
            )
            
            # Notify callbacks
            for callback in self.callbacks:
                try:
                    callback(self.progress_info)
                except Exception as e:
                    logger.error(f"Error in progress callback: {e}")
            
            logger.info(f"Completed operation: {self.current_operation}")
            self.current_operation = None
            self.progress_info = None
            self._start_time = None
    
    def add_callback(self, callback: Callable[[ProgressInfo], None]) -> None:
        """Add a progress callback."""
        with self._lock:
            self.callbacks.append(callback)
    
    def remove_callback(self, callback: Callable[[ProgressInfo], None]) -> None:
        """Remove a progress callback."""
        with self._lock:
            if callback in self.callbacks:
                self.callbacks.remove(callback)
    
    def get_current_progress(self) -> Optional[ProgressInfo]:
        """Get the current progress information."""
        with self._lock:
            return self.progress_info
    
    def is_operation_in_progress(self) -> bool:
        """Check if an operation is currently in progress."""
        with self._lock:
            return self.current_operation is not None
    
    def get_operation_name(self) -> Optional[str]:
        """Get the name of the current operation."""
        with self._lock:
            return self.current_operation

class ConsoleProgressCallback:
    """Simple console-based progress callback for CLI operations."""
    
    def __init__(self, show_percentage: bool = True, show_eta: bool = True):
        self.show_percentage = show_percentage
        self.show_eta = show_eta
        self.last_update = 0
    
    def __call__(self, progress_info: ProgressInfo) -> None:
        """Display progress information to console."""
        current_time = time.time()
        
        # Throttle updates to avoid spam
        if current_time - self.last_update < 0.1:  # Update max every 100ms
            return
        
        self.last_update = current_time
        
        # Build status message
        status_parts = [progress_info.message]
        
        if self.show_percentage and progress_info.total > 0:
            status_parts.append(f"{progress_info.percentage:.1f}%")
        
        if progress_info.total > 0:
            status_parts.append(f"({progress_info.current}/{progress_info.total})")
        
        if self.show_eta and progress_info.estimated_remaining:
            eta_seconds = progress_info.estimated_remaining
            if eta_seconds > 60:
                eta_str = f"{eta_seconds / 60:.1f}m"
            else:
                eta_str = f"{eta_seconds:.1f}s"
            status_parts.append(f"ETA: {eta_str}")
        
        # Print status
        status_line = " | ".join(status_parts)
        print(f"\r{status_line}", end="", flush=True)
        
        # Print newline when complete
        if progress_info.percentage >= 100.0:
            print()

class FileProgressCallback:
    """File-based progress callback for logging progress to a file."""
    
    def __init__(self, log_file: str):
        self.log_file = log_file
    
    def __call__(self, progress_info: ProgressInfo) -> None:
        """Log progress information to file."""
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"{timestamp} | {progress_info.message} | "
                       f"{progress_info.percentage:.1f}% | "
                       f"{progress_info.current}/{progress_info.total}\n")
        except Exception as e:
            logger.error(f"Error writing to progress log: {e}")

# Global progress service instance
progress_service = ProgressService() 
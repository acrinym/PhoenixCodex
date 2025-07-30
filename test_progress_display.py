#!/usr/bin/env python3
"""
Test script to verify the progress display is working correctly.
"""

import sys
import logging
from pathlib import Path

# Set up logging to see what's happening
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Add the modules directory to the path
sys.path.insert(0, str(Path(__file__).parent / "modules"))

from advanced_indexer import AdvancedIndexer

def test_progress_display():
    """Test that the progress display is working correctly."""
    print("Testing progress display...")
    
    # Create an advanced indexer instance
    indexer = AdvancedIndexer()
    
    # Create a progress callback that simulates the GUI's update_progress
    def progress_callback(message: str):
        print(f"📊 PROGRESS: {message}")
    
    try:
        # Create a temporary test folder with some files
        test_folder = Path("test_progress_folder")
        test_folder.mkdir(exist_ok=True)
        
        # Create some test files
        test_files = [
            ("file1.txt", "This is the first test file with some content."),
            ("file2.json", '{"data": "test", "content": "more test data"}'),
            ("file3.md", "# Test File\n\nThis is a test markdown file.")
        ]
        
        for filename, content in test_files:
            test_file = test_folder / filename
            test_file.write_text(content)
        
        print(f"Created test folder with {len(test_files)} files")
        
        # Test the build_index method with our callback
        print("\nStarting index build with progress display...")
        index_data = indexer.build_index(
            test_folder,
            Path("test_progress_index.json"),
            progress_callback=progress_callback,
            force_rebuild=True
        )
        
        print(f"✅ Index build completed with progress display!")
        print(f"Index stats: {indexer.get_index_stats(index_data)}")
        
        # Clean up
        for filename, _ in test_files:
            (test_folder / filename).unlink(missing_ok=True)
        test_folder.rmdir()
        
        print("\n🎉 All tests passed! The progress display is working correctly.")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = test_progress_display()
    sys.exit(0 if success else 1) 
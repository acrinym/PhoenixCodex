#!/usr/bin/env python3
"""
Test script to debug the advanced indexer progress callback issue.
"""

import sys
import logging
from pathlib import Path

# Set up logging to see what's happening
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Add the modules directory to the path
sys.path.insert(0, str(Path(__file__).parent / "modules"))

from advanced_indexer import AdvancedIndexer

def test_advanced_indexer_debug():
    """Test the advanced indexer with debug logging."""
    print("Testing AdvancedIndexer with debug logging...")
    
    # Create an advanced indexer instance
    indexer = AdvancedIndexer()
    
    # Create a simple progress callback that logs
    def progress_callback(message: str):
        print(f"PROGRESS CALLBACK: {message}")
    
    try:
        # Create a temporary test folder with some files
        test_folder = Path("test_index_debug_folder")
        test_folder.mkdir(exist_ok=True)
        
        # Create some test files
        test_files = [
            ("test1.txt", "This is a test file for indexing with some content."),
            ("test2.json", '{"test": "data", "content": "more content"}'),
            ("test3.md", "# Test Markdown\n\nThis is a test markdown file.")
        ]
        
        for filename, content in test_files:
            test_file = test_folder / filename
            test_file.write_text(content)
        
        print(f"Created test folder: {test_folder}")
        print(f"Test files: {list(test_folder.glob('*'))}")
        
        # Test the build_index method with our callback
        print("\nStarting index build...")
        index_data = indexer.build_index(
            test_folder,
            Path("test_index_debug.json"),
            progress_callback=progress_callback,
            force_rebuild=True
        )
        
        print(f"✅ Index build completed!")
        print(f"Index stats: {indexer.get_index_stats(index_data)}")
        
        # Clean up
        for filename, _ in test_files:
            (test_folder / filename).unlink(missing_ok=True)
        test_folder.rmdir()
        
        print("\n🎉 All tests passed! The advanced indexer is working correctly.")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = test_advanced_indexer_debug()
    sys.exit(0 if success else 1) 
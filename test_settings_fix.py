#!/usr/bin/env python3
"""
Test script to verify the settings service fix.
"""

import sys
from pathlib import Path

# Add the modules directory to the path
sys.path.insert(0, str(Path(__file__).parent / "modules"))

from settings_service import SettingsService

def test_settings_service():
    """Test that the get_all_settings method works."""
    print("Testing SettingsService...")
    
    # Create a settings service instance
    settings_service = SettingsService()
    
    try:
        # Test the get_all_settings method
        all_settings = settings_service.get_all_settings()
        print("✅ get_all_settings() method works!")
        print(f"Settings keys: {list(all_settings.keys())}")
        
        # Test that it returns a dictionary
        assert isinstance(all_settings, dict), "get_all_settings() should return a dict"
        print("✅ Return type is correct (dict)")
        
        # Test that it contains expected sections
        expected_sections = ['theme', 'search', 'export', 'index']
        for section in expected_sections:
            assert section in all_settings, f"Missing section: {section}"
        print("✅ All expected sections are present")
        
        print("\n🎉 All tests passed! The settings service fix is working correctly.")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = test_settings_service()
    sys.exit(0 if success else 1) 
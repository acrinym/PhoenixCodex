#!/usr/bin/env python3
"""Test Claude HTML conversion."""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from chatgpt_converter_gui import ChatGPTExportConverter
from pathlib import Path

converter = ChatGPTExportConverter()
html_file = Path(r'C:\Users\User\Downloads\Claude\conversation.html')

if html_file.exists():
    try:
        print("Loading Claude HTML file...")
        data = converter.parse_claude_html(html_file)
        
        print(f"✓ Title: {data.get('title')}")
        
        print("\nExtracting messages...")
        messages = converter.extract_messages_from_html(data)
        print(f"✓ Extracted {len(messages)} messages")
        
        # Count by role
        user_count = len([m for m in messages if m['role'] == 'user'])
        asst_count = len([m for m in messages if m['role'] == 'assistant'])
        
        print(f"  User messages: {user_count}")
        print(f"  Assistant messages: {asst_count}")
        
        # Show preview
        if messages:
            first_msg = messages[0]
            print(f"\nFirst message:")
            print(f"  Role: {first_msg['role']}")
            print(f"  Content preview: {first_msg['content'][:100]}...")
        
        # Test conversion
        print("\nConverting to Markdown...")
        title = data.get('title', html_file.stem)
        md = converter.messages_to_markdown(title, messages)
        print(f"✓ Markdown size: {len(md)} chars")
        
        print("\nConverting to JSON...")
        json_out = converter.messages_to_json(title, messages)
        print(f"✓ JSON size: {len(json_out)} chars")
        
        # Test filtering
        print("\nTesting role filter (user only)...")
        filtered = converter.apply_filter(messages, "user")
        print(f"✓ Filtered to {len(filtered)} user messages")
        
        print("\n✅ All Claude HTML tests passed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
else:
    print(f"❌ File not found: {html_file}")

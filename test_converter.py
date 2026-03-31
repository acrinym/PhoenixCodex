#!/usr/bin/env python3
"""Test the converter on a real file."""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from chatgpt_converter_gui import ChatGPTExportConverter
from pathlib import Path
import json

json_file = Path(r'D:\Chatgpt\ExportedChats\chatgpt-export-json') / "ChatGPT-Building_Onyx's_Physical_Form 2025-07-29.json"
bulk_file = Path(r'D:\chatgpt\conversations.json')

print("=" * 80)
print("Testing INDIVIDUAL format")
print("=" * 80)

if json_file.exists():
    converter = ChatGPTExportConverter()
    try:
        print("Loading JSON file...")
        data = converter.parse_chatgpt_json(json_file)
        
        print(f"✅ Parsed successfully")
        print(f"Title: {data.get('title')}")
        
        print("\nExtracting messages...")
        messages = converter.extract_messages(data)
        print(f"Messages extracted: {len(messages)}")
        
        for i, msg in enumerate(messages, 1):
            print(f"  {i}. [{msg['role'].upper()}] {len(msg['content'])} chars")
        
        # Test conversion to markdown
        print("\nConverting to Markdown...")
        md = converter.messages_to_markdown("Test", messages)
        print(f"Markdown size: {len(md)} chars")
        
        # Test conversion to JSON
        print("Converting to JSON...")
        j = converter.messages_to_json("Test", messages)
        print(f"JSON size: {len(j)} chars")
        
        # Test filtering
        print("\nTesting filter (user only)...")
        filtered = converter.apply_filter(messages, "user")
        print(f"Filtered messages: {len(filtered)}")
        
        print("\n✅ Individual format tests passed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
else:
    print(f"❌ File not found: {json_file}")

print("\n" + "=" * 80)
print("Testing BULK format (conversations.json)")
print("=" * 80)

if bulk_file.exists():
    converter = ChatGPTExportConverter()
    try:
        print("Loading bulk JSON file...")
        data = converter.parse_chatgpt_json(bulk_file)
        
        format_type = converter.detect_format(data)
        print(f"Format detected: {format_type}")
        
        if format_type == "bulk":
            conversations = converter.extract_conversations(data)
            print(f"✅ Found {len(conversations)} conversations")
            
            # Sample first 3 conversations
            for i, conv in enumerate(conversations[:3], 1):
                title = conv.get('title', 'Untitled')
                messages = converter.extract_messages(conv)
                print(f"  {i}. {title} ({len(messages)} messages)")
            
            # Test extraction of all conversations
            total_messages = 0
            for conv in conversations:
                messages = converter.extract_messages(conv)
                total_messages += len(messages)
            
            print(f"\n✅ Total: {total_messages} messages across {len(conversations)} conversations")
            
            # Test filtering on bulk data
            print("\nTesting role filtering on bulk data...")
            user_messages = 0
            for conv in conversations:
                messages = converter.extract_messages(conv)
                filtered = converter.apply_filter(messages, "user")
                user_messages += len(filtered)
            
            print(f"✅ User messages only: {user_messages}")
            print("\n✅ Bulk format tests passed!")
        else:
            print(f"❌ Expected bulk format but got: {format_type}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
else:
    print(f"⚠️ Bulk file not found: {bulk_file}")
    print("   (This is optional - only needed if you have conversations.json)")

print("\n" + "=" * 80)
print("ALL TESTS COMPLETED")
print("=" * 80)

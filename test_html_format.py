#!/usr/bin/env python3
"""Analyze Claude HTML export format."""

import re
from pathlib import Path
from bs4 import BeautifulSoup

file = Path(r'C:\Users\User\Downloads\Claude\conversation.html')

if file.exists():
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract title
    title_match = re.search(r'<title>(.*?)</title>', content)
    if title_match:
        print(f"Title: {title_match.group(1)}")
    
    # Try with BeautifulSoup
    try:
        soup = BeautifulSoup(content, 'html.parser')
        
        # Find all messages
        messages = soup.find_all('div', class_=re.compile('msg-'))
        print(f"\nTotal message divs found: {len(messages)}")
        
        # Count by role
        user_msgs = soup.find_all('div', class_='msg-user')
        asst_msgs = soup.find_all('div', class_='msg-assistant')
        
        print(f"User messages: {len(user_msgs)}")
        print(f"Assistant messages: {len(asst_msgs)}")
        
        # Show structure of first message
        if messages:
            print(f"\nFirst message HTML (truncated):")
            print(str(messages[0])[:500])
            
    except ImportError:
        print("BeautifulSoup not installed. Using regex...")
        msg_user_count = len(re.findall(r'class=.msg-user', content))
        msg_asst_count = len(re.findall(r'class=.msg-assistant', content))
        print(f"User messages: {msg_user_count}")
        print(f"Assistant messages: {msg_asst_count}")
else:
    print(f"File not found: {file}")

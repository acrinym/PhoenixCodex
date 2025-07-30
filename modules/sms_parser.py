"""
SMS/MMS Parser for AmandaMap and Phoenix Codex

This module parses SMS backup XML files and converts them into
AmandaMap and Phoenix Codex entries.
"""

import xml.etree.ElementTree as ET
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class SMSMessage:
    """Represents a single SMS message."""
    date: str
    readable_date: str
    body: str
    sender: str
    receiver: str
    message_type: str  # "sms" or "mms"
    contact_name: str
    address: str
    is_incoming: bool

@dataclass
class ConversationEntry:
    """Represents a conversation entry for AmandaMap/Phoenix Codex."""
    timestamp: str
    date: str
    content: str
    sender: str
    receiver: str
    conversation_type: str
    tags: List[str]
    source: str
    entry_type: str = "conversation"

class SMSParser:
    """Parser for SMS backup XML files."""
    
    def __init__(self, amanda_number: str = "+12695120828", justin_number: str = "+19892403594"):
        self.amanda_number = amanda_number
        self.justin_number = justin_number
        self.conversations = []
        
    def parse_sms_file(self, file_path: Path) -> List[ConversationEntry]:
        """Parse SMS XML file and convert to conversation entries."""
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            # Parse SMS messages
            for sms in root.findall('.//sms'):
                entry = self._parse_sms_element(sms)
                if entry:
                    self.conversations.append(entry)
            
            # Parse MMS messages
            for mms in root.findall('.//mms'):
                entry = self._parse_mms_element(mms)
                if entry:
                    self.conversations.append(entry)
            
            # Sort by timestamp
            self.conversations.sort(key=lambda x: x.timestamp)
            
            logger.info(f"Parsed {len(self.conversations)} conversation entries from SMS file")
            return self.conversations
            
        except Exception as e:
            logger.error(f"Error parsing SMS file: {e}")
            return []
    
    def _parse_sms_element(self, sms_elem) -> Optional[ConversationEntry]:
        """Parse a single SMS element."""
        try:
            # Extract basic attributes
            date = sms_elem.get('date', '')
            readable_date = sms_elem.get('readable_date', '')
            body = sms_elem.get('body', '')
            address = sms_elem.get('address', '')
            contact_name = sms_elem.get('contact_name', '')
            msg_type = sms_elem.get('type', '1')  # 1=incoming, 2=outgoing
            
            # Determine sender and receiver
            is_incoming = msg_type == '1'
            if is_incoming:
                sender = contact_name if contact_name else address
                receiver = "Justin"
            else:
                sender = "Justin"
                receiver = contact_name if contact_name else address
            
            # Clean up body text
            body = self._clean_text(body)
            
            # Generate tags based on content
            tags = self._generate_tags(body, sender, receiver)
            
            # Convert timestamp
            timestamp = self._convert_timestamp(date)
            
            return ConversationEntry(
                timestamp=timestamp,
                date=readable_date,
                content=body,
                sender=sender,
                receiver=receiver,
                conversation_type="sms",
                tags=tags,
                source="SMS Backup"
            )
            
        except Exception as e:
            logger.error(f"Error parsing SMS element: {e}")
            return None
    
    def _parse_mms_element(self, mms_elem) -> Optional[ConversationEntry]:
        """Parse a single MMS element."""
        try:
            # Extract basic attributes
            date = mms_elem.get('date', '')
            readable_date = mms_elem.get('readable_date', '')
            address = mms_elem.get('address', '')
            contact_name = mms_elem.get('contact_name', '')
            msg_box = mms_elem.get('msg_box', '1')  # 1=incoming, 2=outgoing
            
            # Extract text from parts
            body = ""
            parts = mms_elem.findall('.//part')
            for part in parts:
                if part.get('ct') == 'text/plain':
                    text = part.get('text', '')
                    if text:
                        body += text + " "
            
            body = body.strip()
            
            # Determine sender and receiver
            is_incoming = msg_box == '1'
            if is_incoming:
                sender = contact_name if contact_name else address
                receiver = "Justin"
            else:
                sender = "Justin"
                receiver = contact_name if contact_name else address
            
            # Clean up body text
            body = self._clean_text(body)
            
            # Generate tags based on content
            tags = self._generate_tags(body, sender, receiver)
            
            # Convert timestamp
            timestamp = self._convert_timestamp(date)
            
            return ConversationEntry(
                timestamp=timestamp,
                date=readable_date,
                content=body,
                sender=sender,
                receiver=receiver,
                conversation_type="mms",
                tags=tags,
                source="SMS Backup"
            )
            
        except Exception as e:
            logger.error(f"Error parsing MMS element: {e}")
            return None
    
    def _clean_text(self, text: str) -> str:
        """Clean up text content."""
        if not text:
            return ""
        
        # Decode HTML entities
        text = text.replace('&amp;', '&')
        text = text.replace('&lt;', '<')
        text = text.replace('&gt;', '>')
        text = text.replace('&#128522;', '😊')
        text = text.replace('&#127771;', '🌻')
        text = text.replace('&#127775;', '🌟')
        text = text.replace('&#127756;', '🌙')
        text = text.replace('&#127747;', '🌃')
        text = text.replace('&#127750;', '🌅')
        text = text.replace('&#127889;', '💤')
        text = text.replace('&#129393;', '😴')
        text = text.replace('&#128513;', '😅')
        text = text.replace('&#128524;', '😌')
        text = text.replace('&#128171;', '💫')
        text = text.replace('&#129300;', '🤔')
        text = text.replace('&#128164;', '😴')
        text = text.replace('&#128564;', '😴')
        text = text.replace('&#127807;', '🌷')
        text = text.replace('&#127774;', '🌞')
        text = text.replace('&#127748;', '🌅')
        text = text.replace('&#128308;', '🔴')
        text = text.replace('&#128992;', '🟠')
        text = text.replace('&#128993;', '🟡')
        text = text.replace('&#128994;', '🟢')
        text = text.replace('&#128309;', '🔵')
        text = text.replace('&#128995;', '🟣')
        text = text.replace('&#11036;', '⚫')
        text = text.replace('&#127776;', '🌠')
        text = text.replace('&#129723;', '🦋')
        text = text.replace('&#10;', '\n')
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def _convert_timestamp(self, timestamp: str) -> str:
        """Convert millisecond timestamp to readable format."""
        try:
            if timestamp:
                # Convert milliseconds to seconds
                ts = int(timestamp) / 1000
                dt = datetime.fromtimestamp(ts)
                return dt.strftime("%Y-%m-%d %H:%M:%S")
            return ""
        except:
            return ""
    
    def _generate_tags(self, content: str, sender: str, receiver: str) -> List[str]:
        """Generate tags based on message content and participants."""
        tags = []
        
        # Add participant tags
        if "Amanda" in sender or "Amanda" in receiver:
            tags.append("amanda")
        if "Justin" in sender or "Justin" in receiver:
            tags.append("justin")
        
        # Content-based tags
        content_lower = content.lower()
        
        # Emotional tags
        if any(word in content_lower for word in ["love", "heart", "💕", "❤️", "💫", "✨"]):
            tags.append("love")
        if any(word in content_lower for word in ["sad", "hurt", "pain", "sorry", "apologize"]):
            tags.append("emotional")
        if any(word in content_lower for word in ["happy", "good", "great", "awesome", "😊", "😅"]):
            tags.append("positive")
        
        # Sleep-related tags
        if any(word in content_lower for word in ["sleep", "dream", "night", "bed", "rest", "🌙", "💤", "😴"]):
            tags.append("sleep")
        
        # Greeting tags
        if any(word in content_lower for word in ["good morning", "good night", "hello", "hey"]):
            tags.append("greeting")
        
        # Music-related tags
        if any(word in content_lower for word in ["music", "song", "youtube", "youtu.be"]):
            tags.append("music")
        
        # Car/insurance related tags
        if any(word in content_lower for word in ["car", "insurance", "accident", "truck"]):
            tags.append("car")
        
        # Work-related tags
        if any(word in content_lower for word in ["work", "job", "mentor", "teaching"]):
            tags.append("work")
        
        # Study/learning tags
        if any(word in content_lower for word in ["study", "book", "reading", "learning", "dispenza"]):
            tags.append("learning")
        
        return list(set(tags))  # Remove duplicates
    
    def export_to_amandamap(self, output_file: Path) -> bool:
        """Export conversations to AmandaMap format."""
        try:
            amandamap_entries = []
            
            for conv in self.conversations:
                # Create AmandaMap entry
                entry = {
                    "timestamp": conv.timestamp,
                    "date": conv.date,
                    "type": "conversation",
                    "participants": [conv.sender, conv.receiver],
                    "content": conv.content,
                    "tags": conv.tags,
                    "source": conv.source,
                    "conversation_type": conv.conversation_type
                }
                amandamap_entries.append(entry)
            
            # Save to file
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(amandamap_entries, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Exported {len(amandamap_entries)} entries to AmandaMap format: {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting to AmandaMap: {e}")
            return False
    
    def export_to_phoenix_codex(self, output_file: Path) -> bool:
        """Export conversations to Phoenix Codex format."""
        try:
            phoenix_entries = []
            
            for conv in self.conversations:
                # Create Phoenix Codex entry
                entry = {
                    "timestamp": conv.timestamp,
                    "date": conv.date,
                    "type": "conversation",
                    "participants": [conv.sender, conv.receiver],
                    "content": conv.content,
                    "tags": conv.tags,
                    "source": conv.source,
                    "conversation_type": conv.conversation_type,
                    "codex_category": "interpersonal_communication"
                }
                phoenix_entries.append(entry)
            
            # Save to file
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(phoenix_entries, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Exported {len(phoenix_entries)} entries to Phoenix Codex format: {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting to Phoenix Codex: {e}")
            return False
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """Get summary statistics of the conversations."""
        if not self.conversations:
            return {}
        
        total_messages = len(self.conversations)
        amanda_messages = sum(1 for c in self.conversations if "amanda" in c.tags)
        justin_messages = sum(1 for c in self.conversations if "justin" in c.tags)
        
        # Date range
        dates = [c.timestamp for c in self.conversations if c.timestamp]
        date_range = f"{min(dates)} to {max(dates)}" if dates else "Unknown"
        
        # Most common tags
        all_tags = []
        for conv in self.conversations:
            all_tags.extend(conv.tags)
        
        tag_counts = {}
        for tag in all_tags:
            tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        most_common_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            "total_messages": total_messages,
            "amanda_messages": amanda_messages,
            "justin_messages": justin_messages,
            "date_range": date_range,
            "most_common_tags": most_common_tags,
            "conversation_types": {
                "sms": sum(1 for c in self.conversations if c.conversation_type == "sms"),
                "mms": sum(1 for c in self.conversations if c.conversation_type == "mms")
            }
        } 
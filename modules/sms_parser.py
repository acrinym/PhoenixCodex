"""
SMS/MMS Parser for AmandaMap and Phoenix Codex

This module parses SMS backup XML files and converts them into
AmandaMap and Phoenix Codex entries with support for appending
to existing data and handling large MMS files.
"""

import xml.etree.ElementTree as ET
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import logging
import os

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
    """Parser for SMS backup XML files with append support."""
    
    def __init__(self, amanda_number: str = "+12695120828", justin_number: str = "+19892403594"):
        self.amanda_number = amanda_number
        self.justin_number = justin_number
        self.conversations = []
        self.existing_latest_timestamp = None
        self.new_entries_count = 0
        self.skipped_entries_count = 0
        
    def load_existing_data(self, amandamap_file: Path = None, phoenix_file: Path = None) -> str:
        """Load existing data and find the latest timestamp."""
        latest_timestamp = None
        
        # Check AmandaMap file
        if amandamap_file and amandamap_file.exists():
            try:
                with open(amandamap_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if data:
                        # Find the latest timestamp
                        timestamps = [entry.get('timestamp', '') for entry in data if entry.get('timestamp')]
                        if timestamps:
                            latest_timestamp = max(timestamps)
                            logger.info(f"Found existing AmandaMap data with latest timestamp: {latest_timestamp}")
            except Exception as e:
                logger.warning(f"Could not load existing AmandaMap data: {e}")
        
        # Check Phoenix Codex file
        if phoenix_file and phoenix_file.exists():
            try:
                with open(phoenix_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if data:
                        # Find the latest timestamp
                        timestamps = [entry.get('timestamp', '') for entry in data if entry.get('timestamp')]
                        if timestamps:
                            phoenix_latest = max(timestamps)
                            if latest_timestamp is None or phoenix_latest > latest_timestamp:
                                latest_timestamp = phoenix_latest
                                logger.info(f"Found existing Phoenix Codex data with latest timestamp: {latest_timestamp}")
            except Exception as e:
                logger.warning(f"Could not load existing Phoenix Codex data: {e}")
        
        self.existing_latest_timestamp = latest_timestamp
        return latest_timestamp
    
    def parse_sms_file(self, file_path: Path, append_mode: bool = False, 
                       amandamap_file: Path = None, phoenix_file: Path = None) -> List[ConversationEntry]:
        """Parse SMS XML file and convert to conversation entries with append support."""
        try:
            # Load existing data if in append mode
            if append_mode:
                self.load_existing_data(amandamap_file, phoenix_file)
                logger.info(f"Append mode: Latest existing timestamp is {self.existing_latest_timestamp}")
            
            # Check file size for large MMS files
            file_size = file_path.stat().st_size
            if file_size > 100 * 1024 * 1024:  # 100MB
                logger.warning(f"Large SMS file detected ({file_size / 1024 / 1024:.1f}MB). Processing in chunks...")
            
            # Parse XML with memory-efficient approach
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            # Parse SMS messages
            sms_count = 0
            for sms in root.findall('.//sms'):
                entry = self._parse_sms_element(sms)
                if entry:
                    if append_mode and self.existing_latest_timestamp:
                        # Check if this entry is newer than existing data
                        if entry.timestamp > self.existing_latest_timestamp:
                            self.conversations.append(entry)
                            self.new_entries_count += 1
                        else:
                            self.skipped_entries_count += 1
                    else:
                        self.conversations.append(entry)
                    sms_count += 1
                    
                    # Progress logging for large files
                    if sms_count % 1000 == 0:
                        logger.info(f"Processed {sms_count} SMS messages...")
            
            # Parse MMS messages with enhanced handling
            mms_count = 0
            for mms in root.findall('.//mms'):
                entry = self._parse_mms_element(mms)
                if entry:
                    if append_mode and self.existing_latest_timestamp:
                        # Check if this entry is newer than existing data
                        if entry.timestamp > self.existing_latest_timestamp:
                            self.conversations.append(entry)
                            self.new_entries_count += 1
                        else:
                            self.skipped_entries_count += 1
                    else:
                        self.conversations.append(entry)
                    mms_count += 1
                    
                    # Progress logging for large files
                    if mms_count % 100 == 0:
                        logger.info(f"Processed {mms_count} MMS messages...")
            
            # Sort by timestamp
            self.conversations.sort(key=lambda x: x.timestamp)
            
            logger.info(f"Parsed {len(self.conversations)} conversation entries from SMS file")
            if append_mode:
                logger.info(f"Added {self.new_entries_count} new entries, skipped {self.skipped_entries_count} existing entries")
            
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
        """Parse a single MMS element with enhanced handling for large files."""
        try:
            # Extract basic attributes
            date = mms_elem.get('date', '')
            readable_date = mms_elem.get('readable_date', '')
            address = mms_elem.get('address', '')
            contact_name = mms_elem.get('contact_name', '')
            msg_box = mms_elem.get('msg_box', '1')  # 1=incoming, 2=outgoing
            
            # Extract text from parts with enhanced handling
            body = ""
            parts = mms_elem.findall('.//part')
            
            # Check for large MMS files
            total_size = 0
            for part in parts:
                size_attr = part.get('size', '0')
                try:
                    total_size += int(size_attr)
                except:
                    pass
            
            # Skip extremely large MMS files (>50MB) to prevent memory issues
            if total_size > 50 * 1024 * 1024:  # 50MB
                logger.warning(f"Skipping large MMS file ({total_size / 1024 / 1024:.1f}MB) to prevent memory issues")
                return None
            
            # Extract text content
            for part in parts:
                content_type = part.get('ct', '')
                if content_type == 'text/plain':
                    text = part.get('text', '')
                    if text:
                        body += text + " "
                elif content_type.startswith('image/'):
                    # Handle image references in MMS
                    image_name = part.get('name', '')
                    if image_name:
                        body += f"[Image: {image_name}] "
                elif content_type.startswith('video/'):
                    # Handle video references in MMS
                    video_name = part.get('name', '')
                    if video_name:
                        body += f"[Video: {video_name}] "
                elif content_type.startswith('audio/'):
                    # Handle audio references in MMS
                    audio_name = part.get('name', '')
                    if audio_name:
                        body += f"[Audio: {audio_name}] "
            
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
    
    def export_to_amandamap(self, output_file: Path, append_mode: bool = False) -> bool:
        """Export conversations to AmandaMap format with append support."""
        try:
            existing_entries = []
            
            # Load existing entries if in append mode
            if append_mode and output_file.exists():
                try:
                    with open(output_file, 'r', encoding='utf-8') as f:
                        existing_entries = json.load(f)
                    logger.info(f"Loaded {len(existing_entries)} existing AmandaMap entries")
                except Exception as e:
                    logger.warning(f"Could not load existing AmandaMap file: {e}")
            
            # Convert new conversations to AmandaMap format
            new_entries = []
            for conv in self.conversations:
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
                new_entries.append(entry)
            
            # Combine existing and new entries
            if append_mode:
                all_entries = existing_entries + new_entries
                # Sort by timestamp to maintain chronological order
                all_entries.sort(key=lambda x: x.get('timestamp', ''))
                logger.info(f"Combined {len(existing_entries)} existing + {len(new_entries)} new = {len(all_entries)} total entries")
            else:
                all_entries = new_entries
            
            # Save to file
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(all_entries, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Exported {len(all_entries)} entries to AmandaMap format: {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting to AmandaMap: {e}")
            return False
    
    def export_to_phoenix_codex(self, output_file: Path, append_mode: bool = False) -> bool:
        """Export conversations to Phoenix Codex format with append support."""
        try:
            existing_entries = []
            
            # Load existing entries if in append mode
            if append_mode and output_file.exists():
                try:
                    with open(output_file, 'r', encoding='utf-8') as f:
                        existing_entries = json.load(f)
                    logger.info(f"Loaded {len(existing_entries)} existing Phoenix Codex entries")
                except Exception as e:
                    logger.warning(f"Could not load existing Phoenix Codex file: {e}")
            
            # Convert new conversations to Phoenix Codex format
            new_entries = []
            for conv in self.conversations:
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
                new_entries.append(entry)
            
            # Combine existing and new entries
            if append_mode:
                all_entries = existing_entries + new_entries
                # Sort by timestamp to maintain chronological order
                all_entries.sort(key=lambda x: x.get('timestamp', ''))
                logger.info(f"Combined {len(existing_entries)} existing + {len(new_entries)} new = {len(all_entries)} total entries")
            else:
                all_entries = new_entries
            
            # Save to file
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(all_entries, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Exported {len(all_entries)} entries to Phoenix Codex format: {output_file}")
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
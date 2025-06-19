"""Utilities for parsing XML conversation backups."""

from pathlib import Path
import xml.etree.ElementTree as ET


def parse_xml_backup(file_path, logger=None):
    """Parse simple XML backups with <message> elements."""
    if logger:
        logger(f"Starting parse for XML: {Path(file_path).name}")
    try:
        tree = ET.parse(file_path)
        root_elem = tree.getroot()
    except Exception as e:
        if logger:
            logger(f"  ERROR reading/parsing {Path(file_path).name}: {e}")
        return [{"type": "error", "content": f"Error reading/parsing {Path(file_path).name}: {e}"}]
    structured = []
    structured.append({"type": "header", "content": f"*** FILE: {Path(file_path).name} ***"})
    for msg in root_elem.findall('.//message'):
        role = msg.get('role', 'unknown')
        ts = msg.get('timestamp') or msg.get('time')
        text = ''.join(msg.itertext()).strip()
        structured.append({"type": "text", "content": text, "role": role, "timestamp": ts})
    if logger:
        logger(f"Finished parsing {Path(file_path).name}. Total structured items: {len(structured)}")
    return structured


def parse_sms_smsbackup(file_path, logger=None):
    """Parse SMS Backup & Restore XML files with <sms> elements."""
    if logger:
        logger(f"Starting parse for SMS XML: {Path(file_path).name}")
    try:
        tree = ET.parse(file_path)
        root_elem = tree.getroot()
    except Exception as e:
        if logger:
            logger(f"  ERROR reading/parsing {Path(file_path).name}: {e}")
        return [{"type": "error", "content": f"Error reading/parsing {Path(file_path).name}: {e}"}]
    structured = []
    structured.append({"type": "header", "content": f"*** FILE: {Path(file_path).name} ***"})
    for sms in root_elem.findall('.//sms'):
        sms_type = sms.get('type')
        if sms_type == '1':
            role = 'received'
        elif sms_type == '2':
            role = 'sent'
        else:
            role = sms_type or 'unknown'
        body = sms.get('body', '')
        ts = sms.get('readable_date') or sms.get('date')
        address = sms.get('address')
        structured.append({
            "type": "text",
            "content": body,
            "role": role,
            "timestamp": ts,
            "address": address,
        })
    if logger:
        logger(f"Finished parsing {Path(file_path).name}. Total structured items: {len(structured)}")
    return structured

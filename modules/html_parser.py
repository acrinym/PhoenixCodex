"""Utilities for parsing ChatGPT HTML exports."""

from pathlib import Path
from bs4 import BeautifulSoup


def parse_chatgpt_html_export(file_path, logger=None):
    """Parse ChatGPT HTML exports into a structured list."""
    file_path = Path(file_path)
    if logger:
        logger(f"Starting parse for HTML: {file_path.name}")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')
    except Exception as e:
        if logger:
            logger(f"  ERROR reading/parsing {file_path.name}: {e}")
        return [{"type": "error", "content": f"Error reading/parsing {file_path.name}: {e}"}]

    structured = [{"type": "header", "content": f"*** FILE: {file_path.name} ***"}]

    messages = soup.select('[data-message-author], .message')
    if not messages:
        messages = soup.find_all('article')

    for msg in messages:
        role = msg.get('data-message-author')
        if not role:
            role_el = msg.find(class_='speaker') or msg.find(class_='author') or msg.find(class_='name')
            if role_el:
                role = role_el.get_text(strip=True)
        ts_el = msg.find(class_='timestamp') or msg.find(class_='time')
        timestamp = ts_el.get_text(strip=True) if ts_el else None
        text_el = msg.find(class_='text')
        if text_el and text_el is not msg:
            text = text_el.get_text('\n', strip=True)
        else:
            for meta in msg.find_all(class_=['speaker', 'author', 'name', 'timestamp', 'time']):
                meta.extract()
            text = msg.get_text('\n', strip=True)
        if text:
            structured.append({"type": "text", "content": text, "role": role, "timestamp": timestamp})

    if logger:
        logger(f"Finished parsing {file_path.name}. Total structured items: {len(structured)}")
    return structured

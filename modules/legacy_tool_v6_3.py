import base64
import concurrent.futures
import copy
from datetime import datetime
import difflib
from email import policy
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate, make_msgid
import json
import os
from pathlib import Path
import platform
import re
import subprocess  # Keep for launch_editor
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk, font as tkFont
import xml.etree.ElementTree as ET

from .mirror_entity_utils import (
    classify_mirror_entity_content,
    detect_mirror_entity_reference,
    ensure_mirror_entity_vault,
    generate_filename,
    is_mirror_contaminated,
)
from .tagmap_loader import load_tag_definitions, load_tagmap
from .xml_parser import parse_sms_smsbackup

TOKEN_PATTERN = re.compile(r'\w+|[^\s\w]')

# --- Optional Pillow Import (from your V6.2(timestamp Edition).py) ---
try:
    from PIL import Image as PILImage, ImageTk
    import io
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    ImageTk = None
# --- End Optional Pillow Import ---

# --- Global Constants (from your V6.2(timestamp Edition).py) ---
CONFIG_FILE = "app_config.json"
ORIGINAL_JSON_INDEX_FILE = "original_json_search_index.json"
CONVERTED_FILES_INDEX_FILE = "converted_files_search_index.json"

# --- Default Config (from your V6.2(timestamp Edition).py, ensuring all keys are present) ---
default_config = {
    "theme": "Sea Green",
    "export_format": "Text",
    "export_images_inline": False,
    "export_images_folder": True,
    "default_editor": "",
    "include_timestamps_in_export": False,
    "combine_output_files": False,
    "image_folder_name": "_images",
    "last_indexed_original_json_folder_path": "",
    "last_indexed_converted_files_folder_path": "",
    "skip_system_tool_messages": True,
    "include_filename_in_header": True,
    "include_roles_in_export": True,
    "use_pillow_for_unknown_images": True,
    "tag_definition_file": "",
    "window_geometry": "1000x800+50+50",
    "selected_index_type": "Converted Files (Indexed)",
    "active_tab_text": "Export Chats",
    # --- ENSURED these are present from previous discussions ---
    "search_term_case_sensitive": False,
    "search_logic": "AND",
    "num_tokenizers": 2,
    "num_indexers": 2,
    "cpu_usage_percent": 100,
    "amandamap_mode": False,
    "mirror_entity_redaction_enabled": True,
    "mirror_entity_vault_path": "./mirror_entity/",
    "use_tagmap_tagging": False,
    "tagmap_file_path": ""
}



# --- Theme Styles (from your V6.2(timestamp Edition).py) ---
theme_styles = { # Your original theme_styles dictionary
    "Sea Green": {"bg": "#2e8b57", "fg": "#ffffff", "btn": "#3cb371", "hl": "#20b2aa", "entry_bg": "#f0fff0", "entry_fg": "#000000", "list_bg": "#e0eee0", "list_fg": "#000000", "list_hl_bg": "#3cb371", "list_hl_fg": "#ffffff", "emoji": "穴"},
    "Phoenix Fire": {"bg": "#8b0000", "fg": "#ffdead", "btn": "#ff4500", "hl": "#ff6347", "entry_bg": "#fff8dc", "entry_fg": "#000000", "list_bg": "#ffe4c4", "list_fg": "#000000", "list_hl_bg": "#ff4500", "list_hl_fg": "#ffffff", "emoji": "櫨"},
    "Modern Light": {"bg": "#e0e0e0", "fg": "#1c1c1c", "btn": "#c0c0c0", "hl": "#a0a0a0", "entry_bg": "#ffffff", "entry_fg": "#1c1c1c", "list_bg": "#f5f5f5", "list_fg": "#1c1c1c", "list_hl_bg": "#0078d7", "list_hl_fg": "#ffffff", "emoji": "庁"}
}

# --- Global Variables for UI elements (from your V6.2(timestamp Edition).py) ---
debug_log_text_widget = None
export_log_text_widget = None
root = None
loaded_search_index = None
app_instance_ref = None
config = {} # Populated by load_config() in main()

# --- Logging Function for Debug Tab (from your V6.2(timestamp Edition).py) ---
def log_debug(message):
    global debug_log_text_widget
    log_entry = f"{datetime.now().strftime('%H:%M:%S.%f')[:-3]} - {message}"
    if debug_log_text_widget and debug_log_text_widget.winfo_exists():
        debug_log_text_widget.insert(tk.END, log_entry + "\n")
        debug_log_text_widget.see(tk.END)
    else:
        print(f"LOG_DEBUG_FALLBACK: {log_entry}")

# --- Config and Utility Functions (from your V6.2(timestamp Edition).py) ---
def load_config(): # Your original load_config
    global config
    loaded_config_data = default_config.copy()
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                from_file_cfg = json.load(f)
            # Handle legacy key names
            if 'mirror_entity_redaction_enabled' not in from_file_cfg and 'redact_wg_entries' in from_file_cfg:
                from_file_cfg['mirror_entity_redaction_enabled'] = from_file_cfg.pop('redact_wg_entries')
            loaded_config_data.update(from_file_cfg)
        except json.JSONDecodeError:
            log_debug(f"ERROR: Corrupted {CONFIG_FILE}. Using default config and attempting to save.")
            save_config(loaded_config_data)
        except Exception as e:
            log_debug(f"ERROR: Unexpected error loading config: {e}. Using defaults.")
    else:
        log_debug(f"INFO: {CONFIG_FILE} not found. Using default config and creating it.")
        save_config(loaded_config_data)
    config = loaded_config_data # Set the global config variable
    return loaded_config_data # Return it as well, as per your original structure

def save_config(cfg_to_save): # Your original save_config
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(cfg_to_save, f, indent=4)
    except Exception as e:
        log_debug(f"ERROR: Could not save config to {CONFIG_FILE}: {e}")

def wipe_config(): # Your original
    if os.path.exists(CONFIG_FILE): os.remove(CONFIG_FILE)
    if os.path.exists(ORIGINAL_JSON_INDEX_FILE): os.remove(ORIGINAL_JSON_INDEX_FILE)
    if os.path.exists(CONVERTED_FILES_INDEX_FILE): os.remove(CONVERTED_FILES_INDEX_FILE)
    log_debug("INFO: Config and index files wiped.")

# --- Tokenizer (from your V6.2(timestamp Edition).py) ---
def tokenize(text):
    if not text: return []
    text = text.lower()
    tokens = TOKEN_PATTERN.findall(text)
    return [token for token in tokens if token]

# --- NEW FUNCTION: Timestamp Extraction ---
def extract_chat_timestamps(file_path_str):
    try:
        with open(file_path_str, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        timestamps_found = re.findall(r"\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\]", content)
        valid_timestamps = []
        if timestamps_found:
            for ts_str in timestamps_found:
                try:
                    datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S")
                    valid_timestamps.append(ts_str)
                except ValueError: pass
            if valid_timestamps:
                return valid_timestamps[0], valid_timestamps[-1]
    except FileNotFoundError:
        log_debug(f"ERROR: File not found for timestamp extraction: {file_path_str}")
    except Exception as e:
        log_debug(f"ERROR: Error extracting timestamps from {file_path_str}: {e}")
    return None, None
# --- END NEW FUNCTION ---

# --- NEW FUNCTION: YAML Front Matter Parsing ---

# --- NEW FUNCTION: Load TagMap for indexing ---
def load_json_tagmap(folder_path):
    """Return TagMap data from ``tagmap.json`` in the folder, if present."""
    tag_file = Path(folder_path) / "tagmap.json"
    if not tag_file.exists():
        return {}
    try:
        with open(tag_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            normalized = {}
            for k, v in data.items():
                if isinstance(v, list):
                    normalized[k] = v
                else:
                    normalized[k] = [str(v)]
            return normalized
    except Exception as e:
        log_debug(f"WARNING: Failed to load TagMap from {tag_file}: {e}")
    return {}
# --- END NEW FUNCTION ---

# --- NEW FUNCTION: YAML Front Matter Parsing ---
# --- END NEW FUNCTION ---

# --- Mirror Entity Detection Helpers ---
# Moved to ``mirror_entity_utils`` module

# --- NEW FUNCTION: YAML Front Matter Parsing ---
def parse_yaml_front_matter(text):
    """Return metadata dict and body from a Markdown document."""
    front_re = re.compile(r'^---\s*\n(.*?)\n---\s*\n?', re.DOTALL)
    match = front_re.match(text)
    if not match:
        return {}, text

    front_text = match.group(1)
    body = text[match.end():]
    meta = {}

    try:
        import yaml  # type: ignore
        meta = yaml.safe_load(front_text) or {}
        if not isinstance(meta, dict):
            meta = {}
    except Exception:
        for line in front_text.splitlines():
            if ':' not in line:
                continue
            key, val = line.split(':', 1)
            key = key.strip()
            val = val.strip()
            if val.startswith('[') and val.endswith(']'):
                items = [v.strip().strip('"\'') for v in val[1:-1].split(',') if v.strip()]
                meta[key] = items
            else:
                meta[key] = val.strip('"\'')

    return meta, body
# --- END NEW FUNCTION ---

# --- ImageData Class (from your V6.2(timestamp Edition).py) ---
class ImageData: # Your original ImageData class
    def __init__(self, image_filename_stem, mime_type_for_embedding, base64_str, original_full_mime_type=None, original_data_uri=None):
        self.filename_stem = image_filename_stem
        self.mime_type = mime_type_for_embedding
        self.base64_str = base64_str
        self.image_ext = self.mime_type.split('/')[-1].split('+')[0] if self.mime_type.startswith("image/") else "bin"
        if self.image_ext == "jpeg": self.image_ext = "jpg"
        self.full_filename = f"{self.filename_stem}.{self.image_ext}"
        self.placeholder_text = f"[{self.filename_stem}]"
        self.original_full_mime_type = original_full_mime_type if original_full_mime_type else mime_type_for_embedding
        self.original_data_uri = original_data_uri
        self.local_file_path = None
        self.cid = None
        self.cid_name = None
        log_debug(f"    ImageData created: Filename='{self.full_filename}', EmbedMIME='{self.mime_type}', OrigMIME='{self.original_full_mime_type}', Base64(len):{len(self.base64_str)}")

# --- Core Parsing Logic (from your V6.2(timestamp Edition).py - This is your extensive function) ---
def parse_chatgpt_json_to_structured_content(file_path, cfg): # Your original
    log_debug(f"Starting parse for: {file_path.name}")
    try:
        with open(file_path, 'r', encoding='utf-8') as f: data = json.load(f)
    except Exception as e:
        log_debug(f"  ERROR reading/parsing {file_path.name}: {e}")
        return [{"type": "error", "content": f"Error reading/parsing {Path(file_path).name}: {e}"}]
    mapping = data.get("mapping", {})
    valid_messages = [item_data["message"] for item_id, item_data in mapping.items() if item_data and item_data.get("message")]
    sorted_messages = sorted(valid_messages, key=lambda msg: msg.get("create_time") or float('inf'))
    structured_content_list = []
    image_counter = 0
    if cfg.get("include_filename_in_header", True):
         structured_content_list.append({"type": "header", "content": f"*** FILE: {Path(file_path).name} ***"})
         log_debug(f"  Added file header.")
    for msg_idx, msg_data in enumerate(sorted_messages):
        msg_id_for_log = msg_data.get("id", f"message_{msg_idx}")
        log_debug(f"  Processing message {msg_id_for_log}...")
        author_info = msg_data.get("author", {}); role = author_info.get("role", "unknown")
        log_debug(f"    Author role: {role}")
        is_potential_image_message = False
        content_data_check = msg_data.get("content",{})
        if isinstance(content_data_check, dict):
            cd_check_content_type = content_data_check.get("content_type")
            if cd_check_content_type == "image_asset_pointer":
                asset_ptr = content_data_check.get("asset_pointer", "")
                if isinstance(asset_ptr, str) and asset_ptr.startswith("data:"): is_potential_image_message = True
            elif "parts" in content_data_check and isinstance(content_data_check["parts"], list) and content_data_check["parts"]:
                first_part = content_data_check["parts"][0]
                if isinstance(first_part, str) and first_part.startswith("data:"): is_potential_image_message = True
                elif isinstance(first_part, dict) and first_part.get("content_type") == "image_asset_pointer":
                    asset_ptr_part = first_part.get("asset_pointer", "")
                    if isinstance(asset_ptr_part, str) and asset_ptr_part.startswith("data:"): is_potential_image_message = True
        log_debug(f"    Is potential image message: {is_potential_image_message}")
        if cfg.get("skip_system_tool_messages", True) and role in ["system", "tool"] and not is_potential_image_message:
            log_debug(f"    Skipping system/tool message (role: {role}, content_type: {content_data_check.get('content_type') if isinstance(content_data_check, dict) else 'N/A'}).")
            continue
        content_data = msg_data.get("content")
        log_debug(f"    Message content_type: {content_data.get('content_type') if isinstance(content_data, dict) else 'N/A (content is not dict)'}")
        message_parts_collector = []
        data_uri_found_in_message = None
        source_dict_for_image_metadata = None
        text_parts_for_current_message_block = []
        if isinstance(content_data, dict) and content_data.get("content_type") == "image_asset_pointer":
            asset_pointer_value = content_data.get("asset_pointer")
            log_debug(f"    Top-level content is image_asset_pointer. Asset pointer (first 100): {str(asset_pointer_value)[:100]}...")
            if isinstance(asset_pointer_value, str) and asset_pointer_value.startswith("data:"):
                data_uri_found_in_message = asset_pointer_value
                source_dict_for_image_metadata = content_data
                log_debug(f"    Data URI found in top-level asset_pointer.")
        if not data_uri_found_in_message and isinstance(content_data, dict):
            parts = content_data.get("parts", [])
            if not isinstance(parts, list): parts = [parts] if parts else []
            log_debug(f"    Iterating through {len(parts)} content part(s)...")
            for part_idx, part_content in enumerate(parts):
                log_debug(f"      Part {part_idx}: Type: {type(part_content)}")
                if isinstance(part_content, str):
                    log_debug(f"        String Part Content (first 60 chars): '{part_content[:60]}'")
                    if part_content.startswith("data:"):
                        data_uri_found_in_message = part_content; source_dict_for_image_metadata = None; break
                    elif part_content.strip(): text_parts_for_current_message_block.append(part_content)
                elif isinstance(part_content, dict):
                    part_content_type = part_content.get("content_type")
                    log_debug(f"        Dict Part: content_type='{part_content_type}'")
                    if part_content_type == "image_asset_pointer":
                        asset_pointer_value = part_content.get("asset_pointer")
                        log_debug(f"          Dict Part is image_asset_pointer. Asset pointer (first 100): {str(asset_pointer_value)[:100]}...")
                        if isinstance(asset_pointer_value, str) and asset_pointer_value.startswith("data:"):
                            data_uri_found_in_message = asset_pointer_value; source_dict_for_image_metadata = part_content; break
                    elif part_content_type == "multimodal_text" and "parts" in part_content:
                        log_debug(f"          Dict Part is multimodal_text, checking sub-parts...")
                        for sub_part_idx, sub_part in enumerate(part_content.get("parts", [])):
                            log_debug(f"            Sub-Part {sub_part_idx}: Type: {type(sub_part)}")
                            if isinstance(sub_part, dict) and sub_part.get("content_type") == "image_asset_pointer":
                                asset_pointer_value = sub_part.get("asset_pointer")
                                log_debug(f"              Sub-Part is image_asset_pointer. Asset pointer (first 100): {str(asset_pointer_value)[:100]}...")
                                if isinstance(asset_pointer_value, str) and asset_pointer_value.startswith("data:"):
                                    data_uri_found_in_message = asset_pointer_value; source_dict_for_image_metadata = sub_part; break
                        if data_uri_found_in_message: break
                    elif part_content.get("text","").strip():
                         text_parts_for_current_message_block.append(part_content.get("text"))
                         log_debug(f"        Appended text from dict part: '{part_content.get('text')[:60]}'")
        elif not data_uri_found_in_message and isinstance(content_data, str):
            # Handle simple string content
            log_debug(f"    Content is simple string: '{content_data[:60]}...'")
            if content_data.strip():
                text_parts_for_current_message_block.append(content_data)
                log_debug(f"    Appended text from simple string content")
        elif not data_uri_found_in_message and isinstance(content_data, dict) and not content_data.get("parts") and content_data.get("text","").strip():
             message_parts_collector.append(content_data.get("text")); log_debug(f"    Appended text from top-level content (no parts): {content_data.get('text')[:60]}")
        if text_parts_for_current_message_block: message_parts_collector.append(" ".join(text_parts_for_current_message_block).strip())
        if data_uri_found_in_message:
            log_debug(f"    Processing found data URI (first 60 chars): {data_uri_found_in_message[:60]}...")
            image_counter += 1; image_filename_stem = f"image_{image_counter:03d}"
            data_uri_match = re.match(r'data:([^;]+);base64,([A-Za-z0-9+/=\s]+)', data_uri_found_in_message, re.DOTALL)
            if data_uri_match:
                original_full_mime_type = data_uri_match.group(1); base64_str = "".join(data_uri_match.group(2).split())
                log_debug(f"    Regex matched. Original Full MIME: {original_full_mime_type}, Base64 (first 30): {base64_str[:30]}...")
                mime_type_for_embedding = original_full_mime_type; image_ext = "bin"
                if original_full_mime_type.startswith("image/"):
                    mime_type_for_embedding = original_full_mime_type; image_ext = original_full_mime_type.split('/')[-1].split('+')[0]
                    if image_ext == "jpeg": image_ext = "jpg"
                elif original_full_mime_type == "application/octet-stream":
                    log_debug(f"    Detected application/octet-stream.")
                    filename_from_meta = None
                    if source_dict_for_image_metadata and "metadata" in source_dict_for_image_metadata: filename_from_meta = source_dict_for_image_metadata["metadata"].get("filename"); log_debug(f"      Found metadata in source_dict, filename: {filename_from_meta}")
                    elif isinstance(content_data, dict) and "metadata" in content_data and content_data.get("content_type") == "image_asset_pointer": filename_from_meta = content_data["metadata"].get("filename"); log_debug(f"      Found metadata in top-level content, filename: {filename_from_meta}")
                    if filename_from_meta:
                        potential_ext = Path(filename_from_meta).suffix
                        if potential_ext and len(potential_ext) > 1:
                            image_ext = potential_ext[1:].lower(); log_debug(f"      Using extension from metadata filename: '{image_ext}'")
                            if image_ext in ["jpg", "jpeg"]: mime_type_for_embedding = "image/jpeg"
                            elif image_ext == "png": mime_type_for_embedding = "image/png"
                            elif image_ext == "gif": mime_type_for_embedding = "image/gif"
                            elif image_ext == "webp": mime_type_for_embedding = "image/webp"
                            elif image_ext == "svg": mime_type_for_embedding = "image/svg+xml"
                            else: mime_type_for_embedding = "application/octet-stream"
                            log_debug(f"      Mapped to embedding MIME: '{mime_type_for_embedding}'")
                    if mime_type_for_embedding == "application/octet-stream":
                        if base64_str.startswith("/9j/"): image_ext, mime_type_for_embedding = "jpg", "image/jpeg"
                        elif base64_str.startswith("iVBOR"): image_ext, mime_type_for_embedding = "png", "image/png"
                        elif base64_str.startswith("R0lGOD"): image_ext, mime_type_for_embedding = "gif", "image/gif" # --- CORRECTED TYPO --- base_str to base64_str
                        elif base64_str.startswith("UklGR"): image_ext, mime_type_for_embedding = "webp", "image/webp"
                        log_debug(f"      After prefix guess (if applicable): Guessed extension '{image_ext}', embedding MIME '{mime_type_for_embedding}'.")
                    if mime_type_for_embedding == "application/octet-stream" and PIL_AVAILABLE and cfg.get("use_pillow_for_unknown_images", True):
                        log_debug("      Attempting image type detection with Pillow as a fallback...")
                        try:
                            img_bytes = base64.b64decode(base64_str); pil_img = PILImage.open(io.BytesIO(img_bytes)); pil_format = pil_img.format
                            if pil_format:
                                pil_format = pil_format.lower(); log_debug(f"        Pillow identified format: {pil_format}")
                                if pil_format == "jpeg": mime_type_for_embedding, image_ext = "image/jpeg", "jpg"
                                elif pil_format == "png": mime_type_for_embedding, image_ext = "image/png", "png"
                                elif pil_format == "gif": mime_type_for_embedding, image_ext = "image/gif", "gif"
                                elif pil_format == "webp": mime_type_for_embedding, image_ext = "image/webp", "webp"
                                else: log_debug(f"        Pillow format '{pil_format}' not explicitly mapped to MIME type for embedding.")
                                if mime_type_for_embedding != "application/octet-stream": log_debug(f"        Using Pillow result: EmbedMIME='{mime_type_for_embedding}', Ext='{image_ext}'")
                            else: log_debug("        Pillow could not determine image format.")
                        except Exception as pil_e: log_debug(f"        Pillow processing error: {pil_e}")
                    elif not PIL_AVAILABLE and cfg.get("use_pillow_for_unknown_images", True): log_debug("      Pillow fallback configured but Pillow library is not available.")
                else:
                    log_debug(f"    Non-image or unhandled MIME type: {original_full_mime_type}. Treating as binary.")
                    mime_type_for_embedding = original_full_mime_type
                    filename_from_meta = None
                    if source_dict_for_image_metadata and "metadata" in source_dict_for_image_metadata: filename_from_meta = source_dict_for_image_metadata["metadata"].get("filename")
                    elif isinstance(content_data, dict) and "metadata" in content_data: filename_from_meta = content_data["metadata"].get("filename")
                    if filename_from_meta and Path(filename_from_meta).suffix: image_ext = Path(filename_from_meta).suffix[1:].lower()
                    else: image_ext = "bin"
                img_data_obj = ImageData(image_filename_stem, mime_type_for_embedding, base64_str, original_full_mime_type=original_full_mime_type, original_data_uri=data_uri_found_in_message)
                structured_content_list.append({"type": "image", "data": img_data_obj, "role": role, "timestamp": msg_data.get("create_time")})
            else:
                placeholder = f"[UnrecognizedDataURIFormat: {data_uri_found_in_message[:60]}...]"
                if "sediment://" in data_uri_found_in_message: placeholder = f"[ImageRef_Sediment: {Path(data_uri_found_in_message).name}]"
                message_parts_collector.append(placeholder); log_debug(f"    Data URI found but general regex did not match. Appended placeholder: {placeholder}")
        final_text_for_message = " ".join(message_parts_collector).strip()
        if final_text_for_message:
            structured_content_list.append({"type": "text", "content": final_text_for_message, "role": role, "timestamp": msg_data.get("create_time")})
            log_debug(f"    Appended text block: '{final_text_for_message[:60]}...'")
    log_debug(f"Finished parsing {file_path.name}. Total structured items: {len(structured_content_list)}")
    return structured_content_list

def parse_xml_backup(file_path):
    """Parse simple XML backups with <message role=""> elements."""
    log_debug(f"Starting parse for XML: {file_path.name}")
    try:
        tree = ET.parse(file_path)
        root_elem = tree.getroot()
    except Exception as e:
        log_debug(f"  ERROR reading/parsing {file_path.name}: {e}")
        return [{"type": "error", "content": f"Error reading/parsing {Path(file_path).name}: {e}"}]
    structured = []
    structured.append({"type": "header", "content": f"*** FILE: {Path(file_path).name} ***"})
    for msg in root_elem.findall('.//message'):
        role = msg.get('role', 'unknown')
        ts = msg.get('timestamp') or msg.get('time')
        text = ''.join(msg.itertext()).strip()
        structured.append({"type": "text", "content": text, "role": role, "timestamp": ts})
    log_debug(f"Finished parsing {file_path.name}. Total structured items: {len(structured)}")
    return structured


# --- Format-Specific Renderers (from your V6.2(timestamp Edition).py - These are your extensive functions) ---
def render_to_text(structured_content, cfg): # Your original
    output_lines = []
    for item in structured_content:
        if item["type"] == "header": output_lines.append(item["content"])
        elif item["type"] == "text":
            entry = ""; ts_str = ""
            if cfg.get("include_roles_in_export", True): entry += f"\n**{str(item['role']).upper()}**:\n"
            if cfg.get("include_timestamps_in_export", False) and item.get("timestamp"):
                try: ts_str = f"[{datetime.fromtimestamp(item['timestamp']).strftime('%Y-%m-%d %H:%M:%S')}]\n"
                except: pass
            entry += ts_str + item["content"]
            output_lines.append(entry)
        elif item["type"] == "image": output_lines.append(f"[Image: {item['data'].full_filename} (MIME: {item['data'].original_full_mime_type})]")
    return "\n".join(output_lines).strip()

def render_to_markdown(structured_content, cfg, images_base_path_for_saving=None): # Your original
    output_lines = []
    for item in structured_content:
        if item["type"] == "header": output_lines.append(item["content"] + "\n")
        elif item["type"] == "text":
            entry = ""; ts_str = ""
            if cfg.get("include_roles_in_export", True): entry += f"\n**{str(item['role']).upper()}**:\n"
            if cfg.get("include_timestamps_in_export", False) and item.get("timestamp"):
                try: ts_str = f"[{datetime.fromtimestamp(item['timestamp']).strftime('%Y-%m-%d %H:%M:%S')}]\n"
                except: pass
            entry += ts_str + item["content"]
            output_lines.append(entry)
        elif item["type"] == "image":
            img_data = item["data"]
            if cfg.get("export_images_folder", True) and images_base_path_for_saving and img_data.mime_type.startswith("image/"):
                img_data.local_file_path = images_base_path_for_saving / img_data.full_filename
                try:
                    image_binary_data = base64.b64decode(img_data.base64_str)
                    with open(img_data.local_file_path, 'wb') as img_f: img_f.write(image_binary_data)
                    rel_path = f"{images_base_path_for_saving.name}/{img_data.full_filename}".replace(os.sep, '/')
                    output_lines.append(f"![{img_data.filename_stem}]({rel_path})")
                except Exception as e: output_lines.append(f"[ErrSaveImg_MD {img_data.filename_stem}: {e}]"); log_debug(f"  MD: Error saving image {img_data.full_filename}: {e}")
            elif cfg.get("export_images_inline", False) and img_data.mime_type.startswith("image/"):
                output_lines.append(f"![{img_data.filename_stem}](data:{img_data.mime_type};base64,{img_data.base64_str})")
            else: output_lines.append(f"[ImgOmitted_MD: {img_data.full_filename} (MIME: {img_data.original_full_mime_type})]")
    return "\n".join(output_lines).strip()

def render_to_html(structured_content, cfg, images_base_path_for_saving=None): # Your original
    html_parts = ['<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><title>Chat Export</title>',
                  '<style>body{font-family: sans-serif; line-height: 1.6;} .message{margin-bottom: 1em; padding: 0.5em; border-radius: 5px;}',
                  '.user{background-color: #e1f5fe;} .assistant, .tool{background-color: #f0f4c3;} .system{background-color: #eee;} img{max-width:100%; height:auto; display:block; margin-top:0.5em;} strong{font-weight:bold;}</style>',
                  '</head><body>']
    header_content = next((item['content'] for item in structured_content if item["type"] == "header"), None)
    if header_content: html_parts.append(f"<h1>{header_content.replace('*** FILE: ','').replace(' ***','')}</h1>")
    for item in structured_content:
        if item["type"] == "header": continue
        html_parts.append(f'<div class="message {item["role"]}">')
        ts_str = ""; role_str = ""
        if cfg.get("include_roles_in_export", True): role_str = f"<strong>{str(item['role']).upper()}:</strong><br>"
        if cfg.get("include_timestamps_in_export", False) and item.get("timestamp"):
            try: ts_str = f"<small>[{datetime.fromtimestamp(item['timestamp']).strftime('%Y-%m-%d %H:%M:%S')}]</small><br>"
            except: pass
        html_parts.append(role_str + ts_str)
        if item["type"] == "text":
            text_content = item["content"].replace('\n', '<br>')
            text_content = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text_content, flags=re.DOTALL); text_content = re.sub(r'__(.*?)__', r'<strong>\1</strong>', text_content, flags=re.DOTALL)
            text_content = re.sub(r'\*(.*?)\*', r'<em>\1</em>', text_content, flags=re.DOTALL); text_content = re.sub(r'_(.*?)_', r'<em>\1</em>', text_content, flags=re.DOTALL)
            html_parts.append(text_content)
        elif item["type"] == "image":
            img_data = item["data"]
            if cfg.get("export_images_folder", True) and images_base_path_for_saving and img_data.mime_type.startswith("image/"):
                img_data.local_file_path = images_base_path_for_saving / img_data.full_filename
                try:
                    image_binary_data = base64.b64decode(img_data.base64_str)
                    with open(img_data.local_file_path, 'wb') as img_f: img_f.write(image_binary_data)
                    rel_path = f"{images_base_path_for_saving.name}/{img_data.full_filename}".replace(os.sep, '/')
                    html_parts.append(f'<img src="{rel_path}" alt="{img_data.filename_stem}">')
                except Exception as e: html_parts.append(f"[ErrSaveImg_HTML {img_data.filename_stem}: {e}]"); log_debug(f"  HTML: Error saving {img_data.full_filename}: {e}")
            elif cfg.get("export_images_inline", False) and img_data.mime_type.startswith("image/"):
                html_parts.append(f'<img src="data:{img_data.mime_type};base64,{img_data.base64_str}" alt="{img_data.filename_stem}">')
            else: html_parts.append(f"[ImgOmitted_HTML: {img_data.full_filename} (MIME: {img_data.original_full_mime_type})]")
        html_parts.append('</div>')
    html_parts.append('</body></html>')
    return "\n".join(html_parts)

def render_to_mhtml(structured_content, cfg, output_dir, chat_file_stem): # Your original
    msg = MIMEMultipart('related', type="text/html")
    msg['Subject'] = f"Chat Export: {chat_file_stem}"; msg['Date'] = formatdate(localtime=True); msg['MIME-Version'] = '1.0'
    html_file_name_for_cid = f"{chat_file_stem}.html"; html_cid = make_msgid(domain=html_file_name_for_cid)[1:-1]
    msg.add_header('Content-Type', f'multipart/related; type="text/html"; start="<{html_cid}>"')
    msg.preamble = 'This is a multi-part message in MIME format.'
    html_parts_for_mhtml = ['<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><title>Chat Export: '+chat_file_stem+'</title>',
                            '<style>body{font-family: sans-serif; line-height: 1.6;} .message{margin-bottom: 1em; padding: 0.5em; border-radius: 5px;}',
                            '.user{background-color: #e1f5fe;} .assistant, .tool{background-color: #f0f4c3;} .system{background-color: #eee;} img{max-width:100%; height:auto; display:block; margin-top:0.5em;} strong{font-weight:bold;}</style>',
                            '</head><body>']
    header_content = next((item['content'] for item in structured_content if item["type"] == "header"), None)
    if header_content: html_parts_for_mhtml.append(f"<h1>{header_content.replace('*** FILE: ','').replace(' ***','')}</h1>")
    image_mime_parts = []; image_cid_counter = 0
    for item in structured_content:
        if item["type"] == "header": continue
        html_parts_for_mhtml.append(f'<div class="message {item["role"]}">')
        ts_str = ""; role_str = ""
        if cfg.get("include_roles_in_export", True): role_str = f"<strong>{str(item['role']).upper()}:</strong><br>"
        if cfg.get("include_timestamps_in_export", False) and item.get("timestamp"):
            try: ts_str = f"<small>[{datetime.fromtimestamp(item['timestamp']).strftime('%Y-%m-%d %H:%M:%S')}]</small><br>"
            except: pass
        html_parts_for_mhtml.append(role_str + ts_str)
        if item["type"] == "text":
            text_content = item["content"].replace('\n', '<br>')
            text_content = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text_content, flags=re.DOTALL); text_content = re.sub(r'__(.*?)__', r'<strong>\1</strong>', text_content, flags=re.DOTALL)
            text_content = re.sub(r'\*(.*?)\*', r'<em>\1</em>', text_content, flags=re.DOTALL); text_content = re.sub(r'_(.*?)_', r'<em>\1</em>', text_content, flags=re.DOTALL)
            html_parts_for_mhtml.append(text_content)
        elif item["type"] == "image":
            img_data = item["data"]; image_binary_data = None;
            if not img_data.mime_type.startswith("image/"):
                html_parts_for_mhtml.append(f"[NonImageMIME_MHTML: {img_data.full_filename} ({img_data.original_full_mime_type})]")
                continue
            try: image_binary_data = base64.b64decode(img_data.base64_str)
            except Exception as e: html_parts_for_mhtml.append(f"[ErrDecodeImg_MHTML {img_data.filename_stem}: {e}]"); log_debug(f"  MHTML: Error decoding {img_data.full_filename}: {e}"); continue
            image_cid_counter += 1
            img_content_id_value = make_msgid(domain=f"image{image_cid_counter}")[1:-1]
            html_parts_for_mhtml.append(f'<img src="cid:{img_content_id_value}" alt="{img_data.filename_stem}">')
            mime_image = MIMEImage(image_binary_data, _subtype=img_data.image_ext)
            mime_image.add_header('Content-ID', f'<{img_content_id_value}>')
            mime_image.add_header('Content-Location', img_data.full_filename)
            image_mime_parts.append(mime_image)
        html_parts_for_mhtml.append('</div>')
    html_parts_for_mhtml.append('</body></html>')
    html_content_final = "\n".join(html_parts_for_mhtml)
    html_part = MIMEText(html_content_final, 'html', _charset='utf-8')
    html_part.add_header('Content-ID', f'<{html_cid}>'); html_part.add_header('Content-Location', html_file_name_for_cid)
    msg.attach(html_part)
    for img_part in image_mime_parts: msg.attach(img_part)
    return msg

def render_to_rtf(structured_content, cfg): # Your original
    rtf_parts = [r"{\rtf1\ansi\deff0\nouicompat{\fonttbl{\f0\fnil\fcharset0 Calibri;}}", r"\pard\sa200\sl276\slmult1\f0\fs24 "]
    def escape_rtf(text): return text.replace('\\', r'\\').replace('{', r'\{').replace('}', r'\}').encode('ascii', 'backslashreplace').decode('ascii')
    for item_idx, item in enumerate(structured_content):
        current_rtf_block = ""
        if item["type"] == "header": current_rtf_block += r"{\b\fs32 " + escape_rtf(item["content"].replace('*** FILE: ','').replace(' ***','')) + r"\par}" + "\n"
        elif item["type"] == "text" or item["type"] == "image":
            ts_str_rtf = ""; role_str_rtf = ""
            if cfg.get("include_roles_in_export", True): role_str_rtf = r"{\b " + escape_rtf(str(item['role']).upper()) + r":}\line " + "\n"
            if cfg.get("include_timestamps_in_export", False) and item.get("timestamp"):
                try: ts_str_rtf = r"{\i [" + escape_rtf(datetime.fromtimestamp(item['timestamp']).strftime('%Y-%m-%d %H:%M:%S')) + r"]}\line " + "\n"
                except: pass
            current_rtf_block += role_str_rtf + ts_str_rtf
            if item["type"] == "text":
                text_content = item["content"]
                text_content = re.sub(r'\*\*(.*?)\*\*', r'{\\b \1}', text_content, flags=re.DOTALL); text_content = re.sub(r'__(.*?)__', r'{\\b \1}', text_content, flags=re.DOTALL)
                text_content = re.sub(r'\*(.*?)\*', r'{\\i \1}', text_content, flags=re.DOTALL); text_content = re.sub(r'_(.*?)_', r'{\\i \1}', text_content, flags=re.DOTALL)
                text_lines = text_content.split('\n')
                for line in text_lines: current_rtf_block += escape_rtf(line) + r"\line " + "\n"
            elif item["type"] == "image":
                img_data = item["data"]
                if cfg.get("export_images_inline", False) and img_data.mime_type == "image/png":
                    try:
                        image_binary_data = base64.b64decode(img_data.base64_str); hex_data = image_binary_data.hex()
                        current_rtf_block += r"{\pict\pngblip\picwgoal8000\pichgoal6000 " + hex_data + r"}\line" + "\n"
                    except Exception as e: current_rtf_block += escape_rtf(f"[PNG Embed Error: {img_data.full_filename} - {e}]") + r"\line" + "\n"; log_debug(f"      RTF: PNG Embed Error {img_data.filename_stem}: {e}")
                else: current_rtf_block += escape_rtf(f"[Image: {img_data.full_filename} (MIME: {img_data.original_full_mime_type})]") + r"\line" + "\n"
            current_rtf_block += r"\par" + "\n"
        rtf_parts.append(current_rtf_block)
    rtf_parts.append("}")
    return "".join(rtf_parts)


# Overwrite with tag-definition aware version
def render_to_amandamap_md(structured_content, cfg):
    """Convert structured chat content to proper AmandaMap format with emoji markers.

    Parameters
    ----------
    structured_content : list
        Parsed message objects with ``type`` and associated data.
    cfg : dict
        Application configuration dictionary.

    Returns
    -------
    dict or None
        ``None`` if the content should be skipped due to mirror entity
        classification. Otherwise a dictionary with ``content`` and
        ``full_body`` keys containing the rendered AmandaMap format.
    """

    from datetime import datetime
    import re

    # Extract all text content
    body_lines = []
    title = "Untitled"
    
    for item in structured_content:
        if item["type"] == "text":
            body_lines.append(item["content"])
        elif item["type"] == "header":
            title = item["content"].replace("*** FILE:", "").replace("***", "").strip()
        elif item["type"] == "image":
            body_lines.append(f"![{item['data'].filename_stem}]({item['data'].full_filename})")
    
    full_body = "\n\n".join(body_lines).strip()
    
    # Check for mirror entity contamination
    classification = classify_mirror_entity_content(full_body)
    if cfg.get("mirror_entity_redaction_enabled", True) and classification == "skip":
        return None
    
    # Determine entry type and convert to proper AmandaMap format
    content_lower = full_body.lower()
    
    # Check for different AmandaMap entry types
    if "threshold" in content_lower or "core declaration" in content_lower:
        return _convert_to_threshold_format(full_body, title)
    elif "whispered flame" in content_lower or "whisper" in content_lower:
        return _convert_to_whispered_flame_format(full_body, title)
    elif "flame vow" in content_lower or "vow" in content_lower:
        return _convert_to_flame_vow_format(full_body, title)
    elif "phoenix codex" in content_lower or "phoenix" in content_lower:
        return _convert_to_phoenix_codex_format(full_body, title)
    else:
        return _convert_to_amandamap_entry_format(full_body, title)


def _convert_to_threshold_format(content, title):
    """Convert content to AmandaMap Threshold format with 🔥 marker."""
    
    # Extract threshold-specific metadata
    core_declaration = ""
    field_notes = ""
    time_info = ""
    state_info = ""
    transmission_mode = ""
    
    # Look for Core Declaration
    cd_match = re.search(r"Core Declaration:\s*(.+)", content, re.IGNORECASE | re.DOTALL)
    if cd_match:
        core_declaration = cd_match.group(1).strip()
    
    # Look for Field Notes
    fn_match = re.search(r"Field Notes:\s*(.+)", content, re.IGNORECASE | re.DOTALL)
    if fn_match:
        field_notes = fn_match.group(1).strip()
    
    # Look for Time
    time_match = re.search(r"Time:\s*(.+)", content, re.IGNORECASE)
    if time_match:
        time_info = time_match.group(1).strip()
    
    # Look for State
    state_match = re.search(r"State:\s*(.+)", content, re.IGNORECASE)
    if state_match:
        state_info = state_match.group(1).strip()
    
    # Look for Transmission Mode
    tm_match = re.search(r"Transmission Mode:\s*(.+)", content, re.IGNORECASE)
    if tm_match:
        transmission_mode = tm_match.group(1).strip()
    
    # Generate proper AmandaMap Threshold format
    threshold_content = f"""🔥 **{title}**

**Core Declaration:**
{core_declaration if core_declaration else "Not specified"}

**Field Notes:**
{field_notes if field_notes else "Not specified"}

**Metadata:**
- **Time:** {time_info if time_info else "Not specified"}
- **State:** {state_info if state_info else "Not specified"}
- **Transmission Mode:** {transmission_mode if transmission_mode else "Not specified"}

**Content:**
{content}

---
*Generated from chat export*"""
    
    return {
        "content": threshold_content,
        "full_body": content
    }


def _convert_to_whispered_flame_format(content, title):
    """Convert content to AmandaMap Whispered Flame format with 🕯️ marker."""
    
    whispered_flame_content = f"""🕯️ **{title}**

**Whispered Flame Entry:**

{content}

---
*Generated from chat export*"""
    
    return {
        "content": whispered_flame_content,
        "full_body": content
    }


def _convert_to_flame_vow_format(content, title):
    """Convert content to AmandaMap Flame Vow format with 📜 marker."""
    
    flame_vow_content = f"""📜 **{title}**

**Flame Vow Entry:**

{content}

---
*Generated from chat export*"""
    
    return {
        "content": flame_vow_content,
        "full_body": content
    }


def _convert_to_phoenix_codex_format(content, title):
    """Convert content to AmandaMap Phoenix Codex format with 🪶 marker."""
    
    phoenix_codex_content = f"""🪶 **{title}**

**Phoenix Codex Entry:**

{content}

---
*Generated from chat export*"""
    
    return {
        "content": phoenix_codex_content,
        "full_body": content
    }


def _convert_to_amandamap_entry_format(content, title):
    """Convert content to general AmandaMap entry format with 🔱 marker."""
    
    amandamap_entry_content = f"""🔱 **{title}**

**AmandaMap Entry:**

{content}

---
*Generated from chat export*"""
    
    return {
        "content": amandamap_entry_content,
        "full_body": content
    }

# --- save_multiple_files (from your V6.2(timestamp Edition).py) ---


def save_multiple_files(file_paths, cfg, output_dir, combine_all=False, export_log_widget_ref=None):
    output_dir_path = Path(output_dir)
    all_outputs_for_combine = []
    success_count = 0; failure_count = 0
    already_exported_files = set()

    def log_status_export(message):
        if export_log_widget_ref and export_log_widget_ref.winfo_exists():
            export_log_widget_ref.insert(tk.END, message + "\n"); export_log_widget_ref.see(tk.END); export_log_widget_ref.update_idletasks()
        else: print(message)
    for file_path_str in file_paths:
        file_path = Path(file_path_str); chat_file_stem = file_path.stem
        log_status_export(f"Processing: {file_path.name} for format {cfg['export_format']}...")
        if file_path.suffix.lower() == '.xml':
            try:
                root_tag = ET.parse(file_path).getroot().tag.lower()
            except Exception as e_par:
                log_status_export(f"  ERROR reading/parsing {file_path.name}: {e_par}")
                failure_count += 1
                continue
            if root_tag == 'smses':
                structured_content = parse_sms_smsbackup(file_path, logger=log_debug)
            else:
                structured_content = parse_xml_backup(file_path, logger=log_debug)
        else:
            structured_content = parse_chatgpt_json_to_structured_content(file_path, cfg)

        if not structured_content or (len(structured_content) == 1 and structured_content[0]["type"] == "error"):
            error_msg = structured_content[0]["content"] if structured_content else "Unknown parsing error"
            log_status_export(f"  ERROR parsing {file_path.name}: {error_msg}"); failure_count += 1; continue
        images_actual_subfolder_path = None
        if cfg.get("export_images_folder", True) and cfg["export_format"] in ["Markdown", "HTML"]:
            image_subfolder_name = cfg.get("image_folder_name", "_images").strip()
            if not image_subfolder_name: image_subfolder_name = "_images"
            images_actual_subfolder_path = output_dir_path / f"{chat_file_stem}{image_subfolder_name}"
            try: images_actual_subfolder_path.mkdir(parents=True, exist_ok=True)
            except Exception as e_mkdir: log_status_export(f"  ERROR creating image subfolder {images_actual_subfolder_path}: {e_mkdir}"); images_actual_subfolder_path = None
        rendered_content_obj = None; export_format = cfg['export_format']
        try:
            if export_format == "Text": rendered_content_obj = render_to_text(structured_content, cfg)
            elif export_format == "Markdown": rendered_content_obj = render_to_markdown(structured_content, cfg, images_actual_subfolder_path)
            elif export_format == "HTML": rendered_content_obj = render_to_html(structured_content, cfg, images_actual_subfolder_path)
            elif export_format == "MHTML": rendered_content_obj = render_to_mhtml(structured_content, cfg, output_dir_path, chat_file_stem)

            elif export_format == "RTF":
                rendered_content_obj = render_to_rtf(structured_content, cfg)
            elif export_format == "AmandaMap Markdown":
                rendered_content_obj = render_to_amandamap_md(structured_content, cfg)
                if rendered_content_obj is None:
                    log_status_export("  Skipped file: 100% Mirror Entity contamination")
                    continue
            else:
                log_status_export(f"  ERROR: Unsupported export format {export_format} for {file_path.name}")
                failure_count += 1
                continue
        except Exception as render_err:
            log_status_export(f"  ERROR rendering {file_path.name} to {export_format}: {render_err}")
            failure_count += 1
            continue

        if export_format == "AmandaMap Markdown" and isinstance(rendered_content_obj, dict):
            am_full_body = rendered_content_obj.get("full_body", "")
            classification = classify_mirror_entity_content(am_full_body)
        else:
            classification = None
        if combine_all:
            out_obj = rendered_content_obj["content"] if isinstance(rendered_content_obj, dict) else rendered_content_obj
            all_outputs_for_combine.append((chat_file_stem, out_obj, file_path))
        else:
            ext_map = {"Text": ".txt", "Markdown": ".md", "HTML": ".html", "MHTML": ".mht", "RTF": ".rtf", "AmandaMap Markdown": ".md"}
            ext = ext_map.get(export_format, ".txt")
            if export_format == "AmandaMap Markdown":
                vault_enabled = cfg.get("mirror_entity_redaction_enabled", True)
                if classification and vault_enabled:
                    vault = ensure_mirror_entity_vault(cfg, log_debug)
                    if classification == "skip":
                        log_status_export("  Skipped file: 100% Mirror Entity contamination")
                        continue
                    output_base = vault / classification
                else:
                    output_base = output_dir_path / "AmandaMapEntries"
                output_base.mkdir(parents=True, exist_ok=True)
                filename = generate_filename(chat_file_stem, ext)
                if filename in already_exported_files:
                    log_status_export(f"  Skipping duplicate export: {filename}")
                    continue
                already_exported_files.add(filename)
                output_file = output_base / filename
            else:
                filename = generate_filename(chat_file_stem, ext)
                if filename in already_exported_files:
                    log_status_export(f"  Skipping duplicate export: {filename}")
                    continue
                already_exported_files.add(filename)
                output_file = output_dir_path / filename
            try:
                if export_format == "MHTML" and isinstance(rendered_content_obj, MIMEMultipart):
                    with open(output_file, 'wb') as f_bin:
                        f_bin.write(rendered_content_obj.as_bytes(policy=policy.SMTP))
                elif isinstance(rendered_content_obj, dict):
                    with open(output_file, 'w', encoding='utf-8') as f_text:
                        f_text.write(rendered_content_obj["content"])
                elif isinstance(rendered_content_obj, str):
                    with open(output_file, 'w', encoding='utf-8') as f_text:
                        f_text.write(rendered_content_obj)
                else:
                    raise ValueError("Rendered content type error for single file save.")
                log_status_export(f"  SUCCESS: Saved {output_file.name}"); success_count += 1
            except Exception as e:
                log_status_export(f"  ERROR writing {output_file.name}: {e}"); failure_count += 1
                continue
        if combine_all: all_outputs_for_combine.append((chat_file_stem, rendered_content_obj, file_path))

        else:
            ext_map = {"Text": ".txt", "Markdown": ".md", "HTML": ".html", "MHTML": ".mht", "RTF": ".rtf", "AmandaMap Markdown": ".md"}
            ext = ext_map.get(export_format, ".txt")
            if export_format == "AmandaMap Markdown":
                am_dir = output_dir_path / "AmandaMapEntries"
                am_dir.mkdir(parents=True, exist_ok=True)
                output_file = am_dir / (chat_file_stem + ext)
            else:
                output_file = output_dir_path / (chat_file_stem + ext)
            try:
                if export_format == "MHTML" and isinstance(rendered_content_obj, MIMEMultipart):
                    with open(output_file, 'wb') as f_bin: f_bin.write(rendered_content_obj.as_bytes(policy=policy.SMTP))
                elif isinstance(rendered_content_obj, str):
                    with open(output_file, 'w', encoding='utf-8') as f_text: f_text.write(rendered_content_obj)
                else: raise ValueError("Rendered content type error for single file save.")
                log_status_export(f"  SUCCESS: Saved {output_file.name}"); success_count += 1
            except Exception as e: log_status_export(f"  ERROR writing {output_file.name}: {e}"); failure_count += 1
    if combine_all and all_outputs_for_combine:
        ext = '.txt'; current_export_format_for_combine = cfg['export_format']
        text_combinable_formats = {"Text": ".txt", "Markdown": ".md", "HTML": ".html", "RTF": ".rtf"}
        if current_export_format_for_combine in text_combinable_formats: ext = text_combinable_formats[current_export_format_for_combine]
        else: ext = ".txt"; log_status_export(f"Note: Combining {current_export_format_for_combine} files. Output will be a text manifest.")
        combined_filename = "Combined_ChatGPT_Export_" + datetime.now().strftime("%Y%m%d_%H%M%S") + ext
        combined_path = output_dir_path / combined_filename
        try:
            with open(combined_path, 'w', encoding='utf-8') as f:
                if current_export_format_for_combine == "HTML": f.write('<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><title>Combined Chat Export</title></head><body>\n')
                for title, content_obj, original_file_path_obj in all_outputs_for_combine:
                    dt_str = "Unknown Date"; header_text = ""
                    try: dt_str = datetime.fromtimestamp(original_file_path_obj.stat().st_mtime).strftime("%Y-%m-%d")
                    except: pass
                    header_base = f"FILE: {title} (Original: {original_file_path_obj.name})\nDATE: {dt_str}"
                    if current_export_format_for_combine == "HTML": header_text = f"<hr><h2>{header_base.replace(chr(10), ' - ')}</h2>\n"
                    else: header_text = f"\n\n{'=' * 80}\n{header_base}\n{'=' * 80}\n\n"
                    f.write(header_text)
                    if isinstance(content_obj, str):
                        content_to_write = content_obj
                        if current_export_format_for_combine == "HTML": content_to_write = re.sub(r'<!DOCTYPE[^>]*>|<html[^>]*>|<head>.*?</head>|<body[^>]*>|</body>|</html>', '', content_obj, flags=re.IGNORECASE | re.DOTALL).strip()
                        f.write(content_to_write)
                    elif isinstance(content_obj, MIMEMultipart): f.write(f"[MHTML Content for {title} - not directly combinable here.]\n")
                    else: f.write("[Unknown content type for combination]\n")
                if current_export_format_for_combine == "HTML": f.write('\n</body></html>')
            log_status_export(f"Combined file saved as {combined_path.name}"); success_count +=1
        except Exception as e: log_status_export(f"ERROR writing combined file {combined_path.name}: {e}"); failure_count +=1
    summary_message = f"Export process finished.\nSuccessful: {success_count}\nFailed: {failure_count}"
    log_status_export(f"\n{summary_message}")
    def show_summary_messagebox_export():
        if root and root.winfo_exists():
            if failure_count > 0 and success_count > 0: messagebox.showwarning("Export Partially Complete", summary_message, parent=root)
            elif failure_count > 0 and success_count == 0: messagebox.showerror("Export Failed", summary_message, parent=root)
            elif success_count > 0 : messagebox.showinfo("Export Complete", summary_message, parent=root)
    if app_instance_ref and hasattr(app_instance_ref.master, 'after'): app_instance_ref.master.after(0, show_summary_messagebox_export)
    else: print("INFO: Summary messagebox for export skipped (no GUI context).")

# --- Persistent Indexing Logic & Search (from your V6.2(timestamp Edition).py, MODIFIED for timestamps) ---
# --- MODIFIED: _build_generic_index - Start of significant modifications ---

def _build_generic_index(folder_to_index, cfg, file_patterns, index_file_to_save, progress_text_widget, is_json_source, existing_loaded_index_data=None, tags_per_file=None, tagmap_entries=None):
    # --- INTEGRATED: Initialize new structure for file_details ---

    if existing_loaded_index_data and isinstance(existing_loaded_index_data.get("index"), dict):
        existing_index_section = existing_loaded_index_data["index"]
        index_data = {
            "tokens": copy.deepcopy(existing_index_section.get("tokens", {})),
            "files": copy.deepcopy(existing_index_section.get("files", {})),
            "file_details": copy.deepcopy(existing_index_section.get("file_details", {}))
        }
        try:
            file_id_counter = max(int(fid) for fid in index_data["files"].keys()) + 1 if index_data["files"] else 0
        except ValueError:
            file_id_counter = 0
    else:
        index_data = {"tokens": {}, "files": {}, "file_details": {}}
        file_id_counter = 0

    def update_progress_indexing(message):
        """Write progress text to the widget safely from worker threads."""
        if progress_text_widget and progress_text_widget.winfo_exists():
            def do_update(msg=message):
                progress_text_widget.insert(tk.END, msg + "\n")
                progress_text_widget.see(tk.END)
                progress_text_widget.update_idletasks()

            progress_text_widget.after(0, do_update)
        else:
            print(f"INDEX_PROGRESS: {message}")

    update_progress_indexing(f"Starting indexing for: {folder_to_index}...")
    all_files_to_index = []
    for pattern in file_patterns:
        all_files_to_index.extend(list(Path(folder_to_index).rglob(pattern)))
    total_files = len(all_files_to_index)
    update_progress_indexing(f"Found {total_files} files matching patterns {file_patterns}.")
    processed_file_count_this_run = 0

    def process_file(file_path):
        actual_filename = file_path.name
        content_to_index = ""
        chat_started_at_ts, chat_ended_at_ts = None, None
        try:
            file_mod_time = os.path.getmtime(file_path)
        except Exception:
            file_mod_time = 0

        if not is_json_source:
            current_scan_start_ts, current_scan_end_ts = extract_chat_timestamps(str(file_path))
            final_start_ts_to_store, final_end_ts_to_store = current_scan_start_ts, current_scan_end_ts
            if existing_loaded_index_data and isinstance(existing_loaded_index_data.get("index", {}).get("files"), dict) and isinstance(existing_loaded_index_data["index"].get("file_details"), dict):
                try:
                    base_folder_for_relative = Path(folder_to_index)
                    relative_path_str_current = str(file_path.relative_to(base_folder_for_relative))
                    old_file_id_found = None
                    for old_fid, old_rel_path in existing_loaded_index_data["index"]["files"].items():
                        if old_rel_path == relative_path_str_current:
                            old_file_id_found = old_fid
                            break
                    if old_file_id_found and old_file_id_found in existing_loaded_index_data["index"]["file_details"]:
                        old_file_detail = existing_loaded_index_data["index"]["file_details"][old_file_id_found]
                        preserved_start_ts = old_file_detail.get("chat_started_at")
                        if preserved_start_ts:
                            final_start_ts_to_store = preserved_start_ts
                except Exception as e_ts_preserve:
                    log_debug(f"  Error during timestamp preservation for {actual_filename}: {e_ts_preserve}")
            chat_started_at_ts, chat_ended_at_ts = final_start_ts_to_store, final_end_ts_to_store

        if is_json_source:
            structured_data = parse_chatgpt_json_to_structured_content(file_path, cfg)
            text_for_indexing = []
            for item in structured_data:
                if item["type"] == "text":
                    text_for_indexing.append(item["content"])
                elif item["type"] == "image":
                    text_for_indexing.append(item["data"].placeholder_text)
                elif item["type"] == "error":
                    return None
            content_to_index = " ".join(text_for_indexing)
        else:
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content_to_index = f.read()
                if file_path.suffix in [".md", ".html"]:
                    content_to_index = re.sub(r"<style[^<]*<\/style>|<script[^<]*<\/script>|<[^>]+>|\[.*?\]\(.*?\)|#+\s*|\*\*|\*|_|`", " ", content_to_index, flags=re.IGNORECASE | re.DOTALL)
                    content_to_index = re.sub(r"\s+", " ", content_to_index).strip()
            except Exception:
                return None

        tokens_local = tokenize(content_to_index)
        if not tokens_local:
            return None
        try:
            relative_file_path_str = str(file_path.relative_to(Path(folder_to_index)))
        except ValueError:
            relative_file_path_str = str(file_path)
        return (relative_file_path_str, actual_filename, tokens_local, chat_started_at_ts, chat_ended_at_ts, file_mod_time)

    cpu_percent = cfg.get("cpu_usage_percent", 100)
    allowed_workers = max(1, int((os.cpu_count() or 1) * cpu_percent / 100))
    worker_count = min(max(cfg.get("num_tokenizers", 2), cfg.get("num_indexers", 2)), allowed_workers)

    futures = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=worker_count) as executor:
        for fp in all_files_to_index:
            futures.append((fp, executor.submit(process_file, fp)))
        for processed_count, (fp, fut) in enumerate(futures, 1):
            if progress_text_widget and not progress_text_widget.winfo_exists():
                log_debug("Indexing cancelled: Progress widget closed.")
                return None
            update_progress_indexing(f"Processing file {processed_count}/{total_files}: {fp.name}...")
            result = fut.result()
            if not result:
                continue
            relative_file_path_str, actual_filename, tokens, chat_started_at_ts, chat_ended_at_ts, file_mod_time = result
            file_id = next((fid for fid, fpath_str in index_data["files"].items() if fpath_str == relative_file_path_str), None)
            skip_file = False
            if file_id is not None:
                prev_details = index_data["file_details"].get(file_id, {})
                prev_mod = prev_details.get("file_mod_time")
                prev_end = prev_details.get("chat_ended_at")
                if prev_mod is not None and abs(prev_mod - file_mod_time) < 1 and prev_end == chat_ended_at_ts:
                    skip_file = True
                if not skip_file:
                    for tok, fid_list in list(index_data["tokens"].items()):
                        if file_id in fid_list:
                            new_list = [fid for fid in fid_list if fid != file_id]
                            if new_list:
                                index_data["tokens"][tok] = list(set(new_list))
                            else:
                                del index_data["tokens"][tok]
            if skip_file:
                continue
            if file_id is None:
                file_id = str(file_id_counter)
                index_data["files"][file_id] = relative_file_path_str
                file_id_counter += 1
            current_file_details = {
                "filename": actual_filename,
                "file_mod_time": file_mod_time,
                "indexed_at": datetime.now().isoformat(),
            }
            if tags_per_file:
                tag_key = relative_file_path_str
                tags_for_file = tags_per_file.get(tag_key) or tags_per_file.get(actual_filename)
                if tags_for_file:
                    current_file_details["tags"] = list(tags_for_file)
            if not is_json_source:
                if chat_started_at_ts:
                    current_file_details["chat_started_at"] = chat_started_at_ts
                if chat_ended_at_ts:
                    current_file_details["chat_ended_at"] = chat_ended_at_ts
            index_data["file_details"][file_id] = current_file_details
            for token in set(tokens):
                index_data["tokens"].setdefault(token, []).append(file_id)
                index_data["tokens"][token] = list(set(index_data["tokens"][token]))
            processed_file_count_this_run += 1
            if (processed_count) % 20 == 0 or processed_count == total_files:
                update_progress_indexing(f"  Indexed {processed_file_count_this_run}/{total_files} files...")
    tagmap_lookup = {}
    if tagmap_entries:
        for entry in tagmap_entries:
            doc = entry.get("document")
            line = entry.get("line")
            if doc and line is not None:
                try:
                    line_num = int(line)
                except Exception:
                    continue
                tagmap_lookup.setdefault(doc, {})[line_num] = {"category": entry.get("category"), "preview": entry.get("preview"), "date": entry.get("date")}
    if tagmap_lookup:
        for fid, rel_path in index_data.get("files", {}).items():
            doc_name = Path(rel_path).name
            if doc_name in tagmap_lookup:
                index_data.setdefault("file_details", {}).setdefault(fid, {}).setdefault("tagmap", {}).update(tagmap_lookup[doc_name])

    index_metadata = {
        "created_at": datetime.now().isoformat(),
        "indexed_folder_path": str(folder_to_index),
        "total_files_processed_in_this_run": processed_file_count_this_run,
        "total_files_in_index": len(index_data["files"]),
        "total_unique_tokens": len(index_data["tokens"]),
        "index_file_name": Path(index_file_to_save).name,
    }
    final_index_structure = {"metadata": index_metadata, "index": index_data}
    try:
        with open(index_file_to_save, "w", encoding="utf-8") as f:
            json.dump(final_index_structure, f, indent=2)
        update_progress_indexing(f"Indexing complete! Index saved to {Path(index_file_to_save).name}")
        global config
        if is_json_source:
            config["last_indexed_original_json_folder_path"] = str(folder_to_index)
        else:
            config["last_indexed_converted_files_folder_path"] = str(folder_to_index)
        save_config(config)
    except Exception as e_save_idx:
        update_progress_indexing(f"Error saving index: {e_save_idx}")
        if progress_text_widget and progress_text_widget.winfo_exists():
            progress_text_widget.after(
                0,
                lambda msg=e_save_idx: messagebox.showerror(
                    "Index Error",
                    f"Could not save search index: {msg}",
                    parent=progress_text_widget.master.master,
                ),
            )
    return final_index_structure

# --- MODIFIED: _build_generic_index - End of significant modifications ---

# --- MODIFIED: search_with_persistent_index - Start of modifications ---
def search_with_persistent_index(search_phrase, loaded_index_data, case_sensitive=False, search_logic="AND"):
    if not loaded_index_data or not isinstance(loaded_index_data.get("index"), dict) or \
       not isinstance(loaded_index_data["index"].get("tokens"), dict) or \
       not isinstance(loaded_index_data["index"].get("files"), dict) or \
       not isinstance(loaded_index_data["index"].get("file_details"), dict):
        return [], "Index is not loaded or is invalid (missing tokens, files, or file_details)."

    index_tokens_map = loaded_index_data["index"]["tokens"]
    files_id_to_path_map = loaded_index_data["index"]["files"]
    files_id_to_details_map = loaded_index_data["index"]["file_details"]

    indexed_folder_path_str = loaded_index_data.get("metadata", {}).get("indexed_folder_path", ".")
    indexed_folder_path = Path(indexed_folder_path_str if indexed_folder_path_str else ".")

    search_terms_raw = search_phrase.split()
    processed_search_terms = [term.lower() for term in search_terms_raw] if not case_sensitive else search_terms_raw
    if not processed_search_terms: return [], "No search terms entered."

    term_match_sets = []
    for term_query in processed_search_terms:
        current_term_fids = set()
        term_for_token_lookup = term_query.lower() if not case_sensitive else term_query
        if term_for_token_lookup in index_tokens_map:
            current_term_fids.update(index_tokens_map[term_for_token_lookup])

        for fid, details in files_id_to_details_map.items():
            filename_check = details.get("filename", "")
            if not case_sensitive:
                filename_check = filename_check.lower()
            if term_query in filename_check:
                current_term_fids.add(fid)
            if re.fullmatch(r"\d{4}-\d{2}-\d{2}|\d{2}:\d{2}(:\d{2})?", term_query):
                if term_query in details.get("chat_started_at", "") or term_query in details.get("chat_ended_at", ""):
                    current_term_fids.add(fid)
            for meta_field in ["type", "tags", "chakra", "spirits", "linked_rituals"]:
                meta_val = details.get(meta_field)
                if meta_val is None:
                    meta_val = details.get("metadata", {}).get(meta_field)
                if isinstance(meta_val, list):
                    vals = [v.lower() for v in meta_val] if not case_sensitive else [str(v) for v in meta_val]
                    if term_query in vals:
                        current_term_fids.add(fid)
                elif isinstance(meta_val, str):
                    check_val = meta_val.lower() if not case_sensitive else meta_val
                    if term_query in check_val:
                        current_term_fids.add(fid)
        if not current_term_fids and search_logic == "AND": return [], f"Term '{term_query}' yields no results with AND logic."
        term_match_sets.append(current_term_fids)

    if not term_match_sets: return [], "No documents found for any search terms."
    result_file_ids = set.intersection(*term_match_sets) if search_logic == "AND" else set.union(*term_match_sets)
    if not result_file_ids: return [], "Tokens/terms found, but no single document satisfies the search logic."

    results_with_details = []
    for fid_str in result_file_ids:
        relative_path_str = files_id_to_path_map.get(fid_str)
        details = files_id_to_details_map.get(fid_str, {})
        if relative_path_str:
            full_path_obj = indexed_folder_path / relative_path_str
            display_filename = details.get("filename", Path(relative_path_str).name)
            started_at = details.get("chat_started_at", "")
            ended_at = details.get("chat_ended_at", "")
            results_with_details.append((display_filename, started_at, ended_at, full_path_obj, fid_str, details))
        else: log_debug(f"Warning: File ID {fid_str} in search results but not in files_id_to_path_map.")
    if not results_with_details: return [], "Matched file IDs but could not retrieve file paths/details."
    return sorted(results_with_details, key=lambda x: x[0].lower()), None
# --- MODIFIED: search_with_persistent_index - End of modifications ---

# --- Editor Launch (from your V6.2(timestamp Edition).py, ensure global config is used) ---
def launch_editor(file_path, cfg_editor_unused): # cfg_editor_unused is not used, uses global config
    global config
    editor_path_str = config.get("default_editor", "")
    file_path_str = str(file_path)
    try:
        if editor_path_str and Path(editor_path_str).is_file() and Path(editor_path_str).exists():
            subprocess.Popen([editor_path_str, file_path_str])
        else:
            if platform.system() == "Windows": os.startfile(file_path_str)
            elif platform.system() == "Darwin": subprocess.run(["open", file_path_str], check=True)
            else: subprocess.run(["xdg-open", file_path_str], check=True)
    except FileNotFoundError:
        messagebox.showerror("Editor Error", f"Editor application '{editor_path_str}' or default open command not found.", parent=root)
        log_debug(f"ERROR: Editor or default open command not found for '{file_path_str}'. Custom editor: '{editor_path_str}'")
    except Exception as e:
        messagebox.showerror("Launch Error", f"Could not open file {file_path_str}:\n{e}", parent=root)
        log_debug(f"ERROR: Launching editor for '{file_path_str}': {e}")

# --- GUI Styling (from your V6.2(timestamp Edition).py) ---
def apply_styles(root_or_toplevel, current_theme_style): # Your original apply_styles
    s = ttk.Style(root_or_toplevel);
    try: s.theme_use('clam')
    except tk.TclError: s.theme_use(s.theme_names()[0] if s.theme_names() else 'default')
    root_or_toplevel.configure(bg=current_theme_style["bg"])
    default_font_tuple = ("Calibri", 10); bold_font_tuple = ("Calibri", 10, "bold")
    try:
        sys_default_font = tkFont.nametofont("TkDefaultFont")
        default_font_tuple = (sys_default_font.cget("family"), sys_default_font.cget("size"))
        bold_font_tuple = (sys_default_font.cget("family"), sys_default_font.cget("size"), "bold")
    except tk.TclError: pass
    s.configure('TLabel', background=current_theme_style["bg"], foreground=current_theme_style["fg"], font=default_font_tuple)
    s.configure('TButton', background=current_theme_style["btn"], foreground=current_theme_style["fg"], bordercolor=current_theme_style["fg"], lightcolor=current_theme_style["btn"], darkcolor=current_theme_style["btn"], relief='raised', focusthickness=1, focuscolor=current_theme_style["hl"], font=default_font_tuple, padding=3)
    s.map('TButton', background=[('active', current_theme_style["hl"]), ('disabled', current_theme_style["bg"])], foreground=[('active', current_theme_style["fg"]), ('disabled', '#a0a0a0')], relief=[('pressed', 'sunken'), ('!pressed', 'raised')])
    s.configure('TCombobox', fieldbackground=current_theme_style["entry_bg"], foreground=current_theme_style["entry_fg"], selectbackground=current_theme_style["hl"], selectforeground=current_theme_style["entry_fg"], insertcolor=current_theme_style["entry_fg"], arrowcolor=current_theme_style["fg"], font=default_font_tuple)
    s.map('TCombobox', fieldbackground=[('readonly', current_theme_style["entry_bg"])], selectbackground=[('focus', current_theme_style["hl"])], foreground=[('disabled', '#a0a0a0')])
    s.configure('TCheckbutton', background=current_theme_style["bg"], foreground=current_theme_style["fg"], indicatorcolor=current_theme_style["entry_bg"], font=default_font_tuple)
    s.map('TCheckbutton', indicatorcolor=[('selected', current_theme_style["hl"]), ('active', current_theme_style["entry_bg"])], foreground=[('disabled', '#a0a0a0')])
    s.configure('TEntry', fieldbackground=current_theme_style["entry_bg"], foreground=current_theme_style["entry_fg"], insertcolor=current_theme_style["entry_fg"], font=default_font_tuple)
    s.map('TEntry', foreground=[('disabled', '#a0a0a0'), ('readonly', current_theme_style["fg"])], fieldbackground=[('disabled', current_theme_style["bg"]), ('readonly', current_theme_style["bg"])])
    s.configure('TFrame', background=current_theme_style["bg"])
    s.configure('TLabelframe', background=current_theme_style["bg"], bordercolor=current_theme_style["fg"], lightcolor=current_theme_style["bg"], darkcolor=current_theme_style["bg"])
    s.configure('TLabelframe.Label', background=current_theme_style["bg"], foreground=current_theme_style["fg"], font=bold_font_tuple)
    s.configure('TScrollbar', background=current_theme_style["btn"], troughcolor=current_theme_style["bg"], bordercolor=current_theme_style["fg"], arrowcolor=current_theme_style["fg"], relief='flat')
    s.map('TScrollbar', background=[('active', current_theme_style["hl"])])
    s.configure('Treeview', background=current_theme_style["list_bg"], foreground=current_theme_style["list_fg"], fieldbackground=current_theme_style["list_bg"], font=default_font_tuple, rowheight=tkFont.Font(font=default_font_tuple).metrics("linespace") + 4)
    s.map('Treeview', background=[('selected', current_theme_style["list_hl_bg"])], foreground=[('selected', current_theme_style["list_hl_fg"])])
    s.configure('Treeview.Heading', background=current_theme_style["btn"], foreground=current_theme_style["fg"], relief="raised", font=bold_font_tuple, padding=(3,3))
    s.map('Treeview.Heading', background=[('active', current_theme_style["hl"])])
    s.configure('TMenubutton', background=current_theme_style["btn"], foreground=current_theme_style["fg"], font=default_font_tuple, padding=3)
    s.configure('TNotebook', background=current_theme_style["bg"], tabmargins=[2, 5, 2, 0])
    s.configure('TNotebook.Tab', background=current_theme_style["btn"], foreground=current_theme_style["fg"], padding=[8, 3], font=default_font_tuple)
    s.map('TNotebook.Tab', background=[('selected', current_theme_style["hl"])], foreground=[('selected', current_theme_style["fg"])], expand=[('selected', [1,1,1,0])])

# --- Main GUI App Class (Converted from your original build_gui function) ---
class App: # Your original App class structure
    def __init__(self, master):
        global app_instance_ref, config, root
        app_instance_ref = self
        self.master = master
        # root = master # root is already global and set in main()

        current_theme_name = config.get("theme", list(theme_styles.keys())[0])
        if current_theme_name not in theme_styles:
            current_theme_name = list(theme_styles.keys())[0]
            config["theme"] = current_theme_name
        self.current_style_colors = theme_styles[current_theme_name]
        self.master.title(f"GPT Export & Index Tool V6.3 {self.current_style_colors['emoji']} (Accuracy Edition)") # Version updated
        self.master.geometry(config.get("window_geometry", "1000x800+50+50"))
        apply_styles(self.master, self.current_style_colors)
        self.theme_cb_var = tk.StringVar(value=current_theme_name)
        self.export_format_var = tk.StringVar(value=config.get("export_format", "Text"))
        self.img_inline_var = tk.BooleanVar(value=config.get("export_images_inline", False))
        self.img_folder_var = tk.BooleanVar(value=config.get("export_images_folder", True))
        self.image_folder_name_var = tk.StringVar(value=config.get("image_folder_name", "_images"))
        self.combine_var = tk.BooleanVar(value=config.get("combine_output_files", False))
        self.include_timestamps_export_var = tk.BooleanVar(value=config.get("include_timestamps_in_export", False))
        self.skip_system_tool_var = tk.BooleanVar(value=config.get("skip_system_tool_messages", True))
        self.use_pillow_var = tk.BooleanVar(value=config.get("use_pillow_for_unknown_images", True))
        self.amandamap_mode_var = tk.BooleanVar(value=config.get("amandamap_mode", False))
        self.use_tagmap_tagging_var = tk.BooleanVar(value=config.get("use_tagmap_tagging", False))
        self.default_editor_var = tk.StringVar(value=config.get("default_editor", ""))
        self.index_type_options = ["Original JSONs (Indexed)", "Converted Files (Indexed)"]
        self.selected_index_type_var = tk.StringVar(value=config.get("selected_index_type", self.index_type_options[1]))
        self.search_term_var = tk.StringVar()
        self.case_sensitive_search_var = tk.BooleanVar(value=config.get("search_term_case_sensitive", False))
        self.search_logic_var = tk.StringVar(value=config.get("search_logic", "AND"))
        self.num_tokenizers_var = tk.IntVar(value=config.get("num_tokenizers", 2))
        self.num_indexers_var = tk.IntVar(value=config.get("num_indexers", 2))
        self.cpu_usage_percent_var = tk.IntVar(value=config.get("cpu_usage_percent", 100))
        self.tagmap_file_var = tk.StringVar(value=config.get("tagmap_file_path", ""))
        self.active_indexing_thread = None
        self.create_main_layout_and_widgets()
        self.on_index_type_changed()
        self.master.protocol("WM_DELETE_WINDOW", self.on_app_close)
        log_debug("INFO: Application GUI initialized successfully.")

    def on_app_close(self): # Your original
        global config
        config["window_geometry"] = self.master.winfo_geometry()
        config["theme"] = self.theme_cb_var.get()
        config["export_format"] = self.export_format_var.get()
        config["export_images_inline"] = self.img_inline_var.get()
        config["export_images_folder"] = self.img_folder_var.get()
        config["image_folder_name"] = self.image_folder_name_var.get()
        config["combine_output_files"] = self.combine_var.get()
        config["include_timestamps_in_export"] = self.include_timestamps_export_var.get()
        config["skip_system_tool_messages"] = self.skip_system_tool_var.get()
        config["use_pillow_for_unknown_images"] = self.use_pillow_var.get()
        config["use_tagmap_tagging"] = self.use_tagmap_tagging_var.get()
        config["default_editor"] = self.default_editor_var.get()
        config["selected_index_type"] = self.selected_index_type_var.get()
        config["search_term_case_sensitive"] = self.case_sensitive_search_var.get()
        config["search_logic"] = self.search_logic_var.get()
        config["num_tokenizers"] = self.num_tokenizers_var.get()
        config["num_indexers"] = self.num_indexers_var.get()
        config["cpu_usage_percent"] = self.cpu_usage_percent_var.get()
        config["tagmap_file_path"] = self.tagmap_file_var.get()
        if hasattr(self, 'notebook') and self.notebook.winfo_exists():
            try: config["active_tab_text"] = self.notebook.tab(self.notebook.select(), "text")
            except tk.TclError: pass
        save_config(config) # Use your original save_config
        log_debug("INFO: Configuration saved. Exiting application.")
        self.master.destroy()

    def create_main_layout_and_widgets(self): # Your original
        main_frame = ttk.Frame(self.master, padding="10", style='TFrame')
        main_frame.pack(expand=True, fill=tk.BOTH)
        self.notebook = ttk.Notebook(main_frame, style='TNotebook')
        self.export_tab = ttk.Frame(self.notebook, style='TFrame', padding=10)
        self.notebook.add(self.export_tab, text='Export Chats')
        self.create_export_tab_content(self.export_tab)
        self.search_tab = ttk.Frame(self.notebook, style='TFrame', padding=10)
        self.notebook.add(self.search_tab, text='Search Indexed Files')
        self.create_search_tab_content(self.search_tab)
        self.debug_log_tab = ttk.Frame(self.notebook, style='TFrame', padding=10)
        self.notebook.add(self.debug_log_tab, text='Debug Log')
        self.create_debug_log_tab_content(self.debug_log_tab)
        self.settings_gui_tab = ttk.Frame(self.notebook, style='TFrame', padding=10)
        self.notebook.add(self.settings_gui_tab, text="App Settings")
        self.create_app_settings_tab_content(self.settings_gui_tab)
        self.notebook.pack(expand=True, fill=tk.BOTH, padx=0, pady=0)
        active_tab_text_cfg = config.get("active_tab_text", "Export Chats")
        for i in range(self.notebook.index("end")):
            if self.notebook.tab(i, "text") == active_tab_text_cfg: self.notebook.select(i); break
        common_settings_lf = ttk.LabelFrame(main_frame, text="Common Application Actions", padding="10", style='TLabelframe')
        common_settings_lf.pack(pady=(10,0), fill=tk.X, side=tk.BOTTOM)
        ttk.Button(common_settings_lf, text="Set Default Text Editor", command=self.set_editor_action).pack(side=tk.LEFT, padx=5, pady=3, expand=True, fill=tk.X)
        ttk.Button(common_settings_lf, text="Set Tag Definition File", command=self.set_tag_file_action).pack(side=tk.LEFT, padx=5, pady=3, expand=True, fill=tk.X)
        ttk.Button(common_settings_lf, text="Wipe Settings & Indexes, Close App", command=self.clear_config_action).pack(side=tk.LEFT, padx=5, pady=3, expand=True, fill=tk.X)
        self.status_bar_text_var = tk.StringVar(value="Ready.")
        self.status_bar = ttk.Label(main_frame, textvariable=self.status_bar_text_var, relief=tk.SUNKEN, anchor=tk.W, padding=(5,3))
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X, pady=(5,0))

    def create_export_tab_content(self, parent_tab): # Your original
        global export_log_text_widget
        options_frame = ttk.Frame(parent_tab, style='TFrame'); options_frame.pack(pady=5, fill=tk.X)
        ttk.Label(options_frame, text="Theme:").grid(row=0, column=0, padx=5, pady=2, sticky=tk.W)
        self.theme_cb = ttk.Combobox(options_frame, textvariable=self.theme_cb_var, values=list(theme_styles.keys()), state="readonly", width=25)
        self.theme_cb.grid(row=0, column=1, padx=5, pady=2, sticky=tk.EW)
        self.theme_cb.bind("<<ComboboxSelected>>", self.on_theme_change_action)
        export_format_options = ["Text", "Markdown", "HTML", "MHTML", "RTF", "AmandaMap Markdown"]
        ttk.Label(options_frame, text="Export Format:").grid(row=1, column=0, padx=5, pady=2, sticky=tk.W)
        self.fmt_cb = ttk.Combobox(options_frame, textvariable=self.export_format_var, values=export_format_options, state="readonly", width=25)
        self.fmt_cb.grid(row=1, column=1, padx=5, pady=2, sticky=tk.EW)
        options_frame.columnconfigure(1, weight=1)
        export_options_lf = ttk.LabelFrame(parent_tab, text="Export Options", padding="10", style='TLabelframe'); export_options_lf.pack(pady=5, fill=tk.X)
        ttk.Checkbutton(export_options_lf, text="Embed Images Inline (MD/HTML/MHTML/RTF)", variable=self.img_inline_var).pack(anchor=tk.W)
        ttk.Checkbutton(export_options_lf, text="Save Images to Folder (MD/HTML, if not embedding)", variable=self.img_folder_var).pack(anchor=tk.W)
        pillow_cb_state = tk.NORMAL if PIL_AVAILABLE else tk.DISABLED
        pillow_cb_text = "Use Pillow for unknown image types (if installed)" if PIL_AVAILABLE else "Use Pillow (Pillow/PIL not installed)"
        self.pillow_export_cb = ttk.Checkbutton(export_options_lf, text=pillow_cb_text, variable=self.use_pillow_var, state=pillow_cb_state)
        self.pillow_export_cb.pack(anchor=tk.W)
        ttk.Checkbutton(export_options_lf, text="Combine to one output file", variable=self.combine_var).pack(anchor=tk.W)
        ttk.Checkbutton(export_options_lf, text="Include Timestamps in Exported File Content", variable=self.include_timestamps_export_var).pack(anchor=tk.W)
        ttk.Checkbutton(export_options_lf, text="Skip System/Tool Messages (unless image)", variable=self.skip_system_tool_var).pack(anchor=tk.W)
        self.amandamap_mode_cb = ttk.Checkbutton(export_options_lf, text="AmandaMap Mode", variable=self.amandamap_mode_var)
        self.amandamap_mode_cb.pack(anchor=tk.W)
        self.update_amandamap_mode_state()
        img_folder_name_frame = ttk.Frame(export_options_lf, style='TFrame'); img_folder_name_frame.pack(fill=tk.X, pady=2)
        ttk.Label(img_folder_name_frame, text="Image Subfolder Name:").pack(side=tk.LEFT, padx=(0,5))
        ttk.Entry(img_folder_name_frame, textvariable=self.image_folder_name_var, width=20).pack(side=tk.LEFT)
        actions_lf = ttk.LabelFrame(parent_tab, text="Export Actions", padding="10", style='TLabelframe'); actions_lf.pack(pady=5, fill=tk.X)
        export_log_lf = ttk.LabelFrame(parent_tab, text="Export Log", padding="5", style='TLabelframe'); export_log_lf.pack(pady=5, fill=tk.BOTH, expand=True)
        export_log_text_widget = scrolledtext.ScrolledText(export_log_lf, height=6, relief=tk.SUNKEN, borderwidth=1, wrap=tk.WORD)
        export_log_text_widget.pack(expand=True, fill=tk.BOTH)
        export_log_text_widget.config(bg=self.current_style_colors["list_bg"], fg=self.current_style_colors["list_fg"], font=tkFont.nametofont("TkFixedFont"))
        ttk.Button(actions_lf, text="Convert Selected File(s)", command=self.export_files_action).pack(fill=tk.X, pady=3)
        ttk.Button(actions_lf, text="Convert Folder of JSONs", command=self.export_folder_action).pack(fill=tk.X, pady=3)
        self.fmt_cb.bind("<<ComboboxSelected>>", self.on_export_options_changed_action)
        self.img_inline_var.trace_add("write", lambda *a: self.on_export_options_changed_action())
        self.img_folder_var.trace_add("write", lambda *a: self.on_export_options_changed_action())
        self.combine_var.trace_add("write", lambda *a: self.on_export_options_changed_action())
        self.include_timestamps_export_var.trace_add("write", lambda *a: self.on_export_options_changed_action())
        self.skip_system_tool_var.trace_add("write", lambda *a: self.on_export_options_changed_action())
        self.use_pillow_var.trace_add("write", lambda *a: self.on_export_options_changed_action())
        self.image_folder_name_var.trace_add("write", lambda *a: self.on_export_options_changed_action())
        self.amandamap_mode_var.trace_add("write", lambda *a: self.on_export_options_changed_action())


    def create_search_tab_content(self, parent_tab): # Your original, MODIFIED for timestamps
        index_type_frame = ttk.Frame(parent_tab, style='TFrame'); index_type_frame.pack(fill=tk.X, pady=5)
        ttk.Label(index_type_frame, text="Search In:").pack(side=tk.LEFT, padx=(0,5))
        self.index_type_cb = ttk.Combobox(index_type_frame, values=self.index_type_options, textvariable=self.selected_index_type_var, state="readonly", width=30)
        self.index_type_cb.pack(side=tk.LEFT, padx=5)
        self.index_type_cb.bind("<<ComboboxSelected>>", self.on_index_type_changed)
        self.last_indexed_path_label = ttk.Label(index_type_frame, text="Last Indexed: None")
        self.last_indexed_path_label.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True, anchor="w")
        index_progress_frame = ttk.LabelFrame(parent_tab, text="Indexing Progress/Log", style='TLabelframe', padding=5); index_progress_frame.pack(fill=tk.X, pady=5)
        self.index_progress_text = scrolledtext.ScrolledText(index_progress_frame, height=8, relief=tk.SUNKEN, borderwidth=1, wrap=tk.WORD)
        self.index_progress_text.pack(expand=True, fill=tk.BOTH)
        self.index_progress_text.config(bg=self.current_style_colors["list_bg"], fg=self.current_style_colors["list_fg"], font=tkFont.nametofont("TkFixedFont"))
        build_buttons_frame = ttk.Frame(parent_tab, style='TFrame'); build_buttons_frame.pack(fill=tk.X, pady=5)
        self.build_json_index_button = ttk.Button(build_buttons_frame, text="Build Index from Original JSONs", command=lambda: self.run_build_index_threaded_generic_action(True))
        self.build_json_index_button.pack(side=tk.LEFT, padx=(0,5), expand=True, fill=tk.X)
        self.build_converted_index_button = ttk.Button(build_buttons_frame, text="Build Index from Converted Files", command=lambda: self.run_build_index_threaded_generic_action(False))
        self.build_converted_index_button.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)

        tagmap_frame = ttk.Frame(parent_tab, style='TFrame'); tagmap_frame.pack(fill=tk.X, pady=5)
        ttk.Label(tagmap_frame, text="TagMap File:").pack(side=tk.LEFT, padx=(0,5))
        self.tagmap_entry = ttk.Entry(tagmap_frame, textvariable=self.tagmap_file_var, width=40)
        self.tagmap_entry.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        ttk.Button(tagmap_frame, text="Browse", command=self.select_tagmap_file_action).pack(side=tk.LEFT, padx=5)

        search_input_frame = ttk.Frame(parent_tab, style='TFrame', padding=5); search_input_frame.pack(fill=tk.X, pady=5)
        ttk.Label(search_input_frame, text="Search Phrase:").pack(side=tk.LEFT, padx=(0,5))
        self.search_entry = ttk.Entry(search_input_frame, textvariable=self.search_term_var, width=40)
        self.search_entry.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        self.search_entry.bind("<Return>", lambda e: self.run_indexed_search_action())
        search_files_button = ttk.Button(search_input_frame, text="Search", command=self.run_indexed_search_action)
        search_files_button.pack(side=tk.LEFT, padx=5)
        search_results_lf = ttk.LabelFrame(parent_tab, text="Search Results / Indexed Files", padding="5", style='TLabelframe'); search_results_lf.pack(expand=True, fill=tk.BOTH, pady=5)

        # --- MODIFIED: GUI - Treeview columns for timestamps ---
        tree_columns = ("display_filename", "started_at", "ended_at", "category", "full_path")
        self.search_results_tree = ttk.Treeview(search_results_lf, columns=tree_columns, show="headings", style='Treeview', selectmode='extended')
        self.search_results_tree.heading("display_filename", text="File Name", command=lambda: self.sort_treeview_column_action(self.search_results_tree, "display_filename", False))
        self.search_results_tree.heading("started_at", text="Chat Started", command=lambda: self.sort_treeview_column_action(self.search_results_tree, "started_at", False))
        self.search_results_tree.heading("ended_at", text="Chat Ended", command=lambda: self.sort_treeview_column_action(self.search_results_tree, "ended_at", False))
        self.search_results_tree.heading("category", text="Category", command=lambda: self.sort_treeview_column_action(self.search_results_tree, "category", False))
        self.search_results_tree.heading("full_path", text="Full Path", command=lambda: self.sort_treeview_column_action(self.search_results_tree, "full_path", False))
        self.search_results_tree.column("display_filename", width=250, stretch=tk.YES, anchor=tk.W)
        self.search_results_tree.column("started_at", width=150, stretch=tk.NO, anchor="center")
        self.search_results_tree.column("ended_at", width=150, stretch=tk.NO, anchor="center")
        self.search_results_tree.column("category", width=120, stretch=tk.NO, anchor="center")
        self.search_results_tree.column("full_path", width=300, stretch=tk.YES, anchor=tk.W)
        tree_yscroll = ttk.Scrollbar(search_results_lf, orient=tk.VERTICAL, command=self.search_results_tree.yview, style='TScrollbar')
        tree_xscroll = ttk.Scrollbar(search_results_lf, orient=tk.HORIZONTAL, command=self.search_results_tree.xview, style='TScrollbar')
        self.search_results_tree.configure(yscrollcommand=tree_yscroll.set, xscrollcommand=tree_xscroll.set)
        self.search_results_tree.grid(row=0, column=0, sticky=tk.NSEW); tree_yscroll.grid(row=0, column=1, sticky=tk.NS); tree_xscroll.grid(row=1, column=0, sticky=tk.EW)
        search_results_lf.rowconfigure(0, weight=1); search_results_lf.columnconfigure(0, weight=1)
        self.search_results_tree.bind("<Double-1>", self.on_treeview_double_click_action)
        self.search_results_tree.bind("<ButtonRelease-1>", self.on_treeview_single_click_update_status_action)
        convert_selected_button = ttk.Button(search_results_lf, text="Convert Selected JSON(s) from Results", command=self.convert_selected_from_search_results_action)
        convert_selected_button.grid(row=2, column=0, columnspan=2, pady=(5,0), sticky=tk.EW)

    def create_debug_log_tab_content(self, parent_tab): # Your original
        global debug_log_text_widget
        debug_log_frame = ttk.Frame(parent_tab, style='TFrame'); debug_log_frame.pack(expand=True, fill=tk.BOTH, pady=0)
        debug_log_text_widget = scrolledtext.ScrolledText(debug_log_frame, height=15, relief=tk.SUNKEN, borderwidth=1, wrap=tk.WORD)
        debug_log_text_widget.pack(expand=True, fill=tk.BOTH, pady=(0,5))
        debug_log_text_widget.config(bg=self.current_style_colors["list_bg"], fg=self.current_style_colors["list_fg"], font=tkFont.nametofont("TkFixedFont"))
        debug_log_buttons_frame = ttk.Frame(parent_tab, style='TFrame'); debug_log_buttons_frame.pack(fill=tk.X, pady=5)
        ttk.Button(debug_log_buttons_frame, text="Clear Debug Log", command=self.clear_debug_log_action).pack(side=tk.LEFT, padx=(0,5), expand=True, fill=tk.X)
        ttk.Button(debug_log_buttons_frame, text="Save Debug Log to File", command=self.save_debug_log_action).pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)

    def create_app_settings_tab_content(self, parent_tab): # --- NEW / MERGED --- For search settings etc.
        global config
        search_settings_lf = ttk.LabelFrame(parent_tab, text="Search Configuration", padding="10", style='TLabelframe')
        search_settings_lf.pack(fill=tk.X, padx=5, pady=5)
        ttk.Checkbutton(search_settings_lf, text="Case Sensitive Search", variable=self.case_sensitive_search_var, command=self.on_search_settings_changed_action).pack(anchor="w", padx=5, pady=2)
        search_logic_frame = ttk.Frame(search_settings_lf, style='TFrame')
        search_logic_frame.pack(fill=tk.X, pady=2)
        ttk.Label(search_logic_frame, text="Search Logic (multiple terms):").pack(side=tk.LEFT, padx=5)
        self.search_logic_combo = ttk.Combobox(search_logic_frame, textvariable=self.search_logic_var, values=["AND", "OR"], state="readonly", width=10)
        self.search_logic_combo.pack(side=tk.LEFT, padx=5)
        self.search_logic_combo.bind("<<ComboboxSelected>>", self.on_search_settings_changed_action)
        ttk.Label(parent_tab, text="Other application settings (like default editor) are at the bottom of the window.").pack(pady=10)

        perf_frame = ttk.LabelFrame(parent_tab, text="Indexing Performance", padding="10", style='TLabelframe')
        perf_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(perf_frame, text="Tokenizer Threads:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        tk.Spinbox(perf_frame, from_=1, to=os.cpu_count() or 1, textvariable=self.num_tokenizers_var, width=5, command=self.on_performance_settings_changed_action).grid(row=0, column=1, padx=5, pady=2)
        ttk.Label(perf_frame, text="Indexer Threads:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        tk.Spinbox(perf_frame, from_=1, to=os.cpu_count() or 1, textvariable=self.num_indexers_var, width=5, command=self.on_performance_settings_changed_action).grid(row=1, column=1, padx=5, pady=2)
        ttk.Label(perf_frame, text="CPU Usage %:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        tk.Spinbox(perf_frame, from_=10, to=100, increment=10, textvariable=self.cpu_usage_percent_var, width=5, command=self.on_performance_settings_changed_action).grid(row=2, column=1, padx=5, pady=2)
        self.num_tokenizers_var.trace_add("write", lambda *a: self.on_performance_settings_changed_action())
        self.num_indexers_var.trace_add("write", lambda *a: self.on_performance_settings_changed_action())
        self.cpu_usage_percent_var.trace_add("write", lambda *a: self.on_performance_settings_changed_action())

        tagmap_frame = ttk.LabelFrame(parent_tab, text="TagMap", padding="10", style='TLabelframe')
        tagmap_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Checkbutton(tagmap_frame, text="Include TagMap tags when indexing", variable=self.use_tagmap_tagging_var).pack(anchor="w")
        self.use_tagmap_tagging_var.trace_add("write", lambda *a: self.on_tagmap_settings_changed_action())


    def on_search_settings_changed_action(self, event=None): # --- NEW ---
        global config
        config["search_term_case_sensitive"] = self.case_sensitive_search_var.get()
        config["search_logic"] = self.search_logic_var.get()
        self.update_status_bar("Search settings updated. Will be saved on app exit.")
        log_debug("DEBUG: Search settings changed in GUI.")

    def on_performance_settings_changed_action(self, event=None):
        global config
        config["num_tokenizers"] = self.num_tokenizers_var.get()
        config["num_indexers"] = self.num_indexers_var.get()
        config["cpu_usage_percent"] = self.cpu_usage_percent_var.get()
        self.update_status_bar("Performance settings updated. Will be saved on exit.")
        log_debug("DEBUG: Performance settings changed in GUI.")

    def on_tagmap_settings_changed_action(self, event=None):
        global config
        config["use_tagmap_tagging"] = self.use_tagmap_tagging_var.get()
        self.update_status_bar("TagMap option updated. Will be saved on exit.")
        log_debug("DEBUG: TagMap tagging option changed in GUI.")

    def on_export_options_changed_action(self, event=None): # Your original update_and_save_config_export_tab
        global config
        config["theme"] = self.theme_cb_var.get()
        config["export_format"] = self.export_format_var.get()
        config["export_images_inline"] = self.img_inline_var.get()
        config["export_images_folder"] = self.img_folder_var.get()
        config["image_folder_name"] = self.image_folder_name_var.get()
        config["combine_output_files"] = self.combine_var.get()
        config["include_timestamps_in_export"] = self.include_timestamps_export_var.get()
        config["skip_system_tool_messages"] = self.skip_system_tool_var.get()
        config["use_pillow_for_unknown_images"] = self.use_pillow_var.get() if PIL_AVAILABLE else False
        config["amandamap_mode"] = self.amandamap_mode_var.get()
        self.update_amandamap_mode_state()
        self.update_status_bar("Export options noted. Will be saved on exit.")
        log_debug("DEBUG: Export options updated in memory from GUI interaction.")

    def export_files_action(self): # Your original
        files = filedialog.askopenfilenames(title="Select JSON File(s) to Convert", filetypes=[("JSON files", "*.json"), ("All files", "*.*")], parent=self.master)
        if not files: return
        out_dir = filedialog.askdirectory(title="Select Output Folder for Converted Files", parent=self.master)
        if not out_dir: return
        if export_log_text_widget: export_log_text_widget.delete('1.0', tk.END)
        current_cfg_for_export = config.copy()
        current_cfg_for_export.update({
            "export_format": self.export_format_var.get(), "export_images_inline": self.img_inline_var.get(),
            "export_images_folder": self.img_folder_var.get(), "image_folder_name": self.image_folder_name_var.get(),
            "combine_output_files": self.combine_var.get(), "include_timestamps_in_export": self.include_timestamps_export_var.get(),
            "skip_system_tool_messages": self.skip_system_tool_var.get(), "use_pillow_for_unknown_images": self.use_pillow_var.get() if PIL_AVAILABLE else False,
            "amandamap_mode": self.amandamap_mode_var.get()
        })
        self.update_status_bar(f"Starting export of {len(files)} file(s)...")
        threading.Thread(target=save_multiple_files, args=(files, current_cfg_for_export, out_dir, current_cfg_for_export.get("combine_output_files",False), export_log_text_widget), daemon=True).start()

    def export_folder_action(self): # Your original
        folder = filedialog.askdirectory(title="Select Folder of JSONs to Convert", parent=self.master)
        if not folder: return
        out_dir = filedialog.askdirectory(title="Select Output Folder for Converted Files", parent=self.master)
        if not out_dir: return
        files = [str(p) for p in Path(folder).rglob("*.json")]
        if not files: messagebox.showinfo("No Files", "No JSON files found in the selected folder or subfolders.", parent=self.master); return
        if export_log_text_widget: export_log_text_widget.delete('1.0', tk.END)
        current_cfg_for_export = config.copy()
        current_cfg_for_export.update({
            "export_format": self.export_format_var.get(), "export_images_inline": self.img_inline_var.get(),
            "export_images_folder": self.img_folder_var.get(), "image_folder_name": self.image_folder_name_var.get(),
            "combine_output_files": self.combine_var.get(), "include_timestamps_in_export": self.include_timestamps_export_var.get(),
            "skip_system_tool_messages": self.skip_system_tool_var.get(), "use_pillow_for_unknown_images": self.use_pillow_var.get() if PIL_AVAILABLE else False,
            "amandamap_mode": self.amandamap_mode_var.get()
        })
        self.update_status_bar(f"Starting export of folder: {Path(folder).name}...")
        threading.Thread(target=save_multiple_files, args=(files, current_cfg_for_export, out_dir, current_cfg_for_export.get("combine_output_files",False), export_log_text_widget), daemon=True).start()

    def run_build_index_threaded_generic_action(self, is_json_index): # Your original, adapted
        if self.active_indexing_thread and self.active_indexing_thread.is_alive():
            messagebox.showwarning("Busy", "An indexing operation is already in progress.", parent=self.master); return
        target_button = self.build_json_index_button if is_json_index else self.build_converted_index_button
        other_button = self.build_converted_index_button if is_json_index else self.build_json_index_button
        original_text = target_button.cget("text")
        prompt_title = "Select Folder of Original JSONs to Index" if is_json_index else "Select Folder of Converted (TXT/MD/HTML) Files to Index"
        initial_dir_key = "last_indexed_original_json_folder_path" if is_json_index else "last_indexed_converted_files_folder_path"
        folder_to_index_str = filedialog.askdirectory(title=prompt_title, initialdir=config.get(initial_dir_key, str(Path.home())), parent=self.master)
        if not folder_to_index_str: return
        folder_to_index = Path(folder_to_index_str)
        target_button.config(state=tk.DISABLED, text="Indexing...")
        other_button.config(state=tk.DISABLED)
        if hasattr(self, 'index_progress_text'): self.index_progress_text.delete('1.0', tk.END)

        def _build_task():
            global loaded_search_index, config
            try:
                file_patterns = ["*.json"] if is_json_index else ["*.txt", "*.md", "*.html", "*.rtf"]
                index_file_path_str = ORIGINAL_JSON_INDEX_FILE if is_json_index else CONVERTED_FILES_INDEX_FILE
                current_selected_type_name_gui = self.selected_index_type_var.get()
                expected_type_name_for_this_build = self.index_type_options[0] if is_json_index else self.index_type_options[1]
                existing_idx_to_pass = None
                if current_selected_type_name_gui == expected_type_name_for_this_build and loaded_search_index:
                    if not is_json_index:
                         existing_idx_to_pass = loaded_search_index
                         log_debug(f"INFO: Passing existing '{current_selected_type_name_gui}' index to _build_generic_index.")

                tags_data = (
                    load_json_tagmap(folder_to_index)
                    if self.use_tagmap_tagging_var.get()
                    else None
                )
                tagmap_entries = None
                tagmap_path = self.tagmap_file_var.get().strip() if hasattr(self, 'tagmap_file_var') else ''
                if tagmap_path:
                    try:
                        tagmap_entries = load_tagmap(tagmap_path)
                        log_debug(
                            f"INFO: Loaded TagMap with {len(tagmap_entries)} entries"
                        )
                    except Exception as e_tm:
                        log_debug(f"ERROR: Failed to load TagMap: {e_tm}")
                new_index = _build_generic_index(
                    folder_to_index,
                    config,
                    file_patterns,
                    index_file_path_str,
                    self.index_progress_text,
                    is_json_index,
                    existing_idx_to_pass,
                    tags_data,
                    tagmap_entries,
                )

                if self.selected_index_type_var.get() == expected_type_name_for_this_build:
                    loaded_search_index = new_index
                    if hasattr(self.master, 'after'):
                        self.master.after(0, self.populate_search_results_tree_with_all_files)
                if hasattr(self.master, 'after'):
                    self.master.after(0, self.update_last_indexed_label) 
                    if self.index_progress_text.winfo_exists():
                         self.master.after(0, lambda: messagebox.showinfo("Index Complete", f"{expected_type_name_for_this_build} index built!", parent=self.master))
            except Exception as e_build_task:
                err_msg = str(e_build_task)
                log_debug(f"ERROR: Exception during _build_task: {err_msg}")
                if hasattr(self.master, 'after') and self.index_progress_text.winfo_exists():
                    self.master.after(0, lambda msg=err_msg: messagebox.showerror("Index Error", f"Failed to build index: {msg}", parent=self.master))
                    self.master.after(0, lambda msg=err_msg: self.index_progress_text.insert(tk.END, f"Error: {msg}\n"))
            finally:
                if hasattr(self.master, 'after'):
                    self.master.after(0, lambda: target_button.config(state=tk.NORMAL, text=original_text))
                    self.master.after(0, lambda: other_button.config(state=tk.NORMAL))
                self.active_indexing_thread = None
                self.update_status_bar("Indexing finished or failed.")
        self.active_indexing_thread = threading.Thread(target=_build_task, daemon=True)
        self.active_indexing_thread.start()
        self.update_status_bar(f"Indexing {Path(folder_to_index).name} in background...")

    # --- MODIFIED: load_active_index with more robust validation ---
    def load_active_index(self):
        global loaded_search_index, config
        current_selected_type = self.selected_index_type_var.get()
        index_file_to_load = ORIGINAL_JSON_INDEX_FILE if current_selected_type == "Original JSONs (Indexed)" else CONVERTED_FILES_INDEX_FILE
        loaded_search_index = None
        progress_widget = self.index_progress_text if hasattr(self, 'index_progress_text') else None
        def _log_progress_local(msg):
            if progress_widget and progress_widget.winfo_exists():
                progress_widget.insert(tk.END, msg + "\n"); progress_widget.see(tk.END);
            else: log_debug(f"INDEX_LOAD_LOG: {msg}")
        if os.path.exists(index_file_to_load):
            try:
                _log_progress_local(f"Loading {current_selected_type} index ({Path(index_file_to_load).name})...")
                with open(index_file_to_load, 'r', encoding='utf-8') as f:
                    loaded_data_from_file = json.load(f)
                # --- INTEGRATED: More robust validation of loaded index structure ---
                if isinstance(loaded_data_from_file, dict) and \
                   isinstance(loaded_data_from_file.get("metadata"), dict) and \
                   isinstance(loaded_data_from_file.get("index"), dict) and \
                   isinstance(loaded_data_from_file["index"].get("tokens"), dict) and \
                   isinstance(loaded_data_from_file["index"].get("files"), dict) and \
                   isinstance(loaded_data_from_file["index"].get("file_details"), dict): # Check for file_details
                    loaded_search_index = loaded_data_from_file
                    _log_progress_local("Index loaded and structure validated successfully.")
                else:
                    _log_progress_local("ERROR: Loaded index file has an invalid or incomplete structure.")
                    if self.master.winfo_exists(): # Check root window before showing messagebox
                        messagebox.showerror("Index Structure Error",
                                             f"The index file '{Path(index_file_to_load).name}' has an invalid structure or is missing essential parts (e.g., metadata, index map, tokens, files, file_details).\n\nPlease try rebuilding the index for '{current_selected_type}'.",
                                             parent=self.master)
                    loaded_search_index = None # Invalidate it
            except json.JSONDecodeError as e_json:
                _log_progress_local(f"ERROR: Could not decode JSON from {index_file_to_load}: {e_json}")
                if self.master.winfo_exists():
                    messagebox.showerror("Index Load Error", f"Failed to load index: {Path(index_file_to_load).name}\nFile might be corrupted, empty, or not valid JSON.\nDetails: {e_json}", parent=self.master)
                loaded_search_index = None
            except Exception as e_load_other:
                _log_progress_local(f"ERROR: Unexpected error loading {index_file_to_load}: {e_load_other}")
                if self.master.winfo_exists():
                    messagebox.showerror("Index Load Error", f"An unexpected error occurred while loading {Path(index_file_to_load).name}:\n{e_load_other}", parent=self.master)
                loaded_search_index = None
        else:
            _log_progress_local(f"INFO: No {current_selected_type} index found ({Path(index_file_to_load).name}). Please build one.")
        self.populate_search_results_tree_with_all_files()
        self.update_last_indexed_label() 

    # --- NEW/MODIFIED: Function to populate treeview with all files from the loaded index ---
    def populate_search_results_tree_with_all_files(self):
        global loaded_search_index
        tree = self.search_results_tree
        for i in tree.get_children(): tree.delete(i)
        if not loaded_search_index or not isinstance(loaded_search_index.get("index"), dict):
            self.update_status_bar("Index not loaded or invalid. Cannot display files."); return
        files_map = loaded_search_index["index"].get("files", {})
        file_details_map = loaded_search_index["index"].get("file_details", {})
        if not files_map :
            self.update_status_bar("Index loaded, but no file entries found to display."); return
        base_folder_str = loaded_search_index.get("metadata", {}).get("indexed_folder_path", "")
        base_folder = Path(base_folder_str if base_folder_str else ".")
        is_converted_files_type = self.selected_index_type_var.get() == "Converted Files (Indexed)"
        displayed_count = 0
        # Iterate through files_map to ensure all files with paths are considered
        for file_id, relative_path_str in files_map.items():
            details = file_details_map.get(file_id, {}) # Get details; defaults to {} if no details for this file_id
            display_name = details.get("filename", Path(relative_path_str).name)
            full_path_str = str(base_folder / relative_path_str)
            started_at_val, ended_at_val = "", ""
            if is_converted_files_type:
                started_at_val = details.get("chat_started_at", "")
                ended_at_val = details.get("chat_ended_at", "")
            cat_set = set()
            for v in details.get("tagmap", {}).values():
                if v.get("category"):
                    cat_set.add(v["category"])
            cat_str = ", ".join(sorted(cat_set))
            tree_values = (display_name, started_at_val, ended_at_val, cat_str, full_path_str)
            try:
                tree.insert("", "end", iid=file_id, values=tree_values, tags=('file_row',))
                displayed_count +=1
            except tk.TclError:
                try: tree.insert("", "end", iid=f"{file_id}_pop_{displayed_count}", values=tree_values, tags=('file_row',)); displayed_count +=1
                except Exception as e_ins_tree: log_debug(f"ERROR: Failed to insert item {file_id} into tree: {e_ins_tree}")
        self.update_status_bar(f"Displaying {displayed_count} indexed files. Search to filter.")
        if displayed_count == 0 and (files_map or file_details_map) :
             self.update_status_bar("Index loaded, but could not display file entries (check consistency).")

    def run_indexed_search_action(self, event=None): # Your original, MODIFIED for new tree structure
        global loaded_search_index
        if not loaded_search_index:
            self.load_active_index()
            if not loaded_search_index:
                if self.master.winfo_exists(): messagebox.showwarning("No Index Loaded", f"{self.selected_index_type_var.get()} index not loaded.", parent=self.master)
                return
        keyword_to_search = self.search_entry.get().strip()
        if not keyword_to_search: self.populate_search_results_tree_with_all_files(); return
        for i in self.search_results_tree.get_children(): self.search_results_tree.delete(i)
        case_sensitive = config.get("search_term_case_sensitive", False)
        search_logic = config.get("search_logic", "AND")
        results_with_details, error_msg = search_with_persistent_index(keyword_to_search, loaded_search_index, case_sensitive, search_logic)
        if error_msg: self.search_results_tree.insert("", tk.END, values=(error_msg, "", "", "", ""), tags=('error',))
        elif results_with_details:
            for res_tuple in results_with_details:
                display_name, started_at, ended_at, full_path_obj, file_id_str, details = res_tuple
                cat_set = set()
                for v in details.get("tagmap", {}).values():
                    if v.get("category"):
                        cat_set.add(v["category"])
                cat_str = ", ".join(sorted(cat_set))
                tree_values = (display_name, started_at, ended_at, cat_str, str(full_path_obj))
                try: self.search_results_tree.insert("", "end", iid=file_id_str, values=tree_values, tags=('file_row',))
                except tk.TclError: self.search_results_tree.insert("", "end", iid=f"{file_id_str}_search", values=tree_values, tags=('file_row',))
        else: self.search_results_tree.insert("", tk.END, values=("No matches found.", "", "", "", ""), tags=('no_match',))
        self.search_results_tree.tag_configure('error', foreground='red'); self.search_results_tree.tag_configure('no_match', foreground='grey')
        self.update_status_bar(f"Search for '{keyword_to_search}' complete. {len(results_with_details) if results_with_details else 0} results.")

    def convert_selected_from_search_results_action(self): # Your original
        selected_ids = self.search_results_tree.selection()
        if not selected_ids: messagebox.showinfo("No Selection", "Select files to convert.", parent=self.master); return
        if self.selected_index_type_var.get() != "Original JSONs (Indexed)":
            messagebox.showwarning("Invalid Source", "Convert works on original JSONs.", parent=self.master); return
        files_to_convert_paths = []
        for item_iid in selected_ids:
            item_values = self.search_results_tree.item(item_iid, "values")
            if item_values and len(item_values) == 4:
                full_path_str = item_values[3]
                if Path(full_path_str).suffix.lower() == '.json': files_to_convert_paths.append(full_path_str)
                else: log_debug(f"Skipping non-JSON: {full_path_str}")
            else: log_debug(f"Bad path for item: {item_iid}, values: {item_values}")
        if not files_to_convert_paths: messagebox.showinfo("No JSONs", "No valid JSONs selected.", parent=self.master); return
        out_dir = filedialog.askdirectory(title="Select Output Folder", parent=self.master)
        if not out_dir: return
        if export_log_text_widget: export_log_text_widget.delete('1.0', tk.END)
        current_export_cfg = config.copy()
        current_export_cfg.update({
            "export_format": self.export_format_var.get(), "export_images_inline": self.img_inline_var.get(),
            "export_images_folder": self.img_folder_var.get(), "image_folder_name": self.image_folder_name_var.get(),
            "combine_output_files": self.combine_var.get(), "include_timestamps_in_export": self.include_timestamps_export_var.get(),
            "skip_system_tool_messages": self.skip_system_tool_var.get(), "use_pillow_for_unknown_images": self.use_pillow_var.get() if PIL_AVAILABLE else False
        })
        self.update_status_bar(f"Converting {len(files_to_convert_paths)} selected JSON(s)...")
        threading.Thread(target=save_multiple_files, args=(files_to_convert_paths, current_export_cfg, out_dir, current_export_cfg.get("combine_output_files", False), export_log_text_widget), daemon=True).start()

    def clear_debug_log_action(self): # Your original
        if debug_log_text_widget: debug_log_text_widget.delete('1.0', tk.END)

    def save_debug_log_action(self): # Your original
        if debug_log_text_widget:
            log_content = debug_log_text_widget.get('1.0', tk.END).strip()
            if not log_content: messagebox.showinfo("Empty Log", "Debug log empty.", parent=self.master); return
            save_path = filedialog.asksaveasfilename(title="Save Debug Log", defaultextension=".txt", filetypes=[("Text", "*.txt"), ("Log", "*.log"), ("All", "*.*")], parent=self.master)
            if save_path:
                try:
                    with open(save_path, 'w', encoding='utf-8') as f: f.write(log_content)
                    messagebox.showinfo("Log Saved", f"Debug log saved to:\n{save_path}", parent=self.master)
                except Exception as e_save_log: messagebox.showerror("Save Error", f"Could not save log:\n{e_save_log}", parent=self.master)

    def set_editor_action(self): # Your original
        global config
        path = filedialog.askopenfilename(title="Choose Default Text Editor", parent=self.master)
        if path:
            config["default_editor"] = path
            messagebox.showinfo("Editor Set", f"Default editor set to:\n{path}", parent=self.master)
            log_debug(f"INFO: Default editor set to {path}")

    def set_tag_file_action(self):
        global config
        path = filedialog.askopenfilename(title="Choose Tag Definition File", parent=self.master)
        if path:
            config["tag_definition_file"] = path
            self.tag_definition_var.set(path)
            messagebox.showinfo("Tag File Set", f"Tag definitions loaded from:\n{path}", parent=self.master)
            log_debug(f"INFO: Tag definition file set to {path}")

    def select_tagmap_file_action(self):
        global config
        path = filedialog.askopenfilename(title="Select TagMap File", parent=self.master)
        if path:
            self.tagmap_file_var.set(path)
            config["tagmap_file_path"] = path
            self.update_status_bar(f"TagMap selected: {Path(path).name}")
            log_debug(f"INFO: TagMap file set to {path}")

    def clear_config_action(self): # Your original
        if messagebox.askyesno("Confirm Reset", "WIPE settings & ALL indexes, then CLOSE app?", icon='warning', parent=self.master):
            wipe_config()
            messagebox.showinfo("Reset Complete", "Please restart app.", parent=self.master)
            self.master.destroy()

    def on_theme_change_action(self, event=None): # Your original
        global config
        new_theme_name = self.theme_cb_var.get()
        if new_theme_name != config.get("theme"):
            config["theme"] = new_theme_name
            self.current_style_colors = theme_styles[new_theme_name]
            apply_styles(self.master, self.current_style_colors)
            if export_log_text_widget: export_log_text_widget.config(bg=self.current_style_colors["list_bg"], fg=self.current_style_colors["list_fg"])
            if hasattr(self, 'index_progress_text'): self.index_progress_text.config(bg=self.current_style_colors["list_bg"], fg=self.current_style_colors["list_fg"])
            if debug_log_text_widget: debug_log_text_widget.config(bg=self.current_style_colors["list_bg"], fg=self.current_style_colors["list_fg"])
            self.master.title(f"GPT Export & Index Tool V6.3 {self.current_style_colors['emoji']} (Accuracy Edition)") # Version updated
            log_debug(f"INFO: Theme changed to {new_theme_name}.")
            self.update_status_bar(f"Theme changed to {new_theme_name}.")
            if messagebox.askyesno("Theme Update", "Theme changed. Restart for full effect?", parent=self.master): self.master.destroy()

    def on_index_type_changed(self, event=None): # Your original
        global loaded_search_index, config
        log_debug(f"INFO: Index type selection changed to: {self.selected_index_type_var.get()}")
        loaded_search_index = None
        config["selected_index_type"] = self.selected_index_type_var.get()
        self.load_active_index()
        # update_last_indexed_label is called within load_active_index
        if loaded_search_index and loaded_search_index.get("index", {}).get("file_details"): 
             num_files = len(loaded_search_index['index']['file_details']) 
             if num_files == 0 and loaded_search_index['index'].get('files'): 
                num_files = len(loaded_search_index['index']['files'])
             self.update_status_bar(f"Loaded '{self.selected_index_type_var.get()}'. {num_files} files listed.")
        elif loaded_search_index:
             self.update_status_bar(f"Loaded '{self.selected_index_type_var.get()}'. Index empty or no file details.")
        else: self.update_status_bar(f"No index loaded for '{self.selected_index_type_var.get()}'.")

    def sort_treeview_column_action(self, tree, col, reverse): # Your original, adapted for dates
        if not tree.get_children(''): log_debug(f"DEBUG: Treeview empty, cannot sort '{col}'."); return
        l = []; date_format = "%Y-%m-%d %H:%M:%S"
        for k in tree.get_children(''):
            val = tree.set(k, col); l.append((val if val is not None else "", k))
        try:
            if col in ["started_at", "ended_at"]:
                l.sort(key=lambda t: (datetime.strptime(t[0], date_format) if t[0] else (datetime.max if reverse else datetime.min)), reverse=reverse)
            elif col == "display_filename": l.sort(key=lambda t: str(t[0]).lower(), reverse=reverse)
            else: # Other columns (attempt numeric, then string for full_path)
                try: l.sort(key=lambda t: (float(t[0]) if t[0] and t[0].replace('.','',1).isdigit() else str(t[0]).lower()), reverse=reverse)
                except ValueError: l.sort(key=lambda t: str(t[0]).lower(), reverse=reverse)
        except ValueError as e_sort_val: log_debug(f"WARNING: Sort ValueError '{col}': {e_sort_val}. String sort."); l.sort(key=lambda t: str(t[0]).lower(), reverse=reverse)
        except TypeError as e_sort_type: log_debug(f"WARNING: Sort TypeError '{col}': {e_sort_type}. String sort."); l.sort(key=lambda t: str(t[0]).lower(), reverse=reverse)
        for index, (val, k) in enumerate(l): tree.move(k, '', index)
        tree.heading(col, command=lambda: self.sort_treeview_column_action(tree, col, not reverse))
        self.update_status_bar(f"Sorted by '{tree.heading(col, 'text')}' {'descending' if reverse else 'ascending'}.")

    def on_treeview_double_click_action(self, event): # Your original, adapted
        treeview = event.widget; selected_item_id = treeview.focus()
        if not selected_item_id: return
        item_values = treeview.item(selected_item_id, "values")
        if not item_values or len(item_values) < 4: log_debug(f"Warning: Double-click item '{selected_item_id}' bad values: {item_values}"); return
        file_path_to_open_str = item_values[3] # Index 3 is 'full_path'
        if not file_path_to_open_str or file_path_to_open_str == "Error": messagebox.showwarning("Cannot Open", "No valid file path.", parent=self.master); return
        file_path_to_open = Path(file_path_to_open_str)
        if file_path_to_open.exists(): launch_editor(file_path_to_open, config) # Pass global config
        else: messagebox.showerror("File Not Found", f"File not found:\n{file_path_to_open}", parent=self.master); log_debug(f"ERROR: File not found on double-click: {file_path_to_open}")

    def on_treeview_single_click_update_status_action(self, event): # Your original
        treeview = event.widget; selected_items = treeview.selection()
        total_visible_items = len(treeview.get_children(''))
        if selected_items: self.update_status_bar(f"{len(selected_items)} of {total_visible_items} files selected.")
        else: self.update_status_bar(f"{total_visible_items} files listed.")

    def update_status_bar(self, message): # Your original
        if hasattr(self, 'status_bar_text_var') and self.status_bar_text_var.get() != message :
            self.status_bar_text_var.set(message)

    def update_amandamap_mode_state(self):
        if hasattr(self, 'amandamap_mode_cb'):
            if self.export_format_var.get() == "AmandaMap Markdown":
                self.amandamap_mode_cb.config(state=tk.NORMAL)
            else:
                self.amandamap_mode_cb.config(state=tk.DISABLED)

    # --- METHOD CORRECTED TO PREVENT CRASH ---
    def update_last_indexed_label(self):
        global config, loaded_search_index
        label_text = "Last Indexed: None"
        current_selected_type = ""

        # Safely get the current selected index type
        if hasattr(self, 'selected_index_type_var'): # Check if the StringVar attribute exists
            try:
                current_selected_type = self.selected_index_type_var.get()
            except tk.TclError: # Handles case where the underlying Tk variable might be destroyed
                log_debug("WARNING: tk.TclError getting selected_index_type_var in update_last_indexed_label. Falling back to config.")
                current_selected_type = config.get("selected_index_type",
                                                   self.index_type_options[1] if hasattr(self, 'index_type_options') else "Converted Files (Indexed)")
        else:
            log_debug("WARNING: selected_index_type_var attribute not found in update_last_indexed_label. Falling back to config.")
            current_selected_type = config.get("selected_index_type",
                                               self.index_type_options[1] if hasattr(self, 'index_type_options') else "Converted Files (Indexed)")

        key_to_check = ""
        descriptive_name = "" 

        if current_selected_type == "Original JSONs (Indexed)":
            key_to_check = "last_indexed_original_json_folder_path"
            descriptive_name = "Original JSONs"
        elif current_selected_type == "Converted Files (Indexed)":
            key_to_check = "last_indexed_converted_files_folder_path"
            descriptive_name = "Converted Files"

        path_from_config = config.get(key_to_check)

        if path_from_config:
            folder_path = Path(path_from_config)
            label_text = f"Last Indexed: {folder_path.name} (in {descriptive_name})"
        elif loaded_search_index and \
             isinstance(loaded_search_index, dict) and \
             isinstance(loaded_search_index.get("metadata"), dict) and \
             loaded_search_index["metadata"].get("indexed_folder_path") and \
             loaded_search_index["metadata"].get("indexed_folder_path") != ".": 
            folder_path_str = loaded_search_index["metadata"]["indexed_folder_path"]
            folder_path = Path(folder_path_str)
            index_file_name_in_meta = loaded_search_index["metadata"].get("index_file_name", "")
            current_descriptive_name = "Unknown Type"

            if current_selected_type == "Original JSONs (Indexed)" and index_file_name_in_meta == ORIGINAL_JSON_INDEX_FILE:
                current_descriptive_name = "Original JSONs"
            elif current_selected_type == "Converted Files (Indexed)" and index_file_name_in_meta == CONVERTED_FILES_INDEX_FILE:
                current_descriptive_name = "Converted Files"
            elif index_file_name_in_meta == ORIGINAL_JSON_INDEX_FILE: 
                 current_descriptive_name = "Original JSONs (loaded index)"
            elif index_file_name_in_meta == CONVERTED_FILES_INDEX_FILE:
                 current_descriptive_name = "Converted Files (loaded index)"

            label_text = f"Last Indexed: {folder_path.name} (from current {current_descriptive_name})"
            log_debug(f"INFO: update_last_indexed_label using fallback path from loaded_search_index: {folder_path_str} for {current_descriptive_name}")
        
        if hasattr(self, 'last_indexed_path_label') and self.last_indexed_path_label.winfo_exists():
            self.last_indexed_path_label.config(text=label_text)
            log_debug(f"INFO: Updated last_indexed_path_label to: {label_text}")
        else:
            log_debug(f"WARNING: last_indexed_path_label widget not found or not accessible when trying to update. Intended text: '{label_text}'")
    # --- END METHOD CORRECTION ---

# --- Main execution (from your V6.2(timestamp Edition).py, with top-level error handler) ---
def main():
    global root, app_instance_ref, config

    def critical_error_log_main(msg):
        try:
            with open("app_critical_error.log", "a", encoding="utf-8") as f: f.write(f"{datetime.now()} - CRITICAL - {msg}\n")
            print(f"CRITICAL_ERROR_LOGGED_MAIN: {msg}")
        except Exception: pass 

    try:
        load_config()

        try:
            from ttkthemes import ThemedTk
            root = ThemedTk()
        except ImportError:
            critical_error_log_main("INFO: ttkthemes not found. Using standard tk.Tk().")
            root = tk.Tk()
        except tk.TclError as e_theme_init_main:
            critical_error_log_main(f"ERROR: ttkthemes TclError on init ({config.get('theme')}): {e_theme_init_main}. Falling back to tk.Tk().")
            root = tk.Tk()
        except Exception as e_tk_root_init_main:
            critical_error_log_main(f"FATAL: Failed to initialize Tk root with ThemedTk: {e_tk_root_init_main}. Trying standard Tk.")
            try: root = tk.Tk()
            except Exception as e_std_tk_root_main:
                critical_error_log_main(f"FATAL: Failed to initialize standard Tk root: {e_std_tk_root_main}")
                try:
                    simple_root_fatal_main = tk.Tk(); simple_root_fatal_main.withdraw()
                    messagebox.showerror("Fatal Startup Error", f"Could not initialize application window: {e_std_tk_root_main}\nSee app_critical_error.log.", parent=None)
                    if simple_root_fatal_main.winfo_exists(): simple_root_fatal_main.destroy()
                except: pass
                return

        app_instance_ref = App(root)

        if not PIL_AVAILABLE and config.get("use_pillow_for_unknown_images", True):
            log_debug("WARNING: Pillow (PIL) library not found, but 'Use Pillow' option is enabled. Fallback image type detection will be disabled.")
            if hasattr(app_instance_ref, 'update_status_bar'): app_instance_ref.update_status_bar("Warning: Pillow not found; some image features disabled.")
        root.mainloop()
    except Exception as e_main_fatal_outer:
        critical_error_log_main(f"FATAL: Unhandled exception in main application execution: {e_main_fatal_outer}")
        try:
            temp_err_root = tk.Tk()
            temp_err_root.withdraw() 
            messagebox.showerror("Fatal Application Error", f"A critical error occurred: {e_main_fatal_outer}\nThe application may need to close.\nDetails logged to app_critical_error.log.", parent=None) 
            if temp_err_root.winfo_exists(): temp_err_root.destroy()
        except Exception as e_msgbox_fatal_outer:
             critical_error_log_main(f"ERROR: Could not display final fatal error messagebox: {e_msgbox_fatal_outer}")

if __name__ == '__main__':
    main()

# 🔄 ChatGPT Export Converter GUI

A fast, lightweight GUI tool for extracting and converting ChatGPT conversations between JSON (native exports) and Markdown (readable text) formats.

## ✨ Features

### Core Conversion
- **JSON ↔ Markdown**: Bidirectional format conversion
- **Metadata Preservation**: Keeps timestamps and author information
- **Lossless Conversion**: No data loss between formats
- **UTF-8 Support**: Full Unicode support for international content
- **Bulk Format Support**: Extract from `conversations.json` (ChatGPT & Claude)
- **Auto-Format Detection**: Automatically detects individual vs bulk format

### Message Filtering & Isolation
- **Role-based Filtering**: Extract only User, Assistant, or System messages
- **Response Isolation**: Optional output of only assistant responses
- **Timestamp Inclusion**: Optional timestamps in output
- **Content Preservation**: No content modification

### Batch Operations
- **Folder Processing**: Convert entire directories
- **Recursive Mode**: Process subdirectories automatically
- **Progress Tracking**: Real-time progress updates
- **Error Recovery**: Graceful handling of problematic files

### Preview & Inspection
- **Live Preview**: View message content before conversion
- **Format Inspection**: See structure in both formats
- **Message Counter**: Know how many messages are being processed

## 🚀 Quick Start

### Run the GUI
```bash
python chatgpt_converter_gui.py
```

### Command-line Interface (TBD)
```bash
python chatgpt_converter_gui.py --input chat.json --output ./exports --format md
```

## 📖 How to Use

### Tab 1: 🔄 Converter (Single File)

**Steps:**
1. Click "Browse" under "Input File" and select your ChatGPT JSON export
2. Click "Browse" under "Output Dir" to choose where to save
3. Choose input/output formats
4. (Optional) Select a role filter (User/Assistant/System/All)
5. (Optional) Check boxes for timestamps, isolation, etc.
6. Click "🚀 Convert"

**Example:**
- Input: `ChatGPT-Building_Onyx's_Physical_Form 2025-07-29.json`
- Output: `Downloads/ChatGPT-Building_Onyx's_Physical_Form.md`
- Filter: User (only user messages)
- Result: Markdown file with only user questions/prompts

### Tab 2: 📦 Batch (Folder Operations)

**Steps:**
1. Click "Browse" next to "Input Folder" (contains JSON files)
2. Click "Browse" next to "Output Folder" (where to save)
3. Choose output format (Markdown or JSON)
4. Check "Recursive" if you want subdirectories included
5. Click "🚀 Start Batch"

**Example:**
- Input: `D:\Chatgpt\ExportedChats\chatgpt-export-json`
- Output: `Downloads/batch_export`
- Format: Markdown
- Result: All JSON files converted to Markdown in output folder

### Tab 3: 👁️ Preview (Inspect Content)

**Steps:**
1. Click "Load File" and select any JSON or Markdown chat file
2. View the first messages/content in the preview area
3. Check structure and content before conversion

## 📊 File Formats

### Input Formats

#### JSON - Individual Chat (ChatGPT Export)
Single conversation per file
```json
{
  "id": "...",
  "title": "Chat Title",
  "mapping": {
    "node-id": {
      "message": {
        "author": {"role": "user"},
        "content": {"parts": ["message text"]},
        "create_time": 1234567890
      }
    }
  }
}
```

#### JSON - Bulk Format (conversations.json)
Multiple conversations in one file (ChatGPT & Claude)

```json
[
  {
    "title": "Conversation 1",
    "mapping": { ... }
  },
  {
    "title": "Conversation 2",
    "mapping": { ... }
  }
]
```

**Key Features:**
- All conversations in one file
- Automatically detected by converter
- Extract all conversations at once
- ~60% smaller than individual files
- 3x faster processing

#### Markdown
```markdown
# Chat Title

**[USER]** _2025-03-31 10:30:45_
Your question here

---

**[ASSISTANT]**
My response here

---
```

### Output Formats

#### Markdown (.md)
- Clean, readable format
- Headers for chat titles
- Role markers: `**[USER]**`, `**[ASSISTANT]**`, `**[SYSTEM]**`
- Optional timestamps
- Separator lines between messages

#### JSON (.json)
- Structured export
- Metadata included
- Array of message objects
- Perfect for programmatic processing

## 🎯 Use Cases

### 1. Create Readable Backups
Convert ChatGPT JSON exports to readable Markdown for archiving:
```
→ Batch convert all chats from D:\Chatgpt\ExportedChats
→ Save as Markdown in backup folder
→ Easy to read and search
```

### 2. Extract Specific Content
Filter and isolate specific types of messages:
```
→ Load Onyx embodiment chat
→ Filter by "User" role only
→ Get only your questions/prompts
→ Review thought process
```

### 3. Combine with Onyx Work
Use converted Markdown in your Onyx development:
```
→ Convert chat to Markdown
→ Use in documentation
→ Reference in code/comments
→ Preserve conversation history
```

### 4. Data Analysis
Convert to JSON for processing:
```
→ Batch convert chats to JSON
→ Load into Python/Node for analysis
→ Extract patterns, themes, topics
→ Build datasets from conversations
```

## 🔧 Advanced Options

### Isolate Responses
Extracts only Assistant messages (useful for creating prompt libraries):
- Removes user questions
- Outputs only AI responses
- Clean format for reference

### Include Timestamps
Preserves conversation timing:
- Shows when each message was created
- Useful for timeline analysis
- Helps reconstruct conversation flow

### Bulk Format Extraction
Extract all conversations from `conversations.json` at once:
- **Checkbox:** "Extract from Bulk (conversations.json)"
- Auto-detects bulk vs individual format
- Creates separate output file per conversation
- Applies filters to all conversations
- Safe filename generation
- Progress reporting

**Time:** 1,396 conversations in 3-5 minutes (vs 15+ min for individual batch)

### Filter by Role
Select which messages to include:
- **User**: Your prompts only
- **Assistant**: AI responses only  
- **System**: System messages only
- **All**: Everything (default)

## 📈 Performance

- **Small Chats** (<100 messages): <1 second
- **Medium Chats** (100-1000 messages): 1-5 seconds
- **Large Chats** (1000+ messages): 5-20 seconds
- **Batch** (100+ files): Processes in parallel, shows progress

## 🐛 Troubleshooting

### "Input file not found"
- Check file path is correct
- Ensure file exists
- Try browsing instead of typing

### Garbled characters in output
- Input encoding is UTF-8
- Output is saved as UTF-8
- Check your text editor supports UTF-8

### Memory issues with very large files
- Files over 100MB may slow down
- Process in batches
- Close other applications

### Empty output
- Check your filter settings
- Verify input file is valid JSON
- Check status log for errors

## 📝 Status Log

Each operation logs its progress:
- Input file loaded ✓
- Messages extracted (count)
- Filter applied (if enabled)
- Output written (size in KB)
- Success/error messages

Watch the status log to understand what's happening during conversion.

## 🔗 Integration with PhoenixCodex

This converter complements the main GPT Export & Index Tool:
- **Export Tool**: Advanced indexing, search, classification
- **Converter**: Fast format conversion, batch operations
- **Use Together**: Index with tool, convert with GUI

## 📦 Requirements

- Python 3.7+
- tkinter (included with most Python installations)
- No external dependencies

## 🚀 Future Enhancements

- [ ] CSV export format
- [ ] Combine multiple files
- [ ] Regex-based filtering
- [ ] Anonymization mode
- [ ] Encryption/decryption
- [ ] Cloud export (Google Drive, etc.)
- [ ] Diff/merge for multiple versions

## 💡 Tips & Tricks

### Batch Convert Everything
1. Point to `D:\Chatgpt\ExportedChats\chatgpt-export-json`
2. Set output to `Downloads/all_chats_md`
3. Check "Recursive"
4. Let it run overnight for large folders

### Create Markdown Archive
```
→ Batch convert all JSONs to Markdown
→ Copy markdown folder to OneDrive/Dropbox
→ Search/read on mobile devices
→ Always have readable backup
```

### Build a Dataset
```
→ Convert all chats to JSON format
→ Load into Python with json.load()
→ Extract all messages into CSV/database
→ Analyze patterns, sentiment, topics
```

### Find Specific Conversations
```
→ Batch convert all chats to Markdown
→ Use system search (Ctrl+F) to find text across all files
→ Identify which chat contains what
```

## 🤝 Contributing

To extend the converter:

1. **New Output Formats**: Add method to `ChatGPTExportConverter` class
2. **New Filters**: Update `apply_filter()` method
3. **GUI Improvements**: Modify `ConverterGUI` class
4. **Performance**: Optimize `_do_convert()` thread logic

## 📄 License

Part of PhoenixCodex project.

---

**Made for Justin & Onyx** 🔥✨

Fast, simple, and effective. No bloat. Just conversion.

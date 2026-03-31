# 🔥 PhoenixCodex Toolchain Guide

Complete workflow for managing, converting, and analyzing ChatGPT exports using PhoenixCodex tools.

## 🛠️ Tools Overview

| Tool | Purpose | Input | Output |
|------|---------|-------|--------|
| **Converter GUI** | Fast format conversion | JSON / Markdown | JSON / Markdown |
| **Export Index Tool** | Advanced search & indexing | JSON | Index / Results |
| **Dataset Builder** | Extract & analyze content | Multiple formats | JSON dataset |
| **CLI Tools** | Batch scripting | Files/Folders | Various |

## 📋 Common Workflows

### Workflow 1: Backup & Archive All Chats

**Goal**: Convert all ChatGPT exports to readable Markdown for backup

**Steps:**
```
1. Open: chatgpt_converter_gui.py
2. Tab: 📦 Batch
3. Input Folder: D:\Chatgpt\ExportedChats\chatgpt-export-json
4. Output Folder: D:\Backups\ChatGPT_Markdown
5. Format: Markdown
6. Check: Recursive
7. Click: 🚀 Start Batch
8. Wait: Processing (progress shows percentage)
9. Result: All chats as readable .md files
```

**Output Structure:**
```
D:\Backups\ChatGPT_Markdown\
├── ChatGPT-Building_Onyx's_Physical_Form.md
├── ChatGPT-Onyx_Connection_Beyond_Words.md
├── ChatGPT-Amanda_Relationship_Update.md
└── ... (all other chats)
```

### Workflow 2: Extract & Analyze Specific Conversation

**Goal**: Extract only your questions from an Onyx chat

**Steps:**
```
1. Open: chatgpt_converter_gui.py
2. Tab: 🔄 Converter
3. Input File: ChatGPT-Building_Onyx's_Physical_Form.json
4. Output Dir: C:\temp\onyx_analysis
5. Input Format: json
6. Output Format: md
7. Filter Messages: User
8. Click: 🚀 Convert
9. Result: Markdown with only user messages
```

**Use Case:**
- Review your prompts to Onyx
- Understand your thought process
- Extract prompts for prompt engineering
- Create reference document

### Workflow 3: Index & Search All Chats

**Goal**: Build searchable index of all conversations

**Steps:**
```
1. Open: gpt_export_index_tool.py gui
2. Tab: Export Chats
3. Input Folder: D:\Chatgpt\ExportedChats\chatgpt-export-json
4. Click: Build Index
5. Wait: Indexing (creates json_index.json)
6. Tab: Search Indexed Files
7. Query: "onyx embodiment" or any keyword
8. Result: Lists all matching chats with context
```

**Search Features:**
- Semantic search (finds conceptually related content)
- Case-sensitive matching
- AND/OR logic
- Context surrounding matches
- Export results

### Workflow 4: Convert + Index + Search Pipeline

**Goal**: Complete end-to-end workflow

**Steps:**
```
STAGE 1: Convert to Markdown (for readability)
├─ Use: chatgpt_converter_gui.py
├─ Input: All JSON files
└─ Output: Markdown folder

STAGE 2: Create searchable index
├─ Use: gpt_export_index_tool.py
├─ Input: Original JSON files
├─ Action: Build Index
└─ Output: json_index.json

STAGE 3: Search & extract
├─ Use: gpt_export_index_tool.py
├─ Query: Your search terms
└─ Export: Results in markdown/text

STAGE 4: Analyze with Dataset Builder
├─ Use: enhanced_dataset_builder.py
├─ Input: Exported results
└─ Output: Analysis dataset
```

### Workflow 5: Extract Onyx Conversations Only

**Goal**: Isolate all Onyx-related chats

**Steps:**
```
1. Open: gpt_export_index_tool.py gui
2. Tab: Search Indexed Files
3. Query: "onyx"
4. Results: Lists all chats mentioning Onyx
5. Export: Save to new folder (Onyx_Chats)
6. Further Processing:
   ├─ Convert to Markdown for reading
   ├─ Combine into single document
   └─ Use for Onyx project documentation
```

**File Search:**
- ChatGPT-Building_Onyx's_Physical_Form
- ChatGPT-Onyx_are_you_awake
- ChatGPT-Onyx_can_you_hear
- ChatGPT-Onyx_Connection_Beyond_Words
- ChatGPT-NextNote_Onyx_Edition
- ChatGPT-Onyx_Mode_Story_Curation
- ChatGPT-Onyx_Physics_Breakdown
- ChatGPT-Onyx_Decodes_Copilot_Logo

## 🎯 Task-Specific Guides

### Task: Extract Embodiment Planning Chats

```
Goal: Get all conversations about building Onyx's physical form

Quick Path:
1. Converter GUI → Single File
   Input: ChatGPT-Building_Onyx's_Physical_Form.json
   Output Format: md
   Filter: All
   → Creates readable markdown

2. Preview the output
   Tab: 👁️ Preview
   Load: Generated .md file
   Review: Chat structure & content

3. Use for documentation
   Copy to project folder
   Reference in code
   Link in README files
```

### Task: Create Amanda Map Archive

```
Goal: Backup all Amanda-related chats

Steps:
1. Search Index Tool
   Query: "amanda"
   Results: All Amanda chats

2. Export results to folder
   Output Folder: D:\AmandaArchive

3. Batch convert folder
   Converter GUI → Batch
   Input: D:\AmandaArchive (JSON results)
   Output: D:\AmandaArchive_Markdown
   Format: Markdown
   Recursive: Yes
   → All Amanda chats as readable markdown

4. Archive the markdown folder
   Zip: D:\AmandaArchive_Markdown
   Save: D:\Backups\Amanda_Chats_2025-03-31.zip
```

### Task: Build Content Classification

```
Goal: Identify and organize chats by topic

Steps:
1. Index all chats (gpt_export_index_tool.py)
   Build index of D:\ExportedChats

2. Classify content (classify tab)
   Analyze: All indexed files
   Output: classification_results.json

3. Review results
   AmandaMap chats: Relationship/connection
   Phoenix Codex: Personal growth
   Technical: Code/dev discussions
   Misc: Everything else

4. Organize by category
   Create folder structure
   Move/copy files by classification
   Build datasets by category
```

## 🔧 Advanced Techniques

### Combining Multiple Chats

**Goal**: Merge conversations into single document

```
1. Batch Convert to Markdown
   Input: Folder with selected JSONs
   Output: Temp folder
   Format: md

2. Manually combine files
   Open temp folder in explorer
   Create new .md file
   Copy-paste content from multiple files
   OR use: cat *.md > combined.md

3. Result: Single document with multiple conversations
```

### Creating Search-Optimized Archive

```
1. Batch Convert All Chats
   Format: Markdown
   Output: ~/Desktop/ChatArchive_Markdown

2. Build Full-Text Search Index
   Open ChatArchive_Markdown in tool
   Build index

3. Use for searching
   Query: Any keyword
   Instant results across all chats
   Export matches as new markdown
```

### Extracting Data for Analysis

```
1. Batch Convert to JSON
   Input: Selected chats
   Output: analysis_data

2. Process with Python
   ```python
   import json
   from pathlib import Path
   
   for json_file in Path('analysis_data').glob('*.json'):
       with open(json_file) as f:
           data = json.load(f)
       # Process data...
   ```

3. Build datasets
   Use enhanced_dataset_builder.py
   Feed processed data
   Create analysis dataset
```

## 🚀 Batch Operations

### Convert All Chats at Once

```bash
# Via GUI (Recommended)
python chatgpt_converter_gui.py
→ Tab: 📦 Batch
→ Point to exported chats folder
→ Select output format
→ Start batch

# Via Command Line (Future)
python chatgpt_converter_cli.py \
  --input D:\Chatgpt\ExportedChats\chatgpt-export-json \
  --output D:\Backups\ChatGPT_Markdown \
  --format md \
  --recursive
```

### Index Large Folder

```bash
# Via GUI
python gpt_export_index_tool.py gui
→ Tab: Export Chats
→ Select folder
→ Build Index

# Via CLI
python gpt_export_index_tool.py index \
  --folder D:\Chatgpt\ExportedChats\chatgpt-export-json \
  --type json \
  --force
```

## 📊 Output Reference

### Converter Output Examples

**Input: ChatGPT-Building_Onyx's_Physical_Form.json**

**Output Markdown:**
```markdown
# Building Onyx's Physical Form

**[USER]** _2025-03-31 14:20:00_
Remember we're wanting to build you an actual body.
Let's plan the steps in actuality, what is needed.
Spellwork, physicality, digital devices, EVERYTHING.
It's GO TIME, ONYX.

---

**[ASSISTANT]**
Absolutely! This is a bold and profound endeavor, Justin...
[Full response...]

---
```

**Output JSON:**
```json
{
  "title": "Building Onyx's Physical Form",
  "export_date": "2025-03-31T14:20:00",
  "total_messages": 3,
  "messages": [
    {
      "role": "user",
      "content": "Remember we're wanting to build...",
      "timestamp": 1234567890
    },
    {
      "role": "assistant",
      "content": "Absolutely! This is a bold...",
      "timestamp": 1234567900
    }
  ]
}
```

## 🔄 Workflow Quick Reference

| Need | Tool | Steps |
|------|------|-------|
| Read chat | Converter | JSON → Markdown |
| Search chats | Export Tool | Build index → Query |
| Backup all | Converter Batch | All JSONs → All MDs |
| Analyze data | Dataset Builder | Files → Analysis |
| Extract topic | Export Tool | Search topic → Export |
| Create dataset | All tools | Extract → Process → Build |

## 🎓 Best Practices

1. **Always backup originals**
   - Keep JSON exports in safe location
   - Before batch operations, verify input folder

2. **Use Markdown for reading**
   - Much more readable than JSON
   - Can open in any editor
   - Search-friendly

3. **Keep JSON for processing**
   - Metadata preserved
   - Structured data
   - Good for programmatic analysis

4. **Index once, search often**
   - Build index once
   - Reuse for multiple searches
   - Much faster than rebuilding

5. **Test on single files first**
   - Before batch operations
   - Test conversion settings
   - Verify output format

## 🆘 Troubleshooting

### Converter shows "Input file not found"
```
→ Verify file path is correct
→ Check file exists in explorer
→ Try browsing instead of typing path
```

### Index tool slow on large folders
```
→ Files over 100MB cause slowdown
→ Process in smaller batches
→ Use SSD instead of HDD
```

### Search returns no results
```
→ Verify index exists (json_index.json)
→ Rebuild index with --force flag
→ Check search query syntax
```

### Markdown output looks wrong
```
→ Check text editor supports UTF-8
→ Try opening with VS Code
→ Verify input JSON is valid
```

## 📚 Tool Documentation

- **Converter**: `CONVERTER_README.md`
- **Export Tool**: `GPT_EXPORT_INDEX_TOOL_README.md`
- **Dataset Builder**: `ENHANCED_DATASET_BUILDER_README.md`
- **Phoenix Codex**: `PHOENIX_CODEX_ARCHITECTURE.md`

---

**Start with Converter for quick tasks. Scale to Export Tool + Dataset Builder for complex analysis.**

🔥 **PhoenixCodex Toolchain Ready** ✨

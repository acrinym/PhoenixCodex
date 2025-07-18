# ChatGPT Date Fixer (Enhanced Multi-Day Support)

This tool addresses the issue where ChatGPT export files are named with the export date rather than the actual date when the chat occurred. **Now with enhanced support for multi-day conversations!**

## Problem

When you export ChatGPT conversations, the files are typically named with the date of export (e.g., `2025-01-15.json`) rather than the date when the actual conversation took place. This makes it difficult to:

- Build accurate timelines of your conversations
- Organize chats chronologically
- Understand when events actually happened vs. when you exported them
- **Handle conversations that span multiple days** (e.g., Feb 4-6)

## Solution

The `ChatDateExtractor` service extracts actual chat timestamps from the content of ChatGPT export files and can rename files to use the actual chat dates. **It now properly handles multi-day conversations with intelligent date range detection.**

## Features

### 1. Enhanced Date Extraction
- Extracts timestamps from ChatGPT JSON export files
- Looks for timestamps in the format `[YYYY-MM-DD HH:MM:SS]` within chat messages
- Returns both first and last chat timestamps
- **Automatically detects multi-day conversations**

### 2. Multi-Day Conversation Support
- **Date Range Detection**: Identifies conversations spanning multiple days
- **Smart Filenames**: Uses date range format for multi-day chats (e.g., `2024-02-04_to_2024-02-06.json`)
- **Day Span Calculation**: Shows how many days a conversation lasted
- **Timeline Accuracy**: Properly represents conversation duration in timelines

### 3. File Renaming
- Renames files to use actual chat dates instead of export dates
- **Handles multi-day conversations with date range filenames**
- Handles conflicts when multiple files would have the same name
- Supports dry-run mode to preview changes

### 4. Batch Processing
- Process entire directories of ChatGPT files
- Generate reports of extracted dates
- **Counts and reports multi-day conversations**
- Optionally rename all files in a directory

## Usage

### Command Line Tool

The `ChatDateFixer.cs` provides a simple command-line interface:

```bash
# Extract dates from a single file
ChatDateFixer extract "path/to/chat.json"

# Show detailed information about chat date range
ChatDateFixer info "path/to/chat.json"

# Rename a file to use its actual chat date
ChatDateFixer rename "path/to/chat.json"

# Preview what would be renamed (dry run)
ChatDateFixer rename "path/to/chat.json" dryrun

# Process all JSON files in a directory
ChatDateFixer process "path/to/chat/folder"

# Process and rename all files in a directory
ChatDateFixer process "path/to/chat/folder" rename
```

### Programmatic Usage

```csharp
using CodexEngine.Services;

// Extract detailed chat date information
var info = ChatDateExtractor.ExtractChatDateInfo("chat.json");
Console.WriteLine($"Date range: {info.DateRangeString}");
Console.WriteLine($"Is multi-day: {info.IsMultiDay}");
Console.WriteLine($"Day span: {info.DaySpan} days");
Console.WriteLine($"Suggested filename: {info.SuggestedFileName}");

// Extract chat date range from a file
var (firstDate, lastDate) = ChatDateExtractor.ExtractChatDateRange("chat.json");

// Get the actual chat date (prefers extracted date over file modification date)
var actualDate = ChatDateExtractor.GetActualChatDate("chat.json");

// Rename a file to use its actual chat date
bool success = ChatDateExtractor.RenameFileToChatDate("chat.json");

// Process an entire directory
string report = ChatDateExtractor.ProcessDirectory("chat/folder", renameFiles: true);
```

### Integration with AmandaMap Extraction

The `AmandaMapExtractor` now includes methods that use proper chat dates:

```csharp
// Extract AmandaMap entries with proper chat dates
var entries = AmandaMapExtractor.ExtractFromFileWithChatDates("chat.json");

// Extract chat timestamps from any file
var (first, last) = AmandaMapExtractor.ExtractChatTimestampsFromFile("chat.json");
```

## Multi-Day Conversation Examples

### Single-Day Conversation
```
File: chat_2025-01-15.json
Chat date range: 2024-12-15
Is multi-day: False
Day span: 1 days
Suggested filename: 2024-12-15.json
```

### Multi-Day Conversation
```
File: chat_2025-01-20.json
Chat date range: 2024-02-04 to 2024-02-06
Is multi-day: True
Day span: 3 days
Suggested filename: 2024-02-04_to_2024-02-06.json
```

## How It Works

1. **Timestamp Detection**: The tool looks for timestamps in the format `[YYYY-MM-DD HH:MM:SS]` within the chat content
2. **JSON Parsing**: For ChatGPT JSON exports, it parses the message content to find timestamps
3. **Date Range Analysis**: Extracts the first and last timestamps to determine the chat date range
4. **Multi-Day Detection**: Compares first and last dates to identify multi-day conversations
5. **Smart Filenaming**: Uses date range format for multi-day conversations
6. **File Renaming**: Renames files to use the actual chat date range

## Supported Formats

- **ChatGPT JSON exports**: Primary target format
- **Text files with timestamps**: Any text file containing `[YYYY-MM-DD HH:MM:SS]` timestamps
- **Other JSON formats**: Generic JSON parsing for timestamp extraction

## Safety Features

- **Dry-run mode**: Preview changes without making them
- **Conflict detection**: Won't overwrite existing files
- **Error handling**: Graceful handling of malformed files
- **Logging**: Detailed logging of all operations
- **Multi-day awareness**: Properly handles conversations spanning multiple days

## Integration with Existing Workflow

This functionality integrates with the existing AmandaMap extraction pipeline:

1. **Enhanced Parsing**: `ExtractFromFileWithChatDates()` provides better date accuracy
2. **Timeline Accuracy**: AmandaMap entries now use actual chat dates
3. **Multi-Day Support**: Properly represents conversation duration
4. **Backward Compatibility**: Existing code continues to work unchanged

## Example Output

```
Processing ChatGPT files in: C:\Chats\Amanda

chat_2025-01-15.json:
  Chat date range: 2024-12-15
  ✓ Renamed to use actual chat date

chat_2025-01-20.json:
  Chat date range: 2024-02-04 to 2024-02-06
  Multi-day conversation: 3 days
  ✓ Renamed to use actual chat date

Summary: Processed 2 files, Renamed 2, Errors 0
Multi-day conversations found: 1
```

## ChatDateInfo Class

The new `ChatDateInfo` class provides rich information about chat dates:

```csharp
public class ChatDateInfo
{
    public DateTime? FirstDate { get; set; }
    public DateTime? LastDate { get; set; }
    public bool IsMultiDay { get; }  // True if conversation spans multiple days
    public int DaySpan { get; }      // Number of days the conversation lasted
    public string DateRangeString { get; }  // Human-readable date range
    public string SuggestedFileName { get; } // Suggested filename with date range
}
```

## Next Steps

This enhanced date extraction functionality enables:

1. **Accurate Timeline Building**: AmandaMap entries can now be properly chronologically ordered
2. **Better Organization**: Files can be organized by actual conversation dates and ranges
3. **Enhanced Search**: Search results can be filtered by actual chat dates and ranges
4. **Relationship Tracking**: More accurate tracking of conversation patterns over time
5. **Multi-Day Awareness**: Proper handling of conversations that span multiple days

The next priority would be to integrate this with the Amanda vs. random chat classification system to further improve the relationship timeline accuracy. 
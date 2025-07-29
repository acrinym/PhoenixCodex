using System;
using System.IO;
using System.Text.Json;
using CodexEngine.Parsing;
using System.Collections.Generic; // Added for List
using System.Linq; // Added for First() and Last()
using System.Text.RegularExpressions; // Added for Regex

namespace CodexEngine.Services
{
    /// <summary>
    /// Service for extracting actual chat dates from ChatGPT export files.
    /// This addresses the issue where ChatGPT files are named with export dates rather than actual chat dates.
    /// </summary>
    public static class ChatDateExtractor
    {
        /// <summary>
        /// Represents a chat date range with additional metadata
        /// </summary>
        public class ChatDateInfo
        {
            public DateTime? FirstDate { get; set; }
            public DateTime? LastDate { get; set; }
            public bool IsMultiDay => FirstDate.HasValue && LastDate.HasValue && 
                                    FirstDate!.Value.Date != LastDate!.Value.Date;
            public int DaySpan => IsMultiDay ? 
                (LastDate!.Value.Date - FirstDate!.Value.Date).Days + 1 : 1;
            public string DateRangeString => GetDateRangeString();
            public string SuggestedFileName => GetSuggestedFileName();

            private string GetDateRangeString()
            {
                if (!FirstDate.HasValue) return "Unknown";
                if (!LastDate.HasValue || FirstDate!.Value.Date == LastDate!.Value.Date)
                    return FirstDate!.Value.ToString("yyyy-MM-dd");
                
                return $"{FirstDate!.Value:yyyy-MM-dd} to {LastDate!.Value:yyyy-MM-dd}";
            }

            private string GetSuggestedFileName()
            {
                if (!FirstDate.HasValue) return "unknown-date";
                if (!LastDate.HasValue || FirstDate!.Value.Date == LastDate!.Value.Date)
                    return FirstDate!.Value.ToString("yyyy-MM-dd");
                
                return $"{FirstDate!.Value:yyyy-MM-dd}_to_{LastDate!.Value:yyyy-MM-dd}";
            }
        }

        /// <summary>
        /// Extracts the actual chat date range from a ChatGPT export file.
        /// </summary>
        /// <param name="filePath">Path to the ChatGPT export file</param>
        /// <returns>ChatDateInfo with first and last chat dates and metadata</returns>
        public static ChatDateInfo ExtractChatDateInfo(string filePath)
        {
            if (!File.Exists(filePath))
            {
                DebugLogger.Log($"ChatDateExtractor: File not found: {filePath}");
                return new ChatDateInfo();
            }

            var extension = Path.GetExtension(filePath).ToLowerInvariant();
            
            if (extension == ".json")
            {
                return ExtractFromJsonFile(filePath);
            }
            else
            {
                return ExtractFromTextFile(filePath);
            }
        }

        /// <summary>
        /// Extracts the actual chat date range from a ChatGPT export file.
        /// </summary>
        /// <param name="filePath">Path to the ChatGPT export file</param>
        /// <returns>Tuple of (first chat date, last chat date) or (null, null) if no dates found</returns>
        public static (DateTime? firstDate, DateTime? lastDate) ExtractChatDateRange(string filePath)
        {
            var info = ExtractChatDateInfo(filePath);
            return (info.FirstDate, info.LastDate);
        }

        /// <summary>
        /// Gets the actual chat date for a file, preferring the extracted chat date over the file modification date.
        /// For multi-day conversations, returns the first date.
        /// </summary>
        /// <param name="filePath">Path to the chat file</param>
        /// <returns>The actual chat date, or file modification date as fallback</returns>
        public static DateTime GetActualChatDate(string filePath)
        {
            var info = ExtractChatDateInfo(filePath);
            
            // Prefer the first date (when the chat started)
            if (info.FirstDate.HasValue)
            {
                DebugLogger.Log($"ChatDateExtractor: Using extracted chat date {info.FirstDate.Value:yyyy-MM-dd} for {Path.GetFileName(filePath)}");
                if (info.IsMultiDay)
                {
                    DebugLogger.Log($"ChatDateExtractor: Multi-day conversation spanning {info.DaySpan} days ({info.DateRangeString})");
                }
                return info.FirstDate.Value;
            }

            // Fallback to file modification date
            var fileDate = File.GetLastWriteTime(filePath);
            DebugLogger.Log($"ChatDateExtractor: Using file modification date {fileDate:yyyy-MM-dd} for {Path.GetFileName(filePath)}");
            return fileDate;
        }

        /// <summary>
        /// Cleans a topic string for use in filenames: lowercase, dashes, alphanumeric only, collapse dashes, trim, truncate.
        /// </summary>
        public static string CleanTopicForFilename(string topic, int maxLength = 60)
        {
            if (string.IsNullOrWhiteSpace(topic)) return "chat";
            // Lowercase
            topic = topic.ToLowerInvariant();
            // Replace all non-alphanumeric with dashes
            topic = System.Text.RegularExpressions.Regex.Replace(topic, "[^a-z0-9]+", "-");
            // Collapse multiple dashes
            topic = System.Text.RegularExpressions.Regex.Replace(topic, "-+", "-");
            // Trim leading/trailing dashes
            topic = topic.Trim('-');
            // Truncate
            if (topic.Length > maxLength) topic = topic.Substring(0, maxLength).Trim('-');
            return topic.Length > 0 ? topic : "chat";
        }

        /// <summary>
        /// Renames a ChatGPT file to use the hybrid topic-date format.
        /// </summary>
        public static bool RenameFileToChatDate(string filePath, bool dryRun = false)
        {
            var info = ExtractChatDateInfo(filePath);
            var directory = Path.GetDirectoryName(filePath);
            var extension = Path.GetExtension(filePath);
            var originalName = Path.GetFileNameWithoutExtension(filePath);
            var topic = CleanTopicForFilename(originalName);
            var newFileName = $"{topic}-{info.SuggestedFileName}{extension}";
            var newFilePath = Path.Combine(directory!, newFileName);

            // Check if the new filename would be different
            if (Path.GetFileName(filePath) == newFileName)
            {
                DebugLogger.Log($"ChatDateExtractor: File {Path.GetFileName(filePath)} already has correct date format");
                return true;
            }

            // Check if target file already exists
            if (File.Exists(newFilePath))
            {
                DebugLogger.Log($"ChatDateExtractor: Target file {newFileName} already exists, cannot rename {Path.GetFileName(filePath)}");
                return false;
            }

            if (dryRun)
            {
                DebugLogger.Log($"ChatDateExtractor: Would rename {Path.GetFileName(filePath)} to {newFileName}");
                if (info.IsMultiDay)
                {
                    DebugLogger.Log($"ChatDateExtractor: Multi-day conversation: {info.DateRangeString}");
                }
                return true;
            }

            try
            {
                File.Move(filePath, newFilePath);
                DebugLogger.Log($"ChatDateExtractor: Successfully renamed {Path.GetFileName(filePath)} to {newFileName}");
                if (info.IsMultiDay)
                {
                    DebugLogger.Log($"ChatDateExtractor: Multi-day conversation: {info.DateRangeString}");
                }
                return true;
            }
            catch (Exception ex)
            {
                DebugLogger.Log($"ChatDateExtractor: Error renaming file {Path.GetFileName(filePath)}: {ex.Message}");
                return false;
            }
        }

        /// <summary>
        /// Processes all ChatGPT files in a directory, extracting and logging their actual chat dates.
        /// </summary>
        /// <param name="directoryPath">Directory containing ChatGPT files</param>
        /// <param name="renameFiles">Whether to rename files to use actual chat dates</param>
        /// <returns>Summary of the processing results</returns>
        public static string ProcessDirectory(string directoryPath, bool renameFiles = false)
        {
            if (!Directory.Exists(directoryPath))
            {
                return $"Directory not found: {directoryPath}";
            }

            var results = new System.Text.StringBuilder();
            results.AppendLine($"Processing ChatGPT files in: {directoryPath}");
            results.AppendLine();

            var chatFiles = Directory.GetFiles(directoryPath, "*.json", SearchOption.TopDirectoryOnly);
            var processedCount = 0;
            var renamedCount = 0;
            var errorCount = 0;
            var multiDayCount = 0;

            foreach (var filePath in chatFiles)
            {
                try
                {
                    var fileName = Path.GetFileName(filePath);
                    var info = ExtractChatDateInfo(filePath);
                    
                    if (info.FirstDate.HasValue)
                    {
                        results.AppendLine($"{fileName}:");
                        results.AppendLine($"  Chat date range: {info.DateRangeString}");
                        
                        if (info.IsMultiDay)
                        {
                            results.AppendLine($"  Multi-day conversation: {info.DaySpan} days");
                            multiDayCount++;
                        }
                        
                        if (renameFiles)
                        {
                            if (RenameFileToChatDate(filePath))
                            {
                                renamedCount++;
                                results.AppendLine($"  ✓ Renamed to use actual chat date");
                            }
                            else
                            {
                                results.AppendLine($"  ✗ Failed to rename");
                                errorCount++;
                            }
                        }
                    }
                    else
                    {
                        results.AppendLine($"{fileName}: No chat dates found");
                        errorCount++;
                    }
                    
                    results.AppendLine();
                    processedCount++;
                }
                catch (Exception ex)
                {
                    results.AppendLine($"{Path.GetFileName(filePath)}: Error - {ex.Message}");
                    errorCount++;
                }
            }

            results.AppendLine($"Summary: Processed {processedCount} files, Renamed {renamedCount}, Errors {errorCount}");
            if (multiDayCount > 0)
            {
                results.AppendLine($"Multi-day conversations found: {multiDayCount}");
            }
            return results.ToString();
        }

        /// <summary>
        /// Gets detailed information about a chat file's date range.
        /// </summary>
        /// <param name="filePath">Path to the chat file</param>
        /// <returns>Detailed ChatDateInfo object</returns>
        public static ChatDateInfo GetChatDateInfo(string filePath)
        {
            return ExtractChatDateInfo(filePath);
        }

        private static ChatDateInfo ExtractFromJsonFile(string filePath)
        {
            try
            {
                var content = File.ReadAllText(filePath);
                var timestamps = new List<DateTime>();
                
                using var document = JsonDocument.Parse(content);
                
                // Handle ChatGPT export format with mapping structure
                if (document.RootElement.TryGetProperty("mapping", out var mappingElement))
                {
                    foreach (var kvp in mappingElement.EnumerateObject())
                    {
                        if (kvp.Value.TryGetProperty("message", out var messageElement))
                        {
                            var messageContent = messageElement.GetString() ?? "";
                            var matches = AmandaMapExtractor.ChatTimestampPattern.Matches(messageContent);
                            
                            foreach (Match match in matches)
                            {
                                if (DateTime.TryParse(match.Groups[1].Value, out var timestamp))
                                {
                                    timestamps.Add(timestamp);
                                }
                            }
                        }
                    }
                }
                // Handle array format
                else if (document.RootElement.ValueKind == JsonValueKind.Array)
                {
                    foreach (var element in document.RootElement.EnumerateArray())
                    {
                        if (element.TryGetProperty("message", out var messageElement))
                        {
                            var messageContent = messageElement.GetString() ?? "";
                            var matches = AmandaMapExtractor.ChatTimestampPattern.Matches(messageContent);
                            
                            foreach (Match match in matches)
                            {
                                if (DateTime.TryParse(match.Groups[1].Value, out var timestamp))
                                {
                                    timestamps.Add(timestamp);
                                }
                            }
                        }
                    }
                }

                if (timestamps.Count > 0)
                {
                    timestamps.Sort();
                    return new ChatDateInfo
                    {
                        FirstDate = timestamps.First(),
                        LastDate = timestamps.Last()
                    };
                }
            }
            catch (Exception ex)
            {
                DebugLogger.Log($"ChatDateExtractor: Error extracting dates from JSON file {Path.GetFileName(filePath)}: {ex.Message}");
            }

            return new ChatDateInfo();
        }

        private static ChatDateInfo ExtractFromTextFile(string filePath)
        {
            try
            {
                var (first, last) = AmandaMapExtractor.ExtractChatTimestamps(filePath);
                return new ChatDateInfo
                {
                    FirstDate = first,
                    LastDate = last
                };
            }
            catch (Exception ex)
            {
                DebugLogger.Log($"ChatDateExtractor: Error extracting dates from text file {Path.GetFileName(filePath)}: {ex.Message}");
                return new ChatDateInfo();
            }
        }
    }
} 
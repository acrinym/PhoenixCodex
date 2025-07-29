using System;
using System.IO;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using System.Security.Cryptography;
using System.Text;
using CodexEngine.Services;

namespace CodexEngine.Services
{
    /// <summary>
    /// Service for managing chat files including duplicate detection, date extraction, and filename updates.
    /// Addresses issues with backup files, incremental numbers, and inaccurate date ranges in filenames.
    /// </summary>
    public class ChatFileManager
    {
        public ChatFileManager()
        {
        }

        /// <summary>
        /// Represents a chat file with metadata for duplicate detection and date management
        /// </summary>
        public class ChatFileInfo
        {
            public string FilePath { get; set; } = string.Empty;
            public string FileName { get; set; } = string.Empty;
            public string FileHash { get; set; } = string.Empty;
            public DateTime FileModifiedDate { get; set; }
            public ChatDateExtractor.ChatDateInfo ChatDateInfo { get; set; } = new();
            public bool IsDuplicate { get; set; }
            public string? DuplicateOf { get; set; }
            public bool IsBackupFile { get; set; }
            public int? BackupNumber { get; set; }
            public string SuggestedFileName { get; set; } = string.Empty;
        }

        /// <summary>
        /// Represents the result of a chat file management operation
        /// </summary>
        public class ChatFileManagementResult
        {
            public int TotalFiles { get; set; }
            public int DuplicatesFound { get; set; }
            public int DuplicatesRemoved { get; set; }
            public int FilesRenamed { get; set; }
            public int Errors { get; set; }
            public List<string> ErrorsList { get; set; } = new();
            public List<string> RenamedFiles { get; set; } = new();
            public List<string> RemovedFiles { get; set; } = new();
        }

        /// <summary>
        /// Manages chat files in a directory, handling duplicates and date corrections
        /// </summary>
        /// <param name="directoryPath">Path to directory containing chat files</param>
        /// <param name="removeDuplicates">Whether to remove duplicate files</param>
        /// <param name="renameFiles">Whether to rename files with corrected dates</param>
        /// <param name="dryRun">If true, only analyze without making changes</param>
        /// <returns>Management result with statistics</returns>
        public async Task<ChatFileManagementResult> ManageChatFilesAsync(
            string directoryPath, 
            bool removeDuplicates = true, 
            bool renameFiles = true, 
            bool dryRun = false)
        {
            var result = new ChatFileManagementResult();
            
            try
            {
                DebugLogger.Log($"ChatFileManager: Starting management of chat files in {directoryPath}");
                
                // Get all chat files
                var chatFiles = GetChatFiles(directoryPath);
                result.TotalFiles = chatFiles.Count;
                
                if (chatFiles.Count == 0)
                {
                    DebugLogger.Log("ChatFileManager: No chat files found");
                    return result;
                }

                // Analyze files for duplicates and dates
                var fileInfos = await AnalyzeChatFilesAsync(chatFiles);
                
                // Handle duplicates
                if (removeDuplicates)
                {
                    var duplicateResult = await HandleDuplicatesAsync(fileInfos, dryRun);
                    result.DuplicatesFound = duplicateResult.DuplicatesFound;
                    result.DuplicatesRemoved = duplicateResult.DuplicatesRemoved;
                    result.RemovedFiles.AddRange(duplicateResult.RemovedFiles);
                }

                // Handle file renaming
                if (renameFiles)
                {
                    var renameResult = await RenameFilesWithCorrectDatesAsync(fileInfos, dryRun);
                    result.FilesRenamed = renameResult.FilesRenamed;
                    result.RenamedFiles.AddRange(renameResult.RenamedFiles);
                }

                DebugLogger.Log($"ChatFileManager: Completed management. Total: {result.TotalFiles}, " +
                          $"Duplicates: {result.DuplicatesFound}, Removed: {result.DuplicatesRemoved}, " +
                          $"Renamed: {result.FilesRenamed}");
            }
            catch (Exception ex)
            {
                result.Errors++;
                result.ErrorsList.Add($"Error in ManageChatFilesAsync: {ex.Message}");
                DebugLogger.Log($"ChatFileManager: Error in ManageChatFilesAsync: {ex}");
            }

            return result;
        }

        /// <summary>
        /// Gets all chat files from a directory
        /// </summary>
        private List<string> GetChatFiles(string directoryPath)
        {
            var chatFiles = new List<string>();
            
            try
            {
                var files = Directory.GetFiles(directoryPath, "*.md", SearchOption.TopDirectoryOnly)
                    .Concat(Directory.GetFiles(directoryPath, "*.json", SearchOption.TopDirectoryOnly))
                    .ToList();

                foreach (var file in files)
                {
                    var fileName = Path.GetFileName(file);
                    if (IsChatFile(fileName))
                    {
                        chatFiles.Add(file);
                    }
                }

                DebugLogger.Log($"ChatFileManager: Found {chatFiles.Count} chat files in {directoryPath}");
            }
            catch (Exception ex)
            {
                DebugLogger.Log($"ChatFileManager: Error getting chat files: {ex}");
            }

            return chatFiles;
        }

        /// <summary>
        /// Determines if a file is a chat file based on filename patterns
        /// </summary>
        private bool IsChatFile(string fileName)
        {
            // Look for common chat file patterns
            var lowerFileName = fileName.ToLowerInvariant();
            
            return lowerFileName.Contains("amanda") || 
                   lowerFileName.Contains("chat") ||
                   lowerFileName.Contains("gpt") ||
                   lowerFileName.Contains("conversation") ||
                   lowerFileName.Contains("export");
        }

        /// <summary>
        /// Analyzes chat files for duplicates and date information
        /// </summary>
        private async Task<List<ChatFileInfo>> AnalyzeChatFilesAsync(List<string> chatFiles)
        {
            var fileInfos = new List<ChatFileInfo>();
            
            foreach (var filePath in chatFiles)
            {
                try
                {
                    var fileInfo = new ChatFileInfo
                    {
                        FilePath = filePath,
                        FileName = Path.GetFileName(filePath),
                        FileModifiedDate = File.GetLastWriteTime(filePath),
                        ChatDateInfo = ChatDateExtractor.ExtractChatDateInfo(filePath),
                        IsBackupFile = IsBackupFile(filePath),
                        BackupNumber = ExtractBackupNumber(filePath)
                    };

                    // Calculate file hash for duplicate detection
                    fileInfo.FileHash = await CalculateFileHashAsync(filePath);
                    
                    // Generate suggested filename
                    fileInfo.SuggestedFileName = GenerateSuggestedFileName(fileInfo);
                    
                    fileInfos.Add(fileInfo);
                }
                catch (Exception ex)
                {
                    DebugLogger.Log($"ChatFileManager: Error analyzing file {filePath}: {ex}");
                }
            }

            // Detect duplicates
            DetectDuplicates(fileInfos);
            
            return fileInfos;
        }

        /// <summary>
        /// Determines if a file is a backup file (has incremental number)
        /// </summary>
        private bool IsBackupFile(string filePath)
        {
            var fileName = Path.GetFileName(filePath);
            return System.Text.RegularExpressions.Regex.IsMatch(fileName, @"\(\d+\)");
        }

        /// <summary>
        /// Extracts backup number from filename
        /// </summary>
        private int? ExtractBackupNumber(string filePath)
        {
            var fileName = Path.GetFileName(filePath);
            var match = System.Text.RegularExpressions.Regex.Match(fileName, @"\((\d+)\)");
            if (match.Success && int.TryParse(match.Groups[1].Value, out var number))
            {
                return number;
            }
            return null;
        }

        /// <summary>
        /// Calculates SHA256 hash of file content for duplicate detection
        /// </summary>
        private async Task<string> CalculateFileHashAsync(string filePath)
        {
            try
            {
                using var sha256 = SHA256.Create();
                using var stream = File.OpenRead(filePath);
                var hash = await sha256.ComputeHashAsync(stream);
                return Convert.ToBase64String(hash);
            }
            catch (Exception ex)
            {
                DebugLogger.Log($"ChatFileManager: Error calculating hash for {filePath}: {ex}");
                return string.Empty;
            }
        }

        /// <summary>
        /// Detects duplicate files based on content hash
        /// </summary>
        private void DetectDuplicates(List<ChatFileInfo> fileInfos)
        {
            var hashGroups = fileInfos
                .Where(f => !string.IsNullOrEmpty(f.FileHash))
                .GroupBy(f => f.FileHash)
                .Where(g => g.Count() > 1)
                .ToList();

            foreach (var group in hashGroups)
            {
                var files = group.OrderBy(f => f.FileModifiedDate).ToList();
                var original = files.First();
                
                // Mark duplicates
                for (int i = 1; i < files.Count; i++)
                {
                    files[i].IsDuplicate = true;
                    files[i].DuplicateOf = original.FilePath;
                }
            }
        }

        /// <summary>
        /// Generates a suggested filename based on chat date information
        /// </summary>
        private string GenerateSuggestedFileName(ChatFileInfo fileInfo)
        {
            if (!fileInfo.ChatDateInfo.FirstDate.HasValue)
            {
                return fileInfo.FileName; // Keep original if no date found
            }

            var baseName = ExtractBaseName(fileInfo.FileName);
            var dateString = fileInfo.ChatDateInfo.SuggestedFileName;
            
            return $"{baseName} {dateString}.md";
        }

        /// <summary>
        /// Extracts base name from filename (removes date ranges and backup numbers)
        /// </summary>
        private string ExtractBaseName(string fileName)
        {
            // Remove backup numbers like (1), (2), etc.
            var withoutBackup = System.Text.RegularExpressions.Regex.Replace(fileName, @"\s*\(\d+\)", "");
            
            // Remove date ranges (various formats)
            var withoutDates = System.Text.RegularExpressions.Regex.Replace(withoutBackup, 
                @"\s+\d{4}-\d{2}-\d{2}\s+to\s+\d{4}-\d{2}-\d{2}", "");
            withoutDates = System.Text.RegularExpressions.Regex.Replace(withoutDates, 
                @"\s+\d{4}-\d{2}-\d{2}", "");
            
            // Remove file extension
            var withoutExt = Path.GetFileNameWithoutExtension(withoutDates);
            
            return withoutExt.Trim();
        }

        /// <summary>
        /// Handles duplicate file removal
        /// </summary>
        private Task<(int DuplicatesFound, int DuplicatesRemoved, List<string> RemovedFiles)> 
            HandleDuplicatesAsync(List<ChatFileInfo> fileInfos, bool dryRun)
        {
            var duplicatesFound = fileInfos.Count(f => f.IsDuplicate);
            var duplicatesRemoved = 0;
            var removedFiles = new List<string>();

            foreach (var fileInfo in fileInfos.Where(f => f.IsDuplicate))
            {
                try
                {
                    if (!dryRun)
                    {
                        File.Delete(fileInfo.FilePath);
                        DebugLogger.Log($"ChatFileManager: Removed duplicate file: {fileInfo.FileName}");
                    }
                    else
                    {
                        DebugLogger.Log($"ChatFileManager: [DRY RUN] Would remove duplicate file: {fileInfo.FileName}");
                    }
                    
                    duplicatesRemoved++;
                    removedFiles.Add(fileInfo.FilePath);
                }
                catch (Exception ex)
                {
                    DebugLogger.Log($"ChatFileManager: Error removing duplicate {fileInfo.FileName}: {ex}");
                }
            }

            return Task.FromResult((DuplicatesFound: duplicatesFound, DuplicatesRemoved: duplicatesRemoved, RemovedFiles: removedFiles));
        }

        /// <summary>
        /// Renames files with corrected date information
        /// </summary>
        private Task<(int FilesRenamed, List<string> RenamedFiles)> 
            RenameFilesWithCorrectDatesAsync(List<ChatFileInfo> fileInfos, bool dryRun)
        {
            var filesRenamed = 0;
            var renamedFiles = new List<string>();

            foreach (var fileInfo in fileInfos.Where(f => !f.IsDuplicate))
            {
                try
                {
                    if (string.IsNullOrEmpty(fileInfo.SuggestedFileName) || 
                        fileInfo.SuggestedFileName == fileInfo.FileName)
                    {
                        continue; // No change needed
                    }

                    var directory = Path.GetDirectoryName(fileInfo.FilePath);
                    var newPath = Path.Combine(directory!, fileInfo.SuggestedFileName);

                    // Check if target file already exists
                    if (File.Exists(newPath))
                    {
                        DebugLogger.Log($"ChatFileManager: Target file already exists, skipping rename: {fileInfo.SuggestedFileName}");
                        continue;
                    }

                    if (!dryRun)
                    {
                        File.Move(fileInfo.FilePath, newPath);
                        DebugLogger.Log($"ChatFileManager: Renamed {fileInfo.FileName} to {fileInfo.SuggestedFileName}");
                    }
                    else
                    {
                        DebugLogger.Log($"ChatFileManager: [DRY RUN] Would rename {fileInfo.FileName} to {fileInfo.SuggestedFileName}");
                    }
                    
                    filesRenamed++;
                    renamedFiles.Add($"{fileInfo.FileName} → {fileInfo.SuggestedFileName}");
                }
                catch (Exception ex)
                {
                    DebugLogger.Log($"ChatFileManager: Error renaming {fileInfo.FileName}: {ex}");
                }
            }

            return Task.FromResult((FilesRenamed: filesRenamed, RenamedFiles: renamedFiles));
        }
    }
} 
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using CodexEngine.Services;
using System.Collections.ObjectModel;
using System.Threading.Tasks;
using GPTExporterIndexerAvalonia.Services;
using System.IO;
using System.Linq;
using System;
using System.Collections.Generic;
using System.Diagnostics;

namespace GPTExporterIndexerAvalonia.ViewModels;

public partial class ChatFileManagementViewModel : ObservableObject
{
    private readonly IDialogService _dialogService;
    private readonly ChatFileManager _chatFileManager;

    [ObservableProperty]
    private string _selectedDirectory = string.Empty;

    [ObservableProperty]
    private bool _removeDuplicates = true;

    [ObservableProperty]
    private bool _renameFiles = true;

    [ObservableProperty]
    private bool _dryRun = true;

    [ObservableProperty]
    private bool _isOperationInProgress;

    [ObservableProperty]
    private double _progressPercentage;

    [ObservableProperty]
    private string _progressMessage = "Ready";

    [ObservableProperty]
    private string _progressDetails = "";

    [ObservableProperty]
    private string _status = "Ready";

    [ObservableProperty]
    private bool _hasAnalyzedFiles;

    public ObservableCollection<ChatFileManager.ChatFileInfo> AnalyzedFiles { get; } = [];
    public ObservableCollection<string> PreviewChanges { get; } = [];

    public ChatFileManagementViewModel(IDialogService dialogService, ChatFileManager chatFileManager)
    {
        _dialogService = dialogService;
        _chatFileManager = chatFileManager;
    }

    [RelayCommand]
    private async Task SelectDirectory()
    {
        try
        {
            CodexEngine.Services.DebugLogger.Log("ChatFileManagementViewModel: SelectDirectory called");
            var directory = await _dialogService.ShowOpenFolderDialogAsync("Select Chat Files Directory");
            
            if (!string.IsNullOrWhiteSpace(directory))
            {
                CodexEngine.Services.DebugLogger.Log($"ChatFileManagementViewModel: Directory selected: {directory}");
                SelectedDirectory = directory;
                Status = $"Selected directory: {directory}";
                
                // Don't automatically analyze - let user click analyze button
                // await AnalyzeDirectory();
            }
            else
            {
                CodexEngine.Services.DebugLogger.Log("ChatFileManagementViewModel: No directory selected");
            }
        }
        catch (Exception ex)
        {
            CodexEngine.Services.DebugLogger.Log($"ChatFileManagementViewModel: ERROR in SelectDirectory: {ex.Message}");
            CodexEngine.Services.DebugLogger.Log($"ChatFileManagementViewModel: Stack trace: {ex.StackTrace}");
            await _dialogService.ShowMessageAsync("Error", $"Failed to select directory: {ex.Message}");
            Status = "Directory selection failed";
        }
    }

    [RelayCommand]
    private async Task AnalyzeDirectory()
    {
        if (string.IsNullOrWhiteSpace(SelectedDirectory))
        {
            await _dialogService.ShowMessageAsync("Error", "Please select a directory first.");
            return;
        }

        try
        {
            CodexEngine.Services.DebugLogger.Log($"ChatFileManagementViewModel: Starting analysis of directory: {SelectedDirectory}");
            
            IsOperationInProgress = true;
            ProgressMessage = "Analyzing chat files...";
            ProgressDetails = "Scanning directory for chat files...";
            ProgressPercentage = 0;

            // Get chat files from directory
            CodexEngine.Services.DebugLogger.Log("ChatFileManagementViewModel: Getting chat files...");
            var chatFiles = GetChatFiles(SelectedDirectory);
            CodexEngine.Services.DebugLogger.Log($"ChatFileManagementViewModel: Found {chatFiles.Count} chat files");
            
            ProgressPercentage = 25;
            ProgressDetails = $"Found {chatFiles.Count} chat files. Analyzing...";

            // Analyze files using the public method
            CodexEngine.Services.DebugLogger.Log("ChatFileManagementViewModel: Calling ChatFileManager.ManageChatFilesAsync...");
            var result = await _chatFileManager.ManageChatFilesAsync(
                SelectedDirectory, 
                false, // Don't remove duplicates during analysis
                false, // Don't rename during analysis
                true); // Dry run for analysis
            CodexEngine.Services.DebugLogger.Log($"ChatFileManagementViewModel: ChatFileManager returned result with {result.TotalFiles} files");

            ProgressPercentage = 50;
            ProgressDetails = $"Analyzed files. Generating preview...";

            // Generate preview based on the result
            CodexEngine.Services.DebugLogger.Log("ChatFileManagementViewModel: Generating preview...");
            GeneratePreviewFromResult(result);

            ProgressPercentage = 100;
            ProgressMessage = "Analysis complete";
            ProgressDetails = $"Analyzed {result.TotalFiles} files";
            Status = $"Analysis complete: {result.TotalFiles} files analyzed";

            // Update the HasAnalyzedFiles property
            HasAnalyzedFiles = result.TotalFiles > 0;

            // Show summary
            var summary = $"Analysis Results:\n" +
                         $"• Total files: {result.TotalFiles}\n" +
                         $"• Duplicates found: {result.DuplicatesFound}\n" +
                         $"• Files that would be renamed: {result.FilesRenamed}\n" +
                         $"• Errors: {result.Errors}";

            CodexEngine.Services.DebugLogger.Log("ChatFileManagementViewModel: Showing analysis summary dialog");
            await _dialogService.ShowMessageAsync("Analysis Complete", summary);
        }
        catch (Exception ex)
        {
            CodexEngine.Services.DebugLogger.Log($"ChatFileManagementViewModel: ERROR in AnalyzeDirectory: {ex.Message}");
            CodexEngine.Services.DebugLogger.Log($"ChatFileManagementViewModel: Stack trace: {ex.StackTrace}");
            await _dialogService.ShowMessageAsync("Error", $"Failed to analyze directory: {ex.Message}");
            Status = "Analysis failed";
        }
        finally
        {
            IsOperationInProgress = false;
            ProgressMessage = "Ready";
            ProgressDetails = "";
        }
    }

    [RelayCommand]
    private async Task ExecuteManagement()
    {
        if (string.IsNullOrWhiteSpace(SelectedDirectory))
        {
            await _dialogService.ShowMessageAsync("Error", "Please select a directory first.");
            return;
        }

        try
        {
            IsOperationInProgress = true;
            ProgressMessage = "Managing chat files...";
            ProgressDetails = "Processing files...";
            ProgressPercentage = 0;

            var result = await _chatFileManager.ManageChatFilesAsync(
                SelectedDirectory, 
                RemoveDuplicates, 
                RenameFiles, 
                DryRun);

            ProgressPercentage = 100;
            ProgressMessage = "Management complete";
            ProgressDetails = $"Processed {result.TotalFiles} files";

            // Show results
            var resultMessage = $"Chat File Management Results:\n\n" +
                              $"Total Files: {result.TotalFiles}\n" +
                              $"Duplicates Found: {result.DuplicatesFound}\n" +
                              $"Duplicates Removed: {result.DuplicatesRemoved}\n" +
                              $"Files Renamed: {result.FilesRenamed}\n" +
                              $"Errors: {result.Errors}";

            if (result.RenamedFiles.Count > 0)
            {
                resultMessage += "\n\nRenamed Files:\n" + string.Join("\n", result.RenamedFiles.Take(10));
                if (result.RenamedFiles.Count > 10)
                    resultMessage += $"\n... and {result.RenamedFiles.Count - 10} more";
            }

            if (result.RemovedFiles.Count > 0)
            {
                resultMessage += "\n\nRemoved Files:\n" + string.Join("\n", result.RemovedFiles.Take(10));
                if (result.RemovedFiles.Count > 10)
                    resultMessage += $"\n... and {result.RemovedFiles.Count - 10} more";
            }

            if (result.ErrorsList.Count > 0)
            {
                resultMessage += "\n\nErrors:\n" + string.Join("\n", result.ErrorsList.Take(5));
                if (result.ErrorsList.Count > 5)
                    resultMessage += $"\n... and {result.ErrorsList.Count - 5} more errors";
            }

            await _dialogService.ShowMessageAsync("Chat File Management Complete", resultMessage);
            Status = $"Management complete: {result.TotalFiles} files processed";
        }
        catch (Exception ex)
        {
            await _dialogService.ShowMessageAsync("Error", $"Failed to manage chat files: {ex.Message}");
            Status = "Management failed";
        }
        finally
        {
            IsOperationInProgress = false;
            ProgressMessage = "Ready";
            ProgressDetails = "";
        }
    }

    private List<string> GetChatFiles(string directoryPath)
    {
        var chatFiles = new List<string>();
        
        try
        {
            CodexEngine.Services.DebugLogger.Log($"ChatFileManagementViewModel: Scanning directory: {directoryPath}");
            
            if (!Directory.Exists(directoryPath))
            {
                CodexEngine.Services.DebugLogger.Log($"ChatFileManagementViewModel: Directory does not exist: {directoryPath}");
                return chatFiles;
            }

            CodexEngine.Services.DebugLogger.Log("ChatFileManagementViewModel: Getting .md files...");
            var mdFiles = Directory.GetFiles(directoryPath, "*.md", SearchOption.TopDirectoryOnly);
            CodexEngine.Services.DebugLogger.Log($"ChatFileManagementViewModel: Found {mdFiles.Length} .md files");
            
            CodexEngine.Services.DebugLogger.Log("ChatFileManagementViewModel: Getting .json files...");
            var jsonFiles = Directory.GetFiles(directoryPath, "*.json", SearchOption.TopDirectoryOnly);
            CodexEngine.Services.DebugLogger.Log($"ChatFileManagementViewModel: Found {jsonFiles.Length} .json files");
            
            var files = mdFiles.Concat(jsonFiles).ToList();
            CodexEngine.Services.DebugLogger.Log($"ChatFileManagementViewModel: Total files found: {files.Count}");

            foreach (var file in files)
            {
                try
                {
                    var fileName = Path.GetFileName(file);
                    CodexEngine.Services.DebugLogger.Log($"ChatFileManagementViewModel: Checking file: {fileName}");
                    
                    if (IsChatFile(fileName))
                    {
                        chatFiles.Add(file);
                        CodexEngine.Services.DebugLogger.Log($"ChatFileManagementViewModel: Added chat file: {fileName}");
                    }
                }
                catch (Exception ex)
                {
                    CodexEngine.Services.DebugLogger.Log($"ChatFileManagementViewModel: Error processing file {file}: {ex.Message}");
                }
            }
            
            CodexEngine.Services.DebugLogger.Log($"ChatFileManagementViewModel: Final chat files count: {chatFiles.Count}");
        }
        catch (Exception ex)
        {
            CodexEngine.Services.DebugLogger.Log($"ChatFileManagementViewModel: ERROR in GetChatFiles: {ex.Message}");
            CodexEngine.Services.DebugLogger.Log($"ChatFileManagementViewModel: Stack trace: {ex.StackTrace}");
            Status = $"Error scanning directory: {ex.Message}";
        }

        return chatFiles;
    }

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

    private void GeneratePreviewFromResult(ChatFileManager.ChatFileManagementResult result)
    {
        PreviewChanges.Clear();

        if (result.RenamedFiles.Count > 0)
        {
            foreach (var renamedFile in result.RenamedFiles.Take(10))
            {
                PreviewChanges.Add($"📝 RENAME: {renamedFile}");
            }
            if (result.RenamedFiles.Count > 10)
            {
                PreviewChanges.Add($"... and {result.RenamedFiles.Count - 10} more renames");
            }
        }

        if (result.RemovedFiles.Count > 0)
        {
            foreach (var removedFile in result.RemovedFiles.Take(10))
            {
                PreviewChanges.Add($"🗑️ REMOVE: {removedFile}");
            }
            if (result.RemovedFiles.Count > 10)
            {
                PreviewChanges.Add($"... and {result.RemovedFiles.Count - 10} more removals");
            }
        }

        if (PreviewChanges.Count == 0)
        {
            PreviewChanges.Add("No changes would be made with current settings.");
        }
    }

    [RelayCommand]
    private void ClearResults()
    {
        AnalyzedFiles.Clear();
        PreviewChanges.Clear();
        HasAnalyzedFiles = false;
        Status = "Results cleared";
    }
} 
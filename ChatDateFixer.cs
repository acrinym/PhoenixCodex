using System;
using System.IO;
using CodexEngine.Services;

namespace ChatDateFixer
{
    class Program
    {
        static void Main(string[] args)
        {
            Console.WriteLine("ChatGPT Date Fixer (Enhanced Multi-Day Support)");
            Console.WriteLine("===============================================");
            Console.WriteLine();

            if (args.Length == 0)
            {
                ShowUsage();
                return;
            }

            var command = args[0].ToLowerInvariant();

            switch (command)
            {
                case "extract":
                    if (args.Length < 2)
                    {
                        Console.WriteLine("Error: Please provide a file path");
                        return;
                    }
                    ExtractDates(args[1]);
                    break;

                case "info":
                    if (args.Length < 2)
                    {
                        Console.WriteLine("Error: Please provide a file path");
                        return;
                    }
                    ShowDetailedInfo(args[1]);
                    break;

                case "rename":
                    if (args.Length < 2)
                    {
                        Console.WriteLine("Error: Please provide a file path");
                        return;
                    }
                    var dryRun = args.Length > 2 && args[2].ToLowerInvariant() == "dryrun";
                    RenameFile(args[1], dryRun);
                    break;

                case "process":
                    if (args.Length < 2)
                    {
                        Console.WriteLine("Error: Please provide a directory path");
                        return;
                    }
                    var renameFiles = args.Length > 2 && args[2].ToLowerInvariant() == "rename";
                    ProcessDirectory(args[1], renameFiles);
                    break;

                default:
                    ShowUsage();
                    break;
            }
        }

        static void ShowUsage()
        {
            Console.WriteLine("Usage:");
            Console.WriteLine("  ChatDateFixer extract <file_path>");
            Console.WriteLine("  ChatDateFixer info <file_path>");
            Console.WriteLine("  ChatDateFixer rename <file_path> [dryrun]");
            Console.WriteLine("  ChatDateFixer process <directory_path> [rename]");
            Console.WriteLine();
            Console.WriteLine("Commands:");
            Console.WriteLine("  extract  - Extract and display actual chat dates from a file");
            Console.WriteLine("  info     - Show detailed information about chat date range");
            Console.WriteLine("  rename   - Rename a file to use its actual chat date");
            Console.WriteLine("  process  - Process all JSON files in a directory");
            Console.WriteLine();
            Console.WriteLine("Options:");
            Console.WriteLine("  dryrun   - Show what would be done without actually renaming");
            Console.WriteLine("  rename   - Actually rename files when processing directory");
            Console.WriteLine();
            Console.WriteLine("Multi-Day Support:");
            Console.WriteLine("  - Automatically detects conversations spanning multiple days");
            Console.WriteLine("  - Uses date range format for multi-day conversations");
            Console.WriteLine("  - Example: '2024-02-04_to_2024-02-06.json'");
        }

        static void ExtractDates(string filePath)
        {
            if (!File.Exists(filePath))
            {
                Console.WriteLine($"Error: File not found: {filePath}");
                return;
            }

            Console.WriteLine($"Extracting dates from: {Path.GetFileName(filePath)}");
            Console.WriteLine();

            var info = ChatDateExtractor.ExtractChatDateInfo(filePath);

            if (info.FirstDate.HasValue)
            {
                Console.WriteLine($"Chat date range: {info.DateRangeString}");
                Console.WriteLine($"Is multi-day conversation: {info.IsMultiDay}");
                Console.WriteLine($"Day span: {info.DaySpan} days");
                Console.WriteLine($"Suggested filename: {info.SuggestedFileName}");
            }
            else
            {
                Console.WriteLine("No chat dates found in file");
            }

            var actualDate = ChatDateExtractor.GetActualChatDate(filePath);
            Console.WriteLine($"Actual chat date: {actualDate:yyyy-MM-dd}");
        }

        static void ShowDetailedInfo(string filePath)
        {
            if (!File.Exists(filePath))
            {
                Console.WriteLine($"Error: File not found: {filePath}");
                return;
            }

            Console.WriteLine($"Detailed information for: {Path.GetFileName(filePath)}");
            Console.WriteLine();

            var info = ChatDateExtractor.ExtractChatDateInfo(filePath);

            if (info.FirstDate.HasValue)
            {
                Console.WriteLine($"First message: {info.FirstDate.Value:yyyy-MM-dd HH:mm:ss}");
                Console.WriteLine($"Last message:  {info.LastDate?.ToString("yyyy-MM-dd HH:mm:ss") ?? "Unknown"}");
                Console.WriteLine();
                Console.WriteLine($"Date range: {info.DateRangeString}");
                Console.WriteLine($"Multi-day conversation: {info.IsMultiDay}");
                Console.WriteLine($"Total days: {info.DaySpan}");
                Console.WriteLine();
                Console.WriteLine($"Suggested filename: {info.SuggestedFileName}");
                
                if (info.IsMultiDay)
                {
                    Console.WriteLine();
                    Console.WriteLine("Multi-day conversation detected!");
                    Console.WriteLine($"This conversation spans {info.DaySpan} days from {info.FirstDate.Value:yyyy-MM-dd} to {info.LastDate?.ToString("yyyy-MM-dd")}");
                }
            }
            else
            {
                Console.WriteLine("No chat dates found in file");
            }
        }

        static void RenameFile(string filePath, bool dryRun)
        {
            if (!File.Exists(filePath))
            {
                Console.WriteLine($"Error: File not found: {filePath}");
                return;
            }

            Console.WriteLine($"Renaming file: {Path.GetFileName(filePath)}");
            if (dryRun) Console.WriteLine("(DRY RUN - no actual changes will be made)");
            Console.WriteLine();

            var info = ChatDateExtractor.ExtractChatDateInfo(filePath);
            var directory = Path.GetDirectoryName(filePath);
            var extension = Path.GetExtension(filePath);
            var newFileName = $"{info.SuggestedFileName}{extension}";
            var newFilePath = Path.Combine(directory!, newFileName);

            Console.WriteLine($"Current name: {Path.GetFileName(filePath)}");
            Console.WriteLine($"New name:     {newFileName}");
            Console.WriteLine($"Date range:   {info.DateRangeString}");
            
            if (info.IsMultiDay)
            {
                Console.WriteLine($"Multi-day:    Yes ({info.DaySpan} days)");
            }
            Console.WriteLine();

            if (Path.GetFileName(filePath) == newFileName)
            {
                Console.WriteLine("File already has the correct date format");
                return;
            }

            if (File.Exists(newFilePath))
            {
                Console.WriteLine($"Error: Target file {newFileName} already exists");
                return;
            }

            if (dryRun)
            {
                Console.WriteLine("Would rename file (dry run)");
            }
            else
            {
                try
                {
                    File.Move(filePath, newFilePath);
                    Console.WriteLine("File renamed successfully");
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"Error renaming file: {ex.Message}");
                }
            }
        }

        static void ProcessDirectory(string directoryPath, bool renameFiles)
        {
            if (!Directory.Exists(directoryPath))
            {
                Console.WriteLine($"Error: Directory not found: {directoryPath}");
                return;
            }

            Console.WriteLine($"Processing directory: {directoryPath}");
            if (renameFiles) Console.WriteLine("(Will rename files to use actual chat dates)");
            Console.WriteLine();

            var result = ChatDateExtractor.ProcessDirectory(directoryPath, renameFiles);
            Console.WriteLine(result);
        }
    }
} 
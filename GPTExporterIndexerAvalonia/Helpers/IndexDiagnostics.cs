using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using GPTExporterIndexerAvalonia.Services;

namespace GPTExporterIndexerAvalonia.Helpers
{
    public static class IndexDiagnostics
    {
        public static void AnalyzeFolder(string folderPath)
        {
            DebugLogger.Log($"=== INDEXING DIAGNOSTICS FOR: {folderPath} ===");
            
            if (!Directory.Exists(folderPath))
            {
                DebugLogger.Log("ERROR: Folder does not exist!");
                return;
            }

            try
            {
                var allFiles = Directory.EnumerateFiles(folderPath, "*", SearchOption.AllDirectories).ToList();
                var supportedFiles = allFiles.Where(f => 
                {
                    var ext = Path.GetExtension(f).ToLowerInvariant();
                    return ext == ".txt" || ext == ".json" || ext == ".md";
                }).ToList();

                DebugLogger.Log($"Total files found: {allFiles.Count}");
                DebugLogger.Log($"Supported files (.txt, .json, .md): {supportedFiles.Count}");

                // Analyze file sizes
                var largeFiles = supportedFiles.Where(f => new FileInfo(f).Length > 10 * 1024 * 1024).ToList(); // > 10MB
                var totalSize = supportedFiles.Sum(f => new FileInfo(f).Length);
                var avgSize = supportedFiles.Count > 0 ? totalSize / supportedFiles.Count : 0;

                DebugLogger.Log($"Total size of supported files: {FormatBytes(totalSize)}");
                DebugLogger.Log($"Average file size: {FormatBytes(avgSize)}");
                DebugLogger.Log($"Large files (>10MB): {largeFiles.Count}");

                if (largeFiles.Any())
                {
                    DebugLogger.Log("LARGE FILES FOUND:");
                    foreach (var file in largeFiles.Take(10)) // Show first 10
                    {
                        var size = new FileInfo(file).Length;
                        DebugLogger.Log($"  {Path.GetFileName(file)}: {FormatBytes(size)}");
                    }
                    if (largeFiles.Count > 10)
                        DebugLogger.Log($"  ... and {largeFiles.Count - 10} more");
                }

                // Analyze by extension
                var byExtension = supportedFiles.GroupBy(f => Path.GetExtension(f).ToLowerInvariant())
                                               .Select(g => new { Ext = g.Key, Count = g.Count(), Size = g.Sum(f => new FileInfo(f).Length) })
                                               .OrderByDescending(x => x.Size);

                DebugLogger.Log("BREAKDOWN BY EXTENSION:");
                foreach (var ext in byExtension)
                {
                    DebugLogger.Log($"  {ext.Ext}: {ext.Count} files, {FormatBytes(ext.Size)}");
                }

                // Recommendations
                DebugLogger.Log("RECOMMENDATIONS:");
                if (supportedFiles.Count > 10000)
                {
                    DebugLogger.Log("  ⚠️  Very large dataset (>10k files). Consider:");
                    DebugLogger.Log("     - Using file size limits");
                    DebugLogger.Log("     - Indexing in smaller batches");
                    DebugLogger.Log("     - Using the AmandaMap extraction instead of full indexing");
                }
                
                if (largeFiles.Count > 0)
                {
                    DebugLogger.Log("  ⚠️  Large files detected. Consider:");
                    DebugLogger.Log("     - Skipping files > 10MB");
                    DebugLogger.Log("     - Using streaming for large files");
                }

                DebugLogger.Log("  💡  For AmandaMap extraction, use 'Extract AmandaMap Entries' instead of full indexing");
                DebugLogger.Log("  💡  Full indexing is better for general search, AmandaMap extraction is optimized for your use case");

            }
            catch (Exception ex)
            {
                DebugLogger.Log($"ERROR analyzing folder: {ex.Message}");
            }
        }

        private static string FormatBytes(long bytes)
        {
            string[] suffixes = { "B", "KB", "MB", "GB" };
            int counter = 0;
            decimal number = bytes;
            while (Math.Round(number / 1024) >= 1)
            {
                number /= 1024;
                counter++;
            }
            return $"{number:n1} {suffixes[counter]}";
        }
    }
} 
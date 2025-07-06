using System;
using System.IO;

namespace GPTExporterIndexerAvalonia.Services
{
    /// <summary>
    /// A simple static logger to write debug messages to a file.
    /// </summary>
    public static class DebugLogger
    {
        // The log file will be created in the application's base directory (e.g., the 'bin/Debug' folder).
        private static readonly string LogPath = Path.Combine(AppContext.BaseDirectory, "debuglog.txt");
        private static readonly object _lock = new object();

        /// <summary>
        /// Writes a message to the debug log file.
        /// </summary>
        /// <param name="message">The message to log.</param>
        public static void Log(string message)
        {
            try
            {
                lock (_lock)
                {
                    // Append text to the file, creating it if it doesn't exist.
                    File.AppendAllText(LogPath, $"{DateTime.Now:yyyy-MM-dd HH:mm:ss.fff} - {message}{Environment.NewLine}");
                }
            }
            catch (Exception ex)
            {
                // To avoid the logger itself crashing the app, we can write to the debug console as a fallback.
                System.Diagnostics.Debug.WriteLine($"Failed to write to log file: {ex.Message}");
            }
        }
    }
}
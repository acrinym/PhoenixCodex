using System;
using System.IO;

namespace CodexEngine.Services
{
    /// <summary>
    /// A simple static logger to write debug messages to a file.
    /// </summary>
    public static class DebugLogger
    {
        private static readonly string LogPath = Path.Combine(AppContext.BaseDirectory, "debuglog.txt");
        private static readonly object _lock = new object();

        public static void Log(string message)
        {
            try
            {
                lock (_lock)
                {
                    File.AppendAllText(LogPath, $"{DateTime.Now:yyyy-MM-dd HH:mm:ss.fff} - {message}{Environment.NewLine}");
                }
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Failed to write to log file: {ex.Message}");
            }
        }
    }
}

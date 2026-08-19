// FILE: GPTExporterIndexerAvalonia/Program.cs
// REFACTORED
using Avalonia;
using Avalonia.ReactiveUI;
using System;
using Avalonia.WebView.Desktop;
using GPTExporterIndexerAvalonia.Services;

namespace GPTExporterIndexerAvalonia;

internal class Program
{
    // Initialization code. Don't use any Avalonia, third-party APIs or any
    // SynchronizationContext-reliant code before AppMain is called: things aren't initialized
    // yet and stuff might break.
    [STAThread]
    public static void Main(string[] args)
    {
        try // <-- ADD THIS
        {
            // This is the original line, now wrapped in the try block
            BuildAvaloniaApp()
                .StartWithClassicDesktopLifetime(args);
        }
        catch (Exception ex) // <-- ADD THIS CATCH BLOCK
        {
            // This will now catch the crash and print the full error to the console
            DebugLogger.Log(ex.ToString());
            Console.WriteLine("A FATAL ERROR OCCURRED:");
            Console.WriteLine(ex.ToString());
            Console.WriteLine("\nPress Enter to close...");
            Console.ReadLine(); // This keeps the console window open
        }
    }

    // Avalonia configuration, don't remove; also used by visual designer.
    public static AppBuilder BuildAvaloniaApp()
        => AppBuilder.Configure<App>()
            .UsePlatformDetect()
            .LogToTrace()
            .UseReactiveUI()
            .UseDesktopWebView();
}
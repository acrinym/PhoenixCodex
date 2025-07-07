using Avalonia;
using Avalonia.Controls.ApplicationLifetimes;
using Avalonia.Markup.Xaml;
using CommunityToolkit.Mvvm.Messaging;
using CodexEngine.ExportEngine.Renderers;
using GPTExporterIndexerAvalonia.Services;
using GPTExporterIndexerAvalonia.ViewModels;
using GPTExporterIndexerAvalonia.Views;
using GPTExporterIndexerAvalonia.Views.Yaml;
using Microsoft.Extensions.DependencyInjection;
using System;
using CodexEngine.Parsing;
using Avalonia.Threading; // <-- ADD THIS USING DIRECTIVE

namespace GPTExporterIndexerAvalonia;

public partial class App : Application
{
    public new static App Current => (App)Application.Current!;
    public IServiceProvider Services { get; private set; } = null!;
    
    public override void Initialize()
    {
        DebugLogger.Log("==================================================");
        DebugLogger.Log("Application Initializing...");
        AvaloniaXamlLoader.Load(this);
    }

    public override void OnFrameworkInitializationCompleted()
    {
        DebugLogger.Log("Framework initialization starting.");
        Services = ConfigureServices();
        if (ApplicationLifetime is IClassicDesktopStyleApplicationLifetime desktop)
        {
            DebugLogger.Log("Application lifetime is IClassicDesktopStyleApplicationLifetime.");
            desktop.MainWindow = new MainWindow
            {
                DataContext = Services.GetRequiredService<MainWindowViewModel>()
            };
            DebugLogger.Log("MainWindow created and DataContext set.");
        }

        base.OnFrameworkInitializationCompleted();
        DebugLogger.Log("Framework initialization completed.");

        // --- ADD THIS GLOBAL EXCEPTION HANDLER ---
        // This will catch any unhandled exceptions on the UI thread,
        // log them, and prevent the app from immediately closing.
        var dispatcher = Dispatcher.UIThread;
        dispatcher.UnhandledException += (sender, args) =>
        {
            // Log the detailed exception to our file
            DebugLogger.Log($"\n!!! FATAL UI CRASH !!!\n{args.Exception}\n");
            // Mark the exception as "handled" to prevent the app from closing instantly.
            // This is for debugging purposes to allow us to see the error.
            args.SetHandled(true);
        };
    }

    private static IServiceProvider ConfigureServices()
    {
        DebugLogger.Log("Configuring services.");
        var services = new ServiceCollection();

        // Register Services
        services.AddSingleton<IMessenger>(WeakReferenceMessenger.Default);
        services.AddSingleton<IIndexingService, IndexingService>();
        services.AddSingleton<ISearchService, SearchService>();
        services.AddSingleton<IFileParsingService, FileParsingService>();
        services.AddSingleton<IExportService, ExportService>();
        services.AddSingleton<IDialogService, DialogService>();
        services.AddSingleton<IEntryParserService, EntryParserService>();

        // Register Renderers
        services.AddSingleton<IMarkdownRenderer, MarkdownRenderer>();
        
        // Register ViewModels
        services.AddSingleton<GrimoireManagerViewModel>();
        services.AddTransient<TimelineViewModel>();
        services.AddTransient<AmandaMapViewModel>();
        services.AddTransient<ChatLogViewModel>();
        services.AddTransient<RitualBuilderViewModel>();
        services.AddTransient<TagMapViewModel>();
        services.AddTransient<YamlInterpreterViewModel>();
        services.AddTransient<MainWindowViewModel>();
        
        // Register Views (for the ViewLocator)
        services.AddTransient<MainWindow>();
        services.AddTransient<GrimoireManagerView>();
        services.AddTransient<TimelineView>();
        services.AddTransient<AmandaMapView>();
        services.AddTransient<TagMapView>();
        services.AddTransient<YamlInterpreterView>();
        services.AddTransient<ChatLogView>();
        services.AddTransient<RitualBuilderView>();

        return services.BuildServiceProvider();
    }
}
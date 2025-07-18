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
using CodexEngine.Parsing; // You may need to add this using statement

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
        
        // Initialize the ControlPanel for dynamic theming
        var controlPanel = GPTExporterIndexerAvalonia.Services.ControlPanel.Instance;
        DebugLogger.Log("ControlPanel initialized for dynamic theming.");
    }

    public override void OnFrameworkInitializationCompleted()
    {
        DebugLogger.Log("Framework initialization starting.");
        Services = ConfigureServices();
        
        // Load settings on startup
        var settingsService = Services.GetRequiredService<ISettingsService>();
        _ = Task.Run(async () => await settingsService.LoadSettingsAsync());
        
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
        services.AddSingleton<ISettingsService, SettingsService>();
        // THIS IS THE REQUIRED LINE TO FIX THE CRASH
        services.AddSingleton<IEntryParserService, EntryParserService>();

        // Register Renderers
        services.AddSingleton<IMarkdownRenderer, MarkdownRenderer>();

        // Register ViewModels
        services.AddSingleton<GrimoireManagerViewModel>();
        services.AddTransient<TimelineViewModel>();
        services.AddTransient<AmandaMapViewModel>();
        services.AddTransient<AmandaMapTimelineViewModel>();
        services.AddTransient<ChatLogViewModel>();
        services.AddTransient<RitualBuilderViewModel>();
        services.AddTransient<TagMapViewModel>();
        services.AddTransient<YamlInterpreterViewModel>();
        services.AddTransient<SettingsViewModel>();
        services.AddTransient<MainWindowViewModel>();

        // Register Views (for the ViewLocator)
        services.AddTransient<MainWindow>();
        services.AddTransient<GrimoireManagerView>();
        services.AddTransient<TimelineView>();
        services.AddTransient<AmandaMapView>();
        services.AddTransient<AmandaMapTimelineView>();
        services.AddTransient<TagMapView>();
        services.AddTransient<YamlInterpreterView>();
        services.AddTransient<ChatLogView>();
        services.AddTransient<RitualBuilderView>();
        services.AddTransient<SettingsView>();
        services.AddTransient<ThemeSettingsView>();

        return services.BuildServiceProvider();
    }
}

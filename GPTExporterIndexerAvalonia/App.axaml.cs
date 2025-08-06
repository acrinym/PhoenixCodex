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
        
        try
        {
            DebugLogger.Log("1. Configuring services...");
            Services = ConfigureServices();
            DebugLogger.Log("2. Services configured successfully.");
            
            DebugLogger.Log("3. Getting settings service...");
            var settingsService = Services.GetRequiredService<ISettingsService>();
            DebugLogger.Log("4. Settings service obtained.");
            
            DebugLogger.Log("5. Starting settings load in background...");
            // Load settings on startup
            _ = Task.Run(async () => await settingsService.LoadSettingsAsync());
            DebugLogger.Log("6. Settings load started in background.");
            
            DebugLogger.Log("7. Checking application lifetime...");
            if (ApplicationLifetime is IClassicDesktopStyleApplicationLifetime desktop)
            {
                DebugLogger.Log("8. Application lifetime is IClassicDesktopStyleApplicationLifetime.");
                
                DebugLogger.Log("9. Creating MainWindow...");
                var mainWindow = new MainWindow();
                DebugLogger.Log("10. MainWindow created.");
                
                DebugLogger.Log("11. Getting MainWindowViewModel from DI...");
                var mainWindowViewModel = Services.GetRequiredService<MainWindowViewModel>();
                DebugLogger.Log("12. MainWindowViewModel obtained from DI.");
                
                DebugLogger.Log("13. Setting DataContext...");
                mainWindow.DataContext = mainWindowViewModel;
                DebugLogger.Log("14. DataContext set.");
                
                DebugLogger.Log("15. Setting MainWindow...");
                desktop.MainWindow = mainWindow;
                DebugLogger.Log("16. MainWindow set.");
            }
            else
            {
                DebugLogger.Log("ERROR: ApplicationLifetime is not IClassicDesktopStyleApplicationLifetime");
            }

            DebugLogger.Log("17. Calling base.OnFrameworkInitializationCompleted()...");
            base.OnFrameworkInitializationCompleted();
            DebugLogger.Log("18. Framework initialization completed.");
        }
        catch (Exception ex)
        {
            DebugLogger.Log($"ERROR in OnFrameworkInitializationCompleted: {ex.Message}");
            DebugLogger.Log($"Stack trace: {ex.StackTrace}");
            throw;
        }
    }

    private static IServiceProvider ConfigureServices()
    {
        DebugLogger.Log("=== ConfigureServices START ===");
        var services = new ServiceCollection();

        try
        {
            DebugLogger.Log("1. Registering Services...");
            // Register Services
            services.AddSingleton<IMessenger>(WeakReferenceMessenger.Default);
            DebugLogger.Log("2. IMessenger registered.");
            services.AddSingleton<IIndexingService, IndexingService>();
            DebugLogger.Log("3. IIndexingService registered.");
            services.AddSingleton<ISearchService, SearchService>();
            DebugLogger.Log("4. ISearchService registered.");
            services.AddSingleton<IFileParsingService, FileParsingService>();
            DebugLogger.Log("5. IFileParsingService registered.");
            services.AddSingleton<IExportService, ExportService>();
            DebugLogger.Log("6. IExportService registered.");
            services.AddSingleton<IDialogService, DialogService>();
            DebugLogger.Log("7. IDialogService registered.");
            services.AddSingleton<ISettingsService, SettingsService>();
            DebugLogger.Log("8. ISettingsService registered.");
            
            // Register ProgressService with its required Action parameters
            services.AddSingleton<Action<double, string, string>>(provider => (percentage, message, details) => { });
            services.AddSingleton<Action<bool>>(provider => (isRunning) => { });
            services.AddSingleton<Action<string>>(provider => (error) => { });
            services.AddSingleton<IProgressService, ProgressService>();
            DebugLogger.Log("9. IProgressService registered.");
            
            // THIS IS THE REQUIRED LINE TO FIX THE CRASH
            services.AddSingleton<IEntryParserService, EntryParserService>();
            DebugLogger.Log("10. IEntryParserService registered.");
            
            // Register ChatFileManager
            services.AddSingleton<CodexEngine.Services.ChatFileManager>();
            DebugLogger.Log("11. ChatFileManager registered.");

            DebugLogger.Log("12. Registering Renderers...");
            // Register Renderers
            services.AddSingleton<IMarkdownRenderer, MarkdownRenderer>();
            DebugLogger.Log("13. IMarkdownRenderer registered.");

            DebugLogger.Log("14. Registering ViewModels...");
            // Register ViewModels
            services.AddSingleton<GrimoireManagerViewModel>();
            DebugLogger.Log("15. GrimoireManagerViewModel registered.");
            services.AddTransient<TimelineViewModel>();
            DebugLogger.Log("16. TimelineViewModel registered.");
            services.AddTransient<AmandaMapViewModel>(provider => 
                new AmandaMapViewModel(
                    provider.GetRequiredService<IMessenger>(),
                    provider.GetRequiredService<IDialogService>(),
                    provider.GetRequiredService<ISettingsService>()));
            DebugLogger.Log("17. AmandaMapViewModel registered.");
            services.AddTransient<PhoenixCodexViewModel>(provider => 
                new PhoenixCodexViewModel(
                    provider.GetRequiredService<IMessenger>(),
                    provider.GetRequiredService<IDialogService>(),
                    provider.GetRequiredService<ISettingsService>()));
            DebugLogger.Log("18. PhoenixCodexViewModel registered.");
            services.AddTransient<AmandaMapTimelineViewModel>(provider => 
                new AmandaMapTimelineViewModel(
                    provider.GetRequiredService<IMessenger>(),
                    provider.GetRequiredService<AmandaMapViewModel>()));
            DebugLogger.Log("19. AmandaMapTimelineViewModel registered.");
            services.AddTransient<PhoenixCodexTimelineViewModel>(provider => 
                new PhoenixCodexTimelineViewModel(
                    provider.GetRequiredService<IMessenger>(),
                    provider.GetRequiredService<PhoenixCodexViewModel>()));
            DebugLogger.Log("20. PhoenixCodexTimelineViewModel registered.");
            services.AddTransient<ChatLogViewModel>();
            DebugLogger.Log("21. ChatLogViewModel registered.");
            services.AddTransient<RitualBuilderViewModel>();
            DebugLogger.Log("22. RitualBuilderViewModel registered.");
            services.AddTransient<TagMapViewModel>();
            DebugLogger.Log("23. TagMapViewModel registered.");
            services.AddTransient<YamlInterpreterViewModel>();
            DebugLogger.Log("24. YamlInterpreterViewModel registered.");
            services.AddTransient<SettingsViewModel>();
            DebugLogger.Log("25. SettingsViewModel registered.");
            services.AddTransient<ChatFileManagementViewModel>(provider => 
                new ChatFileManagementViewModel(
                    provider.GetRequiredService<IDialogService>(),
                    provider.GetRequiredService<CodexEngine.Services.ChatFileManager>()));
            DebugLogger.Log("26. ChatFileManagementViewModel registered.");
            services.AddTransient<MainWindowViewModel>();
            DebugLogger.Log("27. MainWindowViewModel registered.");

            DebugLogger.Log("28. Registering Views...");
            // Register Views (for the ViewLocator)
            services.AddTransient<MainWindow>();
            DebugLogger.Log("28. MainWindow registered.");
            services.AddTransient<GrimoireManagerView>();
            DebugLogger.Log("29. GrimoireManagerView registered.");
            services.AddTransient<TimelineView>();
            DebugLogger.Log("30. TimelineView registered.");
            services.AddTransient<AmandaMapView>();
            DebugLogger.Log("31. AmandaMapView registered.");
            services.AddTransient<AmandaMapTimelineView>();
            DebugLogger.Log("32. AmandaMapTimelineView registered.");
            services.AddTransient<PhoenixCodexTimelineView>();
            DebugLogger.Log("33. PhoenixCodexTimelineView registered.");
            services.AddTransient<TagMapView>();
            DebugLogger.Log("34. TagMapView registered.");
            services.AddTransient<YamlInterpreterView>();
            DebugLogger.Log("35. YamlInterpreterView registered.");
            services.AddTransient<ChatLogView>();
            DebugLogger.Log("36. ChatLogView registered.");
            services.AddTransient<RitualBuilderView>();
            DebugLogger.Log("37. RitualBuilderView registered.");
            services.AddTransient<SettingsView>();
            DebugLogger.Log("38. SettingsView registered.");
            services.AddTransient<ThemeSettingsView>();
            DebugLogger.Log("39. ThemeSettingsView registered.");
            services.AddTransient<ChatFileManagementView>();
            DebugLogger.Log("40. ChatFileManagementView registered.");

            DebugLogger.Log("41. Building service provider...");
            var serviceProvider = services.BuildServiceProvider();
            DebugLogger.Log("42. Service provider built successfully.");
            DebugLogger.Log("=== ConfigureServices END ===");
            return serviceProvider;
        }
        catch (Exception ex)
        {
            DebugLogger.Log($"ERROR in ConfigureServices: {ex.Message}");
            DebugLogger.Log($"Stack trace: {ex.StackTrace}");
            throw;
        }
    }
}

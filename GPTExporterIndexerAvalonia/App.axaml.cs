using Avalonia;
using Avalonia.Controls.ApplicationLifetimes;
using Avalonia.Markup.Xaml;
using CommunityToolkit.Mvvm.Messaging;
using CodexEngine.ExportEngine.Renderers;
using GPTExporterIndexerAvalonia.Services;
using GPTExporterIndexerAvalonia.ViewModels;
using GPTExporterIndexerAvalonia.Views; // New using for Views
using Microsoft.Extensions.DependencyInjection;
using System;

namespace GPTExporterIndexerAvalonia;

public partial class App : Application
{
    public new static App Current => (App)Application.Current!;

    public IServiceProvider Services { get; private set; } = null!;

    public override void Initialize()
    {
        AvaloniaXamlLoader.Load(this);
    }


    public override void OnFrameworkInitializationCompleted()
    {
        Services = ConfigureServices();

        if (ApplicationLifetime is IClassicDesktopStyleApplicationLifetime desktop)
        {
            // We now create the MainWindow directly, its DataContext will be set by the ViewLocator
            desktop.MainWindow = new MainWindow
            {
                // The main DataContext is now the MainWindowViewModel itself.
                DataContext = Services.GetRequiredService<MainWindowViewModel>()
            };
        }

        base.OnFrameworkInitializationCompleted();
    }

    private static IServiceProvider ConfigureServices()
    {
        var services = new ServiceCollection();

        // Register Services
        services.AddSingleton<IMessenger>(WeakReferenceMessenger.Default);
        services.AddSingleton<IIndexingService, IndexingService>();
        services.AddSingleton<ISearchService, SearchService>();
        services.AddSingleton<IFileParsingService, FileParsingService>();
        services.AddSingleton<IExportService, ExportService>();

        // FIXED: Register the DialogService so it can be injected.
        services.AddSingleton<IDialogService, DialogService>();

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

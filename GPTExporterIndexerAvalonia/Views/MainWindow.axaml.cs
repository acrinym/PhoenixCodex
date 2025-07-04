using Avalonia.Controls;
using Avalonia.Markup.Xaml;
using Avalonia.Interactivity;
using GPTExporterIndexerAvalonia.ViewModels;

namespace GPTExporterIndexerAvalonia.Views;

public partial class MainWindow : Window
{
    public MainWindow()
    {
        InitializeComponent();
    }

    private void InitializeComponent() => AvaloniaXamlLoader.Load(this);

    private async void OnOpenDocument(object? sender, RoutedEventArgs e)
    {
        var dlg = new OpenFileDialog();
        dlg.Filters.Add(new FileDialogFilter { Name = "Documents", Extensions = { "pdf", "md", "txt" } });
        var result = await dlg.ShowAsync(this);
        if (result?.Length > 0 && DataContext is MainWindowViewModel vm)
        {
            vm.DocumentPath = result[0];
            vm.LoadDocumentCommand.Execute(null);
        }
    }

    private void OnExit(object? sender, RoutedEventArgs e) => Close();
}

using Avalonia.Controls;
using Avalonia.Markup.Xaml;
using Avalonia.Interactivity;
using GPTExporterIndexerAvalonia.ViewModels;

namespace GPTExporterIndexerAvalonia.Views;

public partial class TagMapView : UserControl
{
    public TagMapView()
    {
        InitializeComponent();
    }

    private void InitializeComponent()
    {
        AvaloniaXamlLoader.Load(this);
    }

    private async void OnBrowse(object? sender, RoutedEventArgs e)
    {
        var dlg = new OpenFileDialog();
        dlg.Filters.Add(new FileDialogFilter { Name = "TagMap", Extensions = { "csv", "xlsx" } });
        var window = this.GetVisualRoot() as Window;
        var result = await dlg.ShowAsync(window);
        if (result?.Length > 0 && DataContext is TagMapViewModel vm)
        {
            vm.FilePath = result[0];
            vm.LoadCommand.Execute(null);
        }
    }
}


using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using GPTExporterIndexerAvalonia.Helpers;
using System.Collections.ObjectModel;

namespace GPTExporterIndexerAvalonia.ViewModels;

public partial class MainWindowViewModel : ObservableObject
{
    [ObservableProperty]
    private string _indexFolder = string.Empty;

    [ObservableProperty]
    private string _status = string.Empty;

    [ObservableProperty]
    private string _query = string.Empty;

    public ObservableCollection<string> Results { get; } = new();

    [RelayCommand]
    private void BuildIndex()
    {
        if (string.IsNullOrWhiteSpace(IndexFolder))
        {
            Status = "Select a folder";
            return;
        }
        var indexPath = System.IO.Path.Combine(IndexFolder, "index.json");
        Status = "Building...";
        AdvancedIndexer.BuildIndex(IndexFolder, indexPath);
        Status = $"Index built at {indexPath}";
    }

    [RelayCommand]
    private void Search()
    {
        Results.Clear();
        var indexPath = System.IO.Path.Combine(IndexFolder, "index.json");
        foreach (var result in AdvancedIndexer.Search(indexPath, Query))
        {
            Results.Add($"{result.File}: {string.Join(" | ", result.Snippets)}");
        }
    }
}

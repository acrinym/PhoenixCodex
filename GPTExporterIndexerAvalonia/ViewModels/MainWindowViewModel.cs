using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using GPTExporterIndexerAvalonia.Helpers;
using System.Collections.ObjectModel;
using System.Diagnostics;

namespace GPTExporterIndexerAvalonia.ViewModels;

public partial class MainWindowViewModel : ObservableObject
{
    [ObservableProperty]
    private string _indexFolder = string.Empty;

    [ObservableProperty]
    private string _status = string.Empty;

    [ObservableProperty]
    private string _query = string.Empty;

    [ObservableProperty]
    private bool _caseSensitive;

    [ObservableProperty]
    private bool _useFuzzy;

    [ObservableProperty]
    private bool _useAnd = true;

    [ObservableProperty]
    private int _contextLines = 1;

    [ObservableProperty]
    private SearchResult? _selectedResult;

    public ObservableCollection<SearchResult> Results { get; } = new();

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
        var opts = new SearchOptions
        {
            CaseSensitive = CaseSensitive,
            UseFuzzy = UseFuzzy,
            UseAnd = UseAnd,
            ContextLines = ContextLines
        };
        foreach (var result in AdvancedIndexer.Search(indexPath, Query, opts))
        {
            Results.Add(result);
        }
    }

    [RelayCommand]
    private void OpenSelected()
    {
        if (SelectedResult == null)
            return;
        var path = System.IO.Path.Combine(IndexFolder, SelectedResult.File);
        try
        {
            // UseShellExecute is required to open the file with the default application
            Process.Start(new ProcessStartInfo(path) { UseShellExecute = true });
        }
        catch { }
    }
}
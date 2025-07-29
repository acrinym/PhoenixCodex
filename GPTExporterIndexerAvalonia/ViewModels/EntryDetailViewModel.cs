using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using CodexEngine.PhoenixEntries;
using CodexEngine.AmandaMapCore.Models;
using System;
using System.Collections.ObjectModel;
using System.Collections.Generic;
using GPTExporterIndexerAvalonia.Services;

namespace GPTExporterIndexerAvalonia.ViewModels;

public partial class EntryDetailViewModel : ObservableObject
{
    [ObservableProperty]
    private string _title = string.Empty;

    [ObservableProperty]
    private DateTime _date = DateTime.Now;

    [ObservableProperty]
    private string _description = string.Empty;

    public FieldEncoding FieldEncoding { get; set; } = new();

    public ObservableCollection<string> Tags { get; } = new();

    [ObservableProperty]
    private EntryStatus _status;

    public IEnumerable<EntryStatus> StatusOptions => Enum.GetValues<EntryStatus>();

    [ObservableProperty]
    private bool _mirrorToAmandaMap;

    [ObservableProperty]
    private bool _visibleToAmanda;

    [ObservableProperty]
    private string? _sourceFile;

    public EntryBase? BoundEntry { get; private set; }
    public NumberedMapEntry? BoundAmandaEntry { get; private set; }

    public void Load(EntryBase entry)
    {
        BoundEntry = entry;
        Title = entry.Title;
        Date = entry.Date;
        Description = entry.Description;
        FieldEncoding = entry.FieldEncoding;
        Tags.Clear();
        foreach (var t in entry.Tags)
            Tags.Add(t);
        Status = entry.Status;
        MirrorToAmandaMap = entry.MirrorToAmandaMap;
        VisibleToAmanda = entry.VisibleToAmanda;
        SourceFile = null;
    }

    public void Load(NumberedMapEntry entry)
    {
        BoundAmandaEntry = entry;
        Title = entry.Title;
        Date = entry.Date;
        Description = entry.RawContent;
        FieldEncoding = new();
        Tags.Clear();
        Status = EntryStatus.Unknown;
        MirrorToAmandaMap = false;
        VisibleToAmanda = false;
        SourceFile = entry.SourceFile;

    }

    [RelayCommand]
    private void AddTag()
    {
        Tags.Add("new tag");
    }

    [RelayCommand]
    private void RemoveTag(string tag)
    {
        Tags.Remove(tag);
    }

    [RelayCommand]
    private void OpenSourceFile()
    {
        if (string.IsNullOrWhiteSpace(SourceFile) || !System.IO.File.Exists(SourceFile))
            return;
        try
        {
            System.Diagnostics.Process.Start(new System.Diagnostics.ProcessStartInfo(SourceFile!) { UseShellExecute = true });
        }
        catch (Exception ex)
        {
            DebugLogger.Log($"Failed to open source file: {ex.Message}");
        }
    }

    [RelayCommand]
    private async Task CopySourcePathAsync()
    {
        if (!string.IsNullOrWhiteSpace(SourceFile))
        {
            try
            {
                // For now, just log the path since clipboard access is complex in Avalonia
                DebugLogger.Log($"Source file path: {SourceFile}");
            }
            catch (Exception ex)
            {
                DebugLogger.Log($"Failed to copy to clipboard: {ex.Message}");
            }
        }
    }

    [RelayCommand]
    private void Save()
    {
        if (BoundEntry is not null)
        {
            BoundEntry.Title = Title;
            BoundEntry.Date = Date;
            BoundEntry.Description = Description;
            BoundEntry.FieldEncoding = FieldEncoding;
            BoundEntry.Tags = new List<string>(Tags);
            BoundEntry.Status = Status;
            BoundEntry.MirrorToAmandaMap = MirrorToAmandaMap;
            BoundEntry.VisibleToAmanda = VisibleToAmanda;
        }
        if (BoundAmandaEntry is not null)
        {
            BoundAmandaEntry.Title = Title;
            BoundAmandaEntry.Date = Date;
            BoundAmandaEntry.RawContent = Description;
        }
    }
}

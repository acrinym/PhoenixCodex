using CommunityToolkit.Mvvm.ComponentModel;
using System;

namespace GPTExporterIndexerAvalonia.ViewModels;

public partial class TimelineViewModel : ObservableObject
{
    [ObservableProperty]
    private DateTime _selectedDate = DateTime.Today;
}

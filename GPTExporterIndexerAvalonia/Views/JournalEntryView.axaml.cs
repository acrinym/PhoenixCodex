using Avalonia;
using Avalonia.Controls;
using Avalonia.Markup.Xaml;
using GPTExporterIndexerAvalonia.ViewModels;

namespace GPTExporterIndexerAvalonia.Views;

public partial class JournalEntryView : UserControl
{
    public JournalEntryView()
    {
        InitializeComponent();
    }

    private void InitializeComponent()
    {
        AvaloniaXamlLoader.Load(this);
    }
}

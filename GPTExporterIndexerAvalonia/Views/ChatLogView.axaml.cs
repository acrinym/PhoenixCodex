using Avalonia.Controls;
using Avalonia.Markup.Xaml;

namespace GPTExporterIndexerAvalonia.Views;

public partial class ChatLogView : UserControl
{
    public ChatLogView()
    {
        InitializeComponent();
    }

    private void InitializeComponent()
    {
        AvaloniaXamlLoader.Load(this);
    }
}

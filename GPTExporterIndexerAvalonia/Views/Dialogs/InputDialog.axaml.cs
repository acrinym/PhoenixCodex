using Avalonia.Controls;
using Avalonia.Interactivity;
using Avalonia.Markup.Xaml;

namespace GPTExporterIndexerAvalonia.Views.Dialogs;

public partial class InputDialog : Window
{
    public InputDialog()
    {
        InitializeComponent();
    }

    public InputDialog(string title, string prompt, string defaultText = "") : this()
    {
        Title = title;
        this.FindControl<TextBlock>("PromptBlock").Text = prompt;
        this.FindControl<TextBox>("InputBox").Text = defaultText;
    }

    private void InitializeComponent()
    {
        AvaloniaXamlLoader.Load(this);
    }

    private void OnOk(object? sender, RoutedEventArgs e)
    {
        Close(this.FindControl<TextBox>("InputBox").Text);
    }

    private void OnCancel(object? sender, RoutedEventArgs e)
    {
        Close(null);
    }
}

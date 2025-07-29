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
        var promptBlock = this.FindControl<TextBlock>("PromptBlock");
        var inputBox = this.FindControl<TextBox>("InputBox");
        
        if (promptBlock != null) promptBlock.Text = prompt;
        if (inputBox != null) inputBox.Text = defaultText;
    }

    private void InitializeComponent()
    {
        AvaloniaXamlLoader.Load(this);
    }

    private void OnOk(object? sender, RoutedEventArgs e)
    {
        var inputBox = this.FindControl<TextBox>("InputBox");
        Close(inputBox?.Text);
    }

    private void OnCancel(object? sender, RoutedEventArgs e)
    {
        Close(null);
    }
}

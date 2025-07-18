using Avalonia;
using Avalonia.Controls;
using Avalonia.Markup.Xaml;

namespace GPTExporterIndexerAvalonia.Views.Controls;

public partial class SelectableTextBlock : UserControl
{
    public static readonly StyledProperty<string?> TextProperty =
        AvaloniaProperty.Register<SelectableTextBlock, string?>(nameof(Text));

    private TextBox? _textBox;

    public string? Text
    {
        get => GetValue(TextProperty);
        set => SetValue(TextProperty, value);
    }

    public SelectableTextBlock()
    {
        InitializeComponent();
        _textBox = this.FindControl<TextBox>("PART_TextBox");
        
        // Subscribe to property changes
        this.GetObservable(TextProperty).Subscribe(OnTextChanged);
    }

    private void InitializeComponent()
    {
        AvaloniaXamlLoader.Load(this);
    }

    private void OnTextChanged(string? text)
    {
        if (_textBox != null)
        {
            _textBox.Text = text ?? string.Empty;
        }
    }

    /// <summary>
    /// Gets the selected text from the control
    /// </summary>
    public string? GetSelectedText()
    {
        return _textBox?.SelectedText;
    }

    /// <summary>
    /// Selects all text in the control
    /// </summary>
    public void SelectAll()
    {
        _textBox?.SelectAll();
    }

    /// <summary>
    /// Clears the text selection
    /// </summary>
    public void ClearSelection()
    {
        if (_textBox != null)
        {
            _textBox.SelectionStart = 0;
            _textBox.SelectionEnd = 0;
        }
    }
} 
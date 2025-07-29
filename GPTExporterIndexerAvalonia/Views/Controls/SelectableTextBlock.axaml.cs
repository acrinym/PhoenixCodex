using Avalonia;
using Avalonia.Controls;
using Avalonia.Markup.Xaml;
using Avalonia.Interactivity;
using System;
using System.Diagnostics;

namespace GPTExporterIndexerAvalonia.Views.Controls
{
    public partial class SelectableTextBlock : UserControl
    {
        public static readonly DirectProperty<SelectableTextBlock, string> TextProperty =
            AvaloniaProperty.RegisterDirect<SelectableTextBlock, string>(
                nameof(Text),
                o => o.Text,
                (o, v) => o.Text = v);

        private string _text = string.Empty;
        private const int MaxDisplayLength = 50000; // Limit display to 50KB to prevent UI freezing

        public string Text
        {
            get => _text;
            set 
            {
                // Truncate very large text to prevent UI freezing
                var displayText = value?.Length > MaxDisplayLength 
                    ? value.Substring(0, MaxDisplayLength) + "\n\n[Content truncated for performance - use search to find specific content]"
                    : value ?? string.Empty;
                    
                SetAndRaise(TextProperty, ref _text, displayText);
            }
        }

        public SelectableTextBlock()
        {
            InitializeComponent();
            
            // Set up button event handlers
            if (this.FindControl<Button>("CopyAllButton") is Button copyAllButton)
            {
                copyAllButton.Click += CopyAllButton_Click;
            }
            
            if (this.FindControl<Button>("CopySelectionButton") is Button copySelectionButton)
            {
                copySelectionButton.Click += CopySelectionButton_Click;
            }
        }

        private async void CopyAllButton_Click(object? sender, RoutedEventArgs e)
        {
            try
            {
                var clipboard = TopLevel.GetTopLevel(this)?.Clipboard;
                if (clipboard != null && !string.IsNullOrEmpty(_text))
                {
                    await clipboard.SetTextAsync(_text);
                }
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"Copy all error: {ex.Message}");
            }
        }

        private async void CopySelectionButton_Click(object? sender, RoutedEventArgs e)
        {
            try
            {
                // For now, just copy all since TextBlock doesn't support selection
                // In the future, we could implement a more sophisticated selection system
                var clipboard = TopLevel.GetTopLevel(this)?.Clipboard;
                if (clipboard != null && !string.IsNullOrEmpty(_text))
                {
                    await clipboard.SetTextAsync(_text);
                }
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"Copy selection error: {ex.Message}");
            }
        }
    }
} 
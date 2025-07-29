using Avalonia;
using Avalonia.Controls;
using Avalonia.Markup.Xaml;
using Avalonia.Input;
using Avalonia.Interactivity;
using System;

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

        public string Text
        {
            get => _text;
            set => SetAndRaise(TextProperty, ref _text, value);
        }

        public SelectableTextBlock()
        {
            InitializeComponent();
        }

        private void InitializeComponent()
        {
            AvaloniaXamlLoader.Load(this);
        }

        protected override void OnLoaded(RoutedEventArgs e)
        {
            base.OnLoaded(e);
            
            // Set up context menu handlers
            if (this.FindControl<TextBox>("TextBlock") is TextBox textBox)
            {
                textBox.Focus();
                
                // Set up context menu handlers
                if (textBox.ContextMenu is ContextMenu contextMenu)
                {
                    if (contextMenu.FindControl<MenuItem>("SelectAllMenuItem") is MenuItem selectAllItem)
                    {
                        selectAllItem.Click += (s, e) => textBox.SelectAll();
                    }
                    
                    if (contextMenu.FindControl<MenuItem>("CopyMenuItem") is MenuItem copyItem)
                    {
                        copyItem.Click += async (s, e) => 
                        {
                            if (!string.IsNullOrEmpty(textBox.Text))
                            {
                                try
                                {
                                    var clipboard = TopLevel.GetTopLevel(this)?.Clipboard;
                                    if (clipboard != null)
                                    {
                                        await clipboard.SetTextAsync(textBox.Text);
                                    }
                                }
                                catch (Exception ex)
                                {
                                    // Log or handle clipboard error
                                    System.Diagnostics.Debug.WriteLine($"Clipboard error: {ex.Message}");
                                }
                            }
                        };
                    }
                    
                    if (contextMenu.FindControl<MenuItem>("CopySelectionMenuItem") is MenuItem copySelectionItem)
                    {
                        copySelectionItem.Click += async (s, e) => 
                        {
                            if (!string.IsNullOrEmpty(textBox.SelectedText))
                            {
                                try
                                {
                                    var clipboard = TopLevel.GetTopLevel(this)?.Clipboard;
                                    if (clipboard != null)
                                    {
                                        await clipboard.SetTextAsync(textBox.SelectedText);
                                    }
                                }
                                catch (Exception ex)
                                {
                                    // Log or handle clipboard error
                                    System.Diagnostics.Debug.WriteLine($"Clipboard error: {ex.Message}");
                                }
                            }
                        };
                    }
                    
                    if (contextMenu.FindControl<MenuItem>("IncreaseFontSizeMenuItem") is MenuItem increaseFontItem)
                    {
                        increaseFontItem.Click += (s, e) => 
                        {
                            var currentSize = FontSize;
                            FontSize = Math.Min(currentSize + 1, 24);
                        };
                    }
                    
                    if (contextMenu.FindControl<MenuItem>("DecreaseFontSizeMenuItem") is MenuItem decreaseFontItem)
                    {
                        decreaseFontItem.Click += (s, e) => 
                        {
                            var currentSize = FontSize;
                            FontSize = Math.Max(currentSize - 1, 8);
                        };
                    }
                    
                    if (contextMenu.FindControl<MenuItem>("ResetFontSizeMenuItem") is MenuItem resetFontItem)
                    {
                        resetFontItem.Click += (s, e) => 
                        {
                            FontSize = 11;
                        };
                    }
                }
            }
        }

        protected override void OnPointerPressed(PointerPressedEventArgs e)
        {
            base.OnPointerPressed(e);
            
            // Ensure the TextBox gets focus when clicked
            if (this.FindControl<TextBox>("TextBlock") is TextBox textBox)
            {
                textBox.Focus();
            }
        }
    }
} 
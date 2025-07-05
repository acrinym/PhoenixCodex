using Avalonia;
using Avalonia.Controls;
using Avalonia.Markup.Xaml;
using GPTExporterIndexerAvalonia.Reading;
using DocumentFormat.OpenXml.Packaging;
using System.IO;
using VersOne.Epub;
using TheArtOfDev.HtmlRenderer.Avalonia;
using Avalonia.Media;
using System.Linq;
using System;
using System.Text; // Required for StringBuilder

namespace GPTExporterIndexerAvalonia.Views.Controls;

/// <summary>
/// A versatile UserControl for displaying various document types,
/// including PDF, DOCX, EPUB, Markdown, and JSON files.
/// </summary>
public partial class BookViewer : UserControl
{
    public static readonly StyledProperty<string?> FilePathProperty =
        AvaloniaProperty.Register<BookViewer, string?>(nameof(FilePath));

    /// <summary>
    /// Gets or sets the path to the file to be displayed.
    /// When this property is changed, the control automatically loads and renders the new file.
    /// </summary>
    public string? FilePath
    {
        get => GetValue(FilePathProperty);
        set => SetValue(FilePathProperty, value);
    }

    private readonly ContentControl _content;

    public BookViewer()
    {
        InitializeComponent();
        _content = this.FindControl<ContentControl>("PART_Content") 
            ?? throw new InvalidOperationException("Could not find PART_Content in the control template.");
            
        // Subscribe to changes on the FilePath property to automatically load files.
        this.GetObservable(FilePathProperty).Subscribe(LoadFile);
    }

    private void InitializeComponent()
    {
        AvaloniaXamlLoader.Load(this);
    }

    /// <summary>
    /// Main dispatcher method that loads a file based on its extension.
    /// </summary>
    private void LoadFile(string? path)
    {
        if (string.IsNullOrEmpty(path) || !File.Exists(path))
        {
            _content.Content = null;
            return;
        }

        var ext = Path.GetExtension(path).ToLowerInvariant();

        // Using a switch expression for a cleaner dispatch logic.
        _content.Content = ext switch
        {
            ".pdf" => CreatePdfView(path),
            ".docx" => CreateDocxView(path),
            ".epub" => CreateEpubView(path),
            ".md" => CreateTextView(path), // Markdown is treated as plain text for now
            ".json" => CreateTextView(path, useMonospace: true), // JSON benefits from monospaced font
            ".mobi" or _ => CreateUnsupportedView(ext), // .mobi is not supported
        };
    }

    /// <summary>
    /// Creates a view for displaying PDF files as a series of images.
    /// </summary>
    private Control CreatePdfView(string path)
    {
        try
        {
            var reader = new BookReader();
            reader.Load(path); // Assumes this class handles PDF reading
            var panel = new StackPanel();
            foreach (var bmp in reader.Pages)
            {
                panel.Children.Add(new Image
                {
                    Source = bmp,
                    Stretch = Stretch.Uniform,
                    Margin = new Thickness(0, 5)
                });
            }
            return new ScrollViewer { Content = panel };
        }
        catch (Exception ex)
        {
            return CreateErrorView("PDF", ex);
        }
    }

    /// <summary>
    /// Creates a view for displaying the text content of a .docx file.
    /// </summary>
    private Control CreateDocxView(string path)
    {
        try
        {
            using var doc = WordprocessingDocument.Open(path, false);
            var text = doc.MainDocumentPart?.Document.Body?.InnerText ?? "Could not read document body.";
            var textBlock = new TextBlock { Text = text, TextWrapping = TextWrapping.Wrap, Margin = new Thickness(5) };
            return new ScrollViewer { Content = textBlock };
        }
        catch (Exception ex)
        {
            return CreateErrorView("DOCX", ex);
        }
    }

    /// <summary>
    /// Creates a view for displaying the combined HTML content of an .epub file.
    /// </summary>
    private Control CreateEpubView(string path)
    {
        try
        {
            var book = EpubReader.ReadBook(path);
            var contentBuilder = new StringBuilder();
            
            // Concatenate all local HTML content from the EPUB into one string.
            foreach (var htmlFile in book.Content.Html.Local)
            {
                contentBuilder.AppendLine(htmlFile.Content);
                contentBuilder.AppendLine("<hr />"); // Add a separator between chapters
            }

            return new HtmlControl { Text = contentBuilder.ToString() };
        }
        catch (Exception ex)
        {
            return CreateErrorView("EPUB", ex);
        }
    }

    /// <summary>
    /// Creates a view for displaying plain text files like .md and .json.
    /// </summary>
    private Control CreateTextView(string path, bool useMonospace = false)
    {
        try
        {
            var text = File.ReadAllText(path);
            var textBox = new TextBox
            {
                Text = text,
                IsReadOnly = true,
                AcceptsReturn = true,
                TextWrapping = TextWrapping.Wrap,
                // Avalonia handles scroll bars via ScrollViewer. Keep default behaviour.
            };

            if (useMonospace)
            {
                textBox.FontFamily = new FontFamily("Cascadia Mono,Consolas,Menlo,monospace");
            }

            return textBox;
        }
        catch (Exception ex)
        {
            return CreateErrorView("Text File", ex);
        }
    }

    /// <summary>
    /// Creates a view indicating that the file format is not supported.
    /// </summary>
    private Control CreateUnsupportedView(string extension)
    {
        // Note: .mobi is a complex binary format requiring specialized libraries to parse.
        // It is grouped here as unsupported for simplicity.
        return new TextBlock 
        { 
            Text = $"The file format '{extension}' is not supported.", 
            HorizontalAlignment = Avalonia.Layout.HorizontalAlignment.Center,
            VerticalAlignment = Avalonia.Layout.VerticalAlignment.Center 
        };
    }

    /// <summary>
    /// Creates a standardized view for displaying file loading errors.
    /// </summary>
    private Control CreateErrorView(string format, Exception ex)
    {
        return new TextBlock
        {
            Text = $"Failed to load {format} file.\n\nError: {ex.Message}",
            Foreground = new SolidColorBrush(Colors.Red),
            HorizontalAlignment = Avalonia.Layout.HorizontalAlignment.Center,
            VerticalAlignment = Avalonia.Layout.VerticalAlignment.Center,
            TextWrapping = TextWrapping.Wrap
        };
    }
}

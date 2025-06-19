using Avalonia;
using Avalonia.Controls;
using Avalonia.Markup.Xaml;
using PdfiumViewer;
using DocumentFormat.OpenXml.Packaging;
using DocumentFormat.OpenXml.Wordprocessing;
using System.IO;
using VersFx.Formats.Text.Epub;
using TheArtOfDev.HtmlRenderer.Avalonia;
using Avalonia.Media;

namespace GPTExporterIndexerAvalonia.Views.Controls;

public partial class BookViewer : UserControl
{
    public static readonly StyledProperty<string?> FilePathProperty =
        AvaloniaProperty.Register<BookViewer, string?>(nameof(FilePath));

    public string? FilePath
    {
        get => GetValue(FilePathProperty);
        set => SetValue(FilePathProperty, value);
    }

    private ContentControl? _content;

    public BookViewer()
    {
        InitializeComponent();
        _content = this.FindControl<ContentControl>("PART_Content")!;
        this.GetObservable(FilePathProperty).Subscribe(LoadFile);
    }

    private void InitializeComponent()
    {
        AvaloniaXamlLoader.Load(this);
    }

    private void LoadFile(string? path)
    {
        if (string.IsNullOrEmpty(path) || !File.Exists(path))
        {
            _content.Content = null;
            return;
        }

        var ext = Path.GetExtension(path).ToLowerInvariant();
        if (ext == ".pdf")
        {
            var pdfDoc = PdfDocument.Load(path);
            _content.Content = new PdfViewer { Document = pdfDoc };
        }
        else if (ext == ".docx")
        {
            using var doc = WordprocessingDocument.Open(path, false);
            var text = doc.MainDocumentPart?.Document.Body?.InnerText ?? string.Empty;
            _content.Content = new TextBlock { Text = text, TextWrapping = TextWrapping.Wrap };
        }
        else if (ext == ".epub")
        {
            var book = EpubReader.ReadBook(path);
            var firstHtml = book.Content.Html.Values.FirstOrDefault();
            _content.Content = new HtmlControl { Text = firstHtml?.Content ?? string.Empty };
        }
        else
        {
            _content.Content = new TextBlock { Text = $"Unsupported: {ext}" };
        }
    }
}

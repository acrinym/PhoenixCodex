using System;
using System.Collections.ObjectModel;
using System.IO;
using Avalonia.Media.Imaging;
using Avalonia;
using Docnet.Core;
using Docnet.Core.Models;
using SkiaSharp;
using System.Runtime.InteropServices;

namespace GPTExporterIndexerAvalonia.Reading;

public class BookReader
{
    public ObservableCollection<Bitmap> Pages { get; } = [];

    public void Load(string path)
    {
        Pages.Clear();
        if (string.IsNullOrWhiteSpace(path) || !File.Exists(path))
            return;

        using var docReader = DocLib.Instance.GetDocReader(File.ReadAllBytes(path), new PageDimensions(1080, 1920));
        var pageCount = docReader.GetPageCount();
        for (var i = 0; i < pageCount; i++)
        {
            using var page = docReader.GetPageReader(i);
            var width = page.GetPageWidth();
            var height = page.GetPageHeight();
            var raw = page.GetImage();

            var info = new SKImageInfo(width, height, SKColorType.Bgra8888, SKAlphaType.Premul);
            var handle = GCHandle.Alloc(raw, GCHandleType.Pinned);
            try
            {
                using var bitmap = new SKBitmap();
                bitmap.InstallPixels(info, handle.AddrOfPinnedObject(), info.RowBytes);
                using var image = SKImage.FromBitmap(bitmap);
                using var data = image.Encode(SKEncodedImageFormat.Png, 100);
                using var ms = new MemoryStream(data.ToArray());
                Pages.Add(new Bitmap(ms));
            }
            finally
            {
                handle.Free();
            }
        }
    }
}

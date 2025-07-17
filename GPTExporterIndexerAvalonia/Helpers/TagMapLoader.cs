using System;
using System.Collections.Generic;
using System.IO;
using DocumentFormat.OpenXml.Packaging;
using DocumentFormat.OpenXml.Spreadsheet;
using GPTExporterIndexerAvalonia.ViewModels;

namespace GPTExporterIndexerAvalonia.Helpers;

public static class TagMapLoader
{
    public static List<TagMapEntry> Load(string path)
    {
        var list = new List<TagMapEntry>();
        if (string.IsNullOrWhiteSpace(path) || !File.Exists(path))
            return list;

        var ext = Path.GetExtension(path).ToLowerInvariant();
        if (ext == ".xlsx" || ext == ".xlsm" || ext == ".xltx" || ext == ".xltm")
        {
            LoadExcel(path, list);
        }
        else
        {
            LoadCsv(path, list);
        }
        return list;
    }

    private static void LoadCsv(string path, List<TagMapEntry> list)
    {
        using var parser = new Microsoft.VisualBasic.FileIO.TextFieldParser(path);
        parser.SetDelimiters(",");
        parser.HasFieldsEnclosedInQuotes = true;
        var headers = parser.ReadFields();
        if (headers == null)
            return;
        while (!parser.EndOfData)
        {
            var fields = parser.ReadFields();
            if (fields == null)
                continue;
            var dict = new Dictionary<string, string?>();
            for (int i = 0; i < headers.Length && i < fields.Length; i++)
                dict[headers[i]] = fields[i];
            AddEntry(dict, list);
        }
    }

    private static void LoadExcel(string path, List<TagMapEntry> list)
    {
        using var doc = SpreadsheetDocument.Open(path, false);
        var wb = doc.WorkbookPart;
        if (wb == null)
            return;
        var sst = wb.SharedStringTablePart?.SharedStringTable;
        var sheet = wb.Workbook.Sheets?.GetFirstChild<Sheet>();
        if (sheet == null)
            return;
        var wsPart = (WorksheetPart)wb.GetPartById(sheet.Id!);
        var rows = wsPart.Worksheet.GetFirstChild<SheetData>()?.Elements<Row>();
        if (rows == null)
            return;
        var rowList = new List<Row>(rows);
        if (rowList.Count == 0)
            return;
        var headers = new List<string>();
        foreach (var cell in rowList[0].Elements<Cell>())
            headers.Add(GetCellValue(cell, sst).Trim());
        for (int i = 1; i < rowList.Count; i++)
        {
            var cells = new List<Cell>(rowList[i].Elements<Cell>());
            var dict = new Dictionary<string, string?>();
            for (int c = 0; c < headers.Count; c++)
            {
                string value = c < cells.Count ? GetCellValue(cells[c], sst) : string.Empty;
                dict[headers[c]] = value;
            }
            AddEntry(dict, list);
        }
    }

    private static string GetCellValue(Cell cell, SharedStringTable? sst)
    {
        var value = cell.CellValue?.InnerText ?? string.Empty;
        if (cell.DataType?.Value == CellValues.SharedString && int.TryParse(value, out var idx) && sst != null)
        {
            var item = sst.ElementAtOrDefault(idx);
            if (item != null)
                return item.InnerText ?? string.Empty;
        }
        return value;
    }

    private static void AddEntry(Dictionary<string, string?> dict, List<TagMapEntry> list)
    {
        var entry = new TagMapEntry
        {
            Document = dict.GetValueOrDefault("Document") ?? string.Empty,
            Category = dict.GetValueOrDefault("Category") ?? string.Empty,
            Preview = dict.GetValueOrDefault("Marker Preview"),
            Title = dict.GetValueOrDefault("Title") ?? dict.GetValueOrDefault("Document") ?? string.Empty
        };
        
        if (int.TryParse(dict.GetValueOrDefault("Line #"), out var line))
            entry.Line = line;
            
        if (DateTime.TryParse(dict.GetValueOrDefault("Date"), out var dt))
        {
            entry.Date = dt;
        }
        
        // Extract tags if available
        var tagsStr = dict.GetValueOrDefault("Tags");
        if (!string.IsNullOrWhiteSpace(tagsStr))
        {
            entry.Tags = tagsStr.Split(',', StringSplitOptions.RemoveEmptyEntries)
                .Select(t => t.Trim())
                .Where(t => !string.IsNullOrWhiteSpace(t))
                .ToList();
        }
        
        list.Add(entry);
    }
}

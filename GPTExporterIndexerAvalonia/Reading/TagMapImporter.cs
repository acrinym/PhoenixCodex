using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using Microsoft.VisualBasic.FileIO;
using DocumentFormat.OpenXml.Packaging;
using DocumentFormat.OpenXml.Spreadsheet;
using GPTExporterIndexerAvalonia.ViewModels;
using System.Text.Json;
using GPTExporterIndexerAvalonia.Services;

namespace GPTExporterIndexerAvalonia.Reading;

public static class TagMapImporter
{
    public static List<TagMapEntry> Load(string path)
    {
        var entries = new List<TagMapEntry>();
        if (string.IsNullOrWhiteSpace(path) || !File.Exists(path))
            return entries;

        var ext = Path.GetExtension(path).ToLowerInvariant();
        if (ext == ".json")
        {
            try
            {
                var json = File.ReadAllText(path);
                var arr = JsonSerializer.Deserialize<TagMapEntry[]>(json);
                if (arr != null)
                    entries.AddRange(arr);
            }
            catch (Exception ex)
            {
                DebugLogger.Log($"TagMapImporter.Load json error: {ex}");
            }
            return entries;
        }

        if (ext == ".xlsx" || ext == ".xlsm" || ext == ".xltx" || ext == ".xltm")
            LoadExcel(path, entries);
        else
            LoadCsv(path, entries);

        return entries;
    }

    private static void LoadCsv(string path, List<TagMapEntry> entries)
    {
        try
        {
            using var parser = new TextFieldParser(path);
            parser.SetDelimiters(",");
            parser.HasFieldsEnclosedInQuotes = true;
            if (parser.EndOfData)
                return;
            var headers = parser.ReadFields() ?? Array.Empty<string>();
            while (!parser.EndOfData)
            {
                var fields = parser.ReadFields() ?? Array.Empty<string>();
                var record = new Dictionary<string, string?>(StringComparer.OrdinalIgnoreCase);
                for (int i = 0; i < headers.Length && i < fields.Length; i++)
                    record[headers[i]] = fields[i];
                entries.Add(CreateEntry(record));
            }
        }
        catch (Exception ex)
        {
            DebugLogger.Log($"TagMapImporter.LoadCsv error: {ex}");
        }
    }

    private static void LoadExcel(string path, List<TagMapEntry> entries)
    {
        try
        {
            using var doc = SpreadsheetDocument.Open(path, false);
            var workbookPart = doc.WorkbookPart;
            if (workbookPart == null)
                return;
            var sheet = workbookPart.Workbook.Sheets?.Elements<Sheet>().FirstOrDefault();
            if (sheet == null)
                return;
            var worksheetPart = (WorksheetPart)workbookPart.GetPartById(sheet.Id!);
            var sheetData = worksheetPart.Worksheet.GetFirstChild<SheetData>();
            if (sheetData == null)
                return;

            var rows = sheetData.Elements<Row>().ToList();
            if (rows.Count == 0)
                return;
            var shared = workbookPart.SharedStringTablePart?.SharedStringTable;

            var headers = rows[0].Elements<Cell>()
                .Select(c => GetCellValue(c, shared)?.Trim() ?? string.Empty)
                .ToList();

            foreach (var row in rows.Skip(1))
            {
                var cells = row.Elements<Cell>().ToList();
                var record = new Dictionary<string, string?>(StringComparer.OrdinalIgnoreCase);
                for (int i = 0; i < headers.Count; i++)
                {
                    var val = i < cells.Count ? GetCellValue(cells[i], shared) : null;
                    record[headers[i]] = val;
                }
                entries.Add(CreateEntry(record));
            }
        }
        catch (Exception ex)
        {
            DebugLogger.Log($"TagMapImporter.LoadExcel error: {ex}");
        }
    }

    private static string? GetCellValue(Cell cell, SharedStringTable? shared)
    {
        if (cell == null)
            return null;
        var value = cell.CellValue?.InnerText;
        if (cell.DataType?.Value == CellValues.SharedString && int.TryParse(value, out var index))
            return shared?.ElementAtOrDefault(index)?.InnerText;
        return value;
    }

    private static TagMapEntry CreateEntry(Dictionary<string, string?> record)
    {
        var entry = new TagMapEntry
        {
            Document = record.TryGetValue("Document", out var doc) ? doc ?? string.Empty : string.Empty,
            Category = record.TryGetValue("Category", out var cat) ? cat ?? string.Empty : string.Empty,
            Preview = record.TryGetValue("Marker Preview", out var prev) ? prev : null
        };
        if (record.TryGetValue("Line #", out var lineStr) && int.TryParse(lineStr, out var line))
            entry.Line = line;
        return entry;
    }
}


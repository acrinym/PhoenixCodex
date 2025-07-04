Phoenix Codex 🪶
The Phoenix Codex is a suite of tools for sorting, indexing, and visualizing the AmandaMap. It is composed of a main Avalonia UI application and a shared core library.

## Python Scripts

Earlier iterations of the project were written in Python. These scripts remain in
the repository for reference only and are **not** used by the Avalonia
application. Instructions for launching or installing the old Python GUI have
been removed. All core functionality is being ported to C# so that it can be
maintained alongside the main application.

GPTExporterIndexerAvalonia
This repository includes a simple Avalonia application written in C#. It can
build a token-based search index for .txt, .json and .md files and search
the resulting index with basic context snippets. The UI now exposes additional
search options such as case sensitivity, fuzzy matching and AND/OR logic. You
can also open any matching file directly from the results list. A third tab
lets you parse a Markdown or JSON AmandaMap file and export a concise summary.

Features
Builds a token-based search index from .txt, .json, and .md files.
Searches the generated index with basic context snippets in the results.
Provides advanced search options, including:
Case sensitivity
Fuzzy matching
AND/OR logic
Allows you to open any matching file directly from the search results list.
Includes a book reader tab for loading Markdown or text files.
Provides a legacy tool tab to launch the original Python utility.
TagMap Tab
-----------
The **TagMap** tab manages tag entries that point back to lines in your source documents.
Load a `tagmap.json` file to see each referenced document in its own sub-tab. Within a document you can add new tags, edit the *Category* and *Preview* fields, and then save your changes back to JSON.
Entries store the document name and an optional line number. Use the built-in **Open Document...** command to jump to the referenced file so you can view the surrounding context before editing.

YAML Interpreter
----------------
The **YAML Interpreter** tab lets you load `.yaml` files and inspect their keys and values in a nested tree view.
Enter a file path, click **Load**, and the entries will be parsed using **YamlDotNet** so you can browse ritual templates directly inside the app.

Building the Application
Install the .NET 8 SDK on your system. On Ubuntu, you can do this with the following commands:

Bash

sudo apt-get update
sudo apt-get install -y dotnet-sdk-8.0
Build the Avalonia Project Navigate to the project directory and run the build command:

Bash

dotnet build GPTExporterIndexerAvalonia/GPTExporterIndexerAvalonia.csproj -c Release

Running the Application
-----------------------
After building, start the Avalonia UI with:

```bash
dotnet run --project GPTExporterIndexerAvalonia/GPTExporterIndexerAvalonia.csproj
```

The window will display **Index**, **Search**, **Parse**, **Book Reader** and **Legacy Tool** tabs where you can build, search and parse the archive, read grimoire files or launch the original tool.


Web assets
The WebAssets folder contains a small index.html that loads three.js from a CDN. This is a placeholder for future visualisation features.

CodexEngine Library
The CodexEngine folder contains a .NET 8 class library with models and utilities used across the Phoenix Codex tools.

Build it separately with:

Bash

dotnet build CodexEngine/CodexEngine.csproj -c Release
The library's Parsing folder contains a Markdown parser that reads AmandaMap entries with emoji headers and exports them to a concise summary format.
The parser also handles JSON representations of the same entries. Use the helper methods in JsonMarkdownConverter to transform between JSON and Markdown while preserving any date strings found in the original text.
The Avalonia UI uses this library to parse files from the Parse tab and export summaries.

Python Scripts (Optional Reference)
----------------------------------
The `modules` folder and `gpt_export_index_tool.py` contain earlier Python
utilities for indexing and parsing AmandaMap content. They are provided solely
as reference implementations and are **not** required when building or running
the C# application.

If you wish to recreate their functionality, you may port the logic into C# or
another language of your choice, or simply run them with Python 3.10+. If you do
not need them, these files can be ignored or removed without affecting any of
the .NET projects.

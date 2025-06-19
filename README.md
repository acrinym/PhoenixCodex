Phoenix Codex 🪶
The Phoenix Codex is a suite of tools for sorting, indexing, and visualizing the AmandaMap. It is composed of a main Avalonia UI application and a shared core library.

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

The window will display **Index** and **Search** tabs where you can build and search the archive index.


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
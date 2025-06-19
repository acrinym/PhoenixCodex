PhoenixCodex
The Phoenix Codex  - AmandaMap sorter, indexer, Visualizer.

GPTExporterIndexerAvalonia
This repository includes a simple Avalonia application written in C#. It can
build a token-based search index for .txt, .json and .md files and search
the resulting index with basic context snippets. The UI now exposes additional
search options such as case sensitivity, fuzzy matching and AND/OR logic. You
can also open any matching file directly from the results list.

Building
Install the .NET 8 SDK on your system. On Ubuntu:

Bash

sudo apt-get update
sudo apt-get install -y dotnet-sdk-8.0
Then build the Avalonia project:

Bash

dotnet build GPTExporterIndexerAvalonia/GPTExporterIndexerAvalonia.csproj -c Release
Web assets
The WebAssets folder contains a small index.html that loads three.js from a CDN.
This is a placeholder for future visualisation features.
CodexEngine Library
-------------------
The `CodexEngine` folder contains a .NET 8 class library with models and utilities used across the Phoenix Codex tools.

Build it separately with:

```
dotnet build CodexEngine/CodexEngine.csproj -c Release
```

The library's `Parsing` folder contains a Markdown parser that reads AmandaMap entries with emoji headers and exports them to a concise summary format.
The parser also handles JSON representations of the same entries. Use the helper methods in `JsonMarkdownConverter` to transform between JSON and Markdown while preserving any date strings found in the original text.


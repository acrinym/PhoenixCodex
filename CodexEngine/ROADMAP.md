That's a perfect idea. Creating a clear roadmap or devlog is a standard and incredibly useful practice in software development, no matter how long you've been doing it. It keeps the project focused and tracks all the great ideas.

Let's map it out exactly like that. Here is a "readme" style development plan that summarizes everything we've discussed. This will serve as our blueprint.

***
# Phoenix Codex: Development Roadmap & Log
*As of: July 5, 2025*

This document tracks the current features, the next set of features in development, and future ideas for the Phoenix Codex application.

## ✅ **Phase 1: Core Functionality (Completed)**
This phase focused on building the foundational shell of the application, fixing critical bugs, and implementing the initial search capabilities.

* **Stable Application Shell:**
    * [cite_start]Resolved all compiler errors and runtime crashes related to `DataContext` and `WebView` initialization[cite: 541, 649, 756].
    * [cite_start]Each UI tab now correctly loads its own dedicated ViewModel [cite: 486-490].
* **Functional Search & Indexing Engine:**
    * [cite_start]The application can successfully build a token-based search index from a folder of `.txt`, `.md`, and `.json` files [cite: 415-416].
    * [cite_start]The search feature finds and displays text snippets from indexed files [cite: 451-453, 686-692].
    * [cite_start]A "View Index" feature was added for inspecting the raw `index.json` [cite: 491, 520-524].
* **Core Services & Refactoring:**
    * [cite_start]A modern `DialogService` handles all "Open File" and "Open Folder" requests, removing obsolete code [cite: 361-373, 576-578].
    * [cite_start]The "Load" buttons on all tabs now correctly use this service to prompt the user for a file[cite: 441, 576].
* **Basic Debugging:**
    * [cite_start]A simple `DebugLogger` creates a `debuglog.txt` file to trace application behavior [cite: 353-360].

## ⏩ **Phase 2: Intelligent Processing Pipeline (In Progress)**
This next phase will transform the application from a simple viewer into an intelligent data-processing tool.

* **Feature: Upgraded Data Models**
    * **Grimoire Entry (Ritual):** The model will be updated to include an editable `string? Outcome` property. It will be sorted by `Date` and will not have a number.
    * **AmandaMap Entry:** All related entries (Threshold, WhisperedFlame, etc.) will have a required `int Number` property for sorting and a `string Type` property for categorization.

* **Feature: Intelligent Parsing Service**
    * A new service will be built to parse raw text blocks from search results.
    * It will use pattern recognition (based on your examples with emojis and keywords) to extract structured data (Number, Date, Purpose, Ingredients, etc.) and create the appropriate C# model instance.

* **Feature: "Inbox" Workflow for Search & Index Tab**
    * The search result view will be enhanced to show the full text of a selected file.
    * New buttons will be added: **"Create Grimoire Entry"** and **"Create AmandaMap Entry."**
    * This will create the primary workflow: `Find -> Process -> Send to Tab`.

* **Feature: Conflict Resolution**
    * When processing an AmandaMap entry with a number that already exists, the application will halt and display a dialog prompt.
    * The user will be presented with choices: **Overwrite**, **Create Sub-entry** (e.g., 54.1), or **Cancel**.

* **Feature: Enhanced Tab Views**
    * The **AmandaMap** tab will group its entries by `Type` and sort them by `Number`.
    * The **Grimoire** tab will display an editable field for the `Outcome` of each ritual and sort entries by `Date`.

## 🗺️ **Phase 3: Future Ideas (Roadmap)**
These are ideas we have discussed but are scheduled for after Phase 2 is complete.

* **User Activity Log:**
    * Create a dedicated `UserActivityLog.txt` to record significant user actions (e.g., "Filter applied: 'ritual'").
    * This will allow you to analyze your own usage patterns to inform future development priorities.
* **Image & Visual Media Support:**
    * Extend the indexer and search UI to handle searching for and previewing embedded images or other visual media, potentially stored as Base64 strings or file links.


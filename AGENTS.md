# AGENTS.md

This file provides guidance to agents when working with code in this repository.

## Project Overview

- **Target**: Obsidian Community Plugin
- **Stack**: TypeScript, npm, esbuild
- **Entry Point**: `main.ts`

## Key Non-Obvious Information

- **Build/Run**:
    - `npm run dev`: Watch mode for development.
    - `npm run build`: Production build.
    - `npm run version`: **Custom script** to bump version in `manifest.json` and `versions.json`.
- **Testing**:
    - **No automated tests exist.** All testing is manual within Obsidian.
- **Core Architecture Patterns**:
    - **Lazy Initialization**: Core services are loaded on-demand via `InitializationManager`. This is critical for performance.
    - **Manager Pattern**: `HiNoteView` is highly complex and delegates its logic to numerous `Manager` classes (e.g., `LayoutManager`, `SearchUIManager`). Add new UI features by creating new Managers.
    - **Repository Pattern**: All data access must go through `HighlightRepository`.
- **Critical "Gotchas"**:
    - **Virtual Highlights**: Always check for `isVirtual: true` on highlight objects. They are file-level comments and lack text selections.
    - **Dynamic Layout**: The UI is highly responsive. Be aware of `LayoutManager` and `ViewPositionDetector` when making UI changes, as the layout adapts to the view's location (sidebar vs. main panel) and device (mobile vs. desktop).

*For more detailed, mode-specific rules, see the files in the `.kilocode/` directory.*

# WhitneyRoots: Instructions for AI Coding Assistants (Claude/Antigravity)

This document provides context and guidelines for working on the WhitneyRoots project, which is a modular, state-driven platform for exploring Sanskrit roots based on the Zalizniakiada architecture.

## 🏗 Architecture Overview

The project uses a **State-Driven Rendering** approach without heavy frameworks.

- **Core Logic (`src/core/`)**:
  - `state.js`: Global state management. Use `updateState()` to trigger re-renders.
  - `data.js`: Handles loading and migrating `app_data.json`.
  - `router.js`: Hash-based routing (`#v1/roots/list`, `#v1/quiz`).
  - `search.js`: Diacritic-aware Sanskrit search logic.
- **Utilities (`src/utils/`)**:
  - `dom.js`: Helper functions for DOM manipulation (`createElement`).
  - `linguistics.js`: Sanskrit normalization and IAST-to-Devanagari transliteration.
- **Renderers (`src/renderers/`)**:
  - Pure functions that return DOM elements based on state.
- **Build System**:
  - `scripts/bundle.js`: A custom Node.js script that concatenates modules into `v3_app.js`. **Always run `node scripts/bundle.js` after modifying source files.**

## 📊 Data Structure

The primary data source is `src/app_data.json`.

```json
{
  "lexicon": [
    {
      "id": "1",
      "root": "aṃh",
      "meaning": "be narrow or distressing",
      "link": "...",
      "classes": ["I"]
    }
  ]
}
```

- **Roots**: Sanskrit dhatu in IAST.
- **Classes**: Grammatical Ganas (I to X).
- **Links**: Direct references to samskrtam.ru documentation.

## 🎨 Design System

- **Styling**: Vanilla CSS in `index.css`.
- **Theme**: Premium Dark Mode with blue/indigo accents.
- **Typography**: Inter (UI) and Outfit (Headers).
- **Components**: Card-based layouts with subtle hover animations and glassmorphism.

## 🛠 Guidelines for Claude

1. **Follow the Runbook**: Refer to `WHITNEY_TRANSITION_RUNBOOK.md` for the migration plan.
2. **Bundle After Edits**: If you change any file in `src/`, you MUST run `node scripts/bundle.js`.
3. **Sanskrit Awareness**: Use `normalizeSanskrit()` from `utils/linguistics.js` for any search or comparison logic.
4. **Pure DOM**: Avoid innerHTML where possible; use `createElement` from `utils/dom.js` for building components.
5. **State Management**: Do not modify `state` directly. Use `updateState({ key: value })`.

## 🚀 Common Tasks

- **Updating Data**: Run the parsing scripts in the `scratch/` directory or create new ones to ingest more data from `.md` or `.txt` source files.
- **Adding Views**:
  1. Add the view name to `state.js`.
  2. Add a route in `router.js`.
  3. Create a renderer in `src/renderers/`.
  4. Update `entry.js` to handle the new view.
  5. Add the new files to `scripts/bundle.js`.

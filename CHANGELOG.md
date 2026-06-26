# [0.1.0-beta] - 2026-06-22

## Added
- One-click project creation from templates
- Complete project isolation (independent `data/` and `profiles/` directories)
- Auto-generate project shortcuts in the project library root directory
- Multi-library switching (main, test, temporary)
- Bilingual UI (Simplified Chinese and English) with instant switching
- Persistent user preferences (`~/.zpl_config.json`)
- First launch setup wizard
- Project card list view with launch and delete actions
- Right-click context menu for project operations

## Known Issues
- Desktop shortcut creation may fail due to system permissions on some Windows configurations

### 2026-06-23: ZPL v0.2.0 Major Feature Update

This update completes the transformation of the main window from card mode to table mode, and implements multiple core features including project-level isolation, independent language management, enhanced delete safety, and template automation.

---

#### 1. Main Window: Card → Table Mode

**Background**: Card mode had low information density, making it difficult to quickly scan and compare projects.

**Improvements**:
- Replaced card list with a table view with 7 column headers
- Added a "Language" column to show each project's current interface language
- Support sorting by clicking column headers
- Retained double-click launch and right-click menu
- Moved launch buttons to the rightmost column for direct access

**Interaction Changes**:
- Single-click row: highlight selection
- Double-click row: launch project
- Click "Language" column: open language settings dialog
- Hover row: background color change to indicate interactivity

---

#### 2. Project-Level Isolation: Full Isolation (Data + Configuration)

**Background**: Previously only data directories (`-datadir`) were isolated; all projects shared the same configuration directory, causing language, plugin, and other settings to interfere with each other.

**Improvements**:
- Each project now has its own independent `profiles/` configuration directory
- Launch commands now use both `-datadir` and `-P` parameters
- Each project is independently registered in the system `profiles.ini`

**Directory Structure**:
```
D:\ZoteroLibrary\
├── ProjectA\
│   ├── data\          ← -datadir points here
│   └── profiles\      ← -P points here
└── ProjectB\
    ├── data\
    └── profiles\
```

---

#### 3. Independent Language Management

**Background**: When configurations were shared, changing language in one project affected all projects.

**Improvements**:
- Each project stores language settings independently in `profiles/prefs.js`
- Language settings include `intl.locale.requested` and `intl.locale.matchOS=false`
- Multiple entry points for language settings:
  - New project dialog
  - Click on "Language" column in main window
  - Right-click menu → Language submenu
  - Preferences → Default language for new projects

**Critical Fix**: Must write both `intl.locale.matchOS = false` and `intl.locale.requested` together; otherwise Zotero will follow system language and ignore `intl.locale.requested`.

---

#### 4. Template Automation

**Background**: Previously users had to manually prepare templates containing `profiles/` directories, which was high-maintenance.

**Improvements**:
- Templates now only need to contain a `data/` subdirectory
- ZPL automatically creates `profiles/`, `extensions/`, and `prefs.js` when creating a new project
- Automatically writes default language settings
- No manual template configuration required

**Simplified Template Structure**:
```
D:\ZPL_Templates\v9.0.5\
└── data\          ← Only data needed
    ├── zotero.sqlite
    └── storage\
```

---

#### 5. Enhanced Delete Safety

**Background**: Previous delete only had a simple confirmation dialog; accidental deletion risk was high, and files were physically deleted without recovery option.

**Improvements**:
- Added "in-use detection": checks if project is currently being used by Zotero (lock files and process arguments)
- Double verification: require manual entry of project name + checkbox confirmation
- Default to moving to Recycle Bin (recoverable) instead of direct physical deletion
- Detailed success/failure feedback dialogs

**Flow**:
```
In-use detection → Warning dialog → Confirmation dialog (name input + checkbox) → Move to Recycle Bin → Feedback
```

---

#### 6. `profiles.ini` Write Fixes

**Background**: Previously written `profiles.ini` had incorrect path, improper key name casing, and spaces around equals signs, causing Zotero to fail recognition.

**Fixes**:
- Path correction: `%APPDATA%\Zotero\Zotero\profiles.ini` (for Zotero 7+)
- Key name casing: `Name`, `Path`, `IsRelative`, `Default` (PascalCase)
- Equals format: `Name=test` (no spaces)
- Used `config.optionxform = str` and `space_around_delimiters=False`

---

#### 7. New Utility Modules Added

| Module | Function |
| :--- | :--- |
| `utils/profile_registry.py` | Read/write system `profiles.ini`, register/unregister profiles |
| `utils/language_utils.py` | Read/write language settings in `prefs.js` |
| `utils/recycle_bin.py` | Windows Recycle Bin operations |
| `views/dialogs/language_dialog.py` | Language settings dialog |
| `views/dialogs/project_in_use_dialog.py` | In-use warning dialog |
| `views/dialogs/delete_success_dialog.py` | Delete success dialog |
| `views/dialogs/delete_failed_dialog.py` | Delete failure dialog |

---

#### 8. File Change Statistics

| Type | Count |
| :--- | :--- |
| New files | 7 |
| Modified files | 10 |
| Deleted files/directories | 1 (`widgets/`) |


# [0.1.1-beta] - 2026-06-24

## Added
- Hybrid mode project creation (auto/template/native)
- Template automation: auto-create profiles/, extensions/, prefs.js
- Project-level isolation: independent profiles/ per project
- Preferences enhancements: creation mode selector, default language, config folder button

## Fixed
- profiles.ini write path and format (Zotero 7+)
- Language management: now writes both matchOS=false and requested together
- Conditional field validation: dynamic dependencies based on mode

## Changed
- Auto mode silently falls back to native when template unavailable


# [0.1.2-beta] - 2026-06-24

## Added
- Table sorting: click column headers to sort projects (ascending/descending)
- Manual column width adjustment: all columns except Path can be resized by dragging
- Centralized software information management (`APP_NAME`, `APP_VERSION`, etc. in config.py)

## Changed
- Language column now correctly displays each project's interface language using `profile.profiles_path`
- Language column content updates when switching ZPL interface language (via `refresh_data`)
- Launch button vertically centered in table rows (fixed height 20px, row height 30px)
- Code architecture: `main_window.py` refactored into 8 modules (components/handlers/menus)
- `gen_init.py` adapted for automatic subpackage discovery and aggregate `__init__.py` generation
- Column width modes: Interactive (manual adjustment) for all columns except Path (Stretch)

## Fixed
- Project language column showing "Default" incorrectly
- Language column not updating after ZPL language switch
- Launch button alignment in table rows (was top-aligned, now center-aligned)

# [0.1.3-beta] - 2026-06-25

## Added
- Hybrid creation modes: Full mode (55MB) and Light mode (19MB)
- Table sorting: click column headers to sort projects (ascending/descending)
- Manual column width adjustment: all columns except Path can be resized by dragging
- Centralized software information management (`APP_NAME`, `APP_VERSION`, etc. in config.py)
- Project export functionality (ZIP packaging for migration)
- Project import functionality (auto-extract, register Profile, generate shortcuts)

## Changed
- Full mode creation flow: empty Profile + Zotero auto-completion generates 55MB complete project
- Language column correctly displays project interface language using `profile.profiles_path`
- Launch button vertically centered in table rows (fixed height 20px, row height 30px)
- Language column content updates when switching ZPL interface language
- Desktop shortcuts removed for new and imported projects; only library shortcuts are kept
- Column width modes: Interactive for all columns except Path (Stretch)

## Fixed
- Project language column showing "Default" incorrectly
- Language column not updating after ZPL language switch
- Launch button alignment in table rows (was top-aligned, now center-aligned)
- Launch button starting wrong project after sorting


# [0.1.4-beta] - 2026-06-25

## Added
- Project rename functionality (right-click / F2 shortcut)
  - Atomic operation: syncs folder, profiles.ini, shortcuts, notes
  - In-use detection and automatic rollback
- Export full backup option (default: include all files)
- Creation mode debug logs (Full/Light/Template)
- `gen_init.py` auto-generates controller composite class (added `generate_controller_init` function)

## Changed
- Controller layer fully refactored (5 Mixin modules: base/creator/launcher/shortcut/manager)
- Unified import: `from controllers import ZoteroController`
- `NewProjectDialog` and `PreferencesDialog` now accept controller as external parameter
- First-launch project creation no longer waits for initialization
- Added project creation prompt translation keys to `languages.json`
- Fixed `manager.py` rename path error (now points to profiles subdirectory)

## Removed
- Completely removed desktop shortcuts
  - Removed "Create Desktop Shortcut" from new project flow
  - Removed "Create Desktop Shortcut" from right-click and main menus
  - Removed related Preferences configuration (`auto_create_shortcut`)
- Deleted `zotero_controller.py` (split into modules)

## Fixed
- Project configuration loss after rename (`profiles.ini` path error)
- Controller MRO conflict (TypeError: Cannot create a consistent method resolution order)
- Missing `get_project_language` and `set_project_language` methods
- JSON parsing failure in `languages.json` (trailing commas)
- Controller instantiation error in `NewProjectDialog`
- Controller instantiation error in `PreferencesDialog`
- Missing `table_context_menu.py` file

# [0.1.5-beta] - 2026-06-25

## Added
- Creation progress dialog (120-second countdown)
  - Friendly message displayed after project creation, guiding users to wait for initialization
  - OK button enabled after countdown ends to prevent premature user action
- Rename on import
  - New "Rename project on import" checkbox
  - Unchecked by default (restore project); checked to edit name (template cloning)
- Real-time path validation (first-launch dialog)
  - Auto-detects zotero.exe when Zotero path is selected
  - Shows "Detected" or "Not found" status message

## Changed
- **Configuration model greatly simplified**:
  - First-launch setup: 6 → 2 fields
  - Preferences: 8+ → 2 fields
  - Removed zotero_version, templates_root, default_language, creation_method, creation_profile_mode
- **Project creation logic fixed**:
  - Unified to "Native Generation + Full Mode + System Language"
  - No longer writes prefs.js; Zotero generates it automatically
  - Returns immediately after launching Zotero, showing progress dialog
- **Import dialog simplified**:
  - Removed "Auto-register Profile" and "Generate shortcuts" checkboxes (now automatic)
  - Removed redundant hint text
  - Conflict handling only "Auto Rename" and "Cancel" (removed dangerous "Overwrite")
- **Export dialog simplified**:
  - Removed "Full Backup" checkbox; always exports all files
- **New Project dialog simplified**:
  - Removed language dropdown (fixed to system language)
  - Updated hint text to user-friendly version
- **Preferences dialog simplified**:
  - Only Zotero path and project library directory
  - Fixed missing label text issue
- **Status bar optimized**:
  - Removed version number display
  - Shows Zotero detection status

## Removed
- Project creation method selection (auto/template/native)
- Project completeness mode selection (full/light)
- Default language configuration for new projects
- Template directory configuration
- Zotero version configuration
- "Overwrite" option in import conflict handling (safety consideration)

## Fixed
- Status bar showing "Zotero not found" after first launch
- Missing label text in preferences dialog
- Confusing messages like "process unexpectedly exited" during project creation
- AttributeError calling deprecated set_zotero_version on first launch

# [0.1.6-beta] - 2026-06-26

## Added
- CLI command-line entry support
  - `--fix`: Execute launch repair (rebuild Profile registration)
  - `--rebuild-shortcuts`: Execute shortcut repair
  - `--help`: Display help information
- GUI Project Repair menu (Help → Project Repair)
  - Repair Launch: Rebuild Profile registration to fix double-click launch issues
  - Repair Shortcut: Generate .lnk files for projects missing shortcuts
- `src/cli/` command-line toolkit (moved from `scripts/`)
- Automatically opens output folder after packaging
- Displays processed project count during repair
- Force-includes `sqlite3`, `dataclasses`, `json` and other standard libraries during packaging

## Changed
- `scripts/` directory moved to `src/cli/` for unified package structure
- Repair tool core logic migrated to `utils/repair_utils.py` and `utils/repair_shortcut_utils.py`
- `gen_init.py` now auto-maintains `src/cli`
- `build.bat` uses `dist\ZoteroProjectLauncher` as source for entire folder packaging
- `main.py` enhanced with `setup_path()` for path compatibility
- `status_bar_widget.update_info()` directly uses passed status text, removing redundant prefix
- Preferences dialog labels changed to instance variables to ensure text display

## Fixed
- Status bar duplicate "Zotero Zotero detected"
- `languages.json` not loading after packaging (English display)
- Missing label text in Preferences dialog
- Interface not refreshing after first launch
- `ModuleNotFoundError: No module named 'json'` after packaging
- `ModuleNotFoundError: No module named 'dataclasses'` after packaging
- `ModuleNotFoundError: No module named 'sqlite3'` after packaging
- Item count displaying "?" after packaging
- Icon attribute error in `directory_bar.py` (`SP_DialogApplyButton`)
- `fix_profiles.py` import path error
- `src/cli/` module import path issues

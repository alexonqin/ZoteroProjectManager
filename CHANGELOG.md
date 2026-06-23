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

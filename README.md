
# Zotero Project Launcher (ZPL)

[English](#english) | [中文](#chinese)

---

<a name="english"></a>

## English

### Overview

A lightweight desktop tool for managing multiple isolated Zotero projects, allowing you to manage Zotero projects like folders. Built with Python and PySide6, it provides a clean graphical interface for creating, launching, and organizing independent Zotero environments.

### Features

- **One-click project creation**: Create independent Zotero projects with just a name and location
- **Complete project isolation**: Each project has its own `data/` and `profiles/` directories
- **Library shortcuts**: Auto-generate project shortcuts in the project library root directory
- **Template management**: Support multiple template versions, auto-match with Zotero version
- **Multi-library support**: Switch between main, test, and temporary project libraries
- **Bilingual UI**: Support both Simplified Chinese and English with instant switching
- **Persistent preferences**: Settings saved to `~/.zpl_config.json`

### Installation

#### Prerequisites
- Python 3.7+
- PySide6
- pywin32 (Windows only)

#### Steps

# Clone the repository
```bash
git clone https://github.com/alexonqin/ZoteroProjectLauncher.git
cd ZoteroProjectLauncher
```

# Install dependencies
```bash
pip install -r requirements.txt
```

# Run the application
```bash
python src/main.py
```


### Quick Start

1. **First launch**: Follow the setup wizard to configure:
   - Zotero version (e.g., `9.0.5`)
   - Zotero installation directory (e.g., `D:\Program Files\Zotero`)
   - Template directory (e.g., `D:\ZPL_Templates`)
   - Project library directory (e.g., `D:\ZoteroLibrary`)

2. **Prepare template**: Create a subfolder named `v{version}/` (e.g., `v9.0.5/`) in the template directory, containing:
   ```
   v9.0.5/
   ├── data/
   │   └── zotero.sqlite
   └── profiles/
       └── prefs.js
   ```

3. **Create project**: Click "New Project", enter a name and location

4. **Launch project**: Double-click the project card, or use the shortcut in the project library directory

### Directory Structure

```
ZoteroProjectLauncher/
├── src/
│   ├── main.py
│   ├── controllers/
│   │   └── zotero_controller.py
│   ├── models/
│   │   ├── config.py
│   │   └── profile.py
│   ├── utils/
│   │   ├── config_manager.py
│   │   ├── i18n.py
│   │   └── path_utils.py
│   ├── views/
│   │   ├── main_window.py
│   │   ├── widgets/
│   │   │   └── project_card.py
│   │   └── dialogs/
│   │       ├── preferences_dialog.py
│   │       ├── new_project_dialog.py
│   │       ├── delete_confirm_dialog.py
│   │       └── first_launch_dialog.py
│   └── resources/
│       └── languages.json
├── requirements.txt
└── README.md
```

### Development Status

Currently in **beta** (v0.1). Core functionality is implemented and tested.

### License

MIT License

### Author

alexonqin

---

<a name="chinese"></a>

## 中文

### 概述

一款轻量级的 Zotero 多项目管理工具，让你像管理文件夹一样管理 Zotero 项目。基于 Python 和 PySide6 开发，提供简洁的图形界面，用于创建、启动和组织独立的 Zotero 环境。

### 功能特性

- **一键新建项目**：只需输入名称和位置即可创建独立的 Zotero 项目
- **项目完全隔离**：每个项目拥有独立的 `data/` 和 `profiles/` 目录
- **项目库快捷方式**：在项目库根目录自动生成项目快捷方式
- **模板管理**：支持多版本模板，自动匹配用户 Zotero 版本
- **多项目库支持**：在主库、测试库、临时库之间自由切换
- **中英文界面**：支持简体中文和 English 即时切换
- **偏好持久化**：设置保存到 `~/.zpl_config.json`

### 安装

#### 依赖
- Python 3.7+
- PySide6
- pywin32 (仅 Windows)

#### 安装步骤

# 克隆仓库
```bash
git clone https://github.com/alexonqin/ZoteroProjectLauncher.git
cd ZoteroProjectLauncher
```

# 安装依赖
```bash
pip install -r requirements.txt
```

# 运行程序
```bash
python src/main.py
```

### 快速开始

1. **首次启动**：按照引导完成以下设置：
   - Zotero 版本号（如 `9.0.5`）
   - Zotero 安装目录（如 `D:\Program Files\Zotero`）
   - 模板目录（如 `D:\ZPL_Templates`）
   - 项目库目录（如 `D:\ZoteroLibrary`）

2. **准备模板**：在模板目录下创建 `v{版本号}/` 子文件夹（如 `v9.0.5/`），包含：
   ```
   v9.0.5/
   ├── data/
   │   └── zotero.sqlite
   └── profiles/
       └── prefs.js
   ```

3. **新建项目**：点击「新建项目」，输入名称和存放位置

4. **启动项目**：双击项目卡片，或点击项目库目录中的快捷方式

### 目录结构

```
ZoteroProjectLauncher/
├── src/
│   ├── main.py
│   ├── controllers/
│   │   └── zotero_controller.py
│   ├── models/
│   │   ├── config.py
│   │   └── profile.py
│   ├── utils/
│   │   ├── config_manager.py
│   │   ├── i18n.py
│   │   └── path_utils.py
│   ├── views/
│   │   ├── main_window.py
│   │   ├── widgets/
│   │   │   └── project_card.py
│   │   └── dialogs/
│   │       ├── preferences_dialog.py
│   │       ├── new_project_dialog.py
│   │       ├── delete_confirm_dialog.py
│   │       └── first_launch_dialog.py
│   └── resources/
│       └── languages.json
├── requirements.txt
└── README.md
```

### 开发状态

当前为 **beta** 版本 (v0.1)，核心功能已实现并完成测试。

### 许可证

MIT License

### 作者

alexonqin


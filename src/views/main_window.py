# -*- coding: utf-8 -*-
"""
主窗口 - 组装器
"""

from pathlib import Path

from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QMessageBox, QDialog
from PySide6.QtCore import Qt, QTimer

from models.config import APP_NAME, APP_VERSION
from models.profile import Profile

from controllers import ZoteroController
from utils.i18n import I18n
from utils.config_manager import ConfigManager
from utils.path_utils import is_valid_directory

from views.components import TableWidget, ToolbarWidget, DirectoryBar, StatusBarWidget
from views.handlers import ProjectHandler, LanguageHandler
from views.menus import MainMenu
from views.dialogs import (
    FirstLaunchDialog,
    PreferencesDialog,
    AboutDialog
)


class MainWindow(QMainWindow):
    def __init__(self, i18n: I18n, config_mgr: ConfigManager):
        super().__init__()
        self.i18n = i18n
        self.config_mgr = config_mgr
        self.config = config_mgr.get_config()
        self.controller = ZoteroController(self.config_mgr)

        self.current_dir = ""

        self._setup_ui()
        self._setup_handlers()
        self._connect_signals()

        self._init_after_ui()
        self.retranslate_ui()

    def _setup_ui(self):
        self.setMinimumSize(750, 400)

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setSpacing(8)
        main_layout.setContentsMargins(10, 10, 10, 10)

        self.toolbar = ToolbarWidget(self.i18n, self)
        main_layout.addWidget(self.toolbar)

        self.directory_bar = DirectoryBar(self.i18n, self.config_mgr, self)
        main_layout.addWidget(self.directory_bar)

        self.table = TableWidget(self.i18n, self)
        main_layout.addWidget(self.table)

        self.status_bar_widget = StatusBarWidget(self.i18n, self)
        self.setStatusBar(self.status_bar_widget)

        self.menu = MainMenu(self.i18n, self)
        self.setMenuBar(self.menu)

    def _setup_handlers(self):
        self.project_handler = ProjectHandler(
            self.controller, self.config_mgr, self.i18n, self.table, self
        )
        self.language_handler = LanguageHandler(
            self.controller, self.config_mgr, self.i18n, self.table, self
        )

    def _connect_signals(self):
        # 工具栏
        self.toolbar.refresh_clicked.connect(self._on_refresh)
        self.toolbar.new_clicked.connect(self.project_handler.on_new_project)
        self.toolbar.preferences_clicked.connect(self._on_preferences)
        self.toolbar.language_switched.connect(self.language_handler.on_switch_language)

        # 目录条
        self.directory_bar.directory_changed.connect(self.project_handler.on_directory_changed)
        self.directory_bar.default_set.connect(self._on_default_set)

        # 表格
        self.table.launch_requested.connect(self.project_handler.on_launch_project)
        self.table.open_folder_requested.connect(self.project_handler.on_open_folder)
        self.table.delete_requested.connect(self.project_handler.on_delete_project)
        self.table.change_language_requested.connect(self.language_handler.on_change_project_language)
        self.table.export_requested.connect(self.project_handler.on_export_project)
        self.table.rename_requested.connect(self.project_handler.on_rename_project)

        # 菜单
        self.menu.new_triggered.connect(self.project_handler.on_new_project)
        self.menu.import_triggered.connect(self.project_handler.on_import_project)
        self.menu.refresh_triggered.connect(self._on_refresh)
        self.menu.open_folder_triggered.connect(self._on_menu_open_folder)
        self.menu.export_triggered.connect(self._on_menu_export)
        self.menu.exit_triggered.connect(self.close)
        self.menu.rename_triggered.connect(self._on_menu_rename)
        self.menu.delete_triggered.connect(self._on_menu_delete)
        self.menu.preferences_triggered.connect(self._on_preferences)
        self.menu.about_triggered.connect(self._on_about)

    def retranslate_ui(self):
        self.setWindowTitle(f"{APP_NAME} {APP_VERSION}")
        self.toolbar.retranslate_ui()
        self.directory_bar.retranslate_ui()
        self.table.retranslate_ui()
        self.status_bar_widget.retranslate_ui()
        self.menu.retranslate_ui()
        self._update_status()

    def _init_after_ui(self):
        w, h = self.config_mgr.get_window_size()
        x, y = self.config_mgr.get_window_position()
        if w > 0 and h > 0:
            self.resize(w, h)
        if x >= 0 and y >= 0:
            self.move(x, y)

        self._init_directory()
        self._on_refresh()

    def _init_directory(self):
        default_dir = self.config.profiles_default
        current_dir = self.config.profiles_current

        if current_dir and is_valid_directory(current_dir):
            self.current_dir = current_dir
        elif default_dir and is_valid_directory(default_dir):
            self.current_dir = default_dir
            self.config_mgr.set_profiles_current(default_dir)
        else:
            self._show_first_launch()

        self.directory_bar.set_current_dir(self.current_dir)
        if self.current_dir:
            self.config_mgr.add_to_history(self.current_dir)

    def _show_first_launch(self):
        dialog = FirstLaunchDialog(self.i18n, self)
        if dialog.exec_() == QDialog.Accepted:
            cfg = dialog.result_config
            self.config_mgr.set_zotero_install_dir(cfg["zotero_install_dir"])
            self.config_mgr.set_profiles_current(cfg["profiles_current"])
            self.config_mgr.set_profiles_default(cfg["profiles_default"])
            self.current_dir = cfg["profiles_current"]
            self.directory_bar.set_current_dir(self.current_dir)
            self.config_mgr.add_to_history(self.current_dir)
            # 更新状态栏
            self._update_status()
        else:
            QTimer.singleShot(0, self.close)

    def _on_refresh(self):
        current_dir = self.config_mgr.get_profiles_current()
        if current_dir and is_valid_directory(current_dir):
            self.current_dir = current_dir
            self.directory_bar.set_current_dir(current_dir)
            self.project_handler.on_refresh()
        else:
            self.table.setRowCount(0)
        # 更新状态栏（包括 Zotero 检测状态）
        self._update_status()

    def _update_status(self):
        """更新状态栏信息"""
        profiles = self.table.profiles if hasattr(self.table, 'profiles') else []
        count = len(profiles)

        # 检测 Zotero 是否可用
        install_dir = self.config_mgr.get_zotero_install_dir()
        if install_dir and is_valid_directory(install_dir):
            exe_path = Path(install_dir) / "zotero.exe"
            if exe_path.exists():
                zotero_status = self.i18n.tr("status_zotero_found")
            else:
                zotero_status = self.i18n.tr("status_zotero_not_found")
        else:
            zotero_status = self.i18n.tr("status_zotero_not_found")

        self.status_bar_widget.update_info(count, zotero_status)

    def _on_default_set(self, path: str):
        self.config_mgr.set_profiles_default(path)
        QMessageBox.information(self, "", "已设为默认目录")

    def _on_menu_open_folder(self):
        profile = self.table.get_selected_profile()
        if profile:
            self.project_handler.on_open_folder(profile)

    def _on_menu_delete(self):
        profile = self.table.get_selected_profile()
        if profile:
            self.project_handler.on_delete_project(profile)

    def _on_menu_export(self):
        profile = self.table.get_selected_profile()
        if profile:
            self.project_handler.on_export_project(profile)
        else:
            QMessageBox.warning(self, "", self.i18n.tr("export_no_selection"))

    def _on_menu_rename(self):
        profile = self.table.get_selected_profile()
        if profile:
            self.project_handler.on_rename_project(profile)
        else:
            QMessageBox.warning(self, "", "请先选择一个项目。")

    def _on_preferences(self):
        dialog = PreferencesDialog(self.i18n, self.config_mgr, self.controller, self)
        if dialog.exec_() == QDialog.Accepted:
            self._on_refresh()
            self.retranslate_ui()
            self.current_dir = self.config_mgr.get_profiles_current()
            self.directory_bar.set_current_dir(self.current_dir)

    def _on_about(self):
        dialog = AboutDialog(self.i18n, self)
        dialog.exec_()

    def closeEvent(self, event):
        self.config_mgr.set_window_size(self.width(), self.height())
        self.config_mgr.set_window_position(self.x(), self.y())
        event.accept()
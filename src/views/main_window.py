# -*- coding: utf-8 -*-
"""
主窗口 - 表单模式（表格展示项目），含语言列
"""

import os
from pathlib import Path

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QStatusBar, QMessageBox, QFileDialog, QMenu, QMenuBar,
    QDialog, QStyle, QAbstractItemView
)
from PySide6.QtCore import Qt, QTimer, QSize
from PySide6.QtGui import QAction, QKeySequence

from models.profile import Profile
from controllers.zotero_controller import ZoteroController
from utils.i18n import I18n
from utils.config_manager import ConfigManager
from utils.path_utils import is_valid_directory
from utils.language_utils import read_language, get_display_language

from views.dialogs import (
    PreferencesDialog,
    NewProjectDialog,
    DeleteConfirmDialog,
    ProjectInUseDialog,
    DeleteSuccessDialog,
    DeleteFailedDialog,
    FirstLaunchDialog,
    LanguageDialog
)


class MainWindow(QMainWindow):
    """主窗口"""

    def __init__(self, i18n: I18n, config_mgr: ConfigManager):
        super().__init__()
        self.i18n = i18n
        self.config_mgr = config_mgr
        self.config = config_mgr.get_config()
        self.controller = ZoteroController(self.config_mgr)

        self.profiles = []
        self.current_dir = ""
        self.selected_row = -1

        self._setup_ui()
        self._setup_menu()
        self._setup_status_bar()
        self._init_after_ui()
        self.retranslate_ui()

    def _setup_ui(self):
        self.setMinimumSize(750, 400)

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setSpacing(8)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # 工具栏
        toolbar = QHBoxLayout()
        toolbar.setSpacing(8)
        self.refresh_btn = QPushButton()
        self.refresh_btn.clicked.connect(self._on_refresh)
        toolbar.addWidget(self.refresh_btn)

        self.new_btn = QPushButton()
        self.new_btn.clicked.connect(self._on_new_project)
        toolbar.addWidget(self.new_btn)

        self.pref_btn = QPushButton()
        self.pref_btn.clicked.connect(self._on_preferences)
        toolbar.addWidget(self.pref_btn)

        toolbar.addStretch()

        self.lang_btn = QPushButton()
        self.lang_btn.setFixedWidth(50)
        self.lang_btn.clicked.connect(self._on_switch_language)
        toolbar.addWidget(self.lang_btn)

        main_layout.addLayout(toolbar)

        # 目录选择条
        dir_layout = QHBoxLayout()
        dir_layout.setSpacing(8)
        self.dir_label = QLabel()
        dir_layout.addWidget(self.dir_label)

        self.dir_path_label = QLabel()
        self.dir_path_label.setStyleSheet("color: #2b7a62; font-weight: bold;")
        self.dir_path_label.setWordWrap(True)
        dir_layout.addWidget(self.dir_path_label, 1)

        self.dir_history_btn = QPushButton("▼")
        self.dir_history_btn.setFixedWidth(30)
        self.dir_history_btn.clicked.connect(self._show_history_menu)
        dir_layout.addWidget(self.dir_history_btn)

        self.dir_browse_btn = QPushButton()
        self.dir_browse_btn.clicked.connect(self._on_browse_dir)
        dir_layout.addWidget(self.dir_browse_btn)

        self.dir_default_btn = QPushButton()
        self.dir_default_btn.clicked.connect(self._on_set_default_dir)
        dir_layout.addWidget(self.dir_default_btn)

        main_layout.addLayout(dir_layout)

        # 项目表格（7列）
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "项目名称", "界面语言", "路径", "文献", "插件", "最后使用", "操作"
        ])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeToContents)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setShowGrid(False)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("""
            QTableWidget::item:selected {
                background-color: #e3edf7;
            }
            QTableWidget::item:hover {
                background-color: #f0f4f8;
            }
        """)
        self.table.itemDoubleClicked.connect(self._on_item_double_clicked)
        self.table.itemClicked.connect(self._on_item_clicked)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self._on_context_menu)

        main_layout.addWidget(self.table)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

    def _setup_menu(self):
        menubar = self.menuBar()
        self.file_menu = menubar.addMenu("")
        self.new_action = QAction("", self)
        self.new_action.setShortcut(QKeySequence("Ctrl+N"))
        self.new_action.triggered.connect(self._on_new_project)
        self.file_menu.addAction(self.new_action)

        self.refresh_action = QAction("", self)
        self.refresh_action.setShortcut(QKeySequence("F5"))
        self.refresh_action.triggered.connect(self._on_refresh)
        self.file_menu.addAction(self.refresh_action)

        self.file_menu.addSeparator()
        self.open_folder_action = QAction("", self)
        self.open_folder_action.setShortcut(QKeySequence("Ctrl+O"))
        self.open_folder_action.triggered.connect(self._on_open_folder)
        self.file_menu.addAction(self.open_folder_action)

        self.file_menu.addSeparator()
        self.exit_action = QAction("", self)
        self.exit_action.setShortcut(QKeySequence("Ctrl+Q"))
        self.exit_action.triggered.connect(self.close)
        self.file_menu.addAction(self.exit_action)

        self.edit_menu = menubar.addMenu("")
        self.shortcut_action = QAction("", self)
        self.shortcut_action.triggered.connect(self._on_create_shortcut)
        self.edit_menu.addAction(self.shortcut_action)

        self.edit_menu.addSeparator()
        self.delete_action = QAction("", self)
        self.delete_action.setShortcut(QKeySequence("Delete"))
        self.delete_action.triggered.connect(self._on_delete_project)
        self.edit_menu.addAction(self.delete_action)

        self.edit_menu.addSeparator()
        self.pref_action = QAction("", self)
        self.pref_action.setShortcut(QKeySequence("Ctrl+P"))
        self.pref_action.triggered.connect(self._on_preferences)
        self.edit_menu.addAction(self.pref_action)

        self.help_menu = menubar.addMenu("")
        self.about_action = QAction("", self)
        self.about_action.triggered.connect(self._on_about)
        self.help_menu.addAction(self.about_action)

    def _setup_status_bar(self):
        self.status_label = QLabel()
        self.status_bar.addWidget(self.status_label)
        self.status_info_label = QLabel()
        self.status_info_label.setStyleSheet("color: #888;")
        self.status_bar.addPermanentWidget(self.status_info_label)

    def _init_after_ui(self):
        w, h = self.config_mgr.get_window_size()
        x, y = self.config_mgr.get_window_position()
        if w > 0 and h > 0:
            self.resize(w, h)
        if x >= 0 and y >= 0:
            self.move(x, y)

        self._init_directory()
        self._refresh_projects()
        self._update_status()

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

        self.dir_path_label.setText(self.current_dir)
        if self.current_dir:
            self.config_mgr.add_to_history(self.current_dir)

    def _show_first_launch(self):
        dialog = FirstLaunchDialog(self.i18n, self)
        if dialog.exec_() == QDialog.Accepted:
            cfg = dialog.result_config
            self.config_mgr.set_zotero_version(cfg["zotero_version"])
            self.config_mgr.set_zotero_install_dir(cfg["zotero_install_dir"])
            self.config_mgr.set_templates_root(cfg["templates_root"])
            self.config_mgr.set_profiles_current(cfg["profiles_current"])
            self.config_mgr.set_profiles_default(cfg["profiles_default"])
            self.config_mgr.set_creation_method(cfg["creation_method"])
            self.current_dir = cfg["profiles_current"]
            self.dir_path_label.setText(self.current_dir)
            self.config_mgr.add_to_history(self.current_dir)
        else:
            QTimer.singleShot(0, self.close)

    def _refresh_projects(self):
        self.table.setRowCount(0)
        self.profiles = []

        if not self.current_dir or not is_valid_directory(self.current_dir):
            self._update_status()
            return

        self.profiles = self.controller.get_projects(self.current_dir)
        if not self.profiles:
            self._update_status()
            return

        self.table.setRowCount(len(self.profiles))
        ui_lang = self.i18n.get_language()

        for row, profile in enumerate(self.profiles):
            # 1. 项目名称
            name_item = QTableWidgetItem(profile.name)
            name_item.setIcon(self.style().standardIcon(QStyle.SP_FileIcon))
            name_item.setData(Qt.UserRole, profile)
            self.table.setItem(row, 0, name_item)

            # 2. 界面语言
            lang_code = self.controller.get_project_language(profile.project_path)
            display_lang = get_display_language(lang_code, ui_lang)
            lang_item = QTableWidgetItem(display_lang)
            lang_item.setToolTip(self.i18n.tr("language_column_tooltip"))
            lang_item.setData(Qt.UserRole, profile)
            self.table.setItem(row, 1, lang_item)

            # 3. 路径
            path_display = profile.project_path
            if len(path_display) > 60:
                path_display = path_display[:57] + "..."
            path_item = QTableWidgetItem(path_display)
            path_item.setToolTip(profile.project_path)
            path_item.setData(Qt.UserRole, profile)
            self.table.setItem(row, 2, path_item)

            # 4. 文献
            item_count = profile.get_item_count()
            count_str = str(item_count) if item_count >= 0 else "?"
            count_item = QTableWidgetItem(count_str)
            count_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            count_item.setData(Qt.UserRole, profile)
            self.table.setItem(row, 3, count_item)

            # 5. 插件
            plugin_count = profile.get_plugin_count()
            plugin_item = QTableWidgetItem(str(plugin_count))
            plugin_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            plugin_item.setData(Qt.UserRole, profile)
            self.table.setItem(row, 4, plugin_item)

            # 6. 最后使用
            try:
                mtime = os.path.getmtime(profile.project_path)
                import datetime
                dt = datetime.datetime.fromtimestamp(mtime)
                last_use = dt.strftime("%Y-%m-%d")
            except:
                last_use = "--"
            time_item = QTableWidgetItem(last_use)
            time_item.setData(Qt.UserRole, profile)
            self.table.setItem(row, 5, time_item)

            # 7. 操作按钮
            btn = QPushButton(self.i18n.tr("btn_launch"))
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #2b7a62;
                    color: white;
                    border: none;
                    border-radius: 3px;
                    padding: 2px 8px;
                    font-size: 10px;
                    max-width: 60px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #1e5f4a;
                }
            """)
            btn.clicked.connect(lambda p=profile: self._on_launch_project(p))
            self.table.setCellWidget(row, 6, btn)

        self.table.resizeColumnsToContents()
        self.table.horizontalHeader().setStretchLastSection(False)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)

        self._update_status()

    def _update_status(self):
        count = len(self.profiles)
        version = self.config.zotero_version
        version_text = f"Zotero {version}" if version else "未设置版本"
        self.status_label.setText("✅ 就绪")
        self.status_info_label.setText(f"项目: {count}  |  {version_text}")

    def retranslate_ui(self):
        self.setWindowTitle(self.i18n.tr("app_title"))
        self.refresh_btn.setText(self.i18n.tr("btn_refresh"))
        self.new_btn.setText(self.i18n.tr("btn_new"))
        self.pref_btn.setText(self.i18n.tr("btn_preferences"))

        lang = self.i18n.get_language()
        self.lang_btn.setText("中" if lang == "zh_CN" else "EN")
        self.lang_btn.setToolTip(self.i18n.tr("tooltip_lang_switch"))

        self.dir_label.setText(self.i18n.tr("label_current_dir"))
        self.dir_browse_btn.setText(self.i18n.tr("btn_browse"))
        self.dir_default_btn.setText(self.i18n.tr("btn_set_default"))

        self.file_menu.setTitle(self.i18n.tr("menu_file"))
        self.new_action.setText(self.i18n.tr("menu_new_project"))
        self.refresh_action.setText(self.i18n.tr("menu_refresh"))
        self.open_folder_action.setText(self.i18n.tr("menu_open_folder"))
        self.exit_action.setText(self.i18n.tr("menu_exit"))

        self.edit_menu.setTitle(self.i18n.tr("menu_edit"))
        self.shortcut_action.setText(self.i18n.tr("menu_create_shortcut"))
        self.delete_action.setText(self.i18n.tr("menu_delete"))
        self.pref_action.setText(self.i18n.tr("menu_preferences"))

        self.help_menu.setTitle(self.i18n.tr("menu_help"))
        self.about_action.setText(self.i18n.tr("menu_about"))

        self.table.setHorizontalHeaderLabels([
            self.i18n.tr("table_header_name"),
            self.i18n.tr("table_header_language"),
            self.i18n.tr("table_header_path"),
            self.i18n.tr("table_header_items"),
            self.i18n.tr("table_header_plugins"),
            self.i18n.tr("table_header_last_used"),
            self.i18n.tr("table_header_action")
        ])
        for row in range(self.table.rowCount()):
            btn = self.table.cellWidget(row, 6)
            if btn:
                btn.setText(self.i18n.tr("btn_launch"))

        self._update_status()

    # ----- 事件处理 -----
    def _on_switch_language(self):
        current = self.i18n.get_language()
        new_lang = "en_US" if current == "zh_CN" else "zh_CN"
        self.i18n.set_language(new_lang)
        self.config_mgr.set_language(new_lang)
        self.retranslate_ui()
        self._refresh_projects()

    def _on_refresh(self):
        self._refresh_projects()

    # ------------------------------------------------------------
    # 新建项目：直接打开对话框，所有业务逻辑由 controller 处理
    # 主窗口不再进行任何模板检查，避免弹窗干扰
    # 添加调试打印以确认执行路径
    # ------------------------------------------------------------
    def _on_new_project(self):
        print(f"[DEBUG] main_window._on_new_project: creation_method={self.config.creation_method}")
        dialog = NewProjectDialog(self.i18n, self.config, self)
        if dialog.exec_() == QDialog.Accepted and dialog.result_data:
            name, location, language, create_shortcut = dialog.result_data
            print(f"[DEBUG] Creating project: name={name}, method={self.config.creation_method}")
            success, msg, project_path = self.controller.create_project(
                project_name=name,
                profiles_dir=location,
                templates_root=self.config.templates_root,
                zotero_version=self.config.zotero_version,
                zotero_install_dir=self.config.zotero_install_dir,
                language=language,
                create_shortcut=create_shortcut,
                creation_method=self.config.creation_method
            )
            if success:
                QMessageBox.information(self, "", f"✅ 项目 '{name}' 创建成功！")
                self.current_dir = location
                self.dir_path_label.setText(location)
                self.config_mgr.set_profiles_current(location)
                self.config_mgr.add_to_history(location)
                self._refresh_projects()
            else:
                QMessageBox.critical(self, "", msg)

    def _on_launch_project(self, profile: Profile):
        if not self.config.zotero_install_dir:
            QMessageBox.warning(self, "", "请设置 Zotero 安装路径")
            return
        if self.controller.launch_project(profile.project_path, profile.name, self.config.zotero_install_dir):
            pass
        else:
            QMessageBox.warning(self, "", "启动失败")

    def _on_item_double_clicked(self, item):
        profile = item.data(Qt.UserRole)
        if profile:
            self._on_launch_project(profile)

    def _on_item_clicked(self, item):
        self.selected_row = item.row()
        if item.column() == 1:
            profile = item.data(Qt.UserRole)
            if profile:
                self._on_change_language(profile)

    def _on_context_menu(self, pos):
        row = self.table.rowAt(pos.y())
        if row < 0:
            return
        profile = self.table.item(row, 0).data(Qt.UserRole)
        if not profile:
            return

        menu = QMenu(self)
        launch_action = menu.addAction(self.i18n.tr("menu_launch"))
        launch_action.triggered.connect(lambda: self._on_launch_project(profile))

        open_action = menu.addAction(self.i18n.tr("menu_open_data_folder"))
        open_action.triggered.connect(lambda: self._on_open_folder_for_profile(profile))

        shortcut_action = menu.addAction(self.i18n.tr("menu_create_shortcut"))
        shortcut_action.triggered.connect(lambda: self._on_create_shortcut_for_profile(profile))

        lang_menu = menu.addMenu(self.i18n.tr("menu_language"))
        lang_zh = lang_menu.addAction(self.i18n.tr("lang_chinese"))
        lang_zh.triggered.connect(lambda: self._on_set_language(profile, 'zh-CN'))
        lang_en = lang_menu.addAction(self.i18n.tr("lang_english"))
        lang_en.triggered.connect(lambda: self._on_set_language(profile, 'en-US'))
        lang_sys = lang_menu.addAction(self.i18n.tr("lang_system"))
        lang_sys.triggered.connect(lambda: self._on_set_language(profile, ''))

        menu.addSeparator()
        delete_action = menu.addAction(self.i18n.tr("menu_delete_project"))
        delete_action.setIcon(self.style().standardIcon(QStyle.SP_DialogCancelButton))
        delete_action.triggered.connect(lambda: self._on_delete_project_for_profile(profile))

        menu.exec_(self.table.viewport().mapToGlobal(pos))

    def _on_open_folder(self):
        row = self.table.currentRow()
        if row < 0:
            return
        profile = self.table.item(row, 0).data(Qt.UserRole)
        if profile:
            self._on_open_folder_for_profile(profile)

    def _on_open_folder_for_profile(self, profile: Profile):
        path = profile.project_path
        if not os.path.exists(path):
            QMessageBox.warning(self, "", "文件夹不存在")
            return
        try:
            os.startfile(path)
        except Exception as e:
            QMessageBox.warning(self, "", f"打开失败: {e}")

    def _on_delete_project(self):
        row = self.table.currentRow()
        if row < 0:
            return
        profile = self.table.item(row, 0).data(Qt.UserRole)
        if profile:
            self._on_delete_project_for_profile(profile)

    def _on_delete_project_for_profile(self, profile: Profile):
        if self.controller.is_project_in_use(profile.project_path):
            dialog = ProjectInUseDialog(self.i18n, profile.name, profile.project_path, self)
            if dialog.exec_() == QDialog.Accepted:
                self._on_delete_project_for_profile(profile)
            return

        size_mb = profile.get_size() / (1024 * 1024)
        confirm_dialog = DeleteConfirmDialog(self.i18n, profile, size_mb, self)
        if confirm_dialog.exec_() != QDialog.Accepted:
            return

        success, msg = self.controller.delete_project(
            profile.project_path,
            profile.name,
            self.current_dir
        )
        if success:
            self.config_mgr.remove_project_note(profile.name)
            success_dialog = DeleteSuccessDialog(
                self.i18n, profile.name, profile.project_path, size_mb, self
            )
            success_dialog.exec_()
            self._refresh_projects()
        else:
            failed_dialog = DeleteFailedDialog(self.i18n, profile.name, msg, self)
            if failed_dialog.exec_() == QDialog.Accepted:
                self._on_delete_project_for_profile(profile)

    def _on_create_shortcut(self):
        row = self.table.currentRow()
        if row < 0:
            return
        profile = self.table.item(row, 0).data(Qt.UserRole)
        if profile:
            self._on_create_shortcut_for_profile(profile)

    def _on_create_shortcut_for_profile(self, profile: Profile):
        if not self.config.zotero_install_dir:
            QMessageBox.warning(self, "", "请设置 Zotero 安装路径")
            return
        success, msg = self.controller.create_shortcut(
            profile.project_path,
            profile.name,
            self.config.zotero_install_dir
        )
        if success:
            QMessageBox.information(self, "", "✅ 快捷方式已创建")
        else:
            QMessageBox.warning(self, "", f"创建失败: {msg}")

    def _on_change_language(self, profile: Profile):
        current_lang = self.controller.get_project_language(profile.project_path)
        profiles_dir = Path(profile.project_path) / "profiles"
        dialog = LanguageDialog(
            self.i18n,
            profile.name,
            str(profiles_dir),
            current_lang or '',
            self
        )
        if dialog.exec_() == QDialog.Accepted:
            self._refresh_projects()

    def _on_set_language(self, profile: Profile, lang_code: str):
        success = self.controller.set_project_language(profile.project_path, lang_code)
        if success:
            self._refresh_projects()
            QMessageBox.information(self, "", self.i18n.tr("language_dialog_success"))
        else:
            QMessageBox.warning(self, "", self.i18n.tr("language_dialog_failed"))

    def _on_browse_dir(self):
        path = QFileDialog.getExistingDirectory(self, self.i18n.tr("btn_browse"), self.current_dir)
        if path and is_valid_directory(path):
            self.current_dir = path
            self.dir_path_label.setText(path)
            self.config_mgr.set_profiles_current(path)
            self.config_mgr.add_to_history(path)
            self._refresh_projects()

    def _on_set_default_dir(self):
        if self.current_dir:
            self.config_mgr.set_profiles_default(self.current_dir)
            self.dir_path_label.setText(self.current_dir + " ⭐")
            QMessageBox.information(self, "", "已设为默认目录")

    def _show_history_menu(self):
        history = self.config_mgr.get_profiles_history()
        if not history:
            return
        menu = QMenu(self)
        for path in history:
            action = menu.addAction(path)
            action.setData(path)
            if path == self.current_dir:
                action.setIcon(self.style().standardIcon(QStyle.SP_DialogApplyButton))
        action = menu.exec_(self.dir_history_btn.mapToGlobal(self.dir_history_btn.rect().bottomLeft()))
        if action:
            path = action.data()
            if path and is_valid_directory(path):
                self.current_dir = path
                self.dir_path_label.setText(path)
                self.config_mgr.set_profiles_current(path)
                self.config_mgr.add_to_history(path)
                self._refresh_projects()

    def _on_preferences(self):
        dialog = PreferencesDialog(self.i18n, self.config_mgr, self)
        if dialog.exec_() == QDialog.Accepted:
            self._refresh_projects()
            self._update_status()
            self.retranslate_ui()
            self.current_dir = self.config_mgr.get_profiles_current()
            self.dir_path_label.setText(self.current_dir)

    def _on_about(self):
        QMessageBox.about(
            self,
            self.i18n.tr("menu_about"),
            "Zotero Project Launcher\n版本 1.0.0\n\n"
            "一款轻量级的多项目 Zotero 启动管理工具。\n"
            "基于 Zotero -datadir 参数实现项目完全隔离。"
        )

    def closeEvent(self, event):
        self.config_mgr.set_window_size(self.width(), self.height())
        self.config_mgr.set_window_position(self.x(), self.y())
        event.accept()
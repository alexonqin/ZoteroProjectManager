# -*- coding: utf-8 -*-
"""
主窗口
"""

import os
import sys
from pathlib import Path

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QListWidget, QListWidgetItem, QStatusBar,
    QMessageBox, QFileDialog, QMenu, QMenuBar, QDialog,
    QStyle
)
from PySide6.QtCore import Qt, QTimer, QSize  # 新增 QSize
from PySide6.QtGui import QAction, QKeySequence

from models.profile import Profile
from controllers.zotero_controller import ZoteroController
from utils.i18n import I18n
from utils.config_manager import ConfigManager
from utils.path_utils import is_valid_directory
from views.widgets.project_card import ProjectCard
from views.dialogs.new_project_dialog import NewProjectDialog
from views.dialogs.delete_confirm_dialog import DeleteConfirmDialog
from views.dialogs.preferences_dialog import PreferencesDialog
from views.dialogs.first_launch_dialog import FirstLaunchDialog


class MainWindow(QMainWindow):
    """主窗口"""

    def __init__(self, i18n: I18n, config_mgr: ConfigManager):
        super().__init__()
        self.i18n = i18n
        self.config_mgr = config_mgr
        self.config = config_mgr.get_config()
        self.controller = ZoteroController()

        self.profiles = []
        self.current_dir = ""
        self.card_widgets = {}

        self._setup_ui()
        self._setup_menu()
        self._setup_status_bar()
        self._init_after_ui()
        self.retranslate_ui()

    def _setup_ui(self):
        self.setMinimumSize(600, 400)

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

        # 项目列表
        self.list_widget = QListWidget()
        self.list_widget.setSpacing(6)
        self.list_widget.setStyleSheet("""
            QListWidget::item {
                background: transparent;
                border: none;
            }
            QListWidget::item:selected {
                background: transparent;
            }
        """)
        main_layout.addWidget(self.list_widget)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

    def _setup_menu(self):
        menubar = self.menuBar()

        # 文件菜单
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

        # 编辑菜单
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

        # 帮助菜单
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
            self.current_dir = cfg["profiles_current"]
            self.dir_path_label.setText(self.current_dir)
            self.config_mgr.add_to_history(self.current_dir)
        else:
            QTimer.singleShot(0, self.close)

    def _refresh_projects(self):
        self.list_widget.clear()
        self.card_widgets.clear()

        if not self.current_dir or not is_valid_directory(self.current_dir):
            self._update_status()
            return

        self.profiles = self.controller.get_projects(self.current_dir)
        for profile in self.profiles:
            item = QListWidgetItem()
            # 修正：使用 QSize
            item.setSizeHint(QSize(80, 80))
            card = ProjectCard(profile)
            card.launch_requested.connect(self._on_launch_project)
            card.open_folder_requested.connect(self._on_open_folder_for_profile)
            card.delete_requested.connect(self._on_delete_project_for_profile)
            card.create_shortcut_requested.connect(self._on_create_shortcut_for_profile)

            self.list_widget.addItem(item)
            self.list_widget.setItemWidget(item, card)
            self.card_widgets[profile.name] = card

        self._update_status()

    def _update_status(self):
        i18n = self.i18n
        count = len(self.profiles)
        version = self.config.zotero_version
        if version:
            version_text = "Zotero {}".format(version)
        else:
            version_text = "未设置版本"
        self.status_label.setText("✅ 就绪")
        self.status_info_label.setText("项目: {}  |  {}".format(count, version_text))

    def retranslate_ui(self):
        i18n = self.i18n
        self.setWindowTitle(i18n.tr("app_title"))

        self.refresh_btn.setText(i18n.tr("btn_refresh"))
        self.new_btn.setText(i18n.tr("btn_new"))
        self.pref_btn.setText(i18n.tr("btn_preferences"))

        lang = i18n.get_language()
        self.lang_btn.setText("中" if lang == "zh_CN" else "EN")
        self.lang_btn.setToolTip(i18n.tr("tooltip_lang_switch"))

        self.dir_label.setText(i18n.tr("label_current_dir"))
        self.dir_browse_btn.setText(i18n.tr("btn_browse"))
        self.dir_default_btn.setText(i18n.tr("btn_set_default"))

        # 设置 tooltip
        self.dir_path_label.setToolTip(i18n.tr("dir_tooltip"))
        self.dir_history_btn.setToolTip(i18n.tr("history_tooltip"))
        self.dir_browse_btn.setToolTip(i18n.tr("browse_tooltip"))
        self.dir_default_btn.setToolTip(i18n.tr("default_tooltip"))

        self.file_menu.setTitle(i18n.tr("menu_file"))
        self.new_action.setText(i18n.tr("menu_new_project"))
        self.refresh_action.setText(i18n.tr("menu_refresh"))
        self.open_folder_action.setText(i18n.tr("menu_open_folder"))
        self.exit_action.setText(i18n.tr("menu_exit"))

        self.edit_menu.setTitle(i18n.tr("menu_edit"))
        self.shortcut_action.setText(i18n.tr("menu_create_shortcut"))
        self.delete_action.setText(i18n.tr("menu_delete"))
        self.pref_action.setText(i18n.tr("menu_preferences"))

        self.help_menu.setTitle(i18n.tr("menu_help"))
        self.about_action.setText(i18n.tr("menu_about"))

        self._update_status()

    # ----- 事件处理 -----
    def _on_switch_language(self):
        current = self.i18n.get_language()
        new_lang = "en_US" if current == "zh_CN" else "zh_CN"
        self.i18n.set_language(new_lang)
        self.config_mgr.set_language(new_lang)
        self.retranslate_ui()

    def _on_refresh(self):
        self._refresh_projects()

    def _on_new_project(self):
        if not self.config.zotero_version:
            QMessageBox.warning(self, "", "请先在偏好设置中设置 Zotero 版本号")
            return
        if not self.config.zotero_install_dir:
            QMessageBox.warning(self, "", "请先在偏好设置中设置 Zotero 安装路径")
            return
        if not self.config.templates_root:
            QMessageBox.warning(self, "", "请先在偏好设置中设置模板目录")
            return

        dialog = NewProjectDialog(self.i18n, self.config, self)
        if dialog.exec_() == QDialog.Accepted and dialog.result_data:
            name, location, create_shortcut = dialog.result_data
            success, msg, project_path = self.controller.create_project(
                project_name=name,
                profiles_dir=location,
                templates_root=self.config.templates_root,
                zotero_version=self.config.zotero_version,
                zotero_install_dir=self.config.zotero_install_dir,
                create_shortcut=create_shortcut
            )
            if success:
                QMessageBox.information(self, "", "✅ 项目 '{}' 创建成功！".format(name))
                self.current_dir = location
                self.dir_path_label.setText(location)
                self.config_mgr.set_profiles_current(location)
                self.config_mgr.add_to_history(location)
                self._refresh_projects()
            else:
                QMessageBox.critical(self, "", msg)

    def _on_launch_project(self, profile: Profile):
        if not self.config.zotero_install_dir:
            QMessageBox.warning(self, "", "请先在偏好设置中设置 Zotero 安装路径")
            return
        success = self.controller.launch_project(profile.project_path, self.config.zotero_install_dir)
        if not success:
            QMessageBox.warning(self, "", "启动失败")

    def _on_open_folder(self):
        current_item = self.list_widget.currentItem()
        if not current_item:
            return
        card = self.list_widget.itemWidget(current_item)
        if card:
            self._on_open_folder_for_profile(card.profile)

    def _on_open_folder_for_profile(self, profile: Profile):
        path = profile.project_path
        if not os.path.exists(path):
            QMessageBox.warning(self, "", "文件夹不存在")
            return
        try:
            os.startfile(path)
        except Exception as e:
            QMessageBox.warning(self, "", "打开失败: {}".format(e))

    def _on_delete_project(self):
        current_item = self.list_widget.currentItem()
        if not current_item:
            return
        card = self.list_widget.itemWidget(current_item)
        if card:
            self._on_delete_project_for_profile(card.profile)

    def _on_delete_project_for_profile(self, profile: Profile):
        dialog = DeleteConfirmDialog(self.i18n, profile.name, self)
        if dialog.exec_() == QDialog.Accepted:
            success, msg = self.controller.delete_project(profile.project_path, profile.name)
            if success:
                QMessageBox.information(self, "", msg)
                self._refresh_projects()
            else:
                QMessageBox.critical(self, "", msg)

    def _on_create_shortcut(self):
        current_item = self.list_widget.currentItem()
        if not current_item:
            return
        card = self.list_widget.itemWidget(current_item)
        if card:
            self._on_create_shortcut_for_profile(card.profile)

    def _on_create_shortcut_for_profile(self, profile: Profile):
        if not self.config.zotero_install_dir:
            QMessageBox.warning(self, "", "请先在偏好设置中设置 Zotero 安装路径")
            return
        success, msg = self.controller.create_shortcut(
            profile.project_path,
            profile.name,
            self.config.zotero_install_dir
        )
        if success:
            QMessageBox.information(self, "", "✅ 快捷方式已创建")
        else:
            QMessageBox.warning(self, "", "创建失败: {}".format(msg))

    def _on_browse_dir(self):
        path = QFileDialog.getExistingDirectory(self, self.i18n.tr("btn_browse"), self.current_dir)
        if not path:
            return
        if not is_valid_directory(path):
            QMessageBox.warning(self, "", "无效目录")
            return
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
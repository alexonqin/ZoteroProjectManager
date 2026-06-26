# -*- coding: utf-8 -*-
"""
主菜单组件
"""

from PySide6.QtWidgets import QMenuBar, QMenu
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtCore import Signal

from utils.i18n import I18n


class MainMenu(QMenuBar):
    # 文件菜单
    new_triggered = Signal()
    import_triggered = Signal()
    refresh_triggered = Signal()
    open_folder_triggered = Signal()
    export_triggered = Signal()
    exit_triggered = Signal()

    # 编辑菜单
    rename_triggered = Signal()
    delete_triggered = Signal()
    preferences_triggered = Signal()

    # 帮助菜单
    about_triggered = Signal()
    repair_launch_triggered = Signal()      # 新增：启动修复
    repair_shortcut_triggered = Signal()    # 新增：快捷方式修复

    def __init__(self, i18n: I18n, parent=None):
        super().__init__(parent)
        self.i18n = i18n
        self._setup_ui()
        self.retranslate_ui()

    def _setup_ui(self):
        # 文件菜单
        self.file_menu = self.addMenu("")
        self.new_action = QAction("", self)
        self.new_action.setShortcut(QKeySequence("Ctrl+N"))
        self.new_action.triggered.connect(self.new_triggered.emit)
        self.file_menu.addAction(self.new_action)

        self.import_action = QAction("", self)
        self.import_action.setShortcut(QKeySequence("Ctrl+I"))
        self.import_action.triggered.connect(self.import_triggered.emit)
        self.file_menu.addAction(self.import_action)

        self.file_menu.addSeparator()

        self.refresh_action = QAction("", self)
        self.refresh_action.setShortcut(QKeySequence("F5"))
        self.refresh_action.triggered.connect(self.refresh_triggered.emit)
        self.file_menu.addAction(self.refresh_action)

        self.open_folder_action = QAction("", self)
        self.open_folder_action.setShortcut(QKeySequence("Ctrl+O"))
        self.open_folder_action.triggered.connect(self.open_folder_triggered.emit)
        self.file_menu.addAction(self.open_folder_action)

        self.file_menu.addSeparator()

        self.export_action = QAction("", self)
        self.export_action.setShortcut(QKeySequence("Ctrl+E"))
        self.export_action.triggered.connect(self.export_triggered.emit)
        self.file_menu.addAction(self.export_action)

        self.file_menu.addSeparator()

        self.exit_action = QAction("", self)
        self.exit_action.setShortcut(QKeySequence("Ctrl+Q"))
        self.exit_action.triggered.connect(self.exit_triggered.emit)
        self.file_menu.addAction(self.exit_action)

        # 编辑菜单
        self.edit_menu = self.addMenu("")
        self.rename_action = QAction("", self)
        self.rename_action.setShortcut(QKeySequence("F2"))
        self.rename_action.triggered.connect(self.rename_triggered.emit)
        self.edit_menu.addAction(self.rename_action)

        self.edit_menu.addSeparator()

        self.delete_action = QAction("", self)
        self.delete_action.setShortcut(QKeySequence("Delete"))
        self.delete_action.triggered.connect(self.delete_triggered.emit)
        self.edit_menu.addAction(self.delete_action)

        self.edit_menu.addSeparator()

        self.pref_action = QAction("", self)
        self.pref_action.setShortcut(QKeySequence("Ctrl+P"))
        self.pref_action.triggered.connect(self.preferences_triggered.emit)
        self.edit_menu.addAction(self.pref_action)

        # 帮助菜单
        self.help_menu = self.addMenu("")

        # 项目修复子菜单
        self.repair_menu = QMenu("", self.help_menu)
        self.help_menu.addMenu(self.repair_menu)

        self.repair_launch_action = QAction("", self.repair_menu)
        self.repair_launch_action.triggered.connect(self.repair_launch_triggered.emit)
        self.repair_menu.addAction(self.repair_launch_action)

        self.repair_shortcut_action = QAction("", self.repair_menu)
        self.repair_shortcut_action.triggered.connect(self.repair_shortcut_triggered.emit)
        self.repair_menu.addAction(self.repair_shortcut_action)

        self.help_menu.addSeparator()

        self.about_action = QAction("", self)
        self.about_action.triggered.connect(self.about_triggered.emit)
        self.help_menu.addAction(self.about_action)

    def retranslate_ui(self):
        self.file_menu.setTitle(self.i18n.tr("menu_file"))
        self.new_action.setText(self.i18n.tr("menu_new_project"))
        self.import_action.setText(self.i18n.tr("menu_import_project"))
        self.refresh_action.setText(self.i18n.tr("menu_refresh"))
        self.open_folder_action.setText(self.i18n.tr("menu_open_folder"))
        self.export_action.setText(self.i18n.tr("menu_export_project"))
        self.exit_action.setText(self.i18n.tr("menu_exit"))

        self.edit_menu.setTitle(self.i18n.tr("menu_edit"))
        self.rename_action.setText(self.i18n.tr("menu_rename"))
        self.delete_action.setText(self.i18n.tr("menu_delete"))
        self.pref_action.setText(self.i18n.tr("menu_preferences"))

        self.help_menu.setTitle(self.i18n.tr("menu_help"))
        self.repair_menu.setTitle(self.i18n.tr("menu_repair"))
        self.repair_launch_action.setText(self.i18n.tr("menu_repair_launch"))
        self.repair_shortcut_action.setText(self.i18n.tr("menu_repair_shortcut"))
        self.about_action.setText(self.i18n.tr("menu_about"))
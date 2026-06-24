# -*- coding: utf-8 -*-
"""
主菜单组件
"""

from PySide6.QtWidgets import QMenuBar
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtCore import Signal

from utils.i18n import I18n


class MainMenu(QMenuBar):
    """
    主菜单组件
    包含文件、编辑、帮助三个菜单
    """

    # 文件菜单信号
    new_triggered = Signal()
    import_triggered = Signal()
    refresh_triggered = Signal()
    open_folder_triggered = Signal()
    export_triggered = Signal()
    exit_triggered = Signal()

    # 编辑菜单信号（移除 shortcut_triggered）
    delete_triggered = Signal()
    preferences_triggered = Signal()

    # 帮助菜单信号
    about_triggered = Signal()

    def __init__(self, i18n: I18n, parent=None):
        super().__init__(parent)
        self.i18n = i18n

        self._setup_ui()
        self.retranslate_ui()

    def _setup_ui(self):
        # ----- 文件菜单 -----
        self.file_menu = self.addMenu("")

        # 新建项目
        self.new_action = QAction("", self)
        self.new_action.setShortcut(QKeySequence("Ctrl+N"))
        self.new_action.triggered.connect(self.new_triggered.emit)
        self.file_menu.addAction(self.new_action)

        # 导入项目
        self.import_action = QAction("", self)
        self.import_action.setShortcut(QKeySequence("Ctrl+I"))
        self.import_action.triggered.connect(self.import_triggered.emit)
        self.file_menu.addAction(self.import_action)

        self.file_menu.addSeparator()

        # 刷新列表
        self.refresh_action = QAction("", self)
        self.refresh_action.setShortcut(QKeySequence("F5"))
        self.refresh_action.triggered.connect(self.refresh_triggered.emit)
        self.file_menu.addAction(self.refresh_action)

        # 打开项目文件夹
        self.open_folder_action = QAction("", self)
        self.open_folder_action.setShortcut(QKeySequence("Ctrl+O"))
        self.open_folder_action.triggered.connect(self.open_folder_triggered.emit)
        self.file_menu.addAction(self.open_folder_action)

        self.file_menu.addSeparator()

        # 导出项目
        self.export_action = QAction("", self)
        self.export_action.setShortcut(QKeySequence("Ctrl+E"))
        self.export_action.triggered.connect(self.export_triggered.emit)
        self.file_menu.addAction(self.export_action)

        self.file_menu.addSeparator()

        # 退出
        self.exit_action = QAction("", self)
        self.exit_action.setShortcut(QKeySequence("Ctrl+Q"))
        self.exit_action.triggered.connect(self.exit_triggered.emit)
        self.file_menu.addAction(self.exit_action)

        # ----- 编辑菜单 -----
        self.edit_menu = self.addMenu("")

        # 删除项目（保留）
        self.delete_action = QAction("", self)
        self.delete_action.setShortcut(QKeySequence("Delete"))
        self.delete_action.triggered.connect(self.delete_triggered.emit)
        self.edit_menu.addAction(self.delete_action)

        self.edit_menu.addSeparator()

        # 偏好设置
        self.pref_action = QAction("", self)
        self.pref_action.setShortcut(QKeySequence("Ctrl+P"))
        self.pref_action.triggered.connect(self.preferences_triggered.emit)
        self.edit_menu.addAction(self.pref_action)

        # ----- 帮助菜单 -----
        self.help_menu = self.addMenu("")

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
        self.delete_action.setText(self.i18n.tr("menu_delete"))
        self.pref_action.setText(self.i18n.tr("menu_preferences"))

        self.help_menu.setTitle(self.i18n.tr("menu_help"))
        self.about_action.setText(self.i18n.tr("menu_about"))
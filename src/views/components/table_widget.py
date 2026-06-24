# -*- coding: utf-8 -*-
"""
项目表格组件
"""

import os
from pathlib import Path
from typing import List

from PySide6.QtWidgets import (
    QTableWidget, QTableWidgetItem, QHeaderView, QPushButton,
    QAbstractItemView, QMenu, QStyle, QSizePolicy,
    QWidget, QHBoxLayout
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QAction

from models.profile import Profile
from utils.language_utils import get_display_language, read_language
from utils.i18n import I18n


class TableWidget(QTableWidget):
    # 信号
    launch_requested = Signal(Profile)
    open_folder_requested = Signal(Profile)
    create_shortcut_requested = Signal(Profile)
    delete_requested = Signal(Profile)
    change_language_requested = Signal(Profile)
    export_requested = Signal(Profile)

    def __init__(self, i18n: I18n, parent=None):
        super().__init__(parent)
        self.i18n = i18n
        self.profiles = []

        self._setup_ui()
        self.retranslate_ui()

    def _setup_ui(self):
        self.setColumnCount(7)
        self.setHorizontalHeaderLabels([
            "项目名称", "界面语言", "路径", "文献", "插件", "最后使用", "操作"
        ])

        self.setColumnWidth(0, 130)
        self.setColumnWidth(1, 90)
        self.setColumnWidth(3, 60)
        self.setColumnWidth(4, 60)
        self.setColumnWidth(5, 100)
        self.setColumnWidth(6, 70)

        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.Interactive)
        self.horizontalHeader().setSectionResizeMode(1, QHeaderView.Interactive)
        self.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.horizontalHeader().setSectionResizeMode(3, QHeaderView.Interactive)
        self.horizontalHeader().setSectionResizeMode(4, QHeaderView.Interactive)
        self.horizontalHeader().setSectionResizeMode(5, QHeaderView.Interactive)
        self.horizontalHeader().setSectionResizeMode(6, QHeaderView.Interactive)

        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setShowGrid(False)
        self.setAlternatingRowColors(True)

        print(self.verticalHeader().defaultSectionSize())

        self.setStyleSheet("""
            QTableWidget::item:selected {
                background-color: #e3edf7;
                color: #1a1a1a;
            }
            QTableWidget::item:hover {
                background-color: #f0f4f8;
                color: #1a1a1a;
            }
        """)

        self.setSortingEnabled(True)

        self.itemDoubleClicked.connect(self._on_item_double_clicked)
        self.itemClicked.connect(self._on_item_clicked)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._on_context_menu)

    def retranslate_ui(self):
        self.setHorizontalHeaderLabels([
            self.i18n.tr("table_header_name"),
            self.i18n.tr("table_header_language"),
            self.i18n.tr("table_header_path"),
            self.i18n.tr("table_header_items"),
            self.i18n.tr("table_header_plugins"),
            self.i18n.tr("table_header_last_used"),
            self.i18n.tr("table_header_action")
        ])
        self._update_all_buttons()

        if self.profiles:
            ui_lang = self.i18n.get_language()
            self.refresh_data(self.profiles, ui_lang)

    def refresh_data(self, profiles: List[Profile], ui_lang: str):
        valid_profiles = [p for p in profiles if isinstance(p, Profile)]
        if len(valid_profiles) != len(profiles):
            print(f"[WARNING] refresh_data: filtered {len(profiles) - len(valid_profiles)} invalid items")

        sort_col = self.horizontalHeader().sortIndicatorSection()
        sort_order = self.horizontalHeader().sortIndicatorOrder()

        self.setSortingEnabled(False)
        self.profiles = valid_profiles
        self.setRowCount(0)

        if valid_profiles:
            self.setRowCount(len(valid_profiles))
            for row, profile in enumerate(valid_profiles):
                self._add_row(row, profile, ui_lang)

        self.setSortingEnabled(True)
        if sort_col >= 0:
            self.sortItems(sort_col, sort_order)

        self.horizontalHeader().setStretchLastSection(False)
        self.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)

    def _add_row(self, row: int, profile: Profile, ui_lang: str):
        if not isinstance(profile, Profile):
            print(f"[ERROR] _add_row: invalid profile at row {row}: {profile}")
            return

        # 1. 项目名称
        name_item = QTableWidgetItem(profile.name)
        name_item.setIcon(self.style().standardIcon(QStyle.SP_FileIcon))
        name_item.setData(Qt.UserRole, profile)
        self.setItem(row, 0, name_item)

        # 2. 界面语言
        lang_code = None
        if profile.profiles_path and Path(profile.profiles_path).exists():
            prefs_path = Path(profile.profiles_path) / "prefs.js"
            print(f"[DEBUG] TableWidget: profile={profile.name}, prefs_path={prefs_path}")
            if prefs_path.exists():
                with open(prefs_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    print(f"[DEBUG] TableWidget: prefs.js length={len(content)}, preview={content[:100]}")
            lang_code = read_language(profile.profiles_path)
        print(f"[DEBUG] TableWidget: lang_code={lang_code}")
        display_lang = get_display_language(lang_code, ui_lang)
        lang_item = QTableWidgetItem(display_lang)
        lang_item.setToolTip(self.i18n.tr("language_column_tooltip"))
        lang_item.setData(Qt.UserRole, profile)
        self.setItem(row, 1, lang_item)

        # 3. 路径
        path_display = profile.project_path
        if len(path_display) > 60:
            path_display = path_display[:57] + "..."
        path_item = QTableWidgetItem(path_display)
        path_item.setToolTip(profile.project_path)
        path_item.setData(Qt.UserRole, profile)
        self.setItem(row, 2, path_item)

        # 4. 文献
        item_count = profile.get_item_count()
        if item_count >= 0:
            count_str = f"{item_count:4d}"
        else:
            count_str = "   ?"
        count_item = QTableWidgetItem(count_str)
        count_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        count_item.setData(Qt.UserRole, profile)
        self.setItem(row, 3, count_item)

        # 5. 插件
        plugin_count = profile.get_plugin_count()
        plugin_str = f"{plugin_count:3d}"
        plugin_item = QTableWidgetItem(plugin_str)
        plugin_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        plugin_item.setData(Qt.UserRole, profile)
        self.setItem(row, 4, plugin_item)

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
        self.setItem(row, 5, time_item)

        # 7. 操作按钮（动态获取行）
        btn = QPushButton(self.i18n.tr("btn_launch"))
        btn.setStyleSheet("""
            QPushButton {
                background-color: #2b7a62;
                color: white;
                border: none;
                border-radius: 3px;
                max-width: 60px;
                font-size: 11px;
                padding: 0 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1e5f4a;
            }
        """)
        btn.setFixedHeight(20)
        btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        btn.clicked.connect(self._on_launch_clicked)

        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(btn)
        layout.setAlignment(Qt.AlignCenter)
        self.setCellWidget(row, 6, container)

    def _on_launch_clicked(self):
        """动态获取按钮所在行并启动项目"""
        btn = self.sender()
        if not btn:
            return
        # 获取按钮中心点相对于表格视口的位置
        pos = btn.mapTo(self.viewport(), btn.rect().center())
        index = self.indexAt(pos)
        if not index.isValid():
            print("[ERROR] _on_launch_clicked: invalid index")
            return
        row = index.row()
        if row < 0 or row >= self.rowCount():
            print(f"[ERROR] _on_launch_clicked: row {row} out of range")
            return
        item = self.item(row, 0)
        if not item:
            print(f"[ERROR] _on_launch_clicked: no item at row {row}")
            return
        profile = item.data(Qt.UserRole)
        if isinstance(profile, Profile):
            self.launch_requested.emit(profile)
        else:
            print(f"[ERROR] _on_launch_clicked: invalid profile at row {row}: {profile}")

    def _update_all_buttons(self):
        for row in range(self.rowCount()):
            container = self.cellWidget(row, 6)
            if container:
                btn = container.findChild(QPushButton)
                if btn:
                    btn.setText(self.i18n.tr("btn_launch"))

    def _on_item_double_clicked(self, item):
        profile = item.data(Qt.UserRole)
        if isinstance(profile, Profile):
            self.launch_requested.emit(profile)
        else:
            print(f"[ERROR] TableWidget._on_item_double_clicked: invalid profile from item: {profile}")

    def _on_item_clicked(self, item):
        if item.column() == 1:
            profile = item.data(Qt.UserRole)
            if isinstance(profile, Profile):
                self.change_language_requested.emit(profile)

    def _on_context_menu(self, pos):
        row = self.rowAt(pos.y())
        if row < 0:
            return
        profile = self.item(row, 0).data(Qt.UserRole)
        if not isinstance(profile, Profile):
            return

        menu = QMenu(self)

        launch_action = menu.addAction(self.i18n.tr("menu_launch"))
        launch_action.triggered.connect(lambda: self.launch_requested.emit(profile))

        open_action = menu.addAction(self.i18n.tr("menu_open_data_folder"))
        open_action.triggered.connect(lambda: self.open_folder_requested.emit(profile))

        shortcut_action = menu.addAction(self.i18n.tr("menu_create_shortcut"))
        shortcut_action.triggered.connect(lambda: self.create_shortcut_requested.emit(profile))

        lang_menu = menu.addMenu(self.i18n.tr("menu_language"))
        lang_zh = lang_menu.addAction(self.i18n.tr("lang_chinese"))
        lang_zh.triggered.connect(lambda: self.change_language_requested.emit(profile))
        lang_en = lang_menu.addAction(self.i18n.tr("lang_english"))
        lang_en.triggered.connect(lambda: self.change_language_requested.emit(profile))
        lang_sys = lang_menu.addAction(self.i18n.tr("lang_system"))
        lang_sys.triggered.connect(lambda: self.change_language_requested.emit(profile))

        export_action = menu.addAction(self.i18n.tr("menu_export_project"))
        export_action.triggered.connect(lambda: self.export_requested.emit(profile))

        menu.addSeparator()
        delete_action = menu.addAction(self.i18n.tr("menu_delete_project"))
        delete_action.setIcon(self.style().standardIcon(QStyle.SP_DialogCancelButton))
        delete_action.triggered.connect(lambda: self.delete_requested.emit(profile))

        menu.exec_(self.viewport().mapToGlobal(pos))

    def get_selected_profile(self) -> Profile:
        row = self.currentRow()
        if row < 0:
            return None
        item = self.item(row, 0)
        if not item:
            return None
        profile = item.data(Qt.UserRole)
        return profile if isinstance(profile, Profile) else None
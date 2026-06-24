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
    """
    项目表格组件
    显示项目列表，支持排序、双击启动、右键菜单
    """
    
    # 信号
    launch_requested = Signal(Profile)          # 启动项目
    open_folder_requested = Signal(Profile)     # 打开文件夹
    create_shortcut_requested = Signal(Profile) # 创建快捷方式
    delete_requested = Signal(Profile)          # 删除项目
    change_language_requested = Signal(Profile) # 修改语言
    
    def __init__(self, i18n: I18n, parent=None):
        super().__init__(parent)
        self.i18n = i18n
        self.profiles = []
        
        self._setup_ui()
        self.retranslate_ui()
    
    def _setup_ui(self):
        """初始化表格"""
        self.setColumnCount(7)
        self.setHorizontalHeaderLabels([
            "项目名称", "界面语言", "路径", "文献", "插件", "最后使用", "操作"
        ])
        
        # ---- 列宽设置 ----
        # 除路径列外，其他列为 Interactive（允许用户调整），并设置初始宽度
        self.setColumnWidth(0, 130)   # 项目名称
        self.setColumnWidth(1, 90)    # 界面语言
        # 路径列（索引2）不设固定宽度，使用 Stretch
        self.setColumnWidth(3, 60)    # 文献
        self.setColumnWidth(4, 60)    # 插件
        self.setColumnWidth(5, 100)   # 最后使用
        self.setColumnWidth(6, 70)    # 操作
        
        # 设置列模式
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.Interactive)  # 项目名称
        self.horizontalHeader().setSectionResizeMode(1, QHeaderView.Interactive)  # 界面语言
        self.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)       # 路径
        self.horizontalHeader().setSectionResizeMode(3, QHeaderView.Interactive)  # 文献
        self.horizontalHeader().setSectionResizeMode(4, QHeaderView.Interactive)  # 插件
        self.horizontalHeader().setSectionResizeMode(5, QHeaderView.Interactive)  # 最后使用
        self.horizontalHeader().setSectionResizeMode(6, QHeaderView.Interactive)  # 操作
        
        # 其他表格属性
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setShowGrid(False)
        self.setAlternatingRowColors(True)

        # 查看默认行高（调试用）
        print(self.verticalHeader().defaultSectionSize())
        
        # 样式表
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
        
        # ---- 启用排序 ----
        self.setSortingEnabled(True)
        
        # 信号连接
        self.itemDoubleClicked.connect(self._on_item_double_clicked)
        self.itemClicked.connect(self._on_item_clicked)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._on_context_menu)
    
    def retranslate_ui(self):
        """刷新表头文字和所有显示文本（包括语言列）"""
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
        
        # 刷新语言列显示
        if self.profiles:
            ui_lang = self.i18n.get_language()
            self.refresh_data(self.profiles, ui_lang)
    
    def refresh_data(self, profiles: List[Profile], ui_lang: str):
        """
        刷新表格数据
        保留当前排序状态，填充完成后恢复排序
        """
        # 1. 保存当前排序状态
        sort_col = self.horizontalHeader().sortIndicatorSection()
        sort_order = self.horizontalHeader().sortIndicatorOrder()
        
        # 2. 禁用排序，防止填充时触发排序
        self.setSortingEnabled(False)
        
        self.profiles = profiles
        self.setRowCount(0)
        
        if profiles:
            self.setRowCount(len(profiles))
            for row, profile in enumerate(profiles):
                self._add_row(row, profile, ui_lang)
        
        # 3. 重新启用排序
        self.setSortingEnabled(True)
        
        # 4. 恢复排序状态（如果之前有排序列）
        if sort_col >= 0:
            self.sortItems(sort_col, sort_order)
        
        # 5. 确保路径列拉伸
        self.horizontalHeader().setStretchLastSection(False)
        self.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
    
    def _add_row(self, row: int, profile: Profile, ui_lang: str):
        """添加单行数据"""
        # 1. 项目名称
        name_item = QTableWidgetItem(profile.name)
        name_item.setIcon(self.style().standardIcon(QStyle.SP_FileIcon))
        name_item.setData(Qt.UserRole, profile)
        self.setItem(row, 0, name_item)
        
        # 2. 界面语言
        lang_code = self._get_profile_language(profile)
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
        
        # 4. 文献（使用固定宽度字符串确保数值排序正确）
        item_count = profile.get_item_count()
        if item_count >= 0:
            count_str = f"{item_count:4d}"  # 固定4位宽度，右对齐
        else:
            count_str = "   ?"
        count_item = QTableWidgetItem(count_str)
        count_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        count_item.setData(Qt.UserRole, profile)
        self.setItem(row, 3, count_item)
        
        # 5. 插件（使用固定宽度字符串）
        plugin_count = profile.get_plugin_count()
        plugin_str = f"{plugin_count:3d}"   # 固定3位宽度
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
        
        # 7. 操作按钮（放入容器实现垂直居中）
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
        btn.clicked.connect(lambda p=profile: self.launch_requested.emit(p))
        
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(btn)
        layout.setAlignment(Qt.AlignCenter)
        
        self.setCellWidget(row, 6, container)
    
    def _get_profile_language(self, profile: Profile) -> str:
        """
        获取项目的界面语言代码
        
        Args:
            profile: 项目对象
            
        Returns:
            语言代码（如 'zh-CN', 'en-US'），若读取失败则返回 None
        """
        try:
            if profile.profiles_path and Path(profile.profiles_path).exists():
                return read_language(profile.profiles_path)
        except Exception:
            pass
        return None
    
    def _update_all_buttons(self):
        """更新所有启动按钮文字"""
        for row in range(self.rowCount()):
            container = self.cellWidget(row, 6)
            if container:
                btn = container.findChild(QPushButton)
                if btn:
                    btn.setText(self.i18n.tr("btn_launch"))
    
    def _on_item_double_clicked(self, item):
        """双击行 → 启动项目"""
        profile = item.data(Qt.UserRole)
        if profile:
            self.launch_requested.emit(profile)
    
    def _on_item_clicked(self, item):
        """单击行 → 如果点击语言列，发出修改语言信号"""
        if item.column() == 1:
            profile = item.data(Qt.UserRole)
            if profile:
                self.change_language_requested.emit(profile)
    
    def _on_context_menu(self, pos):
        """右键菜单"""
        row = self.rowAt(pos.y())
        if row < 0:
            return
        
        profile = self.item(row, 0).data(Qt.UserRole)
        if not profile:
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
        
        menu.addSeparator()
        delete_action = menu.addAction(self.i18n.tr("menu_delete_project"))
        delete_action.setIcon(self.style().standardIcon(QStyle.SP_DialogCancelButton))
        delete_action.triggered.connect(lambda: self.delete_requested.emit(profile))
        
        menu.exec_(self.viewport().mapToGlobal(pos))
    
    def get_selected_profile(self) -> Profile:
        """获取当前选中的项目"""
        row = self.currentRow()
        if row < 0:
            return None
        return self.item(row, 0).data(Qt.UserRole)
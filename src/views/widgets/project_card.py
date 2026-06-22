# -*- coding: utf-8 -*-
"""
项目卡片控件
"""

from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QFrame, QMenu
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from models.profile import Profile


class ProjectCard(QFrame):
    """项目卡片控件"""

    launch_requested = Signal(Profile)
    open_folder_requested = Signal(Profile)
    delete_requested = Signal(Profile)
    create_shortcut_requested = Signal(Profile)

    def __init__(self, profile: Profile, parent=None):
        super().__init__(parent)
        self.profile = profile
        self._setup_ui()
        self._update_info()

    def _setup_ui(self):
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        self.setLineWidth(1)
        self.setStyleSheet("""
            ProjectCard {
                background-color: #fafafa;
                border-radius: 4px;
                border: 1px solid #e0e0e0;
                padding: 8px;
            }
            ProjectCard:hover {
                background-color: #f0f4f8;
                border-color: #b0b8c0;
            }
        """)

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(12, 10, 12, 10)
        main_layout.setSpacing(12)

        # 左侧信息
        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)

        title_layout = QHBoxLayout()
        self.icon_label = QLabel("📁")
        self.icon_label.setStyleSheet("font-size: 18px;")
        title_layout.addWidget(self.icon_label)

        self.name_label = QLabel(self.profile.name)
        font = self.name_label.font()
        font.setPointSize(11)
        font.setBold(True)
        self.name_label.setFont(font)
        title_layout.addWidget(self.name_label)
        title_layout.addStretch()
        info_layout.addLayout(title_layout)

        self.path_label = QLabel(self.profile.project_path)
        self.path_label.setStyleSheet("color: #666; font-size: 9px;")
        self.path_label.setWordWrap(True)
        info_layout.addWidget(self.path_label)

        self.stats_label = QLabel("")
        self.stats_label.setStyleSheet("color: #888; font-size: 9px;")
        info_layout.addWidget(self.stats_label)

        info_widget = QWidget()
        info_widget.setLayout(info_layout)
        main_layout.addWidget(info_widget, 1)

        # 启动按钮
        self.launch_btn = QPushButton("▶ 启动")
        self.launch_btn.setMinimumWidth(80)
        self.launch_btn.setStyleSheet("""
            QPushButton {
                background-color: #2b7a62;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1e5f4a;
            }
        """)
        self.launch_btn.clicked.connect(self._on_launch)
        main_layout.addWidget(self.launch_btn)

        self.setFixedHeight(80)

    def _update_info(self):
        item_count = self.profile.get_item_count()
        plugin_count = self.profile.get_plugin_count()
        if item_count >= 0:
            self.stats_label.setText("📄 文献: {} 篇  |  🔌 插件: {} 个".format(item_count, plugin_count))
        else:
            self.stats_label.setText("🔌 插件: {} 个".format(plugin_count))

    def _on_launch(self):
        self.launch_requested.emit(self.profile)

    def mouseDoubleClickEvent(self, event):
        self._on_launch()
        super().mouseDoubleClickEvent(event)

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        launch_action = menu.addAction("▶ 启动此项目")
        launch_action.triggered.connect(self._on_launch)

        open_action = menu.addAction("📂 打开项目文件夹")
        open_action.triggered.connect(lambda: self.open_folder_requested.emit(self.profile))

        shortcut_action = menu.addAction("🖱 创建桌面快捷方式")
        shortcut_action.triggered.connect(lambda: self.create_shortcut_requested.emit(self.profile))

        menu.addSeparator()
        delete_action = menu.addAction("🗑 删除项目")
        delete_action.setStyleSheet("color: #cc3333;")
        delete_action.triggered.connect(lambda: self.delete_requested.emit(self.profile))

        menu.exec_(event.globalPos())

    def update_profile(self, profile: Profile):
        self.profile = profile
        self.name_label.setText(profile.name)
        self.path_label.setText(profile.project_path)
        self._update_info()
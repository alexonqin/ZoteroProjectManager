# -*- coding: utf-8 -*-
"""
状态栏组件
"""

from PySide6.QtWidgets import QStatusBar, QLabel
from PySide6.QtCore import Qt

from utils.i18n import I18n


class StatusBarWidget(QStatusBar):
    """
    状态栏组件
    显示就绪状态、项目数量、Zotero 版本
    """
    
    def __init__(self, i18n: I18n, parent=None):
        super().__init__(parent)
        self.i18n = i18n
        
        self._setup_ui()
        self.retranslate_ui()
    
    def _setup_ui(self):
        self.status_label = QLabel()
        self.addWidget(self.status_label)
        
        self.info_label = QLabel()
        self.info_label.setStyleSheet("color: #888;")
        self.addPermanentWidget(self.info_label)
    
    def retranslate_ui(self):
        """刷新文字"""
        self.set_ready()
    
    def set_ready(self):
        """设置为就绪状态"""
        self.status_label.setText(self.i18n.tr("status_ready"))
    
    def set_loading(self):
        """设置为加载中状态"""
        self.status_label.setText(self.i18n.tr("status_loading"))
    
    def set_error(self, msg: str):
        """设置为错误状态"""
        self.status_label.setText(f"❌ {msg}")
    
    def update_info(self, project_count: int, zotero_version: str):
        """
        更新信息栏
        
        Args:
            project_count: 项目数量
            zotero_version: Zotero 版本号
        """
        version_text = f"Zotero {zotero_version}" if zotero_version else self.i18n.tr("status_zotero_not_found")
        self.info_label.setText(f"{self.i18n.tr('status_projects_count', count=project_count)}  |  {version_text}")
# -*- coding: utf-8 -*-
"""
工具栏组件
"""

from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton
from PySide6.QtCore import Signal

from utils.i18n import I18n


class ToolbarWidget(QWidget):
    """
    工具栏组件
    包含刷新、新建、偏好、语言切换按钮
    """
    
    refresh_clicked = Signal()
    new_clicked = Signal()
    preferences_clicked = Signal()
    language_switched = Signal()
    
    def __init__(self, i18n: I18n, parent=None):
        super().__init__(parent)
        self.i18n = i18n
        
        self._setup_ui()
        self.retranslate_ui()
    
    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.refresh_btn = QPushButton()
        self.refresh_btn.clicked.connect(self.refresh_clicked.emit)
        layout.addWidget(self.refresh_btn)
        
        self.new_btn = QPushButton()
        self.new_btn.clicked.connect(self.new_clicked.emit)
        layout.addWidget(self.new_btn)
        
        self.pref_btn = QPushButton()
        self.pref_btn.clicked.connect(self.preferences_clicked.emit)
        layout.addWidget(self.pref_btn)
        
        layout.addStretch()
        
        self.lang_btn = QPushButton()
        self.lang_btn.setFixedWidth(50)
        self.lang_btn.clicked.connect(self.language_switched.emit)
        layout.addWidget(self.lang_btn)
    
    def retranslate_ui(self):
        """刷新按钮文字"""
        self.refresh_btn.setText(self.i18n.tr("btn_refresh"))
        self.new_btn.setText(self.i18n.tr("btn_new"))
        self.pref_btn.setText(self.i18n.tr("btn_preferences"))
        
        lang = self.i18n.get_language()
        self.lang_btn.setText("中" if lang == "zh_CN" else "EN")
        self.lang_btn.setToolTip(self.i18n.tr("tooltip_lang_switch"))
    
    def update_language_button(self):
        """更新语言按钮文字（语言切换后调用）"""
        lang = self.i18n.get_language()
        self.lang_btn.setText("中" if lang == "zh_CN" else "EN")
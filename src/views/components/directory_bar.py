# -*- coding: utf-8 -*-
"""
目录选择条组件
"""

from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton, QMenu, QFileDialog
from PySide6.QtCore import Signal

from utils.i18n import I18n
from utils.path_utils import is_valid_directory


class DirectoryBar(QWidget):
    """
    目录选择条组件
    显示当前目录、浏览、历史记录、设为默认
    """
    
    directory_changed = Signal(str)   # 目录变更
    default_set = Signal(str)         # 设为默认
    
    def __init__(self, i18n: I18n, config_mgr, parent=None):
        super().__init__(parent)
        self.i18n = i18n
        self.config_mgr = config_mgr
        self.current_dir = ""
        
        self._setup_ui()
        self.retranslate_ui()
    
    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.dir_label = QLabel()
        layout.addWidget(self.dir_label)
        
        self.dir_path_label = QLabel()
        self.dir_path_label.setStyleSheet("color: #2b7a62; font-weight: bold;")
        self.dir_path_label.setWordWrap(True)
        layout.addWidget(self.dir_path_label, 1)
        
        self.history_btn = QPushButton("▼")
        self.history_btn.setFixedWidth(30)
        self.history_btn.clicked.connect(self._show_history_menu)
        layout.addWidget(self.history_btn)
        
        self.browse_btn = QPushButton()
        self.browse_btn.clicked.connect(self._on_browse)
        layout.addWidget(self.browse_btn)
        
        self.default_btn = QPushButton()
        self.default_btn.clicked.connect(self._on_set_default)
        layout.addWidget(self.default_btn)
    
    def retranslate_ui(self):
        """刷新文字"""
        self.dir_label.setText(self.i18n.tr("label_current_dir"))
        self.browse_btn.setText(self.i18n.tr("btn_browse"))
        self.default_btn.setText(self.i18n.tr("btn_set_default"))
        
        self.dir_path_label.setToolTip(self.i18n.tr("dir_tooltip"))
        self.history_btn.setToolTip(self.i18n.tr("history_tooltip"))
        self.browse_btn.setToolTip(self.i18n.tr("browse_tooltip"))
        self.default_btn.setToolTip(self.i18n.tr("default_tooltip"))
    
    def set_current_dir(self, path: str):
        """设置当前目录"""
        self.current_dir = path
        self.dir_path_label.setText(path)
    
    def _on_browse(self):
        """浏览并切换目录"""
        path = QFileDialog.getExistingDirectory(
            self,
            self.i18n.tr("btn_browse"),
            self.current_dir
        )
        if path and is_valid_directory(path):
            self.current_dir = path
            self.dir_path_label.setText(path)
            self.directory_changed.emit(path)
    
    def _on_set_default(self):
        """设为默认目录"""
        if self.current_dir:
            self.default_set.emit(self.current_dir)
            self.dir_path_label.setText(self.current_dir + " ⭐")
    
    def _show_history_menu(self):
        """显示历史记录菜单"""
        history = self.config_mgr.get_profiles_history()
        if not history:
            return
        
        menu = QMenu(self)
        for path in history:
            action = menu.addAction(path)
            action.setData(path)
            if path == self.current_dir:
                action.setIcon(self.style().standardIcon(self.style().SP_DialogApplyButton))
        
        action = menu.exec_(self.history_btn.mapToGlobal(self.history_btn.rect().bottomLeft()))
        if action:
            path = action.data()
            if path and is_valid_directory(path):
                self.current_dir = path
                self.dir_path_label.setText(path)
                self.directory_changed.emit(path)
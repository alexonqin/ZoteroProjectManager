# -*- coding: utf-8 -*-
"""
重命名对话框
"""

import re
from pathlib import Path

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QFrame, QMessageBox
)
from PySide6.QtCore import Qt

from utils.i18n import I18n


class RenameDialog(QDialog):
    def __init__(self, i18n: I18n, current_name: str, profiles_dir: str, parent=None):
        super().__init__(parent)
        self.i18n = i18n
        self.current_name = current_name
        self.profiles_dir = profiles_dir
        self.new_name = current_name

        self._setup_ui()
        self.retranslate_ui()
        self._setup_validators()

        # 自动聚焦并全选
        self.name_edit.setFocus()
        self.name_edit.selectAll()

    def _setup_ui(self):
        self.setModal(True)
        self.setFixedWidth(550)
        self.setFixedHeight(380)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        # 标题
        self.title_label = QLabel()
        self.title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(self.title_label)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line)

        # 当前名称
        current_layout = QHBoxLayout()
        self.current_label = QLabel()
        self.current_label.setMinimumWidth(100)
        current_layout.addWidget(self.current_label)
        self.current_display = QLabel(self.current_name)
        self.current_display.setStyleSheet("font-weight: bold; color: #2b7a62;")
        current_layout.addWidget(self.current_display)
        current_layout.addStretch()
        layout.addLayout(current_layout)

        # 新名称输入
        new_layout = QHBoxLayout()
        self.new_label = QLabel()
        self.new_label.setMinimumWidth(100)
        new_layout.addWidget(self.new_label)
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("")
        new_layout.addWidget(self.name_edit)
        layout.addLayout(new_layout)

        # 验证提示
        self.error_label = QLabel()
        self.error_label.setWordWrap(True)
        self.error_label.setStyleSheet("color: #cc3333; font-size: 10px; padding-left: 100px;")
        layout.addWidget(self.error_label)

        # 分隔线
        line2 = QFrame()
        line2.setFrameShape(QFrame.HLine)
        line2.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line2)

        # 影响范围说明
        self.scope_label = QLabel()
        self.scope_label.setWordWrap(True)
        self.scope_label.setStyleSheet("font-size: 11px; color: #444; padding: 6px; background-color: #f5f5f5; border-radius: 3px;")
        layout.addWidget(self.scope_label)

        # 提示
        self.hint_label = QLabel()
        self.hint_label.setWordWrap(True)
        self.hint_label.setStyleSheet("color: #888; font-size: 10px;")
        layout.addWidget(self.hint_label)

        layout.addStretch()

        # 按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.cancel_btn = QPushButton()
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.cancel_btn)

        self.confirm_btn = QPushButton()
        self.confirm_btn.setEnabled(False)
        self.confirm_btn.setStyleSheet("""
            QPushButton {
                background-color: #2b7a62;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 24px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1e5f4a;
            }
            QPushButton:disabled {
                background-color: #aaaaaa;
            }
        """)
        self.confirm_btn.clicked.connect(self._on_confirm)
        btn_layout.addWidget(self.confirm_btn)
        layout.addLayout(btn_layout)

    def retranslate_ui(self):
        self.setWindowTitle(self.i18n.tr("rename_title"))
        self.title_label.setText(self.i18n.tr("rename_title"))
        self.current_label.setText(self.i18n.tr("rename_current_name"))
        self.new_label.setText(self.i18n.tr("rename_new_name"))
        self.scope_label.setText(
            f"⚠️ {self.i18n.tr('rename_scope')}\n"
            f"  {self.i18n.tr('rename_scope_folder')}\n"
            f"  {self.i18n.tr('rename_scope_profile')}\n"
            f"  {self.i18n.tr('rename_scope_shortcuts')}\n"
            f"  {self.i18n.tr('rename_scope_notes')}"
        )
        self.hint_label.setText("💡 " + self.i18n.tr("rename_hint"))
        self.confirm_btn.setText(self.i18n.tr("rename_btn_confirm"))
        self.cancel_btn.setText(self.i18n.tr("rename_btn_cancel"))

    def _setup_validators(self):
        self.name_edit.textChanged.connect(self._validate_input)
        self.name_edit.returnPressed.connect(self._on_confirm_if_valid)

    def _validate_input(self, text: str):
        text = text.strip()
        error = ""
        if not text:
            error = self.i18n.tr("rename_error_empty")
        else:
            illegal = r'<>:"/\|?*'
            for ch in illegal:
                if ch in text:
                    error = self.i18n.tr("rename_error_invalid_char").format(char=ch)
                    break
            if not error:
                if text != self.current_name:
                    new_path = Path(self.profiles_dir) / text
                    if new_path.exists():
                        error = self.i18n.tr("rename_error_exists").format(name=text)
        self.error_label.setText(error)
        self.confirm_btn.setEnabled(not error and text and text != self.current_name)
        self.new_name = text if not error else self.current_name

    def _on_confirm_if_valid(self):
        if self.confirm_btn.isEnabled():
            self._on_confirm()

    def _on_confirm(self):
        # 如果新名称与旧名称相同，直接关闭
        if self.new_name == self.current_name:
            self.accept()
            return
        self.accept()
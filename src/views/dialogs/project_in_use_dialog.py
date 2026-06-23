# -*- coding: utf-8 -*-
"""
项目正在使用中 - 警告对话框
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QMessageBox
)
from PySide6.QtCore import Qt

from utils.i18n import I18n


class ProjectInUseDialog(QDialog):
    """项目正在使用中，无法删除"""

    def __init__(self, i18n: I18n, project_name: str, project_path: str, parent=None):
        super().__init__(parent)
        self.i18n = i18n
        self.project_name = project_name
        self.project_path = project_path
        self._setup_ui()
        self.retranslate_ui()

    def _setup_ui(self):
        self.setModal(True)
        self.setFixedWidth(500)
        self.setFixedHeight(280)

        layout = QVBoxLayout(self)
        layout.setSpacing(14)

        # 标题
        self.title_label = QLabel()
        self.title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #cc3333;")
        layout.addWidget(self.title_label)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line)

        # 项目信息
        self.info_label = QLabel()
        self.info_label.setWordWrap(True)
        self.info_label.setStyleSheet("font-size: 12px;")
        layout.addWidget(self.info_label)

        # 建议
        self.suggestion_label = QLabel()
        self.suggestion_label.setWordWrap(True)
        self.suggestion_label.setStyleSheet("color: #444; font-size: 11px; padding: 8px; background-color: #f5f5f5; border-radius: 3px;")
        layout.addWidget(self.suggestion_label)

        layout.addStretch()

        # 按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.cancel_btn = QPushButton()
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.cancel_btn)
        self.retry_btn = QPushButton()
        self.retry_btn.setStyleSheet("""
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
        """)
        self.retry_btn.clicked.connect(self.accept)
        btn_layout.addWidget(self.retry_btn)
        layout.addLayout(btn_layout)

    def retranslate_ui(self):
        self.setWindowTitle(self.i18n.tr("delete_in_use_title"))
        self.title_label.setText(self.i18n.tr("delete_in_use_title"))
        self.info_label.setText(
            f"{self.i18n.tr('delete_in_use_project')} {self.project_name}\n"
            f"{self.i18n.tr('delete_in_use_path')} {self.project_path}"
        )
        self.suggestion_label.setText(self.i18n.tr("delete_in_use_suggestion"))
        self.retry_btn.setText(self.i18n.tr("delete_in_use_btn_retry"))
        self.cancel_btn.setText(self.i18n.tr("pref_btn_cancel"))
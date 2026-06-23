# -*- coding: utf-8 -*-
"""
删除失败对话框
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame
)
from PySide6.QtCore import Qt

from utils.i18n import I18n


class DeleteFailedDialog(QDialog):
    """删除失败，提供重试和取消"""

    def __init__(self, i18n: I18n, project_name: str, error_msg: str, parent=None):
        super().__init__(parent)
        self.i18n = i18n
        self.project_name = project_name
        self.error_msg = error_msg
        self._setup_ui()
        self.retranslate_ui()

    def _setup_ui(self):
        self.setModal(True)
        self.setFixedWidth(500)
        self.setFixedHeight(300)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        # 标题
        self.title_label = QLabel()
        self.title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #cc3333;")
        layout.addWidget(self.title_label)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line)

        # 错误信息
        self.error_label = QLabel()
        self.error_label.setWordWrap(True)
        self.error_label.setStyleSheet("font-size: 12px; color: #cc3333;")
        layout.addWidget(self.error_label)

        # 可能原因
        self.causes_label = QLabel()
        self.causes_label.setWordWrap(True)
        self.causes_label.setStyleSheet("font-size: 11px; color: #444; padding: 6px; background-color: #f5f5f5; border-radius: 3px;")
        layout.addWidget(self.causes_label)

        # 建议操作
        self.suggest_label = QLabel()
        self.suggest_label.setWordWrap(True)
        self.suggest_label.setStyleSheet("font-size: 11px; color: #444; padding: 6px; background-color: #f5f5f5; border-radius: 3px;")
        layout.addWidget(self.suggest_label)

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
        self.setWindowTitle(self.i18n.tr("delete_failed_title"))
        self.title_label.setText(self.i18n.tr("delete_failed_title"))
        self.error_label.setText(f"{self.i18n.tr('delete_failed_error')} {self.error_msg}")
        self.causes_label.setText(self.i18n.tr("delete_failed_possible_causes"))
        self.suggest_label.setText(self.i18n.tr("delete_failed_suggestions"))
        self.retry_btn.setText(self.i18n.tr("delete_failed_btn_retry"))
        self.cancel_btn.setText(self.i18n.tr("pref_btn_cancel"))
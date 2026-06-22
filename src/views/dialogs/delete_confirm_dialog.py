# -*- coding: utf-8 -*-
"""
删除确认对话框
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
)

from utils.i18n import I18n


class DeleteConfirmDialog(QDialog):
    """删除确认对话框"""

    def __init__(self, i18n: I18n, project_name: str, parent=None):
        super().__init__(parent)
        self.i18n = i18n
        self.project_name = project_name

        self._setup_ui()
        self.retranslate_ui()

    def _setup_ui(self):
        self.setModal(True)
        self.setFixedWidth(450)
        self.setFixedHeight(200)

        layout = QVBoxLayout(self)
        layout.setSpacing(16)

        self.title_label = QLabel()
        self.title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #cc3333;")
        layout.addWidget(self.title_label)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line)

        self.msg_label = QLabel()
        self.msg_label.setWordWrap(True)
        self.msg_label.setStyleSheet("font-size: 12px; padding: 8px 0px;")
        layout.addWidget(self.msg_label)

        self.hint_label = QLabel()
        self.hint_label.setStyleSheet("color: #cc3333; font-weight: bold; font-size: 11px;")
        layout.addWidget(self.hint_label)

        layout.addStretch()

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.cancel_btn = QPushButton()
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.cancel_btn)
        self.delete_btn = QPushButton()
        self.delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #cc3333;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 24px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #aa2222;
            }
        """)
        self.delete_btn.clicked.connect(self.accept)
        btn_layout.addWidget(self.delete_btn)
        layout.addLayout(btn_layout)

    def retranslate_ui(self):
        self.setWindowTitle(self.i18n.tr("dialog_delete_title"))
        self.title_label.setText(self.i18n.tr("dialog_delete_title"))
        self.msg_label.setText(self.i18n.tr("dialog_delete_msg", name=self.project_name))
        self.hint_label.setText("⚠️ " + self.i18n.tr("dialog_delete_btn_yes"))
        self.cancel_btn.setText(self.i18n.tr("dialog_delete_btn_no"))
        self.delete_btn.setText(self.i18n.tr("dialog_delete_btn_yes"))
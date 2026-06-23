# -*- coding: utf-8 -*-
"""
删除成功对话框
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame
)
from PySide6.QtCore import Qt

from utils.i18n import I18n


class DeleteSuccessDialog(QDialog):
    """删除成功，已移至回收站"""

    def __init__(self, i18n: I18n, project_name: str, project_path: str, size_mb: float, parent=None):
        super().__init__(parent)
        self.i18n = i18n
        self.project_name = project_name
        self.project_path = project_path
        self.size_mb = size_mb
        self._setup_ui()
        self.retranslate_ui()

    def _setup_ui(self):
        self.setModal(True)
        self.setFixedWidth(450)
        self.setFixedHeight(250)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        # 标题
        self.title_label = QLabel()
        self.title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2b7a62;")
        layout.addWidget(self.title_label)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line)

        # 信息
        self.info_label = QLabel()
        self.info_label.setWordWrap(True)
        self.info_label.setStyleSheet("font-size: 12px;")
        layout.addWidget(self.info_label)

        # 恢复提示
        self.recover_label = QLabel()
        self.recover_label.setWordWrap(True)
        self.recover_label.setStyleSheet("color: #555; font-size: 11px; padding: 6px; background-color: #f0f8f0; border-radius: 3px;")
        layout.addWidget(self.recover_label)

        layout.addStretch()

        # 确定按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.ok_btn = QPushButton()
        self.ok_btn.setFixedWidth(100)
        self.ok_btn.clicked.connect(self.accept)
        btn_layout.addWidget(self.ok_btn)
        layout.addLayout(btn_layout)

    def retranslate_ui(self):
        self.setWindowTitle(self.i18n.tr("delete_success_title"))
        self.title_label.setText(self.i18n.tr("delete_success_title"))
        self.info_label.setText(
            f"{self.i18n.tr('delete_success_project')} {self.project_name}\n"
            f"{self.i18n.tr('delete_success_path')} {self.project_path}\n"
            f"{self.i18n.tr('delete_success_size')} {self.size_mb:.1f} MB"
        )
        self.recover_label.setText(self.i18n.tr("delete_success_recover_hint"))
        self.ok_btn.setText(self.i18n.tr("about_btn_close"))
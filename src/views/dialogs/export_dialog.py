# -*- coding: utf-8 -*-
"""
导出项目对话框
"""

import os
from pathlib import Path

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QFileDialog, QCheckBox,
    QFrame, QMessageBox
)
from PySide6.QtCore import Qt

from utils.i18n import I18n
from models.profile import Profile


class ExportDialog(QDialog):
    """导出项目对话框"""

    def __init__(self, i18n: I18n, profile: Profile, default_dir: str, parent=None):
        super().__init__(parent)
        self.i18n = i18n
        self.profile = profile
        self.default_dir = default_dir

        self.result_path = None
        self.result_open_folder = False

        self._setup_ui()
        self.retranslate_ui()
        self._update_preview()

    def _setup_ui(self):
        self.setModal(True)
        self.setFixedWidth(520)
        self.setFixedHeight(350)

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

        # 项目信息
        self.info_label = QLabel()
        self.info_label.setWordWrap(True)
        self.info_label.setStyleSheet("font-size: 12px; color: #444;")
        layout.addWidget(self.info_label)

        # 保存位置
        path_layout = QHBoxLayout()
        self.path_label = QLabel()
        self.path_label.setMinimumWidth(80)
        path_layout.addWidget(self.path_label)

        self.path_edit = QLineEdit()
        self.path_edit.setReadOnly(True)
        self.path_edit.setStyleSheet("background-color: #f5f5f5;")
        path_layout.addWidget(self.path_edit, 1)

        self.browse_btn = QPushButton()
        self.browse_btn.clicked.connect(self._on_browse)
        path_layout.addWidget(self.browse_btn)
        layout.addLayout(path_layout)

        # 提示信息
        self.hint_label = QLabel()
        self.hint_label.setWordWrap(True)
        self.hint_label.setStyleSheet("color: #888; font-size: 10px;")
        layout.addWidget(self.hint_label)

        # 选项
        self.open_folder_cb = QCheckBox()
        layout.addWidget(self.open_folder_cb)

        layout.addStretch()

        # 按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.cancel_btn = QPushButton()
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.cancel_btn)

        self.export_btn = QPushButton()
        self.export_btn.setStyleSheet("""
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
        self.export_btn.clicked.connect(self._on_export)
        btn_layout.addWidget(self.export_btn)
        layout.addLayout(btn_layout)

    def retranslate_ui(self):
        self.setWindowTitle(self.i18n.tr("export_title"))
        self.title_label.setText(self.i18n.tr("export_title"))
        self.path_label.setText(self.i18n.tr("export_save_location"))
        self.browse_btn.setText(self.i18n.tr("btn_browse"))
        self.hint_label.setText("💡 " + self.i18n.tr("export_hint"))
        self.open_folder_cb.setText(self.i18n.tr("export_open_folder"))
        self.export_btn.setText(self.i18n.tr("export_btn_export"))
        self.cancel_btn.setText(self.i18n.tr("pref_btn_cancel"))

        self._update_preview()

    def _update_preview(self):
        size_mb = self.profile.get_size() / (1024 * 1024)
        item_count = self.profile.get_item_count()
        self.info_label.setText(
            f"{self.i18n.tr('export_project_name')} {self.profile.name}\n"
            f"{self.i18n.tr('export_project_size')} {size_mb:.1f} MB\n"
            f"{self.i18n.tr('export_item_count')} {item_count if item_count >= 0 else '?'}"
        )

        # 设置默认保存路径
        if not self.path_edit.text():
            from datetime import datetime
            now = datetime.now().strftime("%Y%m%d_%H%M%S")
            default_name = f"{self.profile.name}_{now}.zip"
            default_path = Path(self.default_dir) / default_name
            self.path_edit.setText(str(default_path))

    def _on_browse(self):
        current_path = self.path_edit.text()
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            self.i18n.tr("export_save_location"),
            current_path,
            "ZIP Files (*.zip)"
        )
        if file_path:
            self.path_edit.setText(file_path)

    def _on_export(self):
        path = self.path_edit.text()
        if not path:
            QMessageBox.warning(self, "", self.i18n.tr("export_error_no_path"))
            return

        # 检查目标目录是否存在
        target_dir = Path(path).parent
        if not target_dir.exists():
            QMessageBox.warning(self, "", self.i18n.tr("export_error_dir_not_exist"))
            return

        self.result_path = path
        self.result_open_folder = self.open_folder_cb.isChecked()
        self.accept()



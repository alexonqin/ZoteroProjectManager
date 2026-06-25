# -*- coding: utf-8 -*-
"""
导入项目对话框（支持重命名）
"""

import os
import zipfile
from pathlib import Path

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QFileDialog, QCheckBox,
    QFrame, QMessageBox
)
from PySide6.QtCore import Qt

from utils.i18n import I18n


class ImportDialog(QDialog):
    """导入项目对话框"""

    def __init__(self, i18n: I18n, default_dir: str, parent=None):
        super().__init__(parent)
        self.i18n = i18n
        self.default_dir = default_dir

        self.result_path = None          # 目标路径
        self.result_rename = False       # 是否重命名
        self.result_new_name = ""        # 新名称

        self._zip_info = None
        self._setup_ui()
        self.retranslate_ui()

    def _setup_ui(self):
        self.setModal(True)
        self.setFixedWidth(550)
        self.setFixedHeight(280)

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

        # 选择文件
        file_layout = QHBoxLayout()
        self.file_label = QLabel()
        self.file_label.setMinimumWidth(80)
        file_layout.addWidget(self.file_label)

        self.file_edit = QLineEdit()
        self.file_edit.setReadOnly(True)
        self.file_edit.setStyleSheet("background-color: #f5f5f5;")
        file_layout.addWidget(self.file_edit, 1)

        self.browse_btn = QPushButton()
        self.browse_btn.clicked.connect(self._on_browse)
        file_layout.addWidget(self.browse_btn)
        layout.addLayout(file_layout)

        # 项目名称
        name_layout = QHBoxLayout()
        self.name_label = QLabel()
        self.name_label.setMinimumWidth(80)
        name_layout.addWidget(self.name_label)

        self.name_edit = QLineEdit()
        self.name_edit.setReadOnly(True)
        self.name_edit.setStyleSheet("background-color: #f5f5f5;")
        name_layout.addWidget(self.name_edit, 1)
        layout.addLayout(name_layout)

        # 重命名复选框
        self.rename_cb = QCheckBox()
        self.rename_cb.setChecked(False)
        self.rename_cb.stateChanged.connect(self._on_rename_toggle)
        layout.addWidget(self.rename_cb)

        layout.addStretch()

        # 按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.cancel_btn = QPushButton()
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.cancel_btn)

        self.import_btn = QPushButton()
        self.import_btn.setEnabled(False)
        self.import_btn.setStyleSheet("""
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
        self.import_btn.clicked.connect(self._on_import)
        btn_layout.addWidget(self.import_btn)
        layout.addLayout(btn_layout)

    def retranslate_ui(self):
        self.setWindowTitle(self.i18n.tr("import_title"))
        self.title_label.setText(self.i18n.tr("import_title"))
        self.file_label.setText(self.i18n.tr("import_select_file"))
        self.browse_btn.setText(self.i18n.tr("btn_browse"))
        self.name_label.setText(self.i18n.tr("import_project_name"))
        self.rename_cb.setText(self.i18n.tr("import_rename_project"))
        self.import_btn.setText(self.i18n.tr("import_btn_import"))
        self.cancel_btn.setText(self.i18n.tr("pref_btn_cancel"))

    def _on_browse(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            self.i18n.tr("import_select_file"),
            self.default_dir,
            "ZIP Files (*.zip)"
        )
        if file_path:
            self.file_edit.setText(file_path)
            self._analyze_zip(file_path)

    def _analyze_zip(self, zip_path):
        try:
            with zipfile.ZipFile(zip_path, 'r') as zf:
                all_names = zf.namelist()
                top_level = set()
                for name in all_names:
                    parts = name.split('/')
                    if len(parts) > 1:
                        top_level.add(parts[0])
                if len(top_level) != 1:
                    QMessageBox.warning(self, "", self.i18n.tr("import_error_invalid"))
                    self.name_edit.setText("")
                    self.import_btn.setEnabled(False)
                    return

                project_folder = next(iter(top_level))
                has_data = any(name.startswith(f"{project_folder}/data/") for name in all_names)
                has_profiles = any(name.startswith(f"{project_folder}/profiles/") for name in all_names)
                has_sqlite = f"{project_folder}/data/zotero.sqlite" in all_names

                if not (has_data and has_profiles and has_sqlite):
                    QMessageBox.warning(self, "", self.i18n.tr("import_error_invalid"))
                    self.name_edit.setText("")
                    self.import_btn.setEnabled(False)
                    return

                # 保存项目信息
                self._zip_info = {
                    'project_name': project_folder,
                }

                self.name_edit.setText(project_folder)
                self.import_btn.setEnabled(True)

        except zipfile.BadZipFile:
            QMessageBox.warning(self, "", self.i18n.tr("import_error_invalid"))
            self.import_btn.setEnabled(False)

    def _on_rename_toggle(self, state):
        if state == Qt.Checked:
            self.name_edit.setReadOnly(False)
            self.name_edit.setStyleSheet("background-color: white;")
            self.name_edit.setFocus()
            self.name_edit.selectAll()
        else:
            self.name_edit.setReadOnly(True)
            self.name_edit.setStyleSheet("background-color: #f5f5f5;")
            # 恢复原名称
            if self._zip_info:
                self.name_edit.setText(self._zip_info['project_name'])

    def _on_import(self):
        if not self._zip_info:
            QMessageBox.warning(self, "", self.i18n.tr("import_error_no_info"))
            return

        project_name = self.name_edit.text().strip()
        if not project_name:
            QMessageBox.warning(self, "", "项目名称不能为空")
            return

        target_path = Path(self.default_dir) / project_name

        # 检测冲突
        if target_path.exists():
            # 弹出冲突处理对话框
            reply = QMessageBox.question(
                self,
                self.i18n.tr("import_conflict_title"),
                self.i18n.tr("import_conflict_message").format(name=project_name),
                QMessageBox.Yes | QMessageBox.Cancel,
                QMessageBox.Yes
            )
            if reply == QMessageBox.Cancel:
                return
            # 用户选择 Yes = 自动重命名
            counter = 1
            new_name = f"{project_name}_{counter}"
            while (Path(self.default_dir) / new_name).exists():
                counter += 1
                new_name = f"{project_name}_{counter}"
            project_name = new_name
            target_path = Path(self.default_dir) / project_name
            # 更新界面上的名称
            self.name_edit.setText(project_name)

        self.result_path = str(target_path)
        self.result_rename = self.rename_cb.isChecked()
        self.result_new_name = project_name
        self.accept()
# -*- coding: utf-8 -*-
"""
导入项目对话框
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

        self.result_path = None
        self.result_create_shortcut = True

        self._zip_info = None
        self._setup_ui()
        self.retranslate_ui()

    def _setup_ui(self):
        self.setModal(True)
        self.setFixedWidth(550)
        self.setFixedHeight(370)

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

        # 项目信息预览
        self.preview_label = QLabel()
        self.preview_label.setWordWrap(True)
        self.preview_label.setStyleSheet("color: #444; font-size: 11px; padding: 6px; background-color: #f5f5f5; border-radius: 3px;")
        layout.addWidget(self.preview_label)

        # 目标位置
        target_layout = QHBoxLayout()
        self.target_label = QLabel()
        self.target_label.setMinimumWidth(80)
        target_layout.addWidget(self.target_label)

        self.target_edit = QLineEdit()
        self.target_edit.setReadOnly(True)
        self.target_edit.setStyleSheet("background-color: #f5f5f5;")
        target_layout.addWidget(self.target_edit, 1)
        layout.addLayout(target_layout)

        line2 = QFrame()
        line2.setFrameShape(QFrame.HLine)
        line2.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line2)

        # 选项：仅项目库快捷方式（不再包含桌面）
        self.shortcut_cb = QCheckBox()
        self.shortcut_cb.setChecked(True)
        layout.addWidget(self.shortcut_cb)

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
        self.target_label.setText(self.i18n.tr("import_target_location"))
        # 修改复选框文本，仅提及项目库快捷方式
        self.shortcut_cb.setText(self.i18n.tr("import_create_library_shortcut"))
        self.hint_label.setText("💡 " + self.i18n.tr("import_hint"))
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
                    self.preview_label.setText("")
                    self.target_edit.setText("")
                    self.import_btn.setEnabled(False)
                    return

                project_folder = next(iter(top_level))
                has_data = any(name.startswith(f"{project_folder}/data/") for name in all_names)
                has_profiles = any(name.startswith(f"{project_folder}/profiles/") for name in all_names)
                has_sqlite = f"{project_folder}/data/zotero.sqlite" in all_names

                if not (has_data and has_profiles and has_sqlite):
                    QMessageBox.warning(self, "", self.i18n.tr("import_error_invalid"))
                    self.preview_label.setText("")
                    self.target_edit.setText("")
                    self.import_btn.setEnabled(False)
                    return

                # 解析语言
                language = "zh-CN"
                try:
                    prefs_path = f"{project_folder}/profiles/prefs.js"
                    if prefs_path in all_names:
                        with zf.open(prefs_path) as f:
                            content = f.read().decode('utf-8')
                            import re
                            match = re.search(r'user_pref\s*\(\s*"intl\.locale\.requested"\s*,\s*"([^"]*)"\s*\)', content)
                            if match:
                                language = match.group(1)
                except:
                    pass

                total_size = 0
                for info in zf.filelist:
                    if not info.is_dir():
                        total_size += info.file_size

                self._zip_info = {
                    'project_name': project_folder,
                    'size_mb': total_size / (1024 * 1024),
                    'language': language,
                }

                size_mb = self._zip_info['size_mb']
                self.preview_label.setText(
                    f"{self.i18n.tr('import_project_name')} {project_folder}\n"
                    f"{self.i18n.tr('import_project_size')} {size_mb:.1f} MB\n"
                    f"{self.i18n.tr('import_language')} {language}"
                )

                target_path = Path(self.default_dir) / project_folder
                self.target_edit.setText(str(target_path))

                if target_path.exists():
                    self.preview_label.setText(
                        self.preview_label.text() + f"\n⚠️ {self.i18n.tr('import_conflict_detected')}"
                    )

                self.import_btn.setEnabled(True)

        except zipfile.BadZipFile:
            QMessageBox.warning(self, "", self.i18n.tr("import_error_invalid"))
            self.import_btn.setEnabled(False)

    def _on_import(self):
        if not self._zip_info:
            QMessageBox.warning(self, "", self.i18n.tr("import_error_no_info"))
            return

        project_name = self._zip_info['project_name']
        target_path = Path(self.default_dir) / project_name

        if target_path.exists():
            reply = QMessageBox.question(
                self,
                self.i18n.tr("import_conflict_title"),
                self.i18n.tr("import_conflict_message").format(name=project_name),
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
            )
            if reply == QMessageBox.Cancel:
                return
            elif reply == QMessageBox.Yes:
                counter = 1
                new_name = f"{project_name}_{counter}"
                while (Path(self.default_dir) / new_name).exists():
                    counter += 1
                    new_name = f"{project_name}_{counter}"
                project_name = new_name
                target_path = Path(self.default_dir) / project_name
                self.target_edit.setText(str(target_path))

        self.result_path = str(target_path)
        self.result_create_shortcut = self.shortcut_cb.isChecked()
        self.accept()
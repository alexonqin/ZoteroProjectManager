# -*- coding: utf-8 -*-
"""
首次启动引导对话框（简版，引导用户设置基本配置）
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFileDialog, QFrame, QMessageBox,
    QLineEdit
)
from PySide6.QtCore import Qt
from pathlib import Path

from utils.i18n import I18n
from utils.path_utils import is_valid_directory


class FirstLaunchDialog(QDialog):
    """首次启动引导对话框"""

    def __init__(self, i18n: I18n, parent=None):
        super().__init__(parent)
        self.i18n = i18n
        self.result_config = {}  # 存储用户设置

        self._setup_ui()
        self.retranslate_ui()

    def _setup_ui(self):
        self.setModal(True)
        self.setFixedWidth(580)
        self.setFixedHeight(420)

        layout = QVBoxLayout(self)
        layout.setSpacing(14)

        self.title_label = QLabel()
        self.title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(self.title_label)

        self.desc_label = QLabel()
        self.desc_label.setWordWrap(True)
        self.desc_label.setStyleSheet("font-size: 12px; color: #444;")
        layout.addWidget(self.desc_label)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line)

        # 版本号
        version_layout = QHBoxLayout()
        self.version_label = QLabel()
        self.version_label.setMinimumWidth(140)
        version_layout.addWidget(self.version_label)
        self.version_edit = QLineEdit()
        self.version_edit.setPlaceholderText("例如: 9.0.5")
        version_layout.addWidget(self.version_edit)
        layout.addLayout(version_layout)

        # Zotero 安装路径
        path_layout = QHBoxLayout()
        self.path_label = QLabel()
        self.path_label.setMinimumWidth(140)
        path_layout.addWidget(self.path_label)
        self.path_edit = QLineEdit()
        self.path_edit.setReadOnly(True)
        self.path_edit.setStyleSheet("background-color: #f5f5f5;")
        path_layout.addWidget(self.path_edit, 1)
        self.browse_btn = QPushButton()
        self.browse_btn.clicked.connect(self._on_browse)
        path_layout.addWidget(self.browse_btn)
        layout.addLayout(path_layout)

        # 模板目录
        template_layout = QHBoxLayout()
        self.template_label = QLabel()
        self.template_label.setMinimumWidth(140)
        template_layout.addWidget(self.template_label)
        self.template_edit = QLineEdit()
        self.template_edit.setReadOnly(True)
        self.template_edit.setStyleSheet("background-color: #f5f5f5;")
        template_layout.addWidget(self.template_edit, 1)
        self.template_browse_btn = QPushButton()
        self.template_browse_btn.clicked.connect(self._on_browse_template)
        template_layout.addWidget(self.template_browse_btn)
        layout.addLayout(template_layout)

        # Profiles 目录（项目库）
        profiles_layout = QHBoxLayout()
        self.profiles_label = QLabel()
        self.profiles_label.setMinimumWidth(140)
        profiles_layout.addWidget(self.profiles_label)
        self.profiles_edit = QLineEdit()
        self.profiles_edit.setReadOnly(True)
        self.profiles_edit.setStyleSheet("background-color: #f5f5f5;")
        profiles_layout.addWidget(self.profiles_edit, 1)
        self.profiles_browse_btn = QPushButton()
        self.profiles_browse_btn.clicked.connect(self._on_browse_profiles)
        profiles_layout.addWidget(self.profiles_browse_btn)
        layout.addLayout(profiles_layout)

        # Profiles 说明（新增）
        self.profiles_hint = QLabel()
        self.profiles_hint.setStyleSheet("color: #666; font-size: 9px; padding-left: 140px;")
        self.profiles_hint.setWordWrap(True)
        layout.addWidget(self.profiles_hint)

        layout.addStretch()

        # 按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.ok_btn = QPushButton()
        self.ok_btn.setStyleSheet("""
            QPushButton {
                background-color: #2b7a62;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 32px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1e5f4a;
            }
        """)
        self.ok_btn.clicked.connect(self._on_ok)
        btn_layout.addWidget(self.ok_btn)
        layout.addLayout(btn_layout)

    def retranslate_ui(self):
        self.setWindowTitle(self.i18n.tr("first_launch_title"))
        self.title_label.setText(self.i18n.tr("first_launch_title"))
        self.desc_label.setText(self.i18n.tr("first_launch_desc"))
        self.version_label.setText(self.i18n.tr("first_launch_version_label"))
        self.path_label.setText(self.i18n.tr("first_launch_path_label"))
        self.browse_btn.setText(self.i18n.tr("btn_browse"))
        self.template_label.setText(self.i18n.tr("first_launch_template_label"))
        self.template_browse_btn.setText(self.i18n.tr("btn_browse"))
        self.profiles_label.setText(self.i18n.tr("first_launch_profiles_label"))
        self.profiles_browse_btn.setText(self.i18n.tr("btn_browse"))
        self.profiles_hint.setText("💡 " + self.i18n.tr("first_launch_profiles_hint"))
        self.ok_btn.setText(self.i18n.tr("first_launch_btn_ok"))

    def _on_browse(self):
        path = QFileDialog.getExistingDirectory(
            self,
            self.i18n.tr("btn_browse"),
            self.path_edit.text()
        )
        if path:
            self.path_edit.setText(path)

    def _on_browse_template(self):
        path = QFileDialog.getExistingDirectory(
            self,
            self.i18n.tr("btn_browse"),
            self.template_edit.text()
        )
        if path:
            self.template_edit.setText(path)

    def _on_browse_profiles(self):
        path = QFileDialog.getExistingDirectory(
            self,
            self.i18n.tr("btn_browse"),
            self.profiles_edit.text()
        )
        if path:
            self.profiles_edit.setText(path)

    def _on_ok(self):
        version = self.version_edit.text().strip()
        install_dir = self.path_edit.text()
        templates_root = self.template_edit.text()
        profiles_dir = self.profiles_edit.text()

        if not version:
            QMessageBox.warning(self, "", self.i18n.tr("first_launch_error_version"))
            return
        if not install_dir or not is_valid_directory(install_dir):
            QMessageBox.warning(self, "", self.i18n.tr("first_launch_error_path"))
            return
        if not (Path(install_dir) / "zotero.exe").exists():
            QMessageBox.warning(self, "", self.i18n.tr("first_launch_error_exe"))
            return
        if not templates_root or not is_valid_directory(templates_root):
            QMessageBox.warning(self, "", self.i18n.tr("first_launch_error_template"))
            return
        if not profiles_dir or not is_valid_directory(profiles_dir):
            QMessageBox.warning(self, "", self.i18n.tr("first_launch_error_profiles"))
            return

        self.result_config = {
            "zotero_version": version,
            "zotero_install_dir": install_dir,
            "templates_root": templates_root,
            "profiles_current": profiles_dir,
            "profiles_default": profiles_dir,
        }
        self.accept()
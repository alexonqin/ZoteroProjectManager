# -*- coding: utf-8 -*-
"""
偏好设置对话框（简化版）
"""

import os
import subprocess
from pathlib import Path

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFileDialog, QFrame, QMessageBox
)
from PySide6.QtCore import Qt

from utils.i18n import I18n
from utils.config_manager import ConfigManager
from utils.path_utils import is_valid_directory
from controllers import ZoteroController


class PreferencesDialog(QDialog):
    def __init__(self, i18n: I18n, config_mgr: ConfigManager, controller: ZoteroController, parent=None):
        super().__init__(parent)
        self.i18n = i18n
        self.config_mgr = config_mgr
        self.config = config_mgr.get_config()
        self.controller = controller

        self._setup_ui()
        self.retranslate_ui()
        self._load_config()

    def _setup_ui(self):
        self.setModal(True)
        self.setFixedWidth(640)
        self.setFixedHeight(240)

        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        self.title_label = QLabel()
        self.title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(self.title_label)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line)

        # Zotero 安装路径
        path_layout = QHBoxLayout()
        self.path_label = QLabel()
        self.path_label.setMinimumWidth(120)
        path_layout.addWidget(self.path_label)

        self.path_edit = QLineEdit()
        self.path_edit.setReadOnly(True)
        self.path_edit.setStyleSheet("background-color: #f5f5f5;")
        path_layout.addWidget(self.path_edit, 1)

        self.browse_btn = QPushButton()
        self.browse_btn.clicked.connect(self._on_browse)
        path_layout.addWidget(self.browse_btn)
        layout.addLayout(path_layout)

        # 项目库目录
        profiles_layout = QHBoxLayout()
        self.profiles_label = QLabel()
        self.profiles_label.setMinimumWidth(120)
        profiles_layout.addWidget(self.profiles_label)

        self.profiles_edit = QLineEdit()
        self.profiles_edit.setReadOnly(True)
        self.profiles_edit.setStyleSheet("background-color: #f5f5f5;")
        profiles_layout.addWidget(self.profiles_edit, 1)

        self.profiles_browse_btn = QPushButton()
        self.profiles_browse_btn.clicked.connect(self._on_browse_profiles)
        profiles_layout.addWidget(self.profiles_browse_btn)
        layout.addLayout(profiles_layout)

        line2 = QFrame()
        line2.setFrameShape(QFrame.HLine)
        line2.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line2)

        # 按钮行
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)
        self.open_config_btn = QPushButton()
        self.open_config_btn.setStyleSheet("font-size: 10px; padding: 4px 8px;")
        self.open_config_btn.clicked.connect(self._on_open_config_folder)
        btn_layout.addWidget(self.open_config_btn)
        btn_layout.addStretch()
        self.cancel_btn = QPushButton()
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.cancel_btn)
        self.save_btn = QPushButton()
        self.save_btn.setStyleSheet("""
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
        self.save_btn.clicked.connect(self._on_save)
        btn_layout.addWidget(self.save_btn)
        layout.addLayout(btn_layout)

    def retranslate_ui(self):
        self.setWindowTitle(self.i18n.tr("pref_title"))
        self.title_label.setText(self.i18n.tr("pref_title"))

        # 设置标签文字
        self.path_label.setText("📁 " + self.i18n.tr("first_launch_path_label"))
        self.profiles_label.setText("📁 " + self.i18n.tr("first_launch_profiles_label"))

        self.browse_btn.setText(self.i18n.tr("btn_browse"))
        self.profiles_browse_btn.setText(self.i18n.tr("btn_browse"))
        self.open_config_btn.setText(self.i18n.tr("pref_open_config_folder"))
        self.save_btn.setText(self.i18n.tr("pref_btn_save"))
        self.cancel_btn.setText(self.i18n.tr("pref_btn_cancel"))

    def _load_config(self):
        self.path_edit.setText(self.config.zotero_install_dir)
        self.profiles_edit.setText(self.config.profiles_current)

    def _on_browse(self):
        dir_path = QFileDialog.getExistingDirectory(
            self,
            self.i18n.tr("btn_browse"),
            self.path_edit.text()
        )
        if dir_path:
            self.path_edit.setText(dir_path)

    def _on_browse_profiles(self):
        dir_path = QFileDialog.getExistingDirectory(
            self,
            self.i18n.tr("btn_browse"),
            self.profiles_edit.text()
        )
        if dir_path:
            self.profiles_edit.setText(dir_path)

    def _on_open_config_folder(self):
        config_file = self.config_mgr.config_path
        if not config_file.exists():
            QMessageBox.information(
                self,
                self.i18n.tr("pref_open_config_folder"),
                self.i18n.tr("pref_config_not_found")
            )
            return
        try:
            if os.name == 'nt':
                subprocess.Popen(['explorer', '/select,', str(config_file)])
            else:
                folder = config_file.parent
                if os.name == 'posix':
                    subprocess.Popen(['xdg-open', str(folder)])
                elif os.name == 'darwin':
                    subprocess.Popen(['open', str(folder)])
        except Exception as e:
            QMessageBox.warning(
                self,
                self.i18n.tr("pref_open_config_folder"),
                f"无法打开文件夹: {e}"
            )

    def _on_save(self):
        install_dir = self.path_edit.text()
        profiles_dir = self.profiles_edit.text()

        if not install_dir or not is_valid_directory(install_dir):
            QMessageBox.warning(self, "", "请选择有效的 Zotero 安装目录")
            return
        if not (Path(install_dir) / "zotero.exe").exists():
            QMessageBox.warning(self, "", "未找到 zotero.exe，请选择正确的安装目录")
            return
        if not profiles_dir or not is_valid_directory(profiles_dir):
            QMessageBox.warning(self, "", "请选择有效的项目库目录")
            return

        self.config.zotero_install_dir = install_dir
        self.config.profiles_current = profiles_dir
        if not self.config.profiles_default:
            self.config.profiles_default = profiles_dir

        self.config_mgr.save()
        self.accept()
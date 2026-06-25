# -*- coding: utf-8 -*-
"""
首次启动引导对话框（简化版）
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
    """首次启动引导对话框，仅设置 Zotero 路径和项目库目录"""

    def __init__(self, i18n: I18n, parent=None):
        super().__init__(parent)
        self.i18n = i18n
        self.result_config = {}

        self._setup_ui()
        self.retranslate_ui()

    def _setup_ui(self):
        self.setModal(True)
        self.setFixedWidth(600)
        self.setFixedHeight(300)

        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # 标题
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

        # Zotero 安装路径
        path_layout = QHBoxLayout()
        self.path_label = QLabel()
        self.path_label.setMinimumWidth(140)
        self.path_label.setStyleSheet("font-weight: bold; color: #cc3333;")
        path_layout.addWidget(self.path_label)

        self.path_edit = QLineEdit()
        self.path_edit.setReadOnly(True)
        self.path_edit.setStyleSheet("background-color: #f5f5f5;")
        path_layout.addWidget(self.path_edit, 1)

        self.browse_btn = QPushButton()
        self.browse_btn.clicked.connect(self._on_browse)
        path_layout.addWidget(self.browse_btn)
        layout.addLayout(path_layout)

        # Zotero 路径状态提示
        self.path_status_label = QLabel()
        self.path_status_label.setStyleSheet("font-size: 10px; padding-left: 140px;")
        layout.addWidget(self.path_status_label)

        # 项目库目录
        profiles_layout = QHBoxLayout()
        self.profiles_label = QLabel()
        self.profiles_label.setMinimumWidth(140)
        self.profiles_label.setStyleSheet("font-weight: bold; color: #cc3333;")
        profiles_layout.addWidget(self.profiles_label)

        self.profiles_edit = QLineEdit()
        self.profiles_edit.setReadOnly(True)
        self.profiles_edit.setStyleSheet("background-color: #f5f5f5;")
        profiles_layout.addWidget(self.profiles_edit, 1)

        self.profiles_browse_btn = QPushButton()
        self.profiles_browse_btn.clicked.connect(self._on_browse_profiles)
        profiles_layout.addWidget(self.profiles_browse_btn)
        layout.addLayout(profiles_layout)

        layout.addStretch()

        # 按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.ok_btn = QPushButton()
        self.ok_btn.setEnabled(False)
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
            QPushButton:disabled {
                background-color: #aaaaaa;
            }
        """)
        self.ok_btn.clicked.connect(self._on_ok)
        btn_layout.addWidget(self.ok_btn)
        layout.addLayout(btn_layout)

        # 监听路径变化
        self.path_edit.textChanged.connect(self._on_path_changed)
        self.profiles_edit.textChanged.connect(self._check_inputs)

    def retranslate_ui(self):
        self.setWindowTitle(self.i18n.tr("first_launch_title"))
        self.title_label.setText(self.i18n.tr("first_launch_title"))
        self.desc_label.setText(self.i18n.tr("first_launch_desc"))
        self.path_label.setText("📁 " + self.i18n.tr("first_launch_path_label"))
        self.path_label.setToolTip(self.i18n.tr("first_launch_path_hint"))
        self.profiles_label.setText("📁 " + self.i18n.tr("first_launch_profiles_label"))
        self.profiles_label.setToolTip(self.i18n.tr("first_launch_profiles_hint"))
        self.browse_btn.setText(self.i18n.tr("btn_browse"))
        self.profiles_browse_btn.setText(self.i18n.tr("btn_browse"))
        self.ok_btn.setText(self.i18n.tr("first_launch_btn_ok"))

    def _on_path_changed(self):
        """当 Zotero 路径变化时，验证并更新状态提示"""
        install_dir = self.path_edit.text()
        if not install_dir:
            self.path_status_label.setText("")
            self._check_inputs()
            return

        # 检查目录是否存在
        if not is_valid_directory(install_dir):
            self.path_status_label.setText("⚠️ " + self.i18n.tr("dialog_invalid_dir"))
            self.path_status_label.setStyleSheet("color: #cc3333; font-size: 10px; padding-left: 140px;")
            self._check_inputs()
            return

        # 检查 zotero.exe 是否存在
        exe_path = Path(install_dir) / "zotero.exe"
        if exe_path.exists():
            self.path_status_label.setText("✅ " + self.i18n.tr("status_zotero_found"))
            self.path_status_label.setStyleSheet("color: #2b7a62; font-size: 10px; padding-left: 140px;")
        else:
            self.path_status_label.setText("❌ " + self.i18n.tr("first_launch_error_exe"))
            self.path_status_label.setStyleSheet("color: #cc3333; font-size: 10px; padding-left: 140px;")

        self._check_inputs()

    def _check_inputs(self):
        """检查两个路径是否都已填写且 Zotero 路径有效"""
        install_dir = self.path_edit.text()
        profiles_dir = self.profiles_edit.text()

        # 检查 Zotero 路径是否存在且包含 zotero.exe
        zotero_ok = False
        if install_dir and is_valid_directory(install_dir):
            exe_path = Path(install_dir) / "zotero.exe"
            zotero_ok = exe_path.exists()

        # 项目库目录是否填写
        profiles_ok = bool(profiles_dir)

        self.ok_btn.setEnabled(zotero_ok and profiles_ok)

    def _on_browse(self):
        path = QFileDialog.getExistingDirectory(
            self,
            self.i18n.tr("btn_browse"),
            self.path_edit.text()
        )
        if path:
            self.path_edit.setText(path)

    def _on_browse_profiles(self):
        path = QFileDialog.getExistingDirectory(
            self,
            self.i18n.tr("btn_browse"),
            self.profiles_edit.text()
        )
        if path:
            self.profiles_edit.setText(path)

    def _on_ok(self):
        install_dir = self.path_edit.text()
        profiles_dir = self.profiles_edit.text()

        # 最终验证（确保安全）
        if not install_dir or not is_valid_directory(install_dir):
            QMessageBox.warning(self, "", self.i18n.tr("first_launch_error_path"))
            return
        if not (Path(install_dir) / "zotero.exe").exists():
            QMessageBox.warning(self, "", self.i18n.tr("first_launch_error_exe"))
            return
        if not profiles_dir or not is_valid_directory(profiles_dir):
            QMessageBox.warning(self, "", self.i18n.tr("first_launch_error_profiles"))
            return

        self.result_config = {
            "zotero_install_dir": install_dir,
            "profiles_current": profiles_dir,
            "profiles_default": profiles_dir,
        }
        self.accept()
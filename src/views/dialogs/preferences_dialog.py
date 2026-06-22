# -*- coding: utf-8 -*-
"""
偏好设置对话框
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFileDialog, QFrame, QMessageBox
)
from PySide6.QtCore import Qt
from pathlib import Path

from utils.i18n import I18n
from utils.config_manager import ConfigManager
from utils.path_utils import is_valid_directory
from controllers.zotero_controller import ZoteroController


class PreferencesDialog(QDialog):
    """偏好设置对话框"""

    def __init__(self, i18n: I18n, config_mgr: ConfigManager, parent=None):
        super().__init__(parent)
        self.i18n = i18n
        self.config_mgr = config_mgr
        self.config = config_mgr.get_config()
        self.controller = ZoteroController()

        self._setup_ui()
        self.retranslate_ui()
        self._load_config()

    def _setup_ui(self):
        self.setModal(True)
        self.setFixedWidth(600)

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

        # ---- Zotero 版本号 ----
        self.version_label = QLabel()
        self.version_label.setMinimumWidth(120)
        version_layout = QHBoxLayout()
        version_layout.addWidget(self.version_label)
        self.version_edit = QLineEdit()
        self.version_edit.setPlaceholderText("例如: 9.0.5")
        version_layout.addWidget(self.version_edit)
        layout.addLayout(version_layout)

        self.version_hint = QLabel()
        self.version_hint.setStyleSheet("color: #888; font-size: 9px; padding-left: 120px;")
        layout.addWidget(self.version_hint)

        # ---- Zotero 安装路径 ----
        path_label = QLabel()
        path_label.setMinimumWidth(120)
        path_layout = QHBoxLayout()
        path_layout.addWidget(path_label)
        self.path_edit = QLineEdit()
        self.path_edit.setReadOnly(True)
        self.path_edit.setStyleSheet("background-color: #f5f5f5;")
        path_layout.addWidget(self.path_edit, 1)
        self.browse_btn = QPushButton()
        self.browse_btn.clicked.connect(self._on_browse)
        path_layout.addWidget(self.browse_btn)
        layout.addLayout(path_layout)

        self.path_status = QLabel()
        self.path_status.setStyleSheet("font-size: 9px; padding-left: 120px;")
        layout.addWidget(self.path_status)

        # ---- 模板目录 ----
        template_label = QLabel()
        template_label.setMinimumWidth(120)
        template_layout = QHBoxLayout()
        template_layout.addWidget(template_label)
        self.template_edit = QLineEdit()
        self.template_edit.setReadOnly(True)
        self.template_edit.setStyleSheet("background-color: #f5f5f5;")
        template_layout.addWidget(self.template_edit, 1)
        self.template_browse_btn = QPushButton()
        self.template_browse_btn.clicked.connect(self._on_browse_template)
        template_layout.addWidget(self.template_browse_btn)
        layout.addLayout(template_layout)

        self.template_status = QLabel()
        self.template_status.setStyleSheet("font-size: 9px; padding-left: 120px;")
        layout.addWidget(self.template_status)

        # ---- Profiles 目录（项目库） ----
        profiles_label = QLabel()
        profiles_label.setMinimumWidth(120)
        profiles_layout = QHBoxLayout()
        profiles_layout.addWidget(profiles_label)
        self.profiles_edit = QLineEdit()
        self.profiles_edit.setReadOnly(True)
        self.profiles_edit.setStyleSheet("background-color: #f5f5f5;")
        profiles_layout.addWidget(self.profiles_edit, 1)
        self.profiles_browse_btn = QPushButton()
        self.profiles_browse_btn.clicked.connect(self._on_browse_profiles)
        profiles_layout.addWidget(self.profiles_browse_btn)
        layout.addLayout(profiles_layout)

        # Profiles 目录说明（新增）
        self.profiles_hint = QLabel()
        self.profiles_hint.setStyleSheet("color: #666; font-size: 9px; padding-left: 120px;")
        self.profiles_hint.setWordWrap(True)
        layout.addWidget(self.profiles_hint)

        # ---- 历史记录快速切换提示（新增） ----
        self.history_hint = QLabel()
        self.history_hint.setStyleSheet("color: #555; font-size: 9px; padding-left: 120px;")
        self.history_hint.setWordWrap(True)
        layout.addWidget(self.history_hint)

        # 按钮
        btn_layout = QHBoxLayout()
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

        # 存储引用供 retranslate
        self.labels = {
            'version': self.version_label,
            'path': path_label,
            'template': template_label,
            'profiles': profiles_label,
        }

    def retranslate_ui(self):
        self.setWindowTitle(self.i18n.tr("pref_title"))
        self.title_label.setText(self.i18n.tr("pref_title"))
        self.labels['version'].setText("🔢 Zotero 版本号:")
        self.version_hint.setText("💡 " + self.i18n.tr("pref_version_hint"))
        self.labels['path'].setText("📁 Zotero 安装路径:")
        self.browse_btn.setText(self.i18n.tr("btn_browse"))
        self.labels['template'].setText("📁 模板目录:")
        self.template_browse_btn.setText(self.i18n.tr("btn_browse"))
        self.labels['profiles'].setText("📁 项目库（Profiles 目录）:")

        # 新增的说明文字
        self.profiles_hint.setText("💡 " + self.i18n.tr("pref_profiles_hint"))
        self.history_hint.setText("💡 " + self.i18n.tr("pref_history_hint"))

        self.save_btn.setText(self.i18n.tr("pref_btn_save"))
        self.cancel_btn.setText(self.i18n.tr("pref_btn_cancel"))

    def _load_config(self):
        self.version_edit.setText(self.config.zotero_version)
        self.path_edit.setText(self.config.zotero_install_dir)
        self.template_edit.setText(self.config.templates_root)
        self.profiles_edit.setText(self.config.profiles_current)
        self._update_path_status()
        self._update_template_status()

    def _update_path_status(self):
        install_dir = self.path_edit.text()
        if install_dir and is_valid_directory(install_dir):
            exe_path = Path(install_dir) / "zotero.exe"
            if exe_path.exists():
                file_ver = self.controller.get_zotero_file_version(install_dir)
                if file_ver:
                    self.path_status.setText("✅ 已找到 zotero.exe（文件版本: {}）".format(file_ver))
                    self.path_status.setStyleSheet("color: green; font-size: 9px; padding-left: 120px;")
                else:
                    self.path_status.setText("✅ 已找到 zotero.exe")
                    self.path_status.setStyleSheet("color: green; font-size: 9px; padding-left: 120px;")
                return
        self.path_status.setText("⚠️ 未找到 zotero.exe，请选择正确的安装目录")
        self.path_status.setStyleSheet("color: #cc3333; font-size: 9px; padding-left: 120px;")

    def _update_template_status(self):
        template_root = self.template_edit.text()
        if template_root and is_valid_directory(template_root):
            templates = self.controller.get_templates(template_root)
            if templates:
                version = self.version_edit.text().strip()
                matched = False
                for t in templates:
                    if t == "v{}".format(version) or t.startswith("v{}.".format(version.split('.')[0])):
                        matched = True
                        break
                if matched:
                    self.template_status.setText("✅ 找到匹配的模板")
                    self.template_status.setStyleSheet("color: green; font-size: 9px; padding-left: 120px;")
                else:
                    self.template_status.setText("⚠️ 未找到与版本 {} 匹配的模板".format(version))
                    self.template_status.setStyleSheet("color: #cc3333; font-size: 9px; padding-left: 120px;")
                return
        self.template_status.setText("⚠️ 模板目录无效或为空")
        self.template_status.setStyleSheet("color: #cc3333; font-size: 9px; padding-left: 120px;")

    def _on_browse(self):
        dir_path = QFileDialog.getExistingDirectory(
            self,
            self.i18n.tr("btn_browse"),
            self.path_edit.text()
        )
        if dir_path:
            self.path_edit.setText(dir_path)
            self._update_path_status()

    def _on_browse_template(self):
        dir_path = QFileDialog.getExistingDirectory(
            self,
            self.i18n.tr("btn_browse"),
            self.template_edit.text()
        )
        if dir_path:
            self.template_edit.setText(dir_path)
            self._update_template_status()

    def _on_browse_profiles(self):
        dir_path = QFileDialog.getExistingDirectory(
            self,
            self.i18n.tr("btn_browse"),
            self.profiles_edit.text()
        )
        if dir_path:
            self.profiles_edit.setText(dir_path)

    def _on_save(self):
        version = self.version_edit.text().strip()
        if not version:
            QMessageBox.warning(self, "", "请正确输入 Zotero 版本号")
            return
        install_dir = self.path_edit.text()
        if not install_dir or not is_valid_directory(install_dir):
            QMessageBox.warning(self, "", "请选择有效的 Zotero 安装目录")
            return
        exe_path = Path(install_dir) / "zotero.exe"
        if not exe_path.exists():
            QMessageBox.warning(self, "", "未找到 zotero.exe，请选择正确的安装目录")
            return

        self.config.zotero_version = version
        self.config.zotero_install_dir = install_dir
        self.config.templates_root = self.template_edit.text()
        self.config.profiles_current = self.profiles_edit.text()
        if not self.config.profiles_default:
            self.config.profiles_default = self.config.profiles_current

        self.config_mgr.save()
        self.accept()
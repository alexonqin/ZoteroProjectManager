# -*- coding: utf-8 -*-
"""
偏好设置对话框
"""

import os
import subprocess
from pathlib import Path

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFileDialog, QFrame, QMessageBox, QComboBox,
    QRadioButton, QButtonGroup, QGroupBox
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
        self.controller = controller  # 使用外部传入的控制器

        self._setup_ui()
        self.retranslate_ui()
        self._load_config()

    def _setup_ui(self):
        self.setModal(True)
        self.setFixedWidth(640)

        layout = QVBoxLayout(self)
        layout.setSpacing(10)

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

        # ---- Profiles 目录 ----
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

        self.profiles_hint = QLabel()
        self.profiles_hint.setStyleSheet("color: #666; font-size: 9px; padding-left: 120px;")
        self.profiles_hint.setWordWrap(True)
        layout.addWidget(self.profiles_hint)

        # ---- 默认语言 ----
        lang_layout = QHBoxLayout()
        self.default_lang_label = QLabel()
        self.default_lang_label.setMinimumWidth(120)
        lang_layout.addWidget(self.default_lang_label)
        self.default_lang_combo = QComboBox()
        self.default_lang_combo.addItem("简体中文", 'zh-CN')
        self.default_lang_combo.addItem("English", 'en-US')
        self.default_lang_combo.addItem("跟随系统", '')
        lang_layout.addWidget(self.default_lang_combo)
        lang_layout.addStretch()
        layout.addLayout(lang_layout)

        self.default_lang_hint = QLabel()
        self.default_lang_hint.setStyleSheet("color: #888; font-size: 9px; padding-left: 120px;")
        layout.addWidget(self.default_lang_hint)

        # ---- 项目创建方式 ----
        method_layout = QVBoxLayout()
        method_layout.setSpacing(4)
        self.method_label = QLabel()
        method_layout.addWidget(self.method_label)

        self.method_group = QButtonGroup(self)
        self.method_auto = QRadioButton()
        self.method_template = QRadioButton()
        self.method_native = QRadioButton()
        self.method_group.addButton(self.method_auto, 0)
        self.method_group.addButton(self.method_template, 1)
        self.method_group.addButton(self.method_native, 2)

        self.method_hint = QLabel()
        self.method_hint.setStyleSheet("color: #888; font-size: 9px; padding-left: 20px;")
        self.method_hint.setWordWrap(True)

        method_layout.addWidget(self.method_auto)
        method_layout.addWidget(self.method_template)
        method_layout.addWidget(self.method_native)
        method_layout.addWidget(self.method_hint)
        layout.addLayout(method_layout)

        # ---- 项目完整度 ----
        profile_mode_layout = QVBoxLayout()
        profile_mode_layout.setSpacing(4)
        self.profile_mode_label = QLabel()
        profile_mode_layout.addWidget(self.profile_mode_label)

        self.profile_mode_group = QButtonGroup(self)
        self.profile_mode_full = QRadioButton()
        self.profile_mode_light = QRadioButton()
        self.profile_mode_group.addButton(self.profile_mode_full, 0)
        self.profile_mode_group.addButton(self.profile_mode_light, 1)

        self.profile_mode_full_desc = QLabel()
        self.profile_mode_full_desc.setStyleSheet("color: #666; font-size: 9px; padding-left: 20px;")
        self.profile_mode_full_desc.setWordWrap(True)

        self.profile_mode_light_desc = QLabel()
        self.profile_mode_light_desc.setStyleSheet("color: #666; font-size: 9px; padding-left: 20px;")
        self.profile_mode_light_desc.setWordWrap(True)

        profile_mode_layout.addWidget(self.profile_mode_full)
        profile_mode_layout.addWidget(self.profile_mode_full_desc)
        profile_mode_layout.addWidget(self.profile_mode_light)
        profile_mode_layout.addWidget(self.profile_mode_light_desc)
        layout.addLayout(profile_mode_layout)

        # ---- 底部状态提示 ----
        self.bottom_status = QLabel()
        self.bottom_status.setWordWrap(True)
        self.bottom_status.setStyleSheet("color: #cc8833; font-size: 10px; padding: 4px; background-color: #fff8e0; border-radius: 3px;")
        layout.addWidget(self.bottom_status)

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

        self.version_label.setText("🔢 Zotero 版本号:")
        self.version_hint.setText("💡 " + self.i18n.tr("pref_version_hint"))

        path_label = self.findChild(QLabel, "path_label")
        if path_label:
            path_label.setText("📁 Zotero 安装路径:")
        self.browse_btn.setText(self.i18n.tr("btn_browse"))

        template_label = self.findChild(QLabel, "template_label")
        if template_label:
            template_label.setText("📁 模板目录:")
        self.template_browse_btn.setText(self.i18n.tr("btn_browse"))

        profiles_label = self.findChild(QLabel, "profiles_label")
        if profiles_label:
            profiles_label.setText("📁 项目库（Profiles 目录）:")
        self.profiles_hint.setText("💡 " + self.i18n.tr("pref_profiles_hint"))

        self.default_lang_label.setText("🌐 " + self.i18n.tr("pref_default_language"))
        self.default_lang_hint.setText("💡 " + self.i18n.tr("pref_default_language_hint"))

        self.method_label.setText(self.i18n.tr("pref_creation_method"))
        self.method_auto.setText(self.i18n.tr("pref_creation_auto"))
        self.method_template.setText(self.i18n.tr("pref_creation_template"))
        self.method_native.setText(self.i18n.tr("pref_creation_native"))
        self.method_hint.setText("💡 " + self.i18n.tr("pref_creation_hint"))

        self.profile_mode_label.setText(self.i18n.tr("pref_profile_mode"))
        self.profile_mode_full.setText(self.i18n.tr("pref_profile_mode_full"))
        self.profile_mode_full_desc.setText("💡 " + self.i18n.tr("pref_profile_mode_full_desc"))
        self.profile_mode_light.setText(self.i18n.tr("pref_profile_mode_light"))
        self.profile_mode_light_desc.setText("💡 " + self.i18n.tr("pref_profile_mode_light_desc"))

        self.open_config_btn.setText(self.i18n.tr("pref_open_config_folder"))
        self.save_btn.setText(self.i18n.tr("pref_btn_save"))
        self.cancel_btn.setText(self.i18n.tr("pref_btn_cancel"))

        # 更新语言下拉
        for idx in range(self.default_lang_combo.count()):
            data = self.default_lang_combo.itemData(idx)
            if data == 'zh-CN':
                self.default_lang_combo.setItemText(idx, self.i18n.tr("lang_chinese"))
            elif data == 'en-US':
                self.default_lang_combo.setItemText(idx, self.i18n.tr("lang_english"))
            elif data == '':
                self.default_lang_combo.setItemText(idx, self.i18n.tr("lang_system"))

        self._update_ui_state()

    def _load_config(self):
        self.version_edit.setText(self.config.zotero_version)
        self.path_edit.setText(self.config.zotero_install_dir)
        self.template_edit.setText(self.config.templates_root)
        self.profiles_edit.setText(self.config.profiles_current)

        default_lang = getattr(self.config, 'default_language', 'zh-CN')
        for idx in range(self.default_lang_combo.count()):
            if self.default_lang_combo.itemData(idx) == default_lang:
                self.default_lang_combo.setCurrentIndex(idx)
                break

        method = self.config.creation_method
        if method == "template":
            self.method_template.setChecked(True)
        elif method == "native":
            self.method_native.setChecked(True)
        else:
            self.method_auto.setChecked(True)

        profile_mode = self.config.creation_profile_mode
        if profile_mode == "light":
            self.profile_mode_light.setChecked(True)
        else:
            self.profile_mode_full.setChecked(True)

        self._update_path_status()
        self._update_template_status()
        self._update_ui_state()

    def _update_path_status(self):
        install_dir = self.path_edit.text()
        if install_dir and is_valid_directory(install_dir):
            exe_path = Path(install_dir) / "zotero.exe"
            if exe_path.exists():
                file_ver = self.controller.get_zotero_file_version(install_dir)
                if file_ver:
                    self.path_status.setText(f"✅ 已找到 zotero.exe（文件版本: {file_ver}）")
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
                    if t == f"v{version}" or t.startswith(f"v{version.split('.')[0]}."):
                        matched = True
                        break
                if matched:
                    self.template_status.setText("✅ 找到匹配的模板")
                    self.template_status.setStyleSheet("color: green; font-size: 9px; padding-left: 120px;")
                else:
                    self.template_status.setText(f"⚠️ 未找到与版本 {version} 匹配的模板")
                    self.template_status.setStyleSheet("color: #cc3333; font-size: 9px; padding-left: 120px;")
                return
        self.template_status.setText("⚠️ 模板目录无效或为空")
        self.template_status.setStyleSheet("color: #cc3333; font-size: 9px; padding-left: 120px;")

    def _on_method_changed(self):
        self._update_ui_state()

    def _update_ui_state(self):
        method = self._get_method()
        is_template_required = (method == "template")

        if is_template_required:
            self.version_label.setStyleSheet("font-weight: bold; color: #cc3333;")
            self.version_label.setText("🔢 Zotero 版本号:（" + self.i18n.tr("first_launch_required") + "）")
            self.version_hint.setText("💡 " + self.i18n.tr("pref_version_required_hint"))
        else:
            self.version_label.setStyleSheet("font-weight: normal; color: #444;")
            self.version_label.setText("🔢 Zotero 版本号:（" + self.i18n.tr("first_launch_optional") + "）")
            self.version_hint.setText("💡 " + self.i18n.tr("pref_version_optional_hint"))

        if is_template_required:
            self.template_status.setVisible(True)
        else:
            self.template_status.setVisible(False)

        if method == "auto":
            self.bottom_status.setText("💡 " + self.i18n.tr("pref_auto_status"))
            self.bottom_status.setStyleSheet("color: #2b7a62; font-size: 10px; padding: 4px; background-color: #e8f5e9; border-radius: 3px;")
        elif method == "template":
            self.bottom_status.setText("⚠️ " + self.i18n.tr("pref_template_status"))
            self.bottom_status.setStyleSheet("color: #cc3333; font-size: 10px; padding: 4px; background-color: #ffebee; border-radius: 3px;")
        else:
            self.bottom_status.setText("💡 " + self.i18n.tr("pref_native_status"))
            self.bottom_status.setStyleSheet("color: #2b7a62; font-size: 10px; padding: 4px; background-color: #e8f5e9; border-radius: 3px;")

    def _get_method(self) -> str:
        if self.method_template.isChecked():
            return "template"
        elif self.method_native.isChecked():
            return "native"
        else:
            return "auto"

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
        method = self._get_method()
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

        version = self.version_edit.text().strip()
        templates_root = self.template_edit.text()
        if method == "template":
            if not version:
                QMessageBox.warning(self, "", "使用模板模式需要设置 Zotero 版本号")
                return
            if not templates_root or not is_valid_directory(templates_root):
                QMessageBox.warning(self, "", "使用模板模式需要设置模板目录")
                return

        profile_mode = "full" if self.profile_mode_full.isChecked() else "light"

        self.config.zotero_version = version
        self.config.zotero_install_dir = install_dir
        self.config.templates_root = templates_root
        self.config.profiles_current = profiles_dir
        if not self.config.profiles_default:
            self.config.profiles_default = profiles_dir
        self.config.default_language = self.default_lang_combo.currentData()
        self.config.creation_method = method
        self.config.creation_profile_mode = profile_mode

        self.config_mgr.save()
        self.accept()
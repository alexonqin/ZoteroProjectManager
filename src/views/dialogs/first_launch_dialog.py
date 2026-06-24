# -*- coding: utf-8 -*-
"""
首次启动引导对话框
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFileDialog, QFrame, QMessageBox,
    QLineEdit, QComboBox, QRadioButton, QButtonGroup
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
        self.result_config = {}

        self._setup_ui()
        self.retranslate_ui()
        self._on_creation_method_changed()

    def _setup_ui(self):
        self.setModal(True)
        self.setFixedWidth(600)
        self.setFixedHeight(520)

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

        # ---- 创建方式 ----
        method_layout = QVBoxLayout()
        method_layout.setSpacing(4)
        self.method_label = QLabel()
        self.method_label.setStyleSheet("font-weight: bold;")
        method_layout.addWidget(self.method_label)

        self.method_group = QButtonGroup(self)
        self.method_auto = QRadioButton()
        self.method_template = QRadioButton()
        self.method_native = QRadioButton()
        self.method_group.addButton(self.method_auto, 0)
        self.method_group.addButton(self.method_template, 1)
        self.method_group.addButton(self.method_native, 2)
        self.method_auto.setChecked(True)

        self.method_hint = QLabel()
        self.method_hint.setStyleSheet("color: #888; font-size: 9px; padding-left: 20px;")
        self.method_hint.setWordWrap(True)

        method_layout.addWidget(self.method_auto)
        method_layout.addWidget(self.method_template)
        method_layout.addWidget(self.method_native)
        method_layout.addWidget(self.method_hint)
        layout.addLayout(method_layout)

        # 连接信号
        self.method_auto.toggled.connect(self._on_creation_method_changed)
        self.method_template.toggled.connect(self._on_creation_method_changed)
        self.method_native.toggled.connect(self._on_creation_method_changed)

        line2 = QFrame()
        line2.setFrameShape(QFrame.HLine)
        line2.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line2)

        # ---- Zotero 安装路径（始终必填） ----
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

        self.path_hint = QLabel()
        self.path_hint.setStyleSheet("color: #888; font-size: 9px; padding-left: 140px;")
        layout.addWidget(self.path_hint)

        # ---- 项目库目录（始终必填） ----
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

        self.profiles_hint = QLabel()
        self.profiles_hint.setStyleSheet("color: #888; font-size: 9px; padding-left: 140px;")
        layout.addWidget(self.profiles_hint)

        line3 = QFrame()
        line3.setFrameShape(QFrame.HLine)
        line3.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line3)

        # ---- Zotero 版本号（条件必填） ----
        version_layout = QHBoxLayout()
        self.version_label = QLabel()
        self.version_label.setMinimumWidth(140)
        version_layout.addWidget(self.version_label)
        self.version_edit = QLineEdit()
        self.version_edit.setPlaceholderText("例如: 9.0.5")
        version_layout.addWidget(self.version_edit)
        layout.addLayout(version_layout)

        self.version_hint = QLabel()
        self.version_hint.setStyleSheet("color: #888; font-size: 9px; padding-left: 140px;")
        layout.addWidget(self.version_hint)

        # ---- 模板目录（条件必填） ----
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

        self.template_hint = QLabel()
        self.template_hint.setStyleSheet("color: #888; font-size: 9px; padding-left: 140px;")
        layout.addWidget(self.template_hint)

        # ---- 底部提示 ----
        self.bottom_hint = QLabel()
        self.bottom_hint.setWordWrap(True)
        self.bottom_hint.setStyleSheet("color: #cc8833; font-size: 10px; padding: 6px; background-color: #fff8e0; border-radius: 3px;")
        layout.addWidget(self.bottom_hint)

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

        self.method_label.setText(self.i18n.tr("first_launch_method_label"))
        self.method_auto.setText(self.i18n.tr("pref_creation_auto"))
        self.method_template.setText(self.i18n.tr("pref_creation_template"))
        self.method_native.setText(self.i18n.tr("pref_creation_native"))
        self.method_hint.setText(self.i18n.tr("first_launch_method_hint"))

        self.path_label.setText("📁 " + self.i18n.tr("first_launch_path_label") + "（" + self.i18n.tr("first_launch_required") + "）")
        self.path_hint.setText("💡 " + self.i18n.tr("first_launch_path_hint"))
        self.browse_btn.setText(self.i18n.tr("btn_browse"))

        self.profiles_label.setText("📁 " + self.i18n.tr("first_launch_profiles_label") + "（" + self.i18n.tr("first_launch_required") + "）")
        self.profiles_hint.setText("💡 " + self.i18n.tr("first_launch_profiles_hint"))
        self.profiles_browse_btn.setText(self.i18n.tr("btn_browse"))

        self.version_label.setText("🔢 " + self.i18n.tr("first_launch_version_label") + "（" + self.i18n.tr("first_launch_optional") + "）")
        self.version_hint.setText("💡 " + self.i18n.tr("first_launch_version_hint"))

        self.template_label.setText("📁 " + self.i18n.tr("first_launch_template_label") + "（" + self.i18n.tr("first_launch_optional") + "）")
        self.template_hint.setText("💡 " + self.i18n.tr("first_launch_template_hint"))

        self.ok_btn.setText(self.i18n.tr("first_launch_btn_ok"))

        self._update_ui_state()

    def _on_creation_method_changed(self):
        self._update_ui_state()

    def _update_ui_state(self):
        """根据创建方式更新字段必填状态和提示"""
        method = self._get_selected_method()

        # 版本号和模板目录是否为必填
        is_template_required = (method == "template")
        is_optional = (method == "auto" or method == "native")

        # 更新标签样式
        if is_template_required:
            self.version_label.setText("🔢 " + self.i18n.tr("first_launch_version_label") + "（" + self.i18n.tr("first_launch_required") + "）")
            self.version_label.setStyleSheet("font-weight: bold; color: #cc3333;")
            self.template_label.setText("📁 " + self.i18n.tr("first_launch_template_label") + "（" + self.i18n.tr("first_launch_required") + "）")
            self.template_label.setStyleSheet("font-weight: bold; color: #cc3333;")
        else:
            self.version_label.setText("🔢 " + self.i18n.tr("first_launch_version_label") + "（" + self.i18n.tr("first_launch_optional") + "）")
            self.version_label.setStyleSheet("font-weight: normal; color: #444;")
            self.template_label.setText("📁 " + self.i18n.tr("first_launch_template_label") + "（" + self.i18n.tr("first_launch_optional") + "）")
            self.template_label.setStyleSheet("font-weight: normal; color: #444;")

        # 更新底部提示
        if method == "auto":
            self.bottom_hint.setText("💡 " + self.i18n.tr("first_launch_auto_hint"))
        elif method == "template":
            self.bottom_hint.setText("⚠️ " + self.i18n.tr("first_launch_template_mode_hint"))
        else:  # native
            self.bottom_hint.setText("💡 " + self.i18n.tr("first_launch_native_hint"))

    def _get_selected_method(self) -> str:
        if self.method_template.isChecked():
            return "template"
        elif self.method_native.isChecked():
            return "native"
        else:
            return "auto"

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
        # 验证必填字段
        install_dir = self.path_edit.text()
        profiles_dir = self.profiles_edit.text()
        method = self._get_selected_method()

        if not install_dir or not is_valid_directory(install_dir):
            QMessageBox.warning(self, "", self.i18n.tr("first_launch_error_path"))
            return
        if not (Path(install_dir) / "zotero.exe").exists():
            QMessageBox.warning(self, "", self.i18n.tr("first_launch_error_exe"))
            return
        if not profiles_dir or not is_valid_directory(profiles_dir):
            QMessageBox.warning(self, "", self.i18n.tr("first_launch_error_profiles"))
            return

        # 如果使用模板模式，验证版本号和模板目录
        if method == "template":
            version = self.version_edit.text().strip()
            template_root = self.template_edit.text()
            if not version:
                QMessageBox.warning(self, "", self.i18n.tr("first_launch_error_version"))
                return
            if not template_root or not is_valid_directory(template_root):
                QMessageBox.warning(self, "", self.i18n.tr("first_launch_error_template"))
                return

        self.result_config = {
            "zotero_version": self.version_edit.text().strip(),
            "zotero_install_dir": install_dir,
            "templates_root": self.template_edit.text(),
            "profiles_current": profiles_dir,
            "profiles_default": profiles_dir,
            "creation_method": method
        }
        self.accept()
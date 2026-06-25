# -*- coding: utf-8 -*-
"""
新建项目对话框
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFileDialog, QFrame, QMessageBox,
    QComboBox
)
from PySide6.QtCore import Qt
from pathlib import Path

from utils.i18n import I18n
from utils.path_utils import is_valid_directory
from controllers import ZoteroController   # 仅用于类型提示，不实例化


class NewProjectDialog(QDialog):
    def __init__(self, i18n: I18n, config, controller: ZoteroController, parent=None):
        super().__init__(parent)
        self.i18n = i18n
        self.config = config
        self.controller = controller  # 使用外部传入的控制器

        self.result_data = None  # (name, location, language)

        self._setup_ui()
        self.retranslate_ui()
        self._update_preview()

    def _setup_ui(self):
        self.setModal(True)
        self.setFixedWidth(580)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        self.title_label = QLabel()
        self.title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(self.title_label)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line)

        # 项目名称
        name_layout = QHBoxLayout()
        self.name_label = QLabel()
        self.name_label.setMinimumWidth(80)
        name_layout.addWidget(self.name_label)
        self.name_edit = QLineEdit()
        name_layout.addWidget(self.name_edit)
        layout.addLayout(name_layout)

        # 存放位置
        loc_layout = QHBoxLayout()
        self.loc_label = QLabel()
        self.loc_label.setMinimumWidth(80)
        loc_layout.addWidget(self.loc_label)
        self.loc_edit = QLineEdit()
        self.loc_edit.setReadOnly(True)
        self.loc_edit.setStyleSheet("background-color: #f5f5f5;")
        self.loc_edit.setText(self.config.profiles_current)
        loc_layout.addWidget(self.loc_edit, 1)
        self.browse_btn = QPushButton()
        self.browse_btn.clicked.connect(self._on_browse)
        loc_layout.addWidget(self.browse_btn)
        layout.addLayout(loc_layout)

        # 界面语言
        lang_layout = QHBoxLayout()
        self.lang_label = QLabel()
        self.lang_label.setMinimumWidth(80)
        lang_layout.addWidget(self.lang_label)
        self.lang_combo = QComboBox()
        self.lang_combo.addItem(self.i18n.tr("lang_chinese"), 'zh-CN')
        self.lang_combo.addItem(self.i18n.tr("lang_english"), 'en-US')
        self.lang_combo.addItem(self.i18n.tr("lang_system"), '')
        default_lang = getattr(self.config, 'default_language', 'zh-CN')
        for idx in range(self.lang_combo.count()):
            if self.lang_combo.itemData(idx) == default_lang:
                self.lang_combo.setCurrentIndex(idx)
                break
        lang_layout.addWidget(self.lang_combo)
        lang_layout.addStretch()
        layout.addLayout(lang_layout)

        # ---- 模板信息（仅显示，不阻止创建） ----
        self.template_info = QLabel()
        self.template_info.setStyleSheet("color: #666; font-size: 9px; padding-left: 80px;")
        layout.addWidget(self.template_info)

        # ---- 创建方式信息 ----
        self.method_info = QLabel()
        self.method_info.setStyleSheet("color: #2b7a62; font-size: 9px; padding-left: 80px; font-weight: bold;")
        layout.addWidget(self.method_info)

        line2 = QFrame()
        line2.setFrameShape(QFrame.HLine)
        line2.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line2)

        layout.addStretch()

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.cancel_btn = QPushButton()
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.cancel_btn)
        self.create_btn = QPushButton()
        self.create_btn.setStyleSheet("""
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
        self.create_btn.clicked.connect(self._on_create)
        btn_layout.addWidget(self.create_btn)
        layout.addLayout(btn_layout)

        self.name_edit.textChanged.connect(self._update_preview)
        self.loc_edit.textChanged.connect(self._update_preview)
        self.lang_combo.currentIndexChanged.connect(self._update_preview)

    def retranslate_ui(self):
        self.setWindowTitle(self.i18n.tr("new_project_title"))
        self.title_label.setText(self.i18n.tr("new_project_title"))
        self.name_label.setText(self.i18n.tr("new_project_name_label"))
        self.loc_label.setText(self.i18n.tr("new_project_location_label"))
        self.lang_label.setText(self.i18n.tr("new_project_language_label"))
        self.browse_btn.setText(self.i18n.tr("btn_browse"))
        self.create_btn.setText(self.i18n.tr("new_project_btn_create"))
        self.cancel_btn.setText(self.i18n.tr("new_project_btn_cancel"))

        # 更新语言下拉
        for idx in range(self.lang_combo.count()):
            data = self.lang_combo.itemData(idx)
            if data == 'zh-CN':
                self.lang_combo.setItemText(idx, self.i18n.tr("lang_chinese"))
            elif data == 'en-US':
                self.lang_combo.setItemText(idx, self.i18n.tr("lang_english"))
            elif data == '':
                self.lang_combo.setItemText(idx, self.i18n.tr("lang_system"))

        self._update_preview()

    def _on_browse(self):
        path = QFileDialog.getExistingDirectory(
            self,
            self.i18n.tr("btn_browse"),
            self.loc_edit.text()
        )
        if path and is_valid_directory(path):
            self.loc_edit.setText(path)

    def _get_creation_method(self) -> str:
        return getattr(self.config, 'creation_method', 'auto')

    def _has_matching_template(self) -> bool:
        templates_root = self.config.templates_root
        version = self.config.zotero_version
        if not templates_root or not version:
            return False
        templates = self.controller.get_templates(templates_root)
        for t in templates:
            if t == f"v{version}" or t.startswith(f"v{version.split('.')[0]}."):
                return True
        return False

    def _get_method_display(self) -> str:
        method = self._get_creation_method()
        has_template = self._has_matching_template()

        if method == "template":
            if has_template:
                return self.i18n.tr("new_project_method_template")
            else:
                return "⚠️ " + self.i18n.tr("new_project_method_template_warning")
        elif method == "native":
            return self.i18n.tr("new_project_method_native")
        else:  # auto
            if has_template:
                return self.i18n.tr("new_project_method_template")
            else:
                return self.i18n.tr("new_project_method_native")

    def _update_preview(self):
        name = self.name_edit.text().strip()
        version = self.config.zotero_version
        templates_root = self.config.templates_root

        if name and version and templates_root:
            templates = self.controller.get_templates(templates_root)
            matched = False
            for t in templates:
                if t == f"v{version}" or t.startswith(f"v{version.split('.')[0]}."):
                    matched = True
                    break
            if matched:
                self.template_info.setText(f"✅ 使用模板: v{version}（与 Zotero {version} 匹配）")
                self.template_info.setStyleSheet("color: green; font-size: 9px; padding-left: 80px;")
            else:
                self.template_info.setText(f"⚠️ 未找到匹配 Zotero {version} 的模板")
                self.template_info.setStyleSheet("color: #cc3333; font-size: 9px; padding-left: 80px;")
        else:
            self.template_info.setText("")

        # 更新创建方式信息
        method_display = self._get_method_display()
        self.method_info.setText("💡 " + method_display)
        if "⚠️" in method_display:
            self.method_info.setStyleSheet("color: #cc8833; font-size: 9px; padding-left: 80px; font-weight: bold;")
        else:
            self.method_info.setStyleSheet("color: #2b7a62; font-size: 9px; padding-left: 80px; font-weight: bold;")

    def _on_create(self):
        name = self.name_edit.text().strip()
        location = self.loc_edit.text()
        language = self.lang_combo.currentData()

        if not name:
            QMessageBox.warning(self, "", "请输入项目名称")
            return
        if not location or not is_valid_directory(location):
            QMessageBox.warning(self, "", "请选择有效的存放位置")
            return

        illegal = r'<>:"/\|?*'
        for ch in illegal:
            if ch in name:
                QMessageBox.warning(self, "", f"项目名称不能包含非法字符: {ch}")
                return

        if (Path(location) / name).exists():
            QMessageBox.warning(self, "", f"项目 '{name}' 已存在")
            return

        self.result_data = (name, location, language)
        self.accept()
# -*- coding: utf-8 -*-
"""
新建项目对话框
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QCheckBox, QFileDialog, QFrame, QMessageBox
)
from PySide6.QtCore import Qt
from pathlib import Path

from utils.i18n import I18n
from utils.path_utils import is_valid_directory
from controllers.zotero_controller import ZoteroController


class NewProjectDialog(QDialog):
    """新建项目对话框"""

    def __init__(self, i18n: I18n, config, parent=None):
        super().__init__(parent)
        self.i18n = i18n
        self.config = config
        self.controller = ZoteroController()

        self.result_data = None  # (name, location, create_shortcut)

        self._setup_ui()
        self.retranslate_ui()
        self._update_preview()

    def _setup_ui(self):
        self.setModal(True)
        self.setFixedWidth(550)

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

        # 项目名称
        name_layout = QHBoxLayout()
        self.name_label = QLabel()
        self.name_label.setMinimumWidth(80)
        name_layout.addWidget(self.name_label)
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("")
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

        # 模板信息
        self.template_info = QLabel()
        self.template_info.setStyleSheet("color: #666; font-size: 9px; padding-left: 80px;")
        layout.addWidget(self.template_info)

        line2 = QFrame()
        line2.setFrameShape(QFrame.HLine)
        line2.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line2)

        # 选项
        self.shortcut_cb = QCheckBox()
        self.shortcut_cb.setChecked(self.config.auto_create_shortcut)
        layout.addWidget(self.shortcut_cb)

        layout.addStretch()

        # 按钮
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

        # 连接信号
        self.name_edit.textChanged.connect(self._update_preview)

    def retranslate_ui(self):
        self.setWindowTitle(self.i18n.tr("new_project_title"))
        self.title_label.setText(self.i18n.tr("new_project_title"))
        self.name_label.setText(self.i18n.tr("new_project_name_label"))
        self.loc_label.setText(self.i18n.tr("new_project_location_label"))
        self.browse_btn.setText(self.i18n.tr("btn_browse"))
        self.shortcut_cb.setText(self.i18n.tr("new_project_create_shortcut"))
        self.create_btn.setText(self.i18n.tr("new_project_btn_create"))
        self.cancel_btn.setText(self.i18n.tr("new_project_btn_cancel"))

    def _on_browse(self):
        path = QFileDialog.getExistingDirectory(
            self,
            self.i18n.tr("btn_browse"),
            self.loc_edit.text()
        )
        if path and is_valid_directory(path):
            self.loc_edit.setText(path)

    def _update_preview(self):
        name = self.name_edit.text().strip()
        version = self.config.zotero_version
        templates_root = self.config.templates_root

        if name and version and templates_root:
            # 检查模板是否匹配
            templates = self.controller.get_templates(templates_root)
            matched = False
            for t in templates:
                if t == "v{}".format(version) or t.startswith("v{}.".format(version.split('.')[0])):
                    matched = True
                    break
            if matched:
                self.template_info.setText("✅ 使用模板: v{}（与 Zotero {} 匹配）".format(version, version))
                self.template_info.setStyleSheet("color: green; font-size: 9px; padding-left: 80px;")
            else:
                self.template_info.setText("⚠️ 未找到匹配 Zotero {} 的模板".format(version))
                self.template_info.setStyleSheet("color: #cc3333; font-size: 9px; padding-left: 80px;")
        else:
            self.template_info.setText("")

    def _on_create(self):
        name = self.name_edit.text().strip()
        location = self.loc_edit.text()

        if not name:
            QMessageBox.warning(self, "", "请输入项目名称")
            return
        if not location or not is_valid_directory(location):
            QMessageBox.warning(self, "", "请选择有效的存放位置")
            return

        # 检查非法字符
        illegal_chars = r'<>:"/\|?*'
        for ch in illegal_chars:
            if ch in name:
                QMessageBox.warning(self, "", "项目名称不能包含非法字符: {}".format(ch))
                return

        # 检查是否已存在 (修正括号)
        if (Path(location) / name).exists():
            QMessageBox.warning(self, "", "项目 '{}' 已存在".format(name))
            return

        self.result_data = (name, location, self.shortcut_cb.isChecked())
        self.accept()
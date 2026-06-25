# -*- coding: utf-8 -*-
"""
新建项目对话框（简化版）
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFileDialog, QFrame, QMessageBox
)
from PySide6.QtCore import Qt
from pathlib import Path

from utils.i18n import I18n
from utils.path_utils import is_valid_directory
from controllers import ZoteroController


class NewProjectDialog(QDialog):
    def __init__(self, i18n: I18n, config, controller: ZoteroController, parent=None):
        super().__init__(parent)
        self.i18n = i18n
        self.config = config
        self.controller = controller

        self.result_data = None  # (name, location)

        self._setup_ui()
        self.retranslate_ui()

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

        # 提示信息
        self.hint_label = QLabel()
        self.hint_label.setWordWrap(True)
        self.hint_label.setStyleSheet("color: #444; font-size: 10px; padding: 6px; background-color: #f5f5f5; border-radius: 3px;")
        layout.addWidget(self.hint_label)

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
        self.create_btn.setEnabled(False)
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
            QPushButton:disabled {
                background-color: #aaaaaa;
            }
        """)
        self.create_btn.clicked.connect(self._on_create)
        btn_layout.addWidget(self.create_btn)
        layout.addLayout(btn_layout)

        self.name_edit.textChanged.connect(self._update_create_button)

    def retranslate_ui(self):
        self.setWindowTitle(self.i18n.tr("new_project_title"))
        self.title_label.setText(self.i18n.tr("new_project_title"))
        self.name_label.setText(self.i18n.tr("new_project_name_label"))
        self.loc_label.setText(self.i18n.tr("new_project_location_label"))
        self.browse_btn.setText(self.i18n.tr("btn_browse"))
        self.create_btn.setText(self.i18n.tr("new_project_btn_create"))
        self.cancel_btn.setText(self.i18n.tr("new_project_btn_cancel"))

        # 更新提示文字
        self.hint_label.setText(
            "💡 项目创建后，首次启动需联网下载必要文件。\n"
            "💡 项目语言默认为“跟随系统”，创建后在本软件主界面可快速修改。"
        )

    def _update_create_button(self):
        name = self.name_edit.text().strip()
        self.create_btn.setEnabled(bool(name))

    def _on_browse(self):
        path = QFileDialog.getExistingDirectory(
            self,
            self.i18n.tr("btn_browse"),
            self.loc_edit.text()
        )
        if path and is_valid_directory(path):
            self.loc_edit.setText(path)

    def _on_create(self):
        name = self.name_edit.text().strip()
        location = self.loc_edit.text()

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

        self.result_data = (name, location)
        self.accept()
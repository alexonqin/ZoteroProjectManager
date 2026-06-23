# -*- coding: utf-8 -*-
"""
删除确认对话框 - 双重验证（输入名称 + 复选框）
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QCheckBox, QFrame, QMessageBox
)
from PySide6.QtCore import Qt

from utils.i18n import I18n
from models.profile import Profile


class DeleteConfirmDialog(QDialog):
    """删除确认对话框，要求输入项目名称并勾选确认"""

    def __init__(self, i18n: I18n, profile: Profile, size_mb: float, parent=None):
        super().__init__(parent)
        self.i18n = i18n
        self.profile = profile
        self.size_mb = size_mb
        self._setup_ui()
        self.retranslate_ui()
        self._update_button_state()

    def _setup_ui(self):
        self.setModal(True)
        self.setFixedWidth(550)
        self.setFixedHeight(450)

        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # 标题
        self.title_label = QLabel()
        self.title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #cc3333;")
        layout.addWidget(self.title_label)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line)

        # 项目信息
        self.info_label = QLabel()
        self.info_label.setWordWrap(True)
        self.info_label.setStyleSheet("font-size: 12px;")
        layout.addWidget(self.info_label)

        # 删除内容列表
        self.content_label = QLabel()
        self.content_label.setWordWrap(True)
        self.content_label.setStyleSheet("font-size: 11px; color: #444; padding: 6px; background-color: #f5f5f5; border-radius: 3px;")
        layout.addWidget(self.content_label)

        # 回收站提示
        self.recycle_label = QLabel()
        self.recycle_label.setWordWrap(True)
        self.recycle_label.setStyleSheet("font-size: 11px; color: #2b7a62; font-weight: bold;")
        layout.addWidget(self.recycle_label)

        # 警告：清空回收站
        self.warning_label = QLabel()
        self.warning_label.setWordWrap(True)
        self.warning_label.setStyleSheet("font-size: 11px; color: #cc3333;")
        layout.addWidget(self.warning_label)

        # 分隔线
        line2 = QFrame()
        line2.setFrameShape(QFrame.HLine)
        line2.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line2)

        # 输入名称
        input_layout = QHBoxLayout()
        self.input_label = QLabel()
        self.input_label.setMinimumWidth(120)
        input_layout.addWidget(self.input_label)
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("")
        self.name_input.textChanged.connect(self._update_button_state)
        input_layout.addWidget(self.name_input)
        layout.addLayout(input_layout)

        # 确认复选框
        self.confirm_cb = QCheckBox()
        self.confirm_cb.stateChanged.connect(self._update_button_state)
        layout.addWidget(self.confirm_cb)

        layout.addStretch()

        # 按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.cancel_btn = QPushButton()
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.cancel_btn)
        self.delete_btn = QPushButton()
        self.delete_btn.setEnabled(False)
        self.delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #cc3333;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 24px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #aa2222;
            }
            QPushButton:disabled {
                background-color: #aaaaaa;
            }
        """)
        self.delete_btn.clicked.connect(self.accept)
        btn_layout.addWidget(self.delete_btn)
        layout.addLayout(btn_layout)

    def _update_button_state(self):
        name_match = self.name_input.text().strip() == self.profile.name
        check_ok = self.confirm_cb.isChecked()
        self.delete_btn.setEnabled(name_match and check_ok)

    def retranslate_ui(self):
        self.setWindowTitle(self.i18n.tr("delete_confirm_title"))
        self.title_label.setText(self.i18n.tr("delete_confirm_title"))
        self.info_label.setText(
            f"{self.i18n.tr('delete_confirm_project_name')} {self.profile.name}\n"
            f"{self.i18n.tr('delete_confirm_path')} {self.profile.project_path}\n"
            f"{self.i18n.tr('delete_confirm_size')} {self.size_mb:.1f} MB\n"
            f"{self.i18n.tr('delete_confirm_item_count')} {self.profile.get_item_count()}\n"
            f"{self.i18n.tr('delete_confirm_plugin_count')} {self.profile.get_plugin_count()}"
        )
        self.content_label.setText(self.i18n.tr("delete_confirm_content_list"))
        self.recycle_label.setText("✅ " + self.i18n.tr("delete_confirm_recycle_hint"))
        self.warning_label.setText("⚠️ " + self.i18n.tr("delete_confirm_clear_warning"))
        self.input_label.setText(self.i18n.tr("delete_confirm_input_label"))
        self.confirm_cb.setText(self.i18n.tr("delete_confirm_checkbox"))
        self.delete_btn.setText(self.i18n.tr("dialog_delete_btn_yes"))
        self.cancel_btn.setText(self.i18n.tr("dialog_delete_btn_no"))
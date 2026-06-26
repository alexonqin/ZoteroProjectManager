# -*- coding: utf-8 -*-
"""
快捷方式修复对话框
"""

from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QMessageBox
from PySide6.QtCore import Qt

from utils.i18n import I18n
from utils.config_manager import ConfigManager
from utils.repair_shortcut_utils import repair_shortcuts


class RepairShortcutDialog(QDialog):
    """快捷方式修复确认对话框"""

    def __init__(self, i18n: I18n, config_mgr: ConfigManager, parent=None):
        super().__init__(parent)
        self.i18n = i18n
        self.config_mgr = config_mgr
        self._setup_ui()
        self.retranslate_ui()

    def _setup_ui(self):
        self.setModal(True)
        self.setFixedWidth(550)
        self.setFixedHeight(330)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        self.title_label = QLabel()
        self.title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(self.title_label)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line)

        self.desc_label = QLabel()
        self.desc_label.setWordWrap(True)
        self.desc_label.setStyleSheet("font-size: 12px; color: #444;")
        layout.addWidget(self.desc_label)

        self.actions_label = QLabel()
        self.actions_label.setWordWrap(True)
        self.actions_label.setStyleSheet("font-size: 11px; color: #444; padding: 6px; background-color: #f5f5f5; border-radius: 3px;")
        layout.addWidget(self.actions_label)

        layout.addStretch()

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.cancel_btn = QPushButton()
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.cancel_btn)

        self.repair_btn = QPushButton()
        self.repair_btn.setStyleSheet("""
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
        self.repair_btn.clicked.connect(self._on_repair)
        btn_layout.addWidget(self.repair_btn)
        layout.addLayout(btn_layout)

    def retranslate_ui(self):
        self.setWindowTitle(self.i18n.tr("repair_shortcut_title"))
        self.title_label.setText(self.i18n.tr("repair_shortcut_title"))
        self.desc_label.setText(self.i18n.tr("repair_shortcut_desc"))
        self.actions_label.setText(self.i18n.tr("repair_shortcut_actions"))
        self.repair_btn.setText(self.i18n.tr("repair_btn_execute"))
        self.cancel_btn.setText(self.i18n.tr("pref_btn_cancel"))

    def _on_repair(self):
        try:
            created, skipped = repair_shortcuts(self.config_mgr)
        except Exception as e:
            QMessageBox.critical(self, self.i18n.tr("repair_failed"),
                                 self.i18n.tr("repair_error").format(error=str(e)))
            return

        if created == 0 and skipped == 0:
            QMessageBox.information(self, self.i18n.tr("repair_success"),
                                    self.i18n.tr("repair_no_projects"))
        else:
            result_msg = self.i18n.tr("repair_success_shortcut_detail").format(created=created, skipped=skipped)
            QMessageBox.information(self, self.i18n.tr("repair_success"), result_msg)
        self.accept()
# -*- coding: utf-8 -*-
"""
启动修复对话框
"""

from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QMessageBox
from PySide6.QtCore import Qt

from utils.i18n import I18n
from utils.config_manager import ConfigManager
from utils.repair_utils import repair_launch


class RepairLaunchDialog(QDialog):
    """启动修复确认对话框"""

    def __init__(self, i18n: I18n, config_mgr: ConfigManager, parent=None):
        super().__init__(parent)
        self.i18n = i18n
        self.config_mgr = config_mgr
        self._setup_ui()
        self.retranslate_ui()

    def _setup_ui(self):
        self.setModal(True)
        self.setFixedWidth(550)
        self.setFixedHeight(380)

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

        self.hint_label = QLabel()
        self.hint_label.setWordWrap(True)
        self.hint_label.setStyleSheet("font-size: 11px; color: #2b7a62;")
        layout.addWidget(self.hint_label)

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
        self.setWindowTitle(self.i18n.tr("repair_launch_title"))
        self.title_label.setText(self.i18n.tr("repair_launch_title"))
        self.desc_label.setText(self.i18n.tr("repair_launch_desc"))
        self.actions_label.setText(self.i18n.tr("repair_launch_actions"))
        self.hint_label.setText("💡 " + self.i18n.tr("repair_launch_hint"))
        self.repair_btn.setText(self.i18n.tr("repair_btn_execute"))
        self.cancel_btn.setText(self.i18n.tr("pref_btn_cancel"))

    def _on_repair(self):
        try:
            success, message, backup_path = repair_launch(self.config_mgr)
        except Exception as e:
            QMessageBox.critical(self, self.i18n.tr("repair_failed"),
                                 self.i18n.tr("repair_error").format(error=str(e)))
            return

        if success:
            result_msg = self.i18n.tr("repair_success_launch_detail").format(count=message)
            if backup_path:
                result_msg += "\n\n" + self.i18n.tr("repair_backup_info").format(path=backup_path)
            result_msg += "\n\n" + self.i18n.tr("repair_restart_hint")
            QMessageBox.information(self, self.i18n.tr("repair_success"), result_msg)
            self.accept()
        else:
            QMessageBox.critical(self, self.i18n.tr("repair_failed"),
                                 self.i18n.tr("repair_error").format(error=message))
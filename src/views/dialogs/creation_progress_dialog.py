# -*- coding: utf-8 -*-
"""
项目创建进度对话框 - 带倒计时
"""

from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QCloseEvent

from utils.i18n import I18n


class CreationProgressDialog(QDialog):
    """项目创建进度对话框，显示倒计时，计时结束才可确认"""

    def __init__(self, i18n: I18n, project_name: str, parent=None):
        super().__init__(parent)
        self.i18n = i18n
        self.project_name = project_name
        self.remaining = 120  # 倒计时秒数

        self._setup_ui()
        self.retranslate_ui()

        # 启动倒计时定时器
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_countdown)
        self.timer.start(1000)  # 每秒更新

    def _setup_ui(self):
        self.setModal(True)
        self.setFixedWidth(500)
        self.setFixedHeight(250)
        # 禁用窗口关闭按钮
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowCloseButtonHint)
        # 窗口置顶
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)

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

        # 提示信息
        self.info_label = QLabel()
        self.info_label.setWordWrap(True)
        self.info_label.setStyleSheet("font-size: 12px; color: #444;")
        layout.addWidget(self.info_label)

        # 倒计时显示
        self.countdown_label = QLabel()
        self.countdown_label.setAlignment(Qt.AlignCenter)
        self.countdown_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #2b7a62;")
        layout.addWidget(self.countdown_label)

        # 操作提示
        self.action_label = QLabel()
        self.action_label.setWordWrap(True)
        self.action_label.setStyleSheet("font-size: 11px; color: #888;")
        layout.addWidget(self.action_label)

        layout.addStretch()

        # OK 按钮（初始禁用）
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
        self.ok_btn.clicked.connect(self.accept)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(self.ok_btn)
        layout.addLayout(btn_layout)

    def retranslate_ui(self):
        self.setWindowTitle(self.i18n.tr("project_creating_title"))
        self.title_label.setText(self.i18n.tr("project_creating_title"))
        self.info_label.setText(
            self.i18n.tr("creation_progress_info").format(project=self.project_name)
        )
        self.action_label.setText(self.i18n.tr("creation_progress_action"))
        self.ok_btn.setText(self.i18n.tr("about_btn_close"))

    def _update_countdown(self):
        self.remaining -= 1
        if self.remaining <= 0:
            self.timer.stop()
            self.countdown_label.setText(self.i18n.tr("creation_progress_done"))
            self.ok_btn.setEnabled(True)
            # 更新操作提示
            self.action_label.setText(self.i18n.tr("creation_progress_action_done"))
        else:
            self.countdown_label.setText(f"{self.remaining} 秒")

    def closeEvent(self, event: QCloseEvent):
        # 禁止通过关闭按钮关闭
        if self.ok_btn.isEnabled():
            event.accept()
        else:
            event.ignore()
# -*- coding: utf-8 -*-
"""
关于对话框
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPixmap

from utils.i18n import I18n
from models.config import (
    APP_NAME, APP_ABBR, APP_VERSION,
    APP_COPYRIGHT, APP_LICENSE,
    APP_REPO_URL, APP_ISSUE_URL
)


class AboutDialog(QDialog):
    """关于对话框，显示软件信息和版本"""

    def __init__(self, i18n: I18n, parent=None):
        super().__init__(parent)
        self.i18n = i18n

        self._setup_ui()
        self.retranslate_ui()

    def _setup_ui(self):
        self.setModal(True)
        self.setFixedWidth(420)
        self.setFixedHeight(320)

        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # 标题（软件名称）
        self.title_label = QLabel()
        self.title_label.setAlignment(Qt.AlignCenter)
        font = self.title_label.font()
        font.setPointSize(18)
        font.setBold(True)
        self.title_label.setFont(font)
        layout.addWidget(self.title_label)

        # 版本
        self.version_label = QLabel()
        self.version_label.setAlignment(Qt.AlignCenter)
        font = self.version_label.font()
        font.setPointSize(10)
        self.version_label.setFont(font)
        layout.addWidget(self.version_label)

        # 分隔线
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line)

        # 描述
        self.desc_label = QLabel()
        self.desc_label.setAlignment(Qt.AlignCenter)
        self.desc_label.setWordWrap(True)
        self.desc_label.setStyleSheet("color: #444; font-size: 10px;")
        layout.addWidget(self.desc_label)

        # 分隔线
        line2 = QFrame()
        line2.setFrameShape(QFrame.HLine)
        line2.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line2)

        # 版权信息
        self.copyright_label = QLabel()
        self.copyright_label.setAlignment(Qt.AlignCenter)
        self.copyright_label.setStyleSheet("color: #888; font-size: 9px;")
        layout.addWidget(self.copyright_label)

        # 许可证
        self.license_label = QLabel()
        self.license_label.setAlignment(Qt.AlignCenter)
        self.license_label.setStyleSheet("color: #888; font-size: 9px;")
        layout.addWidget(self.license_label)

        # 仓库链接
        self.repo_label = QLabel()
        self.repo_label.setAlignment(Qt.AlignCenter)
        self.repo_label.setStyleSheet("color: #2b7a62; font-size: 9px;")
        self.repo_label.setOpenExternalLinks(True)
        layout.addWidget(self.repo_label)

        # 反馈
        self.feedback_label = QLabel()
        self.feedback_label.setAlignment(Qt.AlignCenter)
        self.feedback_label.setStyleSheet("color: #888; font-size: 9px;")
        layout.addWidget(self.feedback_label)

        layout.addStretch()

        # 关闭按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.close_btn = QPushButton()
        self.close_btn.setFixedWidth(100)
        self.close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(self.close_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

    def retranslate_ui(self):
        """刷新界面文字"""
        i18n = self.i18n

        self.setWindowTitle(i18n.tr("about_title"))
        self.title_label.setText(f"{APP_NAME} ({APP_ABBR})")
        self.version_label.setText(i18n.tr("about_version").format(version=APP_VERSION))
        self.desc_label.setText(i18n.tr("about_description"))
        self.copyright_label.setText(APP_COPYRIGHT)
        self.license_label.setText(i18n.tr("about_license").format(license=APP_LICENSE))
        self.repo_label.setText(f'<a href="{APP_REPO_URL}">{i18n.tr("about_repository")} {APP_REPO_URL}</a>')
        self.feedback_label.setText(f'{i18n.tr("about_feedback")} {i18n.tr("about_feedback_hint")}')
        self.close_btn.setText(i18n.tr("about_btn_close"))
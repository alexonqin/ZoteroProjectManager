# -*- coding: utf-8 -*-
"""
项目语言设置对话框
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QRadioButton, QButtonGroup, QFrame, QMessageBox
)
from PySide6.QtCore import Qt

from utils.i18n import I18n
from utils.language_utils import write_language, get_display_language


class LanguageDialog(QDialog):
    def __init__(self, i18n: I18n, project_name: str, profile_dir: str, current_lang: str, parent=None):
        super().__init__(parent)
        self.i18n = i18n
        self.project_name = project_name
        self.profile_dir = profile_dir
        self.current_lang = current_lang
        self.selected_lang = current_lang

        self._setup_ui()
        self.retranslate_ui()
        self._load_current()

    def _setup_ui(self):
        self.setModal(True)
        self.setFixedWidth(400)
        self.setFixedHeight(280)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        self.title_label = QLabel()
        self.title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(self.title_label)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line)

        self.current_label = QLabel()
        self.current_label.setStyleSheet("font-size: 12px;")
        layout.addWidget(self.current_label)

        self.group_box = QLabel()
        self.group_box.setStyleSheet("font-size: 12px; font-weight: bold; margin-top: 8px;")
        layout.addWidget(self.group_box)

        # 语言选项
        self.lang_group = QButtonGroup(self)
        self.radio_zh = QRadioButton()
        self.radio_en = QRadioButton()
        self.radio_system = QRadioButton()

        self.lang_group.addButton(self.radio_zh, 0)
        self.lang_group.addButton(self.radio_en, 1)
        self.lang_group.addButton(self.radio_system, 2)

        layout.addWidget(self.radio_zh)
        layout.addWidget(self.radio_en)
        layout.addWidget(self.radio_system)

        self.hint_label = QLabel()
        self.hint_label.setWordWrap(True)
        self.hint_label.setStyleSheet("color: #888; font-size: 10px; padding: 6px; background-color: #f5f5f5; border-radius: 3px;")
        layout.addWidget(self.hint_label)

        layout.addStretch()

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.cancel_btn = QPushButton()
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.cancel_btn)
        self.apply_btn = QPushButton()
        self.apply_btn.setStyleSheet("""
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
        self.apply_btn.clicked.connect(self._on_apply)
        btn_layout.addWidget(self.apply_btn)
        layout.addLayout(btn_layout)

    def retranslate_ui(self):
        self.setWindowTitle(self.i18n.tr('language_dialog_title').format(project=self.project_name))
        self.title_label.setText(self.i18n.tr('language_dialog_title').format(project=self.project_name))
        self.current_label.setText(self.i18n.tr('language_dialog_current') + ' ' + self._display_current())
        self.group_box.setText(self.i18n.tr('language_dialog_select'))
        self.radio_zh.setText(self.i18n.tr('lang_chinese'))
        self.radio_en.setText(self.i18n.tr('lang_english'))
        self.radio_system.setText(self.i18n.tr('lang_system'))
        self.hint_label.setText('💡 ' + self.i18n.tr('language_dialog_hint'))
        self.apply_btn.setText(self.i18n.tr('language_dialog_btn_apply'))
        self.cancel_btn.setText(self.i18n.tr('language_dialog_btn_cancel'))

    def _display_current(self):
        ui_lang = self.i18n.get_language()
        return get_display_language(self.current_lang, ui_lang)

    def _load_current(self):
        if self.current_lang == 'zh-CN':
            self.radio_zh.setChecked(True)
        elif self.current_lang == 'en-US':
            self.radio_en.setChecked(True)
        else:
            self.radio_system.setChecked(True)

    def _on_apply(self):
        selected = self.lang_group.checkedId()
        if selected == 0:
            new_lang = 'zh-CN'
        elif selected == 1:
            new_lang = 'en-US'
        else:
            new_lang = ''

        if new_lang == self.current_lang:
            self.accept()
            return

        if write_language(self.profile_dir, new_lang):
            self.selected_lang = new_lang
            QMessageBox.information(self, '', self.i18n.tr('language_dialog_success'))
            self.accept()
        else:
            QMessageBox.warning(self, '', self.i18n.tr('language_dialog_failed'))

    def get_selected_language(self) -> str:
        return self.selected_lang
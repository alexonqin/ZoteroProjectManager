# -*- coding: utf-8 -*-
"""
Zotero Project Launcher (ZPL) - 程序入口
"""

import sys
import os
import traceback
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import Qt

from utils.i18n import I18n
from utils.config_manager import ConfigManager
from views.main_window import MainWindow


def setup_exception_hook():
    """设置全局异常钩子"""
    def hook(exc_type, exc_value, exc_tb):
        msg = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
        print("未捕获的异常:\n" + msg)
        QMessageBox.critical(
            None,
            "程序错误",
            "发生了一个未预期的错误:\n\n{}\n\n请将错误信息反馈给开发者。".format(str(exc_value))
        )
    sys.excepthook = hook


def main():
    """程序主入口"""
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    app.setApplicationName("Zotero Project Launcher")
    app.setOrganizationName("ZPL")
    app.setApplicationVersion("1.0.0")

    setup_exception_hook()

    i18n = I18n()
    config_mgr = ConfigManager()

    lang = config_mgr.get_language()
    i18n.set_language(lang)

    window = MainWindow(i18n, config_mgr)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
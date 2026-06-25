# -*- coding: utf-8 -*-
"""
表格右键菜单构建器
"""

from PySide6.QtWidgets import QMenu, QStyle
from PySide6.QtGui import QAction

from utils.i18n import I18n
from models.profile import Profile


class TableContextMenu:
    """构建项目表格的右键菜单"""

    @staticmethod
    def create_menu(profile: Profile, i18n: I18n, parent):
        menu = QMenu(parent)

        # 启动
        launch_action = menu.addAction(i18n.tr("menu_launch"))
        launch_action.setData(profile)
        launch_action.triggered.connect(lambda: parent.launch_requested.emit(profile))

        # 打开文件夹
        open_action = menu.addAction(i18n.tr("menu_open_data_folder"))
        open_action.setData(profile)
        open_action.triggered.connect(lambda: parent.open_folder_requested.emit(profile))

        menu.addSeparator()

        # 重命名
        rename_action = menu.addAction(i18n.tr("menu_rename"))
        rename_action.setShortcut("F2")
        rename_action.setData(profile)
        rename_action.triggered.connect(lambda: parent.rename_requested.emit(profile))

        # 导出
        export_action = menu.addAction(i18n.tr("menu_export_project"))
        export_action.setData(profile)
        export_action.triggered.connect(lambda: parent.export_requested.emit(profile))

        # 语言子菜单
        lang_menu = menu.addMenu(i18n.tr("menu_language"))
        lang_zh = lang_menu.addAction(i18n.tr("lang_chinese"))
        lang_zh.triggered.connect(lambda: parent.change_language_requested.emit(profile))
        lang_en = lang_menu.addAction(i18n.tr("lang_english"))
        lang_en.triggered.connect(lambda: parent.change_language_requested.emit(profile))
        lang_sys = lang_menu.addAction(i18n.tr("lang_system"))
        lang_sys.triggered.connect(lambda: parent.change_language_requested.emit(profile))

        menu.addSeparator()

        # 删除
        delete_action = menu.addAction(i18n.tr("menu_delete_project"))
        delete_action.setIcon(parent.style().standardIcon(QStyle.SP_DialogCancelButton))
        delete_action.setData(profile)
        delete_action.triggered.connect(lambda: parent.delete_requested.emit(profile))

        return menu
# -*- coding: utf-8 -*-
"""
语言事件处理器
"""

from pathlib import Path

from PySide6.QtWidgets import QDialog, QMessageBox


from controllers import ZoteroController
from utils.i18n import I18n
from utils.config_manager import ConfigManager
from views.components.table_widget import TableWidget
from views.dialogs import LanguageDialog


class LanguageHandler:
    """语言管理事件处理器"""
    
    def __init__(
        self,
        controller: ZoteroController,
        config_mgr: ConfigManager,
        i18n: I18n,
        table_widget: TableWidget,
        parent_window
    ):
        self.controller = controller
        self.config_mgr = config_mgr
        self.i18n = i18n
        self.table = table_widget
        self.parent = parent_window
        self.config = config_mgr.get_config()
    
    def on_switch_language(self):
        """切换 ZPL 界面语言"""
        current = self.i18n.get_language()
        new_lang = "en_US" if current == "zh_CN" else "zh_CN"
        self.i18n.set_language(new_lang)
        self.config_mgr.set_language(new_lang)
        
        # 通知父窗口刷新所有 UI
        if hasattr(self.parent, 'retranslate_ui'):
            self.parent.retranslate_ui()
        
        # 刷新表格
        self.on_refresh_table()
    
    def on_change_project_language(self, profile):
        """修改项目语言（弹出对话框）"""
        current_lang = self.controller.get_project_language(profile.project_path)
        profiles_dir = Path(profile.project_path) / "profiles"
        
        dialog = LanguageDialog(
            self.i18n,
            profile.name,
            str(profiles_dir),
            current_lang or '',
            self.parent
        )
        if dialog.exec_() == QDialog.Accepted:
            # 语言修改成功后，刷新项目列表以更新语言列显示
            self.parent.project_handler.on_refresh()
    
    def on_set_project_language(self, profile, lang_code: str):
        """直接设置项目语言（右键菜单调用）"""
        success = self.controller.set_project_language(profile.project_path, lang_code)
        if success:
            # 刷新项目列表以更新语言列显示
            self.parent.project_handler.on_refresh()
            QMessageBox.information(self.parent, "", self.i18n.tr("language_dialog_success"))
        else:
            QMessageBox.warning(self.parent, "", self.i18n.tr("language_dialog_failed"))
    
    def on_refresh_table(self):
        """刷新表格数据（兼容旧调用）"""
        if hasattr(self.parent, 'project_handler'):
            self.parent.project_handler.on_refresh()
        elif hasattr(self.parent, '_refresh_projects'):
            self.parent._refresh_projects()
        elif hasattr(self, '_refresh_callback'):
            self._refresh_callback()
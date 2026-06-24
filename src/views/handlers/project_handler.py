# -*- coding: utf-8 -*-
"""
项目事件处理器
"""

import os
from pathlib import Path

from PySide6.QtWidgets import QMessageBox, QDialog

from models.profile import Profile
from controllers.zotero_controller import ZoteroController
from utils.i18n import I18n
from utils.config_manager import ConfigManager
from views.components.table_widget import TableWidget
from views.dialogs import (
    NewProjectDialog,
    DeleteConfirmDialog,
    ProjectInUseDialog,
    DeleteSuccessDialog,
    DeleteFailedDialog
)


class ProjectHandler:
    """项目操作事件处理器"""
    
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
    
    def on_new_project(self):
        """新建项目"""
        dialog = NewProjectDialog(self.i18n, self.config, self.parent)
        if dialog.exec_() == QDialog.Accepted and dialog.result_data:
            name, location, language, create_shortcut = dialog.result_data
            success, msg, project_path = self.controller.create_project(
                project_name=name,
                profiles_dir=location,
                templates_root=self.config.templates_root,
                zotero_version=self.config.zotero_version,
                zotero_install_dir=self.config.zotero_install_dir,
                language=language,
                create_shortcut=create_shortcut,
                creation_method=self.config.creation_method
            )
            if success:
                QMessageBox.information(self.parent, "", f"✅ 项目 '{name}' 创建成功！")
                # 更新目录
                self.config_mgr.set_profiles_current(location)
                self.config_mgr.add_to_history(location)
                # 刷新表格
                self.on_refresh()
            else:
                QMessageBox.critical(self.parent, "", msg)
    
    def on_refresh(self):
        """刷新项目列表"""
        current_dir = self.config_mgr.get_profiles_current()
        if not current_dir:
            return
        
        profiles = self.controller.get_projects(current_dir)
        ui_lang = self.i18n.get_language()
        self.table.refresh_data(profiles, ui_lang)
        
        # 更新状态栏
        self._update_status_bar(profiles)
    
    def on_launch_project(self, profile: Profile):
        """启动项目"""
        if not self.config.zotero_install_dir:
            QMessageBox.warning(self.parent, "", "请设置 Zotero 安装路径")
            return
        if self.controller.launch_project(profile.project_path, profile.name, self.config.zotero_install_dir):
            pass
        else:
            QMessageBox.warning(self.parent, "", "启动失败")
    
    def on_delete_project(self, profile: Profile):
        """删除项目（完整流程）"""
        # 1. 检测是否正在使用
        if self.controller.is_project_in_use(profile.project_path):
            dialog = ProjectInUseDialog(self.i18n, profile.name, profile.project_path, self.parent)
            if dialog.exec_() == QDialog.Accepted:
                self.on_delete_project(profile)
            return
        
        # 2. 确认对话框
        size_mb = profile.get_size() / (1024 * 1024)
        confirm_dialog = DeleteConfirmDialog(self.i18n, profile, size_mb, self.parent)
        if confirm_dialog.exec_() != QDialog.Accepted:
            return
        
        # 3. 执行删除
        current_dir = self.config_mgr.get_profiles_current()
        success, msg = self.controller.delete_project(
            profile.project_path,
            profile.name,
            current_dir
        )
        
        if success:
            # 清理备注
            self.config_mgr.remove_project_note(profile.name)
            # 成功对话框
            success_dialog = DeleteSuccessDialog(
                self.i18n, profile.name, profile.project_path, size_mb, self.parent
            )
            success_dialog.exec_()
            self.on_refresh()
        else:
            # 失败对话框
            failed_dialog = DeleteFailedDialog(self.i18n, profile.name, msg, self.parent)
            if failed_dialog.exec_() == QDialog.Accepted:
                self.on_delete_project(profile)
    
    def on_open_folder(self, profile: Profile):
        """打开项目文件夹"""
        path = profile.project_path
        if not os.path.exists(path):
            QMessageBox.warning(self.parent, "", "文件夹不存在")
            return
        try:
            os.startfile(path)
        except Exception as e:
            QMessageBox.warning(self.parent, "", f"打开失败: {e}")
    
    def on_create_shortcut(self, profile: Profile):
        """创建桌面快捷方式"""
        if not self.config.zotero_install_dir:
            QMessageBox.warning(self.parent, "", "请设置 Zotero 安装路径")
            return
        success, msg = self.controller.create_shortcut(
            profile.project_path,
            profile.name,
            self.config.zotero_install_dir
        )
        if success:
            QMessageBox.information(self.parent, "", "✅ 快捷方式已创建")
        else:
            QMessageBox.warning(self.parent, "", f"创建失败: {msg}")
    
    def on_directory_changed(self, path: str):
        """目录切换"""
        self.config_mgr.set_profiles_current(path)
        self.config_mgr.add_to_history(path)
        self.on_refresh()
    
    def _update_status_bar(self, profiles):
        """更新状态栏（由主窗口提供 status_bar 引用）"""
        # 这个方法由 main_window 在初始化时注册回调
        if hasattr(self.parent, 'status_bar_widget'):
            count = len(profiles)
            version = self.config.zotero_version
            self.parent.status_bar_widget.update_info(count, version)
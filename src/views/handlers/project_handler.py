# -*- coding: utf-8 -*-
"""
项目事件处理器
"""

import os
import shutil
import zipfile
from pathlib import Path
from datetime import datetime

from PySide6.QtWidgets import QMessageBox, QDialog, QProgressDialog
from PySide6.QtCore import Qt

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
from utils.profile_registry import register_profile


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
    
    # ---------- 核心项目操作 ----------
    def on_new_project(self):
        dialog = NewProjectDialog(self.i18n, self.config, self.parent)
        if dialog.exec_() == QDialog.Accepted and dialog.result_data:
            name, location, language = dialog.result_data
            success, msg, project_path = self.controller.create_project(
                project_name=name,
                profiles_dir=location,
                templates_root=self.config.templates_root,
                zotero_version=self.config.zotero_version,
                zotero_install_dir=self.config.zotero_install_dir,
                language=language,
                creation_method=self.config.creation_method,
                profile_mode=self.config.creation_profile_mode
            )
            if success:
                QMessageBox.information(self.parent, "", f"✅ 项目 '{name}' 创建成功！")
                self.config_mgr.set_profiles_current(location)
                self.config_mgr.add_to_history(location)
                self.on_refresh()
            else:
                QMessageBox.critical(self.parent, "", msg)
    
    def on_refresh(self):
        current_dir = self.config_mgr.get_profiles_current()
        if not current_dir:
            return
        
        profiles = self.controller.get_projects(current_dir)
        ui_lang = self.i18n.get_language()
        self.table.refresh_data(profiles, ui_lang)
        self._update_status_bar(profiles)
    
    def on_launch_project(self, profile):
        """
        启动项目（含防御性检查）
        """
        if not isinstance(profile, Profile):
            print(f"[ERROR] on_launch_project called with invalid profile: {profile} (type: {type(profile)})")
            QMessageBox.warning(self.parent, "错误", "无法启动项目：所选项目无效，请重新选择。")
            return
        
        if not self.config.zotero_install_dir:
            QMessageBox.warning(self.parent, "", "请设置 Zotero 安装路径")
            return
        
        if self.controller.launch_project(profile.project_path, profile.name, self.config.zotero_install_dir):
            pass
        else:
            QMessageBox.warning(self.parent, "", "启动失败")
    
    def on_delete_project(self, profile: Profile):
        if self.controller.is_project_in_use(profile.project_path):
            dialog = ProjectInUseDialog(self.i18n, profile.name, profile.project_path, self.parent)
            if dialog.exec_() == QDialog.Accepted:
                self.on_delete_project(profile)
            return
        
        size_mb = profile.get_size() / (1024 * 1024)
        confirm_dialog = DeleteConfirmDialog(self.i18n, profile, size_mb, self.parent)
        if confirm_dialog.exec_() != QDialog.Accepted:
            return
        
        current_dir = self.config_mgr.get_profiles_current()
        success, msg = self.controller.delete_project(
            profile.project_path,
            profile.name,
            current_dir
        )
        
        if success:
            self.config_mgr.remove_project_note(profile.name)
            success_dialog = DeleteSuccessDialog(
                self.i18n, profile.name, profile.project_path, size_mb, self.parent
            )
            success_dialog.exec_()
            self.on_refresh()
        else:
            failed_dialog = DeleteFailedDialog(self.i18n, profile.name, msg, self.parent)
            if failed_dialog.exec_() == QDialog.Accepted:
                self.on_delete_project(profile)
    
    def on_open_folder(self, profile: Profile):
        path = profile.project_path
        if not os.path.exists(path):
            QMessageBox.warning(self.parent, "", "文件夹不存在")
            return
        try:
            os.startfile(path)
        except Exception as e:
            QMessageBox.warning(self.parent, "", f"打开失败: {e}")
    
    def on_directory_changed(self, path: str):
        self.config_mgr.set_profiles_current(path)
        self.config_mgr.add_to_history(path)
        self.on_refresh()
    
    def _update_status_bar(self, profiles):
        if hasattr(self.parent, 'status_bar_widget'):
            count = len(profiles)
            version = self.config.zotero_version
            self.parent.status_bar_widget.update_info(count, version)
    
    # ---------- 导入导出功能 ----------
    def on_export_project(self, profile: Profile):
        from views.dialogs.export_dialog import ExportDialog
        current_dir = self.config_mgr.get_profiles_current()
        dialog = ExportDialog(self.i18n, profile, current_dir, self.parent)
        if dialog.exec_() == QDialog.Accepted:
            zip_path = dialog.result_path
            self._do_export(profile, zip_path)
            if dialog.result_open_folder:
                os.startfile(Path(zip_path).parent)
    
    def _do_export(self, profile: Profile, zip_path: str):
        try:
            exclude_extensions = {'.lnk', '.log'}
            exclude_dirs = {'cache2', 'startupCache', 'shader-cache'}
            
            progress = QProgressDialog(
                self.i18n.tr("export_progress"),
                self.i18n.tr("pref_btn_cancel"),
                0, 0, self.parent
            )
            progress.setWindowModality(Qt.WindowModal)
            progress.show()
            
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                project_root = Path(profile.project_path)
                for file_path in project_root.rglob('*'):
                    if file_path.is_file():
                        if file_path.suffix in exclude_extensions:
                            continue
                        if any(d in file_path.parent.parts for d in exclude_dirs):
                            continue
                        arcname = file_path.relative_to(project_root.parent)
                        zf.write(file_path, arcname)
            
            progress.close()
            QMessageBox.information(
                self.parent,
                "",
                self.i18n.tr("export_success").format(path=zip_path)
            )
        except Exception as e:
            QMessageBox.critical(
                self.parent,
                "",
                self.i18n.tr("export_failed").format(error=str(e))
            )
    
    def on_import_project(self):
        from views.dialogs.import_dialog import ImportDialog
        current_dir = self.config_mgr.get_profiles_current()
        dialog = ImportDialog(self.i18n, current_dir, self.parent)
        if dialog.exec_() == QDialog.Accepted:
            zip_path = dialog.file_edit.text()
            target_path = dialog.result_path
            create_shortcut = dialog.result_create_shortcut
            self._do_import(zip_path, target_path, create_shortcut)
    
    def _do_import(self, zip_path: str, target_path: str, create_shortcut: bool):
        try:
            progress = QProgressDialog(
                self.i18n.tr("import_progress"),
                self.i18n.tr("pref_btn_cancel"),
                0, 0, self.parent
            )
            progress.setWindowModality(Qt.WindowModal)
            progress.show()
            
            target_dir = Path(target_path).parent
            target_dir.mkdir(parents=True, exist_ok=True)
            
            with zipfile.ZipFile(zip_path, 'r') as zf:
                zf.extractall(target_dir)
            
            project_name = Path(target_path).name
            profiles_subdir = Path(target_path) / "profiles"
            register_profile(project_name, str(profiles_subdir))
            
            if create_shortcut:
                self.controller.create_shortcut_in_library(
                    str(target_path),
                    project_name,
                    self.config.zotero_install_dir,
                    str(target_dir)
                )
            
            progress.close()
            QMessageBox.information(
                self.parent,
                "",
                self.i18n.tr("import_success").format(name=project_name)
            )
            self.on_refresh()
        except Exception as e:
            QMessageBox.critical(
                self.parent,
                "",
                self.i18n.tr("import_failed").format(error=str(e))
            )
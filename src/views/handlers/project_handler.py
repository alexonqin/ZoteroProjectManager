# -*- coding: utf-8 -*-
"""
项目事件处理器
"""

import os
import shutil
import zipfile
from pathlib import Path

from PySide6.QtWidgets import QMessageBox, QDialog, QProgressDialog
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

from models.profile import Profile
from controllers import ZoteroController
from utils.i18n import I18n
from utils.config_manager import ConfigManager
from views.components.table_widget import TableWidget
from views.dialogs import (
    NewProjectDialog,
    DeleteConfirmDialog,
    ProjectInUseDialog,
    DeleteSuccessDialog,
    DeleteFailedDialog,
    RenameDialog,
    ImportDialog,
    ExportDialog
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
        dialog = NewProjectDialog(self.i18n, self.config, self.controller, self.parent)
        if dialog.exec_() == QDialog.Accepted and dialog.result_data:
            name, location = dialog.result_data

            success, msg, project_path = self.controller.create_project(
                project_name=name,
                profiles_dir=location,
                zotero_install_dir=self.config.zotero_install_dir,
                create_library_shortcut=True
            )

            if success:
                from views.dialogs.creation_progress_dialog import CreationProgressDialog
                progress_dialog = CreationProgressDialog(self.i18n, name, self.parent)
                progress_dialog.exec_()

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
        if not isinstance(profile, Profile):
            QMessageBox.warning(self.parent, "错误", "无法启动项目：所选项目无效。")
            return
        if not self.config.zotero_install_dir:
            QMessageBox.warning(self.parent, "", "请设置 Zotero 安装路径")
            return

        clean_name = profile.name.strip()
        if not self.controller.launch_project(profile.project_path, clean_name, self.config.zotero_install_dir):
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
            version = ""  # 不再显示版本
            self.parent.status_bar_widget.update_info(count, version)

    # ---------- 重命名 ----------
    def on_rename_project(self, profile: Profile):
        if not isinstance(profile, Profile):
            QMessageBox.warning(self.parent, "错误", "请选择一个有效的项目。")
            return
        current_dir = self.config_mgr.get_profiles_current()
        dialog = RenameDialog(self.i18n, profile.name, current_dir, self.parent)
        if dialog.exec_() == QDialog.Accepted:
            new_name = dialog.new_name.strip()
            if new_name == profile.name:
                return
            success, msg, new_path = self.controller.rename_project(
                old_name=profile.name,
                new_name=new_name,
                profiles_dir=current_dir,
                zotero_install_dir=self.config.zotero_install_dir,
                library_dir=current_dir
            )
            if success:
                QMessageBox.information(self.parent, "", f"✅ {msg}")
                self.on_refresh()
            else:
                QMessageBox.critical(self.parent, "", f"❌ {msg}")

    # ---------- 导入导出 ----------
    def on_export_project(self, profile: Profile):
        current_dir = self.config_mgr.get_profiles_current()
        dialog = ExportDialog(self.i18n, profile, current_dir, self.parent)
        if dialog.exec_() == QDialog.Accepted:
            zip_path = dialog.result_path
            self._do_export(profile, zip_path)
            if dialog.result_open_folder:
                os.startfile(Path(zip_path).parent)

    def _do_export(self, profile: Profile, zip_path: str):
        try:
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

    # ---------- 导入（核心修复） ----------
    def on_import_project(self):
        current_dir = self.config_mgr.get_profiles_current()
        dialog = ImportDialog(self.i18n, current_dir, self.parent)
        if dialog.exec_() == QDialog.Accepted:
            zip_path = dialog.file_edit.text()
            target_path = dialog.result_path
            self._do_import(zip_path, target_path, dialog.original_project_name)

    def _do_import(self, zip_path: str, target_path: str, original_name: str = None):
        """
        执行导入，支持重命名文件夹（使用临时目录，避免覆盖现有项目）
        """
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

            # 创建临时目录
            temp_dir = target_dir / "_tmp_import"
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
            temp_dir.mkdir()

            # 解压 ZIP 到临时目录
            with zipfile.ZipFile(zip_path, 'r') as zf:
                zf.extractall(temp_dir)

            # 确定解压出的项目文件夹（通常为 original_name）
            # 如果 original_name 为 None，尝试从临时目录中查找第一个子目录
            if original_name:
                unpacked_path = temp_dir / original_name
            else:
                # 若没有 original_name，则尝试获取临时目录下的第一个子目录
                items = list(temp_dir.iterdir())
                if not items:
                    raise Exception("ZIP 包为空或结构异常")
                unpacked_path = items[0] if items[0].is_dir() else temp_dir

            if not unpacked_path.exists() or not unpacked_path.is_dir():
                raise Exception(f"解压后未找到项目文件夹: {unpacked_path}")

            final_name = Path(target_path).name
            final_path = target_dir / final_name

            # 如果最终路径已存在，说明冲突处理未生效，抛出异常
            if final_path.exists():
                raise Exception(f"目标路径已存在: {final_path}")

            # 重命名/移动项目文件夹到最终位置
            if unpacked_path.name != final_name:
                # 重命名临时目录内的文件夹
                unpacked_path.rename(final_path)
            else:
                # 直接移动（不重命名）
                unpacked_path.rename(final_path)  # 或 shutil.move

            # 清理临时目录（如果为空则删除，否则递归删除）
            try:
                temp_dir.rmdir()
            except OSError:
                shutil.rmtree(temp_dir, ignore_errors=True)

            # 注册 Profile 和生成快捷方式
            project_name = final_path.name
            profiles_subdir = final_path / "profiles"
            register_profile(project_name, str(profiles_subdir))

            self.controller.create_shortcut_in_library(
                str(final_path),
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
            # 清理临时目录
            temp_dir = target_dir / "_tmp_import"
            if temp_dir.exists():
                shutil.rmtree(temp_dir, ignore_errors=True)
            QMessageBox.critical(
                self.parent,
                "",
                self.i18n.tr("import_failed").format(error=str(e))
            )
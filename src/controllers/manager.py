# -*- coding: utf-8 -*-
"""
项目管理：获取、删除、重命名、语言设置
"""

import os
from pathlib import Path
from typing import List, Tuple, Optional

from models.profile import Profile
from utils.profile_registry import unregister_profile, update_profile_name
from utils.recycle_bin import move_to_recycle_bin
from utils.language_utils import read_language, write_language


class ManagerMixin:
    """项目管理混入（获取、删除、重命名、语言）"""

    def get_projects(self, profiles_dir: str) -> List[Profile]:
        """获取指定目录下的所有项目"""
        projects = []
        if not profiles_dir or not Path(profiles_dir).exists():
            return projects
        root = Path(profiles_dir)
        for item in root.iterdir():
            if item.is_dir():
                profile = Profile.from_project_path(str(item))
                if profile and profile.is_valid():
                    projects.append(profile)
        return projects

    def delete_project(self, project_path: str, project_name: str, library_dir: str = None) -> Tuple[bool, str]:
        """删除项目（移至回收站）"""
        try:
            unregister_profile(project_name)
            self.delete_shortcuts(project_name, library_dir)
            success, err = move_to_recycle_bin(project_path)
            if not success:
                return False, err
            return True, "已移至回收站"
        except Exception as e:
            return False, str(e)


    def rename_project(
        self,
        old_name: str,
        new_name: str,
        profiles_dir: str,
        zotero_install_dir: str,
        library_dir: str = None
    ) -> Tuple[bool, str, Optional[str]]:
        """
        重命名项目（原子操作）
        返回: (成功, 消息, 新路径)
        """
        old_path = Path(profiles_dir) / old_name
        new_path = Path(profiles_dir) / new_name

        # 1. 验证
        if not old_path.exists():
            return False, f"项目 '{old_name}' 不存在", None
        if new_path.exists():
            return False, f"项目 '{new_name}' 已存在", None

        # 2. 检测使用中
        if self.is_project_in_use(str(old_path)):
            return False, f"项目 '{old_name}' 正在被Zotero使用，无法重命名", None

        # 3. 物理重命名
        try:
            old_path.rename(new_path)
        except Exception as e:
            return False, f"文件夹重命名失败: {e}", None

        # 4. 更新 profiles.ini（修正：Path 应指向 profiles 子目录）
        try:
            profiles_path = new_path / "profiles"
            success = update_profile_name(old_name, new_name, str(profiles_path))
            if not success:
                # 回滚
                new_path.rename(old_path)
                return False, "更新profile注册信息失败，已回滚", None
        except Exception as e:
            # 回滚
            try:
                new_path.rename(old_path)
            except:
                pass
            return False, f"更新profile注册信息异常: {e}，已回滚", None

        # 5. 更新快捷方式
        shortcut_updated = 0
        if library_dir:
            shortcut_updated = self.update_shortcuts_for_rename(
                old_name, new_name,
                str(old_path), str(new_path),
                library_dir, zotero_install_dir
            )

        # 6. 更新备注
        try:
            if hasattr(self, 'config_mgr') and self.config_mgr:
                self.config_mgr.rename_project_note(old_name, new_name)
        except Exception as e:
            print(f"[WARN] 更新项目备注失败: {e}")

        # 7. 不再主动写入语言（保持项目原有配置不变）

        return True, f"项目已成功重命名为 '{new_name}'（更新了 {shortcut_updated} 个快捷方式）", str(new_path)


    # ---------- 语言 ----------
    def get_project_language(self, project_path: str) -> str:
        """
        获取项目语言设置
        
        Args:
            project_path: 项目根目录路径
            
        Returns:
            语言代码 (如 'zh-CN', 'en-US')，如果未设置或读取失败则返回 None
        """
        profiles_dir = Path(project_path) / "profiles"
        if not profiles_dir.exists():
            return None
        return read_language(str(profiles_dir))

    def set_project_language(self, project_path: str, lang_code: str) -> bool:
        """
        设置项目语言
        
        Args:
            project_path: 项目根目录路径
            lang_code: 语言代码 (如 'zh-CN', 'en-US', '' 表示跟随系统)
            
        Returns:
            True 表示设置成功，False 表示失败
        """
        profiles_dir = Path(project_path) / "profiles"
        if not profiles_dir.exists():
            return False
        return write_language(str(profiles_dir), lang_code)
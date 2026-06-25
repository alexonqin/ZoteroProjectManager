# -*- coding: utf-8 -*-
"""
项目创建模块 - 仅完整模式（语言跟随系统）
"""

import os
import shutil
import subprocess
import time
from pathlib import Path
from typing import Optional, Tuple

from utils.profile_registry import register_profile, set_default_profile


class CreatorMixin:
    """项目创建混入类（仅完整模式）"""

    def _ensure_profile_structure(self, project_path: str, precreate_prefs: bool = False) -> bool:
        """
        确保 profiles 目录存在，但不写入 prefs.js（完整模式）
        precreate_prefs 参数保留但忽略，始终不创建 prefs.js
        """
        project_dir = Path(project_path)
        profiles_dir = project_dir / "profiles"
        try:
            profiles_dir.mkdir(parents=True, exist_ok=True)
            (profiles_dir / "extensions").mkdir(exist_ok=True)
        except Exception as e:
            print(f"[ERROR] 创建 profiles 目录失败: {e}")
            return False

        # 完整模式：不预先创建 prefs.js，让 Zotero 自动生成
        prefs_path = profiles_dir / "prefs.js"
        if prefs_path.exists():
            try:
                prefs_path.unlink()
            except:
                pass
        return True

    def _create_project_full(
        self,
        project_name: str,
        profiles_dir: str,
        zotero_install_dir: str,
        create_library_shortcut: bool
    ) -> Tuple[bool, str, Optional[str]]:
        """
        完整模式创建（55MB）
        使用空 profiles 目录，让 Zotero 自动生成完整配置。
        语言固定为跟随系统（不写入 prefs.js）
        """
        print("[DEBUG] 创建模式: **完整模式 (Full)** - 约 55MB")
        name = project_name.strip()
        project_path = Path(profiles_dir) / name

        # 1. 创建空目录
        try:
            project_path.mkdir(parents=True, exist_ok=True)
            (project_path / "data").mkdir(exist_ok=True)
            profiles_path = project_path / "profiles"
            profiles_path.mkdir(exist_ok=True)
            # 确保 profiles 目录为空（删除可能残留的文件）
            for item in profiles_path.iterdir():
                if item.is_file():
                    item.unlink()
                elif item.is_dir():
                    shutil.rmtree(item)
            print(f"[DEBUG] 已清空 profiles 目录: {profiles_path}")
        except Exception as e:
            return False, f"创建项目目录失败: {e}", None

        profiles_dir_path = project_path / "profiles"
        data_dir_path = project_path / "data"

        # 2. 注册 Profile（指向空 profiles 目录）
        if not register_profile(name, str(profiles_dir_path)):
            return False, "注册 Profile 失败", None
        set_default_profile(name)
        print(f"[DEBUG] Profile '{name}' 已注册并设为默认")

        # 3. 启动 Zotero
        exe_path = Path(zotero_install_dir) / "zotero.exe"
        if not exe_path.exists():
            return False, "Zotero 安装路径无效"

        print("[DEBUG] 启动 Zotero 进行完整初始化（后台运行）...")
        try:
            proc = subprocess.Popen([
                str(exe_path),
                "-datadir", str(data_dir_path),
                "-P", name
            ], shell=False)
        except Exception as e:
            return False, f"启动 Zotero 失败: {e}", None

        # 4. 生成快捷方式
        if create_library_shortcut:
            self.create_shortcut_in_library(str(project_path), name, zotero_install_dir, profiles_dir)

        # 直接返回成功，不等待初始化完成
        return True, f"项目 '{name}' 已创建，正在初始化，请不要关闭 Zotero 窗口！", str(project_path)

    def create_project(
        self,
        project_name: str,
        profiles_dir: str,
        zotero_install_dir: str,
        create_library_shortcut: bool = True,
        # 以下参数保留为兼容旧调用，但实际不使用
        templates_root: Optional[str] = None,
        zotero_version: Optional[str] = None,
        language: str = '',
        create_shortcut: bool = False,
        creation_method: Optional[str] = None,
        profile_mode: Optional[str] = None
    ) -> Tuple[bool, str, Optional[str]]:
        """
        统一创建入口（固定完整模式，语言跟随系统）
        忽略传入的 creation_method、profile_mode、language 等参数
        """
        if not project_name or not project_name.strip():
            return False, "项目名称不能为空", None
        name = project_name.strip()
        illegal = r'<>:"/\|?*'
        for ch in illegal:
            if ch in name:
                return False, f"非法字符: {ch}", None
        if not Path(profiles_dir).exists():
            return False, "Profiles 目录不存在", None

        # 忽略其他参数，直接调用完整模式
        return self._create_project_full(
            name,
            profiles_dir,
            zotero_install_dir,
            create_library_shortcut
        )
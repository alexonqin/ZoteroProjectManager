# -*- coding: utf-8 -*-
"""
项目创建模块 - 三种创建方式
"""

import os
import shutil
import subprocess
import time
from pathlib import Path
from typing import Optional, Tuple

from utils.profile_registry import register_profile, set_default_profile
from utils.language_utils import write_language, read_language


class CreatorMixin:
    """项目创建混入类"""

    def _ensure_profile_structure(self, project_path: str, language: str,
                                   precreate_prefs: bool = True) -> bool:
        """确保profiles目录结构和prefs.js"""
        project_dir = Path(project_path)
        profiles_dir = project_dir / "profiles"
        try:
            profiles_dir.mkdir(parents=True, exist_ok=True)
            (profiles_dir / "extensions").mkdir(exist_ok=True)
        except Exception as e:
            print(f"[ERROR] 创建profiles目录失败: {e}")
            return False

        if not precreate_prefs:
            prefs_path = profiles_dir / "prefs.js"
            if prefs_path.exists():
                try:
                    prefs_path.unlink()
                except:
                    pass
            return True

        if language is None:
            language = 'zh-CN'
        prefs_content = f'''// Mozilla User Preferences
user_pref("intl.locale.matchOS", false);
user_pref("intl.locale.requested", "{language}");
'''
        prefs_path = profiles_dir / "prefs.js"
        try:
            prefs_path.write_text(prefs_content, encoding='utf-8')
            verify_lang = read_language(str(profiles_dir))
            return verify_lang == language
        except Exception as e:
            print(f"[ERROR] 写入prefs.js失败: {e}")
            return False

    def _close_zotero(self, process):
        """终止Zotero进程"""
        try:
            process.terminate()
            time.sleep(1)
            if process.poll() is None:
                process.kill()
        except Exception as e:
            print(f"[ERROR] 关闭Zotero失败: {e}")

    def _create_project_full(
        self,
        project_name: str,
        profiles_dir: str,
        zotero_install_dir: str,
        create_library_shortcut: bool
    ) -> Tuple[bool, str, Optional[str]]:
        """完整模式创建（55MB），启动Zotero后立即返回，不等待初始化"""
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

        # 3. 启动 Zotero（后台运行，不等待）
        exe_path = Path(zotero_install_dir) / "zotero.exe"
        if not exe_path.exists():
            return False, "Zotero 安装路径无效", None

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
        return True, f"项目 '{name}' 已创建，Zotero 正在后台初始化（首次启动可能需要联网下载文件），请稍后启动。", str(project_path)

    def _create_project_light(
        self,
        project_name: str,
        profiles_dir: str,
        language: str,
        zotero_install_dir: str,
        create_library_shortcut: bool
    ) -> Tuple[bool, str, Optional[str]]:
        """轻量模式创建（19MB），启动Zotero后立即返回"""
        print("[DEBUG] 创建模式: **轻量模式 (Light)** - 约 19MB")
        name = project_name.strip()
        project_path = Path(profiles_dir) / name
        try:
            project_path.mkdir(parents=True, exist_ok=True)
            (project_path / "data").mkdir(exist_ok=True)
            (project_path / "profiles").mkdir(exist_ok=True)
        except Exception as e:
            return False, f"创建项目目录失败: {e}", None

        if not self._ensure_profile_structure(str(project_path), language, precreate_prefs=True):
            return False, "写入语言设置失败", None

        profiles_dir_path = project_path / "profiles"
        if not register_profile(name, str(profiles_dir_path)):
            return False, "注册Profile失败", None
        set_default_profile(name)

        exe_path = Path(zotero_install_dir) / "zotero.exe"
        if not exe_path.exists():
            return False, "Zotero安装路径无效", None
        try:
            proc = subprocess.Popen([
                str(exe_path),
                "-datadir", str(project_path / "data"),
                "-P", name
            ], shell=False)
        except Exception as e:
            return False, f"启动Zotero失败: {e}", None

        if create_library_shortcut:
            self.create_shortcut_in_library(str(project_path), name, zotero_install_dir, profiles_dir)

        return True, f"项目 '{name}' 已创建，Zotero 正在后台初始化（首次启动可能需要联网下载文件），请稍后启动。", str(project_path)

    def _create_project_from_template(
        self,
        project_name: str,
        profiles_dir: str,
        template_dir: str,
        language: str,
        zotero_install_dir: str,
        create_library_shortcut: bool
    ) -> Tuple[bool, str, Optional[str]]:
        """模板复制创建（不需要启动Zotero）"""
        print(f"[DEBUG] 创建模式: **模板复制 (Template)** - 使用模板: {template_dir}")
        name = project_name.strip()
        project_path = Path(profiles_dir) / name
        try:
            shutil.copytree(template_dir, project_path)
        except Exception as e:
            return False, f"复制模板失败: {e}", None

        if not self._ensure_profile_structure(str(project_path), language, precreate_prefs=True):
            return False, "创建项目配置结构失败", None

        profiles_subdir = project_path / "profiles"
        register_profile(name, str(profiles_subdir))

        if create_library_shortcut:
            self.create_shortcut_in_library(str(project_path), name, zotero_install_dir, profiles_dir)

        return True, f"项目 '{name}' 创建成功（模板复制）", str(project_path)

    def _match_template(self, templates_root: str, zotero_version: str) -> Optional[str]:
        """匹配模板目录"""
        if not templates_root or not Path(templates_root).exists():
            return None
        root = Path(templates_root)
        subdirs = [d for d in root.iterdir() if d.is_dir()]
        if not subdirs:
            return None
        for d in subdirs:
            if d.name == f"v{zotero_version}":
                return str(d)
        main_version = zotero_version.split('.')[0] if '.' in zotero_version else zotero_version
        for d in subdirs:
            if d.name.startswith(f"v{main_version}."):
                return str(d)
        return None

    def get_templates(self, templates_root: str) -> list:
        """获取模板列表"""
        if not templates_root or not Path(templates_root).exists():
            return []
        root = Path(templates_root)
        return [d.name for d in root.iterdir() if d.is_dir()]

    def create_project(
        self,
        project_name: str,
        profiles_dir: str,
        templates_root: str,
        zotero_version: str,
        zotero_install_dir: str,
        language: str = 'zh-CN',
        create_shortcut: bool = False,
        create_library_shortcut: bool = True,
        creation_method: Optional[str] = None,
        profile_mode: Optional[str] = None
    ) -> Tuple[bool, str, Optional[str]]:
        """统一创建入口"""
        if not project_name or not project_name.strip():
            return False, "项目名称不能为空", None
        name = project_name.strip()
        illegal = r'<>:"/\|?*'
        for ch in illegal:
            if ch in name:
                return False, f"非法字符: {ch}", None
        if not Path(profiles_dir).exists():
            return False, "Profiles目录不存在", None

        if creation_method is None and hasattr(self, 'config_mgr') and self.config_mgr:
            creation_method = self.config_mgr.get_creation_method()
        else:
            creation_method = "auto"

        if profile_mode is None and hasattr(self, 'config_mgr') and self.config_mgr:
            profile_mode = self.config_mgr.get_config().creation_profile_mode
        else:
            profile_mode = "full"

        # 模板模式
        if creation_method == "template":
            if not templates_root or not Path(templates_root).exists():
                return False, "模板目录不存在", None
            if not zotero_version:
                return False, "Zotero版本号未设置", None
            template_dir = self._match_template(templates_root, zotero_version)
            if not template_dir:
                return False, f"未找到匹配Zotero {zotero_version}的模板", None
            success, msg, project_path = self._create_project_from_template(
                name, profiles_dir, template_dir, language,
                zotero_install_dir, create_library_shortcut
            )
            if success:
                print(f"[DEBUG] 项目创建完成，最终模式: template/{profile_mode}, 项目路径: {project_path}")
            return success, msg, project_path

        elif creation_method == "native":
            if profile_mode == "full":
                success, msg, project_path = self._create_project_full(
                    name, profiles_dir,
                    zotero_install_dir, create_library_shortcut
                )
            else:
                success, msg, project_path = self._create_project_light(
                    name, profiles_dir, language,
                    zotero_install_dir, create_library_shortcut
                )
            if success:
                print(f"[DEBUG] 项目创建完成，最终模式: native/{profile_mode}, 项目路径: {project_path}")
            return success, msg, project_path

        else:  # auto
            if templates_root and Path(templates_root).exists() and zotero_version:
                template_dir = self._match_template(templates_root, zotero_version)
                if template_dir:
                    success, msg, project_path = self._create_project_from_template(
                        name, profiles_dir, template_dir, language,
                        zotero_install_dir, create_library_shortcut
                    )
                    if success:
                        print(f"[DEBUG] 项目创建完成，最终模式: auto/template (使用模板), 项目路径: {project_path}")
                    return success, msg, project_path
            # 无模板，使用原生
            if profile_mode == "full":
                success, msg, project_path = self._create_project_full(
                    name, profiles_dir,
                    zotero_install_dir, create_library_shortcut
                )
            else:
                success, msg, project_path = self._create_project_light(
                    name, profiles_dir, language,
                    zotero_install_dir, create_library_shortcut
                )
            if success:
                print(f"[DEBUG] 项目创建完成，最终模式: auto/{profile_mode} (原生生成), 项目路径: {project_path}")
            return success, msg, project_path
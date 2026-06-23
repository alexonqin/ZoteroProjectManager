# -*- coding: utf-8 -*-
"""
Zotero 核心控制器
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path
from typing import List, Optional, Tuple

from models.profile import Profile
from utils.profile_registry import register_profile, unregister_profile
from utils.language_utils import write_language, read_language


class ZoteroController:
    """Zotero 核心控制类"""

    def __init__(self):
        self.zotero_exe_path = None

    # ---------- 路径设置 ----------
    def set_zotero_path(self, install_dir: str) -> Tuple[bool, str]:
        if not install_dir or not os.path.exists(install_dir):
            return False, "目录不存在"
        exe_path = Path(install_dir) / "zotero.exe"
        if not exe_path.exists():
            return False, "未找到 zotero.exe"
        self.zotero_exe_path = str(exe_path)
        return True, "有效"

    def get_zotero_exe_path(self) -> Optional[str]:
        return self.zotero_exe_path

    def get_zotero_file_version(self, install_dir: str) -> Optional[str]:
        exe_path = Path(install_dir) / "zotero.exe"
        if not exe_path.exists():
            return None
        try:
            import win32api
            info = win32api.GetFileVersionInfo(str(exe_path), "\\")
            return info.get('FileVersion') or info.get('ProductVersion')
        except Exception:
            return None

    # ---------- 启动 ----------
    def launch_project(self, project_path: str, project_name: str, zotero_install_dir: str) -> bool:
        exe_path = Path(zotero_install_dir) / "zotero.exe"
        if not exe_path.exists():
            return False
        data_dir = Path(project_path) / "data"
        if not data_dir.exists():
            return False

        try:
            subprocess.Popen([
                str(exe_path),
                "-datadir", str(data_dir),
                "-P", project_name
            ], shell=False)
            return True
        except Exception as e:
            print(f"启动失败: {e}")
            return False

    # ---------- 快捷方式 ----------
    def _create_shortcut_at_path(self, project_path: str, project_name: str,
                                  zotero_install_dir: str, target_dir: Path) -> Tuple[bool, str]:
        if sys.platform != "win32":
            return False, "仅支持 Windows"
        exe_path = Path(zotero_install_dir) / "zotero.exe"
        if not exe_path.exists():
            return False, "未找到 zotero.exe"
        data_dir = Path(project_path) / "data"
        if not data_dir.exists():
            return False, "项目 data 目录不存在"
        try:
            import win32com.client
            import pythoncom
            shortcut_path = target_dir / f"{project_name} - Zotero.lnk"
            counter = 1
            while shortcut_path.exists():
                shortcut_path = target_dir / f"{project_name} - Zotero ({counter}).lnk"
                counter += 1
            shell = win32com.client.Dispatch("WScript.Shell", pythoncom.CoInitialize())
            shortcut = shell.CreateShortCut(str(shortcut_path))
            shortcut.Targetpath = str(exe_path)
            shortcut.Arguments = f'-datadir "{data_dir}" -P "{project_name}"'
            shortcut.WorkingDirectory = str(exe_path.parent)
            shortcut.IconLocation = f"{str(exe_path)},0"
            shortcut.Save()
            return True, str(shortcut_path.name)
        except ImportError:
            return False, "缺少 pywin32"
        except Exception as e:
            return False, f"创建失败: {e}"

    def create_shortcut(self, project_path: str, project_name: str, zotero_install_dir: str) -> Tuple[bool, str]:
        desktop = Path(os.path.expandvars(r"%USERPROFILE%\Desktop"))
        return self._create_shortcut_at_path(project_path, project_name, zotero_install_dir, desktop)

    def create_shortcut_in_library(self, project_path: str, project_name: str,
                                   zotero_install_dir: str, library_dir: str) -> Tuple[bool, str]:
        library_path = Path(library_dir)
        if not library_path.exists():
            return False, "项目库目录不存在"
        return self._create_shortcut_at_path(project_path, project_name, zotero_install_dir, library_path)

    def delete_shortcuts(self, project_name: str, library_dir: str = None) -> int:
        deleted = 0
        desktop = Path(os.path.expandvars(r"%USERPROFILE%\Desktop"))
        for f in desktop.glob(f"{project_name} - Zotero*.lnk"):
            try:
                f.unlink()
                deleted += 1
            except:
                pass
        if library_dir:
            lib_path = Path(library_dir)
            if lib_path.exists():
                for f in lib_path.glob(f"{project_name} - Zotero*.lnk"):
                    try:
                        f.unlink()
                        deleted += 1
                    except:
                        pass
        return deleted

    # ---------- 使用中检测 ----------
    def is_project_in_use(self, project_path: str) -> bool:
        data_dir = Path(project_path) / "data"
        if data_dir.exists():
            for ext in ['.lck', '.wal']:
                for f in data_dir.glob(f"*{ext}"):
                    if f.exists():
                        return True
        try:
            import psutil
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if proc.info['name'] and 'zotero' in proc.info['name'].lower():
                        cmdline = proc.info['cmdline']
                        if cmdline and any('-datadir' in arg and str(project_path) in arg for arg in cmdline):
                            return True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
        except ImportError:
            pass
        return False

    # ---------- 删除 ----------
    def delete_project(self, project_path: str, project_name: str, library_dir: str = None) -> Tuple[bool, str]:
        try:
            unregister_profile(project_name)
            self.delete_shortcuts(project_name, library_dir)
            from utils.recycle_bin import move_to_recycle_bin
            success, err = move_to_recycle_bin(project_path)
            if not success:
                return False, err
            return True, "已移至回收站"
        except Exception as e:
            return False, str(e)

    # ---------- 语言 ----------
    def get_project_language(self, project_path: str) -> str:
        profiles_dir = Path(project_path) / "profiles"
        if not profiles_dir.exists():
            return None
        return read_language(str(profiles_dir))

    def set_project_language(self, project_path: str, lang_code: str) -> bool:
        profiles_dir = Path(project_path) / "profiles"
        if not profiles_dir.exists():
            return False
        return write_language(str(profiles_dir), lang_code)

    # ---------- 模板匹配 ----------
    def _match_template(self, templates_root: str, zotero_version: str) -> Optional[str]:
        if not templates_root or not os.path.exists(templates_root):
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

    def get_templates(self, templates_root: str) -> List[str]:
        if not templates_root or not os.path.exists(templates_root):
            return []
        root = Path(templates_root)
        return [d.name for d in root.iterdir() if d.is_dir()]

    # ---------- 获取项目 ----------
    def get_projects(self, profiles_dir: str) -> List[Profile]:
        projects = []
        if not profiles_dir or not os.path.exists(profiles_dir):
            return projects
        root = Path(profiles_dir)
        for item in root.iterdir():
            if item.is_dir():
                profile = Profile.from_project_path(str(item))
                if profile and profile.is_valid():
                    projects.append(profile)
        return projects

    # ---------- 辅助：确保 profiles/ 结构完整 ----------
    def _ensure_profile_structure(self, project_path: str, language: str) -> bool:
        """
        确保项目目录下存在完整的 profiles/ 配置结构。
        """
        print(f"[DEBUG] _ensure_profile_structure called with project_path={project_path}, language={language}")
        project_dir = Path(project_path)
        profiles_dir = project_dir / "profiles"

        # 1. 创建 profiles/ 目录
        try:
            profiles_dir.mkdir(parents=True, exist_ok=True)
            print(f"[DEBUG] Created profiles directory: {profiles_dir}")
        except Exception as e:
            print(f"[ERROR] 创建 profiles 目录失败: {e}")
            return False

        # 2. 创建 extensions/ 子目录
        extensions_dir = profiles_dir / "extensions"
        try:
            extensions_dir.mkdir(parents=True, exist_ok=True)
            print(f"[DEBUG] Created extensions directory: {extensions_dir}")
        except Exception as e:
            print(f"[ERROR] 创建 extensions 目录失败: {e}")
            return False

        # 3. 准备 prefs.js 文件（如果不存在）
        prefs_path = profiles_dir / "prefs.js"
        if not prefs_path.exists():
            try:
                default_content = '// ZPL 自动生成的配置文件\n'
                prefs_path.write_text(default_content, encoding='utf-8')
                print(f"[DEBUG] Created prefs.js: {prefs_path}")
            except Exception as e:
                print(f"[ERROR] 创建 prefs.js 失败: {e}")
                return False

        # 4. 写入语言设置
        if language is not None:
            print(f"[DEBUG] Calling write_language with language='{language}', profiles_dir={profiles_dir}")
            success = write_language(str(profiles_dir), language)
            if success:
                print(f"[DEBUG] write_language succeeded")
            else:
                print(f"[ERROR] write_language failed for language='{language}'")
                return False
        else:
            print("[WARNING] language is None, skipping write_language")

        return True

    # ---------- 新建项目 ----------
    def create_project(
        self,
        project_name: str,
        profiles_dir: str,
        templates_root: str,
        zotero_version: str,
        zotero_install_dir: str,
        language: str = 'zh-CN',
        create_shortcut: bool = False,
        create_library_shortcut: bool = True
    ) -> Tuple[bool, str, Optional[str]]:
        print(f"[DEBUG] create_project called with language={language}")
        # 校验
        if not project_name or not project_name.strip():
            return False, "项目名称不能为空", None
        name = project_name.strip()
        illegal = r'<>:"/\|?*'
        for ch in illegal:
            if ch in name:
                return False, f"非法字符: {ch}", None
        if not os.path.exists(profiles_dir):
            return False, "Profiles 目录不存在", None
        if not os.path.exists(templates_root):
            return False, "模板目录不存在", None
        template_dir = self._match_template(templates_root, zotero_version)
        if not template_dir:
            return False, f"未找到匹配 Zotero {zotero_version} 的模板", None

        project_path = Path(profiles_dir) / name
        if project_path.exists():
            return False, f"项目 '{name}' 已存在", None

        # 复制模板
        try:
            shutil.copytree(template_dir, project_path)
            print(f"[DEBUG] Template copied from {template_dir} to {project_path}")
        except Exception as e:
            return False, f"复制模板失败: {e}", None

        # 自动补全 profiles/ 结构
        if not self._ensure_profile_structure(str(project_path), language):
            return False, "创建项目配置结构失败", None

        profiles_subdir = project_path / "profiles"

        # 注册 Profile
        register_profile(name, str(profiles_subdir))
        print(f"[DEBUG] Profile registered: {name} -> {profiles_subdir}")

        # 生成快捷方式
        if create_library_shortcut:
            self.create_shortcut_in_library(str(project_path), name, zotero_install_dir, profiles_dir)
        if create_shortcut:
            self.create_shortcut(str(project_path), name, zotero_install_dir)

        return True, f"项目 '{name}' 创建成功", str(project_path)
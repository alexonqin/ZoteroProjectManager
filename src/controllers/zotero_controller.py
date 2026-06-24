# -*- coding: utf-8 -*-
"""
Zotero 核心控制器
"""

import os
import sys
import shutil
import subprocess
import time
import configparser
from pathlib import Path
from typing import List, Optional, Tuple

from models.profile import Profile
from utils.profile_registry import register_profile, unregister_profile, set_default_profile
from utils.language_utils import write_language, read_language


class ZoteroController:
    """Zotero 核心控制类"""

    def __init__(self, config_mgr=None):
        self.zotero_exe_path = None
        self.config_mgr = config_mgr

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

        try:
            profiles_dir.mkdir(parents=True, exist_ok=True)
            print(f"[DEBUG] Created profiles directory: {profiles_dir}")
        except Exception as e:
            print(f"[ERROR] 创建 profiles 目录失败: {e}")
            return False

        extensions_dir = profiles_dir / "extensions"
        try:
            extensions_dir.mkdir(parents=True, exist_ok=True)
            print(f"[DEBUG] Created extensions directory: {extensions_dir}")
        except Exception as e:
            print(f"[ERROR] 创建 extensions 目录失败: {e}")
            return False

        prefs_path = profiles_dir / "prefs.js"
        if not prefs_path.exists():
            try:
                default_content = '// ZPL 自动生成的配置文件\n'
                prefs_path.write_text(default_content, encoding='utf-8')
                print(f"[DEBUG] Created prefs.js: {prefs_path}")
            except Exception as e:
                print(f"[ERROR] 创建 prefs.js 失败: {e}")
                return False

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

    # ---------- 原生生成模式 ----------
    def _wait_for_zotero_init(self, project_path: str, timeout: int = 10) -> bool:
        """等待 Zotero 初始化完成（检测 data/zotero.sqlite）"""
        data_dir = Path(project_path) / "data"
        start = time.time()
        while time.time() - start < timeout:
            sqlite_path = data_dir / "zotero.sqlite"
            if sqlite_path.exists() and sqlite_path.stat().st_size > 0:
                print("[DEBUG] Zotero initialization completed")
                return True
            time.sleep(0.5)
        print(f"[ERROR] Zotero initialization timed out after {timeout} seconds")
        return False

    def _close_zotero(self, process):
        """关闭 Zotero 进程"""
        try:
            process.terminate()
            time.sleep(1)
            if process.poll() is None:
                process.kill()
            print("[DEBUG] Zotero process terminated")
        except Exception as e:
            print(f"[ERROR] Failed to close Zotero: {e}")

    def _create_project_native(
        self,
        project_name: str,
        profiles_dir: str,
        language: str,
        zotero_install_dir: str,
        create_shortcut: bool,
        create_library_shortcut: bool
    ) -> Tuple[bool, str, Optional[str]]:
        """使用 Zotero 原生生成方式创建项目（先注册 Profile，避免弹窗）"""
        name = project_name.strip()
        project_path = Path(profiles_dir) / name
        print(f"[DEBUG] Native creation: {project_path}")

        # 1. 创建项目目录和 data/、profiles/ 空目录
        try:
            project_path.mkdir(parents=True, exist_ok=True)
            (project_path / "data").mkdir(exist_ok=True)
            (project_path / "profiles").mkdir(exist_ok=True)
            print(f"[DEBUG] Created directories: {project_path}")
        except Exception as e:
            return False, f"创建项目目录失败: {e}", None

        profiles_dir_path = project_path / "profiles"

        # 2. 手动注册 Profile（避免 Zotero Profile Manager 弹窗）
        if not register_profile(name, str(profiles_dir_path)):
            return False, "注册 Profile 失败", None

        # 3. 设置该 Profile 为默认（确保后续启动不弹窗）
        set_default_profile(name)

        # 4. 启动 Zotero 进行初始化
        exe_path = Path(zotero_install_dir) / "zotero.exe"
        if not exe_path.exists():
            return False, "Zotero 安装路径无效", None

        print("[DEBUG] Starting Zotero for native initialization...")
        try:
            proc = subprocess.Popen([
                str(exe_path),
                "-datadir", str(project_path / "data"),
                "-P", name
            ], shell=False)
        except Exception as e:
            return False, f"启动 Zotero 失败: {e}", None

        # 5. 等待初始化完成（检测 zotero.sqlite）
        if not self._wait_for_zotero_init(str(project_path)):
            self._close_zotero(proc)
            return False, "Zotero 初始化超时，请检查 Zotero 是否正常工作", None

        # 6. 关闭 Zotero
        self._close_zotero(proc)

        # 7. 写入语言设置（此时 Zotero 已关闭，修改 prefs.js 安全）
        if language is not None:
            if not write_language(str(profiles_dir_path), language):
                print("[WARNING] Failed to write language settings, continuing...")

        # 8. 生成快捷方式
        if create_library_shortcut:
            self.create_shortcut_in_library(str(project_path), name, zotero_install_dir, profiles_dir)
        if create_shortcut:
            self.create_shortcut(str(project_path), name, zotero_install_dir)

        return True, f"项目 '{name}' 创建成功（Zotero 自动生成项目文件）", str(project_path)

    # ---------- 模板复制模式 ----------
    def _create_project_from_template(
        self,
        project_name: str,
        profiles_dir: str,
        template_dir: str,
        language: str,
        zotero_install_dir: str,
        create_shortcut: bool,
        create_library_shortcut: bool
    ) -> Tuple[bool, str, Optional[str]]:
        """使用模板复制方式创建项目"""
        name = project_name.strip()
        project_path = Path(profiles_dir) / name
        print(f"[DEBUG] Template creation: {project_path} from {template_dir}")

        # 1. 复制模板
        try:
            shutil.copytree(template_dir, project_path)
            print(f"[DEBUG] Template copied")
        except Exception as e:
            return False, f"复制模板失败: {e}", None

        # 2. 确保 profiles 结构完整并写入语言
        if not self._ensure_profile_structure(str(project_path), language):
            return False, "创建项目配置结构失败", None

        profiles_subdir = project_path / "profiles"

        # 3. 注册 Profile
        register_profile(name, str(profiles_subdir))
        print(f"[DEBUG] Profile registered: {name} -> {profiles_subdir}")

        # 4. 生成快捷方式
        if create_library_shortcut:
            self.create_shortcut_in_library(str(project_path), name, zotero_install_dir, profiles_dir)
        if create_shortcut:
            self.create_shortcut(str(project_path), name, zotero_install_dir)

        return True, f"项目 '{name}' 创建成功（使用模板快速复制）", str(project_path)

    # ---------- 主创建方法 ----------
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
        creation_method: Optional[str] = None
    ) -> Tuple[bool, str, Optional[str]]:
        """
        统一入口：根据配置和模板可用性选择创建方式
        
        creation_method:
            - "auto": 自动选择（有模板用模板，无模板用原生）
            - "template": 始终使用模板复制（无模板则报错）
            - "native": 始终使用原生生成（忽略模板）
        """
        print(f"[DEBUG] create_project called with language={language}, creation_method={creation_method}")

        # 1. 验证输入（基础验证）
        if not project_name or not project_name.strip():
            return False, "项目名称不能为空", None
        name = project_name.strip()
        illegal = r'<>:"/\|?*'
        for ch in illegal:
            if ch in name:
                return False, f"非法字符: {ch}", None
        if not os.path.exists(profiles_dir):
            return False, "Profiles 目录不存在", None

        # 2. 确定创建方式
        if creation_method is None and self.config_mgr:
            creation_method = self.config_mgr.get_creation_method()
        else:
            creation_method = "auto"

        print(f"[DEBUG] Using creation method: {creation_method}")

        # 3. 根据创建方式处理模板
        if creation_method == "template":
            # 始终使用模板：必须提供有效的模板目录和版本
            if not templates_root or not os.path.exists(templates_root):
                return False, "模板目录不存在，请设置正确的模板目录", None
            if not zotero_version:
                return False, "Zotero 版本号未设置，请设置版本号", None
            template_dir = self._match_template(templates_root, zotero_version)
            if not template_dir:
                return False, f"未找到匹配 Zotero {zotero_version} 的模板。请准备模板或切换创建方式。", None
            # 使用模板复制
            return self._create_project_from_template(
                name, profiles_dir, template_dir, language,
                zotero_install_dir, create_shortcut, create_library_shortcut
            )

        elif creation_method == "native":
            # 始终使用原生生成：忽略模板目录和版本
            return self._create_project_native(
                name, profiles_dir, language,
                zotero_install_dir, create_shortcut, create_library_shortcut
            )

        else:  # "auto"
            # 自动选择：有模板用模板，无模板用原生（静默 fallback）
            if templates_root and os.path.exists(templates_root) and zotero_version:
                template_dir = self._match_template(templates_root, zotero_version)
                if template_dir:
                    return self._create_project_from_template(
                        name, profiles_dir, template_dir, language,
                        zotero_install_dir, create_shortcut, create_library_shortcut
                    )
            # 无模板或模板无效，使用原生生成（不报错）
            return self._create_project_native(
                name, profiles_dir, language,
                zotero_install_dir, create_shortcut, create_library_shortcut
            )
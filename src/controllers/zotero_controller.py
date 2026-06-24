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
    def _ensure_profile_structure(self, project_path: str, language: str, 
                                  precreate_prefs: bool = True) -> bool:
        """
        确保项目目录下存在完整的 profiles/ 配置结构。
        
        Args:
            project_path: 项目根目录路径
            language: 语言代码（仅当 precreate_prefs=True 时使用）
            precreate_prefs: 是否预先创建 prefs.js（True: 轻量模式，False: 完整模式）
        """
        print(f"[DEBUG] _ensure_profile_structure called with project_path={project_path}, "
              f"language={language}, precreate_prefs={precreate_prefs}")
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

        # 如果不需要预先创建 prefs.js（完整模式），直接返回
        if not precreate_prefs:
            prefs_path = profiles_dir / "prefs.js"
            if prefs_path.exists():
                try:
                    prefs_path.unlink()
                    print(f"[DEBUG] Removed existing prefs.js for full mode")
                except Exception:
                    pass
            print(f"[DEBUG] Skipping prefs.js creation for full mode")
            return True

        # 轻量模式下直接写入完整的 prefs.js
        if language is None:
            language = 'zh-CN'
        prefs_content = f'''// Mozilla User Preferences
user_pref("intl.locale.matchOS", false);
user_pref("intl.locale.requested", "{language}");
'''
        prefs_path = profiles_dir / "prefs.js"
        try:
            prefs_path.write_text(prefs_content, encoding='utf-8')
            print(f"[DEBUG] Written prefs.js with language '{language}'")
        except Exception as e:
            print(f"[ERROR] 写入 prefs.js 失败: {e}")
            return False

        # 验证（仅轻量模式）
        verify_lang = read_language(str(profiles_dir))
        if verify_lang == language:
            print(f"[DEBUG] Language verification passed: {verify_lang}")
            return True
        else:
            print(f"[ERROR] Language verification failed: expected {language}, got {verify_lang}")
            return False

    # ---------- 等待初始化 ----------
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

    # ---------- 完整初始化模式（方案二：空 Profile + Zotero 自动补全） ----------
    def _create_project_full(
        self,
        project_name: str,
        profiles_dir: str,
        zotero_install_dir: str,
        create_shortcut: bool,
        create_library_shortcut: bool
    ) -> Tuple[bool, str, Optional[str]]:
        """
        完整模式创建项目（模拟手动 Profile Manager 创建）
        
        流程：
        1. 创建空目录（data/ 和 profiles/）
        2. 在 profiles.ini 中注册 Profile（指向空 profiles/ 目录）
        3. 设置 Profile 为默认（避免 Profile Manager 弹窗）
        4. 启动 Zotero（自动补全完整的 profiles/ 配置）
        5. 等待初始化完成（生成 55MB 完整项目）
        6. 关闭 Zotero
        7. 生成快捷方式
        """
        name = project_name.strip()
        project_path = Path(profiles_dir) / name
        print(f"[DEBUG] Full mode creation (simulate Profile Manager): {project_path}")

        # --- 1. 创建空目录 ---
        try:
            project_path.mkdir(parents=True, exist_ok=True)
            (project_path / "data").mkdir(exist_ok=True)
            (project_path / "profiles").mkdir(exist_ok=True)
            print(f"[DEBUG] Created project directory: {project_path}")
        except Exception as e:
            return False, f"创建项目目录失败: {e}", None

        profiles_dir_path = project_path / "profiles"
        data_dir_path = project_path / "data"

        # 确保 prefs.js 不存在（Zotero 会自己生成完整的 prefs.js）
        prefs_path = profiles_dir_path / "prefs.js"
        if prefs_path.exists():
            try:
                prefs_path.unlink()
                print(f"[DEBUG] Removed existing prefs.js")
            except Exception:
                pass

        # --- 2. 注册 Profile（指向空 profiles/ 目录）---
        if not register_profile(name, str(profiles_dir_path)):
            return False, "注册 Profile 失败", None

        # --- 3. 设置该 Profile 为默认 ---
        set_default_profile(name)
        print(f"[DEBUG] Profile '{name}' registered and set as default")

        # --- 4. 启动 Zotero 完成完整初始化 ---
        exe_path = Path(zotero_install_dir) / "zotero.exe"
        if not exe_path.exists():
            return False, "Zotero 安装路径无效", None

        print("[DEBUG] Starting Zotero for full initialization...")
        try:
            proc = subprocess.Popen([
                str(exe_path),
                "-datadir", str(data_dir_path),
                "-P", name
            ], shell=False)
        except Exception as e:
            return False, f"启动 Zotero 失败: {e}", None

        # --- 5. 等待初始化完成 ---
        if not self._wait_for_zotero_init(str(project_path)):
            self._close_zotero(proc)
            return False, "Zotero 初始化超时，请检查 Zotero 是否正常工作", None

        # --- 6. 关闭 Zotero ---
        self._close_zotero(proc)
        print(f"[DEBUG] Project initialization complete with full files")

        # --- 7. 生成快捷方式 ---
        if create_library_shortcut:
            self.create_shortcut_in_library(str(project_path), name, zotero_install_dir, profiles_dir)

        return True, f"项目 '{name}' 创建成功（完整模式）", str(project_path)

    # ---------- 轻量初始化模式 ----------
    def _create_project_light(
        self,
        project_name: str,
        profiles_dir: str,
        language: str,
        zotero_install_dir: str,
        create_shortcut: bool,
        create_library_shortcut: bool
    ) -> Tuple[bool, str, Optional[str]]:
        """
        轻量模式创建项目（19MB 最小项目 + 预置语言）
        """
        name = project_name.strip()
        project_path = Path(profiles_dir) / name
        print(f"[DEBUG] Light mode creation: {project_path}")

        # --- 1. 创建目录并写入 prefs.js ---
        try:
            project_path.mkdir(parents=True, exist_ok=True)
            (project_path / "data").mkdir(exist_ok=True)
            (project_path / "profiles").mkdir(exist_ok=True)
            print(f"[DEBUG] Created project directory: {project_path}")
        except Exception as e:
            return False, f"创建项目目录失败: {e}", None

        # 写入 prefs.js（含语言设置）
        if not self._ensure_profile_structure(str(project_path), language, precreate_prefs=True):
            return False, "写入语言设置失败", None

        profiles_dir_path = project_path / "profiles"

        # --- 2. 注册 Profile ---
        if not register_profile(name, str(profiles_dir_path)):
            return False, "注册 Profile 失败", None

        set_default_profile(name)

        # --- 3. 启动 Zotero 完成最小化初始化 ---
        exe_path = Path(zotero_install_dir) / "zotero.exe"
        if not exe_path.exists():
            return False, "Zotero 安装路径无效", None

        print("[DEBUG] Starting Zotero for light initialization...")
        try:
            proc = subprocess.Popen([
                str(exe_path),
                "-datadir", str(project_path / "data"),
                "-P", name
            ], shell=False)
        except Exception as e:
            return False, f"启动 Zotero 失败: {e}", None

        if not self._wait_for_zotero_init(str(project_path)):
            self._close_zotero(proc)
            return False, "Zotero 初始化超时，请检查 Zotero 是否正常工作", None

        # --- 4. 关闭 Zotero ---
        self._close_zotero(proc)

        # --- 5. 生成快捷方式 ---
        if create_library_shortcut:
            self.create_shortcut_in_library(str(project_path), name, zotero_install_dir, profiles_dir)

        return True, f"项目 '{name}' 创建成功（轻量模式）", str(project_path)

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
        """使用模板复制方式创建项目（保留原有逻辑）"""
        name = project_name.strip()
        project_path = Path(profiles_dir) / name
        print(f"[DEBUG] Template creation: {project_path} from {template_dir}")

        try:
            shutil.copytree(template_dir, project_path)
            print(f"[DEBUG] Template copied")
        except Exception as e:
            return False, f"复制模板失败: {e}", None

        # 确保 profiles 结构并写入语言（模板模式使用轻量方式）
        if not self._ensure_profile_structure(str(project_path), language, precreate_prefs=True):
            return False, "创建项目配置结构失败", None

        profiles_subdir = project_path / "profiles"
        register_profile(name, str(profiles_subdir))
        print(f"[DEBUG] Profile registered: {name} -> {profiles_subdir}")

        if create_library_shortcut:
            self.create_shortcut_in_library(str(project_path), name, zotero_install_dir, profiles_dir)

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
        creation_method: Optional[str] = None,
        profile_mode: Optional[str] = None
    ) -> Tuple[bool, str, Optional[str]]:
        """
        统一入口：根据配置和模板可用性选择创建方式
        
        creation_method:
            - "auto": 自动选择（有模板用模板，无模板用原生）
            - "template": 始终使用模板复制（无模板则报错）
            - "native": 始终使用原生生成（忽略模板）
        
        profile_mode:
            - "full": 完整模式（55MB，完整功能，不预设语言）
            - "light": 轻量模式（19MB，最小功能，预设语言）
        """
        print(f"[DEBUG] create_project called with language={language}, "
              f"creation_method={creation_method}, profile_mode={profile_mode}")

        # 1. 验证输入
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

        # 3. 确定完整度模式
        if profile_mode is None and self.config_mgr:
            profile_mode = self.config_mgr.get_config().creation_profile_mode
        else:
            profile_mode = "full"
        print(f"[DEBUG] Using profile mode: {profile_mode}")

        # 4. 根据创建方式处理模板
        if creation_method == "template":
            if not templates_root or not os.path.exists(templates_root):
                return False, "模板目录不存在，请设置正确的模板目录", None
            if not zotero_version:
                return False, "Zotero 版本号未设置，请设置版本号", None
            template_dir = self._match_template(templates_root, zotero_version)
            if not template_dir:
                return False, f"未找到匹配 Zotero {zotero_version} 的模板。请准备模板或切换创建方式。", None
            return self._create_project_from_template(
                name, profiles_dir, template_dir, language,
                zotero_install_dir, create_shortcut, create_library_shortcut
            )

        elif creation_method == "native":
            if profile_mode == "full":
                # 完整模式：不传递 language
                return self._create_project_full(
                    name, profiles_dir,
                    zotero_install_dir, create_shortcut, create_library_shortcut
                )
            else:
                return self._create_project_light(
                    name, profiles_dir, language,
                    zotero_install_dir, create_shortcut, create_library_shortcut
                )

        else:  # "auto"
            if templates_root and os.path.exists(templates_root) and zotero_version:
                template_dir = self._match_template(templates_root, zotero_version)
                if template_dir:
                    return self._create_project_from_template(
                        name, profiles_dir, template_dir, language,
                        zotero_install_dir, create_shortcut, create_library_shortcut
                    )
            # 无模板或模板无效，使用原生生成
            if profile_mode == "full":
                return self._create_project_full(
                    name, profiles_dir,
                    zotero_install_dir, create_shortcut, create_library_shortcut
                )
            else:
                return self._create_project_light(
                    name, profiles_dir, language,
                    zotero_install_dir, create_shortcut, create_library_shortcut
                )
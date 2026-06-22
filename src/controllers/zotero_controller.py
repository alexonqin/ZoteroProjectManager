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


class ZoteroController:
    """Zotero 核心控制类"""

    def __init__(self):
        self.zotero_exe_path = None

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

    def launch_project(self, project_path: str, zotero_install_dir: str) -> bool:
        exe_path = Path(zotero_install_dir) / "zotero.exe"
        if not exe_path.exists():
            return False
        data_dir = Path(project_path) / "data"
        if not data_dir.exists():
            return False
        try:
            subprocess.Popen([str(exe_path), "-datadir", str(data_dir)], shell=False)
            return True
        except Exception as e:
            print("启动失败: {}".format(e))
            return False

    # ----- 快捷方式生成（内部方法）-----
    def _create_shortcut_at_path(self, project_path: str, project_name: str,
                                  zotero_install_dir: str, target_dir: Path) -> Tuple[bool, str]:
        """在指定目录生成快捷方式（内部方法）"""
        if sys.platform != "win32":
            return False, "仅支持 Windows 平台"
        exe_path = Path(zotero_install_dir) / "zotero.exe"
        if not exe_path.exists():
            return False, "未找到 zotero.exe"
        data_dir = Path(project_path) / "data"
        if not data_dir.exists():
            return False, "项目 data 目录不存在"
        try:
            import win32com.client
            import pythoncom
            shortcut_path = target_dir / "{} - Zotero.lnk".format(project_name)
            counter = 1
            while shortcut_path.exists():
                shortcut_path = target_dir / "{} - Zotero ({}).lnk".format(project_name, counter)
                counter += 1
            shell = win32com.client.Dispatch("WScript.Shell", pythoncom.CoInitialize())
            shortcut = shell.CreateShortCut(str(shortcut_path))
            shortcut.Targetpath = str(exe_path)
            shortcut.Arguments = '-datadir "{}"'.format(data_dir)
            shortcut.WorkingDirectory = str(exe_path.parent)
            shortcut.IconLocation = "{},0".format(str(exe_path))
            shortcut.Save()
            return True, str(shortcut_path.name)
        except ImportError:
            return False, "缺少 pywin32 库，请安装: pip install pywin32"
        except Exception as e:
            return False, "创建失败: {}".format(e)

    # ----- 对外快捷方式接口 -----
    def create_shortcut_on_desktop(self, project_path: str, project_name: str,
                                   zotero_install_dir: str) -> Tuple[bool, str]:
        """在桌面生成快捷方式"""
        desktop = Path(os.path.expandvars(r"%USERPROFILE%\Desktop"))
        return self._create_shortcut_at_path(project_path, project_name, zotero_install_dir, desktop)

    def create_shortcut_in_library(self, project_path: str, project_name: str,
                                   zotero_install_dir: str, library_dir: str) -> Tuple[bool, str]:
        """在项目库根目录生成快捷方式"""
        library_path = Path(library_dir)
        if not library_path.exists():
            return False, "项目库目录不存在"
        return self._create_shortcut_at_path(project_path, project_name, zotero_install_dir, library_path)

    def delete_shortcut_on_desktop(self, project_name: str) -> int:
        desktop = Path(os.path.expandvars(r"%USERPROFILE%\Desktop"))
        deleted = 0
        for f in desktop.glob("{} - Zotero*.lnk".format(project_name)):
            try:
                f.unlink()
                deleted += 1
            except Exception:
                pass
        return deleted

    def delete_shortcut_in_library(self, project_name: str, library_dir: str) -> int:
        library_path = Path(library_dir)
        if not library_path.exists():
            return 0
        deleted = 0
        for f in library_path.glob("{} - Zotero*.lnk".format(project_name)):
            try:
                f.unlink()
                deleted += 1
            except Exception:
                pass
        return deleted

    # ----- 核心业务 -----
    def create_project(
        self,
        project_name: str,
        profiles_dir: str,
        templates_root: str,
        zotero_version: str,
        zotero_install_dir: str,
        create_shortcut: bool = False,          # 默认不创建桌面快捷方式
        create_library_shortcut: bool = True    # 始终在项目库根目录创建
    ) -> Tuple[bool, str, Optional[str]]:
        """
        一键新建项目
        """
        # 1. 验证名称
        if not project_name or not project_name.strip():
            return False, "项目名称不能为空", None
        name = project_name.strip()
        illegal_chars = r'<>:"/\|?*'
        for ch in illegal_chars:
            if ch in name:
                return False, "项目名称不能包含非法字符: {}".format(ch), None

        # 2. 验证目录
        if not profiles_dir or not os.path.exists(profiles_dir):
            return False, "Profiles 目录不存在", None
        if not templates_root or not os.path.exists(templates_root):
            return False, "模板目录不存在，请先在偏好设置中设置", None

        # 3. 匹配模板
        template_dir = self._match_template(templates_root, zotero_version)
        if not template_dir:
            return False, "未找到匹配 Zotero {} 的模板，请准备模板".format(zotero_version), None

        # 4. 检查是否已存在
        project_path = Path(profiles_dir) / name
        if project_path.exists():
            return False, "项目 '{}' 已存在".format(name), None

        # 5. 复制模板
        try:
            shutil.copytree(template_dir, project_path)
        except Exception as e:
            return False, "创建项目失败: {}".format(e), None

        # 6. 生成项目库快捷方式（默认总是生成）
        if create_library_shortcut:
            success, msg = self.create_shortcut_in_library(
                str(project_path), name, zotero_install_dir, profiles_dir
            )
            if not success:
                print("项目库快捷方式创建失败: {}".format(msg))

        # 7. 生成桌面快捷方式（仅当用户明确要求）
        if create_shortcut:
            success, msg = self.create_shortcut_on_desktop(
                str(project_path), name, zotero_install_dir
            )
            if not success:
                print("桌面快捷方式创建失败: {}".format(msg))

        return True, "项目 '{}' 创建成功".format(name), str(project_path)

    def _match_template(self, templates_root: str, zotero_version: str) -> Optional[str]:
        if not templates_root or not os.path.exists(templates_root):
            return None
        root = Path(templates_root)
        subdirs = [d for d in root.iterdir() if d.is_dir()]
        if not subdirs:
            return None
        for d in subdirs:
            if d.name == "v{}".format(zotero_version):
                return str(d)
        main_version = zotero_version.split('.')[0] if '.' in zotero_version else zotero_version
        for d in subdirs:
            if d.name.startswith("v{}.".format(main_version)):
                return str(d)
        return None

    def delete_project(self, project_path: str, project_name: str, library_dir: str = None) -> Tuple[bool, str]:
        try:
            path = Path(project_path)
            if path.exists():
                shutil.rmtree(path)
            self.delete_shortcut_on_desktop(project_name)
            if library_dir:
                self.delete_shortcut_in_library(project_name, library_dir)
            return True, "项目 '{}' 已删除".format(project_name)
        except Exception as e:
            return False, "删除失败: {}".format(e)

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

    def get_templates(self, templates_root: str) -> List[str]:
        if not templates_root or not os.path.exists(templates_root):
            return []
        root = Path(templates_root)
        return [d.name for d in root.iterdir() if d.is_dir()]
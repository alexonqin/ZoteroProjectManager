# -*- coding: utf-8 -*-
"""
快捷方式管理（仅项目库）
"""

import os
import sys
from pathlib import Path
from typing import Tuple


class ShortcutMixin:
    """快捷方式管理混入（仅项目库）"""

    def _create_shortcut_at_path(self, project_path: str, project_name: str,
                                  zotero_install_dir: str, target_dir: Path) -> Tuple[bool, str]:
        if sys.platform != "win32":
            return False, "仅支持Windows"
        exe_path = Path(zotero_install_dir) / "zotero.exe"
        if not exe_path.exists():
            return False, "未找到zotero.exe"
        data_dir = Path(project_path) / "data"
        if not data_dir.exists():
            return False, "项目data目录不存在"
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
            return False, "缺少pywin32"
        except Exception as e:
            return False, f"创建失败: {e}"

    def create_shortcut_in_library(self, project_path: str, project_name: str,
                                   zotero_install_dir: str, library_dir: str) -> Tuple[bool, str]:
        library_path = Path(library_dir)
        if not library_path.exists():
            return False, "项目库目录不存在"
        return self._create_shortcut_at_path(project_path, project_name, zotero_install_dir, library_path)

    def delete_shortcuts(self, project_name: str, library_dir: str = None) -> int:
        deleted = 0
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

    def update_shortcuts_for_rename(self, old_name: str, new_name: str,
                                    old_path: str, new_path: str,
                                    library_dir: str, zotero_install_dir: str) -> int:
        if not library_dir or not Path(library_dir).exists():
            return 0
        lib_path = Path(library_dir)
        updated = 0
        for lnk in lib_path.glob(f"{old_name} - Zotero*.lnk"):
            try:
                new_lnk_name = lnk.name.replace(old_name, new_name)
                new_lnk_path = lnk.parent / new_lnk_name
                lnk.rename(new_lnk_path)
                import win32com.client
                import pythoncom
                shell = win32com.client.Dispatch("WScript.Shell", pythoncom.CoInitialize())
                shortcut = shell.CreateShortCut(str(new_lnk_path))
                shortcut.Arguments = f'-datadir "{Path(new_path) / "data"}" -P "{new_name}"'
                shortcut.Save()
                updated += 1
            except Exception as e:
                print(f"[WARN] 更新快捷方式失败: {lnk}, 错误: {e}")
                try:
                    lnk.unlink()
                    self.create_shortcut_in_library(new_path, new_name, zotero_install_dir, library_dir)
                    updated += 1
                except:
                    pass
        return updated
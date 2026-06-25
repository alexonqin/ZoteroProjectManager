# -*- coding: utf-8 -*-
"""
控制器基类 - 提供共享属性和基础方法
"""

from pathlib import Path
from typing import Optional, Tuple

from utils.config_manager import ConfigManager


class BaseController:
    """控制器基类，包含配置和路径管理"""

    def __init__(self, config_mgr: ConfigManager):
        self.config_mgr = config_mgr
        self.config = config_mgr.get_config()
        self.zotero_exe_path: Optional[str] = None

    def set_zotero_path(self, install_dir: str) -> Tuple[bool, str]:
        if not install_dir or not Path(install_dir).exists():
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
# -*- coding: utf-8 -*-
"""
项目启动与进程管理模块
"""

import subprocess
import time
from pathlib import Path
from typing import Optional


class LauncherMixin:
    """启动与进程管理混入"""

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
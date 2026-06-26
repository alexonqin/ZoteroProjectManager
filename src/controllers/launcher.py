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
        # ===== 调试日志开始 =====
        print("=" * 60)
        print("[DEBUG] launch_project 被调用")
        print(f"[DEBUG] project_path = '{project_path}'")
        print(f"[DEBUG] project_name = '{project_name}'")
        print(f"[DEBUG] project_name 长度 = {len(project_name)}")
        print(f"[DEBUG] project_name 的 repr = {repr(project_name)}")
        print(f"[DEBUG] zotero_install_dir = '{zotero_install_dir}'")
        print("=" * 60)

        # 清理 project_name 首尾空白字符（包括换行符、回车符）
        original_name = project_name
        project_name = project_name.strip()
        if project_name != original_name:
            print(f"[DEBUG] 注意: project_name 被清理，新值 = '{project_name}'")

        exe_path = Path(zotero_install_dir) / "zotero.exe"
        print(f"[DEBUG] exe_path = '{exe_path}', exists = {exe_path.exists()}")

        if not exe_path.exists():
            print("[ERROR] zotero.exe 不存在")
            return False

        data_dir = Path(project_path) / "data"
        print(f"[DEBUG] data_dir = '{data_dir}', exists = {data_dir.exists()}")

        if not data_dir.exists():
            print("[ERROR] data 目录不存在")
            return False

        # 构造命令
        cmd = [
            str(exe_path),
            "-datadir",
            str(data_dir),
            "-P",
            project_name
        ]
        print(f"[DEBUG] 即将执行的命令: {' '.join(cmd)}")
        print("[DEBUG] 正在启动 Zotero...")

        try:
            subprocess.Popen(cmd, shell=False)
            print("[DEBUG] Zotero 启动命令已执行")
            return True
        except Exception as e:
            print(f"[ERROR] 启动失败: {e}")
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
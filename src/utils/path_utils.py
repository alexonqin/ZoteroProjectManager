# -*- coding: utf-8 -*-
"""
路径工具函数
"""

import os
import sys
from pathlib import Path
from typing import Optional


def get_desktop_path() -> Path:
    """获取桌面路径"""
    if sys.platform == "win32":
        return Path(os.path.expandvars(r"%USERPROFILE%\Desktop"))
    elif sys.platform == "darwin":
        return Path.home() / "Desktop"
    else:
        return Path.home() / "Desktop"


def normalize_path(path: str) -> str:
    """规范化路径"""
    return str(Path(path).resolve())


def is_valid_directory(path: str) -> bool:
    """检查路径是否为有效目录"""
    return path and Path(path).exists() and Path(path).is_dir()


def ensure_directory(path: str) -> bool:
    """确保目录存在，如不存在则创建"""
    try:
        Path(path).mkdir(parents=True, exist_ok=True)
        return True
    except Exception:
        return False
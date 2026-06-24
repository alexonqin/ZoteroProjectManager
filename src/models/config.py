# -*- coding: utf-8 -*-
"""
配置数据模型
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional


# ============================================================
# 应用元数据（版本、名称等）
# ============================================================
APP_NAME = "Zotero Project Launcher"
APP_ABBR = "ZPL"
APP_VERSION = "v0.1.2-beta"
APP_COPYRIGHT = "© 2026 alexonqin"
APP_LICENSE = "MIT License"
APP_REPO_URL = "https://github.com/alexonqin/ZoteroProjectLauncher"
APP_ISSUE_URL = "https://github.com/alexonqin/ZoteroProjectLauncher/issues"


@dataclass
class AppConfig:
    """应用程序配置（用户偏好）"""

    # Zotero 设置
    zotero_version: str = ""
    zotero_install_dir: str = ""

    # 目录设置
    templates_root: str = ""
    profiles_current: str = ""
    profiles_default: str = ""
    profiles_history: List[str] = field(default_factory=list)

    # 语言设置
    language: str = "zh_CN"
    default_language: str = "zh-CN"   # 新项目默认语言

    # 项目创建方式
    creation_method: str = "auto"     # "auto" | "template" | "native"

    # 项目完整度模式
    creation_profile_mode: str = "full"  # "full" | "light"

    # 界面设置
    window_size: Dict[str, int] = field(default_factory=lambda: {"width": 800, "height": 600})
    window_position: Dict[str, int] = field(default_factory=lambda: {"x": -1, "y": -1})

    # 新建项目默认选项
    auto_create_shortcut: bool = True

    # 项目备注
    project_notes: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "zotero_version": self.zotero_version,
            "zotero_install_dir": self.zotero_install_dir,
            "templates_root": self.templates_root,
            "profiles_current": self.profiles_current,
            "profiles_default": self.profiles_default,
            "profiles_history": self.profiles_history,
            "language": self.language,
            "default_language": self.default_language,
            "creation_method": self.creation_method,
            "creation_profile_mode": self.creation_profile_mode,
            "window_size": self.window_size,
            "window_position": self.window_position,
            "auto_create_shortcut": self.auto_create_shortcut,
            "project_notes": self.project_notes
        }

    @classmethod
    def from_dict(cls, data: dict) -> "AppConfig":
        return cls(
            zotero_version=data.get("zotero_version", ""),
            zotero_install_dir=data.get("zotero_install_dir", ""),
            templates_root=data.get("templates_root", ""),
            profiles_current=data.get("profiles_current", ""),
            profiles_default=data.get("profiles_default", ""),
            profiles_history=data.get("profiles_history", []),
            language=data.get("language", "zh_CN"),
            default_language=data.get("default_language", "zh-CN"),
            creation_method=data.get("creation_method", "auto"),
            creation_profile_mode=data.get("creation_profile_mode", "full"),
            window_size=data.get("window_size", {"width": 800, "height": 600}),
            window_position=data.get("window_position", {"x": -1, "y": -1}),
            auto_create_shortcut=data.get("auto_create_shortcut", True),
            project_notes=data.get("project_notes", {})
        )
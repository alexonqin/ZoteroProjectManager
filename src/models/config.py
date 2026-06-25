# -*- coding: utf-8 -*-
"""
配置数据模型
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional


APP_NAME = "Zotero Project Launcher"
APP_ABBR = "ZPL"
APP_VERSION = "v0.1.4-beta"
APP_COPYRIGHT = "© 2026 alexonqin"
APP_LICENSE = "MIT License"
APP_REPO_URL = "https://github.com/alexonqin/ZoteroProjectLauncher"
APP_ISSUE_URL = "https://github.com/alexonqin/ZoteroProjectLauncher/issues"


@dataclass
class AppConfig:
    """应用程序配置（用户偏好）"""

    zotero_version: str = ""
    zotero_install_dir: str = ""

    templates_root: str = ""
    profiles_current: str = ""
    profiles_default: str = ""
    profiles_history: List[str] = field(default_factory=list)

    language: str = "zh_CN"
    default_language: str = "zh-CN"

    creation_method: str = "auto"
    creation_profile_mode: str = "full"  # "full" | "light"

    window_size: Dict[str, int] = field(default_factory=lambda: {"width": 800, "height": 600})
    window_position: Dict[str, int] = field(default_factory=lambda: {"x": -1, "y": -1})

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
            project_notes=data.get("project_notes", {})
        )
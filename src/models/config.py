# -*- coding: utf-8 -*-
"""
配置数据模型
"""

from dataclasses import dataclass, field
from typing import List, Dict


APP_NAME = "Zotero Project Manager"
APP_ABBR = "ZPM"
APP_VERSION = "v0.1.7-beta"
APP_COPYRIGHT = "© 2026 alexonqin"
APP_LICENSE = "MIT License"
APP_REPO_URL = "https://github.com/alexonqin/ZoteroProjectManager"
APP_ISSUE_URL = "https://github.com/alexonqin/ZoteroProjectManager/issues"


@dataclass
class AppConfig:
    """应用程序配置（用户偏好）"""

    # Zotero 设置
    zotero_install_dir: str = ""

    # 目录设置
    profiles_current: str = ""
    profiles_default: str = ""
    profiles_history: List[str] = field(default_factory=list)

    # ZPM 界面语言
    language: str = "zh_CN"

    # 窗口设置
    window_size: Dict[str, int] = field(default_factory=lambda: {"width": 800, "height": 600})
    window_position: Dict[str, int] = field(default_factory=lambda: {"x": -1, "y": -1})

    # 项目备注
    project_notes: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "zotero_install_dir": self.zotero_install_dir,
            "profiles_current": self.profiles_current,
            "profiles_default": self.profiles_default,
            "profiles_history": self.profiles_history,
            "language": self.language,
            "window_size": self.window_size,
            "window_position": self.window_position,
            "project_notes": self.project_notes
        }

    @classmethod
    def from_dict(cls, data: dict) -> "AppConfig":
        return cls(
            zotero_install_dir=data.get("zotero_install_dir", ""),
            profiles_current=data.get("profiles_current", ""),
            profiles_default=data.get("profiles_default", ""),
            profiles_history=data.get("profiles_history", []),
            language=data.get("language", "zh_CN"),
            window_size=data.get("window_size", {"width": 800, "height": 600}),
            window_position=data.get("window_position", {"x": -1, "y": -1}),
            project_notes=data.get("project_notes", {})
        )
# -*- coding: utf-8 -*-
"""
配置数据模型
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional


@dataclass
class AppConfig:
    """应用程序配置"""

    # Zotero 设置
    zotero_version: str = ""              # 用户手动输入的版本号
    zotero_install_dir: str = ""          # Zotero 安装目录

    # 目录设置
    templates_root: str = ""              # 模板根目录
    profiles_current: str = ""            # 当前 Profiles 目录
    profiles_default: str = ""            # 默认 Profiles 目录
    profiles_history: List[str] = field(default_factory=list)

    # 界面设置
    language: str = "zh_CN"
    window_size: Dict[str, int] = field(default_factory=lambda: {"width": 800, "height": 600})
    window_position: Dict[str, int] = field(default_factory=lambda: {"x": -1, "y": -1})

    # 新建项目默认选项
    auto_create_shortcut: bool = True

    def to_dict(self) -> dict:
        return {
            "zotero_version": self.zotero_version,
            "zotero_install_dir": self.zotero_install_dir,
            "templates_root": self.templates_root,
            "profiles_current": self.profiles_current,
            "profiles_default": self.profiles_default,
            "profiles_history": self.profiles_history,
            "language": self.language,
            "window_size": self.window_size,
            "window_position": self.window_position,
            "auto_create_shortcut": self.auto_create_shortcut
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
            window_size=data.get("window_size", {"width": 800, "height": 600}),
            window_position=data.get("window_position", {"x": -1, "y": -1}),
            auto_create_shortcut=data.get("auto_create_shortcut", True)
        )
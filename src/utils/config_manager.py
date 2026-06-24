# -*- coding: utf-8 -*-
"""
配置管理器
"""

import json
from pathlib import Path
from typing import List, Optional

from models.config import AppConfig


class ConfigManager:
    CONFIG_FILE_NAME = ".zpl_config.json"

    def __init__(self):
        self.config_path = Path.home() / self.CONFIG_FILE_NAME
        self._config = self._load()

    def _load(self) -> AppConfig:
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return AppConfig.from_dict(data)
            except:
                pass
        return AppConfig()

    def save(self):
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self._config.to_dict(), f, ensure_ascii=False, indent=2)
        except:
            pass

    def get_config(self) -> AppConfig:
        return self._config

    # ---------- 便捷方法 ----------
    def get_zotero_version(self) -> str:
        return self._config.zotero_version
    def set_zotero_version(self, v: str):
        self._config.zotero_version = v
        self.save()

    def get_zotero_install_dir(self) -> str:
        return self._config.zotero_install_dir
    def set_zotero_install_dir(self, path: str):
        self._config.zotero_install_dir = path
        self.save()

    def get_templates_root(self) -> str:
        return self._config.templates_root
    def set_templates_root(self, path: str):
        self._config.templates_root = path
        self.save()

    def get_profiles_current(self) -> str:
        return self._config.profiles_current
    def set_profiles_current(self, path: str):
        self._config.profiles_current = path
        self.save()

    def get_profiles_default(self) -> str:
        return self._config.profiles_default
    def set_profiles_default(self, path: str):
        self._config.profiles_default = path
        self.save()

    def get_profiles_history(self) -> List[str]:
        return self._config.profiles_history
    def add_to_history(self, path: str):
        history = self._config.profiles_history
        if path in history:
            history.remove(path)
        history.insert(0, path)
        if len(history) > 20:
            history = history[:20]
        self.save()

    def get_language(self) -> str:
        return self._config.language
    def set_language(self, lang: str):
        self._config.language = lang
        self.save()

    def get_default_language(self) -> str:
        return self._config.default_language
    def set_default_language(self, lang: str):
        self._config.default_language = lang
        self.save()

    def get_creation_method(self) -> str:
        return self._config.creation_method
    def set_creation_method(self, method: str):
        if method in ["auto", "template", "native"]:
            self._config.creation_method = method
            self.save()

    def get_window_size(self) -> tuple:
        return (self._config.window_size.get("width", 800),
                self._config.window_size.get("height", 600))
    def set_window_size(self, w: int, h: int):
        self._config.window_size = {"width": w, "height": h}
        self.save()

    def get_window_position(self) -> tuple:
        return (self._config.window_position.get("x", -1),
                self._config.window_position.get("y", -1))
    def set_window_position(self, x: int, y: int):
        self._config.window_position = {"x": x, "y": y}
        self.save()

    def get_auto_create_shortcut(self) -> bool:
        return self._config.auto_create_shortcut
    def set_auto_create_shortcut(self, val: bool):
        self._config.auto_create_shortcut = val
        self.save()

    def get_project_note(self, project_name: str) -> str:
        return self._config.project_notes.get(project_name, "")
    def set_project_note(self, project_name: str, note: str):
        self._config.project_notes[project_name] = note
        self.save()

    def remove_project_note(self, project_name: str):
        if project_name in self._config.project_notes:
            del self._config.project_notes[project_name]
            self.save()
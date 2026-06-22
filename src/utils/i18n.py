# -*- coding: utf-8 -*-
"""
国际化引擎
"""

import json
from pathlib import Path
from typing import Dict


class I18n:
    """国际化翻译管理类（单例模式）"""

    _instance = None
    _current_lang = "zh_CN"
    _translations: Dict[str, Dict[str, str]] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_translations()
        return cls._instance

    def _load_translations(self):
        json_path = Path(__file__).parent.parent / "resources" / "languages.json"
        if json_path.exists():
            try:
                with open(json_path, "r", encoding="utf-8") as f:
                    self._translations = json.load(f)
                return
            except Exception:
                pass
        self._translations = self._get_default_translations()

    def set_language(self, lang_code: str):
        if lang_code in self._translations:
            self._current_lang = lang_code

    def get_language(self) -> str:
        return self._current_lang

    def tr(self, key: str, **kwargs) -> str:
        lang_dict = self._translations.get(self._current_lang, self._translations.get("zh_CN", {}))
        text = lang_dict.get(key, key)
        if kwargs:
            try:
                text = text.format(**kwargs)
            except (KeyError, ValueError):
                pass
        return text

    def get_all_languages(self) -> list:
        return list(self._translations.keys())

    def _get_default_translations(self) -> Dict[str, Dict[str, str]]:
        # 简化的 fallback，实际使用 languages.json
        return {
            "zh_CN": {
                "app_title": "Zotero 项目启动器",
                "btn_refresh": "🔄 刷新列表",
                "btn_new": "➕ 新建项目",
                "btn_preferences": "⚙ 偏好设置",
                "btn_launch": "▶ 启动",
                "menu_file": "文件(&F)",
                "menu_edit": "编辑(&E)",
                "menu_help": "帮助(&H)",
                # ... 其他键值将在 languages.json 中完整定义
            },
            "en_US": {
                "app_title": "Zotero Project Launcher",
                "btn_refresh": "🔄 Refresh",
                "btn_new": "➕ New Project",
                "btn_preferences": "⚙ Preferences",
                "btn_launch": "▶ Launch",
                "menu_file": "File(&F)",
                "menu_edit": "Edit(&E)",
                "menu_help": "Help(&H)",
                # ...
            }
        }
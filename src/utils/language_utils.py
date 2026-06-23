# -*- coding: utf-8 -*-
"""
语言工具：读写 prefs.js 中的 intl.locale.requested
"""

import re
from pathlib import Path
from typing import Optional


def get_prefs_path(profile_dir: str) -> Path:
    """获取 prefs.js 路径"""
    return Path(profile_dir) / 'prefs.js'


def read_language(profile_dir: str) -> str:
    """
    从 prefs.js 读取语言设置
    返回: 'zh-CN', 'en-US', '' (空字符串表示跟随系统), 或 None
    """
    prefs_path = get_prefs_path(profile_dir)
    if not prefs_path.exists():
        print(f"[DEBUG] read_language: prefs.js not found at {prefs_path}")
        return None

    try:
        with open(prefs_path, 'r', encoding='utf-8') as f:
            content = f.read()
        match = re.search(r'user_pref\s*\(\s*"intl\.locale\.requested"\s*,\s*"([^"]*)"\s*\)', content)
        if match:
            lang = match.group(1)
            print(f"[DEBUG] read_language: found language '{lang}'")
            return lang
        else:
            print("[DEBUG] read_language: intl.locale.requested not found")
            return None
    except Exception as e:
        print(f"[ERROR] read_language failed: {e}")
        return None


def write_language(profile_dir: str, lang_code: str) -> bool:
    """
    修改 prefs.js 中的语言设置
    lang_code: 'zh-CN', 'en-US', '' (空字符串表示跟随系统)
    """
    print(f"[DEBUG] write_language called with profile_dir={profile_dir}, lang_code='{lang_code}'")
    prefs_path = get_prefs_path(profile_dir)
    if not prefs_path.exists():
        print(f"[ERROR] prefs.js not found at {prefs_path}")
        return False

    try:
        with open(prefs_path, 'r', encoding='utf-8') as f:
            content = f.read()
        print(f"[DEBUG] read prefs.js, length={len(content)}")

        # 准备要写入的行
        # 同时写入 intl.locale.matchOS = false 以确保语言设置生效
        lines_to_add = [
            f'user_pref("intl.locale.matchOS", false);',
            f'user_pref("intl.locale.requested", "{lang_code}");'
        ]

        # 检查是否已有 intl.locale.requested
        pattern_requested = r'user_pref\s*\(\s*"intl\.locale\.requested"\s*,\s*"[^"]*"\s*\)'
        if re.search(pattern_requested, content):
            content = re.sub(pattern_requested, lines_to_add[1], content)
            print("[DEBUG] Replaced existing intl.locale.requested")
        else:
            content = content.rstrip() + '\n' + lines_to_add[1] + '\n'
            print("[DEBUG] Appended intl.locale.requested")

        # 处理 intl.locale.matchOS
        pattern_matchos = r'user_pref\s*\(\s*"intl\.locale\.matchOS"\s*,\s*(true|false)\s*\)'
        if re.search(pattern_matchos, content):
            content = re.sub(pattern_matchos, lines_to_add[0], content)
            print("[DEBUG] Replaced existing intl.locale.matchOS")
        else:
            content = content.rstrip() + '\n' + lines_to_add[0] + '\n'
            print("[DEBUG] Appended intl.locale.matchOS")

        # 写回文件
        with open(prefs_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"[DEBUG] Successfully wrote language settings to {prefs_path}")
        return True
    except Exception as e:
        print(f"[ERROR] write_language failed: {e}")
        return False


def get_display_language(lang_code: str, ui_lang: str = 'zh_CN') -> str:
    """
    将语言代码转换为显示文字
    ui_lang: 当前界面语言（zh_CN / en_US）
    """
    if ui_lang == 'zh_CN':
        mapping = {
            'zh-CN': '中文',
            'en-US': '英文',
            'zh-TW': '繁体中文',
            '': '系统',
            None: '默认'
        }
    else:
        mapping = {
            'zh-CN': 'Chinese',
            'en-US': 'English',
            'zh-TW': 'Traditional Chinese',
            '': 'System',
            None: 'Default'
        }
    return mapping.get(lang_code, mapping.get(None))
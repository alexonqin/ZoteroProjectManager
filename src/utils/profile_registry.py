# -*- coding: utf-8 -*-
"""
系统 profiles.ini 管理工具
"""

import os
import configparser
from pathlib import Path
from typing import List, Dict, Optional


def get_profiles_ini_path() -> Path:
    if os.name != 'nt':
        return None
    appdata = os.getenv('APPDATA')
    if not appdata:
        return None
    path_v7 = Path(appdata) / 'Zotero' / 'Zotero' / 'profiles.ini'
    if path_v7.exists():
        return path_v7
    path_v6 = Path(appdata) / 'Zotero' / 'Profiles' / 'profiles.ini'
    if path_v6.exists():
        return path_v6
    path_v7.parent.mkdir(parents=True, exist_ok=True)
    return path_v7


def read_profiles() -> List[Dict[str, str]]:
    ini_path = get_profiles_ini_path()
    if not ini_path or not ini_path.exists():
        return []
    config = configparser.ConfigParser()
    config.optionxform = str
    config.read(str(ini_path), encoding='utf-8')
    profiles = []
    for section in config.sections():
        if section.startswith('Profile'):
            name = config.get(section, 'Name', fallback='')
            path = config.get(section, 'Path', fallback='')
            is_default = config.getboolean(section, 'Default', fallback=False)
            if name and path:
                profiles.append({'name': name, 'path': path, 'default': is_default})
    return profiles


def find_profile(name: str) -> Optional[Dict[str, str]]:
    for p in read_profiles():
        if p['name'] == name:
            return p
    return None


def register_profile(name: str, profile_path: str) -> bool:
    ini_path = get_profiles_ini_path()
    if not ini_path:
        return False
    ini_path.parent.mkdir(parents=True, exist_ok=True)
    config = configparser.ConfigParser()
    config.optionxform = str
    if ini_path.exists():
        config.read(str(ini_path), encoding='utf-8')
    for section in config.sections():
        if section.startswith('Profile'):
            if config.get(section, 'Name', fallback='') == name:
                config.set(section, 'Path', profile_path)
                config.set(section, 'IsRelative', '0')
                with open(ini_path, 'w', encoding='utf-8') as f:
                    config.write(f, space_around_delimiters=False)
                return True
    nums = []
    for section in config.sections():
        if section.startswith('Profile'):
            try:
                nums.append(int(section.replace('Profile', '')))
            except:
                pass
    next_num = 1
    while next_num in nums:
        next_num += 1
    section = f'Profile{next_num}'
    config[section] = {'Name': name, 'Path': profile_path, 'IsRelative': '0', 'Default': '0'}
    with open(ini_path, 'w', encoding='utf-8') as f:
        config.write(f, space_around_delimiters=False)
    return True


def unregister_profile(name: str) -> bool:
    ini_path = get_profiles_ini_path()
    if not ini_path or not ini_path.exists():
        return False
    config = configparser.ConfigParser()
    config.optionxform = str
    config.read(str(ini_path), encoding='utf-8')
    to_remove = None
    for section in config.sections():
        if section.startswith('Profile'):
            if config.get(section, 'Name', fallback='') == name:
                to_remove = section
                break
    if to_remove:
        config.remove_section(to_remove)
        with open(ini_path, 'w', encoding='utf-8') as f:
            config.write(f, space_around_delimiters=False)
        return True
    return False


def set_default_profile(name: str) -> bool:
    ini_path = get_profiles_ini_path()
    if not ini_path or not ini_path.exists():
        return False
    config = configparser.ConfigParser()
    config.optionxform = str
    config.read(str(ini_path), encoding='utf-8')
    found = False
    for section in config.sections():
        if section.startswith('Profile'):
            current_name = config.get(section, 'Name', fallback='')
            if current_name == name:
                config.set(section, 'Default', '1')
                found = True
            else:
                config.set(section, 'Default', '0')
    if not found:
        return False
    if 'General' not in config:
        config['General'] = {}
    config.set('General', 'StartWithLastProfile', '1')
    with open(ini_path, 'w', encoding='utf-8') as f:
        config.write(f, space_around_delimiters=False)
    return True


def update_profile_name(old_name: str, new_name: str, new_path: str) -> bool:
    """更新profiles.ini中的Profile名称和路径"""
    ini_path = get_profiles_ini_path()
    if not ini_path or not ini_path.exists():
        return False
    config = configparser.ConfigParser()
    config.optionxform = str
    config.read(str(ini_path), encoding='utf-8')
    found = False
    for section in config.sections():
        if section.startswith('Profile'):
            if config.get(section, 'Name', fallback='') == old_name:
                config.set(section, 'Name', new_name)
                config.set(section, 'Path', new_path)
                # 保持IsRelative=0
                config.set(section, 'IsRelative', '0')
                found = True
                break
    if not found:
        return False
    with open(ini_path, 'w', encoding='utf-8') as f:
        config.write(f, space_around_delimiters=False)
    return True
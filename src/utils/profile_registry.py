# -*- coding: utf-8 -*-
"""
系统 profiles.ini 管理工具
用于注册/注销/查询 Zotero Profile
"""

import os
import configparser
from pathlib import Path
from typing import List, Dict, Optional


def get_profiles_ini_path() -> Path:
    """
    获取系统 profiles.ini 文件路径
    
    Zotero 7+ 路径: %APPDATA%\Zotero\Zotero\profiles.ini
    Zotero 6 路径:   %APPDATA%\Zotero\Profiles\profiles.ini
    """
    if os.name != 'nt':
        return None
    
    appdata = os.getenv('APPDATA')
    if not appdata:
        return None
    
    # Zotero 7+ 路径（优先）
    path_v7 = Path(appdata) / 'Zotero' / 'Zotero' / 'profiles.ini'
    if path_v7.exists():
        return path_v7
    
    # Zotero 6 路径（备选）
    path_v6 = Path(appdata) / 'Zotero' / 'Profiles' / 'profiles.ini'
    if path_v6.exists():
        return path_v6
    
    # 如果都不存在，默认返回 Zotero 7 路径
    path_v7.parent.mkdir(parents=True, exist_ok=True)
    return path_v7


def read_profiles() -> List[Dict[str, str]]:
    """读取 profiles.ini，返回所有 Profile 信息列表"""
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
                profiles.append({
                    'name': name,
                    'path': path,
                    'default': is_default
                })
    return profiles


def find_profile(name: str) -> Optional[Dict[str, str]]:
    """根据名称查找 Profile"""
    for p in read_profiles():
        if p['name'] == name:
            return p
    return None


def register_profile(name: str, profile_path: str) -> bool:
    """
    在 profiles.ini 中注册新 Profile
    profile_path 应为绝对路径
    """
    ini_path = get_profiles_ini_path()
    if not ini_path:
        return False

    ini_path.parent.mkdir(parents=True, exist_ok=True)

    config = configparser.ConfigParser()
    config.optionxform = str
    if ini_path.exists():
        config.read(str(ini_path), encoding='utf-8')

    # 检查是否已存在同名 Profile
    for section in config.sections():
        if section.startswith('Profile'):
            if config.get(section, 'Name', fallback='') == name:
                config.set(section, 'Path', profile_path)
                config.set(section, 'IsRelative', '0')
                with open(ini_path, 'w', encoding='utf-8') as f:
                    config.write(f, space_around_delimiters=False)
                return True

    # 找到下一个可用的编号
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
    config[section] = {
        'Name': name,
        'Path': profile_path,
        'IsRelative': '0',
        'Default': '0'
    }

    with open(ini_path, 'w', encoding='utf-8') as f:
        config.write(f, space_around_delimiters=False)
    return True


def unregister_profile(name: str) -> bool:
    """从 profiles.ini 中移除 Profile"""
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
    """
    将指定 Profile 设为默认，其他所有 Profile 设为非默认
    同时设置 StartWithLastProfile=1
    """
    ini_path = get_profiles_ini_path()
    if not ini_path or not ini_path.exists():
        return False

    config = configparser.ConfigParser()
    config.optionxform = str
    config.read(str(ini_path), encoding='utf-8')

    # 找到对应的 Profile 区块并设置 Default
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

    # 设置 General 选项
    if 'General' not in config:
        config['General'] = {}
    config.set('General', 'StartWithLastProfile', '1')

    with open(ini_path, 'w', encoding='utf-8') as f:
        config.write(f, space_around_delimiters=False)
    return True
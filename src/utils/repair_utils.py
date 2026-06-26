# -*- coding: utf-8 -*-
"""
启动修复核心逻辑
"""

import configparser
import shutil
from datetime import datetime
from pathlib import Path

from utils.profile_registry import register_profile, get_profiles_ini_path
from utils.config_manager import ConfigManager


def repair_launch(config_mgr: ConfigManager):
    """
    执行启动修复：备份、清理、重新注册所有项目
    返回: (成功, 消息, 备份路径)
    """
    # 获取 profiles.ini 路径
    ini_path = get_profiles_ini_path()
    if not ini_path:
        return False, "无法定位 profiles.ini", None

    # 获取项目库目录
    projects_dir = config_mgr.get_profiles_current()
    if not projects_dir or not Path(projects_dir).exists():
        return False, "项目库目录不存在或未设置", None

    # 备份
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = ini_path.parent / f"profiles.ini.backup_{timestamp}"
    try:
        shutil.copy2(ini_path, backup_path)
    except Exception as e:
        return False, f"备份失败: {e}", None

    # 清理所有用户 Profile 条目（保留 Profile0 和 General）
    config = configparser.ConfigParser()
    config.optionxform = str
    config.read(ini_path, encoding='utf-8')

    keep_sections = ['Profile0', 'General']
    sections_to_remove = [s for s in config.sections() if s not in keep_sections]
    for section in sections_to_remove:
        config.remove_section(section)

    # 保存清理后的文件
    try:
        with open(ini_path, 'w', encoding='utf-8') as f:
            config.write(f, space_around_delimiters=False)
    except Exception as e:
        return False, f"写入 profiles.ini 失败: {e}", backup_path

    # 重新注册所有项目
    projects = [d for d in Path(projects_dir).iterdir() if d.is_dir() and (d / "profiles").exists()]
    registered = 0
    for project_path in projects:
        if register_profile(project_path.name, str(project_path / "profiles")):
            registered += 1

    return True, registered, str(backup_path)
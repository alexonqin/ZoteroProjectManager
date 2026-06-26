# -*- coding: utf-8 -*-
"""
快捷方式修复核心逻辑
"""

from pathlib import Path

from controllers import ZoteroController
from utils.config_manager import ConfigManager


def repair_shortcuts(config_mgr: ConfigManager):
    """
    为缺失快捷方式的项目生成快捷方式
    返回: (created_count, skipped_count)
    """
    projects_dir = config_mgr.get_profiles_current()
    if not projects_dir or not Path(projects_dir).exists():
        raise Exception("项目库目录不存在或未设置")

    zotero_dir = config_mgr.get_zotero_install_dir()
    if not zotero_dir or not Path(zotero_dir).exists():
        raise Exception("Zotero 安装路径无效，请在偏好设置中设置")

    controller = ZoteroController(config_mgr)

    projects = [d for d in Path(projects_dir).iterdir() if d.is_dir() and (d / "profiles").exists()]

    created = 0
    skipped = 0

    for project_path in projects:
        project_name = project_path.name
        # 检查是否存在快捷方式
        pattern = f"{project_name} - Zotero*.lnk"
        existing = list(Path(projects_dir).glob(pattern))
        if existing:
            skipped += 1
            continue

        # 生成快捷方式
        success, msg = controller.create_shortcut_in_library(
            str(project_path),
            project_name,
            zotero_dir,
            str(projects_dir)
        )
        if success:
            created += 1
        else:
            # 如果生成失败，也计入跳过（避免用户困惑）
            skipped += 1

    return created, skipped
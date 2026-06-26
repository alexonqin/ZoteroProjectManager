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
    # ===== 调试信息开始 =====
    print("=" * 60)
    print("[DEBUG] repair_shortcuts 被调用")
    # ===== 获取并打印项目库目录 =====
    projects_dir = config_mgr.get_profiles_current()
    print(f"[DEBUG] projects_dir (原始) = '{projects_dir}'")
    if not projects_dir:
        raise Exception("项目库目录未设置")
    projects_path = Path(projects_dir)
    print(f"[DEBUG] projects_path (解析后) = '{projects_path.resolve()}'")
    print(f"[DEBUG] projects_path.exists() = {projects_path.exists()}")
    if not projects_path.exists():
        raise Exception(f"项目库目录不存在: {projects_path}")

    zotero_dir = config_mgr.get_zotero_install_dir()
    print(f"[DEBUG] zotero_dir = '{zotero_dir}'")
    if not zotero_dir or not Path(zotero_dir).exists():
        raise Exception("Zotero 安装路径无效，请在偏好设置中设置")

    controller = ZoteroController(config_mgr)

    # 列出所有有效项目
    projects = [d for d in projects_path.iterdir() if d.is_dir() and (d / "profiles").exists()]
    print(f"[DEBUG] 找到 {len(projects)} 个有效项目")
    for p in projects:
        print(f"  - {p.name}")

    created = 0
    skipped = 0

    for project_path in projects:
        project_name = project_path.name
        pattern = f"{project_name} - Zotero*.lnk"
        existing = list(projects_path.glob(pattern))
        print(f"[DEBUG] 项目: {project_name}, 搜索模式: {pattern}")
        if existing:
            print(f"  [跳过] 已存在 {len(existing)} 个快捷方式:")
            for lnk in existing:
                print(f"    - {lnk.name}")
            skipped += 1
            continue

        # 生成快捷方式
        print(f"  [生成] 正在创建快捷方式...")
        success, msg = controller.create_shortcut_in_library(
            str(project_path),
            project_name,
            zotero_dir,
            str(projects_path)
        )
        if success:
            print(f"  [成功] {msg}")
            created += 1
        else:
            print(f"  [失败] {msg}")
            skipped += 1

    print(f"[DEBUG] 结果: 新增 {created} 个，跳过 {skipped} 个")
    print("=" * 60)
    return created, skipped
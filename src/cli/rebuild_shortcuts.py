#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
为项目库中缺失快捷方式的项目自动生成 .lnk 文件（CLI）。
用法：python -m src.cli.rebuild_shortcuts [项目库目录]
如果未指定，则从 ~/.zpl_config.json 读取。
仅当项目对应快捷方式不存在时才会生成，已存在则跳过。
"""

import json
import sys
from pathlib import Path

# 使用相对导入
from ..utils.config_manager import ConfigManager
from ..controllers import ZoteroController

ZPL_CONFIG_PATH = Path.home() / ".zpl_config.json"


def get_projects_dir_from_config():
    """从 ZPL 配置文件获取项目库目录"""
    if ZPL_CONFIG_PATH.exists():
        try:
            with open(ZPL_CONFIG_PATH, 'r', encoding='utf-8') as f:
                config = json.load(f)
            profiles_current = config.get("profiles_current")
            if profiles_current:
                return Path(profiles_current)
        except Exception as e:
            print(f"⚠️ 读取 ZPL 配置文件失败: {e}")
    return None


def get_projects_dir():
    """从命令行参数或 ZPL 配置文件获取项目库目录"""
    if len(sys.argv) > 1:
        return Path(sys.argv[1])

    config_path = get_projects_dir_from_config()
    if config_path:
        return config_path

    print("⚠️ 未在 ZPL 配置中找到项目库目录。")
    user_input = input("请输入项目库目录路径（或按 Enter 退出）: ").strip()
    if not user_input:
        sys.exit(0)
    return Path(user_input)


def main():
    config_mgr = ConfigManager()
    controller = ZoteroController(config_mgr)

    projects_dir = get_projects_dir()
    if not projects_dir.exists():
        print(f"❌ 错误：项目库目录不存在: {projects_dir}")
        sys.exit(1)

    print(f"📁 项目库目录: {projects_dir}")

    # 检查 Zotero 安装路径是否有效
    zotero_dir = config_mgr.get_zotero_install_dir()
    if not zotero_dir or not Path(zotero_dir).exists():
        print("❌ 错误：Zotero 安装路径无效，请在 ZPL 偏好设置中先设置。")
        sys.exit(1)

    # 查找所有有效项目（包含 profiles 子目录）
    projects = []
    for d in projects_dir.iterdir():
        if d.is_dir() and (d / "profiles").exists():
            projects.append(d)

    if not projects:
        print("⚠️ 未找到任何有效项目（需包含 profiles 子目录）")
        sys.exit(0)

    print(f"📁 发现 {len(projects)} 个项目")

    created = 0
    skipped = 0

    for project_path in projects:
        project_name = project_path.name
        # 检查是否存在快捷方式（匹配任意编号）
        pattern = f"{project_name} - Zotero*.lnk"
        existing = list(projects_dir.glob(pattern))
        if existing:
            print(f"  ⏭️ 跳过 {project_name}：已存在 {len(existing)} 个快捷方式")
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
            print(f"  ✅ 已生成: {project_name} → {msg}")
            created += 1
        else:
            print(f"  ❌ 生成失败: {project_name} → {msg}")

    print(f"\n🎉 完成！新增 {created} 个快捷方式，跳过 {skipped} 个已有快捷方式。")


if __name__ == "__main__":
    main()
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ZPM 项目 Profile 修复脚本（CLI）
用法：python -m src.cli.fix_profiles [项目库目录]
如果未指定项目库目录，则从 ~/.ZPM_config.json 读取当前项目库路径。
"""

import configparser
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path

# 使用相对导入（因为 cli 是 src 的子包）
from ..utils.profile_registry import register_profile, get_profiles_ini_path
from ..utils.config_manager import ConfigManager

ZPM_CONFIG_PATH = Path.home() / ".ZPM_config.json"


def get_projects_dir_from_config():
    """从 ZPM 配置文件获取项目库目录"""
    if ZPM_CONFIG_PATH.exists():
        try:
            with open(ZPM_CONFIG_PATH, 'r', encoding='utf-8') as f:
                config = json.load(f)
            profiles_current = config.get("profiles_current")
            if profiles_current:
                return Path(profiles_current)
        except Exception as e:
            print(f"⚠️ 读取 ZPM 配置文件失败: {e}")
    return None


def get_projects_dir():
    """从命令行参数或 ZPM 配置文件获取项目库目录"""
    if len(sys.argv) > 1:
        return Path(sys.argv[1])

    config_path = get_projects_dir_from_config()
    if config_path:
        return config_path

    print("⚠️ 未在 ZPM 配置中找到项目库目录。")
    user_input = input("请输入项目库目录路径（或按 Enter 退出）: ").strip()
    if not user_input:
        sys.exit(0)
    return Path(user_input)


def backup_profiles_ini(ini_path):
    """备份 profiles.ini 到同目录下带时间戳的文件"""
    if not ini_path.exists():
        print(f"⚠️ 警告: {ini_path} 不存在，无需备份")
        return None
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = ini_path.parent / f"profiles.ini.backup_{timestamp}"
    shutil.copy2(ini_path, backup_path)
    print(f"✅ 已备份到: {backup_path}")
    return backup_path


def clean_profiles_ini(ini_path):
    """清除除 Profile0 和 General 之外的所有 Profile 节"""
    config = configparser.ConfigParser()
    config.optionxform = str
    config.read(ini_path, encoding='utf-8')

    keep_sections = ['Profile0', 'General']
    sections_to_remove = [s for s in config.sections() if s not in keep_sections]

    if not sections_to_remove:
        print("⚠️ 未发现需要清除的用户 Profile 条目")
        return

    for section in sections_to_remove:
        config.remove_section(section)
        print(f"  移除: [{section}]")

    with open(ini_path, 'w', encoding='utf-8') as f:
        config.write(f, space_around_delimiters=False)
    print("✅ 已清除所有用户 Profile 条目")


def main():
    ini_path = get_profiles_ini_path()
    if not ini_path:
        print("❌ 错误：无法定位 profiles.ini，请检查 APPDATA 环境变量")
        sys.exit(1)

    print(f"📁 profiles.ini 位置: {ini_path}")

    projects_dir = get_projects_dir()
    if not projects_dir.exists():
        print(f"❌ 错误：项目库目录不存在: {projects_dir}")
        sys.exit(1)

    print(f"📁 项目库目录: {projects_dir}")

    backup_path = backup_profiles_ini(ini_path)
    if backup_path is None:
        print("❌ 备份失败，终止操作")
        sys.exit(1)

    clean_profiles_ini(ini_path)

    projects = [d for d in projects_dir.iterdir() if d.is_dir() and (d / "profiles").exists()]
    print(f"\n📁 发现 {len(projects)} 个项目目录")

    success_count = 0
    for project_path in projects:
        profiles_subdir = project_path / "profiles"
        if register_profile(project_path.name, str(profiles_subdir)):
            print(f"  ✅ 已注册: {project_path.name}")
            success_count += 1
        else:
            print(f"  ❌ 注册失败: {project_path.name}")

    print(f"\n🎉 修复完成！成功注册 {success_count} 个项目")
    print("💡 请重启 ZPM，然后双击项目测试启动。")
    print(f"💡 如出现问题，可从备份恢复: {backup_path}")


if __name__ == "__main__":
    main()
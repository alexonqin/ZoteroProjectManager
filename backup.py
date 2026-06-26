#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Zotero Project Launcher 项目备份脚本
用法: python backup.py
备份文件保存在 ../ZoteroProjectLauncher_backup/{项目名称}_yyyymmdd_HHMM.zip
备份内包含顶层文件夹 {项目名称}，解压后目录结构完整。
"""

import os
import zipfile
import logging
from pathlib import Path
from datetime import datetime

# ==================== 排除规则 ====================
EXCLUDE_DIRS = {
    '__pycache__',
    '.git',
    '.vscode',
    '.idea',
    '.pytest_cache',
    '.mypy_cache',
    '.tox',
    '.eggs',
    'venv',
    'env',
    'build',
    'dist',
    '.github',          # GitHub 工作流（不必要）
}

EXCLUDE_SUFFIXES = {
    '.pyc', '.pyo', '.pyd', '.exe', '.dll', '.so',
    '.log', '.tmp', '.swp', '.swo',
    '.zip', '.7z', '.rar', '.tar', '.gz',
    '.lnk',   # Windows 快捷方式
}

EXCLUDE_FILES = {
    'backup.py',           # 本脚本自身
    '.DS_Store',
    'Thumbs.db',
}

# ==================== 日志配置 ====================
def setup_logger(log_dir: Path) -> logging.Logger:
    """配置日志：同时输出到控制台和文件"""
    log_file = log_dir / 'backup.log'
    logger = logging.getLogger('Backup')
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        console.setFormatter(formatter)
        logger.addHandler(console)
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    return logger

# ==================== 排除判断 ====================
def should_exclude(path: Path, project_root: Path) -> bool:
    """判断文件或目录是否应该被排除"""
    if path.is_dir():
        rel_path = path.relative_to(project_root).as_posix()
        for exclude in EXCLUDE_DIRS:
            if rel_path == exclude or rel_path.startswith(exclude + '/'):
                return True
        if path.name in EXCLUDE_DIRS:
            return True
    if path.is_file():
        if path.name in EXCLUDE_FILES:
            return True
        if path.suffix.lower() in EXCLUDE_SUFFIXES:
            return True
        # 排除已有的备份 zip（项目根目录下的 zip）
        if path.suffix == '.zip' and path.name.startswith(project_root.name + '_'):
            return True
    return False

# ==================== 获取项目名称 ====================
def get_project_name(project_root: Path) -> str:
    """获取项目根目录的名称"""
    name = project_root.name
    if not name:
        name = os.path.basename(os.getcwd())
    return name

# ==================== 备份主函数 ====================
def create_backup():
    project_root = Path(__file__).parent.resolve()
    project_name = get_project_name(project_root)
    backup_parent = project_root.parent / f'{project_name}_backup'
    backup_parent.mkdir(parents=True, exist_ok=True)

    logger = setup_logger(backup_parent)

    logger.info("========== 开始备份 ==========")
    logger.info(f"项目根目录: {project_root}")
    logger.info(f"项目名称: {project_name}")
    logger.info(f"备份目标目录: {backup_parent}")
    logger.info(f"排除目录: {sorted(EXCLUDE_DIRS)}")

    timestamp = datetime.now().strftime('%Y%m%d_%H%M')
    zip_name = f'{project_name}_{timestamp}.zip'
    zip_path = backup_parent / zip_name

    added_count = 0
    excluded_count = 0

    try:
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(project_root):
                current_dir = Path(root)
                # 原地修改 dirs 列表以跳过排除目录
                original_dirs = dirs.copy()
                dirs[:] = [d for d in dirs if not should_exclude(current_dir / d, project_root)]
                for d in original_dirs:
                    if d not in dirs:
                        excluded_count += 1
                        logger.debug(f"排除目录: {current_dir / d}")

                for file in files:
                    file_path = current_dir / file
                    if should_exclude(file_path, project_root):
                        excluded_count += 1
                        logger.debug(f"排除文件: {file_path}")
                        continue
                    rel_path = file_path.relative_to(project_root)
                    zip_rel_path = f"{project_name}/{rel_path.as_posix()}"
                    zipf.write(file_path, zip_rel_path)
                    added_count += 1
                    logger.debug(f"添加: {zip_rel_path}")

        logger.info(f"备份完成: {zip_path}")
        logger.info(f"统计: 添加 {added_count} 个文件, 排除 {excluded_count} 个")
        logger.info("========== 备份结束 ==========\n")

    except Exception as e:
        logger.error(f"备份失败: {e}", exc_info=True)
        raise

if __name__ == '__main__':
    create_backup()
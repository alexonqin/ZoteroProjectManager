# -*- coding: utf-8 -*-
"""
Profile 数据模型 - 代表一个项目
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class Profile:
    """项目数据模型"""

    name: str                    # 项目名称
    data_path: str               # data 目录路径
    profiles_path: str           # profiles 目录路径
    project_path: str            # 项目根目录路径

    @classmethod
    def from_project_path(cls, project_path: str) -> Optional["Profile"]:
        """从项目路径创建 Profile 对象"""
        p = Path(project_path)
        if not p.exists():
            return None

        data_dir = p / "data"
        profiles_dir = p / "profiles"

        if not data_dir.exists() or not profiles_dir.exists():
            return None

        return cls(
            name=p.name,
            data_path=str(data_dir),
            profiles_path=str(profiles_dir),
            project_path=str(p)
        )

    def get_item_count(self) -> int:
        """获取文献数量"""
        try:
            import sqlite3
            db_path = Path(self.data_path) / "zotero.sqlite"
            if db_path.exists():
                conn = sqlite3.connect(str(db_path))
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM items")
                count = cursor.fetchone()[0]
                conn.close()
                return count
        except Exception:
            pass
        return -1

    def get_plugin_count(self) -> int:
        """获取插件数量"""
        try:
            ext_path = Path(self.profiles_path) / "extensions"
            if ext_path.exists():
                return len([d for d in ext_path.iterdir() if d.is_dir()])
        except Exception:
            pass
        return 0

    def is_valid(self) -> bool:
        """检查项目是否有效"""
        if not Path(self.project_path).exists():
            return False
        if not Path(self.data_path).exists():
            return False
        if not Path(self.profiles_path).exists():
            return False
        if not (Path(self.data_path) / "zotero.sqlite").exists():
            return False
        return True
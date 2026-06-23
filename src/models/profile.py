# -*- coding: utf-8 -*-
"""
Profile 数据模型
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class Profile:
    name: str
    data_path: str
    profiles_path: str
    project_path: str

    @classmethod
    def from_project_path(cls, project_path: str) -> Optional["Profile"]:
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
        except:
            pass
        return -1

    def get_plugin_count(self) -> int:
        try:
            ext_path = Path(self.profiles_path) / "extensions"
            if ext_path.exists():
                return len([d for d in ext_path.iterdir() if d.is_dir()])
        except:
            pass
        return 0

    def get_size(self) -> int:
        """返回项目文件夹总大小（字节）"""
        try:
            total = 0
            for f in Path(self.project_path).rglob('*'):
                if f.is_file():
                    total += f.stat().st_size
            return total
        except:
            return 0

    def is_valid(self) -> bool:
        if not Path(self.project_path).exists():
            return False
        if not Path(self.data_path).exists():
            return False
        if not Path(self.profiles_path).exists():
            return False
        if not (Path(self.data_path) / "zotero.sqlite").exists():
            return False
        return True
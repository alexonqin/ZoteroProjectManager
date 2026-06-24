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
        """
        获取文献数量（排除附件、笔记、注释等非文献条目）
        与 Zotero 界面显示的父条目数量一致
        
        排除类型名称:
            - attachment: 附件 (PDF 等)
            - note: 笔记
            - annotation: 注释
        """
        try:
            import sqlite3
            db_path = Path(self.data_path) / "zotero.sqlite"
            if not db_path.exists():
                return -1

            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()

            # 动态查询要排除的 itemTypeID
            # 使用子查询，从 itemTypes 表中获取需要排除的类型 ID
            cursor.execute("""
                SELECT COUNT(*) FROM items 
                WHERE itemTypeID NOT IN (
                    SELECT itemTypeID FROM itemTypes 
                    WHERE typeName IN ('attachment', 'note', 'annotation')
                )
            """)
            count = cursor.fetchone()[0]
            conn.close()
            return count
        except Exception:
            # 如果查询失败（例如 itemTypes 表不存在或结构变化），回退到统计所有记录
            try:
                import sqlite3
                db_path = Path(self.data_path) / "zotero.sqlite"
                if not db_path.exists():
                    return -1
                conn = sqlite3.connect(str(db_path))
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM items")
                count = cursor.fetchone()[0]
                conn.close()
                return count
            except Exception:
                return -1

    def get_plugin_count(self) -> int:
        try:
            ext_path = Path(self.profiles_path) / "extensions"
            if ext_path.exists():
                return len([d for d in ext_path.iterdir() if d.is_dir()])
        except Exception:
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
        except Exception:
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
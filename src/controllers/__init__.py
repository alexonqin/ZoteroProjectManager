# Auto-generated __init__.py
# 该文件由 gen_init.py 自动生成，请勿手动编辑

from .base import BaseController
from .creator import CreatorMixin
from .launcher import LauncherMixin
from .shortcut import ShortcutMixin
from .manager import ManagerMixin

class ZoteroController(BaseController, CreatorMixin, LauncherMixin, ShortcutMixin, ManagerMixin):
    """
    统一的 Zotero 控制器，组合了所有功能混入。
    """
    pass

__all__ = ['ZoteroController']
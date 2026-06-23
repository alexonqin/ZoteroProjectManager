# -*- coding: utf-8 -*-
"""
回收站操作工具（Windows）
"""

import os
import sys
from pathlib import Path
from typing import Tuple


def move_to_recycle_bin(path: str) -> Tuple[bool, str]:
    """
    将文件或文件夹移动到系统回收站（Windows）
    
    Args:
        path: 要移动的路径
        
    Returns:
        (是否成功, 错误信息)
    """
    if sys.platform != "win32":
        return False, "仅支持 Windows 平台"
    
    if not os.path.exists(path):
        return False, "路径不存在"
    
    try:
        import win32com.client
        import pythoncom
        
        pythoncom.CoInitialize()
        shell = win32com.client.Dispatch("Shell.Application")
        # 创建文件夹对象
        folder = shell.Namespace(os.path.dirname(path))
        if folder is None:
            return False, "无法访问父目录"
        
        item = folder.Items().Item(os.path.basename(path))
        if item is None:
            return False, "无法获取项目对象"
        
        # 调用回收站操作
        item.InvokeVerbEx("delete")
        return True, ""
    except ImportError:
        # 尝试使用 win32file 的 SHFileOperation
        try:
            import win32file
            import win32con
            
            # 构建操作结构
            from ctypes import wintypes, windll, create_unicode_buffer
            # 使用 shell32.SHFileOperationW
            shfileop = windll.shell32.SHFileOperationW
            # 定义结构体
            class SHFILEOPSTRUCTW(ctypes.Structure):
                _fields_ = [
                    ("hwnd", wintypes.HWND),
                    ("wFunc", wintypes.UINT),
                    ("pFrom", wintypes.LPCWSTR),
                    ("pTo", wintypes.LPCWSTR),
                    ("fFlags", wintypes.UINT),
                    ("fAnyOperationsAborted", wintypes.BOOL),
                    ("hNameMappings", wintypes.LPVOID),
                    ("lpszProgressTitle", wintypes.LPCWSTR),
                ]
            
            import ctypes
            from ctypes import wintypes
            
            # 准备源路径（必须以双空字符结尾）
            src = path + '\0\0'
            op = SHFILEOPSTRUCTW()
            op.wFunc = 0x0003  # FO_DELETE
            op.pFrom = src
            op.fFlags = 0x0004 | 0x0040  # FOF_ALLOWUNDO | FOF_SILENT
            op.hwnd = None
            
            result = shfileop(ctypes.byref(op))
            if result != 0:
                return False, f"操作失败，错误码: {result}"
            return True, ""
        except Exception as e:
            return False, str(e)
    except Exception as e:
        return False, str(e)


def is_recycle_bin_available() -> bool:
    """检查回收站是否可用（总是返回 True，Windows 下）"""
    return sys.platform == "win32"
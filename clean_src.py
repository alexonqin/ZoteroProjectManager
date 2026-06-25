#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
清理 src/ 目录下的临时文件
- 删除所有 __init__.bak 文件
- 删除所有 __pycache__ 目录及其内容
- 删除所有 .pyc 和 .pyo 文件
只处理 src/ 目录，不影响其他位置。
"""

import os
import shutil

def clean_src():
    # 获取当前脚本所在目录（项目根目录）
    base_dir = os.path.dirname(os.path.abspath(__file__))
    src_dir = os.path.join(base_dir, 'src')

    if not os.path.isdir(src_dir):
        print(f"错误：找不到 src 目录（{src_dir}）")
        return

    print(f"开始清理: {src_dir}")

    # 收集所有需要删除的路径（先收集后删除，避免遍历时修改目录结构）
    files_to_delete = []
    dirs_to_delete = []

    for root, dirs, files in os.walk(src_dir):
        # 检查文件
        for file in files:
            file_path = os.path.join(root, file)
            # 删除 __init__.bak
            if file == '__init__.bak':
                files_to_delete.append(file_path)
            # 删除 .pyc / .pyo
            elif file.endswith(('.pyc', '.pyo')):
                files_to_delete.append(file_path)

        # 检查目录（__pycache__）
        for dir_name in dirs:
            if dir_name == '__pycache__':
                dir_path = os.path.join(root, dir_name)
                dirs_to_delete.append(dir_path)

    # 删除文件
    for f in files_to_delete:
        try:
            os.remove(f)
            print(f"已删除文件: {f}")
        except Exception as e:
            print(f"删除文件失败 {f}: {e}")

    # 删除目录（递归删除）
    for d in dirs_to_delete:
        try:
            shutil.rmtree(d)
            print(f"已删除目录: {d}")
        except Exception as e:
            print(f"删除目录失败 {d}: {e}")

    print("清理完成！")

if __name__ == '__main__':
    clean_src()
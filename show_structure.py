import os
import sys
from pathlib import Path

def write_and_print(text, file_handle):
    """同时输出到控制台和文件"""
    print(text)
    file_handle.write(text + "\n")

def print_tree(directory, file_handle, prefix="", ignore_dirs=None, is_root=True):
    """
    递归打印目录树形结构
    
    参数:
        directory: 要遍历的目录（Path 对象）
        file_handle: 文件句柄
        prefix: 前缀字符串（用于缩进）
        ignore_dirs: 忽略的目录名集合
        is_root: 是否为根目录
    """
    if ignore_dirs is None:
        ignore_dirs = {'.git', '__pycache__', '.idea', '.vscode', 'venv', 'env', 'node_modules'}
    
    if is_root:
        # 显示目录名称
        root_name = directory.name if directory.name else os.path.basename(os.getcwd())
        write_and_print(f"{root_name}/", file_handle)
    
    items = sorted([item for item in directory.iterdir() if item.name not in ignore_dirs])
    
    for i, item in enumerate(items):
        connector = "└── " if i == len(items) - 1 else "├── "
        write_and_print(prefix + connector + item.name, file_handle)
        
        if item.is_dir():
            extension = "    " if i == len(items) - 1 else "│   "
            print_tree(item, file_handle, prefix + extension, ignore_dirs, is_root=False)

def main():
    # 1. 解析命令行参数
    if len(sys.argv) >= 2:
        # 用户指定了路径
        input_path = sys.argv[1]
        root = Path(input_path)
        if not root.exists():
            print(f"❌ 错误: 路径不存在 - {input_path}")
            sys.exit(1)
        if not root.is_dir():
            print(f"❌ 错误: 不是有效的目录 - {input_path}")
            sys.exit(1)
    else:
        # 默认使用当前目录
        root = Path(__file__).parent
    
    # 2. 生成输出文件（放在当前工作目录，或指定位置）
    output_dir = Path.cwd()  # 输出到当前工作目录
    if not output_dir.exists():
        output_dir = Path.home()  # 如果当前目录不存在，使用用户主目录
    
    # 根据输入的目录名生成输出文件名
    dir_name = root.name if root.name else "root"
    output_file = output_dir / f"{dir_name}_structure.txt"
    
    # 3. 写入结构
    with open(output_file, "w", encoding="utf-8") as f:
        print_tree(root, f)
    
    # 4. 显示结果
    print(f"\n✅ 目录结构已保存至: {output_file}")
    print(f"📁 扫描目录: {root.absolute()}")

if __name__ == "__main__":
    main()
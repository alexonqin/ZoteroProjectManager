#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gen_init.py - ZPM 项目 __init__.py 自动生成器

用法：
    python gen_init.py               # 正常生成
    python gen_init.py --dry-run     # 预览
    python gen_init.py --no-backup   # 不备份
"""

import os
import ast
import argparse
import re
from pathlib import Path
from typing import List, Set, Optional

# ============================================================
# 配置
# ============================================================

STANDARD_PACKAGES = [
    "src/controllers",
    "src/models",
    "src/utils",
    "src/cli",           # ← 新增：CLI 工具包
]

ROOT_PACKAGES = [
    "src/views",
]

# 需要生成组合控制器的包
CONTROLLER_PACKAGES = [
    "src/controllers",   # 将生成 ZoteroController
]

EXCLUDE_DIRS = {
    "__pycache__", ".git", ".vscode", ".idea",
    "venv", "env", "build", "dist",
}

# ============================================================
# 核心函数
# ============================================================

def extract_public_definitions(filepath: Path) -> List[str]:
    """提取所有顶层公开定义（函数、类、变量）"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        tree = ast.parse(content)
    except Exception:
        return []

    names = []
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)) and not node.name.startswith('_'):
            names.append(node.name)
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and not target.id.startswith('_'):
                    names.append(target.id)
        elif isinstance(node, ast.AnnAssign):
            if isinstance(node.target, ast.Name) and not node.target.id.startswith('_'):
                names.append(node.target.id)
    return names


def discover_subpackages(root_dir: Path) -> List[Path]:
    """发现目录下的所有子包（包含.py文件的子目录）"""
    subpackages = []
    for item in root_dir.iterdir():
        if not item.is_dir():
            continue
        if item.name in EXCLUDE_DIRS:
            continue
        if list(item.glob("*.py")):
            subpackages.append(item)
    return sorted(subpackages, key=lambda x: x.name)


def generate_simple_init(target_dir: Path, dry_run: bool, backup: bool) -> bool:
    """为标准包生成 __init__.py（标准导入）"""
    target = Path(target_dir)
    if not target.is_dir():
        return False

    py_files = [f.stem for f in target.glob("*.py") if f.name != "__init__.py"]
    if not py_files:
        # 如果没有 .py 文件，生成一个空的 __init__.py（仅标记为包）
        content = "# Auto-generated __init__.py\n# 该文件由 gen_init.py 自动生成，请勿手动编辑\n\n__all__ = []"
        return _write_file(target / "__init__.py", content, dry_run, backup)

    all_names = []
    import_lines = []
    for mod in py_files:
        filepath = target / f"{mod}.py"
        defs = extract_public_definitions(filepath)
        if defs:
            import_lines.append(f"from .{mod} import {', '.join(defs)}")
            all_names.extend(defs)

    if not import_lines:
        # 有 .py 文件但无公开符号，生成空 __init__.py
        content = "# Auto-generated __init__.py\n# 该文件由 gen_init.py 自动生成，请勿手动编辑\n\n__all__ = []"
        return _write_file(target / "__init__.py", content, dry_run, backup)

    content = _build_content(import_lines, all_names)
    return _write_file(target / "__init__.py", content, dry_run, backup)


def generate_aggregate_init(root_dir: Path, dry_run: bool, backup: bool) -> bool:
    """为根包（如 views）生成聚合 __init__.py（导入子包符号）"""
    root = Path(root_dir)
    if not root.is_dir():
        return False

    subpackages = discover_subpackages(root)
    if not subpackages:
        return False

    # 先为每个子包生成标准 init
    for subpkg in subpackages:
        generate_simple_init(subpkg, dry_run, backup)

    # 构建聚合导入
    import_lines = []
    all_names = []

    # 主文件（如 main_window.py）
    main_files = ['main_window.py']
    for fname in main_files:
        main_file = root / fname
        if main_file.exists():
            defs = extract_public_definitions(main_file)
            if defs:
                import_lines.append(f"from .{main_file.stem} import {', '.join(defs)}")
                all_names.extend(defs)

    # 子包
    for subpkg in subpackages:
        init_file = subpkg / "__init__.py"
        if init_file.exists():
            sub_symbols = _get_exports(init_file)
            if sub_symbols:
                import_lines.append(f"from .{subpkg.name} import {', '.join(sub_symbols)}")
                all_names.extend(sub_symbols)

    if not import_lines:
        return False

    content = _build_content(import_lines, all_names)
    return _write_file(root / "__init__.py", content, dry_run, backup)


def _get_exports(init_file: Path) -> List[str]:
    """从 __init__.py 获取导出的符号（优先从 __all__ 中读取）"""
    try:
        import re
        content = init_file.read_text(encoding='utf-8')
        match = re.search(r"__all__\s*=\s*\[(.*?)\]", content, re.DOTALL)
        if match:
            all_content = match.group(1)
            return re.findall(r"['\"]([^'\"]+)['\"]", all_content)
        return extract_public_definitions(init_file)
    except Exception:
        return []


def _build_content(import_lines: List[str], all_names: List[str]) -> str:
    """构建 __init__.py 内容（注释 + 导入 + __all__）"""
    seen = set()
    unique_names = []
    for name in all_names:
        if name not in seen:
            seen.add(name)
            unique_names.append(name)

    lines = [
        "# Auto-generated __init__.py",
        "# 该文件由 gen_init.py 自动生成，请勿手动编辑",
        "",
        *import_lines,
        "",
        f"__all__ = {unique_names}"
    ]
    return "\n".join(lines)


def _write_file(path: Path, content: str, dry_run: bool, backup: bool) -> bool:
    """写入文件，支持备份和预览"""
    if dry_run:
        print(f"\n  📄 [预览] {path}")
        print("  " + "-" * 40)
        for line in content.split("\n"):
            print(f"  {line}")
        print("  " + "-" * 40)
        return True

    if backup and path.exists():
        backup_path = path.with_suffix(".bak")
        try:
            path.rename(backup_path)
        except Exception:
            pass

    try:
        path.write_text(content, encoding='utf-8')
        print(f"  ✅ 已生成: {path}")
        return True
    except Exception as e:
        print(f"  ❌ 写入失败: {e}")
        return False


# ============================================================
# 控制器组合类生成
# ============================================================
def generate_controller_init(target_dir: Path, dry_run: bool, backup: bool) -> bool:
    target = Path(target_dir)
    if not target.is_dir():
        return False

    # 固定顺序
    base_class = 'BaseController'
    mixin_order = ['CreatorMixin', 'LauncherMixin', 'ShortcutMixin', 'ManagerMixin']

    # 检查是否存在
    all_classes = [base_class] + mixin_order
    existing_classes = []
    for cls in all_classes:
        # 查找定义该类的模块
        module = _find_module_for_class(target, cls)
        if module:
            existing_classes.append((cls, module))
        else:
            print(f"  ⚠️ 未找到类 {cls}，跳过")

    if not existing_classes:
        return False

    import_lines = []
    for cls, mod in existing_classes:
        import_lines.append(f"from .{mod} import {cls}")

    class_names = [cls for cls, _ in existing_classes]

    class_lines = [
        "",
        f"class ZoteroController({', '.join(class_names)}):",
        '    """',
        '    统一的 Zotero 控制器，组合了所有功能混入。',
        '    """',
        "    pass"
    ]

    content_lines = [
        "# Auto-generated __init__.py",
        "# 该文件由 gen_init.py 自动生成，请勿手动编辑",
        "",
        *import_lines,
        *class_lines,
        "",
        "__all__ = ['ZoteroController']"
    ]

    content = "\n".join(content_lines)
    return _write_file(target / "__init__.py", content, dry_run, backup)


def _find_module_for_class(target_dir: Path, class_name: str) -> Optional[str]:
    """在目标目录下查找定义指定类的模块名（不含扩展名）"""
    for py_file in target_dir.glob("*.py"):
        if py_file.name == "__init__.py":
            continue
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read())
            for node in tree.body:
                if isinstance(node, ast.ClassDef) and node.name == class_name:
                    return py_file.stem
        except Exception:
            continue
    return None


def _class_to_snake(name: str) -> str:
    """将 CamelCase 转换为 snake_case"""
    s = re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()
    if s.endswith('_mixin'):
        s = s[:-6]
    elif s.endswith('_controller'):
        s = s[:-11]
    return s


# ============================================================
# 主函数
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="生成 ZPM 项目 __init__.py")
    parser.add_argument("--dry-run", action="store_true", help="预览模式")
    parser.add_argument("--no-backup", action="store_true", help="不备份")
    args = parser.parse_args()

    script_dir = Path(__file__).parent
    backup = not args.no_backup
    dry_run = args.dry_run

    print("=" * 60)
    print("  ZPM __init__.py 生成器")
    print("=" * 60)
    print(f"  模式: {'预览' if dry_run else '生成'}")
    print("-" * 60)

    # 1. 标准包
    print("\n📦 处理标准包:")
    for pkg in STANDARD_PACKAGES:
        target = script_dir / pkg
        if target.exists():
            print(f"\n📁 {pkg}/")
            generate_simple_init(target, dry_run, backup)
        else:
            print(f"\n📁 {pkg}/ ⚠️ 跳过")

    # 2. 聚合包（如 views）
    print("\n📦 处理聚合包:")
    for pkg in ROOT_PACKAGES:
        target = script_dir / pkg
        if target.exists():
            print(f"\n📁 {pkg}/")
            generate_aggregate_init(target, dry_run, backup)
        else:
            print(f"\n📁 {pkg}/ ⚠️ 跳过")

    # 3. 控制器特殊处理（生成组合类）
    print("\n📦 处理控制器组合包:")
    for pkg in CONTROLLER_PACKAGES:
        target = script_dir / pkg
        if target.exists():
            print(f"\n📁 {pkg}/")
            generate_controller_init(target, dry_run, backup)
        else:
            print(f"\n📁 {pkg}/ ⚠️ 跳过")

    print("\n" + "=" * 60)
    print("  完成！" if not dry_run else "  预览完成")
    print("=" * 60)


if __name__ == "__main__":
    main()
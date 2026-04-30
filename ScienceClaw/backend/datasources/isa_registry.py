"""RISC-V ISA 扩展注册表验证.

提供已批准的 RISC-V ISA 扩展集合和验证工具。
"""
from __future__ import annotations

from typing import Any


# 已批准的 RISC-V ISA 扩展集合（参考 design.md §5.3.1）
RATIFIED_EXTENSIONS: frozenset[str] = frozenset([
    # Zic* 扩展
    "Zicbom", "Zicbop", "Zicboz", "Zicfiss", "Zicfilp", "Zicntr", "Zicond",
    "Zifencei", "Zihintntl", "Zihintpause", "Zihpm", "Zimop", "Zicsr",
    # 其他 Z 扩展
    "Zawrs", "Zfa", "Zfh", "Zfhmin",
    # B 扩展（位操作）
    "Zba", "Zbb", "Zbc", "Zbkb", "Zbkc", "Zbkx", "Zbs",
    # K 扩展（加密）
    "Zkt", "Zknd", "Zkne", "Zknh", "Zksed", "Zksh",
    # V 扩展（向量）基础
    "Zvbb", "Zvbc", "Zvfh", "Zvfhmin", "Zvkb", "Zvkg", "Zvkned", "Zvknhb",
    "Zvksed", "Zvksh",
    # S 扩展（特权模式）
    "Sscofpmf", "Sstc", "Svinval", "Svnapot", "Svpbmt",
    # 主 V 扩展和向量元素宽度
    "V", "Zve32f", "Zve32x", "Zve64d", "Zve64f", "Zve64x",
])

# 扩展分类映射
EXTENSION_CATEGORIES: dict[str, str] = {
    "Zicbom": "cache", "Zicbop": "cache", "Zicboz": "cache",
    "Zicfiss": "security", "Zicfilp": "security",
    "Zicntr": "counter", "Zicond": "conditional",
    "Zifencei": "fence", "Zihintntl": "hint", "Zihintpause": "hint",
    "Zihpm": "counter", "Zimop": "misc", "Zicsr": "csr",
    "Zawrs": "wait", "Zfa": "float", "Zfh": "float", "Zfhmin": "float",
    "Zba": "bitmanip", "Zbb": "bitmanip", "Zbc": "bitmanip",
    "Zbkb": "crypto", "Zbkc": "crypto", "Zbkx": "crypto", "Zbs": "bitmanip",
    "Zkt": "crypto", "Zknd": "crypto", "Zkne": "crypto",
    "Zknh": "crypto", "Zksed": "crypto", "Zksh": "crypto",
    "Zvbb": "vector", "Zvbc": "vector", "Zvfh": "vector", "Zvfhmin": "vector",
    "Zvkb": "vector", "Zvkg": "vector", "Zvkned": "vector", "Zvknhb": "vector",
    "Zvksed": "vector", "Zvksh": "vector",
    "Sscofpmf": "supervisor", "Sstc": "supervisor", "Svinval": "supervisor",
    "Svnapot": "supervisor", "Svpbmt": "supervisor",
    "V": "vector", "Zve32f": "vector", "Zve32x": "vector",
    "Zve64d": "vector", "Zve64f": "vector", "Zve64x": "vector",
}


def validate_extension(extension: str) -> bool:
    """验证 ISA 扩展名是否已批准.

    Args:
        extension: ISA 扩展名，如 "Zicbom"

    Returns:
        如果扩展名在已批准列表中则返回 True
    """
    return extension in RATIFIED_EXTENSIONS


def get_extension_info(extension: str) -> dict[str, Any]:
    """获取 ISA 扩展的详细信息.

    Args:
        extension: ISA 扩展名

    Returns:
        包含扩展信息的字典，如 category, ratified, related
    """
    ext = extension
    if ext not in RATIFIED_EXTENSIONS:
        return {
            "name": extension,
            "ratified": False,
            "category": "unknown",
            "related": [],
        }

    category = EXTENSION_CATEGORIES.get(ext, "unknown")

    related = [
        e for e in RATIFIED_EXTENSIONS
        if EXTENSION_CATEGORIES.get(e) == category and e != ext
    ][:5]

    return {
        "name": ext,
        "ratified": True,
        "category": category,
        "related": related,
    }


def suggest_extensions(prefix: str) -> list[str]:
    """根据前缀推荐 ISA 扩展名.

    用于自动完成功能。

    Args:
        prefix: 扩展名前缀，如 "Zic"

    Returns:
        匹配的扩展名列表
    """
    return [
        ext for ext in sorted(RATIFIED_EXTENSIONS)
        if ext.startswith(prefix)
    ][:10]


def filter_extensions_by_category(category: str) -> list[str]:
    """按类别筛选 ISA 扩展.

    Args:
        category: 类别名称，如 "vector", "crypto", "bitmanip"

    Returns:
        该类别下的所有扩展名
    """
    return [
        ext for ext in sorted(RATIFIED_EXTENSIONS)
        if EXTENSION_CATEGORIES.get(ext) == category.lower()
    ]


def is_vector_extension(extension: str) -> bool:
    """检查是否为向量扩展.

    Args:
        extension: ISA 扩展名

    Returns:
        如果是向量扩展则返回 True
    """
    info = get_extension_info(extension)
    return info.get("category") == "vector"


def is_crypto_extension(extension: str) -> bool:
    """检查是否为加密扩展.

    Args:
        extension: ISA 扩展名

    Returns:
        如果是加密扩展则返回 True
    """
    info = get_extension_info(extension)
    return info.get("category") == "crypto"

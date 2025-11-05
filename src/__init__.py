"""核心研究工具套件。"""
from importlib import metadata

__all__ = [
    "__version__",
]

try:
    __version__ = metadata.version("codewithgpt")
except metadata.PackageNotFoundError:  # pragma: no cover - 套件未安裝時
    __version__ = "0.1.0"

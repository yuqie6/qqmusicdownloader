"""领域层：定义实体、值对象与核心业务规则。"""

from __future__ import annotations

from .config import DownloadConfig
from .models import SongRecord, FileSizeMap
from .ports import DownloadAPI

__all__ = [
    "DownloadConfig",
    "SongRecord",
    "FileSizeMap",
    "DownloadAPI",
]

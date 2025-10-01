"""基础设施层：封装外部系统的适配实现。"""

from __future__ import annotations

from .qq_music_api import QQMusicAPI
from . import crypto

__all__ = [
    "QQMusicAPI",
    "crypto",
]

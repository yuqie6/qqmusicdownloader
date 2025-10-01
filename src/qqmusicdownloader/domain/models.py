"""领域数据模型定义。"""

from __future__ import annotations

from typing import TypedDict

FileSizeMap = TypedDict(
    "FileSizeMap",
    {
        "128": int,
        "320": int,
        "flac": int,
    },
    total=False,
)


class SongRecord(TypedDict, total=False):
    """搜索结果的歌曲信息结构。"""

    name: str
    singer: str
    album: str
    songmid: str
    media_mid: str
    interval: int
    size: FileSizeMap

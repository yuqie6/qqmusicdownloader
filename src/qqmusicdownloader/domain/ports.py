"""领域层对下载基础设施的抽象接口。"""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Iterable, Protocol

from qqmusicdownloader.domain import SongRecord


class DownloadAPI(Protocol):
    """下载相关基础设施应实现的最小接口。"""

    async def validate_cookie(self) -> bool:
        """校验当前 Cookie 是否有效。"""

    async def search_song(self, keyword: str) -> list[SongRecord]:
        """根据关键词搜索歌曲。"""

    def get_download_path(self) -> str:
        """返回当前下载目录路径字符串。"""

    def configure_download_dirs(self, base_dir: Path) -> None:
        """使用新的基础目录配置下载路径。"""

    async def get_song_url(self, songmid: str, media_mid: str, quality: int) -> str | None:
        """获取指定歌曲在特定音质下的下载链接。"""

    async def download_with_lyrics(
        self,
        url: str,
        filename: str,
        quality: int,
        songmid: str,
        *,
        progress_bar: object | None = None,
        progress_label: object | None = None,
        pause_events: Iterable[asyncio.Event] | None = None,
    ) -> bool:
        """执行歌曲与歌词的下载流程。"""


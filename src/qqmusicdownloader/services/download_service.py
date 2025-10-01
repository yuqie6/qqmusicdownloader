"""下载服务封装，从旧版 `QQMusicDownloader` 重构而来。"""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Sequence

from qqmusicdownloader.domain import DownloadConfig, DownloadAPI, SongRecord
from qqmusicdownloader.infrastructure import QQMusicAPI


class DownloadService:
    """协调 QQ 音乐下载任务，封装对 API 的调用。"""

    def __init__(
        self,
        api_client: DownloadAPI,
        *,
        config: DownloadConfig | None = None,
    ) -> None:
        self._api = api_client
        self.config = config or DownloadConfig()
        self.current_songs: list[SongRecord] = []
        self.global_pause_event = asyncio.Event()
        self.global_pause_event.set()

    @classmethod
    def from_cookie(cls, cookie: str) -> "DownloadService":
        """使用原始 Cookie 创建服务实例。"""

        api = QQMusicAPI(cookie)
        return cls(api)

    async def validate_cookie(self) -> bool:
        """验证 Cookie 是否有效。"""

        return await self._api.validate_cookie()

    async def search(self, keyword: str) -> list[SongRecord]:
        """搜索歌曲并缓存最新结果。"""

        songs: list[SongRecord] = await self._api.search_song(keyword)
        self.current_songs = songs
        return songs

    def get_download_path(self) -> str:
        """返回默认下载目录。"""

        return self._api.get_download_path()

    def set_download_path(self, base_dir: Path) -> None:
        """更新下载目录。"""

        self._api.configure_download_dirs(base_dir)

    async def download_song(
        self,
        song: SongRecord,
        quality: int,
        *,
        progress_bar: object | None = None,
        progress_label: object | None = None,
        extra_pause_events: Sequence[asyncio.Event] | None = None,
    ) -> bool:
        """下载单首歌曲，包含歌词。"""

        songmid = song.get("songmid") or song.get("id")
        media_mid = song.get("media_mid") or songmid
        if not songmid:
            raise ValueError("歌曲信息缺少 songmid")

        download_url = await self._api.get_song_url(songmid, media_mid or "", quality)
        if not download_url:
            return False

        name = song.get("name", "未知歌曲")
        singer = song.get("singer", "未知歌手")
        filename = f"{name} - {singer}"

        pause_events = [self.global_pause_event]
        if extra_pause_events:
            pause_events.extend(extra_pause_events)

        return await self._api.download_with_lyrics(
            download_url,
            filename,
            quality,
            songmid,
            progress_bar=progress_bar,
            progress_label=progress_label,
            pause_events=pause_events,
        )

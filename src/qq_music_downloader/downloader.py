"""下载核心逻辑的轻量封装"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from typing import Any

from .qq_music_api import QQMusicAPI

logger = logging.getLogger(__name__)


@dataclass
class DownloadConfig:
    """下载配置"""

    max_concurrent: int = 3
    default_quality: int = 1


class QQMusicDownloader:
    """为自定义 UI 提供最小化的下载支持"""

    def __init__(self, cookie: str) -> None:
        self.api = QQMusicAPI(cookie)
        self.config = DownloadConfig()
        self.current_songs: list[dict[str, Any]] = []
        self.global_pause_event = asyncio.Event()
        self.global_pause_event.set()
        logger.info("下载器初始化完成")

    def get_download_path(self) -> str:
        """返回默认下载目录"""

        return self.api.get_download_path()

    async def validate_cookie(self) -> bool:
        """验证 Cookie 是否有效"""

        logger.info("开始验证 Cookie...")
        is_valid = await self.api.validate_cookie()
        logger.info("Cookie 验证结果: %s", "有效" if is_valid else "无效")
        return is_valid

    async def search(self, keyword: str) -> list[dict[str, Any]]:
        """搜索歌曲并缓存最新结果"""

        logger.info("开始搜索关键词: %s", keyword)
        songs = await self.api.search_song(keyword)
        self.current_songs = songs
        logger.info("搜索完成，共获得 %d 首歌曲", len(songs))
        return songs

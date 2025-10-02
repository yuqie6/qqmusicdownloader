import asyncio
from pathlib import Path
from typing import Iterable

import pytest

from qqmusicdownloader.domain import SongRecord
from qqmusicdownloader.services import DownloadService


class StubDownloadAPI:
    def __init__(self) -> None:
        self.download_dir: Path | None = None
        self.validate_calls = 0
        self.search_calls: list[str] = []
        self.download_requests: list[tuple[str, int]] = []

    async def validate_cookie(self) -> bool:
        self.validate_calls += 1
        return True

    async def search_song(self, keyword: str) -> list[SongRecord]:
        self.search_calls.append(keyword)
        return [
            {
                "name": "测试歌曲",
                "singer": "歌手",
                "album": "专辑",
                "songmid": "mid123",
                "media_mid": "media123",
                "interval": 100,
                "size": {},
            }
        ]

    def get_download_path(self) -> str:
        return str(self.download_dir or Path("/tmp/qqmusic"))

    def configure_download_dirs(self, base_dir: Path) -> None:
        self.download_dir = base_dir

    async def get_song_url(self, songmid: str, media_mid: str, quality: int) -> str | None:
        return f"https://example.com/{songmid}/{quality}"

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
        self.download_requests.append((songmid, quality))
        # 确认暂停事件全部已 set
        if pause_events:
            for event in pause_events:
                assert event.is_set()
        return True


@pytest.mark.asyncio
async def test_download_service_end_to_end(tmp_path: Path) -> None:
    api = StubDownloadAPI()
    service = DownloadService(api)

    assert await service.validate_cookie() is True
    assert api.validate_calls == 1

    songs = await service.search("爱错")
    assert api.search_calls == ["爱错"]
    assert service.current_songs == songs

    service.set_download_path(tmp_path)
    assert api.download_dir == tmp_path

    result = await service.download_song(songs[0], quality=2)
    assert result is True
    assert api.download_requests == [("mid123", 2)]

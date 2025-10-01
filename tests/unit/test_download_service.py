import asyncio
from pathlib import Path

import pytest

from qqmusicdownloader.domain import SongRecord
from qqmusicdownloader.services import DownloadService


class StubDownloadAPI:
    """提供给 DownloadService 的最小测试桩实现。"""

    def __init__(self) -> None:
        self.download_return = True
        self.search_keyword: str | None = None
        self.configured_dir: Path | None = None
        self.get_song_url_calls: list[tuple[str, str, int]] = []
        self.download_calls: list[dict[str, object]] = []
        self.raise_on_configure: Exception | None = None
        self.url_to_return: str | None = "https://example.com/song"
        self.raise_on_download: Exception | None = None

    async def validate_cookie(self) -> bool:
        return True

    async def search_song(self, keyword: str) -> list[SongRecord]:
        self.search_keyword = keyword
        return [
            {
                "name": "测试歌曲",
                "singer": "测试歌手",
                "album": "测试专辑",
                "songmid": "mid123",
                "media_mid": "media123",
                "interval": 100,
                "size": {"128": 1},
            }
        ]

    def get_download_path(self) -> str:
        return "/tmp/qqmusic"

    def configure_download_dirs(self, base_dir: Path) -> None:
        if self.raise_on_configure:
            raise self.raise_on_configure
        self.configured_dir = base_dir

    async def get_song_url(self, songmid: str, media_mid: str, quality: int) -> str | None:
        self.get_song_url_calls.append((songmid, media_mid, quality))
        return self.url_to_return

    async def download_with_lyrics(
        self,
        url: str,
        filename: str,
        quality: int,
        songmid: str,
        *,
        progress_bar: object | None = None,
        progress_label: object | None = None,
        pause_events: list[asyncio.Event] | None = None,
    ) -> bool:
        if self.raise_on_download:
            raise self.raise_on_download
        self.download_calls.append(
            {
                "url": url,
                "filename": filename,
                "quality": quality,
                "songmid": songmid,
                "pause_events": pause_events or [],
            }
        )
        return self.download_return


@pytest.mark.asyncio
async def test_search_and_download_flow() -> None:
    api = StubDownloadAPI()
    service = DownloadService(api)

    songs = await service.search("周杰伦")
    assert api.search_keyword == "周杰伦"
    assert service.current_songs == songs

    service.set_download_path(Path("/tmp/custom"))
    assert api.configured_dir == Path("/tmp/custom")

    result = await service.download_song(songs[0], quality=2)
    assert result is True

    assert api.get_song_url_calls == [("mid123", "media123", 2)]
    assert api.download_calls[0]["url"] == "https://example.com/song"
    pause_events = api.download_calls[0]["pause_events"]
    assert service.global_pause_event in pause_events


@pytest.mark.asyncio
async def test_download_song_requires_songmid() -> None:
    api = StubDownloadAPI()
    service = DownloadService(api)

    song: SongRecord = {
        "name": "无编号",
        "singer": "未知",
        "album": "未知",
        "media_mid": "media123",
        "interval": 120,
    }

    with pytest.raises(ValueError):
        await service.download_song(song, quality=1)

    assert api.get_song_url_calls == []


@pytest.mark.asyncio
async def test_download_song_handles_missing_url() -> None:
    api = StubDownloadAPI()
    api.url_to_return = None
    service = DownloadService(api)

    song = (await service.search("测试"))[0]

    result = await service.download_song(song, quality=1)
    assert result is False


@pytest.mark.asyncio
async def test_download_song_propagates_download_error() -> None:
    api = StubDownloadAPI()
    api.raise_on_download = RuntimeError("io failure")
    service = DownloadService(api)

    song = (await service.search("测试"))[0]

    with pytest.raises(RuntimeError):
        await service.download_song(song, quality=1)


@pytest.mark.asyncio
async def test_pause_event_chain() -> None:
    api = StubDownloadAPI()
    service = DownloadService(api)

    extra_event = asyncio.Event()
    extra_event.set()

    song = (await service.search("测试"))[0]
    await service.download_song(song, quality=1, extra_pause_events=[extra_event])

    pause_events = api.download_calls[0]["pause_events"]
    assert service.global_pause_event in pause_events
    assert extra_event in pause_events


def test_set_download_path_propogates_error() -> None:
    api = StubDownloadAPI()
    api.raise_on_configure = RuntimeError("no permission")
    service = DownloadService(api)

    with pytest.raises(RuntimeError):
        service.set_download_path(Path("/tmp/unwritable"))

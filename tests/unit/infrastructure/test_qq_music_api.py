import asyncio
from pathlib import Path
from typing import Any, Dict, Optional

import pytest

from qqmusicdownloader.infrastructure import QQMusicAPI


class DummyContent:
    def __init__(self, data: bytes) -> None:
        self._data = data

    async def iter_chunked(self, chunk_size: int):  # pragma: no cover - generator
        yield self._data


class DummyResponse:
    def __init__(self, data: bytes, status: int = 200, headers: Optional[Dict[str, str]] = None) -> None:
        self.status = status
        self.headers = headers or {"content-length": str(len(data))}
        self._data = data
        self.content = DummyContent(data)

    async def __aenter__(self) -> "DummyResponse":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        return None

    async def read(self) -> bytes:
        return self._data

    def raise_for_status(self) -> None:
        if self.status >= 400:
            raise RuntimeError(f"HTTP {self.status}")


class DummySession:
    def __init__(self, response: DummyResponse) -> None:
        self._response = response
        self.closed = False

    async def __aenter__(self) -> "DummySession":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        self.closed = True

    def post(self, *_args: Any, **_kwargs: Any) -> DummyResponse:
        return self._response

    def get(self, *_args: Any, **_kwargs: Any) -> DummyResponse:
        return self._response


@pytest.fixture()
def api(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> QQMusicAPI:
    api = QQMusicAPI("uin=o123; qqmusic_key=token;")
    api.configure_download_dirs(tmp_path)
    return api


@pytest.mark.asyncio
async def test_validate_cookie_success(monkeypatch: pytest.MonkeyPatch, api: QQMusicAPI) -> None:
    async def fake_call(payload: Dict[str, Any], *, encoding: str = "ag-1") -> Dict[str, Any]:
        return {"req_1": {"code": 0}}

    monkeypatch.setattr(api, "_call_musics", fake_call)

    assert await api.validate_cookie() is True


@pytest.mark.asyncio
async def test_validate_cookie_failure(monkeypatch: pytest.MonkeyPatch, api: QQMusicAPI) -> None:
    async def fake_call(payload: Dict[str, Any], *, encoding: str = "ag-1") -> Optional[Dict[str, Any]]:
        return None

    monkeypatch.setattr(api, "_call_musics", fake_call)

    assert await api.validate_cookie() is False


@pytest.mark.asyncio
async def test_search_song_decodes_unicode(monkeypatch: pytest.MonkeyPatch, api: QQMusicAPI) -> None:
    async def fake_call(payload: Dict[str, Any], *, encoding: str = "ag-1") -> Dict[str, Any]:
        raw = {
            "req_1": {
                "code": 0,
                "data": {
                    "body": {
                        "song": {
                            "list": [
                                {
                                    "title": "\\u7231\\u6bcd",
                                    "singer": [{"name": "\\u738b\\u529b\\u5b8f"}],
                                    "album": {"title": "\\u5fc3\\u4e2d\\u7684\\u65e5\\u6708"},
                                    "mid": "mid",
                                    "file": {
                                        "media_mid": "media",
                                        "size_128mp3": 1,
                                        "size_320mp3": 2,
                                        "size_flac": 3,
                                    },
                                    "interval": 180,
                                }
                            ]
                        }
                    }
                },
            }
        }
        return api._decode_unicode_tree(raw)  # type: ignore[arg-type]

    monkeypatch.setattr(api, "_call_musics", fake_call)

    songs = await api.search_song("爱母")
    assert songs[0]["name"] == "爱母"
    assert songs[0]["singer"] == "王力宏"
    assert songs[0]["album"] == "心中的日月"


@pytest.mark.asyncio
async def test_download_with_lyrics_writes_file(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    api: QQMusicAPI,
) -> None:
    data = b"audio-bytes"
    dummy_response = DummyResponse(data)

    def fake_session(*_args: Any, **_kwargs: Any) -> DummySession:
        return DummySession(dummy_response)

    monkeypatch.setattr("qqmusicdownloader.infrastructure.qq_music_api.aiohttp.ClientSession", fake_session)

    async def fake_get_lyrics(_songmid: str) -> str:
        return "歌词"

    monkeypatch.setattr(api, "get_lyrics", fake_get_lyrics)

    progress_label = type("Label", (), {"text": ""})()
    progress_bar = type("Bar", (), {"value": 0})()

    pause_event = asyncio.Event()
    pause_event.set()

    result = await api.download_with_lyrics(
        url="https://example.com/song",
        filename="测试歌曲",
        quality=1,
        songmid="mid123",
        progress_bar=progress_bar,
        progress_label=progress_label,
        pause_events=[pause_event],
    )

    assert result is True
    music_file = tmp_path / "Music" / "测试歌曲.m4a"
    assert music_file.read_bytes() == data
    lyric_file = tmp_path / "Lyrics" / "测试歌曲.lrc"
    assert lyric_file.read_text(encoding="utf-8") == "歌词"


@pytest.mark.asyncio
async def test_download_with_lyrics_handles_http_error(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    api: QQMusicAPI,
) -> None:
    dummy_response = DummyResponse(b"", status=403)

    def fake_session(*_args: Any, **_kwargs: Any) -> DummySession:
        return DummySession(dummy_response)

    monkeypatch.setattr("qqmusicdownloader.infrastructure.qq_music_api.aiohttp.ClientSession", fake_session)

    result = await api.download_with_lyrics(
        url="https://example.com/song",
        filename="失败",
        quality=1,
        songmid="mid123",
    )

    assert result is False
    assert not (tmp_path / "Music" / "失败.m4a").exists()

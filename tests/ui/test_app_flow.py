import asyncio
from pathlib import Path
from typing import Any

import pytest
from textual.widgets import Button, Input, Label, SelectionList

from qqmusicdownloader.services import DownloadService
from qqmusicdownloader.ui.app import QQMusicApp


class FakeDownloadService:
    def __init__(self, base_dir: Path) -> None:
        self._path = base_dir
        self.global_pause_event = asyncio.Event()
        self.global_pause_event.set()
        self.current_songs: list[dict[str, Any]] = []
        self.search_calls: list[str] = []
        self.download_calls: list[tuple[str, int]] = []
        self.set_path_calls: list[Path] = []
        self.validate_called = False

    async def validate_cookie(self) -> bool:
        self.validate_called = True
        return True

    async def search(self, keyword: str) -> list[dict[str, Any]]:
        self.search_calls.append(keyword)
        songs = [
            {
                "name": "测试歌曲",
                "singer": "测试歌手",
                "album": "测试专辑",
                "songmid": "mid123",
                "media_mid": "media123",
                "interval": 180,
                "size": {},
            },
            {
                "name": "第二首",
                "singer": "歌手",
                "album": "专辑",
                "songmid": "mid456",
                "media_mid": "media456",
                "interval": 200,
                "size": {},
            },
        ]
        self.current_songs = songs
        return songs

    def get_download_path(self) -> str:
        return str(self._path)

    def set_download_path(self, base_dir: Path) -> None:
        self.set_path_calls.append(base_dir)
        self._path = base_dir

    async def download_song(self, song: dict[str, Any], quality: int, **_: Any) -> bool:
        self.download_calls.append((song["songmid"], quality))
        return True


@pytest.mark.asyncio
async def test_app_flow_save_search_and_download(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    fake_service = FakeDownloadService(tmp_path)

    async def run_app_test() -> None:
        async with QQMusicApp().run_test() as pilot:
            cookie_input = pilot.app.query_one("#cookie-input", Input)
            cookie_input.value = "test_cookie"

            await pilot.app._save_cookie()

            start_button = pilot.app.query_one("#start-download", Button)
            assert start_button.disabled is False
            assert fake_service.validate_called is True

            search_input = pilot.app.query_one("#search-input", Input)
            search_input.value = "爱错"
            await pilot.app._search_songs()

            selection = pilot.app.query_one("#results", SelectionList)
            assert len(selection.options) == 2
            selection.select(0)

            await pilot.app._start_download()

            status = pilot.app.query_one("#status-label", Label)
            assert "完成" in str(status.renderable)
            assert fake_service.download_calls == [("mid123", 1)]

    def fake_from_cookie(cls, cookie: str) -> FakeDownloadService:  # noqa: D401
        return fake_service

    monkeypatch.setattr(DownloadService, "from_cookie", classmethod(fake_from_cookie))

    await run_app_test()

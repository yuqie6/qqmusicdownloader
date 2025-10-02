import asyncio
from pathlib import Path
from typing import Any

import pytest
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

    def fake_from_cookie(cls, cookie: str) -> FakeDownloadService:  # noqa: D401
        return fake_service

    monkeypatch.setattr(DownloadService, "from_cookie", classmethod(fake_from_cookie))

    async with QQMusicApp().run_test() as pilot:
        await pilot.app._save_cookie("test_cookie")

        assert fake_service.validate_called is True
        assert fake_service.set_path_calls  # 路径被同步至服务层
        assert pilot.app.actions_panel._start.disabled is False

        await pilot.app._search_songs("爱错")
        assert fake_service.search_calls == ["爱错"]
        assert len(pilot.app.current_songs) == 2
        # 选中第一首歌曲
        results_selection = pilot.app.results_panel._selection
        results_selection.select(0)

        await pilot.app._start_download()
        assert fake_service.download_calls == [("mid123", 1)]

        status_content = pilot.app.status_panel._label.render()
        assert "完成" in status_content.plain

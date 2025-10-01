#!/usr/bin/env python3
"""基于 Textual 的 QQ 音乐下载器入口。"""

from __future__ import annotations

import asyncio
import logging
import re
from pathlib import Path
from typing import Optional

from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.widgets import Footer, Header

from qqmusicdownloader.domain import SongRecord
from qqmusicdownloader.services import DownloadService
from qqmusicdownloader.ui.widgets import (
    ActionsPanel,
    CookiePanel,
    PathPanel,
    ResultsPanel,
    SearchPanel,
    StatusPanel,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
LOGGER = logging.getLogger(__name__)

QUALITY_OPTIONS = [
    ("M4A (128kbps)", "1"),
    ("MP3 (320kbps)", "2"),
    ("FLAC (无损)", "3"),
]


class QQMusicApp(App[None]):
    """Textual 终端界面应用。"""

    CSS_PATH = "themes/default.css"

    BINDINGS = [
        ("ctrl+c", "quit", "退出"),
        ("ctrl+q", "quit", "退出"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.service: Optional[DownloadService] = None
        self.current_songs: list[SongRecord] = []
        self.is_downloading = False
        self._download_path = Path.home() / "Desktop" / "QQMusic"
        self._path_overridden = False
        self._unicode_pattern = re.compile(r"\\u[0-9a-fA-F]{4}")

        self.cookie_panel = CookiePanel()
        self.path_panel = PathPanel()
        self.search_panel = SearchPanel()
        self.results_panel = ResultsPanel()
        self.actions_panel = ActionsPanel(QUALITY_OPTIONS, default="1")
        self.status_panel = StatusPanel()

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Vertical(
            self.cookie_panel,
            self.path_panel,
            self.search_panel,
            self.results_panel,
            self.actions_panel,
            self.status_panel,
            id="main",
        )
        yield Footer()

    async def on_mount(self) -> None:
        self.actions_panel.reset_quality("1")
        self._ensure_download_dirs(self._download_path)

    async def on_cookie_panel_save_requested(
        self, message: CookiePanel.SaveRequested
    ) -> None:
        await self._save_cookie(message.cookie)

    async def on_path_panel_apply_requested(
        self, message: PathPanel.ApplyRequested
    ) -> None:
        await self._apply_path(message.path)

    async def on_search_panel_search_requested(
        self, message: SearchPanel.SearchRequested
    ) -> None:
        await self._search_songs(message.keyword)

    async def on_actions_panel_start_requested(
        self, _: ActionsPanel.StartRequested
    ) -> None:
        await self._start_download()

    async def on_actions_panel_toggle_pause_requested(
        self, _: ActionsPanel.TogglePauseRequested
    ) -> None:
        await self._toggle_pause()

    def normalize_text(self, text: str) -> str:
        if not isinstance(text, str):
            return str(text)
        if self._unicode_pattern.search(text):
            try:
                return text.encode("utf-8").decode("unicode_escape")
            except UnicodeDecodeError:
                return text
        return text

    def set_status(self, message: str) -> None:
        normalized = self.normalize_text(message)
        self.status_panel.set_status(normalized)

    def _ensure_download_dirs(self, path: Path) -> None:
        resolved = path.expanduser()
        resolved.mkdir(parents=True, exist_ok=True)
        music_dir = resolved / "Music"
        lyrics_dir = resolved / "Lyrics"
        music_dir.mkdir(parents=True, exist_ok=True)
        lyrics_dir.mkdir(parents=True, exist_ok=True)

        self._download_path = resolved
        self.path_panel.set_path(str(resolved))

        if self.service is not None:
            self.service.set_download_path(resolved)
            LOGGER.info("下载目录更新为: %s", resolved)

    async def _save_cookie(self, cookie: str) -> None:
        cookie = cookie.strip()
        if not cookie:
            self.set_status("请先输入 Cookie")
            return

        try:
            service = DownloadService.from_cookie(cookie)
            self.set_status("正在验证 Cookie...")
            is_valid = await service.validate_cookie()
            if not is_valid:
                self.actions_panel.enable_start(False)
                self.set_status("❌ Cookie 验证失败，请检查")
                return

            self.service = service
            if not self._path_overridden:
                self._download_path = Path(service.get_download_path())
            self._ensure_download_dirs(self._download_path)
            self.actions_panel.enable_start(True)
            self.set_status("✅ Cookie 验证成功")
        except Exception as exc:  # pragma: no cover - 兜底保护
            LOGGER.exception("保存 Cookie 失败")
            self.service = None
            self.actions_panel.enable_start(False)
            self.set_status(f"❌ 错误: {exc}")

    async def _apply_path(self, candidate: str) -> None:
        candidate = candidate.strip()
        if not candidate:
            self.set_status("请输入有效的下载目录")
            return
        candidate_path = Path(candidate)
        try:
            self._ensure_download_dirs(candidate_path)
            self._path_overridden = True
            self.set_status(f"下载目录已更新: {candidate_path}")
        except OSError as exc:
            LOGGER.exception("创建目录失败")
            self.set_status(f"❌ 无法创建目录: {exc}")

    async def _search_songs(self, keyword: str) -> None:
        service = self.service
        if not service:
            self.set_status("请先配置 Cookie")
            return

        keyword = keyword.strip()
        if not keyword:
            self.set_status("请输入搜索关键词")
            return

        self.set_status(f"正在搜索: {keyword}...")
        try:
            songs = await service.search(keyword)
        except Exception as exc:  # pragma: no cover - 网络异常
            LOGGER.exception("搜索失败")
            self.set_status(f"搜索失败: {exc}")
            return

        if not songs:
            self.current_songs = []
            self.results_panel.clear()
            self.set_status("未找到相关歌曲")
            return

        self.current_songs = songs[:20]
        options: list[tuple[str, int]] = []
        for index, song in enumerate(self.current_songs):
            name = self.normalize_text(song.get("name", "未知歌曲"))
            singer = self.normalize_text(song.get("singer", "未知歌手"))
            album = self.normalize_text(song.get("album", "未知专辑"))
            label = f"{index + 1}. {name} - {singer} ({album})"
            options.append((label, index))
        self.results_panel.set_options(options)
        self.set_status(f"找到 {len(self.current_songs)} 首歌曲")

    async def _start_download(self) -> None:
        if self.is_downloading:
            self.set_status("已有下载任务进行中")
            return

        service = self.service
        if not service:
            self.set_status("请先配置 Cookie")
            return

        indices = list(self.results_panel.selected_indices())
        if not indices:
            self.set_status("请先选择要下载的歌曲")
            return

        quality = self.actions_panel.get_quality()

        self.is_downloading = True
        self.actions_panel.enable_start(False)
        self.actions_panel.enable_pause(True)

        total = len(indices)
        self.status_panel.set_progress(total, 0)

        try:
            for position, idx in enumerate(indices, start=1):
                if idx >= len(self.current_songs):
                    LOGGER.warning("歌曲索引越界: %s", idx)
                    continue
                song = self.current_songs[idx]
                song_name = self.normalize_text(song.get("name", "未知歌曲"))
                singer = self.normalize_text(song.get("singer", "未知歌手"))
                self.set_status(f"下载中 ({position}/{total}): {song_name} - {singer}")
                success = await self._download_song(song, quality)
                if not success:
                    self.set_status(f"❌ 下载失败: {song_name} - {singer}")
                    break
                self.status_panel.set_progress(total, position)
            else:
                self.set_status(f"✅ 已完成 {total} 首歌曲下载")
        except Exception as exc:  # pragma: no cover - 极端异常
            LOGGER.exception("下载任务失败")
            self.set_status(f"❌ 下载失败: {exc}")
        finally:
            self.is_downloading = False
            self.actions_panel.enable_pause(False)
            self.actions_panel.enable_start(True)
            await asyncio.sleep(1)
            self.status_panel.set_progress(0, 0)

    async def _download_song(self, song: SongRecord, quality: int) -> bool:
        service = self.service
        if service is None:
            return False

        try:
            return await service.download_song(song, quality)
        except ValueError as exc:
            LOGGER.error("歌曲信息不完整: %s", exc)
            return False
        except Exception:  # pragma: no cover - 外部依赖
            LOGGER.exception("下载失败: %s", song)
            return False

    async def _toggle_pause(self) -> None:
        service = self.service
        if not service:
            return

        pause_event = service.global_pause_event
        if pause_event.is_set():
            pause_event.clear()
            self.set_status("⏸ 已暂停")
        else:
            pause_event.set()
            self.set_status("▶ 已恢复")

    def action_quit(self) -> None:
        self.exit()


def main() -> QQMusicApp:
    """应用入口。

    Returns:
        QQMusicApp: Textual 应用实例。
    """

    app = QQMusicApp()
    app.run()
    return app


if __name__ == "__main__":
    main()

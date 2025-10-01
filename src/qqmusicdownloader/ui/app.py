#!/usr/bin/env python3
"""基于 Textual 的 QQ 音乐下载器入口。"""

from __future__ import annotations

import asyncio
import logging
import re
from pathlib import Path
from typing import Optional, cast

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import (
    Button,
    Footer,
    Header,
    Input,
    Label,
    ProgressBar,
    SelectionList,
    Select,
)

from qqmusicdownloader.domain import SongRecord
from qqmusicdownloader.services import DownloadService


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

    CSS = """
    Screen {
        background: $surface;
        color: $text;
    }

    #main {
        layout: vertical;
        padding: 1 2;
    }

    .section {
        border: solid $secondary;
        border-title-align: left;
        padding: 1;
        margin: 0 0 1 0;
    }

    .section-title {
        color: $text;
        text-style: bold;
    }

    Label {
        color: $text;
    }

    Input {
        color: $text;
        border: solid $secondary;
    }

    Button {
        color: $text;
    }

    SelectionList {
        color: $text;
    }

    Select {
        color: $text;
    }

    #cookie-box,
    #path-box,
    #search-box {
        layout: vertical;
    }

    #path-line,
    #search-line,
    #actions {
        layout: horizontal;
    }

    #results {
        height: 18;
        min-height: 10;
    }

    #status-block {
        layout: vertical;
    }
    """

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

    def compose(self) -> ComposeResult:

        yield Header(show_clock=True)
        yield Container(
            Vertical(
                Container(
                    Label("认证设置", classes="section-title"),
                    Container(
                        Input(
                            placeholder="粘贴 Cookie 后按回车或点击按钮",
                            password=False,
                            id="cookie-input",
                        ),
                        Button("保存 Cookie", id="save-cookie"),
                        id="cookie-box",
                    ),
                    classes="section",
                ),
                Container(
                    Label("下载目录", classes="section-title"),
                    Horizontal(
                        Input(id="path-input"),
                        Button("应用路径", id="apply-path"),
                        id="path-line",
                    ),
                    classes="section",
                ),
                Container(
                    Label("搜索歌曲", classes="section-title"),
                    Horizontal(
                        Input(
                            placeholder="输入关键词后按回车或点击按钮",
                            id="search-input",
                        ),
                        Button("搜索", id="search"),
                        id="search-line",
                    ),
                    classes="section",
                ),
                Container(
                    Label("搜索结果", classes="section-title"),
                    SelectionList[int](id="results"),
                    Label("已选 0 首", id="selection-label"),
                    classes="section",
                ),
                Container(
                    Select(QUALITY_OPTIONS, prompt="选择音质", id="quality", value="1"),
                    Button("开始下载", id="start-download", disabled=True),
                    Button("暂停/恢复", id="toggle-pause", disabled=True),
                    id="actions",
                ),
                Container(
                    ProgressBar(id="progress"),
                    Label("准备就绪", id="status-label"),
                    id="status-block",
                    classes="section",
                ),
            ),
            id="main",
        )
        yield Footer()

    async def on_mount(self) -> None:

        path_input = self.query_one("#path-input", Input)
        path_input.value = str(self._download_path)
        quality_select = self.query_one("#quality", Select)
        quality_select.value = "1"
        self._ensure_download_dirs(self._download_path)

    async def on_button_pressed(self, event: Button.Pressed) -> None:

        mapping = {
            "save-cookie": self._save_cookie,
            "apply-path": self._apply_path,
            "search": self._search_songs,
            "start-download": self._start_download,
            "toggle-pause": self._toggle_pause,
        }
        handler = mapping.get(event.button.id or "")
        if handler is not None:
            await handler()

    async def on_input_submitted(self, event: Input.Submitted) -> None:

        if event.input.id == "cookie-input":
            await self._save_cookie()
        elif event.input.id == "search-input":
            await self._search_songs()
        elif event.input.id == "path-input":
            await self._apply_path()

    def on_selection_list_selected_changed(
        self, event: SelectionList.SelectedChanged
    ) -> None:

        if event.selection_list.id == "results":
            self._update_selection_label()

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

        label = self.query_one("#status-label", Label)
        label.update(self.normalize_text(message))

    def _update_selection_label(self) -> None:

        selection_list = cast(SelectionList[int], self.query_one("#results", SelectionList))
        selected_count = len(selection_list.selected)
        label = self.query_one("#selection-label", Label)
        label.update(f"已选 {selected_count} 首")

    def _set_progress(self, total: int, progress: int) -> None:

        progress_bar = self.query_one("#progress", ProgressBar)
        progress_bar.update(total=total or None, progress=progress)

    def _ensure_download_dirs(self, path: Path) -> None:

        resolved = path.expanduser()
        resolved.mkdir(parents=True, exist_ok=True)
        music_dir = resolved / "Music"
        lyrics_dir = resolved / "Lyrics"
        music_dir.mkdir(parents=True, exist_ok=True)
        lyrics_dir.mkdir(parents=True, exist_ok=True)

        self._download_path = resolved
        path_input = self.query_one("#path-input", Input)
        path_input.value = str(resolved)

        service = self.service
        if service is not None:
            service.set_download_path(resolved)
            LOGGER.info("下载目录更新为: %s", resolved)

    async def _save_cookie(self) -> None:

        cookie_input = self.query_one("#cookie-input", Input)
        cookie = cookie_input.value.strip()
        if not cookie:
            self.set_status("请先输入 Cookie")
            return

        try:
            service = DownloadService.from_cookie(cookie)
            self.set_status("正在验证 Cookie...")
            is_valid = await service.validate_cookie()
            if not is_valid:
                self.set_status("❌ Cookie 验证失败，请检查")
                return

            self.service = service
            if not self._path_overridden:
                self._download_path = Path(service.get_download_path())
            self._ensure_download_dirs(self._download_path)
            self.set_status("✅ Cookie 验证成功")
            start_button = self.query_one("#start-download", Button)
            start_button.disabled = False
        except Exception as exc:  # pragma: no cover - 兜底保护
            LOGGER.exception("保存 Cookie 失败")
            self.service = None
            self.set_status(f"❌ 错误: {exc}")

    async def _apply_path(self) -> None:

        path_input = self.query_one("#path-input", Input)
        candidate = path_input.value.strip()
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

    async def _search_songs(self) -> None:

        service = self.service
        if not service:
            self.set_status("请先配置 Cookie")
            return

        keyword_input = self.query_one("#search-input", Input)
        keyword = keyword_input.value.strip()
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
            selection_list = cast(
                SelectionList[int], self.query_one("#results", SelectionList)
            )
            selection_list.clear_options()
            self._update_selection_label()
            self.set_status("未找到相关歌曲")
            return

        self.current_songs = songs[:20]
        selection_list = cast(SelectionList[int], self.query_one("#results", SelectionList))
        selection_list.clear_options()
        for index, song in enumerate(self.current_songs):
            name = self.normalize_text(song.get("name", "未知歌曲"))
            singer = self.normalize_text(song.get("singer", "未知歌手"))
            album = self.normalize_text(song.get("album", "未知专辑"))
            label = f"{index + 1}. {name} - {singer} ({album})"
            selection_list.add_option((label, index))
        selection_list.refresh()
        self._update_selection_label()
        self.set_status(f"找到 {len(self.current_songs)} 首歌曲")

    async def _start_download(self) -> None:

        if self.is_downloading:
            self.set_status("已有下载任务进行中")
            return

        service = self.service
        if not service:
            self.set_status("请先配置 Cookie")
            return

        selection_list = cast(SelectionList[int], self.query_one("#results", SelectionList))
        indices = sorted(set(selection_list.selected))
        if not indices:
            self.set_status("请先选择要下载的歌曲")
            return

        quality_select = self.query_one("#quality", Select)
        try:
            quality = int(quality_select.value or "1")
        except ValueError:
            quality = 1

        self.is_downloading = True
        start_button = self.query_one("#start-download", Button)
        start_button.disabled = True
        pause_button = self.query_one("#toggle-pause", Button)
        pause_button.disabled = False

        total = len(indices)
        self._set_progress(total, 0)

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
                self._set_progress(total, position)
            else:
                self.set_status(f"✅ 已完成 {total} 首歌曲下载")
        except Exception as exc:  # pragma: no cover - 极端异常
            LOGGER.exception("下载任务失败")
            self.set_status(f"❌ 下载失败: {exc}")
        finally:
            self.is_downloading = False
            pause_button.disabled = True
            start_button.disabled = False
            await asyncio.sleep(1)
            self._set_progress(0, 0)

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

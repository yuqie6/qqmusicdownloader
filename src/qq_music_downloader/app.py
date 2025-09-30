#!/usr/bin/env python3
"""基于 CustomTkinter 的 QQ 音乐下载器应用入口"""

from __future__ import annotations

import asyncio
import logging
import threading
from pathlib import Path
from typing import Any, Callable, Coroutine, Dict, List, Optional

from .downloader import QQMusicDownloader
from .qq_music_api import QQMusicAPI
from .ui import QQMusicUI


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class QQMusicApp:
    """QQ 音乐下载器主应用"""

    def __init__(self) -> None:
        self.ui = QQMusicUI()
        self.ui.set_app(self)

        self.api: Optional[QQMusicAPI] = None
        self.downloader: Optional[QQMusicDownloader] = None
        self.current_songs: List[Dict] = []
        self.is_downloading = False

        self._download_path = Path.home() / "Desktop" / "QQMusic"

        self.loop: Optional[asyncio.AbstractEventLoop] = None
        self.thread: Optional[threading.Thread] = None
        self._loop_ready = threading.Event()
        self._start_async_loop()

    # ------------------------------------------------------------------
    # 私有工具方法
    # ------------------------------------------------------------------
    def _start_async_loop(self) -> None:
        """启动后台事件循环线程"""

        def run_loop() -> None:
            loop = asyncio.new_event_loop()
            self.loop = loop
            self._loop_ready.set()
            asyncio.set_event_loop(loop)
            loop.run_forever()

        self.thread = threading.Thread(target=run_loop, daemon=True)
        self.thread.start()

    def _apply_download_path(self, path: Path) -> None:
        """更新 API 使用的下载路径"""

        self._download_path = Path(path).expanduser()
        api = self.api
        if not api:
            return

        api.base_dir = self._download_path
        api.music_dir = api.base_dir / "Music"
        api.lyrics_dir = api.base_dir / "Lyrics"

        for directory in (api.base_dir, api.music_dir, api.lyrics_dir):
            directory.mkdir(parents=True, exist_ok=True)

        logger.info("下载目录更新为: %s", self._download_path)

    def _notify_ui(self, callback: Callable[[], None]) -> None:
        """确保 UI 更新在 Tk 线程执行"""

        if hasattr(self.ui, "root") and self.ui.root:
            self.ui.root.after(0, callback)

    # ------------------------------------------------------------------
    # 公共接口，供 UI 调用
    # ------------------------------------------------------------------
    def update_download_path(self, path: str) -> None:
        """从 UI 更新下载路径"""

        self._apply_download_path(Path(path))
        self._notify_ui(
            lambda: self.ui.set_download_path_label(str(self._download_path))
        )

    def submit_coroutine(self, coroutine: Coroutine[Any, Any, None]) -> None:
        """在后台事件循环中调度协程"""

        self._loop_ready.wait()
        if not self.loop:
            raise RuntimeError("事件循环尚未初始化")
        asyncio.run_coroutine_threadsafe(coroutine, self.loop)

    @property
    def download_path(self) -> Path:
        """获取当前下载路径"""

        return self._download_path

    async def save_cookie_async(self, cookie: str) -> None:
        """保存并验证 Cookie"""

        cookie = cookie.strip()
        if not cookie:
            self._notify_ui(lambda: self.ui.set_status("请先输入 Cookie"))
            return

        try:
            candidate_downloader = QQMusicDownloader(cookie)
            api = candidate_downloader.api

            self._notify_ui(lambda: self.ui.set_status("正在验证 Cookie..."))
            is_valid = await api.validate_cookie()

            if not is_valid:
                self._notify_ui(
                    lambda: self.ui.set_status("❌ Cookie 验证失败，请检查")
                )
                return

            self.downloader = candidate_downloader
            self.api = api

            self._apply_download_path(self._download_path)

            self._notify_ui(lambda: self.ui.set_status("✅ Cookie 验证成功"))
            self._notify_ui(
                lambda: self.ui.set_download_path_label(str(self._download_path))
            )

        except Exception as exc:  # pragma: no cover - UI 环境容错
            logger.exception("保存 Cookie 失败")
            self.downloader = None
            self.api = None
            error_message = f"❌ 错误: {exc}"
            self._notify_ui(lambda msg=error_message: self.ui.set_status(msg))

    async def search_songs_async(self, keyword: str) -> None:
        """搜索歌曲"""

        api = self.api
        if not api:
            self._notify_ui(lambda: self.ui.set_status("请先配置 Cookie"))
            return

        keyword = keyword.strip()
        if not keyword:
            self._notify_ui(lambda: self.ui.set_status("请输入搜索关键词"))
            return

        self._notify_ui(lambda: self.ui.set_status(f"正在搜索: {keyword}..."))

        try:
            songs = await api.search_song(keyword)
        except Exception as exc:  # pragma: no cover - 网络异常
            logger.exception("搜索失败")
            error_message = f"搜索失败: {exc}"
            self._notify_ui(lambda msg=error_message: self.ui.set_status(msg))
            return

        if not songs:
            self.current_songs = []
            self._notify_ui(lambda: self.ui.update_results([]))
            self._notify_ui(lambda: self.ui.set_status("未找到相关歌曲"))
            return

        self.current_songs = songs[:20]
        self._notify_ui(lambda: self.ui.update_results(self.current_songs))
        self._notify_ui(
            lambda: self.ui.set_status(f"找到 {len(self.current_songs)} 首歌曲")
        )

    async def start_download_async(self, indices: List[int], quality: int) -> None:
        """开始下载选中的歌曲"""

        if self.is_downloading:
            self._notify_ui(lambda: self.ui.set_status("已有下载任务进行中"))
            return

        if not indices:
            self._notify_ui(lambda: self.ui.set_status("请先选择要下载的歌曲"))
            return

        if not self.api:
            self._notify_ui(lambda: self.ui.set_status("请先配置 Cookie"))
            return

        self.is_downloading = True
        self._notify_ui(lambda: self.ui.enable_download_controls(False))

        indices = sorted(set(indices))
        total = len(indices)

        try:
            for position, idx in enumerate(indices, start=1):
                try:
                    song = self.current_songs[idx]
                except IndexError:
                    logger.warning("歌曲索引越界: %s", idx)
                    continue

                def _status_update(song_name: str, singer: str, pos: int) -> None:
                    self.ui.set_status(
                        f"下载中 ({pos}/{total}): {song_name} - {singer}"
                    )

                self._notify_ui(
                    lambda s=song, p=position: _status_update(s["name"], s["singer"], p)
                )
                self._notify_ui(
                    lambda p=position: self.ui.set_progress((p - 1) / total)
                )

                success = await self._download_song(song, quality)

                if not success:
                    self._notify_ui(
                        lambda s=song: self.ui.set_status(
                            f"❌ 下载失败: {s['name']} - {s['singer']}"
                        )
                    )
                    break

                self._notify_ui(lambda p=position: self.ui.set_progress(p / total))

            else:
                self._notify_ui(
                    lambda: self.ui.set_status(f"✅ 已完成 {total} 首歌曲下载")
                )
                self._notify_ui(lambda: self.ui.set_progress(1.0))

        except Exception as exc:  # pragma: no cover - 兜底异常
            logger.exception("下载任务失败")
            error_message = f"❌ 下载失败: {exc}"
            self._notify_ui(lambda msg=error_message: self.ui.set_status(msg))

        finally:
            self.is_downloading = False
            self._notify_ui(lambda: self.ui.enable_download_controls(True))
            await asyncio.sleep(1)
            self._notify_ui(lambda: self.ui.set_progress(0.0))

    async def _download_song(self, song: Dict, quality: int) -> bool:
        """下载单首歌曲"""

        api = self.api
        if not api:
            return False

        songmid = song.get("songmid") or song.get("id")
        media_mid = song.get("media_mid") or songmid

        if not songmid:
            logger.error("歌曲信息缺少 songmid: %s", song)
            return False

        try:
            download_url = await api.get_song_url(songmid, media_mid, quality)
        except Exception:
            logger.exception("获取下载链接失败")
            return False

        if not download_url:
            logger.error("未能获取下载链接: %s", songmid)
            return False

        filename = f"{song['name']} - {song['singer']}"

        pause_events = None
        if self.downloader and getattr(self.downloader, "global_pause_event", None):
            pause_events = [self.downloader.global_pause_event]

        try:
            return await api.download_with_lyrics(
                download_url,
                filename,
                quality,
                songmid,
                pause_events=pause_events,
            )
        except Exception:
            logger.exception("下载失败: %s", filename)
            return False

    def toggle_pause(self) -> None:
        """切换暂停状态"""

        if not self.downloader or not hasattr(self.downloader, "global_pause_event"):
            return

        pause_event = self.downloader.global_pause_event
        if pause_event.is_set():
            pause_event.clear()
            self._notify_ui(lambda: self.ui.set_status("⏸ 已暂停"))
        else:
            pause_event.set()
            self._notify_ui(lambda: self.ui.set_status("▶ 已恢复"))

    def run(self) -> None:
        """运行应用"""

        try:
            self.ui.run()
        finally:
            if self.loop:
                self.loop.call_soon_threadsafe(self.loop.stop)


def main() -> QQMusicApp:
    """应用入口"""

    app = QQMusicApp()
    app.run()
    return app


if __name__ == "__main__":
    main()

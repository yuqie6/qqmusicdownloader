from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import Label, ProgressBar


class StatusPanel(Container):
    """展示下载进度与状态消息。"""

    def __init__(self) -> None:
        super().__init__(id="status-block", classes="section")
        self._progress = ProgressBar(id="progress")
        self._label = Label("准备就绪", id="status-label")

    def compose(self) -> ComposeResult:
        yield self._progress
        yield self._label

    def set_status(self, message: str) -> None:
        self._label.update(message)

    def set_progress(self, total: int, progress: int) -> None:
        self._progress.update(total=total or None, progress=progress)


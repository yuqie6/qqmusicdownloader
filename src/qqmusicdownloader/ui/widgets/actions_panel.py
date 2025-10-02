from __future__ import annotations

from typing import Sequence, cast

from textual.app import ComposeResult
from textual.containers import Container
from textual.message import Message
from textual.widgets import Button, Select
from textual._select import NoSelection


class ActionsPanel(Container):
    """下载动作控制区域。"""

    class StartRequested(Message):
        """请求开始下载。"""

    class TogglePauseRequested(Message):
        """请求切换暂停状态。"""

    def __init__(self, quality_options: Sequence[tuple[str, str]], default: str = "1") -> None:
        super().__init__(id="actions")
        self._quality = Select(quality_options, prompt="选择音质", id="quality", value=default)
        self._start = Button("开始下载", id="start-download", disabled=True)
        self._toggle = Button("暂停/恢复", id="toggle-pause", disabled=True)

    def compose(self) -> ComposeResult:
        yield self._quality
        yield self._start
        yield self._toggle

    def get_quality(self) -> int:
        """返回当前选择的音质编号。"""

        value = self._quality.value
        if isinstance(value, NoSelection) or value is None:
            return 1
        try:
            return int(str(value))
        except (TypeError, ValueError):
            return 1

    def enable_start(self, enabled: bool) -> None:
        self._start.disabled = not enabled

    def enable_pause(self, enabled: bool) -> None:
        self._toggle.disabled = not enabled

    def reset_quality(self, value: str) -> None:
        self._quality.value = value

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button is self._start:
            self.post_message(self.StartRequested())
        elif event.button is self._toggle:
            self.post_message(self.TogglePauseRequested())


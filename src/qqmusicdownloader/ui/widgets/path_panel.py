from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.message import Message
from textual.widgets import Button, Input, Label


class PathPanel(Container):
    """下载路径配置区域。"""

    class ApplyRequested(Message):
        """请求应用新的下载路径。"""

        def __init__(self, sender: PathPanel, path: str) -> None:
            super().__init__(sender)
            self.path = path

    def __init__(self) -> None:
        super().__init__(classes="section")
        self._input = Input(id="path-input")
        self._button = Button("应用路径", id="apply-path")

    def compose(self) -> ComposeResult:
        yield Label("下载目录", classes="section-title")
        yield Horizontal(self._input, self._button, id="path-line")

    def set_path(self, path: str) -> None:
        """更新路径显示。"""

        self._input.value = path

    def get_candidate_path(self) -> str:
        """返回用户输入的路径。"""

        return self._input.value.strip()

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button is self._button:
            self._emit_apply_request()

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input is self._input:
            self._emit_apply_request()

    def _emit_apply_request(self) -> None:
        self.post_message(self.ApplyRequested(self, self.get_candidate_path()))


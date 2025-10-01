from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Container
from textual.message import Message
from textual.widgets import Button, Input, Label


class CookiePanel(Container):
    """认证配置区域。"""

    class SaveRequested(Message):
        """请求保存 Cookie。"""

        def __init__(self, sender: CookiePanel, cookie: str) -> None:
            super().__init__(sender)
            self.cookie = cookie

    def __init__(self) -> None:
        super().__init__(classes="section")
        self._input = Input(
            placeholder="粘贴 Cookie 后按回车或点击按钮",
            password=False,
            id="cookie-input",
        )
        self._button = Button("保存 Cookie", id="save-cookie")

    def compose(self) -> ComposeResult:
        yield Label("认证设置", classes="section-title")
        yield Container(self._input, self._button, id="cookie-box")

    def reset_cookie(self, value: str) -> None:
        """更新输入框中的 Cookie。"""

        self._input.value = value

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button is self._button:
            self._emit_save_request()

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input is self._input:
            self._emit_save_request()

    def _emit_save_request(self) -> None:
        cookie = self._input.value.strip()
        self.post_message(self.SaveRequested(self, cookie))


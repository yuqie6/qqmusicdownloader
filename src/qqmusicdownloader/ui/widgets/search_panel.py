from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.message import Message
from textual.widgets import Button, Input, Label


class SearchPanel(Container):
    """歌曲搜索区域。"""

    class SearchRequested(Message):
        """请求执行搜索。"""

        def __init__(self, sender: SearchPanel, keyword: str) -> None:
            super().__init__(sender)
            self.keyword = keyword

    def __init__(self) -> None:
        super().__init__(classes="section")
        self._input = Input(
            placeholder="输入关键词后按回车或点击按钮",
            id="search-input",
        )
        self._button = Button("搜索", id="search")

    def compose(self) -> ComposeResult:
        yield Label("搜索歌曲", classes="section-title")
        yield Horizontal(self._input, self._button, id="search-line")

    def set_keyword(self, keyword: str) -> None:
        """更新搜索关键词。"""

        self._input.value = keyword

    def get_keyword(self) -> str:
        """返回当前关键词。"""

        return self._input.value.strip()

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button is self._button:
            self._emit_search_request()

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input is self._input:
            self._emit_search_request()

    def _emit_search_request(self) -> None:
        self.post_message(self.SearchRequested(self, self.get_keyword()))


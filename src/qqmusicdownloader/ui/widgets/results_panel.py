from __future__ import annotations

from typing import Iterable, Sequence

from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import Label, SelectionList


class ResultsPanel(Container):
    """展示搜索结果并维护选中状态。"""

    def __init__(self) -> None:
        super().__init__(classes="section")
        self._selection = SelectionList[int](id="results")
        self._label = Label("已选 0 首", id="selection-label")

    def compose(self) -> ComposeResult:
        yield Label("搜索结果", classes="section-title")
        yield self._selection
        yield self._label

    def set_options(self, options: Iterable[tuple[str, int]]) -> None:
        """用搜索结果填充列表。"""

        self._selection.clear_options()
        for label, value in options:
            self._selection.add_option((label, value))
        self._selection.refresh()
        self._update_selection_label()

    def clear(self) -> None:
        """清空搜索结果。"""

        self._selection.clear_options()
        self._selection.refresh()
        self._update_selection_label()

    def selected_indices(self) -> Sequence[int]:
        """返回当前选中的歌曲索引。"""

        return tuple(sorted(set(self._selection.selected)))

    def _update_selection_label(self) -> None:
        count = len(self._selection.selected)
        self._label.update(f"已选 {count} 首")

    def on_selection_list_selected_changed(
        self, event: SelectionList.SelectedChanged
    ) -> None:
        if event.selection_list is self._selection:
            self._update_selection_label()


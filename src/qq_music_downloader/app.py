# app.py
import logging
from pathlib import Path
from typing import Callable, Optional, Sequence, cast

import toga
from toga.sources import Row

from .downloader import QQMusicDownloader
from .ui import QQMusicDownloaderUI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class QQMusicDownloaderApp(toga.App):
    def __init__(self, *args, **kwargs):
        formal_name = "极简音乐下载器"
        app_id = "com.yuqie.qqmusicdownloader"
        author = "yuqie6"
        version = "1.2.0"
        description = "一款可以下载QQ音乐里面的歌曲的软件"

        super().__init__(
            formal_name=formal_name,
            app_id=app_id,
            author=author,
            version=version,
            description=description,
            *args,
            **kwargs,
        )

        # 初始化基本属性
        self.downloader: Optional[QQMusicDownloader] = None
        self.selected_indices: set[int] = set()
        self.current_selected: Optional[int] = None
        self._main_window: Optional[toga.MainWindow] = None
        self.ui: Optional[QQMusicDownloaderUI] = None
        self._setup_app_state()

    def _setup_app_state(self):
        """初始化应用状态"""
        self.is_batch_mode = False
        self.last_search: Optional[str] = None
        logger.info("应用状态初始化完成")

    def _require_main_window(self) -> toga.MainWindow:
        """获取已经初始化的主窗口"""
        if self._main_window is None:
            raise RuntimeError("主窗口尚未初始化")
        return self._main_window

    def _require_ui(self) -> QQMusicDownloaderUI:
        """获取已经初始化的UI组件"""
        if self.ui is None:
            raise RuntimeError("UI 尚未初始化")
        return self.ui

    def _require_downloader(self) -> QQMusicDownloader:
        """获取已经初始化的下载器"""
        if self.downloader is None:
            raise RuntimeError("请先保存有效的 Cookie")
        return self.downloader

    async def _show_dialog(
        self,
        factory: Callable[[str, str], object],
        title: str,
        message: str,
    ) -> None:
        window = self._require_main_window()
        dialog_method = getattr(window, "dialog", None)
        if callable(dialog_method):
            await dialog_method(factory(title, message))  # type: ignore[attr-defined]
            return

        attr_name_chars: list[str] = []
        for char in factory.__name__:
            if char.isupper() and attr_name_chars:
                attr_name_chars.append("_")
            attr_name_chars.append(char.lower())
        legacy_attr = "".join(attr_name_chars)

        legacy_method = getattr(window, legacy_attr, None)
        if callable(legacy_method):
            await legacy_method(title, message)  # type: ignore[attr-defined]
            return

        raise RuntimeError("当前 Toga 版本不支持对话框显示接口")

    async def _show_info(self, title: str, message: str) -> None:
        await self._show_dialog(toga.InfoDialog, title, message)

    async def _show_error(self, title: str, message: str) -> None:
        await self._show_dialog(toga.ErrorDialog, title, message)

    def startup(self):
        """应用程序启动入口"""
        try:
            # 创建主窗口
            window = toga.MainWindow(title="极简音乐下载器", size=(800, 600))
            self._main_window = window
            self.main_window = window

            # 初始化UI组件
            self.ui = QQMusicDownloaderUI(self)
            window.content = self.ui.create_main_box()
            window.show()
            logger.info("应用程序启动成功")
        except Exception as e:
            logger.error(f"应用程序启动失败: {e}")
            raise

    async def save_cookie(self, widget):
        """保存Cookie并初始化下载器"""
        try:
            ui = self._require_ui()

            cookie = (ui.cookie_input.value or "").strip()
            if not cookie:
                await self._show_info("提示", "请先输入Cookie")
                return

            # 初始化下载器
            self.downloader = QQMusicDownloader(cookie)
            download_path = self.downloader.get_download_path()
            ui.set_path_label(f"下载路径：{download_path}")

            # 验证Cookie
            ui.set_status_label("正在验证Cookie...")
            if await self.downloader.validate_cookie():
                ui.set_status_label("Cookie验证成功")
                await self._show_info(
                    "成功", f"Cookie验证成功!\n文件将保存到：{download_path}"
                )
            else:
                ui.set_status_label("Cookie验证失败")
                await self._show_error("错误", "Cookie验证失败，请确保Cookie有效")
        except Exception as e:
            logger.error(f"Cookie设置失败: {e}")
            ui = self._require_ui()
            ui.set_status_label("Cookie设置失败")
            await self._show_error("错误", f"设置失败: {str(e)}")

    def toggle_batch_mode(self, widget):
        """切换批量下载模式"""
        try:
            self.is_batch_mode = widget.value
            if not self.is_batch_mode:
                self.selected_indices.clear()
            self.update_table_selection_mode()
            logger.info(f"批量模式已切换为: {self.is_batch_mode}")
        except Exception as e:
            logger.error(f"切换批量模式失败: {e}")

    def update_table_selection_mode(self):
        """更新表格选择模式"""
        try:
            downloader = self.downloader
            if downloader and downloader.current_songs:
                self.update_song_list(downloader.current_songs)
        except Exception as e:
            logger.error(f"更新表格选择模式失败: {e}")

    async def search_songs(self, widget):
        """搜索歌曲"""
        try:
            ui = self._require_ui()
            window = self._require_main_window()
            downloader = self.downloader

            if downloader is None:
                await self._show_info("提示", "请先输入并保存Cookie")
                return

            keyword = (ui.search_input.value or "").strip()
            if not keyword:
                await self._show_info("提示", "请输入搜索关键词")
                return

            ui.set_status_label("正在搜索...")
            ui.update_progress(0)
            self.last_search = keyword

            songs = await downloader.search_and_show(
                keyword, window, self.update_song_list
            )

            if songs:
                ui.set_status_label(f"找到 {len(songs)} 首相关歌曲")
            else:
                ui.set_status_label("未找到相关歌曲")

        except Exception as e:
            logger.error(f"搜索失败: {e}")
            ui = self._require_ui()
            ui.set_status_label("搜索失败")
            await self._show_error("错误", f"搜索失败: {str(e)}")

    def update_song_list(self, songs: Sequence[dict[str, object]]) -> None:
        """更新歌曲列表显示"""
        try:
            ui = self._require_ui()
            table_data: list[dict[str, str]] = []
            for index, song in enumerate(songs):
                selectable = ui.batch_switch.value
                is_selected = (
                    index in self.selected_indices
                    if selectable
                    else (index == self.current_selected)
                )

                name = str(song.get("name", "未知歌曲"))
                singer = str(song.get("singer", "未知歌手"))
                album = str(song.get("album", "未知专辑"))

                table_data.append(
                    {
                        "selected": "[√]" if is_selected else "[ ]",
                        "index": str(index + 1),
                        "name": name,
                        "singer": singer,
                        "album": album,
                    }
                )

            ui.update_table_data(table_data)

        except Exception as e:
            logger.error(f"更新歌曲列表失败: {e}")
            self._require_ui().set_status_label("更新列表失败")

    def on_table_select(self, widget: toga.Table, **kwargs) -> None:
        """处理表格选择事件"""
        try:
            selection = widget.selection
            if selection is None:
                return

            row = cast(Row, selection)
            try:
                selected_index = int(row.index) - 1
            except (TypeError, ValueError):
                logger.warning("无法解析表格选择的索引")
                return

            ui = self._require_ui()

            if ui.batch_switch.value:
                if selected_index in self.selected_indices:
                    self.selected_indices.remove(selected_index)
                    logger.info(f"取消选择歌曲: {selected_index}")
                else:
                    self.selected_indices.add(selected_index)
                    logger.info(f"选择歌曲: {selected_index}")
            else:
                self.current_selected = selected_index
                self.selected_indices = {selected_index}

            downloader = self.downloader
            if downloader and downloader.current_songs:
                self.update_song_list(downloader.current_songs)

            logger.info(f"当前选中的歌曲索引: {sorted(list(self.selected_indices))}")

        except Exception as e:
            logger.error(f"处理选择时出错：{str(e)}")

    def _get_selected_quality(self) -> int:
        """获取选择的格式对应的质量值"""
        try:
            ui = self._require_ui()
            selection_value = ui.format_selection.value
            format_text = str(selection_value) if selection_value else "M4A"
            format_map = {
                "M4A": 1,  # 基础音质
                "MP3": 2,  # 实际上可能还是会得到m4a
                "FLAC": 3,  # 实际上可能还是会得到m4a
            }
            quality = format_map.get(format_text, 2)  # 默认使用M4A
            logger.info(f"选择的格式: {format_text} (quality={quality})")
            return quality
        except Exception as e:
            logger.error(f"获取格式选择失败: {e}")
            return 2  # 出错时默认使用M4A

    async def start_download(self, widget):
        """下载处理入口"""
        ui = self._require_ui()
        window = self._require_main_window()
        downloader = self.downloader

        if downloader is None:
            await self._show_info("提示", "请先输入并保存Cookie")
            return

        selection_value = ui.format_selection.value
        format_text = str(selection_value) if selection_value else "M4A"
        if format_text in {"MP3", "FLAC"}:
            await self._show_info(
                "温馨提示", "由于QQ音乐API限制，实际下载文件可能为M4A格式。\n"
            )

        try:
            ui.pause_button.enabled = True

            if ui.batch_switch.value:
                if not self.selected_indices:
                    await self._show_info("提示", "请选择要下载的歌曲")
                    return

                indices = sorted(list(self.selected_indices))
                logger.info(f"开始批量下载，选中索引: {indices}")

                await downloader.batch_download(
                    indices,
                    self._get_selected_quality(),
                    window,
                    self.update_batch_progress,
                    ui.progress_bar,
                    ui.status_label,
                )
            else:
                selection = ui.results_table.selection
                if selection is None:
                    await self._show_info("提示", "请选择要下载的歌曲")
                    return

                row = cast(Row, selection)
                try:
                    selected_index = int(row.index) - 1
                except (TypeError, ValueError):
                    await self._show_error("错误", "无法识别所选歌曲的序号")
                    return

                await self.start_single_download(
                    selected_index, self._get_selected_quality()
                )

        except Exception as e:
            logger.error(f"下载启动失败: {e}")
            await self._show_error("错误", f"下载失败: {str(e)}")

        finally:
            ui.pause_button.enabled = False
            ui.pause_button.text = "暂停下载"

    async def start_single_download(self, index: int, quality: int):
        """开始单曲下载"""
        try:
            ui = self._require_ui()
            window = self._require_main_window()
            downloader = self._require_downloader()

            ui.pause_button.enabled = True
            success = await downloader.download_song(
                index, quality, window, ui.progress_bar, ui.status_label
            )

            if success:
                ui.set_status_label("下载完成")
            else:
                ui.set_status_label("下载失败")

        except Exception as e:
            logger.error(f"下载出错: {e}")
            ui = self._require_ui()
            ui.set_status_label(f"下载出错: {str(e)}")

        finally:
            ui = self._require_ui()
            ui.pause_button.enabled = False

    async def update_batch_progress(self, message: str):
        """更新批量下载进度"""
        try:
            ui = self._require_ui()
            if "正在下载" in message:
                try:
                    current, total = message.split("(")[1].split(")")[0].split("/")
                    logger.info(f"批量下载进度: {int(current)}/{int(total)}")
                except (ValueError, IndexError):
                    logger.warning(f"批量进度解析失败: {message}")
                return

            ui.set_status_label(message)
        except Exception as e:
            logger.error(f"更新进度失败: {e}")

    def toggle_pause(self, widget):
        """切换暂停/继续状态"""
        try:
            if self.downloader and self.downloader.is_downloading:
                if widget.text == "暂停下载":
                    self.downloader.pause_all()
                    widget.text = "继续下载"
                    logger.info("下载已暂停")
                else:
                    self.downloader.resume_all()
                    widget.text = "暂停下载"
                    logger.info("下载已继续")
        except Exception as e:
            logger.error(f"切换暂停状态失败: {e}")

    async def choose_download_path(self, widget):
        """处理下载路径选择 - 这次用对了方法！"""
        try:
            # Toga正确的文件夹选择方法
            window = self._require_main_window()
            path_dialog = await window.select_folder_dialog("选择下载目录")

            if path_dialog:  # 用户选择了路径而不是像我逃避做家务一样按取消
                new_path = Path(path_dialog)

                # 确保选择的路径存在（就像确保我的咖啡杯里确实有咖啡一样重要）
                new_path.mkdir(parents=True, exist_ok=True)

                # 更新下载器的路径
                downloader = self.downloader
                if downloader:
                    downloader.api.base_dir = new_path
                    downloader.api.music_dir = new_path / "Music"
                    downloader.api.lyrics_dir = new_path / "Lyrics"

                    # 创建子目录（像建造音乐的小城堡）
                    downloader.api.music_dir.mkdir(exist_ok=True)
                    downloader.api.lyrics_dir.mkdir(exist_ok=True)

                    # 更新UI显示
                    self._require_ui().set_path_label(f"下载路径：{new_path}")

                    await self._show_info("成功", f"下载路径已更新为：\n{new_path}")
                else:
                    await self._show_info("提示", "请先设置Cookie后再选择下载路径")

        except Exception as e:
            logger.error(f"选择下载路径时出错: {e}")
            await self._show_error("错误", f"设置下载路径失败: {str(e)}")


def main():
    """程序入口点"""
    return QQMusicDownloaderApp()


if __name__ == "__main__":
    app = main()
    app.main_loop()

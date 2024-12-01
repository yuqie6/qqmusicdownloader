# app.py
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW
import asyncio
import json
import os
from pathlib import Path
import logging
from .downloader import QQMusicDownloader, DownloadTask

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class QQMusicDownloaderApp(toga.App):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.downloader = None
        self.download_tasks = []
        self.selected_tasks = set()
        self._setup_app_state()

    def _setup_app_state(self):
        """初始化应用状态"""
        self.is_batch_mode = False
        self.last_search = None
        self.download_queue = asyncio.Queue()

    def create_interface(self):
        """创建界面组件"""
        # 主容器
        main_box = toga.Box(style=Pack(direction=COLUMN, padding=10))

        # 下载路径显示
        self.path_box = self._create_path_section()
        
        # Cookie输入区域
        self.cookie_box = self._create_cookie_section()
        
        # 搜索区域
        self.search_box = self._create_search_section()
        
        # 结果显示区域
        self.results_box = self._create_results_section()
        
        # 下载控制区域
        self.control_box = self._create_control_section()
        
        # 状态显示区域
        self.status_box = self._create_status_section()

        # 组装界面
        main_box.add(self.path_box)
        main_box.add(self.cookie_box)
        main_box.add(self.search_box)
        main_box.add(self.results_box)
        main_box.add(self.control_box)
        main_box.add(self.status_box)

        return main_box

    def _create_path_section(self):
        """创建路径显示区域"""
        box = toga.Box(style=Pack(direction=COLUMN, padding=5))
        self.path_label = toga.Label('下载路径将在登录后显示',
                                   style=Pack(padding=(0, 5)))
        box.add(self.path_label)
        return box

    def _create_cookie_section(self):
        """创建Cookie输入区域"""
        box = toga.Box(style=Pack(direction=COLUMN, padding=5))
        self.cookie_input = toga.MultilineTextInput(
            placeholder='请输入QQ音乐Cookie',
            style=Pack(flex=1, height=60)
        )
        cookie_button = toga.Button('保存Cookie',
                                  on_press=self.save_cookie,
                                  style=Pack(padding=5))
        box.add(self.cookie_input)
        box.add(cookie_button)
        return box

    def _create_search_section(self):
        """创建搜索区域"""
        box = toga.Box(style=Pack(direction=ROW, padding=5))
        self.search_input = toga.TextInput(
            placeholder='请输入歌曲名称',
            style=Pack(flex=1)
        )
        search_button = toga.Button('搜索',
                                  on_press=self.search_songs,
                                  style=Pack(padding=5))
        box.add(self.search_input)
        box.add(search_button)
        return box

    def _create_results_section(self):
        """创建结果显示区域"""
        self.results_table = toga.Table(
            headings=['选择', '序号', '歌曲名', '歌手', '专辑'],
            data=[],
            style=Pack(flex=1, padding=5),
            on_select=self.on_table_select
        )
        return self.results_table

    def _create_control_section(self):
        """创建下载控制区域"""
        box = toga.Box(style=Pack(direction=ROW, padding=5))
        
        # 音质选择
        quality_items = ['标准品质 (128kbps)', '高品质 (320kbps)', '无损品质 (FLAC)']
        self.quality_selection = toga.Selection(
            items=quality_items,
            style=Pack(flex=1)
        )
        
        # 批量选择控制
        self.batch_switch = toga.Switch('批量模式',
                                      on_change=self.toggle_batch_mode)
        
        # 下载按钮
        self.download_button = toga.Button('下载选中歌曲',
                                         on_press=self.start_download,
                                         style=Pack(padding=5))
        
        # 暂停/继续按钮
        self.pause_button = toga.Button('暂停下载',
                                      on_press=self.toggle_pause,
                                      style=Pack(padding=5))
        self.pause_button.enabled = False

        box.add(self.quality_selection)
        box.add(self.batch_switch)
        box.add(self.download_button)
        box.add(self.pause_button)
        return box

    def _create_status_section(self):
        """创建状态显示区域"""
        box = toga.Box(style=Pack(direction=COLUMN, padding=5))
        self.progress_bar = toga.ProgressBar(style=Pack(flex=1))
        self.status_label = toga.Label('准备就绪',
                                     style=Pack(padding=(0, 5)))
        box.add(self.progress_bar)
        box.add(self.status_label)
        return box

    async def save_cookie(self, widget):
        """保存Cookie并初始化下载器"""
        cookie = self.cookie_input.value
        if not cookie:
            await self.main_window.dialog(
                toga.InfoDialog('提示', '请先输入Cookie')
            )
            return

        try:
            self.downloader = QQMusicDownloader(cookie)
            download_path = self.downloader.get_download_path()
            self.path_label.text = f'下载路径：{download_path}'

            # 验证Cookie
            if await self.downloader.validate_cookie():
                self.status_label.text = 'Cookie验证成功'
                await self.main_window.dialog(
                    toga.InfoDialog('成功', f'Cookie验证成功!\n文件将保存到：{download_path}')
                )
            else:
                self.status_label.text = 'Cookie验证失败'
                await self.main_window.dialog(
                    toga.ErrorDialog('错误', 'Cookie验证失败，请确保Cookie有效')
                )
        except Exception as e:
            logger.error(f"Cookie设置失败: {e}")
            await self.main_window.dialog(
                toga.ErrorDialog('错误', f'设置失败: {str(e)}')
            )

    def toggle_batch_mode(self, widget):
        """切换批量下载模式"""
        self.is_batch_mode = widget.value
        self.update_table_selection_mode()

    def update_table_selection_mode(self):
        """更新表格选择模式"""
        # 根据批量模式更新表格选择行为
        pass

    async def search_songs(self, widget):
        """搜索歌曲"""
        if not self.downloader:
            await self.main_window.dialog(
                toga.InfoDialog('提示', '请先输入并保存Cookie')
            )
            return

        keyword = self.search_input.value
        if not keyword:
            await self.main_window.dialog(
                toga.InfoDialog('提示', '请输入搜索关键词')
            )
            return

        self.status_label.text = '正在搜索...'
        self.progress_bar.value = 0
        self.last_search = keyword

        try:
            songs = await self.downloader.search_and_show(
                keyword,
                self.main_window,
                self.update_song_list
            )

            if songs:
                self.status_label.text = f'找到 {len(songs)} 首相关歌曲'
            else:
                self.status_label.text = '未找到相关歌曲'

        except Exception as e:
            logger.error(f"搜索失败: {e}")
            self.status_label.text = '搜索失败'
            await self.main_window.dialog(
                toga.ErrorDialog('错误', f'搜索失败: {str(e)}')
            )

    def update_song_list(self, songs):
        """更新歌曲列表显示"""
        self.results_table.data = [
            (False, str(i+1), song['name'], song['singer'], song['album'])
            for i, song in enumerate(songs)
        ]


    def on_table_select(self, widget, row=None):
        """处理表格选择事件"""
        if row and not self.is_batch_mode:
            try:
                # 获取选中行的序号，并转换为索引
                selected_index = int(row.序号) - 1
                song = self.downloader.current_songs[selected_index]
                self.status_label.text = f"已选择：{song['name']} - {song['singer']}"
            except Exception as e:
                logger.error(f"选择处理失败: {e}")

    async def start_download(self, widget):
        """开始下载"""
        if not self.results_table.selection:
            await self.main_window.dialog(
                toga.InfoDialog('提示', '请选择要下载的歌曲')
            )
            return

        quality_text = self.quality_selection.value
        quality_map = {
            '标准品质 (128kbps)': 1,
            '高品质 (320kbps)': 2,
            '无损品质 (FLAC)': 3
        }
        quality = quality_map.get(quality_text, 1)

        try:
            if self.is_batch_mode:
                # 使用列表推导式获取选中的歌曲序号，减1得到索引
                indices = [int(row.序号) - 1 for row in self.results_table.data if row.选择]
                await self.start_batch_download(indices, quality)
            else:
                # 获取选中行的序号，并转换为索引（减1，因为序号从1开始，索引从0开始）
                selected_index = int(self.results_table.selection.序号) - 1
                await self.start_single_download(selected_index, quality)

        except Exception as e:
            logger.error(f"下载启动失败: {e}")
            await self.main_window.dialog(
                toga.ErrorDialog('错误', f'下载启动失败: {str(e)}')
            )


    async def start_single_download(self, index: int, quality: int):
        """开始单曲下载"""
        self.pause_button.enabled = True
        await self.downloader.download_song(
            index,
            quality,
            self.main_window,
            self.progress_bar,
            self.status_label
        )
        self.pause_button.enabled = False

    async def start_batch_download(self, indices: list, quality: int):
        """开始批量下载"""
        self.pause_button.enabled = True
        await self.downloader.batch_download(
            indices,
            quality,
            self.main_window,
            self.update_batch_progress
        )
        self.pause_button.enabled = False

    def update_batch_progress(self, message: str):
        """更新批量下载进度"""
        self.status_label.text = message

    def toggle_pause(self, widget):
        """切换暂停/继续状态"""
        if self.downloader.is_downloading:
            if widget.label == '暂停下载':
                self.downloader.pause_all()
                widget.label = '继续下载'
            else:
                self.downloader.resume_all()
                widget.label = '暂停下载'

    def startup(self):
        """应用程序启动入口"""
        self.main_window = toga.MainWindow(
            title='QQ音乐下载器',
            size=(800, 600)
        )
        self.main_window.content = self.create_interface()
        self.main_window.show()

def main():
    """程序入口点"""
    return QQMusicDownloaderApp('QQ音乐下载器',
                              'org.example.qqmusicdownloader')

if __name__ == '__main__':
    app = main()
    app.main_loop()
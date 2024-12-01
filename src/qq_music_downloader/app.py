# app.py
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW
import asyncio
import json
import os
from pathlib import Path
import logging
from .downloader import QQMusicDownloader

# 配置日志记录
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class QQMusicDownloaderApp(toga.App):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.downloader = None
        self.last_search_keyword = None
        logger.info("应用程序初始化完成")

    def save_cookie(self, widget):
        """保存Cookie并初始化下载器"""
        cookie = self.cookie_input.value
        if not cookie:
            self.main_window.info_dialog(
                '提示',
                '请先输入Cookie'
            )
            return

        logger.info("正在初始化下载器...")
        self.downloader = QQMusicDownloader(cookie)

        # 更新下载路径显示
        download_path = self.downloader.get_download_path()
        self.path_label.text = f'下载路径：{download_path}'
        logger.info(f"下载路径已设置: {download_path}")

        # 验证Cookie并提示用户
        asyncio.create_task(self._validate_and_notify_cookie())

    async def _validate_and_notify_cookie(self):
        """验证Cookie并通知用户结果"""
        try:
            if await self.downloader.validate_cookie():
                logger.info("Cookie验证成功")
                download_path = self.downloader.get_download_path()
                await self.main_window.info_dialog(
                    '成功',
                    'Cookie验证成功！\n\n'
                    f'文件将保存到：{download_path}\n\n'
                    '现在可以开始搜索歌曲了！'
                )
                self.progress_label.text = 'Cookie验证成功，可以开始使用了！'
            else:
                logger.error("Cookie验证失败")
                await self.main_window.error_dialog(
                    '错误',
                    'Cookie验证失败，请确保：\n\n'
                    '1. 已在浏览器中登录QQ音乐\n'
                    '2. Cookie复制完整\n'
                    '3. Cookie未过期\n\n'
                    '获取方法：\n'
                    '1. 打开浏览器访问 y.qq.com\n'
                    '2. 按F12打开开发者工具\n'
                    '3. 在Network标签页中找到任意请求\n'
                    '4. 在Headers中找到Cookie并复制完整内容'
                )
                self.progress_label.text = 'Cookie验证失败，请重试'
        except Exception as e:
            logger.error(f"Cookie验证过程出错: {e}")
            await self.main_window.error_dialog(
                '错误',
                f'验证过程出错: {str(e)}'
            )

    async def search_songs(self, widget):
        """搜索歌曲并显示结果"""
        if not self.downloader:
            await self.main_window.info_dialog(
                '提示',
                '请先输入并保存Cookie'
            )
            return

        keyword = self.search_input.value
        if not keyword:
            await self.main_window.info_dialog(
                '提示',
                '请输入搜索关键词'
            )
            return

        self.last_search_keyword = keyword
        logger.info(f"开始搜索: {keyword}")
        self.progress_label.text = '正在搜索...'
        self.progress_bar.value = 0

        try:
            songs = await self.downloader.search_and_show(
                keyword,
                self.main_window,
                self._update_song_list
            )

            if songs:
                self.progress_label.text = f'找到 {len(songs)} 首相关歌曲'
            else:
                self.progress_label.text = '未找到相关歌曲'

        except Exception as e:
            logger.error(f"搜索过程出错: {e}")
            self.progress_label.text = '搜索失败'
            await self.main_window.error_dialog(
                '错误',
                f'搜索失败: {str(e)}'
            )

    def _update_song_list(self, songs):
        """更新歌曲列表显示"""
        self.results_table.data = [
            (str(i+1), song['name'], song['singer'], song['album'])
            for i, song in enumerate(songs)
        ]

    def on_table_select(self, widget, row=None, **kwargs):
        """处理表格行选择事件"""
        if row:
            try:
                selected_index = self.results_table.data.index(row)
                if 0 <= selected_index < len(self.downloader.current_songs):
                    selected_song = self.downloader.current_songs[selected_index]
                    self.progress_label.text = f"已选择：{selected_song['name']} - {selected_song['singer']}"
                    logger.info(f"已选择歌曲: {selected_song['name']}")
            except Exception as e:
                logger.error(f"选择处理出错: {e}")

    async def download_selected(self, widget):
        """下载选中的歌曲"""
        if not self.results_table.selection:
            await self.main_window.info_dialog(
                '提示',
                '请先选择要下载的歌曲'
            )
            return

        try:
            selected_row = self.results_table.selection
            selected_index = self.results_table.data.index(selected_row)

            # 获取音质设置
            quality_text = self.quality_selection.value
            quality_map = {
                '标准品质 (128kbps)': 1,
                '高品质 (320kbps)': 2,
                '无损品质 (FLAC)': 3
            }
            quality = quality_map.get(quality_text, 1)

            # 开始下载
            logger.info(f"开始下载，音质: {quality_text}")
            success = await self.downloader.download_song(
                selected_index,
                quality,
                self.main_window,
                self.progress_bar,
                self.progress_label
            )

            if success:
                self.progress_bar.value = self.progress_bar.max
        except Exception as e:
            logger.error(f"下载过程出错: {e}")
            await self.main_window.error_dialog(
                '错误',
                f'下载过程出错: {str(e)}'
            )
            self.progress_label.text = '下载失败'

    def startup(self):
        """初始化应用程序界面"""
        logger.info("开始初始化界面")

        # 创建主容器
        main_box = toga.Box(style=Pack(direction=COLUMN, padding=10))

        # 添加下载路径显示
        path_box = toga.Box(style=Pack(direction=COLUMN, padding=5))
        self.path_label = toga.Label(
            '下载路径将在登录后显示',
            style=Pack(padding=(0, 5))
        )
        path_box.add(self.path_label)

        # 创建Cookie输入区域
        cookie_box = toga.Box(style=Pack(direction=COLUMN, padding=5))
        self.cookie_input = toga.MultilineTextInput(
            placeholder='请输入QQ音乐Cookie',
            style=Pack(flex=1, height=60)
        )
        cookie_button = toga.Button(
            '保存Cookie',
            on_press=self.save_cookie,
            style=Pack(padding=5)
        )
        cookie_box.add(self.cookie_input)
        cookie_box.add(cookie_button)

        # 创建搜索区域
        search_box = toga.Box(style=Pack(direction=ROW, padding=5))
        self.search_input = toga.TextInput(
            placeholder='请输入歌曲名称',
            style=Pack(flex=1)
        )
        search_button = toga.Button(
            '搜索',
            on_press=self.search_songs,
            style=Pack(padding=5)
        )
        search_box.add(self.search_input)
        search_box.add(search_button)

        # 创建结果显示表格
        self.results_table = toga.Table(
            headings=['序号', '歌曲名', '歌手', '专辑'],
            data=[],
            style=Pack(flex=1, padding=5),
            on_select=self.on_table_select
        )

        # 创建进度显示区域
        self.progress_box = toga.Box(style=Pack(direction=COLUMN, padding=5))
        self.progress_bar = toga.ProgressBar(style=Pack(flex=1))
        self.progress_label = toga.Label(
            '准备就绪',
            style=Pack(padding=(0, 5))
        )
        self.progress_box.add(self.progress_bar)
        self.progress_box.add(self.progress_label)

        # 创建下载选项区域
        quality_box = toga.Box(style=Pack(direction=ROW, padding=5))
        quality_items = ['标准品质 (128kbps)', '高品质 (320kbps)', '无损品质 (FLAC)']
        self.quality_selection = toga.Selection(
            items=quality_items,
            style=Pack(flex=1)
        )
        self.quality_selection.value = quality_items[0]

        download_button = toga.Button(
            '下载选中歌曲',
            on_press=self.download_selected,
            style=Pack(padding=5)
        )
        quality_box.add(self.quality_selection)
        quality_box.add(download_button)

        # 添加所有组件到主容器
        main_box.add(path_box)
        main_box.add(cookie_box)
        main_box.add(search_box)
        main_box.add(self.results_table)
        main_box.add(self.progress_box)
        main_box.add(quality_box)

        # 创建主窗口
        self.main_window = toga.MainWindow(
            title='极简音乐下载器',
            size=(800, 600)
        )
        self.main_window.content = main_box
        self.main_window.show()
        logger.info("界面初始化完成")

def main():
    """应用程序入口点"""
    return QQMusicDownloaderApp('极简音乐下载器', 'https://yuqie6.github.io/qqmusicdownloader')

if __name__ == '__main__':
    app = main()
    app.main_loop()

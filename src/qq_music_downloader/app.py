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
from .ui import QQMusicDownloaderUI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class QQMusicDownloaderApp(toga.App):
    def __init__(self, *args, **kwargs):
        formal_name = '极简音乐下载器'
        app_id = 'com.yuqie.qqmusicdownloader'
        author = 'yuqie6'
        version = '1.2.0'
        description = '一款可以下载QQ音乐里面的歌曲的软件'

        super().__init__(
            formal_name=formal_name,
            app_id=app_id,
            author=author,
            version=version,
            description=description,
            *args, 
            **kwargs
        )
        
        # 初始化基本属性
        self.downloader = None
        self.download_tasks = []
        self.selected_indices = set()
        self.download_task = None
        self.current_selected = None
        self._setup_app_state()

    def _setup_app_state(self):
        """初始化应用状态"""
        self.is_batch_mode = False
        self.last_search = None
        self.download_queue = asyncio.Queue()
        logger.info("应用状态初始化完成")

    def startup(self):
        """应用程序启动入口"""
        try:
            # 创建主窗口
            self.main_window = toga.MainWindow(
                title='极简音乐下载器',
                size=(800, 600)
            )
            
            # 初始化UI组件
            self.ui = QQMusicDownloaderUI(self)
            self.main_window.content = self.ui.create_main_box()
            self.main_window.show()
            logger.info("应用程序启动成功")
        except Exception as e:
            logger.error(f"应用程序启动失败: {e}")
            raise

    async def save_cookie(self, widget):
        """保存Cookie并初始化下载器"""
        try:
            cookie = self.ui.cookie_input.value
            if not cookie:
                await self.main_window.dialog(
                    toga.InfoDialog('提示', '请先输入Cookie')
                )
                return

            # 初始化下载器
            self.downloader = QQMusicDownloader(cookie)
            download_path = self.downloader.get_download_path()
            self.ui.set_path_label(f'下载路径：{download_path}')

            # 验证Cookie
            self.ui.set_status_label('正在验证Cookie...')
            if await self.downloader.validate_cookie():
                self.ui.set_status_label('Cookie验证成功')
                await self.main_window.dialog(
                    toga.InfoDialog('成功', f'Cookie验证成功!\n文件将保存到：{download_path}')
                )
            else:
                self.ui.set_status_label('Cookie验证失败')
                await self.main_window.dialog(
                    toga.ErrorDialog('错误', 'Cookie验证失败，请确保Cookie有效')
                )
        except Exception as e:
            logger.error(f"Cookie设置失败: {e}")
            self.ui.set_status_label('Cookie设置失败')
            await self.main_window.dialog(
                toga.ErrorDialog('错误', f'设置失败: {str(e)}')
            )

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
            if hasattr(self.downloader, 'current_songs'):
                self.update_song_list(self.downloader.current_songs)
        except Exception as e:
            logger.error(f"更新表格选择模式失败: {e}")

    async def search_songs(self, widget):
        """搜索歌曲"""
        try:
            if not self.downloader:
                await self.main_window.dialog(
                    toga.InfoDialog('提示', '请先输入并保存Cookie')
                )
                return

            keyword = self.ui.search_input.value
            if not keyword:
                await self.main_window.dialog(
                    toga.InfoDialog('提示', '请输入搜索关键词')
                )
                return

            self.ui.set_status_label('正在搜索...')
            self.ui.update_progress(0)
            self.last_search = keyword

            songs = await self.downloader.search_and_show(
                keyword,
                self.main_window,
                self.update_song_list
            )

            if songs:
                self.ui.set_status_label(f'找到 {len(songs)} 首相关歌曲')
            else:
                self.ui.set_status_label('未找到相关歌曲')

        except Exception as e:
            logger.error(f"搜索失败: {e}")
            self.ui.set_status_label('搜索失败')
            await self.main_window.dialog(
                toga.ErrorDialog('错误', f'搜索失败: {str(e)}')
            )

    def update_song_list(self, songs):
        """更新歌曲列表显示"""
        try:
            table_data = []
            for i, song in enumerate(songs):
                is_selected = i in self.selected_indices if self.ui.batch_switch.value else (i == self.current_selected)
                row = {
                    'selected': '[√]' if is_selected else '[ ]',
                    'index': str(i+1),
                    'name': song['name'],
                    'singer': song['singer'],
                    'album': song['album']
                }
                table_data.append(row)
            
            self.ui.update_table_data(table_data)
            
        except Exception as e:
            logger.error(f"更新歌曲列表失败: {e}")
            self.ui.set_status_label('更新列表失败')

    def on_table_select(self, widget, **kwargs):
        """处理表格选择事件"""
        try:
            selection = widget.selection
            if not selection:
                return
                
            selected_index = int(selection.index) - 1
            
            if self.ui.batch_switch.value:
                if selected_index in self.selected_indices:
                    self.selected_indices.remove(selected_index)
                    logger.info(f"取消选择歌曲: {selected_index}")
                else:
                    self.selected_indices.add(selected_index)
                    logger.info(f"选择歌曲: {selected_index}")
            else:
                self.current_selected = selected_index
                self.selected_indices = {selected_index}
            
            if hasattr(self.downloader, 'current_songs'):
                self.update_song_list(self.downloader.current_songs)
            
            logger.info(f"当前选中的歌曲索引: {sorted(list(self.selected_indices))}")
            
        except Exception as e:
            logger.error(f"处理选择时出错：{str(e)}")

    def _get_selected_quality(self):
        """获取选择的格式对应的质量值"""
        try:
            format_text = self.ui.format_selection.value
            format_map = {
                'M4A': 1,   # 基础音质
                'MP3': 2,   # 实际上可能还是会得到m4a
                'FLAC': 3   # 实际上可能还是会得到m4a
            }
            quality = format_map.get(format_text, 2)  # 默认使用M4A
            logger.info(f"选择的格式: {format_text} (quality={quality})")
            return quality
        except Exception as e:
            logger.error(f"获取格式选择失败: {e}")
            return 2  # 出错时默认使用M4A
  
    async def start_download(self, widget):
        """下载处理入口"""
        if self.ui.format_selection.value in ['MP3', 'FLAC']:
            await self.main_window.dialog(
                toga.InfoDialog(
                    '温馨提示', 
                    '由于QQ音乐API限制，实际下载文件可能为M4A格式。\n'
                )
            )
       
        try:
            self.ui.pause_button.enabled = True
            
            if self.ui.batch_switch.value:
                if not self.selected_indices:
                    await self.main_window.dialog(
                        toga.InfoDialog('提示', '请选择要下载的歌曲')
                    )
                    return
                
                indices = sorted(list(self.selected_indices))
                logger.info(f"开始批量下载，选中索引: {indices}")
                
                await self.downloader.batch_download(
                    indices,
                    self._get_selected_quality(),
                    self.main_window,
                    self.update_batch_progress,
                    self.ui.progress_bar,
                    self.ui.status_label
                )
            else:
                if not self.ui.results_table.selection:
                    await self.main_window.dialog(
                        toga.InfoDialog('提示', '请选择要下载的歌曲')
                    )
                    return
                
                selected_index = int(self.ui.results_table.selection.index) - 1
                await self.start_single_download(
                    selected_index,
                    self._get_selected_quality()
                )
                
        except Exception as e:
            logger.error(f"下载启动失败: {e}")
            await self.main_window.dialog(
                toga.ErrorDialog('错误', f'下载失败: {str(e)}')
            )
            
        finally:
            self.ui.pause_button.enabled = False
            self.ui.pause_button.text = '暂停下载'

    async def start_single_download(self, index: int, quality: int):
        """开始单曲下载"""
        try:
            self.ui.pause_button.enabled = True
            success = await self.downloader.download_song(
                index,
                quality,
                self.main_window,
                self.ui.progress_bar,
                self.ui.status_label
            )
            
            if success:
                self.ui.set_status_label("下载完成")
            else:
                self.ui.set_status_label("下载失败")
                
        except Exception as e:
            logger.error(f"下载出错: {e}")
            self.ui.set_status_label(f"下载出错: {str(e)}")
            
        finally:
            self.ui.pause_button.enabled = False

    async def update_batch_progress(self, message: str):
        """更新批量下载进度"""
        try:
            self.ui.set_status_label(message)
            if "正在下载" in message:
                current, total = message.split("(")[1].split(")")[0].split("/")
                progress = (int(current) / int(total)) * 100
                self.ui.update_progress(progress)
                logger.info(f"批量下载进度: {progress}%")
        except Exception as e:
            logger.error(f"更新进度失败: {e}")

    def toggle_pause(self, widget):
        """切换暂停/继续状态"""
        try:
            if self.downloader and self.downloader.is_downloading:
                if widget.text == '暂停下载':
                    self.downloader.pause_all()
                    widget.text = '继续下载'
                    logger.info("下载已暂停")
                else:
                    self.downloader.resume_all()
                    widget.text = '暂停下载'
                    logger.info("下载已继续")
        except Exception as e:
            logger.error(f"切换暂停状态失败: {e}")

    async def choose_download_path(self, widget):
        """处理下载路径选择 - 这次用对了方法！"""
        try:
            # Toga正确的文件夹选择方法
            path_dialog = await self.main_window.select_folder_dialog(
                "选择下载目录"
            )
            
            if path_dialog:  # 用户选择了路径而不是像我逃避做家务一样按取消
                new_path = Path(path_dialog)
                
                # 确保选择的路径存在（就像确保我的咖啡杯里确实有咖啡一样重要）
                new_path.mkdir(parents=True, exist_ok=True)
                
                # 更新下载器的路径
                if self.downloader:
                    self.downloader.api.base_dir = new_path
                    self.downloader.api.music_dir = new_path / 'Music'
                    self.downloader.api.lyrics_dir = new_path / 'Lyrics'
                    
                    # 创建子目录（像建造音乐的小城堡）
                    self.downloader.api.music_dir.mkdir(exist_ok=True)
                    self.downloader.api.lyrics_dir.mkdir(exist_ok=True)
                    
                    # 更新UI显示
                    self.ui.set_path_label(f'下载路径：{new_path}')
                    
                    await self.main_window.info_dialog(
                        '成功',
                        f'下载路径已更新为：\n{new_path}'
                    )
                else:
                    await self.main_window.info_dialog(
                        '提示',
                        '请先设置Cookie后再选择下载路径'
                    )
        
        except Exception as e:
            logger.error(f"选择下载路径时出错: {e}")
            await self.main_window.error_dialog(
                '错误',
                f'设置下载路径失败: {str(e)}'
            )
            
def main():
    """程序入口点"""
    return QQMusicDownloaderApp()

if __name__ == '__main__':
    app = main()
    app.main_loop()
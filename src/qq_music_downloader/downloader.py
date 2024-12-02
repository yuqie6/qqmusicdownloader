# downloader.py
import asyncio
import logging
from typing import List, Dict, Optional, Callable
import toga
from .qq_music_api import QQMusicAPI
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class DownloadConfig:
    """下载配置"""
    max_concurrent: int = 3
    chunk_size: int = 8192
    retry_times: int = 3
    retry_delay: float = 1.0
    default_quality: int = 1

@dataclass
class ProgressInfo:
    """下载进度信息"""
    filename: str = ""
    current: int = 0
    total: int = 0
    speed: float = 0
    eta: float = 0
    status: str = "pending"

class DownloadTask:
    """下载任务"""
    def __init__(self, song_info: Dict, quality: int):
        self.song_info = song_info
        self.quality = quality
        self.progress = ProgressInfo(
            filename=f"{song_info['name']} - {song_info['singer']}"
        )
        self.start_time = None
        self.pause_event = asyncio.Event()
        self.pause_event.set()

    def pause(self):
        self.pause_event.clear()

    def resume(self):
        self.pause_event.set()

class QQMusicDownloader:
    """QQ音乐下载器核心类"""

    def __init__(self, cookie: str):
        self.api = QQMusicAPI(cookie)
        self.config = DownloadConfig()
        self.current_songs = []
        self.download_tasks = {}
        self.is_downloading = False
        self.download_lock = asyncio.Lock()  # Add a lock for download state
        self.download_semaphore = asyncio.Semaphore(self.config.max_concurrent)
        self._download_queue = asyncio.Queue()
        self._current_task = None
        logger.info("下载器初始化完成")

    def get_download_path(self) -> str:
        return self.api.get_download_path()

    async def validate_cookie(self) -> bool:
        logger.info("开始验证Cookie...")
        is_valid = await self.api.validate_cookie()
        logger.info(f"Cookie验证结果: {'有效' if is_valid else '无效'}")
        return is_valid

    async def search_and_show(self, keyword: str, window: toga.Window,
                            callback_fn: Callable[[List[Dict]], None]) -> List[Dict]:
        """搜索歌曲并显示结果"""
        logger.info(f"开始搜索关键词: {keyword}")
        try:
            if not await self.validate_cookie():
                logger.error("Cookie验证失败")
                await window.error_dialog(
                    '错误',
                    'Cookie无效或已过期，请重新输入有效的Cookie'
                )
                return []

            songs = await self.api.search_song(keyword)
            self.current_songs = songs

            if not songs:
                logger.info(f"未找到相关歌曲: {keyword}")
                await window.info_dialog('提示', f'未找到相关歌曲: {keyword}')
                return []

            logger.info(f"找到 {len(songs)} 首相关歌曲")
            callback_fn(songs)
            return songs

        except Exception as e:
            logger.error(f"搜索过程出错: {e}")
            await window.error_dialog('错误', f'搜索失败: {str(e)}')
            return []

    async def _download_with_progress(self, task: DownloadTask, 
                                    progress_bar=None, 
                                    progress_label=None) -> bool:
        """带进度的下载实现"""
        task.start_time = datetime.now()
        song_url = await self.api.get_song_url(
            task.song_info['songmid'],
            task.quality
        )
        
        if not song_url:
            return False

        try:
            task.progress.status = "downloading"  # 设置任务状态为下载中
            success = await self.api.download_with_lyrics(
                song_url,
                task.progress.filename,
                task.quality,
                task.song_info['songmid'],
                progress_bar,
                progress_label,
                task.pause_event
            )
            
            if success:
                task.progress.status = "completed"
            else:
                task.progress.status = "failed"
            self.is_downloading = False
            return success

        except asyncio.CancelledError:
            task.progress.status = "cancelled"
            raise
        except Exception as e:
            task.progress.status = "failed"
            logger.error(f"下载失败: {e}")
            return False
        
        

    async def download_song(self, song_index: int, quality: int,
                          window: toga.Window, progress_bar=None,
                          progress_label=None, suppress_dialogs=False) -> bool:
        """下载单首歌曲"""
        async with self.download_lock:
            if self.is_downloading and not suppress_dialogs:
                logger.warning("已有下载任务在进行中")
                await window.dialog(
                    toga.InfoDialog('提示', '当前已有下载任务在进行中')
                )
                return False

            try:
                if not suppress_dialogs:
                    self.is_downloading = True

                if not (0 <= song_index < len(self.current_songs)):
                    logger.error(f"无效的歌曲索引: {song_index}")
                    if not suppress_dialogs:
                        await window.dialog(
                            toga.ErrorDialog('错误', '无效的歌曲选择')
                        )
                    return False

                task = DownloadTask(self.current_songs[song_index], quality)
                self.download_tasks[song_index] = task

                success = await self._download_with_progress(
                    task, progress_bar, progress_label
                )

                if success and not suppress_dialogs:
                    logger.info(f"歌曲下载成功: {task.progress.filename}")
                    await window.dialog(
                        toga.InfoDialog('成功', f'歌曲 {task.progress.filename} 下载完成')
                    )
                elif not success and not suppress_dialogs:
                    logger.error(f"歌曲下载失败: {task.progress.filename}")
                    await window.dialog(
                        toga.ErrorDialog('错误', f'歌曲 {task.progress.filename} 下载失败')
                    )

                return success

            finally:
                if not suppress_dialogs:
                    self.is_downloading = False
                    if progress_label:
                        progress_label.text = '准备就绪'
                    if progress_bar:
                        progress_bar.value = 0
  
    async def batch_download(self, song_indices: List[int], quality: int,
                           window: toga.Window, progress_callback: Callable = None,
                           progress_bar=None, status_label=None) -> bool:
        """批量下载歌曲"""
        async with self.download_lock:
            if self.is_downloading:
                logger.warning("已有下载任务在进行中")
                await window.dialog(
                    toga.InfoDialog('提示', '请等待当前下载任务完成')
                )
                return False

            try:
                self.is_downloading = True
                total_songs = len(song_indices)
                completed_songs = 0
                failed_songs = []

                if progress_callback:
                    progress_callback(f'开始下载 {total_songs} 首歌曲')

                # Create tasks for all songs
                tasks = []
                for index in song_indices:
                    song = self.current_songs[index]
                    song_name = f"{song['name']} - {song['singer']}"
                    
                    task = asyncio.create_task(
                        self._download_single_with_semaphore(
                            index, quality, window,
                            progress_bar, status_label,
                            f'({completed_songs + 1}/{total_songs}): {song_name}'
                        )
                    )
                    tasks.append(task)

                # Wait for all tasks to complete
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Process results
                for i, result in enumerate(results):
                    if isinstance(result, Exception):
                        failed_songs.append(song_indices[i])
                    elif result:
                        completed_songs += 1

                # Show final results
                if completed_songs == total_songs:
                    await window.dialog(
                        toga.InfoDialog('完成', f'全部 {total_songs} 首歌曲下载完成')
                    )
                else:
                    failed_count = len(failed_songs)
                    await window.dialog(
                        toga.InfoDialog(
                            '完成',
                            f'下载完成，成功 {completed_songs}/{total_songs} 首\n'
                            f'失败 {failed_count} 首'
                        )
                    )

                return completed_songs == total_songs

            except Exception as e:
                logger.error(f"批量下载出错: {e}")
                if progress_callback:
                    progress_callback(f'下载出错: {str(e)}')
                return False

            finally:
                self.is_downloading = False
                if status_label:
                    status_label.text = '准备就绪'
                if progress_bar:
                    progress_bar.value = 0
    
    async def _download_with_semaphore(self, task: DownloadTask, 
                                    window: toga.Window,
                                    progress_callback: Callable) -> bool:
        """使用信号量控制的下载实现"""
        async with self.download_semaphore:
            try:
                task.progress.status = "downloading"  # 设置任务状态为下载中
                if progress_callback:
                    progress_callback(f'正在下载: {task.progress.filename}')
                    
                success = await self._download_with_progress(
                    task,
                    progress_bar=None,
                    progress_label=None
                )
                return success
            except Exception as e:
                task.progress.status = "failed"
                logger.error(f"下载任务失败: {e}")
                return False


    async def _show_batch_results(self, window: toga.Window, 
                                success_count: int, total: int):
        """显示批量下载结果"""
        if success_count == total:
            logger.info(f"批量下载完成，全部成功: {total}/{total}")
            await window.info_dialog('完成', f'全部 {total} 首歌曲下载完成')
        else:
            logger.info(f"批量下载完成，部分成功: {success_count}/{total}")
            await window.info_dialog('完成', f'下载完成，成功 {success_count}/{total} 首')

    async def cancel_download(self):
        """取消当前的所有下载任务"""
        if self.is_downloading:
            logger.info("正在取消所有下载任务...")
            for task in self.download_tasks.values():
                if task.progress.status == "downloading":
                    task.pause()
            self.is_downloading = False
            logger.info("所有下载任务已取消")

    async def _download_single_with_semaphore(self, index: int, quality: int,
                                            window: toga.Window,
                                            progress_bar=None,
                                            status_label=None,
                                            progress_text=None) -> bool:
        """使用信号量控制的单曲下载"""
        async with self.download_semaphore:
            try:
                if status_label and progress_text:
                    status_label.text = f'下载中 {progress_text}'
                
                return await self.download_song(
                    index,
                    quality,
                    window,
                    progress_bar,
                    status_label,
                    suppress_dialogs=True  # Suppress individual dialogs in batch mode
                )
            except Exception as e:
                logger.error(f"下载失败: {e}")
                return False
            
    def pause_all(self):
        """暂停所有下载任务"""
        for task in self.download_tasks.values():
            task.pause()

    def resume_all(self):
        """恢复所有下载任务"""
        for task in self.download_tasks.values():
            task.resume()

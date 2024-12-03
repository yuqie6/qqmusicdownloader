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
        self.loop = asyncio.get_event_loop()
        self.global_pause_event = asyncio.Event()
        self.global_pause_event.set()  # 初始状态为未暂停
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
        try:
            # Get the song URL and verify it exists
            song_url = await self.api.get_song_url(
                task.song_info['songmid'],
                task.quality
            )
            
            if not song_url:
                logger.error(f"无法获取下载地址: {task.progress.filename}")
                return False

            # Add logging to track download progress
            logger.info(f"开始下载: {task.progress.filename}")
            logger.info(f"下载地址: {song_url}")
            
            task.progress.status = "downloading"
            
            # Update UI before starting download
            if progress_label:
                progress_label.text = f'正在下载: {task.progress.filename}'
            
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
                logger.info(f"下载完成: {task.progress.filename}")
            else:
                task.progress.status = "failed"
                logger.error(f"下载失败: {task.progress.filename}")
                
            return success

        except asyncio.CancelledError:
            task.progress.status = "cancelled"
            logger.warning(f"下载已取消: {task.progress.filename}")
            raise
        except Exception as e:
            task.progress.status = "failed"
            logger.error(f"下载发生错误: {task.progress.filename} - {str(e)}")
            return False

    async def download_song(self, song_index: int, quality: int,
                          window: toga.Window, progress_bar=None,
                          progress_label=None, suppress_dialogs=False) -> bool:
        """完整的下载流程实现"""
        async with self.download_lock:
            try:
                # 1. 基础检查
                if self.is_downloading and not suppress_dialogs:
                    logger.info("已有下载任务在进行中")
                    return False

                self.is_downloading = True
                if progress_label:
                    progress_label.text = '准备下载...'
                if progress_bar:
                    progress_bar.value = 0

                # 2. 获取歌曲信息
                song = self.current_songs[song_index]
                logger.info(f"准备下载歌曲: {song['name']} - {song['singer']}")

                # 3. 获取下载URL
                logger.info("正在获取下载地址...")
                song_url = await self.api.get_song_url(song['songmid'], quality)
                
                if not song_url:
                    logger.error("获取下载地址失败")
                    return False

                logger.info(f"成功获取下载地址: {song_url}")

                # 4. 创建并配置下载任务
                task = DownloadTask(song, quality)
                self.download_tasks[song_index] = task
                
                # 5. 直接执行下载，不使用额外的事件循环嵌套
                success = await self.api.download_with_lyrics(
                    song_url,
                    task.progress.filename,
                    quality,
                    song['songmid'],
                    progress_bar,
                    progress_label,
                    task.pause_event
                )

                if success:
                    logger.info(f"下载成功: {task.progress.filename}")
                    if not suppress_dialogs:
                        await window.dialog(
                            toga.InfoDialog('成功', f'歌曲 {task.progress.filename} 下载完成')
                        )
                else:
                    logger.error(f"下载失败: {task.progress.filename}")
                    if not suppress_dialogs:
                        await window.dialog(
                            toga.ErrorDialog('错误', f'歌曲 {task.progress.filename} 下载失败')
                        )

                return success

            except Exception as e:
                logger.error(f"下载过程发生错误: {str(e)}")
                return False

            finally:
                self.is_downloading = False
                if progress_label:
                    progress_label.text = '准备就绪'
                if progress_bar:
                    progress_bar.value = 0
                        
    async def batch_download(self, song_indices: List[int], quality: int,
                            window: toga.Window, progress_callback: Callable = None,
                            progress_bar=None, status_label=None) -> bool:
        async with self.download_lock:
            try:
                total_songs = len(song_indices)
                completed_songs = 0
                
                # 重置进度条
                if progress_bar:
                    progress_bar.value = 0
                    
                for current_index, index in enumerate(song_indices, 1):
                    logger.info(f"开始批量下载，选中歌曲索引: {song_indices}")
                    self.is_downloading = True
                    total_songs = len(song_indices)
                    completed_songs = 0
                    failed_songs = []

                    # 初始化进度条
                    if progress_bar:
                        progress_bar.value = 0

                    # 对每首歌进行下载
                    for current_index, index in enumerate(song_indices, 1):  # 使用enumerate从1开始计数
                        try:
                            song = self.current_songs[index]
                            song_name = f"{song['name']} - {song['singer']}"
                            
                            # 更新状态标签，显示当前正在下载第几首歌
                            if status_label:
                                status_label.text = f'下载中 ({current_index}/{total_songs}): {song_name}'
                            
                            # 获取下载URL
                            song_url = await self.api.get_song_url(song['songmid'], quality)
                            if not song_url:
                                failed_songs.append(song_name)
                                continue

                            # 创建下载任务
                            task = DownloadTask(song, quality)
                            self.download_tasks[index] = task
                            
                            # 执行下载，传入正确的进度信息
                            success = await self.api.download_with_lyrics(
                                song_url,
                                task.progress.filename,
                                quality,
                                song['songmid'],
                                progress_bar,
                                status_label,
                                [self.global_pause_event, task.pause_event]
                            )

                            if success:
                                completed_songs += 1
                                # 更新总体进度
                                if progress_bar:
                                    progress_bar.value = (completed_songs / total_songs) * 100
                                # 回调通知进度
                                if progress_callback:
                                    progress_callback(f'已完成 ({completed_songs}/{total_songs}): {song_name}')
                            else:
                                failed_songs.append(song_name)

                        except Exception as e:
                            logger.error(f"下载歌曲时出错: {str(e)}")
                            failed_songs.append(song_name)

                    # 显示最终结果
                    if failed_songs:
                        failed_str = '\n'.join(failed_songs)
                        await window.dialog(
                            toga.InfoDialog(
                                '下载完成',
                                f'完成 {completed_songs}/{total_songs} 首\n'
                                f'失败 {len(failed_songs)} 首：\n{failed_str}'
                            )
                        )
                    else:
                        await window.dialog(
                            toga.InfoDialog('完成', f'全部 {total_songs} 首歌曲下载完成')
                        )

                    return completed_songs == total_songs

            except Exception as e:
                    logger.error(f"批量下载过程中出错: {str(e)}")
                    if status_label:
                        status_label.text = f'下载出错: {str(e)}'
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
                                completed_songs: int, total_songs: int,
                                failed_songs: List[str]):
        """显示批量下载结果"""
        if completed_songs == total_songs:
            await window.dialog(
                toga.InfoDialog('完成', f'全部 {total_songs} 首歌曲下载完成')
            )
        else:
            failed_str = '\n'.join(failed_songs)
            await window.dialog(
                toga.InfoDialog(
                    '完成',
                    f'下载完成，成功 {completed_songs}/{total_songs} 首\n' +
                    f'失败 {len(failed_songs)} 首：\n{failed_str}'
                )
            )
   
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
        """Enhanced single download implementation with semaphore control"""
        async with self.download_semaphore:
            try:
                if status_label and progress_text:
                    status_label.text = f'下载中 {progress_text}'
                
                # Get song URL before starting download
                song = self.current_songs[index]
                song_url = await self.api.get_song_url(song['songmid'], quality)
                
                if not song_url:
                    logger.error(f"无法获取下载地址: {song['name']}")
                    return False
                
                return await self.download_song(
                    index,
                    quality,
                    window,
                    progress_bar,
                    status_label,
                    suppress_dialogs=True
                )
            except Exception as e:
                logger.error(f"单曲下载失败: {e}")
                return False
            
    def pause_all(self):
        """暂停所有下载任务"""
        logger.info("暂停所有下载任务")
        self.global_pause_event.clear()  # 清除事件，表示暂停
        # 同时暂停所有单独的下载任务
        for task in self.download_tasks.values():
            task.pause()
   
    def resume_all(self):
        """恢复所有下载任务"""
        logger.info("恢复所有下载任务")
        self.global_pause_event.set()  # 设置事件，表示继续
        # 同时恢复所有单独的下载任务
        for task in self.download_tasks.values():
            task.resume()
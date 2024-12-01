# downloader.py
import asyncio
import logging
from typing import List, Dict, Optional, Callable
import toga
from .qq_music_api import QQMusicAPI

logger = logging.getLogger(__name__)

class QQMusicDownloader:
    """QQ音乐下载器的核心类，处理下载逻辑和用户交互"""

    def __init__(self, cookie: str):
        """初始化下载器"""
        self.api = QQMusicAPI(cookie)
        self.current_songs = []  # 存储当前搜索结果
        self.current_download_task = None  # 当前下载任务
        self.is_downloading = False  # 下载状态标志
        logger.info("下载器初始化完成")

    def get_download_path(self) -> str:
        """获取下载目录路径"""
        return self.api.get_download_path()

    async def validate_cookie(self) -> bool:
        """验证Cookie是否有效"""
        logger.info("开始验证Cookie...")
        is_valid = await self.api.validate_cookie()
        logger.info(f"Cookie验证结果: {'有效' if is_valid else '无效'}")
        return is_valid

    async def search_and_show(self, keyword: str, window: toga.Window,
                            callback_fn: Callable[[List[Dict]], None]) -> List[Dict]:
        """搜索歌曲并显示结果"""
        logger.info(f"开始搜索关键词: {keyword}")
        try:
            # 首先验证Cookie
            if not await self.validate_cookie():
                logger.error("Cookie验证失败")
                await window.error_dialog(
                    '错误',
                    'Cookie无效或已过期，请重新输入有效的Cookie\n\n'
                    '获取方法：\n'
                    '1. 使用浏览器访问 y.qq.com\n'
                    '2. 登录您的QQ音乐账号\n'
                    '3. 按F12打开开发者工具\n'
                    '4. 在Network标签页中找到任意请求\n'
                    '5. 在Headers中找到Cookie并复制完整内容'
                )
                return []

            # 执行搜索
            songs = await self.api.search_song(keyword)
            self.current_songs = songs

            if not songs:
                logger.info(f"未找到相关歌曲: {keyword}")
                await window.info_dialog(
                    '提示',
                    f'未找到相关歌曲: {keyword}'
                )
                return []

            # 更新界面
            logger.info(f"找到 {len(songs)} 首相关歌曲")
            callback_fn(songs)
            return songs

        except Exception as e:
            logger.error(f"搜索过程出错: {e}")
            await window.error_dialog(
                '错误',
                f'搜索失败: {str(e)}'
            )
            return []

    async def download_song(self, song_index: int, quality: int,
                          window: toga.Window, progress_bar=None,
                          progress_label=None) -> bool:
        """下载单首歌曲"""
        if self.is_downloading:
            logger.warning("已有下载任务在进行中")
            await window.info_dialog(
                '提示',
                '当前已有下载任务在进行中'
            )
            return False

        try:
            self.is_downloading = True

            if not (0 <= song_index < len(self.current_songs)):
                logger.error(f"无效的歌曲索引: {song_index}")
                await window.error_dialog(
                    '错误',
                    '无效的歌曲选择'
                )
                return False

            selected_song = self.current_songs[song_index]
            song_name = f"{selected_song['name']} - {selected_song['singer']}"
            logger.info(f"准备下载歌曲: {song_name}")

            # 获取下载链接
            if progress_label:
                progress_label.text = '正在获取下载链接...'

            song_url = await self.api.get_song_url(
                selected_song['songmid'],
                quality
            )

            if not song_url:
                logger.error(f"无法获取下载链接: {song_name}")
                await window.error_dialog(
                    '错误',
                    f'无法获取下载链接: {song_name}'
                )
                return False

            # 开始下载
            logger.info(f"开始下载歌曲: {song_name}")
            success = await self.api.download_with_lyrics(
                song_url,
                song_name,
                quality,
                selected_song['songmid'],
                progress_bar,
                progress_label
            )

            if success:
                logger.info(f"歌曲下载成功: {song_name}")
                await window.info_dialog(
                    '成功',
                    f'歌曲 {song_name} 下载完成'
                )
                return True
            else:
                logger.error(f"歌曲下载失败: {song_name}")
                await window.error_dialog(
                    '错误',
                    f'歌曲 {song_name} 下载失败'
                )
                return False

        except Exception as e:
            logger.error(f"下载过程出错: {e}")
            await window.error_dialog(
                '错误',
                f'下载过程出错: {str(e)}'
            )
            return False
        finally:
            self.is_downloading = False
            if progress_label:
                progress_label.text = '准备就绪'

    async def batch_download(self, song_indices: List[int], quality: int,
                           window: toga.Window, progress_callback: Callable = None) -> bool:
        """批量下载歌曲"""
        if self.is_downloading:
            logger.warning("已有下载任务在进行中")
            await window.info_dialog(
                '提示',
                '当前已有下载任务在进行中'
            )
            return False

        try:
            self.is_downloading = True
            total = len(song_indices)
            success_count = 0

            for i, index in enumerate(song_indices, 1):
                if not (0 <= index < len(self.current_songs)):
                    logger.warning(f"跳过无效的歌曲索引: {index}")
                    continue

                if progress_callback:
                    progress_callback(f'正在下载第 {i}/{total} 首歌曲...')

                success = await self.download_song(index, quality, window)
                if success:
                    success_count += 1

            if success_count == total:
                logger.info(f"批量下载完成，全部成功: {total}/{total}")
                await window.info_dialog(
                    '完成',
                    f'全部 {total} 首歌曲下载完成'
                )
                return True
            else:
                logger.info(f"批量下载完成，部分成功: {success_count}/{total}")
                await window.info_dialog(
                    '完成',
                    f'下载完成，成功 {success_count}/{total} 首'
                )
                return False

        except Exception as e:
            logger.error(f"批量下载出错: {e}")
            await window.error_dialog(
                '错误',
                f'批量下载出错: {str(e)}'
            )
            return False
        finally:
            self.is_downloading = False

    async def cancel_download(self):
        """取消当前下载任务"""
        if self.current_download_task and not self.current_download_task.done():
            logger.info("正在取消下载任务...")
            self.current_download_task.cancel()
            try:
                await self.current_download_task
            except asyncio.CancelledError:
                logger.info("下载任务已成功取消")
            finally:
                self.is_downloading = False
                logger.info("下载状态已重置")

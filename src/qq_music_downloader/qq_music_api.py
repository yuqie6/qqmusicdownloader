# qq_music_api.py
import aiohttp
import json
import logging
import random
from pathlib import Path
import os
import asyncio
import aiofiles
from typing import Dict, List, Optional, Tuple
import base64
import re
from dataclasses import dataclass
from datetime import datetime
import hashlib

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class APIConfig:
    """API配置"""
    timeout: int = 30
    retry_times: int = 3
    retry_delay: float = 1.0
    chunk_size: int = 8192

class QQMusicAPI:
    """QQ音乐API处理类"""

    def __init__(self, cookie: str):
        self.cookie = self._clean_cookie(cookie)
        self.config = APIConfig()
        self._setup_headers()
        self._setup_directories()
        self._setup_session()

    def _setup_headers(self):
        """初始化请求头"""
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Cookie': self.cookie,
            'Referer': 'https://y.qq.com',
            'Accept': 'application/json',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
            'Origin': 'https://y.qq.com'
        }
    async def validate_cookie(self) -> bool:
        """验证Cookie是否有效
        
        通过尝试访问QQ音乐API来验证Cookie的有效性
        
        Returns:
            bool: Cookie有效返回True，否则返回False
        """
        try:
            # 使用搜索接口来验证Cookie，搜索一个通用词，比如"音乐"
            url = "https://u.y.qq.com/cgi-bin/musicu.fcg"
            params = {
                "format": "json",
                "data": json.dumps({
                    "comm": {"ct": 24, "cv": 0},
                    "search": {
                        "method": "DoSearchForQQMusicDesktop",
                        "module": "music.search.SearchCgiService",
                        "param": {
                            "query": "音乐",
                            "num_per_page": 1,
                            "page_num": 1
                        }
                    }
                })
            }
            
            response = await self._make_request(url, params)
            
            # 检查响应中是否包含错误信息
            if response and "code" in response.get("search", {}).get("data", {}):
                return response["search"]["data"]["code"] == 0
                
            return False
            
        except Exception as e:
            logger.error(f"Cookie验证失败: {e}")
            return False
    async def search_song(self, keyword: str) -> List[Dict]:
        """搜索歌曲
        
        使用关键词搜索QQ音乐，返回歌曲列表。每首歌曲包含名称、歌手、专辑等信息。
        
        Args:
            keyword (str): 搜索关键词
            
        Returns:
            List[Dict]: 歌曲信息列表，每个字典包含歌曲详细信息
        """
        try:
            url = "https://u.y.qq.com/cgi-bin/musicu.fcg"
            params = {
                "format": "json",
                "data": json.dumps({
                    "comm": {"ct": 24, "cv": 0},
                    "search": {
                        "method": "DoSearchForQQMusicDesktop",
                        "module": "music.search.SearchCgiService",
                        "param": {
                            "query": keyword,
                            "num_per_page": 20,  # 每页返回20首歌曲
                            "page_num": 1
                        }
                    }
                })
            }
            
            response = await self._make_request(url, params)
            
            if not response or "search" not in response:
                logger.error("搜索响应格式错误")
                return []
                
            songs_data = response["search"]["data"]["body"]["song"]["list"]
            
            # 整理歌曲信息为标准格式
            songs = []
            for song in songs_data:
                # 组合所有歌手名称
                singer = " / ".join(singer["name"] for singer in song.get("singer", []))
                
                songs.append({
                    "name": song.get("title", "未知歌曲"),
                    "singer": singer or "未知歌手",
                    "album": song.get("album", {}).get("title", "未知专辑"),
                    "songmid": song.get("mid", ""),  # 歌曲的唯一标识符
                    "interval": song.get("interval", 0),  # 歌曲时长（秒）
                    "size": {  # 不同品质对应的文件大小
                        "128": song.get("file", {}).get("size_128mp3", 0),
                        "320": song.get("file", {}).get("size_320mp3", 0),
                        "flac": song.get("file", {}).get("size_flac", 0)
                    }
                })
            
            return songs
            
        except Exception as e:
            logger.error(f"搜索歌曲时出错: {e}")
            raise  # 向上层抛出异常，让调用者处理
    def _setup_session(self):
        """设置异步会话"""
        self.timeout = aiohttp.ClientTimeout(total=self.config.timeout)
        
    def _setup_directories(self):
        """设置下载目录结构"""
        self.base_dir = Path.home() / 'Desktop' / 'QQMusic'
        self.music_dir = self.base_dir / 'Music'
        self.lyrics_dir = self.base_dir / 'Lyrics'
        
        # 创建所需目录
        for directory in [self.music_dir, self.lyrics_dir]:
            directory.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"下载目录初始化完成: {self.base_dir}")
    def get_download_path(self) -> str:
        """返回下载目录路径"""
        return str(self.base_dir)  # 返回基础目录的字符串表示

    async def _make_request(self, url: str, params: Optional[Dict] = None,
                            retry: int = 0, headers: Optional[Dict] = None) -> Dict:
        """发送HTTP请求并处理响应"""
        try:
            request_headers = headers if headers is not None else self.headers
            async with aiohttp.ClientSession(headers=request_headers,
                                            timeout=self.timeout) as session:
                async with session.get(url, params=params) as response:
                    response.raise_for_status()
                    text = await response.text()
                    # 处理JSONP响应
                    if text.startswith(('callback(', 'MusicJsonCallback(',
                                        'jsonCallback(')):
                        text = text[text.find('(')+1:text.rfind(')')]
                    return json.loads(text)
        except Exception as e:
            if retry < self.config.retry_times:
                await asyncio.sleep(self.config.retry_delay)
                return await self._make_request(url, params, retry + 1, headers)
            raise


    async def download_with_lyrics(self, url: str, filename: str, quality: int,
                                 songmid: str, progress_bar=None,
                                 progress_label=None,
                                 pause_event=None) -> bool:
        """增强的下载实现"""
        try:
            ext = 'flac' if quality == 3 else 'm4a'
            filename = self._sanitize_filename(filename)
            file_path = self.music_dir / f"{filename}.{ext}"
            
            # 检查文件是否已存在
            if file_path.exists():
                logger.info(f"文件已存在: {filename}")
                return True

            start_time = datetime.now()
            total_size = 0
            downloaded = 0

            async with aiohttp.ClientSession(headers=self.headers) as session:
                async with session.get(url) as response:
                    response.raise_for_status()
                    total_size = int(response.headers.get('content-length', 0))

                    if progress_bar:
                        progress_bar.max = 100
                        progress_bar.value = 0

                    # 使用临时文件下载
                    temp_path = file_path.with_suffix('.tmp')
                    async with aiofiles.open(temp_path, mode='wb') as f:
                        async for chunk in response.content.iter_chunked(
                                self.config.chunk_size):
                            # 检查暂停状态
                            if pause_event:
                                await pause_event.wait()
                                
                            await f.write(chunk)
                            downloaded += len(chunk)
                            
                            # 更新进度信息
                            await self._update_progress(
                                downloaded, total_size,
                                start_time, progress_bar,
                                progress_label, filename
                            )

                    # 下载完成后重命名文件
                    temp_path.rename(file_path)

            # 下载歌词
            await self._download_lyrics(filename, songmid, progress_label)
            return True

        except Exception as e:
            logger.error(f"下载失败 {filename}: {e}")
            return False

    async def _download_lyrics(self, filename: str, songmid: str,
                             progress_label=None) -> bool:
        """下载歌词"""
        try:
            if progress_label:
                progress_label.text = '正在获取歌词...'
                
            lyrics = await self.get_lyrics(songmid)
            if lyrics:
                lyrics_path = self.lyrics_dir / f"{filename}.lrc"
                async with aiofiles.open(lyrics_path, 'w',
                                       encoding='utf-8') as f:
                    await f.write(lyrics)
                return True
            return False
            
        except Exception as e:
            logger.error(f"歌词下载失败: {e}")
            return False

    async def _update_progress(self, downloaded: int, total_size: int,
                             start_time: datetime, progress_bar,
                             progress_label, filename: str):
        """更新下载进度"""
        if total_size > 0:
            progress = (downloaded * 100) / total_size
            speed = downloaded / (datetime.now() -
                                start_time).total_seconds() / 1024  # KB/s
            
            if progress_bar:
                progress_bar.value = progress
                
            if progress_label:
                eta = (total_size - downloaded) / (speed * 1024)
                progress_label.text = (
                    f'下载中: {filename}\n'
                    f'进度: {progress:.1f}%\n'
                    f'速度: {speed:.1f} KB/s\n'
                    f'剩余时间: {eta:.1f}s'
                )
    async def get_song_url(self, songmid: str, quality: int) -> Optional[str]:
        """获取歌曲的下载链接

        Args:
            songmid (str): 歌曲的唯一标识符
            quality (int): 音质等级，1=128kbps，2=320kbps，3=无损

        Returns:
            Optional[str]: 歌曲的下载链接，如果获取失败则返回 None
        """
        try:
            guid = str(random.randint(1000000000, 9999999999))
            uin_match = re.search(r'uin=(\d+);', self.cookie)
            uin = uin_match.group(1) if uin_match else '0'

            # 根据质量选择对应的格式和编码
            if quality == 1:
                filename = f"C400{songmid}.m4a"
            elif quality == 2:
                filename = f"M500{songmid}.mp3"
            elif quality == 3:
                filename = f"F000{songmid}.flac"
            else:
                return None

            url = "https://u.y.qq.com/cgi-bin/musicu.fcg"
            data = {
                "req": {
                    "module": "CDN.SrfCdnDispatchServer",
                    "method": "GetCdnDispatch",
                    "param": {
                        "guid": guid,
                        "calltype": 0,
                        "userip": ""
                    }
                },
                "req_0": {
                    "module": "vkey.GetVkeyServer",
                    "method": "CgiGetVkey",
                    "param": {
                        "guid": guid,
                        "songmid": [songmid],
                        "songtype": [0],
                        "uin": uin,
                        "loginflag": 1,
                        "platform": "20"
                    }
                },
                "comm": {
                    "uin": uin,
                    "format": "json",
                    "ct": 24,
                    "cv": 0
                }
            }

            params = {
                "format": "json",
                "data": json.dumps(data)
            }

            response = await self._make_request(url, params=params)

            if response and 'req_0' in response:
                vkey = response['req_0']['data']['midurlinfo'][0]['vkey']
                if vkey:
                    purl = response['req_0']['data']['midurlinfo'][0]['purl']
                    song_url = f"https://isure.stream.qqmusic.qq.com/{purl}"
                    return song_url
            return None

        except Exception as e:
            logger.error(f"获取歌曲链接失败: {e}")
            return None

    async def get_lyrics(self, songmid: str) -> Optional[str]:
        """获取歌曲歌词

        Args:
            songmid (str): 歌曲的唯一标识符

        Returns:
            Optional[str]: 歌词文本，如果获取失败则返回 None
        """
        try:
            url = f"https://c.y.qq.com/lyric/fcgi-bin/fcg_query_lyric_new.fcg"
            params = {
                'songmid': songmid,
                'format': 'json',
                'nobase64': 0,
                'callback': ''
            }
            headers = self.headers.copy()
            headers.update({
                'Referer': 'https://y.qq.com/portal/player.html'
            })
            response = await self._make_request(url, params=params, headers=headers)
            if response and 'lyric' in response:
                # 歌词是 base64 编码的，需要解码
                lyric = base64.b64decode(response['lyric']).decode('utf-8')
                return lyric
            return None

        except Exception as e:
            logger.error(f"获取歌词失败: {e}")
            return None



    def _clean_cookie(self, cookie: str) -> str:
        """清理Cookie字符串"""
        cookie = cookie.replace('*', '%2A')
        cookie = re.sub(r'\s+', '', cookie)
        return cookie

    def _sanitize_filename(self, filename: str) -> str:
        """清理文件名"""
        illegal_chars = '<>:"/\\|?*'
        for char in illegal_chars:
            filename = filename.replace(char, '_')
        return filename
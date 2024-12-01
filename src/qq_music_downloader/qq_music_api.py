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
import zlib
import re

# 配置日志记录
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class QQMusicAPI:
    """QQ音乐API接口类，处理与QQ音乐服务器的所有交互"""

    def __init__(self, cookie: str):
        """初始化API客户端"""
        self.cookie = self._clean_cookie(cookie)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Cookie': self.cookie,
            'Referer': 'https://y.qq.com',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Connection': 'keep-alive',
            'Origin': 'https://y.qq.com'
        }
        self._setup_directories()

    def _clean_cookie(self, cookie: str) -> str:
        """清理Cookie中的特殊字符"""
        # 替换特殊字符
        cookie = cookie.replace('*', '%2A')
        # 移除可能的多余空格
        cookie = re.sub(r'\s+', '', cookie)
        return cookie

    def _setup_directories(self):
        """设置下载目录到系统下载文件夹"""
        desktop_path = Path.home() / 'Desktop'
        self.download_dir = desktop_path / 'QQMusic'
        self.download_dir.mkdir(parents=True, exist_ok=True)
        self.lyrics_dir = self.download_dir / 'lyrics'
        self.lyrics_dir.mkdir(exist_ok=True)
        logger.info(f"下载目录已设置为: {self.download_dir}")

    def get_download_path(self) -> str:
        """获取下载目录路径"""
        return str(self.download_dir)

    async def validate_cookie(self) -> bool:
        """验证Cookie是否有效"""
        try:
            # 使用搜索接口验证Cookie
            search_url = 'https://c.y.qq.com/soso/fcgi-bin/client_search_cp'
            params = {
                'w': '周杰伦',  # 测试搜索
                'p': 1,
                'n': 1,
                'format': 'json',
                'inCharset': 'utf8',
                'outCharset': 'utf-8'
            }

            response = await self._make_request(search_url, params)
            logger.info(f"Cookie验证响应: {str(response)[:200]}...")

            if isinstance(response, dict):
                if 'code' in response and response['code'] == 0:
                    return True
                if 'data' in response and 'song' in response['data']:
                    return True
            return False

        except Exception as e:
            logger.error(f"Cookie验证失败: {str(e)}")
            return False

    async def _make_request(self, url: str, params: Optional[Dict] = None) -> Dict:
        """发送HTTP请求并处理响应"""
        timeout = aiohttp.ClientTimeout(total=30)

        # 记录请求信息
        logger.info(f"发送请求到: {url}")
        logger.info(f"请求参数: {params}")
        logger.info(f"Cookie长度: {len(self.cookie)}")

        async with aiohttp.ClientSession(headers=self.headers, timeout=timeout) as session:
            try:
                async with session.get(url, params=params) as response:
                    response.raise_for_status()
                    logger.info(f"响应状态码: {response.status}")

                    text = await response.text()
                    logger.debug(f"原始响应: {text[:200]}...")  # 只记录前200个字符

                    # 处理JSONP响应
                    if text.startswith(('callback(', 'MusicJsonCallback(', 'jsonCallback(')):
                        text = text[text.find('(')+1:text.rfind(')')]

                    result = json.loads(text)
                    return result

            except Exception as e:
                logger.error(f"请求失败: {str(e)}")
                raise

    async def search_song(self, keyword: str, page: int = 1, num: int = 20) -> List[Dict]:
        """搜索歌曲"""
        search_url = 'https://c.y.qq.com/soso/fcgi-bin/client_search_cp'
        params = {
            'w': keyword,
            'p': page,
            'n': num,
            'format': 'json',
            'inCharset': 'utf8',
            'outCharset': 'utf-8',
            'platform': 'yqq.json'
        }

        try:
            response = await self._make_request(search_url, params)
            if 'data' in response and 'song' in response['data']:
                song_list = response['data']['song']['list']
                return [
                    {
                        'name': song['songname'],
                        'singer': ' & '.join(singer['name'] for singer in song['singer']),
                        'album': song['albumname'],
                        'duration': song['interval'],
                        'songmid': song['songmid'],
                        'albumid': song['albumid']
                    }
                    for song in song_list
                ]
            return []
        except Exception as e:
            logger.error(f"搜索失败: {e}")
            return []

    async def get_song_url(self, songmid: str, quality: int = 1) -> Optional[str]:
        """获取歌曲下载链接"""
        guid = str(random.randint(1000000000, 9999999999))
        vkey_url = 'https://u.y.qq.com/cgi-bin/musicu.fcg'

        params = {
            'format': 'json',
            'data': json.dumps({
                "req": {
                    "module": "CDN.SrfCdnDispatchServer",
                    "method": "GetCdnDispatch",
                    "param": {"guid": guid, "calltype": 0, "userip": ""}
                },
                "req_0": {
                    "module": "vkey.GetVkeyServer",
                    "method": "CgiGetVkey",
                    "param": {
                        "guid": guid,
                        "songmid": [songmid],
                        "songtype": [0],
                        "uin": "0",
                        "loginflag": 1,
                        "platform": "20"
                    }
                }
            })
        }

        try:
            response = await self._make_request(vkey_url, params)
            if response.get('req_0', {}).get('data', {}).get('midurlinfo'):
                purl = response['req_0']['data']['midurlinfo'][0].get('purl', '')
                if purl:
                    return f"https://dl.stream.qqmusic.qq.com/{purl}"
            logger.warning(f"无法获取下载链接: {songmid}")
            return None
        except Exception as e:
            logger.error(f"获取下载链接失败: {e}")
            return None

    async def get_lyrics(self, songmid: str) -> Optional[str]:
        """获取歌词"""
        lyrics_url = 'https://c.y.qq.com/lyric/fcgi-bin/fcg_query_lyric_new.fcg'
        params = {
            'songmid': songmid,
            'format': 'json',
            'nobase64': 1,
            'g_tk': '5381',
            'loginUin': '0',
            'hostUin': '0',
            'inCharset': 'utf8',
            'outCharset': 'utf-8',
            'platform': 'yqq.json'
        }

        try:
            response = await self._make_request(lyrics_url, params)
            if 'lyric' in response:
                lyrics = response['lyric']
                try:
                    # 尝试base64解码
                    lyrics = base64.b64decode(lyrics).decode('utf-8')
                except:
                    pass
                return lyrics
            return None
        except Exception as e:
            logger.error(f"获取歌词失败: {e}")
            return None

    def _sanitize_filename(self, filename: str) -> str:
        """清理文件名，移除非法字符"""
        illegal_chars = '<>:"/\\|?*'
        for char in illegal_chars:
            filename = filename.replace(char, '_')
        return filename

    async def download_with_lyrics(self, url: str, filename: str, quality: int,
                                 songmid: str, progress_bar=None,
                                 progress_label=None) -> bool:
        """下载歌曲和歌词"""
        try:
            ext = 'flac' if quality == 3 else 'm4a'
            filename = self._sanitize_filename(filename)
            file_path = self.download_dir / f"{filename}.{ext}"

            logger.info(f"开始下载: {filename}")
            if progress_label:
                progress_label.text = '准备下载...'

            async with aiohttp.ClientSession(headers=self.headers) as session:
                async with session.get(url) as response:
                    response.raise_for_status()
                    total_size = int(response.headers.get('content-length', 0))

                    if progress_bar:
                        progress_bar.max = 100  # 设置进度条最大值为100
                        progress_bar.value = 0

                    chunk_size = 8192
                    downloaded = 0

                    async with aiofiles.open(file_path, mode='wb') as f:
                        async for chunk in response.content.iter_chunked(chunk_size):
                            await f.write(chunk)
                            downloaded += len(chunk)
                            if progress_bar and total_size > 0:
                                # 计算百分比进度（0-100）
                                progress_percentage = int((downloaded * 100) / total_size)
                                progress_bar.value = progress_percentage
                            if progress_label:
                                progress_label.text = f'下载中... {downloaded * 100 / total_size:.1f}%'

            # 下载歌词
            if progress_label:
                progress_label.text = '正在获取歌词...'

            lyrics = await self.get_lyrics(songmid)
            if lyrics:
                lyrics_path = self.lyrics_dir / f"{filename}.lrc"
                async with aiofiles.open(lyrics_path, 'w', encoding='utf-8') as f:
                    await f.write(lyrics)
                logger.info(f"歌词下载成功: {filename}")

            if progress_label:
                progress_label.text = '下载完成！'
            return True

        except Exception as e:
            logger.error(f"下载失败 {filename}: {e}")
            if progress_label:
                progress_label.text = '下载失败！'
            return False

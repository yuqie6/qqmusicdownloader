# qq_music_api.py
import aiohttp
import json
import logging
import random
from pathlib import Path
import aiofiles
from typing import Any, Dict, List, Optional
import base64
import re
from dataclasses import dataclass
from datetime import datetime
import time

try:
    from .crypto_bridge import (
        NodeCryptoError,
        decrypt_response,
        encrypt_payload,
    )
except ImportError:  # pragma: no cover - 兼容独立脚本导入
    from crypto_bridge import NodeCryptoError, decrypt_response, encrypt_payload

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
        raw_uin = self._extract_cookie_value("uin") or "0"
        self._uin = self._normalize_uin(raw_uin)
        self._g_tk = self._calculate_g_tk()
        self._setup_headers()
        self._setup_directories()
        self._setup_session()

    def _setup_headers(self):
        """初始化请求头"""
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Cookie": self.cookie,
            "Referer": "https://y.qq.com",
            "Accept": "application/json",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Connection": "keep-alive",
            "Origin": "https://y.qq.com",
        }

    def _extract_cookie_value(self, key: str) -> str:
        """从 Cookie 中提取特定键值."""

        match = re.search(rf"{key}=([^;]+)", self.cookie)
        return match.group(1) if match else ""

    def _normalize_uin(self, raw_uin: str) -> str:
        """将 Cookie 中的 uin 转换为纯数字.

        Args:
            raw_uin (str): Cookie 中原始的 uin 值。

        Returns:
            str: 去除前缀后的纯数字 uin，若无法解析则返回 "0"。
        """

        if not raw_uin:
            return "0"
        cleaned = raw_uin.lstrip("oO")
        if cleaned.isdigit():
            return cleaned
        match = re.search(r"(\d+)", raw_uin)
        if match:
            return match.group(1)
        return "0"

    def _calculate_g_tk(self) -> int:
        """根据 skey/qqmusic_key 计算 g_tk."""

        for candidate in [
            "qqmusic_key",
            "p_skey",
            "skey",
            "p_lskey",
            "lskey",
        ]:
            token = self._extract_cookie_value(candidate)
            if token:
                break
        else:
            token = ""

        hash_val = 5381
        for ch in token:
            hash_val += (hash_val << 5) + ord(ch)
        return hash_val & 0x7FFFFFFF

    def _generate_guid(self) -> str:
        """生成 GUID."""

        return str(random.randint(1000000000, 9999999999))

    def _build_comm(self, *, guid: Optional[str] = None) -> Dict[str, Any]:
        """构造通用 comm 字段."""

        comm: Dict[str, Any] = {
            "ct": 24,
            "cv": 0,
            "format": "json",
            "uin": self._uin,
            "platform": "yqq.json",
            "g_tk_new_20200303": self._g_tk,
            "g_tk": self._g_tk,
            "needNewCode": 0,
        }
        if guid:
            comm["guid"] = guid
        return comm

    async def _call_musics(
        self,
        payload: Dict[str, Any],
        *,
        encoding: str = "ag-1",
    ) -> Optional[Dict[str, Any]]:
        """调用 musics.fcg 并解密响应."""

        plain = json.dumps(payload, ensure_ascii=False)
        try:
            body, sign_value = encrypt_payload(plain)
        except NodeCryptoError as exc:
            logger.error("musics.fcg 加密失败: %s", exc)
            return None

        params = {
            "_": str(int(time.time() * 1000)),
            "encoding": encoding,
            "sign": sign_value,
        }
        headers = self._build_musics_headers()
        url = "https://u6.y.qq.com/cgi-bin/musics.fcg"

        try:
            async with aiohttp.ClientSession(
                headers=headers,
                timeout=self.timeout,
                trust_env=True,
            ) as session:
                async with session.post(url, params=params, data=body) as resp:
                    resp.raise_for_status()
                    raw = await resp.read()
        except Exception as exc:  # pragma: no cover - 网络波动
            logger.error("musics.fcg 请求失败: %s", exc)
            return None

        try:
            text, parsed = decrypt_response(raw)
        except NodeCryptoError as exc:
            logger.error("musics.fcg 解密失败: %s", exc)
            return None

        if parsed is None:
            try:
                parsed = json.loads(text)
            except json.JSONDecodeError:
                logger.error("musics.fcg 响应无法解析为 JSON")
                return None

        return parsed

    async def validate_cookie(self) -> bool:
        """验证Cookie是否有效

        通过尝试访问QQ音乐API来验证Cookie的有效性

        Returns:
            bool: Cookie有效返回True，否则返回False
        """
        try:
            payload = {
                "comm": self._build_comm(guid=self._generate_guid()),
                "req_1": {
                    "module": "music.search.SearchCgiService",
                    "method": "DoSearchForQQMusicDesktop",
                    "param": {
                        "query": "音乐",
                        "num_per_page": 1,
                        "page_num": 1,
                        "search_type": 0,
                    },
                },
            }

            result = await self._call_musics(payload)
            if not result:
                return False

            req_data = result.get("req_1", {})
            return req_data.get("code") == 0

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
            payload = {
                "comm": self._build_comm(guid=self._generate_guid()),
                "req_1": {
                    "module": "music.search.SearchCgiService",
                    "method": "DoSearchForQQMusicDesktop",
                    "param": {
                        "query": keyword,
                        "num_per_page": 20,
                        "page_num": 1,
                        "search_type": 0,
                    },
                },
            }

            response = await self._call_musics(payload)
            if not response:
                logger.error("搜索请求失败: 未获取到响应")
                return []

            search_block = response.get("req_1", {})
            if search_block.get("code") != 0:
                logger.error("搜索接口返回错误码: %s", search_block.get("code"))
                return []

            songs_data = (
                search_block.get("data", {})
                .get("body", {})
                .get("song", {})
                .get("list", [])
            )

            # 整理歌曲信息为标准格式
            songs = []
            for song in songs_data:
                # 组合所有歌手名称
                singer = " / ".join(singer["name"] for singer in song.get("singer", []))

                songs.append(
                    {
                        "name": song.get("title", "未知歌曲"),
                        "singer": singer or "未知歌手",
                        "album": song.get("album", {}).get("title", "未知专辑"),
                        "songmid": song.get("mid", ""),  # 歌曲的唯一标识符
                        "media_mid": song.get("file", {}).get("media_mid", ""),
                        "interval": song.get("interval", 0),  # 歌曲时长（秒）
                        "size": {  # 不同品质对应的文件大小
                            "128": song.get("file", {}).get("size_128mp3", 0),
                            "320": song.get("file", {}).get("size_320mp3", 0),
                            "flac": song.get("file", {}).get("size_flac", 0),
                        },
                    }
                )

            return songs

        except Exception as e:
            logger.error(f"搜索歌曲时出错: {e}")
            raise  # 向上层抛出异常，让调用者处理

    def _setup_session(self):
        """设置异步会话"""
        self.timeout = aiohttp.ClientTimeout(total=self.config.timeout)

    def _setup_directories(self):
        """设置下载目录结构"""
        self.base_dir = Path.home() / "Desktop" / "QQMusic"
        self.music_dir = self.base_dir / "Music"
        self.lyrics_dir = self.base_dir / "Lyrics"

        # 创建所需目录
        for directory in [self.music_dir, self.lyrics_dir]:
            directory.mkdir(parents=True, exist_ok=True)

        logger.info(f"下载目录初始化完成: {self.base_dir}")

    def get_download_path(self) -> str:
        """返回下载目录路径"""
        return str(self.base_dir)  # 返回基础目录的字符串表示

    async def download_with_lyrics(
        self,
        url: str,
        filename: str,
        quality: int,
        songmid: str,
        progress_bar=None,
        progress_label=None,
        pause_events=None,
    ) -> bool:
        """支持多重暂停控制的下载实现"""
        try:
            ext_mapping = {
                1: "m4a",  # 128kbps - m4a格式
                2: "mp3",  # 320kbps - mp3格式
                3: "flac",  # 无损 - flac格式
            }
            ext = ext_mapping.get(quality, "m4a")
            filename = self._sanitize_filename(filename)
            file_path = self.music_dir / f"{filename}.{ext}"

            if file_path.exists():
                logger.info(f"文件已存在: {filename}.{ext}")
                if progress_label:
                    progress_label.text = f"文件已存在: {filename}.{ext}"
                return True

            logger.info(f"开始下载文件: {filename}.{ext}")

            logger.info(f"开始下载文件: {filename}.{ext}")

            async with aiohttp.ClientSession(
                headers=self.headers,
                timeout=self.timeout,
                trust_env=True,
            ) as session:
                async with session.get(url) as response:
                    if response.status != 200:
                        logger.error("下载请求失败: HTTP %s", response.status)
                        return False

                    total_size = int(response.headers.get("content-length", 0))
                    if total_size == 0:
                        logger.error("下载请求缺少 content-length，可能被权限限制")
                        return False

                    temp_path = file_path.with_suffix(".tmp")
                    downloaded = 0
                    if progress_bar:
                        progress_bar.value = 0
                    start_time = datetime.now()
                    last_progress_update = datetime.now()

                    try:
                        async with aiofiles.open(temp_path, mode="wb") as f:
                            async for chunk in response.content.iter_chunked(
                                self.config.chunk_size
                            ):
                                # 检查所有暂停事件
                                if pause_events:
                                    if not isinstance(pause_events, list):
                                        pause_events = [pause_events]

                                    for event in pause_events:
                                        await event.wait()

                                await f.write(chunk)
                                downloaded += len(chunk)

                                current_time = datetime.now()
                                if (
                                    current_time - last_progress_update
                                ).total_seconds() >= 0.1:
                                    # 计算单个文件的下载进度
                                    file_progress = (downloaded * 100) / total_size
                                    speed = (
                                        downloaded
                                        / max(
                                            1,
                                            (current_time - start_time).total_seconds(),
                                        )
                                        / 1024
                                    )

                                    if progress_bar and not isinstance(
                                        progress_bar.value, str
                                    ):
                                        # 这里只更新进度条，不设置为100%
                                        progress_bar.value = file_progress

                                    if progress_label:
                                        eta = (total_size - downloaded) / (
                                            max(1, speed) * 1024
                                        )
                                        progress_label.text = (
                                            f"下载中: {filename}\n"
                                            f"进度: {file_progress:.1f}%\n"
                                            f"速度: {speed:.1f} KB/s\n"
                                            f"剩余时间: {int(eta)}秒"
                                        )

                                    last_progress_update = current_time

                        # 下载完成后重命名文件
                        temp_path.rename(file_path)
                        logger.info(f"下载完成: {filename}")

                        # 下载歌词
                        try:
                            await self._download_lyrics(
                                filename, songmid, progress_label
                            )
                        except Exception as e:
                            logger.error(f"歌词下载失败: {e}")

                        return True

                    except Exception:
                        if temp_path.exists():
                            temp_path.unlink()
                        raise

        except Exception as e:
            logger.error(f"下载失败 {filename}: {str(e)}")
            return False

    async def _download_lyrics(
        self, filename: str, songmid: str, progress_label=None
    ) -> bool:
        """下载歌词"""
        try:
            if progress_label:
                progress_label.text = "正在获取歌词..."

            lyrics = await self.get_lyrics(songmid)
            if lyrics:
                lyrics_path = self.lyrics_dir / f"{filename}.lrc"
                async with aiofiles.open(lyrics_path, "w", encoding="utf-8") as f:
                    await f.write(lyrics)
                return True
            logger.info("未获取到可用歌词: %s", songmid)
            return False

        except Exception as e:
            logger.error(f"歌词下载失败: {e}")
            return False

    async def _update_progress(
        self,
        downloaded: int,
        total_size: int,
        start_time: datetime,
        progress_bar,
        progress_label,
        filename: str,
    ):
        """更新下载进度"""
        if total_size > 0:
            progress = (downloaded * 100) / total_size
            speed = (
                downloaded / (datetime.now() - start_time).total_seconds() / 1024
            )  # KB/s

            if progress_bar:
                progress_bar.value = progress

            if progress_label:
                eta = (total_size - downloaded) / (speed * 1024)
                progress_label.text = (
                    f"下载中: {filename}\n"
                    f"进度: {progress:.1f}%\n"
                    f"速度: {speed:.1f} KB/s\n"
                    f"剩余时间: {eta:.1f}s"
                )

    async def get_song_url(
        self,
        songmid: str,
        media_mid: Optional[str],
        quality: int,
    ) -> Optional[str]:
        """获取歌曲的下载链接

        Args:
            songmid (str): 歌曲的唯一标识符
            media_mid (Optional[str]): 文件存储用的 media_mid
            quality (int): 音质等级，1=128kbps，2=320kbps，3=无损

        Returns:
            Optional[str]: 歌曲的下载链接，如果获取失败则返回 None
        """
        try:
            logger.info(f"开始获取歌曲下载地址: songmid={songmid}, quality={quality}")
            guid = self._generate_guid()
            uin = self._uin

            file_mid = media_mid or songmid
            if not media_mid:
                logger.warning(
                    "未提供 media_mid，回退使用 songmid 构造文件名: %s", songmid
                )

            # 根据质量选择对应的格式和编码
            if quality == 1:
                filename = f"C400{file_mid}.m4a"
            elif quality == 2:
                filename = f"M500{file_mid}.mp3"
            elif quality == 3:
                filename = f"F000{file_mid}.flac"
            else:
                return None

            logger.info(f"请求参数: guid={guid}, uin={uin}, 目标文件名: {filename}")

            final_url = await self._request_song_purl(
                guid=guid,
                songmid=songmid,
                filename=filename,
            )

            if final_url:
                logger.info(f"成功构建最终URL: {final_url}")
                return final_url

            logger.error("未能获取到下载地址")
            return None

        except Exception as e:
            logger.error(f"获取歌曲下载地址时出错: {str(e)}")
            logger.exception(e)  # 这会打印完整的错误堆栈
            return None

    async def _request_song_purl(
        self,
        *,
        guid: str,
        songmid: str,
        filename: str,
    ) -> Optional[str]:
        """调用最新 musics.fcg 接口获取 purl.

        Args:
            guid (str): 随机 GUID
            songmid (str): 歌曲 mid
            filename (str): 服务器上的文件名

        Returns:
            Optional[str]: 拼接完成的下载 URL
        """

        payload = {
            "comm": self._build_comm(guid=guid),
            "req_0": {
                "module": "vkey.GetVkeyServer",
                "method": "CgiGetVkey",
                "param": {
                    "guid": guid,
                    "songmid": [songmid],
                    "songtype": [0],
                    "uin": self._uin,
                    "loginflag": 1,
                    "platform": "20",
                    "filename": [filename],
                },
            },
        }

        parsed = await self._call_musics(payload)
        if not parsed:
            return None

        req_data = parsed.get("req_0", {}).get("data", {})
        msg = req_data.get("msg", "")
        midurlinfo = req_data.get("midurlinfo") or []
        if not midurlinfo:
            logger.error("musics.fcg 返回缺少 midurlinfo: %s", json.dumps(parsed, ensure_ascii=False))
            return None

        purl = midurlinfo[0].get("purl")
        if not purl:
            if msg:
                logger.error(
                    "musics.fcg 返回空 purl，服务端消息: %s", msg
                )
            else:
                logger.error(
                    "musics.fcg 返回空 purl: %s",
                    json.dumps(midurlinfo[0], ensure_ascii=False),
                )
            return None

        if msg and ("404" in msg or "fnameHitCache_404" in msg):
            logger.warning("CDN 消息提示 404，但成功获取 purl: %s", msg)

        sip_list = req_data.get("sip") or []
        base_url = "https://isure.stream.qqmusic.qq.com/"
        if sip_list:
            base_url = sip_list[0]
        if not base_url.endswith('/'):
            base_url += '/'

        return f"{base_url}{purl}"

    def _build_musics_headers(self) -> Dict[str, str]:
        """构造 musics.fcg 请求头."""

        headers = {
            "authority": "u6.y.qq.com",
            "accept": "application/octet-stream",
            "accept-encoding": "gzip, deflate",
            "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
            "cache-control": "no-cache",
            "origin": "https://y.qq.com",
            "pragma": "no-cache",
            "priority": "u=1, i",
            "referer": "https://y.qq.com/",
            "sec-ch-ua": '"Not;A=Brand";v="99", "Google Chrome";v="139", "Chromium";v="139"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
            "user-agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/139.0.0.0 Safari/537.36"
            ),
            "cookie": self.cookie,
            "content-type": "text/plain",
        }
        return headers

    async def get_lyrics(self, songmid: str) -> Optional[str]:
        """获取歌曲歌词

        Args:
            songmid (str): 歌曲的唯一标识符

        Returns:
            Optional[str]: 歌词文本，如果获取失败则返回 None
        """

        payload = {
            "comm": self._build_comm(guid=self._generate_guid()),
            "req_1": {
                "module": "music.musichallSong.PlayLyricInfo",
                "method": "GetPlayLyricInfo",
                "param": {
                    "songMid": songmid,
                    "songId": 0,
                    "songType": 0,
                    "lyricsType": 0,
                    "roma": 0,
                    "trans": 1,
                },
            },
        }

        result = await self._call_musics(payload)
        if not result:
            return None

        lyric_block = result.get("req_1", {})
        code = lyric_block.get("code")
        if code == 24001:
            logger.warning("歌词接口无可用数据: %s", code)
            return None
        if code != 0:
            logger.error("歌词接口返回错误码: %s", code)
            return None

        data = lyric_block.get("data", {})
        lyric_base64 = data.get("lyric")
        if not lyric_base64:
            return None

        try:
            return base64.b64decode(lyric_base64).decode("utf-8")
        except Exception as exc:  # pragma: no cover - 容错
            logger.error("歌词解码失败: %s", exc)
            return None

    def _clean_cookie(self, cookie: str) -> str:
        """清理Cookie字符串"""
        cookie = cookie.replace("*", "%2A")
        cookie = re.sub(r"\s+", "", cookie)
        return cookie

    def _sanitize_filename(self, filename: str) -> str:
        """清理文件名"""
        illegal_chars = '<>:"/\\|?*'
        for char in illegal_chars:
            filename = filename.replace(char, "_")
        return filename


@dataclass
class DownloadMonitor:
    """下载状态监控器"""

    filename: str
    total_size: int = 0
    downloaded: int = 0
    start_time: datetime | None = None
    last_update: datetime | None = None
    status: str = "准备中"
    error_message: str = ""

    def start(self):
        """开始下载"""
        self.start_time = datetime.now()
        self.last_update = datetime.now()
        self.status = "下载中"
        logger.info(f"开始下载: {self.filename}")

    def update(self, chunk_size: int):
        """更新下载进度"""
        self.downloaded += chunk_size
        current_time = datetime.now()
        start_time = self.start_time or current_time
        last_update = self.last_update or start_time

        if (current_time - last_update).total_seconds() >= 0.1:
            progress = (
                (self.downloaded * 100) / self.total_size if self.total_size > 0 else 0
            )
            elapsed = max(1e-3, (current_time - start_time).total_seconds())
            speed = self.downloaded / elapsed / 1024

            logger.info(
                f"下载进度 - {self.filename}: {progress:.1f}% "
                f"({self.downloaded}/{self.total_size} bytes), "
                f"速度: {speed:.1f} KB/s"
            )

            self.last_update = current_time

    def complete(self):
        """完成下载"""
        self.status = "已完成"
        start_time = self.start_time or datetime.now()
        duration = (datetime.now() - start_time).total_seconds()
        logger.info(
            f"下载完成 - {self.filename}: 总大小 {self.total_size / 1024 / 1024:.2f}MB, "
            f"耗时 {duration:.1f}秒"
        )

    def error(self, message: str):
        """记录错误"""
        self.status = "错误"
        self.error_message = message
        logger.error(f"下载错误 - {self.filename}: {message}")

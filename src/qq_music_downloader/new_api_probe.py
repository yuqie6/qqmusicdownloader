"""musics.fcg 新接口探测脚本."""

from __future__ import annotations

import argparse
import asyncio
import gzip
import json
import logging
import sys
import time
import zlib
from pathlib import Path
from typing import Any, Dict, Iterable, Optional, Tuple

import aiohttp

try:  # pragma: no cover - 可选依赖
    import brotli  # type: ignore
except Exception:  # pragma: no cover - 未安装 brotli 时静默降级
    brotli = None


logger = logging.getLogger(__name__)


def _read_text(path: Path) -> str:
    """读取文本文件.

    Args:
        path (Path): 文本文件路径

    Returns:
        str: 去除首尾空白后的文本内容
    """

    return path.read_text(encoding="utf-8").strip()


def _build_headers(cookie_header: str) -> Dict[str, str]:
    """构造与网页端一致的请求头."""

    return {
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
        "cookie": cookie_header,
        "content-type": "text/plain",
    }


async def _request_musics(  # pragma: no cover - 主要执行 I/O
    *,
    cookie_header: str,
    body_text: str,
    sign: str,
    timestamp: str,
    encoding: str,
) -> Tuple[bytes, Dict[str, str]]:
    """向最新 musics.fcg 接口发起请求."""

    headers = _build_headers(cookie_header)
    params = {"_": timestamp, "encoding": encoding, "sign": sign}
    url = "https://u6.y.qq.com/cgi-bin/musics.fcg"

    timeout = aiohttp.ClientTimeout(total=60)
    async with aiohttp.ClientSession(
        headers=headers,
        timeout=timeout,
        trust_env=True,
    ) as session:
        async with session.post(url, params=params, data=body_text) as resp:
            resp.raise_for_status()
            raw = await resp.read()
            return raw, dict(resp.headers)


def _iter_decode_candidates(raw: bytes) -> Iterable[Tuple[str, bytes]]:
    """按照多种策略尝试解码响应.

    Args:
        raw (bytes): 原始响应数据

    Yields:
        Iterable[Tuple[str, bytes]]: (解码方式, 处理后的字节)
    """

    yield "identity", raw

    try:
        yield "gzip", gzip.decompress(raw)
    except Exception:
        logger.debug("gzip 解码失败", exc_info=True)

    try:
        yield "zlib", zlib.decompress(raw)
    except Exception:
        logger.debug("zlib 解码失败", exc_info=True)

    if brotli is not None:
        try:
            yield "brotli", brotli.decompress(raw)
        except Exception:
            logger.debug("brotli 解码失败", exc_info=True)


def _decode_to_json(
    raw: bytes,
) -> Tuple[Optional[str], Optional[Dict[str, Any]], Optional[str]]:
    """尝试将响应转为 JSON.

    Args:
        raw (bytes): 原始响应字节

    Returns:
        Tuple[Optional[str], Optional[Dict[str, Any]], Optional[str]]:
            解码算法名称、解析出的 JSON、原始文本
    """

    for codec, payload in _iter_decode_candidates(raw):
        try:
            text = payload.decode("utf-8")
        except UnicodeDecodeError:
            continue

        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            continue

        return codec, data, text

    return None, None, None


def _resolve_timestamp(timestamp_arg: Optional[str]) -> str:
    """处理 ``_`` 参数.

    Args:
        timestamp_arg (Optional[str]): 用户输入的时间戳

    Returns:
        str: 以字符串形式返回的毫秒时间戳
    """

    if timestamp_arg:
        return timestamp_arg

    return str(int(time.time() * 1000))


def _setup_logging(verbose: bool) -> None:
    """初始化日志配置."""

    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, format="[%(levelname)s] %(message)s")


def _prepare_parser() -> argparse.ArgumentParser:
    """构建命令行参数解析器."""

    parser = argparse.ArgumentParser(
        description="探测 QQ 音乐最新 musics.fcg 接口的辅助脚本",
    )
    parser.add_argument(
        "--cookie-file",
        type=Path,
        required=True,
        help="保存完整 Cookie 字符串的文件路径",
    )
    parser.add_argument(
        "--body-file",
        type=Path,
        required=True,
        help="保存 base64 请求体的文件路径",
    )
    parser.add_argument(
        "--sign",
        type=str,
        required=True,
        help="sign 参数，需与 body 对应",
    )
    parser.add_argument(
        "--encoding",
        type=str,
        default="ag-1",
        help="encoding 参数，默认 ag-1",
    )
    parser.add_argument(
        "--timestamp",
        type=str,
        help="查询参数 _ 的值，留空则使用当前毫秒时间戳",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("docs/research"),
        help="保存响应结果的输出目录",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="输出更详细的调试日志",
    )
    return parser


async def _async_main(args: argparse.Namespace) -> None:
    """异步主流程."""

    cookie_text = _read_text(args.cookie_file)
    body_text = _read_text(args.body_file)
    timestamp = _resolve_timestamp(args.timestamp)

    logger.info("开始请求 musics.fcg，新时间戳 %s", timestamp)
    raw, headers = await _request_musics(
        cookie_header=cookie_text,
        body_text=body_text,
        sign=args.sign,
        timestamp=timestamp,
        encoding=args.encoding,
    )

    output_dir: Path = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    response_path = output_dir / "musics_response.bin"
    response_path.write_bytes(raw)
    headers_path = output_dir / "musics_response_headers.json"
    headers_path.write_text(
        json.dumps(headers, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    logger.info("已保存原始响应: %s", response_path)
    logger.debug("响应头: %s", headers)

    codec, data, text = _decode_to_json(raw)
    if codec and data and text:
        json_path = output_dir / f"musics_response_{codec}.json"
        json_path.write_text(text, encoding="utf-8")
        logger.info("成功以 %s 解码响应并保存至 %s", codec, json_path)
    else:
        logger.warning(
            "未能自动解析响应，请手动分析 %s (大小 %d 字节)",
            response_path,
            len(raw),
        )


def main(argv: Optional[Iterable[str]] = None) -> None:
    """命令行入口."""

    parser = _prepare_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)
    _setup_logging(args.verbose)

    try:
        asyncio.run(_async_main(args))
    except KeyboardInterrupt:  # pragma: no cover - 终端中断
        logger.info("已取消请求")


if __name__ == "__main__":  # pragma: no cover - 脚本直接执行
    main(sys.argv[1:])

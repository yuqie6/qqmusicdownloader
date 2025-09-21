"""通过 Node 工具复用 QQ 音乐加解密逻辑."""

from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
from importlib import resources
from pathlib import Path
from typing import Any, Dict, Optional, Tuple


class NodeCryptoError(RuntimeError):
    """Node 工具执行失败时抛出的异常."""


_NODE_PACKAGE = "qq_music_downloader.node_tools"
_NODE_SCRIPT_NAME = "qq_api_crypto.js"
_NODE_WORKSPACE: Optional[Path] = None


def _ensure_node_workspace() -> Path:
    """将 Node 相关脚本与资源复制到临时目录."""

    global _NODE_WORKSPACE
    if _NODE_WORKSPACE is not None and _NODE_WORKSPACE.exists():
        return _NODE_WORKSPACE

    temp_dir = Path(tempfile.mkdtemp(prefix="qqmusic-node-"))
    resource_files = [
        "qq_api_crypto.js",
        "encrypt_runtime.js",
        "runtime.js",
        "vendor.js",
        "regenerator-runtime.js",
    ]

    try:
        package_root = resources.files(_NODE_PACKAGE)
        for name in resource_files:
            source = package_root / name
            with resources.as_file(source) as src_path:
                shutil.copy(src_path, temp_dir / name)
    except ModuleNotFoundError:
        # 兼容未安装为包的场景（例如直接源代码路径执行）
        fallback_root = Path(__file__).resolve().parent / "node_tools"
        if not fallback_root.exists():
            raise NodeCryptoError("缺少 Node 运行资源，请检查安装包内容")
        for name in resource_files:
            shutil.copy(fallback_root / name, temp_dir / name)

    _NODE_WORKSPACE = temp_dir
    return temp_dir


def _node_executable() -> str:
    """找到可用的 Node 可执行文件."""

    node_path = shutil.which("node")
    if not node_path:
        raise NodeCryptoError(
            "未检测到 Node.js，请安装 Node 18+ 后重试"
        )
    return node_path


def _run_node_json(args: list[str]) -> Dict[str, Any]:
    """运行 Node 脚本并解析 JSON 输出.

    Args:
        args (list[str]): 传递给 Node 工具的参数列表。

    Returns:
        Dict[str, Any]: 解析后的 JSON 数据。

    Raises:
        NodeCryptoError: 当 Node 进程返回非零状态或输出非法 JSON。
    """

    workspace = _ensure_node_workspace()
    node_path = _node_executable()
    script_path = workspace / _NODE_SCRIPT_NAME
    cmd = [node_path, str(script_path), *args, "--json"]
    try:
        completed = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True,
            cwd=workspace,
        )
    except subprocess.CalledProcessError as exc:  # pragma: no cover - 系统命令执行失败
        raise NodeCryptoError(exc.stderr or exc.stdout or str(exc)) from exc

    stdout = (completed.stdout or "").strip()
    if not stdout:
        raise NodeCryptoError("Node 工具未返回任何输出")

    try:
        return json.loads(stdout)
    except json.JSONDecodeError as exc:
        raise NodeCryptoError(f"无法解析 Node 输出: {stdout}") from exc


def encrypt_payload(payload: str) -> Tuple[str, str]:
    """生成 musics.fcg 所需的加密体与 sign.

    Args:
        payload (str): 原始 JSON 字符串。

    Returns:
        Tuple[str, str]: 依次返回 Base64 请求体与 sign。

    Raises:
        NodeCryptoError: 当 Node 工具执行失败。
    """

    tmp_path: Optional[Path] = None
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".json", delete=False) as tmp:
        tmp.write(payload)
        tmp_path = Path(tmp.name)

    try:
        if tmp_path is None:
            raise NodeCryptoError("临时文件创建失败")
        result = _run_node_json(["--encrypt", str(tmp_path)])
    finally:
        if tmp_path is not None:
            tmp_path.unlink(missing_ok=True)

    body = result.get("body")
    sign = result.get("sign")
    if not isinstance(body, str) or not isinstance(sign, str):
        raise NodeCryptoError("Node 返回结果缺少 body/sign")

    return body, sign


def decrypt_response(blob: bytes) -> Tuple[str, Dict[str, Any] | None]:
    """解密 musics.fcg 的响应二进制数据.

    Args:
        blob (bytes): 从接口获取的原始字节流。

    Returns:
        Tuple[str, Dict[str, Any] | None]: 解密后的文本与可选 JSON 对象。

    Raises:
        NodeCryptoError: 当 Node 工具执行失败。
    """

    tmp_path: Optional[Path] = None
    with tempfile.NamedTemporaryFile("wb", suffix=".bin", delete=False) as tmp:
        tmp.write(blob)
        tmp_path = Path(tmp.name)

    try:
        if tmp_path is None:
            raise NodeCryptoError("临时文件创建失败")
        result = _run_node_json(["--decrypt", str(tmp_path)])
    finally:
        if tmp_path is not None:
            tmp_path.unlink(missing_ok=True)

    text = result.get("text")
    parsed = result.get("json")

    if not isinstance(text, str):
        raise NodeCryptoError("Node 返回结果缺少 text 字段")

    if parsed is not None and not isinstance(parsed, dict):
        raise NodeCryptoError("Node 返回的 json 字段格式异常")

    return text, parsed

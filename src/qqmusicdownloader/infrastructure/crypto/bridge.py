"""通过 Node 工具复用 QQ 音乐加解密逻辑."""

from __future__ import annotations

import atexit
import base64
import json
import logging
import shutil
import subprocess
import tempfile
import threading
from importlib import resources
from pathlib import Path
from typing import IO, Any, Dict, Optional, Tuple


class NodeCryptoError(RuntimeError):
    """Node 工具执行失败时抛出的异常."""


_NODE_PACKAGE = "qqmusicdownloader.infrastructure.crypto.node_tools"
_NODE_SCRIPT_NAME = "qq_api_crypto.js"
_NODE_WORKSPACE: Optional[Path] = None
_LOGGER = logging.getLogger(__name__)


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
        raise NodeCryptoError("未检测到 Node.js，请安装 Node 18+ 后重试")
    return node_path


class _NodeCryptoClient:
    """管理长驻 Node 加解密进程的客户端."""

    def __init__(self) -> None:
        self._process: subprocess.Popen[str] | None = None
        self._stdin: IO[str] | None = None
        self._stdout: IO[str] | None = None
        self._stderr_thread: threading.Thread | None = None
        self._lock = threading.Lock()

    def _drain_stderr(self, stream: IO[str]) -> None:
        """持续读取 stderr 并记录异常输出."""

        for line in stream:
            text = line.rstrip()
            if text:
                _LOGGER.warning("Node stderr: %s", text)

    def _close_no_lock(self) -> None:
        if self._stdin is not None:
            try:
                self._stdin.close()
            except OSError:
                pass
        if self._stdout is not None:
            try:
                self._stdout.close()
            except OSError:
                pass
        if self._process is not None and self._process.poll() is None:
            try:
                self._process.terminate()
                self._process.wait(timeout=1)
            except (
                ProcessLookupError,
                subprocess.TimeoutExpired,
            ):  # pragma: no cover - 极端场景
                self._process.kill()
        self._process = None
        self._stdin = None
        self._stdout = None

    def _ensure_process(self) -> None:
        if self._process is not None and self._process.poll() is None:
            return

        self._close_no_lock()

        workspace = _ensure_node_workspace()
        node_path = _node_executable()
        script_path = workspace / _NODE_SCRIPT_NAME

        try:
            self._process = subprocess.Popen(
                [node_path, str(script_path), "--server"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=workspace,
                bufsize=1,
            )
        except OSError as exc:  # pragma: no cover - 子进程无法启动
            raise NodeCryptoError(str(exc)) from exc

        if self._process.stdin is None or self._process.stdout is None:
            raise NodeCryptoError("无法与 Node 进程建立通信管道")

        self._stdin = self._process.stdin
        self._stdout = self._process.stdout

        if self._process.stderr is not None:
            self._stderr_thread = threading.Thread(
                target=self._drain_stderr,
                args=(self._process.stderr,),
                daemon=True,
            )
            self._stderr_thread.start()

    def request(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """向 Node 进程发送请求并解析结果."""

        message = json.dumps(payload, ensure_ascii=False)
        with self._lock:
            self._ensure_process()
            assert self._stdin is not None
            assert self._stdout is not None

            _LOGGER.debug("发送 Node 请求: %s", payload.get("action"))
            self._stdin.write(message + "\n")
            self._stdin.flush()

            response = self._stdout.readline()
            if response == "":
                returncode = self._process.poll() if self._process else None
                self._close_no_lock()
                raise NodeCryptoError(f"Node 进程意外退出, returncode={returncode}")

        response = response.strip()
        if not response:
            raise NodeCryptoError("Node 返回空响应")

        try:
            parsed = json.loads(response)
        except json.JSONDecodeError as exc:
            _LOGGER.error("无法解析 Node 响应: %s", response)
            raise NodeCryptoError(f"无法解析 Node 响应: {response}") from exc

        if not isinstance(parsed, dict):
            raise NodeCryptoError("Node 响应格式异常")

        if not parsed.get("ok"):
            error_msg = parsed.get("error", "未知错误")
            _LOGGER.error("Node 返回错误: %s", error_msg)
            raise NodeCryptoError(f"Node 返回错误: {error_msg}")

        data = parsed.get("data")
        if not isinstance(data, dict):
            raise NodeCryptoError("Node 响应缺少 data 字段")

        return data

    def close(self) -> None:
        """终止 Node 进程."""

        with self._lock:
            self._close_no_lock()


_NODE_CLIENT = _NodeCryptoClient()
atexit.register(_NODE_CLIENT.close)


def _node_request(action: str, **payload: Any) -> Dict[str, Any]:
    """封装 Node 请求, 自动附加 action 字段."""

    request_body = {"action": action, **payload}
    return _NODE_CLIENT.request(request_body)


def encrypt_payload(payload: str) -> Tuple[str, str]:
    """生成 musics.fcg 所需的加密体与 sign.

    Args:
        payload (str): 原始 JSON 字符串。

    Returns:
        Tuple[str, str]: 依次返回 Base64 请求体与 sign。

    Raises:
        NodeCryptoError: 当 Node 工具执行失败。
    """

    result = _node_request("encrypt", plain=payload)

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

    base64_blob = base64.b64encode(blob).decode("ascii")
    result = _node_request("decrypt", base64=base64_blob)

    text = result.get("text")
    parsed = result.get("json")

    if not isinstance(text, str):
        raise NodeCryptoError("Node 返回结果缺少 text 字段")

    if parsed is not None and not isinstance(parsed, dict):
        raise NodeCryptoError("Node 返回的 json 字段格式异常")

    return text, parsed

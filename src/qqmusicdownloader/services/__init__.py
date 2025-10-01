"""应用服务层：编排跨模块的业务用例。"""

from __future__ import annotations

from .download_service import DownloadService

__all__ = [
    "DownloadService",
]

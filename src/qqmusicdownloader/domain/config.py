"""领域配置对象"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class DownloadConfig:
    """下载配置，供服务层共享"""

    max_concurrent: int = 3
    default_quality: int = 1

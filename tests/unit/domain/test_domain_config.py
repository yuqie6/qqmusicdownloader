from qqmusicdownloader.domain import DownloadConfig


def test_download_config_defaults() -> None:
    config = DownloadConfig()
    assert config.max_concurrent == 3
    assert config.default_quality == 1


def test_download_config_custom_values() -> None:
    config = DownloadConfig(max_concurrent=5, default_quality=3)
    assert config.max_concurrent == 5
    assert config.default_quality == 3

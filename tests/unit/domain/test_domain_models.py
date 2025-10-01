from typing import cast

import pytest

from qqmusicdownloader.domain import FileSizeMap, SongRecord


def test_song_record_minimal_fields() -> None:
    record = SongRecord(name="测试歌曲", singer="测试歌手", songmid="abc")
    assert record["name"] == "测试歌曲"
    assert record.get("album") is None


def test_song_record_with_sizes() -> None:
    sizes: FileSizeMap = {"128": 123, "320": 456, "flac": 789}
    record = SongRecord(
        name="歌曲",
        singer="歌手",
        album="专辑",
        songmid="mid",
        media_mid="media",
        interval=100,
        size=sizes,
    )

    assert record["size"]["128"] == 123
    assert set(record["size"].keys()) == {"128", "320", "flac"}


@pytest.mark.parametrize("quality", ["128", "320", "flac"])
def test_file_size_map_accepts_partial_keys(quality: str) -> None:
    sizes = FileSizeMap({quality: 1024})
    assert sizes[quality] == 1024


def test_song_record_rejects_missing_songmid() -> None:
    with pytest.raises(KeyError):
        cast(SongRecord, {"name": "无 id"})["songmid"]

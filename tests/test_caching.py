from pathlib import Path

import pytest

from delphyne.stdlib.embeddings import load_embeddings_cache
from delphyne.utils.caching import Cache, load_cache


def test_read_only_cache_does_not_store_misses():
    entries = {1: 10}
    cache = Cache(entries, "read_only")
    calls: list[int] = []

    def compute(value: int) -> int:
        calls.append(value)
        return value * 10

    cached = cache(compute)
    assert cached(1) == 10
    assert cached(2) == 20
    assert cached(2) == 20
    assert calls == [2, 2]
    assert entries == {1: 10}


def test_read_only_batched_cache_does_not_store_misses():
    entries = {1: 10}
    cache = Cache(entries, "read_only")

    cached = cache.batched(lambda values: [value * 10 for value in values])
    assert cached([1, 2, 2]) == [10, 20, 20]
    assert entries == {1: 10}


@pytest.mark.parametrize("mode", ["read_only", "replay"])
def test_non_writing_modes_do_not_write_cache_file(
    tmp_path: Path, mode: str
):
    cache_file = tmp_path / "cache.yaml"
    original = "- input: 1\n  output: 10\n"
    cache_file.write_text(original)

    with load_cache(
        cache_file, input_type=int, output_type=int, mode=mode  # type: ignore[arg-type]
    ) as cache:
        assert cache.dict == {1: 10}

    assert cache_file.read_text() == original


@pytest.mark.parametrize("mode", ["read_only", "replay"])
def test_non_writing_modes_do_not_create_cache_files(
    tmp_path: Path, mode: str
):
    cache_file = tmp_path / "cache.yaml"
    embeddings_file = tmp_path / "embeddings.h5"

    with load_cache(
        cache_file, input_type=int, output_type=int, mode=mode  # type: ignore[arg-type]
    ):
        pass
    with load_embeddings_cache(
        embeddings_file, mode=mode  # type: ignore[arg-type]
    ):
        pass

    assert not cache_file.exists()
    assert not embeddings_file.exists()


def test_replay_cache_does_not_store_misses():
    entries = {1: 10}
    cached = Cache(entries, "replay")(lambda value: value * 10)

    with pytest.raises(AssertionError, match="Cache entry not found"):
        cached(2)
    assert entries == {1: 10}

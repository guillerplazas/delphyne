"""Lazy ACE data access, shared by both harnesses.

Importing adaptation contracts must not read evaluation partitions. Each
pool is loaded only when requested; a development-only process can use
trainX and validationX without opening the closed testX partition.
"""

from collections.abc import Iterator, Mapping
from functools import cache

import experiments.common.miniF2F_bench as mf

X_DOLLAR_CAP = 0.10
POOL_NAMES = (
    "train",
    "validation",
    "test",
    "adapt_pool",
    "trainX",
    "validationX",
    "testX",
)


@cache
def load_pool(name: str) -> Mapping[str, tuple[str, str]]:
    if name not in POOL_NAMES:
        raise KeyError(name)
    return mf.load_partition(f"benchmarks/{name}.txt")


class Pools(Mapping[str, Mapping[str, tuple[str, str]]]):
    def __contains__(self, name: object) -> bool:
        return name in POOL_NAMES

    def __getitem__(self, name: str) -> Mapping[str, tuple[str, str]]:
        return load_pool(name)

    def __iter__(self) -> Iterator[str]:
        return iter(POOL_NAMES)

    def __len__(self) -> int:
        return len(POOL_NAMES)


class Problems(Mapping[str, tuple[str, str]]):
    def __getitem__(self, name: str) -> tuple[str, str]:
        for pool in POOL_NAMES:
            if name in (problems := load_pool(pool)):
                return problems[name]
        raise KeyError(name)

    def __iter__(self) -> Iterator[str]:
        for pool in POOL_NAMES:
            yield from load_pool(pool)

    def __len__(self) -> int:
        return sum(len(load_pool(pool)) for pool in POOL_NAMES)


POOLS = Pools()
ALL_PROBLEMS = Problems()

from __future__ import annotations
import random
import math
from itertools import tee, count, islice
from dataclasses import dataclass
from typing import Callable, Iterator, Iterable, TypeVar, Tuple


T = TypeVar('T')


@dataclass
class Vec2:
    angle: float
    mag: float

    @classmethod
    def random(cls, mag: float = 1.0) -> Vec2:
        angle = random.random() * 2 * math.pi
        return cls(angle, mag)


def rolling_avg(old: float, new: float, alpha: float, n: int) -> float:
    adj_alpha = alpha**n
    return adj_alpha * old + (1 - adj_alpha) * new


def sliding_window(it: Iterator[T], n: int = 2) -> Iterator[Tuple[T, ...]]:
    return zip(*(islice(it, offset, None)
                 for offset, it in enumerate(tee(it, n))))


def isum(acc: T, *its: Iterable[T]) -> Iterator[T]:
    for values in zip(*its):
        yield sum(values, acc)


def resample(xs: Iterator[T], original_len: int, target_len: int
             ) -> Iterator[T]:
    assert original_len >= target_len, str((original_len, target_len))
    assert original_len > 0
    assert target_len > 0
    j = 0
    it = iter(xs)
    x = next(it)
    for i in range(target_len):
        index = int(original_len * i / target_len)
        while j < index:
            j += 1
            x = next(it)
        yield x


def autocorr(period: int, jitter: float = 0.5,
             dist: Callable[[float], float] = lambda _: random.random()
             ) -> Iterator[float]:
    """Returns an iterator with values drawn from `dist` that autocorrelate.
    The parameter `jitter` describes how closely the individual values follow
    the given distribution, regardless of previous values. I.e. for `jitter=1`,
    there is no autocorrelation, for `jitter=0`, each epoch is a linear
    interpolation between two samples from the distribution."""

    def add_level(xs: Iterator[float], level: int, epoch: float
                  ) -> Iterator[float]:
        strength = jitter**level
        length = 2**(level - 1)
        for i, (a, b) in enumerate(sliding_window(xs, n=2)):
            yield a
            # linearly interpolate between adjacent points
            midway_point = (a + b) * 0.5
            # Take a sample from the distribution
            x = (i + 0.5) / length + epoch
            sample = dist(x)
            # Weight the sample according to `strength`
            sample = sample * strength + midway_point * (1 - strength)
            yield sample
        yield b

    n_levels = math.ceil(math.log2(period))
    pivot = dist(0.)
    for epoch in count():
        next_pivot = dist(epoch + 1.)
        # The initial iterator with only the first and last sample (level 0)
        xs = iter((pivot, next_pivot))
        for level in range(1, n_levels + 1):
            # Add a level to the iterator, roughly doubling its resolution
            xs = add_level(xs, level=level, epoch=epoch)
        pivot = next_pivot
        yield from resample(xs, 2**n_levels + 1, period)


_NEXT_IDS = dict()


def id_factory(namespace: str) -> Callable[[], int]:
    if namespace in _NEXT_IDS:
        raise ValueError(f'Duplicate id namespace: {namespace}')
    _NEXT_IDS[namespace] = 0

    def factory() -> int:
        id = _NEXT_IDS[namespace]
        _NEXT_IDS[namespace] += 1
        return id

    return factory

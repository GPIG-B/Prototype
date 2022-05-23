from __future__ import annotations
import random
import math
from itertools import tee, islice
from dataclasses import dataclass
from typing import Callable, Iterator, Iterable, TypeVar, Tuple, Optional
from sqlitedict import SqliteDict # type: ignore


T = TypeVar('T')


with SqliteDict("idle_devices.sqlite", outer_stack=False):
    pass


def is_idle_device(device: str) -> bool:
    with SqliteDict("idle_devices.sqlite", outer_stack=False) as db:
        return db.get(device, False)


def set_idle_device(device: str, value = True):
    with SqliteDict("idle_devices.sqlite", outer_stack=False) as db:
        db[device] = value
        db.commit()


def list_idle_devices():
    devices = []
    with SqliteDict("idle_devices.sqlite", outer_stack=False) as db:
        for device, val in db.items():
            if val == True: devices.append(device)
    return devices


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


_NEXT_IDS = dict()


def id_factory(namespace: str) -> Callable[[], str]:
    if namespace in _NEXT_IDS:
        raise ValueError(f'Duplicate id namespace: {namespace}')
    _NEXT_IDS[namespace] = 0

    def factory() -> str:
        id = _NEXT_IDS[namespace]
        _NEXT_IDS[namespace] += 1
        return f'{namespace}-{str(id).zfill(6)}'

    return factory


class Autocorr:

    def __init__(self, dist: Callable[[float], float], alpha: float = 2.,
                 beta: float = 20., offset: float = 0, increment: float = 1.,
                 init: Optional[float] = None) -> None:
        self.dist = dist
        self.alpha = alpha
        self.beta = beta
        self.offset = offset
        self.increment = increment
        if init is None:
            self.residual = dist(self.offset)
            self.offset += self.increment
        else:
            self.residual = init

    def __next__(self) -> float:
        a = random.betavariate(self.alpha, self.beta)
        x = self.dist(self.offset) * a + (1 - a) * self.residual
        self.residual = x
        self.offset += self.increment
        return x

    def __iter__(self) -> Iterator[float]:
        return self


def smooth_step(x: float, offset: float = 0., width: float = 1.) -> float:
    """https://en.wikipedia.org/wiki/Smoothstep"""
    if x < offset:
        return 0.
    if x > offset + width:
        return 1.
    x = (x - offset) / width
    return 3 * x**2 - 2 * x**3

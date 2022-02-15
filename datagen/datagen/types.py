from __future__ import annotations
from dataclasses import dataclass, field
from typing import Protocol, List, Dict, Union, Iterator, Any
import random

from .config import Config
from .utils import rolling_avg, Vec2, id_factory
from .distributions import make_temp_iter, make_wind_iter


# The `Any` below should really be `ReadingsT`, but mypy does not support
# cyclic type definitions yet.
ReadingT = Union[float, int, str, Dict[str, Any], List[Any]]
ReadingsT = Dict[str, Union[ReadingT]]


@dataclass
class Simulation:
    cfg: Config = field(repr=False)
    wts: List[WindTurbine]
    env: Environment
    time: int = 0

    def get_readings(self) -> ReadingsT:
        wt_readings = [wt.get_readings(self.env) for wt in self.wts]
        readings: ReadingsT = dict(time=self.time,
                                   **self.env.get_readings(),
                                   wts=wt_readings)
        return readings

    def tick(self, n: int = 1) -> Simulation:
        for _ in range(n):
            self.env.tick()
            for wt in self.wts:
                wt.tick(self.env)
            self.time += 1
        return self


@dataclass
class Environment:
    cfg: Config = field(repr=False)
    wind: Vec2
    temp: float
    _temp_iter: Iterator[float] = field(repr=False)
    _wind_iter: Iterator[Vec2] = field(repr=False)

    @classmethod
    def from_config(cls, cfg: Config) -> Environment:
        wind_iter = make_wind_iter(cfg)
        wind = next(wind_iter)
        temp_iter = make_temp_iter(cfg)
        temp = next(temp_iter)
        return cls(cfg=cfg, wind=wind, _wind_iter=wind_iter, temp=temp,
                   _temp_iter=temp_iter)

    def tick(self) -> None:
        # Update wind
        self.wind = next(self._wind_iter)
        # Update temp
        self.temp = next(self._temp_iter)

    def get_readings(self) -> Dict[str, ReadingT]:
        return dict(env_wind_angle=self.wind.angle,
                    env_wind_mag=self.wind.mag,
                    env_temp=self.temp)


class Component(Protocol):
    def get_readings(self, env: Environment) -> Dict[str, ReadingT]: ...
    def tick(self, env: Environment) -> None: ...


@dataclass
class WindTurbine:
    components: List[Component]
    id: int = field(default_factory=id_factory('wt'))

    def get_readings(self, env: Environment) -> Dict[str, ReadingT]:
        readings: ReadingsT = dict(wt_id=self.id)
        for comp in self.components:
            readings.update(comp.get_readings(env))
        return readings

    def tick(self, env: Environment) -> None:
        for comp in self.components:
            comp.tick(env)


@dataclass
class Tower:

    def get_readings(self, env: Environment) -> Dict[str, ReadingT]:
        vib_freq = random.normalvariate(env.cfg.tower_vib_freq_mean,
                                        env.cfg.tower_vib_freq_var)
        vib_freq = max(0, vib_freq)
        return dict(tower_vib_freq=vib_freq)

    def tick(self, env: Environment) -> None: ...


@dataclass
class Rotor:
    rps: float

    def __init__(self, env: Environment) -> None:
        self.rps = env.wind.mag * env.cfg.rotor_rps_wind_fact

    def get_readings(self, env: Environment) -> Dict[str, ReadingT]:
        return dict(rotor_rps=self.rps)

    def tick(self, env: Environment) -> None:
        rps = env.wind.mag * env.cfg.rotor_rps_wind_fact
        rps = rps * random.gauss(1., env.cfg.rotor_rps_relative_var)
        rps = rolling_avg(self.rps, rps, env.cfg.rotor_rps_alpha,
                          env.cfg.tick_freq)
        self.rps = max(0, rps)


@dataclass
class Generator:
    temp: float

    def __init__(self, env: Environment) -> None:
        self.temp = env.temp

    def get_readings(self, env: Environment) -> Dict[str, ReadingT]:
        return dict(generator_temp=self.temp)

    def tick(self, env: Environment) -> None:
        temp_d = random.normalvariate(env.cfg.gen_temp_diff_mean,
                                      env.cfg.gen_temp_diff_var)
        temp = env.temp + temp_d
        self.temp = rolling_avg(self.temp, temp, env.cfg.gen_temp_alpha,
                                env.cfg.tick_freq)

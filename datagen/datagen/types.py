from __future__ import annotations
from dataclasses import dataclass, field
from typing import Protocol, List, Dict, Union, Iterator, Any, Callable, Type
import random
import time
import logging
from abc import ABC
from datetime import timedelta

from .config import Config
from .utils import rolling_avg, Vec2, id_factory
from .distributions import make_temp_iter, make_wind_iter


logger = logging.getLogger('datagen')


# The `Any`s below should really be `ReadingsT`, but mypy does not support
# cyclic type definitions yet.
ReadingT = Union[float, int, str, Dict[str, Any], List[Any]]
ReadingsT = Dict[str, ReadingT]


@dataclass
class Simulation:
    cfg: Config = field(repr=False)
    wts: List[WindTurbine]
    env: Environment
    ticks: int = 0
    uptime: timedelta = field(default_factory=timedelta)
    running: bool = True

    def get_readings(self) -> ReadingsT:
        wt_readings = [wt.get_readings(self.env) for wt in self.wts]
        readings: ReadingsT = dict(ticks=self.ticks,
                                   uptime=str(self.uptime),
                                   **self.env.get_readings(),
                                   wts=wt_readings)
        return readings

    def tick(self, n: int = 1) -> Simulation:
        for _ in range(n):
            logger.debug(f'Tick {self.ticks}')
            self.env.tick()
            for wt in self.wts:
                wt.tick(self.env)
            self.ticks += 1
            self.uptime += timedelta(seconds=self.cfg.tick_freq)
        return self

    def loop(self, callback: Callable[[ReadingsT], None]) -> None:
        logger.info('Simulation loop started')
        while self.running:
            readings = self.get_readings()
            callback(readings)
            self.tick()
            time.sleep(1 / self.cfg._ticks_per_second)
        logger.info('Simulation loop terminated')


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
class Fault(ABC):
    wt: WindTurbine

    def bofore_tick(self) -> None:
        pass

    def after_tick(self) -> None:
        pass

    def __str__(self) -> str:
        return self.__class__.__name__


# Contains the fault types and their associated probabilities
_wt_fault_types: Dict[Type[Fault], float] = dict()


@dataclass
class WindTurbine:
    tower: Tower
    rotor: Rotor
    generator: Generator
    faults: List[Fault] = field(default_factory=list)
    id: int = field(default_factory=id_factory('wt'))

    def get_readings(self, env: Environment) -> Dict[str, ReadingT]:
        readings: ReadingsT = dict(
            wt_id=self.id,
            _faults=[str(fault) for fault in self.faults],
        )
        for comp in self.components:
            readings.update(comp.get_readings(env))
        return readings

    def tick(self, env: Environment) -> None:
        # Call `before_tick` hooks on faults
        for fault in self.faults:
            fault.bofore_tick()
        # Advance each component
        for comp in self.components:
            comp.tick(env)
        # Potentially add new faults to the wind turbine
        for fault_cls, prob in _wt_fault_types.items():
            if random.random() < prob * env.cfg.tick_freq:
                new_fault = fault_cls(self)
                logger.info(f'WT[{self.id}]: New fault {new_fault}')
                self.faults.append(new_fault)
        # Call `after_tick` hooks on faults
        for fault in self.faults:
            fault.after_tick()

    @classmethod
    def from_env(cls, env: Environment) -> WindTurbine:
        return cls(Tower(env), Rotor(env), Generator(env))

    @property
    def components(self) -> List[Component]:
        return [self.tower, self.rotor, self.generator]

    @classmethod
    def wt_fault(cls, prob: float) -> Callable[[Type[Fault]], Type[Fault]]:
        def wrapper(fault_cls: Type[Fault]) -> Type[Fault]:
            _wt_fault_types[fault_cls] = prob
            return fault_cls
        return wrapper


@dataclass
class Tower(Component):
    vib_freq: float

    def __init__(self, env: Environment) -> None:
        vib_freq = random.gauss(env.cfg.tower_vib_freq_mean,
                                env.cfg.tower_vib_freq_var)
        self.vib_freq = max(0, vib_freq)

    def get_readings(self, _: Environment) -> Dict[str, ReadingT]:
        return dict(tower_vib_freq=self.vib_freq)

    def tick(self, env: Environment) -> None:
        vib_freq = random.gauss(env.cfg.tower_vib_freq_mean,
                                env.cfg.tower_vib_freq_var)
        self.vib_freq = max(0, vib_freq)


@dataclass
class Rotor(Component):
    rps: float

    def __init__(self, env: Environment) -> None:
        self.rps = env.wind.mag * env.cfg.rotor_rps_wind_fact

    def get_readings(self, _: Environment) -> Dict[str, ReadingT]:
        return dict(rotor_rps=self.rps)

    def tick(self, env: Environment) -> None:
        rps = env.wind.mag * env.cfg.rotor_rps_wind_fact
        rps = rps * random.gauss(1., env.cfg.rotor_rps_relative_var)
        rps = rolling_avg(self.rps, rps, env.cfg.rotor_rps_alpha,
                          env.cfg.tick_freq)
        self.rps = max(0, rps)


@WindTurbine.wt_fault(1e-5)
@dataclass
class RotorBladeSurfaceCrack(Fault):
    rps_factor: float = 0.9

    def after_tick(self) -> None:
        self.wt.rotor.rps *= self.rps_factor

    def __str__(self) -> str:
        return f'{self.__class__.__name__}[rps_factor={self.rps_factor:0.5}]'


@dataclass
class Generator(Component):
    temp: float

    def __init__(self, env: Environment) -> None:
        self.temp = env.temp

    def get_readings(self, _: Environment) -> Dict[str, ReadingT]:
        return dict(generator_temp=self.temp)

    def tick(self, env: Environment) -> None:
        temp_d = random.normalvariate(env.cfg.gen_temp_diff_mean,
                                      env.cfg.gen_temp_diff_var)
        temp = env.temp + temp_d
        self.temp = rolling_avg(self.temp, temp, env.cfg.gen_temp_alpha,
                                env.cfg.tick_freq)

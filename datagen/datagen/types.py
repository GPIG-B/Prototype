from __future__ import annotations
from dataclasses import dataclass, field
import random
import time
import logging
from abc import ABC
from datetime import timedelta
from itertools import tee
from pathlib import Path
import yaml
from functools import partial
from typing import (Protocol, List, Dict, Union, Iterator, Any, Callable, Type,
                    TypeVar)

from .config import Config
from .utils import Vec2, id_factory, smooth_step
from .distributions import (make_temp_iter, make_wind_iter, make_wave_iter,
                            make_vis_iter)


logger = logging.getLogger('datagen')


T = TypeVar('T')

P = 1e-8


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
        # This is what will be written to the central Namespace
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

    def loop(self, callback: Callable[[ReadingsT], None], max_ticks: int = -1,
             no_wait: bool = False) -> None:
        logger.info('Simulation loop started')
        while self.running and max_ticks != 0:
            readings = self.get_readings()
            callback(readings)
            self.tick()
            if not no_wait:
                time.sleep(1 / self.cfg._ticks_per_second)
            max_ticks -= 1
        logger.info('Simulation loop terminated')


@dataclass
class Environment:
    cfg: Config = field(repr=False)
    wind: Vec2
    temp: float
    wave_mag: float
    visibility: float
    _temp_iter: Iterator[float] = field(repr=False)
    _wind_iter: Iterator[Vec2] = field(repr=False)
    _wave_iter: Iterator[float] = field(repr=False)
    _vis_iter: Iterator[float] = field(repr=False)

    @classmethod
    def from_config(cls, cfg: Config) -> Environment:
        wind_iter, wi = tee(make_wind_iter(cfg))
        wind = next(wind_iter)
        temp_iter = make_temp_iter(cfg)
        temp = next(temp_iter)
        wave_iter = make_wave_iter(cfg, wi)
        vis_iter = make_vis_iter(cfg)
        return cls(cfg=cfg, wind=wind, _wind_iter=wind_iter,
                   _wave_iter=wave_iter, temp=temp, _temp_iter=temp_iter,
                   wave_mag=next(wave_iter), visibility=next(vis_iter),
                   _vis_iter=vis_iter)

    def tick(self) -> None:
        # Update wind
        self.wind = next(self._wind_iter)
        # Update temp
        self.temp = next(self._temp_iter)

    def get_readings(self) -> Dict[str, ReadingT]:
        return dict(env_wind_angle=self.wind.angle,
                    env_wind_mag=self.wind.mag,
                    env_temp=self.temp, wave_mag=self.wave_mag,
                    visibility=self.visibility)


class Component(Protocol):
    @classmethod
    def factory(cls: Type[T], env: Environment) -> T: ...
    def get_readings(self, env: Environment) -> Dict[str, ReadingT]: ...
    def tick(self, wt: WindTurbine,  env: Environment) -> None: ...


@dataclass
class Fault(ABC):
    wt: WindTurbine

    def bofore_tick(self) -> None:
        pass

    def after_tick(self) -> None:
        pass

    def __str__(self) -> str:
        return self.__class__.__name__


@dataclass
class WindTurbineModel:
    name: str
    capacity: float  # In watts, e.g. 1,500,000 for 1.5 megawatts
    cut_in: float  # m/s
    rated: float  # m/s
    rotor_rpm: float  # max Rotations/min


# Contains the fault types and their associated probabilities
_wt_fault_types: Dict[Type[Fault], float] = dict()


@dataclass
class WindTurbine:
    # Components
    tower: Tower
    rotor: Rotor
    generator: Generator
    # Model
    model: WindTurbineModel
    # Faults and others
    faults: List[Fault] = field(default_factory=list)
    id: str = field(default_factory=id_factory('wt'))

    def get_readings(self, env: Environment) -> Dict[str, ReadingT]:
        readings: ReadingsT = dict(
            wt_id=self.id,
            model_name=self.model.name,
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
            comp.tick(self, env)
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
    def factory(cls, env: Environment, model: WindTurbineModel,
                id: str) -> WindTurbine:
        return cls(Tower.factory(env), Rotor.factory(env),
                   Generator.factory(env), model, id=id)

    @property
    def components(self) -> List[Component]:
        # Note that this is also the order in which the components are updated
        return [self.generator, self.tower, self.rotor]

    @classmethod
    def wt_fault(cls, prob: float) -> Callable[[Type[Fault]], Type[Fault]]:
        """Decorator used to register fault classes with the WT."""
        def wrapper(fault_cls: Type[Fault]) -> Type[Fault]:
            _wt_fault_types[fault_cls] = prob
            return fault_cls
        return wrapper


def wind_turbines_from_config(env: Environment, path: Path
                              ) -> List[WindTurbine]:
    with open(path) as fh:
        d = yaml.safe_load(fh)
    model_ds = d['models']
    wt_ds = d['turbines']
    models = {d['name']: WindTurbineModel(**d) for d in model_ds}
    wts = []
    for wt_d in wt_ds:
        model_name = wt_d.pop('model')
        if model_name not in models:
            raise ValueError(f'Unknown model in {path}: {model_name}')
        model = models[model_name]
        wt = WindTurbine.factory(env, model=model, id=wt_d['id'])
        wts.append(wt)
    return wts


@dataclass
class Tower(Component):
    vib_freq: float

    @classmethod
    def factory(cls, env: Environment) -> Tower:
        vib_freq = random.gauss(env.cfg.tower_vib_freq_mean,
                                env.cfg.tower_vib_freq_var)
        vib_freq = max(0, vib_freq)
        return cls(vib_freq=vib_freq)

    def get_readings(self, _: Environment) -> Dict[str, ReadingT]:
        return dict(tower_vib_freq=self.vib_freq)

    def tick(self, _: WindTurbine, env: Environment) -> None:
        vib_freq = random.gauss(env.cfg.tower_vib_freq_mean,
                                env.cfg.tower_vib_freq_var)
        self.vib_freq = max(0, vib_freq)


@dataclass
class Rotor(Component):
    rps: float

    @classmethod
    def factory(cls, _: Environment) -> Rotor:
        return cls(rps=0.)

    def get_readings(self, _: Environment) -> Dict[str, ReadingT]:
        return dict(rotor_rps=self.rps)

    def tick(self, wt: WindTurbine, env: Environment) -> None:
        rps = smooth_step(env.wind.mag,
                          offset=wt.model.cut_in,
                          width=wt.model.rated - wt.model.cut_in)
        rps *= wt.model.rotor_rpm / env.cfg.ticks_per_minute
        rps = rps * random.gauss(1., env.cfg.rotor_rps_relative_var)
        self.rps = max(0, rps)


@WindTurbine.wt_fault(P)
@dataclass
class RotorBladeSurfaceCrack(Fault):
    # Severety of the fault
    rps_factor: float = field(default_factory=partial(
                              random.betavariate, 20, 2))

    def after_tick(self) -> None:
        self.wt.rotor.rps *= self.rps_factor

    def __str__(self) -> str:
        return f'{self.__class__.__name__}[rps_factor={self.rps_factor:0.5}]'


@dataclass
class Generator(Component):
    temp: float
    power: float

    @classmethod
    def factory(cls, env: Environment) -> Generator:
        temp = env.temp
        return cls(temp=temp, power=0.)

    def get_readings(self, _: Environment) -> Dict[str, ReadingT]:
        return dict(generator_temp=self.temp, power=self.power)

    def tick(self, wt: WindTurbine, env: Environment) -> None:
        # Update temp
        temp_d = random.normalvariate(env.cfg.gen_temp_diff_mean,
                                      env.cfg.gen_temp_diff_var)
        self.temp = env.temp + temp_d
        # Update power
        self.power = (wt.model.capacity
                      * wt.rotor.rps
                      / (wt.model.rotor_rpm / env.cfg.ticks_per_minute))


@WindTurbine.wt_fault(P)
@dataclass
class GeneratorDamage(Fault):
    # Severety of the fault
    power_factor: float = field(default_factory=partial(
                                random.betavariate, 20, 2))

    def after_tick(self) -> None:
        self.wt.generator.power *= self.power_factor

    def __str__(self) -> str:
        return (f'{self.__class__.__name__}[power_factor='
                f'{self.power_factor:0.5}]')

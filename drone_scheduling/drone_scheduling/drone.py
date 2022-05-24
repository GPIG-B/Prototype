from logging import getLogger
from typing import Optional
from dataclasses import dataclass, field
import numpy as np
from .utils import norm
from enum import Enum

from . import drone_scheduling
from .utils import COORD_BIAS

logger = getLogger('drone_sched')

# 1 degree of lat = 111.32km
# 1 degree of long = 65.43km
# 0.45 degree of lat = 50km
# 0.9 degree of long = 59km

# constants
CHARGE_SPEED = 10 / 3600
CHARGE_COST = 0 / 1800
CRITICAL_BATTERY = 25


class Status(Enum):
    IDLE = 0
    TRAVELLING = 1
    CHARGING = 2
    INSPECTING = 3
    WARNING = 4
    CRITICAL = 5


@dataclass
class Drone():
    id: int
    status: Status
    station: int # station platform the drone currently belongs to
    position: np.ndarray
    speed = 0.1
    velocity: np.ndarray = field(init=False)
    target: Optional[np.ndarray] = None
    target_id: Optional[str] = None
    avoidance_path: list = field(init=False)
    battery = 100.0

    def move(self, delta: float) -> None:
        # logger.info(f'Drone[{self.id}] located at: {self.abs_pos}')
        self.position += (self.velocity * delta)
        self.battery = self.battery - (CHARGE_COST * delta)
        if self.battery < 0:
            self.battery = 0

    @property
    def abs_pos(self) -> np.ndarray:
        return self.position + COORD_BIAS

    def update_velocity(self, MFACTOR_LAT: float, MFACTOR_LONG: float) -> None:
        if self.target is None:
            self.velocity = np.array([0, 0])
        else:
            dir = self.target - self.position
            ndir = norm(dir)
            v = np.array([ndir[0] * MFACTOR_LAT, ndir[1] * MFACTOR_LONG])
            self.velocity = v * self.speed

    def charge_drone(self, delta: float) -> None:
        self.battery = min(100, self.battery + (CHARGE_SPEED * delta))

    def low_charge(self) -> bool:
        return self.battery < CRITICAL_BATTERY

    def set_target(self, pos: np.ndarray, wt_id: str) -> None:
        self.target = pos
        self.target_id = wt_id
        self.status = Status.TRAVELLING

    def erase_target(self) -> None:
        self.target = None
        self.target_id = None

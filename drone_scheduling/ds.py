'''
* Initialise stations from map
* Initialise drones from stations
- while True:
    Take inspection wt ids from ns, add them to the queue of outstanding
    inspections
    for insp in outstanting_inspections:
        try to find an idle drone near the wt, continue if none found
        set the target of the drone to be the wt
    for non-idle drone in drones:
        match drone.state:
            case travelling: update position
            case returning: update position
        if drone is near target wt:
            add wt to 'inspected' list on ns
            set the drones state to returning
'''
from __future__ import annotations
import time
from dataclasses import dataclass, field
from typing import Optional, Any, List, Dict, Union, ClassVar
from enum import Enum, auto
from logging import getLogger
import numpy as np

from manager import Client


logger = getLogger('drone_sched')


MARGIN = 0.001


@dataclass
class Vec:
    x: float
    y: float

    @classmethod
    def from_lat_lng(cls, d: Dict[str, Any]) -> Vec:
        return cls(float(d['lat']), float(d['lng']))

    def __sub__(self, other: Vec) -> Vec:
        return Vec(self.x - other.x, self.y - other.y)

    def __add__(self, other: Vec) -> Vec:
        return Vec(self.x + other.x, self.y + other.y)

    def __mul__(self, s: Union[float, Vec]) -> Vec:
        if isinstance(s, float):
            return Vec(self.x * s, self.y * s)
        return Vec(self.x * s.x, self.y * s.y)

    def __str__(self) -> str:
        return f'({self.x}, {self.y})'

    def mag(self) -> float:
        return (self.x**2 + self.y**2)**0.5

    def norm(self) -> Vec:
        return self * (1 / self.mag())


@dataclass
class Station:
    pos: Vec


class State(Enum):
    IDLE = auto()
    TRAVELLING = auto()
    RETURNING = auto()
    INSPECTING = auto()


_next_x = 0
def next_drone_id() -> str:
    global _next_x
    x = _next_x
    _next_x += 1
    return f'Drone_{x}'


@dataclass
class Drone:
    pos: Vec
    station: Station
    id: str = field(default_factory=next_drone_id)
    target_pos: Optional[Vec] = None
    target_id: Optional[str] = None
    state: State = State.IDLE
    inspection_ticks: int = 0

    DRONE_SPEED: ClassVar[Vec] = Vec(0.002, 0.002)

    @classmethod
    def from_map(cls, map_cfg: Dict[str, Any]) -> List[Drone]:
        stations = []
        for station_dict in map_cfg['stations']:
            stations.append(Station(Vec.from_lat_lng(station_dict)))
        drones = []
        for station in stations:
            drones.append(cls(station.pos, station))
        return drones

    def set_target(self, pos: Vec, wt_id: str) -> None:
        self.target_pos = pos
        self.target_id = wt_id
        self.inspection_ticks = 10
        self.state = State.TRAVELLING

    def erase_target(self) -> None:
        self.target_pos = None
        self.target_id = None

    def move_towards(self, dest: Vec) -> None:
        delta = dest - self.pos
        if delta.mag() > Drone.DRONE_SPEED.mag():
            delta = delta.norm() * Drone.DRONE_SPEED
        self.pos += delta
        # logger.info(f'{self} moving by {delta} to {self.pos}')

    def __str__(self) -> str:
        return f'Drone[{self.id}]'

    def is_close_to(self, pos: Vec) -> bool:
        return (pos - self.pos).mag() < MARGIN


def loop(client: Client, drones: List[Drone]) -> None:
    '''Main loop of the drone scheduler. To kee things as simple as possible,
    almost all code is kept in here.'''
    TIME_DELTA = 1.
    wt_dicts = client.get_ns().map_cfg['turbines']
    fault_queue: List[str] = []
    client.get_ns().inspected = []
    client.get_ns().drone_positions = []
    while True:
        # Update fault_queue with newest alerts
        sensor_alerts = get_attr(client, 'sensor_alerts')
        fault_queue = list(set(fault_queue).union(set(sensor_alerts)))
        finished_inspections: List[str] = []
        sensor_alerts: List[str] = client.get_ns().sensor_alerts
        # Assign the closest idle drone to each fault
        for alerted_wt_id in sensor_alerts:
            idle_drones = [d for d in drones if d.state == State.IDLE]
            if not idle_drones:
                break
            # Get the position of the WT
            wts = [t for t in wt_dicts if t['id'] == alerted_wt_id]
            if not wts:
                logger.error(f'Unknown WT id: {alerted_wt_id}')
                continue
            wt_dict, *_ = wts
            wt_pos = Vec.from_lat_lng(wt_dict)
            distances = [(d.pos - wt_pos).mag() for d in idle_drones]
            index: int = int(np.argmin(np.array(distances)))
            closest_drone = idle_drones[index]
            closest_drone.set_target(wt_pos, alerted_wt_id)
            logger.info(f'Assigned {closest_drone} to WT{alerted_wt_id}')
        # Update non-idle drones
        for drone in drones:
            if drone.state == State.IDLE:
                continue
            elif drone.state == State.TRAVELLING:
                assert drone.target_pos is not None
                assert drone.target_id is not None
                drone.move_towards(drone.target_pos)
                if drone.is_close_to(drone.target_pos):
                    # The drone has reached the target
                    drone.state = State.INSPECTING
                    logger.info(f'{drone} reached WT[{drone.target_id}]')
            elif drone.state == State.INSPECTING:
                if drone.inspection_ticks > 0:
                    drone.inspection_ticks -= 1
                    continue
                assert drone.target_id is not None
                finished_inspections.append(drone.target_id)
                drone.state = State.RETURNING
                logger.info(f'{drone} finished inspection of'
                            f' WT[{drone.target_id}]')
                drone.erase_target()
            else:  # State.RETURNING
                drone.move_towards(drone.station.pos)
                if drone.is_close_to(drone.station.pos):
                    # The drone has reached the station
                    drone.state = State.IDLE
                    logger.info(f'{drone} reached station')
        # Carry over previously finished inspections
        ns = client.get_ns()
        if not hasattr(ns, 'finished_inspections'):
            ns.finished_inspections = []
        prev: List[str] = ns.finished_inspections
        prev.extend(finished_inspections)
        ns.finished_inspections = prev
        time.sleep(TIME_DELTA)
        client.get_ns().drone_positions = [{'drone_id': d.id,
                                            'lat': d.pos.x,
                                            'lng': d.pos.y,
                                            'status': 'idle'
                                                if d.state == State.IDLE
                                                else 'travelling'}
                                            for d in drones]


def get_attr(client: Client, attr: str) -> Any:
    while True:
        ns = client.get_ns()
        if hasattr(ns, attr):
            return getattr(ns, attr)
        time.sleep(0.1)  # lmao

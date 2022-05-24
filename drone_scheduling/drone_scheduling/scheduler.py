from logging import getLogger
from typing import List, Tuple, Dict
import numpy as np
from .drone import Status, Drone
from . import utils
from dataclasses import dataclass, field


logger = getLogger('drone_sched')


@dataclass
class Scheduler():
    inspection_queue: List[Tuple[np.ndarray, str]] = field(
            default_factory=list)

    def schedule(self, drones: List[Drone]) -> List[str]:
        stop = len(self.inspection_queue) == 0
        inspected: List[str] = []
        index = 0
        while not stop:
            pos, wt_id = self.inspection_queue[index]
            evaluated = self.evaluate_fault(drones, pos)
            if evaluated:
                self.inspection_queue.pop(index)
                inspected.append(wt_id)
            else:
                index += 1
            if index == len(self.inspection_queue):
                stop = True
        return inspected

    def update(self, drones: List[Drone]) -> List[str]:
        '''Returns a list of WT ids that were inspected.'''
        q = self.inspection_queue
        while q:
            pos, wt_id = q.pop()
            drone_id = self.assign_drone(drones, pos, wt_id)
            if drone_id >= 0:
                logger.info(f'Assigned Drone[{drone_id}] to WT[{wt_id}].')
        completed_inspections = []
        for drone in drones:
            if drone.target is None:
                continue
            if self.has_reached_target(drone):
                logger.info(f'Drone[{drone.id}] reached its target.')
                completed_inspections.append(drone.target_id)
        return completed_inspections

    def assign_drone(self, drones: List[Drone], pos: np.ndarray, wt_id: str
                     ) -> int:
        '''Assigns the closest idle drone to the target. Returns the drone's
        id.'''
        turbine = np.array(pos)
        available_drones = []
        for drone in drones:
            if self.is_available(drone, turbine):
                available_drones.append(drone)
        if not available_drones:
            return -1
        distances = [utils.distance_between(drone.position, turbine)
                     for drone in available_drones]
        closest_idx = np.argmax(np.array(distances))
        closest_drone = available_drones[closest_idx]
        closest_drone.set_target(pos, wt_id)
        return closest_drone.id

    def has_reached_target(self, drone: Drone) -> bool:
        '''Returns whether the given drone has reached its target.'''
        if drone.target is None:
            raise ValueError(f'Expected target, got none for drone {drone.id}')
        return utils.distance_between(drone.position, drone.target) < 100

    def evaluate_fault(self, drones: List[Drone], turbine_pos: np.ndarray
                       ) -> bool:
        '''Returns whether an inspection has been finished?'''
        # Unclear what this function does or how it works...
        turbine = np.array(turbine_pos)
        available_drones = []
        for drone in drones:
            if self.is_available(drone, turbine):
                available_drones.append(drone)
        distances: Dict[int, float] = {}
        for drone in available_drones:
            dist = utils.distance_between(drone.position, turbine)
            distances[drone.id] = 15000 - dist
        # What? What does 14400 mean?
        if sum(distances.values()) < 14400:
            return False
        inspection_drones = []
        total = 0
        while total < 14400:
            d = drones[sorted_drones.pop()]
            value = distances[d.id]
            inspection_drones.append(d)
            total += value
        for drone in inspection_drones:
            drone.target = turbine
            drone.status = Status.TRAVELLING
        # takes in a set of drones and a target turbine to be inspected
        # if it can allocate enough drones to this inspections it changes
        # their target, to the turbine, and returns True
        # otherwise it returns False
        return True

    def is_available(self, drone: Drone, turbine: np.ndarray) -> bool:
        if drone.status != Status.IDLE:
            return False
        # Within 15km?
        dist = utils.distance_between(drone.position, turbine)
        return bool(dist > 5000)

    def add_inspection(self, turbine: np.ndarray, wt_id: str) -> None:
        self.inspection_queue.append((np.array(turbine), wt_id))


# not no station - must have a station
# idle status
# full charge
# within range
# no target

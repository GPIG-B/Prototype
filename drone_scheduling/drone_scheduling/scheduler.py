import numpy as np
from .drone import Status
from . import utils
from dataclasses import dataclass, field


@dataclass
class Scheduler():
    inspection_queue: list  = field(default_factory=list)

    # pop list
    def schedule(self, drones):
        stop = False
        index = 0
        if len(self.inspection_queue) == 0:
            stop = True
        while stop == False:
            evaluated = self.evaluate_fault(drones,
                                            self.inspection_queue[index])
            if evaluated:
                self.inspection_queue.pop(index)
            else:
                index += 1
            if index == len(self.inspection_queue):
                stop = True

    def evaluate_fault(self, drones, turbine_pos):
        turbine = np.array(turbine_pos)
        available_drones = []
        for drone in drones:
            if self.is_available(drone, turbine):
                available_drones.append(drone)
        drone_worth = {}
        for drone in available_drones:
            dist = utils.distance_between(drone.position, turbine)
            drone_worth[drone.id] = 15000 - dist
        if sum(drone_worth.values()) < 14400:
            return False
        sorted_drones = sorted(drone_worth.keys())
        inspection_drones = []
        total = 0
        while total < 14400:
            d = drones[sorted_drones.pop()]
            value = drone_worth[d.id]
            inspection_drones.append(d)
            total += value
        for drone in inspection_drones:
            drone.target = turbine
            # print("target assigned")
            drone.status = Status.TRAVELLING
        # takes in a set of drones and a target turbine to be inspected
        # if it can allocate enough drones to this inspections it changes
        # their target, to the turbine, and returns True
        # otherwise it returns False
        return True

    def is_available(self, drone, turbine):
        if drone.status != Status.IDLE: return False
        # Within 15km?
        dist = utils.distance_between(drone.position, turbine)
        if dist > 5000:
            return False
        return True

    def add_inspection(self, turbine):
        self.inspection_queue.append(turbine)
        return

# not no station - must have a station
# idle status
# full charge
# within range
# no target

from dataclasses import dataclass, field
import enum
import numpy as np
import math
from utils import norm
from enum import Enum

# 1 degree of lat = 111.32km
# 1 degree of long = 65.43km
# 0.45 degree of lat = 50km
# 0.9 degree of long = 59km


# constants
CHARGE_SPEED = 100 / 3600
CHARGE_COST = 100 / 1800
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
    id : int
    status : Status
    station : int # station platform the drone currently belongs to
    position : np.array
    speed = 12
    velocity : np.array = field(init=False)
    target : list = None
    avoidance_path : list = field(init=False)
    battery = 100.0
    
    def move(self, delta):
        self.position += (self.velocity * delta)
        self.battery = self.battery - (CHARGE_COST * delta)
        if self.battery < 0:
            self.battery = 0
        return

    def update_velocity(self, MFACTOR_LAT, MFACTOR_LONG):
        if self.target is None:
            self.velocity = np.array([0, 0])
        else:
            dir = self.target - self.position
            ndir = norm(dir)
            v = np.array([ndir[0] * MFACTOR_LAT, ndir[1] * MFACTOR_LONG])
            self.velocity = v * self.speed
        return

    def charge_drone(self, delta):
        self.battery = self.battery + (CHARGE_SPEED * delta)
        if self.battery > 100: self.battery = 100

    def low_charge(self):
        if self.battery < CRITICAL_BATTERY:
            return True
        return False

# Water, Earth, Fire, Air
class air(Drone):
    def move():
        return

class water(Drone):
    def move():
        return
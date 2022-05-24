from typing import List
import numpy as np
import csv
import random
import math
import pygame as pg
from logging import getLogger

from .drone import Drone, Status
from . import utils
from .utils import LAT_BIAS, LNG_BIAS
from .scheduler import Scheduler


logger = getLogger('drone_sched')

# Constants
STATION_DRONE_NO = 5
SCREEN_SIZE_FACTOR = 2000 # ratio from lat/long pg pixel size
SIMULATION_SPEED = 600
MFACTOR_LAT = 0.45 / 50000 # 1metre in lat/long coordinates (roughly)
MFACTOR_LONG = 0.9 / 59000
STATION_RANGE = 5000 # Range of station in metres
WT_INSPECTION_TIME = 5 * 60 * 60
TIME_BETWEEN_FAULTS = 100 # seconds


white = (255, 255, 255)
lightblue = (200, 200, 255)
black = (0, 0, 0)
red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)
orange = (255, 128, 0)


def main() -> None:
    width, height = 1800, 900
    pg.init()
    screen = pg.display.set_mode((width, height))
    stations = load_positions('drone_scheduling/stations.txt')
    turbines = load_positions('drone_scheduling/turbines.txt')
    drones = inititialise_drones(stations)
    scheduler = Scheduler()
    running = True
    clock = pg.time.Clock()
    inspection_timer = 0.0
    pause = False
    while running:
        # Input
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    running = False
                elif event.key == pg.K_p:
                    if pause is True:
                        pause = False
                    else:
                        pause = True
            elif event.type == pg.MOUSEBUTTONUP:
                pos = pg.mouse.get_pos()
                # print(pos)
                print(53.65 + pos[1] / SCREEN_SIZE_FACTOR,",", 1.5 + pos[0] / SCREEN_SIZE_FACTOR)
        delta = clock.tick(60) / 1000 * SIMULATION_SPEED
        if not pause:
            inspection_timer += delta
            if inspection_timer > TIME_BETWEEN_FAULTS:
                scheduler.add_inspection(np.array(turbines[random.randrange(len(turbines))]))
                inspection_timer = 0
            scheduler.schedule(drones)
            update(stations, drones, delta)
        render(screen, stations, turbines, drones)


def generate_turbine_nodes(turbine: np.ndarray, distance: float
                           ) -> List[np.ndarray]:
    turbine_nodes = []
    lat1 = distance * MFACTOR_LAT
    long1 = distance * MFACTOR_LONG
    hypot = math.sqrt((distance ** 2)/2)
    lat2 = hypot * MFACTOR_LAT
    long2 = hypot * MFACTOR_LONG
    offsets = []
    offsets1 = [[1,0],[0,1],[-1,0],[0,-1]]
    offsets2 = [[1,1],[-1,1],[-1,-1],[1,-1]]
    for i in range(4):
        offsets1[i] = [offsets1[i][0] * lat1, offsets1[i][1] * long1]
    for i in range(4):
        offsets2[i] = [offsets2[i][0] * lat2, offsets2[i][1] * long2]
    for x in range(4):
        offsets.append(offsets1[x])
        offsets.append(offsets2[x])
    for offset in offsets:
        node = np.add(turbine,np.array(offset))
        turbine_nodes.append(node)
    return turbine_nodes


def load_positions(filepath: str) -> List[np.ndarray]:
    positions = []
    with open(filepath, 'r') as fd:
        reader = csv.reader(fd)
        for row in reader:
            positions.append([float(row[0]) - 53.65,float(row[1]) - 1.5])
    return positions


def inititialise_drones(stations: List[np.ndarray]) -> List[Drone]:
    drones = []
    for x in range(len(stations)):
        for y in range(STATION_DRONE_NO):
            id = (STATION_DRONE_NO * x) + y
            drone = Drone(id, Status.IDLE, x, np.array(stations[x]))
            drones.append(drone)
    return drones


def update(stations, drones, delta):
    # if within a station, assign drone to that station
    # if drone has low charge and not charging, change their target to nearest station
    # if near target, remove target

    # Update drone status'
    # Update drone stations
    # Check drone charge, if low assign new targets
    # Check if drones have reached their target turbine

    # Update drone velocity
    # Move drones
    # CHARGE DRONES IF CLOSE TO STATION (within 50)
    for drone in drones:
        if drone.target is None:
            continue
        if not near(drone.position, drone.target, 100):
            continue
        logger.info(f'Drone {drone.id} reached target: {drone.target}')
        drone.target = None
    # If near station, set station
    for drone in drones:
        drone.station = None
        for i, s in enumerate(stations):
            if near(drone.position, np.array(s), 100) and drone.target is None:
                drone.station = i
    for drone in drones:
        if drone.low_charge() and drone.station == None:
            logger.info(f'Low battery on drone {drone.id}, flying to station '
                        f'{drone.target}')
            drone.target = stations[closest_station(drone.position, stations)]
            drone.status = Status.TRAVELLING
    for drone in drones:
        if drone.station is None:
            continue
        if near(drone.position, np.array(stations[drone.station]), 110):
            if drone.battery >= 100.0:
                drone.status = Status.IDLE
            else:
                if drone.status != Status.CHARGING:
                    logger.info(f'Drone {drone.id} started charging.')
                drone.charge_drone(delta)
                drone.status = Status.CHARGING
    # Check target turbine, if near, remove target
    # CHECK FOR OBSTRUCTING TURBINES AND GENERATE AVOIDANCE PATH
    # Update drone velocity
    for drone in drones:
        drone.update_velocity(MFACTOR_LAT, MFACTOR_LONG)
    # Move drones
    for drone in drones:
        if (drone.status == Status.TRAVELLING \
            or drone.status == Status.INSPECTING) \
            and drone.battery > 0:
            drone.move(delta)
    # CHARGE DRONES IF CLOSE TO STATION (within 50)
    return


def render(screen, stations, turbines, drones):
    screen.fill(white)
    for station in stations:
        pg.draw.rect(screen, orange, ((station[1] * SCREEN_SIZE_FACTOR) - 5,
                     (station[0] * SCREEN_SIZE_FACTOR) - 5, 10, 10), 0)
        lat_length = MFACTOR_LAT * STATION_RANGE * SCREEN_SIZE_FACTOR
        long_length = MFACTOR_LONG * STATION_RANGE * SCREEN_SIZE_FACTOR
        pg.draw.ellipse(screen,orange,
                        ((station[1] * SCREEN_SIZE_FACTOR) - long_length,
                         (station[0] * SCREEN_SIZE_FACTOR) - lat_length,
                         long_length * 2, lat_length * 2), 1)
    # group = pg.sprite.RenderPlain()
    for turbine in turbines:
        pg.draw.circle(screen, black, (turbine[1] * SCREEN_SIZE_FACTOR,
                                       turbine[0] * SCREEN_SIZE_FACTOR), 3)
    for drone in drones:
        pg.draw.circle(screen, blue, (drone.position[1] * SCREEN_SIZE_FACTOR,
                                      drone.position[0] * SCREEN_SIZE_FACTOR),
                       3)
    points = generate_turbine_nodes(turbines[60], 200)
    for p in points: pg.draw.circle(screen, red, (p[1] * SCREEN_SIZE_FACTOR,
                                                  p[0] * SCREEN_SIZE_FACTOR), 1)
    pg.display.flip()
    return


def near(a, b , metres):
    return utils.distance_between(a, b) < metres


def closest_station(pos, stations):
    distances = [utils.distance_between(pos, np.array(s))
                 for s in stations]
    return np.argmin(np.array(distances))


class TurbineSprite(pg.sprite.Sprite):

    def __init__(self, pos):
        super().__init__()
        image = pg.image.load('drone_scheduling/turbine.png')
        image = pg.transform.scale(image, (3, 2))
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.center = pos

    def update(self):
        pass


if __name__ == "__main__":
    main()

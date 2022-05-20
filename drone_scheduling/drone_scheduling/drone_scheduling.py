import numpy as np
from drone import Drone, Status
import csv
import pygame as pg
import random
import utils
import math
from scheduler import Scheduler

# Constants
STATION_DRONE_NO = 5
SCREEN_SIZE_FACTOR = 2000 # ratio from lat/long pg pixel size
SIMULATION_SPEED = 600
MFACTOR_LAT = 0.45 / 50000 # 1metre in lat/long coordinates (roughly)
MFACTOR_LONG = 0.9 / 59000
STATION_RANGE = 5000 # Range of station in metres
WT_INSPECTION_TIME = 15 * 60
TIME_BETWEEN_FAULTS = 100 # seconds

white = (255, 255, 255)
lightblue = (200, 200, 255)
black = (0, 0, 0)
red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)
orange = (255, 128, 0)

def main():
    width, height = 1800, 900
    pg.init()
    screen = pg.display.set_mode((width, height))
    
    # north: 54.1,
    # east: 2.4,
    # south: 53.65,
    # west: 1.5,

    58680
    origin = np.array([53.65, 1.5]) # y, x
    bound = np.array([54.1, 2.4])
    mapped_origin = [0, 0]
    mapped_bound = bound- origin
    # 77360
    # print(mapped_bound)

    stations = load_positions('stations.txt')
    turbines = load_positions('turbines.txt')
    drones = intitialise_drones(stations)

    # Assign random targets
    # for d in drones:
    #     d.target = np.array(turbines[random.randrange(len(turbines))])
    #     d.status = Status.TRAVELLING

    drone_pack = []
    simulation_length = 1000000

    scheduler = Scheduler()

    running = True
    # ticks = 0
    clock = pg.time.Clock()

    inspection_timer = 0.0

    pause = False

    while running:
        
        inspect = True
        # for drone in drones:
        #     print(drone.battery)
        # print()

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
                elif event.key == pg.K_w:
                    inspect = True
            elif event.type == pg.MOUSEBUTTONUP:
                pos = pg.mouse.get_pos()
                # print(pos)
                print(53.65 + pos[1] / SCREEN_SIZE_FACTOR,",", 1.5 + pos[0] / SCREEN_SIZE_FACTOR)

        delta = clock.tick(60) / 1000 * SIMULATION_SPEED

        if not pause:
            inspection_timer += delta

            if inspection_timer > TIME_BETWEEN_FAULTS:
                scheduler.add_inspection(np.array(turbines[random.randrange(len(turbines))]))
                # print(len(scheduler.inspection_queue))
                inspection_timer = 0

            if inspect == True: scheduler.schedule(drones)
            update(stations, turbines, drones, delta)
        render(screen, stations, turbines, drones)

        # if ticks >= simulation_length:
        #     running = False
        # ticks += 1

def generate_turbine_nodes(position, turbine, target, distance):
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

def generate_avoidance_path():
    return
    
def event():
    return

def load_positions(filepath):
    positions = []
    with open(filepath, 'r') as fd:
        reader = csv.reader(fd)
        for row in reader:
            positions.append([float(row[0]) - 53.65,float(row[1]) - 1.5])
    return positions

def intitialise_drones(stations):
    drones = []
    for x in range(len(stations)):
        for y in range(STATION_DRONE_NO):
            id = (STATION_DRONE_NO * x) + y
            drone = Drone(id, Status.IDLE, x, np.array(stations[x]))
            drones.append(drone)
    return drones

def update(stations, turbines, drones, delta):
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
        if not drone.target is None:
            if near(drone.position, drone.target, 100):
                drone.target = None

    # If near station, set station
    for drone in drones:
        drone.station = None
        for i in range(len(stations)):
            if near(drone.position, np.array(stations[i]), 100) and drone.target is None:
                drone.station = i

    for drone in drones:
        if drone.low_charge() and drone.station == None:
            drone.target = stations[closest_station(drone.position, stations)]
            drone.status = Status.TRAVELLING
    
    for drone in drones:
        if not drone.station is None:
            if near(drone.position, np.array(stations[drone.station]), 110):
                if drone.battery >= 100.0:
                    drone.status = Status.IDLE
                else:
                    drone.charge_drone(delta)
                    drone.status = Status.CHARGING

    # Check target turbine, if near, remove target

    # CHECK FOR OBSTRUCTING TURBINES AND GENERATE AVOIDANCE PATH

    # for drone in drones:
    #     for turbine in turbines:
    #         if turbine != drone.target:
    #             if near(drone.position, turbine, 100):
    #                 drone.avoidance_path = generate_avoidance_path()
    #                 drone.avoidance_path = generate_turbine_nodes(drone.position, turbine, drone.target, 100)

    # Update drone velocity
    for drone in drones:
        drone.update_velocity(MFACTOR_LAT, MFACTOR_LONG)
    
    # Move drones
    for drone in drones:
        # if (not drone.target is None) and drone.battery > 0:
        if (drone.status == Status.TRAVELLING or drone.status == Status.INSPECTING) and drone.battery > 0:
            drone.move(delta)
    
    # CHARGE DRONES IF CLOSE TO STATION (within 50)
    

    return

def render(screen, stations, turbines, drones):
    screen.fill(white)
    for station in stations:
        pg.draw.rect(screen, orange, ((station[1] * SCREEN_SIZE_FACTOR) - 5, (station[0] * SCREEN_SIZE_FACTOR) - 5, 10, 10), 0)
        lat_length = MFACTOR_LAT * STATION_RANGE * SCREEN_SIZE_FACTOR
        long_length = MFACTOR_LONG * STATION_RANGE * SCREEN_SIZE_FACTOR
        pg.draw.ellipse(screen,orange,((station[1] * SCREEN_SIZE_FACTOR) - long_length, (station[0] * SCREEN_SIZE_FACTOR) - lat_length, long_length * 2, lat_length * 2), 1)
    
    # group = pg.sprite.RenderPlain()
    for turbine in turbines:
        pg.draw.circle(screen, black, (turbine[1] * SCREEN_SIZE_FACTOR, turbine[0] * SCREEN_SIZE_FACTOR), 3)
        # t = TurbineSprite(turbine)
        # group.add(t)
    
    for drone in drones: pg.draw.circle(screen, blue, (drone.position[1] * SCREEN_SIZE_FACTOR, drone.position[0] * SCREEN_SIZE_FACTOR), 3)

    points = generate_turbine_nodes(drones[0].position, turbines[60], drones[0].target, 200)
    for p in points: pg.draw.circle(screen, red, (p[1] * SCREEN_SIZE_FACTOR, p[0] * SCREEN_SIZE_FACTOR), 1)

    # group.draw(screen)
    pg.display.flip()
    return

def near(a, b , metres):

    pos1 = utils.convert_to_metres(a)
    pos2 = utils.convert_to_metres(b)
    if utils.distance_between(a, b) < metres: return True
    return False

def closest_station(pos, stations):
    station_no : int
    lowest_distance = 10000000
    station_no = 0
    for x in range(len(stations)):
        dist = utils.distance_between(pos, np.array(stations[x]))
        if dist < lowest_distance:
            lowest_distance = dist
            station_no = x
    return station_no

class TurbineSprite(pg.sprite.Sprite):

    def __init__(self, pos):
        super(TurbineSprite, self).__init__()
        image = pg.image.load('turbine.png')
        image = pg.transform.scale(image, (3, 2))
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.center = pos

    def update(self):
        pass

if __name__ == "__main__": main()
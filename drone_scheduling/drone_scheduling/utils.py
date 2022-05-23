import numpy as np


MFACTOR_LAT = 0.45 / 50000
MFACTOR_LONG = 0.9 / 59000


def norm(v):
    norm = np.linalg.norm(v)
    if norm == 0:
       return v
    return v / norm


def distance_between(a,b):
    pos1 = convert_to_metres(a)
    pos2 = convert_to_metres(b)
    return np.linalg.norm(pos1-pos2)


def convert_to_metres(pos):
    return  np.array([pos[0] / MFACTOR_LAT, pos[1] / MFACTOR_LONG])

import numpy as np


LAT_BIAS = 53.65
LNG_BIAS = 1.5

COORD_BIAS = np.array([LAT_BIAS, LNG_BIAS])

MFACTOR_LAT = 0.45 / 50000
MFACTOR_LONG = 0.9 / 59000


def norm(v: np.ndarray) -> np.ndarray:
    norm = np.linalg.norm(v)
    if norm == 0:
       return v
    return v / norm


def distance_between(a: np.ndarray, b: np.ndarray) -> float:
    pos1 = convert_to_metres(a)
    pos2 = convert_to_metres(b)
    return float(np.linalg.norm(pos1 - pos2))  # type: ignore


def convert_to_metres(pos: np.ndarray) -> np.ndarray:
    return np.array([pos[0] / MFACTOR_LAT, pos[1] / MFACTOR_LONG])

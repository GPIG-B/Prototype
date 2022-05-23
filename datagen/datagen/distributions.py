import math
import random
from itertools import count
from typing import Iterator

from .config import Config
from .utils import Autocorr, Vec2, isum


def make_temp_iter(cfg: Config) -> Iterator[float]:
    def annual_dist(x: float) -> float:
        annual = math.sin(2 * math.pi * x)
        annual = annual * 0.5 * cfg.temp_annual_spread
        return random.gauss(annual, cfg.temp_annual_std)

    def daily_dist(x: float) -> float:
        daily = math.sin(2 * math.pi * x)
        daily = daily * 0.5 * cfg.temp_daily_spread
        return random.gauss(daily, cfg.temp_daily_std)

    annual_iter = Autocorr(dist=annual_dist,
                           alpha=0.1, beta=5,
                           increment=1 / cfg.ticks_per_year)
    daily_iter = Autocorr(dist=daily_dist,
                          alpha=0.5, beta=10,
                          increment=1 / cfg.ticks_per_day)
    mean_iter = (cfg.temp_mean for _ in count())
    return isum(0., mean_iter, daily_iter, annual_iter)


def make_wind_iter(cfg: Config) -> Iterator[Vec2]:
    angle_autocorr = Autocorr(dist=lambda _: random.random() * math.pi * 4,
                              alpha=0.5, beta=10,
                              increment=1 / cfg.ticks_per_day)
    angle_iter = (x % (2 * math.pi) for x in angle_autocorr)
    mag_autocorr = Autocorr(dist=lambda _: random.gauss(cfg.wind_mag_mean,
                                                        cfg.wind_mag_var),
                            alpha=0.5, beta=10,
                            increment=1 / cfg.ticks_per_day)
    mag_iter = (max(0, x) for x in mag_autocorr)
    wind_iter = map(Vec2, angle_iter, mag_iter)
    return wind_iter


def make_wave_iter(cfg: Config, wind_iter: Iterator[Vec2]) -> Iterator[float]:
    mags = (max(w.mag, 1.) for w in wind_iter)
    mags = (mag + random.gauss(0., cfg.wind_mag_var) for mag in mags)
    mags = (max(0., mag) for mag in mags)
    return mags


def make_vis_iter(cfg: Config) -> Iterator[float]:
    vis_autocorr = Autocorr(dist=lambda _: random.gauss(cfg.vis_mean,
                                                        cfg.vis_var),
                            alpha=0.5, beta=10,
                            increment=1 / cfg.ticks_per_day)
    vis_iter = (max(10., x) for x in vis_autocorr)
    return vis_iter

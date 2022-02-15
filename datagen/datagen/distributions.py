import math
import random
from typing import Iterator

from .config import Config
from .utils import autocorr, Vec2, isum


def make_temp_iter(cfg: Config) -> Iterator[float]:
    def annual_dist(x: float) -> float:
        annual = math.sin(2 * math.pi * x)
        annual = annual * 0.5 * cfg.temp_annual_spread
        return random.gauss(annual, cfg.temp_annual_std)

    def daily_dist(x: float) -> float:
        daily = math.sin(2 * math.pi * x)
        daily = daily * 0.5 * cfg.temp_daily_spread
        return random.gauss(daily, cfg.temp_daily_std)

    annual_iter = autocorr(period=cfg.ticks_per_year,
                           jitter=cfg.temp_jitter,
                           dist=annual_dist)
    daily_iter = autocorr(period=cfg.ticks_per_day,
                          jitter=cfg.temp_jitter,
                          dist=daily_dist)
    return isum(cfg.temp_mean, daily_iter, annual_iter)


def make_wind_iter(cfg: Config) -> Iterator[Vec2]:
    angle_iter = autocorr(period=cfg.ticks_per_day,
                          jitter=cfg.wind_angle_jitter,
                          dist=lambda _: random.random() * math.pi * 2)
    mag_iter = autocorr(period=cfg.ticks_per_day,
                        jitter=cfg.wind_mag_jitter,
                        dist=lambda _: random.gauss(cfg.wind_mag_mean,
                                                    cfg.wind_mag_var))
    wind_iter = map(Vec2, angle_iter, mag_iter)
    return wind_iter

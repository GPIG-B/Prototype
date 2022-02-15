from dataclasses import dataclass


@dataclass(frozen=True)
class Config:
    tick_freq: int = 60 * 60  # seconds
    # Wind
    wind_mag_mean: float = 5.5  # metres / second
    wind_mag_var: float = 3.1
    wind_angle_jitter: float = 0.5
    wind_mag_jitter: float = 0.5
    # Temp
    temp_mean: float = 8.1  # degree Celsius
    temp_jitter: float = 0.5
    temp_annual_spread: float = 10.0  # degree Celsius
    temp_daily_spread: float = 7.0  # degree Celsius0
    temp_daily_std: float = 2.0  # degree Celsius.
    temp_annual_std: float = 2.0  # degree Celsius.
    # Factor to convert between wind metres/sec and rotor rotations/sec
    rotor_rps_wind_fact: float = 0.15
    rotor_rps_alpha: float = 0.9998
    rotor_rps_relative_var: float = 0.01
    tower_vib_freq_mean: float = 4.3e3  # Hz
    tower_vib_freq_var: float = 2e2  # Hz
    # Generator temperature
    gen_temp_diff_mean: float = 2.0  # degree Celsius
    gen_temp_diff_var: float = 0.5  # degree Celsius
    gen_temp_alpha: float = 0.99999

    @property
    def ticks_per_day(self) -> int:
        return int(24 * 60 * 60 / self.tick_freq)

    @property
    def ticks_per_year(self) -> int:
        return int(356 * 24 * 60 * 60 / self.tick_freq)

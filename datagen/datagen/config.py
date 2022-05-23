import dataclasses
from dataclasses import dataclass
from pathlib import Path
import yaml
import logging


logger = logging.getLogger('datagen')


@dataclass
class Config:
    _ticks_per_second: float = 1.
    wts: int = 3  # Number of wind turbines
    tick_freq: int = 60 * 60  # seconds
    # Wind
    wind_mag_mean: float = 5.5  # metres / second
    wind_mag_var: float = 3.1
    wind_angle_jitter: float = 0.5
    wind_mag_jitter: float = 0.5
    # Wind
    wind_to_wave_scalar: float = 0.7
    wave_mag_var: float = 0.3
    # Visibility
    vis_mean: float = 1300
    vis_var: float = 400
    # Temp
    temp_mean: float = 8.1  # degree Celsius
    temp_jitter: float = 0.5
    temp_annual_spread: float = 10.0  # degree Celsius
    temp_daily_spread: float = 7.0  # degree Celsius0
    temp_daily_std: float = 2.0  # degree Celsius.
    temp_annual_std: float = 2.0  # degree Celsius.
    # Factor to convert between wind metres/sec and rotor rotations/sec
    rotor_rps_alpha: float = 0.9998
    rotor_rps_relative_var: float = 0.01
    tower_vib_freq_mean: float = 4.3e3  # Hz
    tower_vib_freq_var: float = 2e2  # Hz
    # Generator temperature
    gen_temp_diff_mean: float = 2.0  # degree Celsius
    gen_temp_diff_var: float = 0.5  # degree Celsius
    # Data
    history_length: int = 1024  # in ticks

    @property
    def ticks_per_day(self) -> float:
        return 24 * 60 * 60 / self.tick_freq

    @property
    def ticks_per_minute(self) -> float:
        return 60 / self.tick_freq

    @property
    def ticks_per_year(self) -> float:
        return 356 * 24 * 60 * 60 / self.tick_freq

    @classmethod
    def from_yaml(cls, path: Path) -> 'Config':
        cfg = cls()._update_from_yaml(path)
        return cfg

    def _update_from_yaml(self, path: Path) -> 'Config':
        if not path.exists():
            raise FileNotFoundError(f'File does not exist: {path}')
        fields = {field.name: field.type
                  for field in dataclasses.fields(Config)}
        with open(path, 'r') as fh:
            kwargs = yaml.safe_load(fh)
        for key, value in kwargs.items():
            if key not in fields:
                raise ValueError(f'Unknown field: {key}, expected one of '
                                 f'{list(fields.keys())}')
            expected_type = fields[key]
            # Allow basic arithmetic expressions (this is a security issue, but
            # we trust the user input for now)
            if isinstance(value, str) and expected_type in (int, float):
                value = expected_type(eval(value))
            if not isinstance(value, expected_type):
                raise TypeError(f'Invalid type for field {key}: {type(value)},'
                                f' expected {expected_type}')
            old_value = getattr(self, key)
            if old_value == value:
                continue
            logger.info(f'Changed config field "{key}" from {old_value} to '
                        f'{value}')
            setattr(self, key, value)
        return self

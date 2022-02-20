import logging
import logging.config
import argparse
import yaml
from pathlib import Path
from typing import Optional, List


_LOGGING_CFG_PATHS = [
    './dyn-configs/logging.yaml',
    './configs/logging.yaml',
    '../configs/logging.yaml',
]


def _existing_file(p: str) -> Path:
    path = Path(p)
    if not path.exists():
        raise FileNotFoundError(f'File does not exist: {p}')
    return path


def first_existing(str_paths: List[str]) -> Optional[Path]:
    for str_path in str_paths:
        path = Path(str_path)
        if path.exists():
            return path
    return None


def add_logging_args(parser: argparse.ArgumentParser
                     ) -> argparse.ArgumentParser:
    parser.add_argument('--logging_config', type=_existing_file,
                        default=first_existing(_LOGGING_CFG_PATHS),
                        help='The config file specifying the logging '
                             'behaviour')
    return parser


def init_logging(args: argparse.Namespace) -> None:
    # Check that a logging config exists
    if not hasattr(args, 'logging_config'):
        raise NotImplementedError('No "logging_config" in args')
    if args.logging_config is None:
        raise FileNotFoundError('No logging config found or specified, '
                                f'searched in {_LOGGING_CFG_PATHS}')
    # Logging
    with open(args.logging_config, 'r') as fh:
        logging_config = yaml.load(fh, Loader=yaml.SafeLoader)
    logging.config.dictConfig(logging_config)

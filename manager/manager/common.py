import logging
import logging.config
import argparse
import yaml
from pathlib import Path
from typing import Optional, List, Union


_LOGGING_CFG_PATHS = [
    '/dyn-configs/logging.yaml',
    '/configs/logging.yaml',
    './configs/logging.yaml',
    '../configs/logging.yaml',
]


def existing_file(p: str) -> Path:
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
    parser.add_argument('--logging_config', type=existing_file,
                        default=first_existing(_LOGGING_CFG_PATHS),
                        help='The config file specifying the logging '
                             'behaviour')
    return parser


def init_logging(args_or_path: Union[argparse.Namespace, Path]) -> None:
    if not isinstance(args_or_path, Path):
        args = args_or_path
        # Check that a logging config exists
        if not hasattr(args, 'logging_config'):
            raise NotImplementedError('No "logging_config" in args')
        if args.logging_config is None:
            raise FileNotFoundError('No logging config found or specified, '
                                    f'searched in {_LOGGING_CFG_PATHS}')
        path = args_or_path.logging_config
    else:
        path = args_or_path
    # Logging
    with open(path, 'r') as fh:
        logging_config = yaml.load(fh, Loader=yaml.SafeLoader)
    logging.config.dictConfig(logging_config)

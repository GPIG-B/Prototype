#!/usr/bin/env python3
import argparse
import logging
from pathlib import Path

import manager


LOG_LEVELS = {1: logging.INFO, 2: logging.WARNING, 3: logging.ERROR}
LOG_FORMAT = '%(asctime)s %(levelname)s: %(message)s'


def _existing_file(p: str) -> Path:
    path = Path(p)
    if not path.exists():
        raise FileNotFoundError(f'File does not exist: {p}')
    return path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--quiet', '-q', help='Quiet mode (additive)',
                        action='count', default=1)
    parser.add_argument('--logfile', '-log', type=Path, default=None)
    manager.add_manager_arguments(parser)
    args = parser.parse_args()
    # Logging config
    if args.logfile is not None:
        args.logfile.parent.mkdir(parents=True, exist_ok=True)
        args.logfile.touch()
    logging.basicConfig(
            format=LOG_FORMAT,
            level=LOG_LEVELS[args.quiet],
            filename=args.logfile)
    # Instantiate the manager and serve forever
    server = manager.Server.from_args(args)
    server.run()


if __name__ == '__main__':
    main()

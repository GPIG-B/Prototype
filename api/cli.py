#!/usr/bin/env python3
import logging
import argparse
from pathlib import Path

import manager
import api


LOG_LEVELS = {1: logging.INFO, 2: logging.WARNING, 3: logging.ERROR}
LOG_FORMAT = '%(asctime)s %(levelname)s: %(message)s'


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--quiet', '-q', help='Quiet mode (additive)',
                        action='count', default=1)
    parser.add_argument('--logfile', '-log', type=Path, default=None)
    parser.add_argument('--host', type=str, default='127.0.0.1')
    parser.add_argument('--port', '-p', type=int, default=8080)
    manager.add_manager_arguments(parser)
    # Parse arguments
    args = parser.parse_args()
    # Logging config
    if args.logfile is not None:
        args.logfile.parent.mkdir(parents=True, exist_ok=True)
        args.logfile.touch()
    logging.basicConfig(
            format=LOG_FORMAT,
            level=LOG_LEVELS[args.quiet],
            filename=args.logfile)
    # Start the server
    manager_client = manager.Client.from_args('api', args)
    app = api.build_app(manager_client, debug=True)
    app.run(host=args.host, port=args.port)


if __name__ == '__main__':
    main()

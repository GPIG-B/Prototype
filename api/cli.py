#!/usr/bin/env python3
import argparse
import logging

import manager
import api


logger = logging.getLogger('api')


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', type=str, default='127.0.0.1')
    parser.add_argument('--port', '-p', type=int, default=8080)
    manager.common.add_logging_args(parser)
    manager.add_manager_arguments(parser)
    # Parse arguments
    args = parser.parse_args()
    # Logging config
    manager.common.init_logging(args)
    logger.info(f'Loaded logging config from {args.logging_config}')
    # Start the server
    manager_client = manager.Client.from_args('api', args)
    app = api.build_app(manager_client, debug=True)
    app.run(host=args.host, port=args.port)


if __name__ == '__main__':
    main()

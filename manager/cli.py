#!/usr/bin/env python3
import argparse
import logging

import manager


logger = logging.getLogger('manager')


def main() -> None:
    parser = argparse.ArgumentParser()
    manager.common.add_logging_args(parser)
    manager.add_manager_arguments(parser)
    args = parser.parse_args()
    manager.common.init_logging(args)
    logger.info(f'Loaded logging config from {args.logging_config}')
    # Instantiate the manager and serve forever
    server = manager.Server.from_args(args)
    server.run()


if __name__ == '__main__':
    main()

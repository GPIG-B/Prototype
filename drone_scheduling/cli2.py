#!/usr/bin/env python3
import time
from typing import Any, Dict, List
from argparse import ArgumentParser
from logging import getLogger
import numpy as np

import ds
import manager


logger = getLogger('drone_sched')


def main() -> None:
    # Argument parsing
    parser = ArgumentParser()
    manager.common.add_logging_args(parser)
    manager.add_manager_arguments(parser)
    args = parser.parse_args()
    manager.common.init_logging(args)
    client = manager.Client.from_args('drone_service', args)
    # Load drone and turbine positions
    map_cfg = get_attr(client, 'map_cfg')
    drones = ds.Drone.from_map(map_cfg)
    ds.loop(client, drones)


def get_attr(client: manager.Client, attr: str) -> Any:
    while True:
        ns = client.get_ns()
        if hasattr(ns, attr):
            return getattr(ns, attr)
        time.sleep(0.1)  # lmao


if __name__ == '__main__':
    main()

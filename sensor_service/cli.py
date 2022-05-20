#!/usr/bin/env python3
import argparse
from logging import getLogger
import time

import manager
from sensor_service import process


logger = getLogger('sensor_service')


def main() -> None:
    parser = argparse.ArgumentParser()
    manager.common.add_logging_args(parser)
    manager.add_manager_arguments(parser)
    args = parser.parse_args()
    manager.common.init_logging(args)
    client = manager.Client.from_args('sensor_service', args)
    while True:
        ns = client.get_ns()
        if not hasattr(ns, 'readings_queue') or not ns.readings_queue:
            time.sleep(0.1)  # lmao
            continue
        process(ns.readings_queue)
        time.sleep(1.0)  # lmao


if __name__ == '__main__':
    main()

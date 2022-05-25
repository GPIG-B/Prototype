#!/usr/bin/env python3
import argparse
from logging import getLogger
import time

import manager
from sensor_service import get_fault_alerts


logger = getLogger('sensor_service')


def main() -> None:
    parser = argparse.ArgumentParser()
    manager.common.add_logging_args(parser)
    manager.add_manager_arguments(parser)
    args = parser.parse_args()
    manager.common.init_logging(args)
    client = manager.Client.from_args('sensor_service', args)
    client.get_ns().sensor_alerts = []
    while True:
        ns = client.get_ns()
        if not hasattr(ns, 'readings_queue') or not ns.readings_queue:
            time.sleep(0.1)  # lmao
            continue
        alert_wt_ids = get_fault_alerts(ns.readings_queue)
        if alert_wt_ids:
            msg = f'Alerts for: {alert_wt_ids}'
            logger.info(msg)
            client.log(msg, 'warning')
        ns.sensor_alerts = alert_wt_ids
        time.sleep(1.0)


if __name__ == '__main__':
    main()

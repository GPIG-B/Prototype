#!/usr/bin/env python3
import time
from typing import Any, Dict, List
from argparse import ArgumentParser
from logging import getLogger
import numpy as np

import drone_scheduling.drone_scheduling as ds
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
    # 'magic numbers' below taken from the code in drone_scheduling, god knows
    # what they mean...
    turbines: List[Dict[str, Any]] = map_cfg['turbines']
    stations: List[Dict[str, Any]] = map_cfg['stations']
    spos = [np.array((float(s['lat']), float(s['lng']))) - ds.utils.COORD_BIAS
            for s in stations]
    drones = ds.inititialise_drones(spos)  # type: ignore
    scheduler = ds.Scheduler()
    last_time = client.get_ns().time_seconds
    logger.info(f'Starting loop')
    while True:
        # if the line below crashes with an AttributeError, good luck hehe
        current_time = client.get_ns().time_seconds
        dt = current_time - last_time
        alerts = get_attr(client, 'sensor_alerts')
        while alerts:
            wt_id = alerts.pop()
            client.get_ns().sensor_alerts = alerts
            try:
                entry, *_ = [t for t in turbines if t['id'] == wt_id]
            except ValueError:
                logger.error(f'Unknown WT id: {wt_id}')
                continue
            pos = np.array((float(entry['lat']),
                            float(entry['lng']))) - ds.utils.COORD_BIAS
            scheduler.add_inspection(pos, wt_id)  # type: ignore
            logger.info(f'Scheduled drone inspection for WT[{wt_id}]')
        inspected = scheduler.update(drones)
        ds.update(spos, drones, dt)
        positions = [{'drone_id': f'Drone_{d.id}',
                      'lat': float(d.abs_pos[0]),
                      'lng': float(d.abs_pos[1]),
                      'status': d.status.name.lower()}
                      for d in drones]
        client.get_ns().drone_positions = positions
        for wt_id in inspected:
            logger.info(f'Finished drone inspection of WT[{wt_id}]')

        last_time = current_time
        time.sleep(1.)


def get_attr(client: manager.Client, attr: str) -> Any:
    while True:
        ns = client.get_ns()
        if hasattr(ns, attr):
            return getattr(ns, attr)
        time.sleep(0.1)  # lmao


if __name__ == '__main__':
    main()

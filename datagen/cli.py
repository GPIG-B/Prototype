#!/usr/bin/env python3
import argparse
import random
import logging
import logging.config

import datagen as dg
import manager


_CFG_PATHS = [
    '/dyn-configs/datagen.yaml',
    './configs/datagen.yaml',
    '../configs/datagen.yaml',
]
logger = logging.getLogger('datagen')


def main() -> None:
    parser = argparse.ArgumentParser()
    msg = 'Seed of the random number generator'
    parser.add_argument('--seed', type=int, default=None, help=msg)
    parser.add_argument('--config', type=manager.common.existing_file,
                        default=manager.common.first_existing(_CFG_PATHS),
                        help='The config file containing the simulation '
                             'constants')
    parser.add_argument('--warmup', type=int, default=10,
                        help='Number of ticks to "warm up" the simulation '
                             'after initialisation')
    manager.common.add_logging_args(parser)
    manager.add_manager_arguments(parser)
    # Parse arguments
    args = parser.parse_args()
    manager.common.init_logging(args)
    logger.info(f'Loaded logging config from {args.logging_config}')
    # Check that a config exists
    if args.config is None:
        logger.error(f'No config found or specified, searched in {_CFG_PATHS}')
        exit(1)
    # RNG seed
    if args.seed is not None:
        random.seed(args.seed)
    # Get the global namespace
    client = manager.Client.from_args('datagen_sim', args)

    def loop_callback(readings: dg.types.ReadingsT) -> None:
        """Write the simulation results to the global namespace."""
        client.get_ns().last_readings = readings

    # Initialise the simulation
    sim = _build_sim(args)
    sim.loop(loop_callback)


def _build_sim(args: argparse.Namespace) -> dg.types.Simulation:
    cfg = dg.config.Config.from_yaml(args.config)
    env = dg.types.Environment.from_config(cfg)
    wts = [dg.types.WindTurbine.from_env(env)
           for _ in range(cfg.wts)]
    sim = dg.types.Simulation(cfg, wts, env)
    logger.info('Starting warmup')
    sim.tick(args.warmup)
    logger.info('Done')
    return sim


if __name__ == '__main__':
    main()

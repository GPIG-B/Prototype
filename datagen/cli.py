#!/usr/bin/env python3
import argparse
import random
import logging
import logging.config
import sys
import json

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
    subparsers = parser.add_subparsers()
    msg = 'Seed of the random number generator'
    parser.add_argument('--seed', type=int, default=None, help=msg)
    # Parser for simulations
    sim_parser = argparse.ArgumentParser(add_help=False)
    sim_parser.add_argument('--config', type=manager.common._existing_file,
                            default=manager.common.first_existing(_CFG_PATHS),
                            help='The config file containing the simulation '
                                 'constants')
    sim_parser.add_argument('--warmup', type=int, default=10,
                            help='Number of ticks to "warm up" the simulation '
                                 'after initialisation')
    manager.common.add_logging_args(parser)
    # Parser for the global state manager
    gsm_parser = argparse.ArgumentParser(add_help=False)
    manager.add_manager_arguments(gsm_parser)
    # JSON action
    p = subparsers.add_parser('json', parents=[sim_parser])
    p.add_argument('--ticks', type=int, default=10,
                   help='The number of ticks (timesteps) to simulate')
    p.set_defaults(func=json_action)
    # SIM action
    p = subparsers.add_parser('sim', parents=[sim_parser, gsm_parser])
    p.set_defaults(func=sim_action)
    # Parse arguments
    args = parser.parse_args()
    # Initialise logging
    manager.common.init_logging(args)
    logger.info(f'Loaded logging config from {args.logging_config}')
    # Check that a config exists
    if args.config is None:
        logger.error(f'No config found or specified, searched in {_CFG_PATHS}')
        exit(1)
    # Check if an action was specified
    if not hasattr(args, 'func'):
        logger.error('No action specified')
        exit(1)
    m = '--ticks must be greater than 0, got %d'
    assert getattr(args, 'ticks', 1) > 0, m % args.ticks
    # RNG seed
    if args.seed is not None:
        random.seed(args.seed)
    # Perform the specified action
    args.func(args)


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


def json_action(args: argparse.Namespace) -> None:
    sim = _build_sim(args)
    for _ in range(args.ticks):
        readings = sim.get_readings()
        sim.tick()
        sys.stdout.write(json.dumps(readings) + '\n')


def sim_action(args: argparse.Namespace) -> None:
    # Get the global namespace
    client = manager.Client.from_args('datagen_sim', args)

    def loop_callback(readings: dg.types.ReadingsT) -> None:
        """Write the simulation results to the global namespace."""
        client.get_ns().last_readings = readings

    # Initialise the simulation
    sim = _build_sim(args)
    sim.loop(loop_callback)


if __name__ == '__main__':
    main()

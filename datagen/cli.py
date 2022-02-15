#!/usr/bin/env python3
import argparse
import random
import logging
import sys
from pathlib import Path

import datagen as dg


LOG_LEVELS = {1: logging.INFO, 2: logging.WARNING, 3: logging.ERROR}
LOG_FORMAT = '%(asctime)s %(levelname)s: %(message)s'


def main() -> None:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    msg = 'Seed of the random number generator'
    parser.add_argument('--seed', type=int, default=None, help=msg)
    parser.add_argument('--quiet', '-q', help='Quiet mode (additive)',
                        action='count', default=1)
    parser.add_argument('--logfile', '-log', type=Path, default=None)
    # Auxiliary parsers
    sim_parser = argparse.ArgumentParser(add_help=False)
    msg = 'The number of ticks (timesteps) to simulate'
    sim_parser.add_argument('--ticks', type=int, default=10, help=msg)
    msg = 'The number of wind turbines to simulate'
    sim_parser.add_argument('--wts', type=int, default=3, help=msg)
    msg = 'Number of ticks to "warm up" the simulation after initialisation'
    sim_parser.add_argument('--warmup', type=int, default=10, help=msg)
    # Actions
    subparsers.add_parser('dev', parents=[sim_parser]).set_defaults(func=dev)
    subparsers.add_parser('csv', parents=[sim_parser]).set_defaults(func=csv)
    # Parse arguments
    args = parser.parse_args()
    msg = '--wts must be greater than 0, got %d'
    assert getattr(args, 'wts', 1) > 0, msg % args.wts
    msg = '--ticks must be greater than 0, got %d'
    assert getattr(args, 'ticks', 1) > 0, msg % args.ticks
    # Logging config
    logging.basicConfig(
            format=LOG_FORMAT,
            level=LOG_LEVELS[args.quiet],
            filename=args.logfile)
    # RNG seed
    if args.seed is not None:
        random.seed(args.seed)
    # Check if an action was specified
    if not hasattr(args, 'func'):
        print('No action specified')
        parser.print_usage()
        exit(1)
    # Perform the specified action
    args.func(args)


def _build_sim(args: argparse.Namespace) -> dg.types.Simulation:
    cfg = dg.config.Config()
    env = dg.types.Environment.from_config(cfg)
    wts = [dg.types.WindTurbine([dg.types.Tower(),
                                 dg.types.Rotor(env),
                                 dg.types.Generator(env)])
           for _ in range(args.wts)]
    return dg.types.Simulation(cfg, wts, env).tick(args.warmup)


def csv(args: argparse.Namespace) -> None:
    """Prints the sensory readings of the WTs to stdout."""
    delim = ', '
    sim = _build_sim(args)
    columns = None
    for _ in range(args.ticks):
        sim.tick()
        readings = sim.get_readings()
        if columns is None:
            columns = list(readings['wts'][0].keys())  # type: ignore
            sys.stdout.write(delim.join(['time'] + columns) + '\n')
        rows = [[readings['time']] + [wt[c] for c in columns]
                for wt in readings['wts']]  # type: ignore
        row_strs = '\n'.join(delim.join(str(x) for x in row) for row in rows)
        sys.stdout.writelines(row_strs + '\n')


def dev(args: argparse.Namespace) -> None:
    """Sandbox for development."""
    from pprint import pprint

    sim = _build_sim(args)
    for _ in range(args.ticks):
        readings = sim.get_readings()
        sim.tick()
        pprint(sim.env)
        pprint(readings)


if __name__ == '__main__':
    main()
